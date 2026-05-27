from algorithm.sort_and_count import sort_and_count


def run_test(label, arr, expected_inv):
    sorted_arr, inversions = sort_and_count(arr)
    status = "OK" if inversions == expected_inv else "FALHOU"
    print(f"[{status}] {label}")
    print(f"       entrada  : {arr}")
    print(f"       ordenado : {sorted_arr}")
    print(f"       inversões: {inversions}  (esperado: {expected_inv})")
    print()


if __name__ == "__main__":
    print("=" * 40)
    print("  Testes — Contagem de Inversões")
    print("=" * 40)
    print()

    # [3,1,2] → (3,1), (3,2) = 2 inversões
    run_test("caso básico [3,1,2]", [3, 1, 2], 2)

    # já ordenado → 0 inversões
    run_test("já ordenado [1,2,3,4]", [1, 2, 3, 4], 0)

    # ordem inversa [4,3,2,1] → 6 inversões (máximo para n=4)
    run_test("ordem inversa [4,3,2,1]", [4, 3, 2, 1], 6)

    # único elemento → 0 inversões
    run_test("único elemento [7]", [7], 0)

    # lista vazia → 0 inversões
    run_test("lista vazia []", [], 0)

    # caso com repetição [2,2,1] → (2,1),(2,1) = 2 inversões
    run_test("com repetição [2,2,1]", [2, 2, 1], 2)

    # exemplo do enunciado: permutação de 10 elementos
    run_test(
        "exemplo do enunciado (n=10)",
        [2, 4, 1, 3, 5, 6, 7, 8, 10, 9],
        4,  # (2,1),(4,1),(4,3),(10,9)
    )
