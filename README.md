# G34_D-C_PA-26.1

Projeto de comparação de gostos cinematográficos usando o algoritmo de **Contagem de Inversões** (Divide and Conquer / Merge Sort).

---

## Programas disponíveis

| Arquivo | Descrição |
|---|---|
| `main.py` | Compara os rankings de dois usuários a partir de uma lista fixa de 10 filmes |
| `imdb-API.py` | Compara o gosto do usuário com o ranking oficial do Top IMDb usando notas de 0 a 10 |

---

## Configuração da chave de API (necessário apenas para `imdb-API.py`)

O `imdb-API.py` busca os filmes diretamente do IMDb via [RapidAPI](https://rapidapi.com). Siga os passos abaixo para configurar:

### 1. Criar conta no RapidAPI

Acesse [https://rapidapi.com](https://rapidapi.com) e crie uma conta gratuita.

### 2. Assinar a API imdb236

1. Acesse [https://rapidapi.com/rapidapi-org1-rapidapi-org-default/api/imdb236/playground/apiendpoint_28f544bf-846a-4ee3-a876-6ee0488af568](https://rapidapi.com/rapidapi-org1-rapidapi-org-default/api/imdb236/playground/apiendpoint_28f544bf-846a-4ee3-a876-6ee0488af568)
2. Clique em **Subscribe to Test** e escolha o plano **Basic (Free)**

### 3. Copiar sua chave

1. No menu superior, acesse **Apps → My Apps → Default App → Authorization**
2. Copie o valor de **X-RapidAPI-Key**

### 4. Criar o arquivo `.env`

Na raiz do projeto, crie um arquivo chamado `.env` com o seguinte conteúdo:

```
RAPIDAPI_KEY=sua_chave_aqui
```

---

## Como executar

```bash
# Comparação entre dois usuários (lista fixa de 10 filmes)
python3 main.py

# Comparação com o Top IMDb (requer .env configurado)
python3 imdb-API.py
```

---

## Como o algoritmo funciona

1. Cada usuário define sua ordem de preferência dos filmes
2. O ranking do segundo usuário é convertido em uma **permutação** relativa ao primeiro
3. O algoritmo conta as **inversões** nessa permutação usando Merge Sort modificado
   - Uma inversão ocorre quando um filme aparece "fora de ordem" em relação ao outro ranking
   - Cada vez que um elemento da metade direita é menor que um da esquerda, somamos todos os elementos restantes da esquerda de uma vez (`len(left) - i`)
4. O número de inversões é normalizado pelo máximo possível `n*(n-1)/2` para gerar um score de 0% a 100%

| Inversões | Similaridade |
|---|---|
| 0 | 100% — gostos idênticos |
| ≤ 25% do máximo | Alta similaridade |
| ≤ 75% do máximo | Similaridade moderada |
| < máximo | Baixa similaridade |
| = máximo | 0% — gostos opostos |
