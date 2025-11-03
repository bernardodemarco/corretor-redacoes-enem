import json

# --- CONFIGURAÇÃO ---
ARQUIVO_UOL = "uol/todas_as_redacoes_uol_final.json"
ARQUIVO_BRASIL_ESCOLA = "brasil-escola/dados_limpos_brasilescola.json"
ARQUIVO_SAIDA = "DADOS_UNIFICADOS.json"
# --------------------

def processar_dados_uol(dados):
    """Converte os dados do formato UOL para o formato padronizado."""
    dados_padronizados = []
    total_redacoes = 0
    
    for tema_uol in dados:
        tema_novo = {
            "tema_geral": tema_uol.get("tema_geral"),
            "url_tema": tema_uol.get("url_tema"),
            "fonte": "UOL Educação",
            "redacoes": []
        }
        
        for redacao_uol in tema_uol.get('redacoes', []):
            total_redacoes += 1
            
            # Mapeia as notas e comentários de competências para um formato único
            detalhes_competencias = []
            notas = [nc for nc in redacao_uol.get('notas_competencias', []) if 'final' not in nc.get('competencia', '').lower()]
            comentarios = redacao_uol.get('comentarios_competencias', [])
            
            for i in range(len(notas)):
                detalhes_competencias.append({
                    "competencia": notas[i].get('competencia'),
                    "nota": notas[i].get('nota'),
                    "observacao": comentarios[i] if i < len(comentarios) else ""
                })

            correcao_padronizada = {
                "tipo": "Tradicional",
                "nota_final": redacao_uol.get('nota_final'),
                "comentario_geral": redacao_uol.get('comentario_geral'),
                "detalhes_competencias": detalhes_competencias
            }
            
            redacao_nova = {
                "titulo": redacao_uol.get('titulo'),
                "url": redacao_uol.get('url'),
                "texto_html_corrigido": redacao_uol.get('texto_redacao_html'),
                "correcoes": [correcao_padronizada]
            }
            tema_novo['redacoes'].append(redacao_nova)
        
        dados_padronizados.append(tema_novo)
        
    print(f"Processados {len(dados)} temas e {total_redacoes} redações do arquivo UOL.")
    return dados_padronizados

def processar_dados_brasil_escola(dados):
    """Converte os dados do formato Brasil Escola para o formato padronizado."""
    dados_padronizados = []
    total_redacoes = 0
    
    for tema_be in dados:
        tema_novo = {
            "tema_geral": tema_be.get("tema_geral"),
            "url_tema": tema_be.get("url_tema"),
            "fonte": "Brasil Escola",
            "redacoes": []
        }
        
        for redacao_be in tema_be.get('redacoes', []):
            total_redacoes += 1
            
            redacao_nova = {
                "titulo": redacao_be.get('titulo_redacao'),
                "url": redacao_be.get('url_redacao'),
                "texto_html_corrigido": redacao_be.get('texto_html_corrigido'),
                "correcoes": []
            }
            
            # Processa a correção tradicional, se existir
            corr_trad = redacao_be.get('correcao_tradicional')
            if corr_trad:
                detalhes_trad = []
                for comp in corr_trad.get('competencias', []):
                    detalhes_trad.append({
                        "competencia": comp.get('competencia'),
                        "nota": comp.get('nota'),
                        "observacao": comp.get('motivo') # Renomeando 'motivo' para 'observacao'
                    })
                
                redacao_nova['correcoes'].append({
                    "tipo": "Tradicional",
                    "nota_final": corr_trad.get('nota_final'),
                    "comentario_geral": corr_trad.get('comentario_geral'),
                    "detalhes_competencias": detalhes_trad
                })

            # Processa a correção por IA, se existir
            corr_ia = redacao_be.get('correcao_ia')
            if corr_ia:
                detalhes_ia = []
                for comp in corr_ia.get('competencias', []):
                    detalhes_ia.append({
                        "competencia": comp.get('competencia'),
                        "nota": comp.get('nota'),
                        "observacao": comp.get('observacao')
                    })

                redacao_nova['correcoes'].append({
                    "tipo": "IA",
                    "nota_final": corr_ia.get('nota_final_ia'),
                    "comentario_geral": corr_ia.get('comentario_geral_ia'),
                    "detalhes_competencias": detalhes_ia
                })
            
            tema_novo['redacoes'].append(redacao_nova)
            
        dados_padronizados.append(tema_novo)
        
    print(f"Processados {len(dados)} temas e {total_redacoes} redações do arquivo Brasil Escola.")
    return dados_padronizados


if __name__ == "__main__":
    dados_unificados = []

    # Carrega e processa o primeiro arquivo
    try:
        print(f"Lendo o arquivo '{ARQUIVO_UOL}'...")
        with open(ARQUIVO_UOL, 'r', encoding='utf-8') as f:
            dados_uol = json.load(f)
        dados_unificados.extend(processar_dados_uol(dados_uol))
    except FileNotFoundError:
        print(f"AVISO: Arquivo '{ARQUIVO_UOL}' não encontrado. Pulando.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar '{ARQUIVO_UOL}': {e}")

    # Carrega e processa o segundo arquivo
    try:
        print(f"\nLendo o arquivo '{ARQUIVO_BRASIL_ESCOLA}'...")
        with open(ARQUIVO_BRASIL_ESCOLA, 'r', encoding='utf-8') as f:
            dados_be = json.load(f)
        dados_unificados.extend(processar_dados_brasil_escola(dados_be))
    except FileNotFoundError:
        print(f"AVISO: Arquivo '{ARQUIVO_BRASIL_ESCOLA}' não encontrado. Pulando.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar '{ARQUIVO_BRASIL_ESCOLA}': {e}")
        
    # Salva o resultado final
    print(f"\nSalvando dados unificados em '{ARQUIVO_SAIDA}'...")
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        json.dump(dados_unificados, f, ensure_ascii=False, indent=4)
        
    total_temas_final = len(dados_unificados)
    total_redacoes_final = sum(len(tema.get('redacoes', [])) for tema in dados_unificados)

    print(f"\n{'='*50}")
    print(" UNIFICAÇÃO CONCLUÍDA!")
    print(f"{'='*50}")
    print(f"Total de temas no arquivo final: {total_temas_final}")
    print(f"Total de redações no arquivo final: {total_redacoes_final}")
    print(f"Arquivo salvo como: '{ARQUIVO_SAIDA}'")
    print(f"{'='*50}\n")