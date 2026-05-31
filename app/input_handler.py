# -*- coding: utf-8 -*-

def parse_and_validate_ranking(input_str, num_movies):
    """
    Analisa uma string contendo IDs de filmes e valida as regras.
    O ranking deve conter todos os inteiros de 1 a num_movies sem repetição.
    Retorna a lista de inteiros validados se estiver correto.
    Caso contrário, levanta ValueError com uma mensagem descritiva.
    """
    # Substitui vírgulas por espaços para tratar ambos os separadores uniformemente
    cleaned = input_str.replace(',', ' ')
    tokens = cleaned.split()

    if len(tokens) != num_movies:
        raise ValueError(f"O ranking deve conter exatamente {num_movies} números. Você forneceu {len(tokens)}.")

    ranking = []
    for token in tokens:
        try:
            val = int(token)
        except ValueError:
            raise ValueError(f"Entrada inválida: '{token}' não é um número inteiro válido.")

        if val < 1 or val > num_movies:
            raise ValueError(f"ID inválido: {val}. Cada número deve estar entre 1 e {num_movies}.")

        ranking.append(val)

    # Verifica duplicatas e integridade do ranking
    unique_elements = set(ranking)
    if len(unique_elements) != num_movies:
        duplicates = set([x for x in ranking if ranking.count(x) > 1])
        raise ValueError(f"Elementos duplicados detectados: {list(duplicates)}. Cada ID deve aparecer exatamente uma vez.")

    return ranking


def get_user_ranking(movies, username="Usuário"):
    """
    Exibe os filmes disponíveis no terminal e solicita o ranking do usuário de forma interativa.
    Continua solicitando até que a entrada seja válida.
    """
    num_movies = len(movies)
    print(f"\n=== Ranking de Filmes - {username} ===")
    print("Por favor, ordene os seguintes filmes do seu FAVORITO (1º) ao seu MENOS PREFERIDO (10º):")
    
    for i, movie in enumerate(movies, 1):
        print(f"  [{i:2d}] {movie}")

    while True:
        try:
            prompt_msg = f"\nDigite os números de 1 a {num_movies} na sua ordem de preferência (separados por espaço ou vírgula):\n> "
            entrada = input(prompt_msg)
            ranking = parse_and_validate_ranking(entrada, num_movies)
            return ranking
        except ValueError as e:
            print(f"\n[ERRO DE VALIDAÇÃO] {e} Tente novamente.")


def get_number_of_movies():
    while True:
        try:
            entrada = input("\nQuantos filmes do Top IMDb você quer comparar? (5 a 250): ").strip()
            n = int(entrada)
            if 5 <= n <= 250:
                return n
            print("[ERRO] Digite um número entre 5 e 250.")
        except ValueError:
            print("[ERRO] Entrada inválida. Digite um número inteiro.")


def get_user_ratings(movies):
    print("\n=== Avalie cada filme de 0 a 10 (decimais permitidos, ex: 8.5) ===")
    ratings = []
    for i, movie in enumerate(movies, 1):
        while True:
            try:
                entrada = input(f"  [{i:3d}] {movie}: ").strip()
                rating = float(entrada)
                if 0.0 <= rating <= 10.0:
                    ratings.append(rating)
                    break
                print("       [ERRO] A nota deve ser entre 0 e 10.")
            except ValueError:
                print("       [ERRO] Entrada inválida. Digite um número.")
    return ratings
