# -*- coding: utf-8 -*-

from algorithm.sort_and_count import sort_and_count

def ranking_to_permutation(ranking1, ranking2):
    """
    Converte os dois rankings em uma permutação correspondente de índices.
    ranking1 serve como a referência (baseline). Cada elemento de ranking2 é mapeado 
    para o índice que ele ocupa em ranking1.
    
    Exemplo:
      ranking1 = [3, 1, 2] -> mapeia 3: 0, 1: 1, 2: 2
      ranking2 = [1, 3, 2] -> retorna [1, 0, 2]
    """
    pos1 = {movie_id: index for index, movie_id in enumerate(ranking1)}
    permutation = [pos1[movie_id] for movie_id in ranking2]
    return permutation


def calculate_similarity(ranking1, ranking2):
    """
    Calcula a similaridade entre os rankings dos dois usuários.
    Retorna o número de inversões entre eles.
    """
    permutation = ranking_to_permutation(ranking1, ranking2)
    _, inversions = sort_and_count(permutation)
    return inversions


def interpret_score(inversions, max_inversions=45):
    """
    Interpreta o número de inversões, calculando a porcentagem de compatibilidade
    e fornecendo uma descrição em linguagem natural sobre a afinidade entre os usuários.
    
    Para 10 filmes, o número máximo de inversões é 10 * 9 / 2 = 45.
    """
    if max_inversions <= 0:
        return 100.0, "Gostos idênticos! Não há filmes suficientes para comparação."

    # Calcula a porcentagem de similaridade (0 inversões = 100%, max_inversions = 0%)
    similarity_pct = (1.0 - (inversions / max_inversions)) * 100.0
    similarity_pct = max(0.0, min(100.0, similarity_pct))

    # Define a mensagem descritiva
    if inversions == 0:
        interpretation = "Compatibilidade Perfeita! Vocês têm exatamente as mesmas preferências para estes filmes."
    elif inversions <= max_inversions * 0.25:
        interpretation = "Alta Similaridade! Vocês concordam na maioria das escolhas e possuem perfis bem próximos."
    elif inversions <= max_inversions * 0.75:
        interpretation = "Similaridade Moderada! Vocês têm alguns filmes em comum, mas divergem na ordem de preferência de outros."
    elif inversions < max_inversions:
        interpretation = "Baixa Similaridade! Seus gostos para cinema são bem diferentes."
    else:
        interpretation = "Oposição Completa! Suas preferências são o oposto absoluto uma da outra."

    return similarity_pct, interpretation
