# -*- coding: utf-8 -*-
"""
Servidor Flask para a interface web de comparação de rankings de filmes.
Expõe endpoints REST que fazem a ponte entre o frontend e a lógica existente
do algoritmo de contagem de inversões.
"""
import base64
import html
import http.client
import json
import os
import sys
import hashlib
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

# ---------------------------------------------------------------------------
# Importar módulos existentes do projeto
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
from algorithm.sort_and_count import sort_and_count
from app.movies import MOVIES
from app.similarity import ratings_to_permutation, interpret_score

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------
_HOST = "imdb236.p.rapidapi.com"
_TOP250_URL = "/api/imdb/top250-movies"
_ROOT_ENV_PATH = Path(__file__).resolve().parent / ".env"
_APP_ENV_PATH = Path(__file__).resolve().parent / "app" / ".env"

_POSTER_PALETTE = [
    ("#1f1147", "#7b2d8e"),
    ("#0f172a", "#2563eb"),
    ("#10261f", "#16a34a"),
    ("#3b1d0a", "#ea580c"),
    ("#2b124c", "#ec4899"),
]

app = Flask(__name__, static_folder="web", static_url_path="")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_env():
    """Carrega variáveis do arquivo .env na raiz do projeto."""
    for env_path in (_ROOT_ENV_PATH, _APP_ENV_PATH):
        if not env_path.exists():
            continue
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


def _get_api_key():
    """Obtém a chave da API RapidAPI do ambiente."""
    _load_env()
    key = os.environ.get("RAPIDAPI_KEY", "").strip()
    return key


def _poster_data_uri(title, year="", rank=None):
        """Gera um pôster SVG local para usar como imagem de fallback."""
        palette_index = int(hashlib.sha1(title.encode("utf-8")).hexdigest(), 16) % len(_POSTER_PALETTE)
        color_a, color_b = _POSTER_PALETTE[palette_index]

        safe_title = html.escape(title)
        safe_year = html.escape(str(year)) if year else ""
        rank_text = f"#{rank}" if rank is not None else "CineRank"

        svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='800' height='1200' viewBox='0 0 800 1200'>
    <defs>
        <linearGradient id='g' x1='0%' y1='0%' x2='100%' y2='100%'>
            <stop offset='0%' stop-color='{color_a}'/>
            <stop offset='100%' stop-color='{color_b}'/>
        </linearGradient>
        <filter id='shadow' x='-20%' y='-20%' width='140%' height='140%'>
            <feDropShadow dx='0' dy='24' stdDeviation='28' flood-color='#000' flood-opacity='0.35'/>
        </filter>
    </defs>
    <rect width='800' height='1200' rx='36' fill='url(#g)'/>
    <circle cx='650' cy='150' r='110' fill='#ffffff' fill-opacity='0.08'/>
    <circle cx='160' cy='1020' r='180' fill='#ffffff' fill-opacity='0.06'/>
    <rect x='70' y='70' width='660' height='1060' rx='28' fill='#ffffff' fill-opacity='0.06' stroke='#ffffff' stroke-opacity='0.12'/>
    <text x='110' y='170' fill='#f4ecff' font-family='Arial, sans-serif' font-size='34' font-weight='700' letter-spacing='4'>{rank_text}</text>
    <text x='110' y='400' fill='#ffffff' font-family='Arial, sans-serif' font-size='58' font-weight='800'>
        <tspan x='110' dy='0'> {safe_title[:22]}</tspan>
        <tspan x='110' dy='74'> {safe_title[22:44]}</tspan>
        <tspan x='110' dy='74'> {safe_title[44:66]}</tspan>
    </text>
        {f"<text x='110' y='980' fill='#ffffff' fill-opacity='0.86' font-family='Arial, sans-serif' font-size='30' font-weight='600'>{safe_year}</text>" if safe_year else ""}
        <text x='110' y='1060' fill='#ffffff' fill-opacity='0.72' font-family='Arial, sans-serif' font-size='28' font-weight='500'>Poster indisponível</text>
</svg>"""

        data = base64.b64encode(svg.encode("utf-8")).decode("ascii")
        return f"data:image/svg+xml;base64,{data}"


def _extract_image_url(item):
    """Extrai a URL de imagem do payload da API IMDb."""
    img_obj = item.get("primaryImage")
    if isinstance(img_obj, str) and img_obj.strip():
        return img_obj.strip()

    if isinstance(img_obj, dict):
        img_url = img_obj.get("url", "")
        if isinstance(img_url, str) and img_url.strip():
            return img_url.strip()

    thumbnails = item.get("thumbnails")
    if isinstance(thumbnails, list) and thumbnails:
        first_thumb = thumbnails[0]
        if isinstance(first_thumb, str) and first_thumb.strip():
            return first_thumb.strip()
        if isinstance(first_thumb, dict):
            thumb_url = first_thumb.get("url", "")
            if isinstance(thumb_url, str) and thumb_url.strip():
                return thumb_url.strip()

    return ""


def _fallback_movies(n):
    """
    Retorna uma lista local de filmes para o modo offline.

    O modo sem chave suporta apenas a lista fixa do projeto, que contém
    exatamente 10 filmes.
    """
    if n > len(MOVIES):
        raise RuntimeError(
            f"Sem RAPIDAPI_KEY, o modo offline suporta no máximo {len(MOVIES)} filmes. "
            "Configure a chave no arquivo .env para buscar o Top IMDb completo."
        )

    return [
        {
            "title": title,
            "year": "",
            "rating": 0,
            "image": _poster_data_uri(title, rank=i + 1),
            "imdb_rank": i + 1,
        }
        for i, title in enumerate(MOVIES[:n])
    ]


def _fetch_rich_movies(n):
    """
    Busca os top n filmes da API IMDb com dados enriquecidos
    (título, ano, nota, imagem).
    """
    if not 1 <= n <= 250:
        raise ValueError(f"n deve estar entre 1 e 250, recebeu {n}.")

    key = _get_api_key()

    if not key:
        return _fallback_movies(n)

    conn = http.client.HTTPSConnection(_HOST)
    headers = {
        "x-rapidapi-key": key,
        "x-rapidapi-host": _HOST,
        "Content-Type": "application/json",
    }

    try:
        conn.request("GET", _TOP250_URL, headers=headers)
        res = conn.getresponse()

        if res.status != 200:
            raise RuntimeError(
                f"Erro na API do IMDb: HTTP {res.status} ({res.reason})"
            )

        data = json.loads(res.read().decode("utf-8"))

        if not isinstance(data, list):
            raise RuntimeError("Resposta inesperada da API.")

        movies = []
        for i, item in enumerate(data[:n]):
            title = item.get("primaryTitle", "")
            if not title:
                continue

            img_url = _extract_image_url(item)

            movies.append({
                "title": title,
                "year": item.get("startYear", ""),
                "rating": item.get("averageRating", 0),
                "image": img_url,
                "imdb_rank": i + 1,
            })

        if len(movies) < n:
            raise RuntimeError(
                f"API retornou apenas {len(movies)} filmes, mas {n} foram solicitados."
            )

        return movies

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------

@app.after_request
def _set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "img-src 'self' https: data:; "
        "connect-src 'self'"
    )
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )
    return response


# ---------------------------------------------------------------------------
# Rotas - Páginas
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory("web", "index.html")


# ---------------------------------------------------------------------------
# Rotas - API
# ---------------------------------------------------------------------------

@app.route("/api/movies")
def api_movies():
    """Retorna os top n filmes com dados enriquecidos."""
    try:
        n_raw = request.args.get("n", "")
        if not n_raw.isdigit():
            return jsonify({"error": "Parâmetro 'n' deve ser um número inteiro."}), 400

        n = int(n_raw)
        if n < 5 or n > 250:
            return jsonify({"error": "n deve estar entre 5 e 250."}), 400

        movies = _fetch_rich_movies(n)
        return jsonify({"movies": movies})

    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502
    except Exception:
        return jsonify({"error": "Erro interno do servidor."}), 500


@app.route("/api/movies", methods=["OPTIONS"])
def api_movies_options():
    return ("", 204)


@app.route("/api/compare", methods=["POST"])
def api_compare():
    """Recebe as notas do usuário e calcula a similaridade."""
    try:
        body = request.get_json(silent=True)
        if not body:
            return jsonify({"error": "Corpo da requisição inválido."}), 400

        movies = body.get("movies", [])
        movie_ratings = body.get("movie_ratings", [])
        ratings = body.get("ratings", [])

        if not isinstance(movies, list) or not isinstance(ratings, list):
            return jsonify({"error": "movies e ratings devem ser listas."}), 400

        if movie_ratings and not isinstance(movie_ratings, list):
            return jsonify({"error": "movie_ratings deve ser uma lista."}), 400

        if len(movies) < 2 or len(ratings) < 2:
            return jsonify({"error": "Mínimo de 2 filmes para comparar."}), 400

        if len(movies) != len(ratings):
            return jsonify({
                "error": "movies e ratings devem ter o mesmo comprimento."
            }), 400

        if movie_ratings and len(movie_ratings) != len(movies):
            return jsonify({
                "error": "movies e movie_ratings devem ter o mesmo comprimento."
            }), 400

        # Validar cada nota
        validated_ratings = []
        for i, r in enumerate(ratings):
            try:
                val = float(r)
            except (TypeError, ValueError):
                return jsonify({
                    "error": f"Nota inválida na posição {i + 1}: '{r}'"
                }), 400

            if val < 0.0 or val > 10.0:
                return jsonify({
                    "error": f"Nota na posição {i + 1} deve estar entre 0 e 10."
                }), 400
            validated_ratings.append(val)

        n = len(validated_ratings)

        # Gerar a permutação do usuário (índices ordenados por nota decrescente)
        permutation = ratings_to_permutation(validated_ratings)

        # Contar inversões
        _, inversions = sort_and_count(permutation)

        # Calcular similaridade
        max_inversions = n * (n - 1) // 2
        similarity_pct, interpretation = interpret_score(inversions, max_inversions)

        # Montar rankings comparativos
        user_ranking_pairs = sorted(
            enumerate(validated_ratings), key=lambda x: x[1], reverse=True
        )

        imdb_ranking = []
        user_ranking = []
        for rank in range(n):
            imdb_ranking.append({
                "rank": rank + 1,
                "title": movies[rank],
                "rating": movie_ratings[rank] if movie_ratings else None,
            })
            user_idx, user_rating = user_ranking_pairs[rank]
            user_ranking.append({
                "rank": rank + 1,
                "title": movies[user_idx],
                "rating": user_rating,
            })

        return jsonify({
            "inversions": inversions,
            "max_inversions": max_inversions,
            "similarity_pct": round(similarity_pct, 2),
            "interpretation": interpretation,
            "imdb_ranking": imdb_ranking,
            "user_ranking": user_ranking,
        })

    except Exception:
        return jsonify({"error": "Erro interno do servidor."}), 500


@app.route("/api/compare", methods=["OPTIONS"])
def api_compare_options():
    return ("", 204)


# ---------------------------------------------------------------------------
# Entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # TODO(security): Em produção, usar WSGI server (gunicorn/waitress)
    app.run(host="127.0.0.1", port=5000, debug=True)
