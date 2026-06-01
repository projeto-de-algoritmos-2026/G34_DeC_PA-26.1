from algorithm.merge_count import merge_count


def sort_and_count(arr):
    # Caso base: lista de 0 ou 1 elemento já está ordenada, sem inversões
    if len(arr) <= 1:
        return arr, 0

    # Divide o array ao meio
    mid = len(arr) // 2
    left, right = arr[:mid], arr[mid:]

    # Conta inversões recursivamente em cada metade
    sorted_left, inv_left = sort_and_count(left)
    sorted_right, inv_right = sort_and_count(right)

    # Conta inversões entre as duas metades durante o merge
    sorted_arr, inv_merge = merge_count(sorted_left, sorted_right)

    # Total = inversões da metade esquerda + direita + entre as metades
    return sorted_arr, inv_left + inv_right + inv_merge
