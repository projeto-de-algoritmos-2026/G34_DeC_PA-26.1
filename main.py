# -*- coding: utf-8 -*-
import sys
from app.movies import MOVIES
from app.input_handler import get_user_ranking
from app.similarity import calculate_similarity, interpret_score

def main():
    print("=" * 60)
    print("      SISTEMA DE COMPATIBILIDADE DE GOSTOS DE FILMES")
    print("          (Algoritmo de Contagem de Inversões)")
    print("=" * 60)
    print("\nEste sistema compara os gostos cinematográficos de dois usuários")
    print("com base na ordem em que classificam 10 filmes clássicos.")
    
    # Obter ranking para o Usuário A
    ranking_a = get_user_ranking(MOVIES, "Usuário A")
    
    # Obter ranking para o Usuário B
    ranking_b = get_user_ranking(MOVIES, "Usuário B")
    
    # Calcular similaridade
    inversions = calculate_similarity(ranking_a, ranking_b)
    
    # Como são 10 filmes, o número máximo de inversões é 10 * 9 / 2 = 45
    max_inversions = len(MOVIES) * (len(MOVIES) - 1) // 2
    
    similarity_pct, interpretation = interpret_score(inversions, max_inversions)
    
    # Exibir resultados
    print("\n" + "=" * 60)
    print("                      RESULTADO")
    print("=" * 60)
    print(f"Número de Inversões detectadas: {inversions} (de um máximo de {max_inversions})")
    print(f"Porcentagem de Similaridade   : {similarity_pct:.2f}%")
    print(f"Interpretação: {interpretation}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrograma encerrado pelo usuário. Até logo!")
        sys.exit(0)
