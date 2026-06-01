# -*- coding: utf-8 -*-
import json
import os
import subprocess
from pathlib import Path

_HOST = "imdb236.p.rapidapi.com"
_TOP250_URL = f"https://{_HOST}/api/imdb/top250-movies"
_ROOT_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
_APP_ENV_PATH = Path(__file__).resolve().parent / ".env"


def _load_env():
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
    _load_env()
    key = os.environ.get("RAPIDAPI_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "Chave da API não encontrada.\n"
            f"  Adicione RAPIDAPI_KEY=sua_chave no arquivo {_ROOT_ENV_PATH} ou {_APP_ENV_PATH}"
        )
    return key


def fetch_top_movies(n):
    if not 1 <= n <= 250:
        raise ValueError(f"n deve estar entre 1 e 250, recebeu {n}.")

    key = _get_api_key()

    result = subprocess.run(
        [
            "curl", "-s",
            "-H", "Content-Type: application/json",
            "-H", f"x-rapidapi-host: {_HOST}",
            "-H", f"x-rapidapi-key: {key}",
            _TOP250_URL,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Erro ao conectar com a API: {result.stderr[:200]}")

    data = json.loads(result.stdout)

    if not isinstance(data, list):
        raise RuntimeError(f"Resposta inesperada da API: {str(data)[:200]}")

    movies = [
        {
            "title": item["primaryTitle"],
            "image": item.get("primaryImage", ""),
            "rating": item.get("averageRating", "N/A"),
        }
        for item in data[:n]
        if item.get("primaryTitle")
    ]

    if len(movies) < n:
        raise RuntimeError(f"API retornou apenas {len(movies)} filmes, mas {n} foram solicitados.")

    return movies
