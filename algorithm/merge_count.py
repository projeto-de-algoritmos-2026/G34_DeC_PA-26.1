def merge_count(left, right):
    # Combina duas sublistas já ordenadas em uma única lista ordenada,
    # contando inversões: cada vez que um elemento de 'right' é menor
    # que um elemento de 'left', todos os elementos restantes em 'left'
    # formariam inversão com ele, então somamos len(left) - i.
    merged = []
    inversions = 0
    i = 0  # ponteiro para left
    j = 0  # ponteiro para right

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            # Elemento da esquerda é menor ou igual: sem inversão
            merged.append(left[i])
            i += 1
        else:
            # Elemento da direita é menor: todos os left[i..] formam inversão com right[j]
            merged.append(right[j])
            inversions += len(left) - i
            j += 1

    # Acrescenta os elementos restantes (já ordenados, sem novas inversões)
    merged.extend(left[i:])
    merged.extend(right[j:])

    return merged, inversions
