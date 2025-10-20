import json

# --- CONFIGURAÇÃO ---
# Nome do arquivo JSON grande e completo gerado pelo scraper.
ARQUIVO_ENTRADA = "dados_completos_brasilescola.json" 

# Nome do novo arquivo que será gerado, contendo apenas os dados limpos.
ARQUIVO_SAIDA = "dados_limpos_brasilescola.json"
# --------------------

def limpar_dados(dados):
    """
    Processa os dados, removendo redações com sistema de nota antigo (0-10).
    Retorna a estrutura de dados limpa e estatísticas da limpeza.
    """
    dados_limpos = []
    total_redacoes_lidas = 0
    total_redacoes_removidas = 0

    # Itera sobre cada tema na lista principal
    for tema in dados:
        total_redacoes_lidas += len(tema.get('redacoes', []))
        
        redacoes_validas = []
        # Itera sobre cada redação dentro de um tema
        for redacao in tema.get('redacoes', []):
            manter_redacao = True # Começamos assumindo que a redação é válida
            
            # Verifica a existência da correção tradicional e da nota final
            correcao = redacao.get('correcao_tradicional')
            if correcao and 'nota_final' in correcao and isinstance(correcao['nota_final'], int):
                
                # AQUI ESTÁ A LÓGICA PRINCIPAL:
                # Se a nota final for 10 ou menos, é do sistema antigo e será removida.
                if correcao['nota_final'] <= 10:
                    manter_redacao = False
                    total_redacoes_removidas += 1
            
            if manter_redacao:
                redacoes_validas.append(redacao)

        # Se o tema ainda tiver redações válidas após a limpeza, nós o mantemos.
        if redacoes_validas:
            tema['redacoes'] = redacoes_validas # Substitui a lista de redações pela lista limpa
            dados_limpos.append(tema)

    return dados_limpos, total_redacoes_lidas, total_redacoes_removidas

if __name__ == "__main__":
    try:
        print(f"Lendo o arquivo de dados: '{ARQUIVO_ENTRADA}'...")
        with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f:
            dados_originais = json.load(f)
        
        print("Iniciando processo de limpeza...")
        dados_limpos, lidas, removidas = limpar_dados(dados_originais)
        
        print("Salvando o novo arquivo limpo...")
        with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
            json.dump(dados_limpos, f, ensure_ascii=False, indent=4)
            
        # --- Relatório Final da Limpeza ---
        print(f"\n{'='*50}")
        print(" LIMPEZA CONCLUÍDA COM SUCESSO!")
        print(f"{'='*50}")
        print(f"Total de redações lidas: {lidas}")
        print(f"Redações removidas (com nota antiga): {removidas}")
        print(f"Total de redações válidas restantes: {lidas - removidas}")
        print(f"\nO arquivo limpo foi salvo como: '{ARQUIVO_SAIDA}'")
        print(f"{'='*50}\n")

    except FileNotFoundError:
        print(f"Erro: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        print("Verifique se o nome do arquivo está correto e na mesma pasta.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")