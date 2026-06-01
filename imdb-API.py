# -*- coding: utf-8 -*-
import sys
from app.imdb_client import fetch_top_movies, is_offline_mode
from app.input_handler import get_number_of_movies, get_user_ratings
from app.similarity import ratings_to_permutation, interpret_score
from algorithm.sort_and_count import sort_and_count

def main():
    print("=" * 60)
    print("     COMPARAÇÃO DE GOSTOS CINEMATOGRÁFICOS COM O TOP IMDb")
    print("           (Baseado no Algoritmo de Inversões)")
    print("=" * 60)
    print("\nEste programa obtém os 'n' filmes mais bem avaliados do IMDb")
    print("e calcula a compatibilidade dos seus gostos com o ranking oficial")
    print("com base nas notas de 0 a 10 que você atribuir a cada um deles.")

    # 1. Obter 'n' do usuário
    n = get_number_of_movies()

    # 2. Buscar dados da API
    if is_offline_mode():
        print(f"\n[MODO OFFLINE] Nenhum .env com RAPIDAPI_KEY foi encontrado; usando os {n} filmes de app/movies.py.")
    else:
        print(f"\n[API] Conectando ao IMDb e buscando os top {n} filmes mais bem avaliados...")
    try:
        movies = fetch_top_movies(n)
        if is_offline_mode():
            print(f"[LOCAL] Sucesso! {len(movies)} filmes carregados da lista local.")
        else:
            print(f"[API] Sucesso! {len(movies)} filmes carregados.")
    except Exception as e:
        print(f"\n[ERRO FATAL] Não foi possível carregar os filmes do IMDb: {e}")
        print("Certifique-se de estar conectado à internet e que a chave da API é válida.")
        sys.exit(1)

    # 3. Coletar notas do usuário para cada filme
    ratings = get_user_ratings([m["title"] for m in movies])

    # 4. Converter as notas para permutação de índices baseada na ordem IMDb
    permutation = ratings_to_permutation(ratings)

    # 5. Calcular inversões
    _, inversions = sort_and_count(permutation)

    # 6. Exibir o ranking comparativo
    print("\n" + "=" * 60)
    print("                COMPARATIVO DE RANKINGS")
    print("=" * 60)
    print(f"{'Ranking IMDb (Oficial)':<30} | {'Seu Ranking (Baseado em Notas)'}")
    print("-" * 60)
    
    # Geramos o ranking ordenado do usuário para exibição
    user_ranking_pairs = sorted(list(enumerate(ratings)), key=lambda x: x[1], reverse=True)
    
    for rank in range(n):
        imdb_movie = movies[rank]["title"]
        user_movie_idx, user_rating = user_ranking_pairs[rank]
        user_movie = movies[user_movie_idx]["title"]

        # Exibe lado a lado (com limites de tamanho de string para alinhamento)
        imdb_movie_display = (imdb_movie[:26] + '...') if len(imdb_movie) > 29 else imdb_movie
        user_movie_display = (user_movie[:21] + '...') if len(user_movie) > 24 else user_movie
        print(f"{rank + 1:2d}. {imdb_movie_display:<29} | {rank + 1:2d}. {user_movie_display:<24} (Nota: {user_rating:.1f})")
    
    # 7. Calcular métricas e interpretar
    max_inversions = n * (n - 1) // 2
    similarity_pct, interpretation = interpret_score(inversions, max_inversions)

    print("\n" + "=" * 60)
    print("                      RESULTADO")
    print("=" * 60)
    print(f"Número de Inversões: {inversions} (de um máximo de {max_inversions})")
    print(f"Compatibilidade     : {similarity_pct:.2f}%")
    print(f"Interpretação: {interpretation}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma encerrado pelo usuário. Até logo!")
        sys.exit(0)