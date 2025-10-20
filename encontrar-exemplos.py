import json

# --- CONFIGURAÇÃO ---
NOME_ARQUIVO_JSON = "DADOS_UNIFICADOS.json"
# --------------------

def encontrar_nota_1000_com_ia(caminho_arquivo):
    """
    Busca no dataset redações que receberam nota 1000 na correção tradicional
    e que também possuem uma correção por IA.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return

    redacoes_encontradas = []

    # Itera por todos os temas e redações
    for tema in dados:
        # A correção por IA só existe na fonte 'Brasil Escola'
        if tema.get('fonte') != 'Brasil Escola':
            continue

        for redacao in tema.get('redacoes', []):
            tem_correcao_trad_1000 = False
            tem_correcao_ia = False
            nota_ia_para_comparar = None

            # Verifica as correções de uma única redação
            for correcao in redacao.get('correcoes', []):
                if correcao.get('tipo') == 'Tradicional' and correcao.get('nota_final') == 1000:
                    tem_correcao_trad_1000 = True
                
                if correcao.get('tipo') == 'IA':
                    tem_correcao_ia = True
                    nota_ia_para_comparar = correcao.get('nota_final')

            # Se ambos os critérios foram atendidos, armazena o resultado
            if tem_correcao_trad_1000 and tem_correcao_ia:
                info_redacao = {
                    'titulo': redacao.get('titulo'),
                    'url': redacao.get('url'),
                    'nota_ia': nota_ia_para_comparar
                }
                redacoes_encontradas.append(info_redacao)

    # Imprime os resultados
    print(f"\n{'='*70}")
    print(" BUSCA POR REDAÇÕES NOTA 1000 COM CORREÇÃO POR IA")
    print(f"{'='*70}")

    if redacoes_encontradas:
        print(f"\nSucesso! Foram encontradas {len(redacoes_encontradas)} redação(ões) que atendem aos critérios:\n")
        for r in redacoes_encontradas:
            print(f"  - Título: {r['titulo']}")
            print(f"  - Nota Tradicional: 1000")
            print(f"  - Nota da IA:       {r['nota_ia']}")
            print(f"  - URL:              {r['url']}")
            print("-" * 30)
    else:
        print("\nNenhuma redação com nota 1000 (tradicional) e que também possua correção por IA foi encontrada no dataset.")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    encontrar_nota_1000_com_ia(NOME_ARQUIVO_JSON)