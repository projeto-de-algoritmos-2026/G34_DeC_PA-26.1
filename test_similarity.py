# -*- coding: utf-8 -*-
from app.input_handler import parse_and_validate_ranking
from app.similarity import ranking_to_permutation, calculate_similarity, interpret_score, ratings_to_permutation

def run_test(label, condition):
    status = "OK" if condition else "FALHOU"
    print(f"[{status}] {label}")
    return condition

if __name__ == "__main__":
    print("=" * 50)
    print("  Testes Unitários — Componente de Similaridade")
    print("=" * 50)
    print()

    # 1. Testar ranking_to_permutation
    r1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    r2 = [1, 2, 3, 4, 5, 6, 7, 8, 10, 9]
    perm = ranking_to_permutation(r1, r2)
    run_test("ranking_to_permutation simples", perm == [0, 1, 2, 3, 4, 5, 6, 7, 9, 8])

    r3 = [3, 1, 2]
    r4 = [2, 1, 3]
    perm2 = ranking_to_permutation(r3, r4)
    run_test("ranking_to_permutation customizado", perm2 == [2, 1, 0])

    # 2. Testar calculate_similarity
    inv1 = calculate_similarity(r1, r2)
    run_test("calculate_similarity (1 inversão)", inv1 == 1)

    inv2 = calculate_similarity(r3, r4)
    run_test("calculate_similarity (3 inversões)", inv2 == 3)

    # 3. Testar interpret_score
    pct1, desc1 = interpret_score(0, 45)
    run_test("interpret_score (0 inversões / 100%)", pct1 == 100.0 and "Compatibilidade Perfeita" in desc1)

    pct2, desc2 = interpret_score(45, 45)
    run_test("interpret_score (45 inversões / 0%)", pct2 == 0.0 and "Oposição Completa" in desc2)

    pct3, desc3 = interpret_score(10, 45)
    run_test("interpret_score (10 inversões / similaridade alta)", pct3 > 75.0 and "Alta Similaridade" in desc3)

    # 4. Testar parse_and_validate_ranking
    try:
        res1 = parse_and_validate_ranking("1, 2, 3, 4, 5, 6, 7, 8, 9, 10", 10)
        run_test("parse_and_validate_ranking (válido com vírgulas)", res1 == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    except Exception:
        run_test("parse_and_validate_ranking (válido com vírgulas)", False)

    try:
        res2 = parse_and_validate_ranking("10 9 8 7 6 5 4 3 2 1", 10)
        run_test("parse_and_validate_ranking (válido com espaços)", res2 == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])
    except Exception:
        run_test("parse_and_validate_ranking (válido com espaços)", False)

    # Casos de erro
    try:
        parse_and_validate_ranking("1, 2, 3", 10)
        run_test("parse_and_validate_ranking (erro menos elementos)", False)
    except ValueError as e:
        run_test("parse_and_validate_ranking (erro menos elementos)", "deve conter exatamente 10" in str(e))

    try:
        parse_and_validate_ranking("1 2 3 4 5 6 7 8 9 11", 10)
        run_test("parse_and_validate_ranking (erro valor fora do range)", False)
    except ValueError as e:
        run_test("parse_and_validate_ranking (erro valor fora do range)", "ID inválido: 11" in str(e))

    try:
        parse_and_validate_ranking("1 2 3 4 5 6 7 8 9 9", 10)
        run_test("parse_and_validate_ranking (erro duplicata)", False)
    except ValueError as e:
        run_test("parse_and_validate_ranking (erro duplicata)", "duplicados" in str(e))

    # 5. Testar ratings_to_permutation com desempate estável
    # Casos simples:
    res_ratings1 = ratings_to_permutation([8.0, 9.5, 7.0])
    run_test("ratings_to_permutation ordenação simples", res_ratings1 == [1, 0, 2])

    # Caso com empates:
    res_ratings2 = ratings_to_permutation([8.0, 9.5, 9.5])
    # Deve preservar a ordem original (1 antes de 2) devido à estabilidade
    run_test("ratings_to_permutation com empates (estável)", res_ratings2 == [1, 2, 0])

    print("\nTodos os testes unitários concluídos.")

