import json
from collections import Counter

# --- CONFIGURAÇÃO ---
# Nome do arquivo JSON unificado que será validado.
NOME_ARQUIVO_JSON = "DADOS_UNIFICADOS.json"
# Quantas redações mostrar na amostra inicial.
NUMERO_DE_AMOSTRAS = 15
# --------------------

def validar_comparacao_ia_tradicional(dados):
    """
    Analisa as redações que possuem tanto correção de IA quanto tradicional,
    mostrando dados brutos para validação.
    """
    dados_comparaveis = []
    
    # 1. Filtra apenas as redações que têm os dois tipos de correção
    for tema in dados:
        if tema.get('fonte') == 'Brasil Escola':
            for redacao in tema.get('redacoes', []):
                correcoes = redacao.get('correcoes', [])
                
                nota_ia = None
                nota_trad = None
                
                for c in correcoes:
                    if c.get('tipo') == 'IA':
                        nota_ia = c.get('nota_final')
                    elif c.get('tipo') == 'Tradicional':
                        nota_trad = c.get('nota_final')

                # Se ambas as notas foram encontradas, adiciona à lista de comparação
                if nota_ia is not None and nota_trad is not None:
                    diferenca = nota_ia - nota_trad
                    dados_comparaveis.append({
                        'url': redacao.get('url'),
                        'nota_trad': nota_trad,
                        'nota_ia': nota_ia,
                        'diferenca': diferenca
                    })

    if not dados_comparaveis:
        print("Nenhuma redação com ambas as correções (IA e Tradicional) foi encontrada para comparação.")
        return

    print(f"\nTotal de redações com ambas as correções encontradas: {len(dados_comparaveis)}")
    
    # 2. Mostra uma amostra bruta dos dados para verificação manual
    print(f"\n{'='*70}")
    print(f" AMOSTRA BRUTA DE COMPARAÇÃO (primeiras {NUMERO_DE_AMOSTRAS} redações)")
    print(f"{'='*70}")
    for item in dados_comparaveis[:NUMERO_DE_AMOSTRAS]:
        print(f"URL: {item['url']}")
        print(f"  - Nota Tradicional: {item['nota_trad']:>4}")
        print(f"  - Nota IA:          {item['nota_ia']:>4}")
        print(f"  - Diferença:        {item['diferenca']:>+4}") # O '+' mostra o sinal (+40 ou -40)
        print("-" * 20)
        
    # 3. Encontra e mostra os casos de maior discordância (outliers)
    dados_ordenados = sorted(dados_comparaveis, key=lambda x: x['diferenca'])
    
    print(f"\n{'='*70}")
    print(" CASOS EXTREMOS (MAIORES DISCORDÂNCIAS)")
    print(f"{'='*70}")
    
    print("\n--- Onde a IA foi MAIS RÍGIDA que o corretor humano ---")
    pior_caso = dados_ordenados[0]
    print(f"URL: {pior_caso['url']}")
    print(f"  - Nota Tradicional: {pior_caso['nota_trad']}")
    print(f"  - Nota IA:          {pior_caso['nota_ia']}")
    print(f"  - Diferença:        {pior_caso['diferenca']}")

    print("\n--- Onde a IA foi MAIS GENEROSA que o corretor humano ---")
    melhor_caso = dados_ordenados[-1]
    print(f"URL: {melhor_caso['url']}")
    print(f"  - Nota Tradicional: {melhor_caso['nota_trad']}")
    print(f"  - Nota IA:          {melhor_caso['nota_ia']}")
    print(f"  - Diferença:        {melhor_caso['diferenca']:+}")

    # 4. Mostra a distribuição de frequência das diferenças
    diferencas = [item['diferenca'] for item in dados_comparaveis]
    contagem_diferencas = Counter(diferencas)
    
    print(f"\n{'='*70}")
    print(" DISTRIBUIÇÃO DE FREQUÊNCIA DAS DIFERENÇAS DE NOTA")
    print(" (Quantas vezes cada diferença de nota apareceu)")
    print(f"{'='*70}")
    
    # Imprime as 15 diferenças mais comuns
    for diferenca, contagem in contagem_diferencas.most_common(15):
        porcentagem = (contagem / len(dados_comparaveis)) * 100
        print(f"Diferença de {diferenca:>+4} pontos: {contagem:>4} vezes ({porcentagem:.2f}%)")

    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        with open(NOME_ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            print(f"Lendo e validando o arquivo '{NOME_ARQUIVO_JSON}'...")
            dados_json = json.load(f)
        validar_comparacao_ia_tradicional(dados_json)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{NOME_ARQUIVO_JSON}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")