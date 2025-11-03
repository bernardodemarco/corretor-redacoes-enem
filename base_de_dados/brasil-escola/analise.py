import json
import numpy as np # Biblioteca para cálculos estatísticos (média, desvio padrão)
from collections import Counter # Para contagem de frequências

# --- CONFIGURAÇÃO ---
# Coloque aqui o nome do arquivo JSON gerado pelo seu scraper.
NOME_ARQUIVO_JSON = "dados_limpos_brasilescola.json" 
# --------------------

def analisar_dados(dados):
    """
    Função principal que recebe os dados carregados do JSON e gera as estatísticas.
    """
    total_temas = len(dados)
    todas_redacoes = [redacao for tema in dados for redacao in tema.get('redacoes', [])]
    total_redacoes = len(todas_redacoes)

    # --- Estatísticas de Coleta ---
    print(f"\n{'='*60}")
    print(" BALANÇO GERAL DA COLETA DE DADOS")
    print(f"{'='*60}")
    print(f"Total de Temas Processados: {total_temas}")
    print(f"Total de Redações Coletadas: {total_redacoes}")

    redacoes_com_ia = [r for r in todas_redacoes if r.get('correcao_ia')]
    redacoes_com_tradicional = [r for r in todas_redacoes if r.get('correcao_tradicional')]
    
    print(f"\n- Redações com Correção Tradicional: {len(redacoes_com_tradicional)} ({len(redacoes_com_tradicional)/total_redacoes:.1%})")
    print(f"- Redações com Correção por IA: {len(redacoes_com_ia)} ({len(redacoes_com_ia)/total_redacoes:.1%})")

    # --- Análise das Notas (Correção Tradicional) ---
    notas_tradicionais = [
        r['correcao_tradicional']['nota_final'] 
        for r in redacoes_com_tradicional 
        if r['correcao_tradicional'] and 'nota_final' in r['correcao_tradicional'] and isinstance(r['correcao_tradicional']['nota_final'], int)
    ]
    
    if notas_tradicionais:
        print(f"\n\n{'='*60}")
        print(" ANÁLISE DAS NOTAS - CORREÇÃO TRADICIONAL")
        print(f"{'='*60}")
        print(f"Nota Média: {np.mean(notas_tradicionais):.2f}")
        print(f"Mediana das Notas: {np.median(notas_tradicionais):.2f}")
        print(f"Desvio Padrão: {np.std(notas_tradicionais):.2f}")
        print(f"Maior Nota: {np.max(notas_tradicionais)}")
        print(f"Menor Nota: {np.min(notas_tradicionais)}")
        
        # Análise por competência
        print("\n--- Média por Competência (Tradicional) ---")
        notas_por_competencia = {i: [] for i in range(1, 6)}

        for r in redacoes_com_tradicional:
            if r.get('correcao_tradicional') and r['correcao_tradicional'].get('competencias'):
                for idx, comp in enumerate(r['correcao_tradicional']['competencias']):
                    if idx < 5: # Garante que estamos pegando apenas as 5 competências
                        notas_por_competencia[idx + 1].append(comp.get('nota', 0))

        for i, notas in notas_por_competencia.items():
            if notas:
                # O nome da competência pode variar, então usamos um genérico "Competência X"
                nome_competencia = f"Competência {i}"
                print(f"{nome_competencia}: {np.mean(notas):.2f}")

    # --- Análise das Notas (Correção por IA) ---
    notas_ia = [
        r['correcao_ia']['nota_final_ia'] 
        for r in redacoes_com_ia 
        if r.get('correcao_ia') and 'nota_final_ia' in r['correcao_ia'] and isinstance(r['correcao_ia']['nota_final_ia'], int)
    ]

    if notas_ia:
        print(f"\n\n{'='*60}")
        print(" ANÁLISE DAS NOTAS - CORREÇÃO POR IA")
        print(f"{'='*60}")
        print(f"Nota Média (IA): {np.mean(notas_ia):.2f}")
        print(f"Mediana das Notas (IA): {np.median(notas_ia):.2f}")
        print(f"Desvio Padrão (IA): {np.std(notas_ia):.2f}")
        print(f"Maior Nota (IA): {np.max(notas_ia)}")
        print(f"Menor Nota (IA): {np.min(notas_ia)}")

        # Análise por competência da IA
        print("\n--- Média por Competência (IA) ---")
        notas_por_competencia_ia = {f"Competência {i}": [] for i in range(1, 6)}

        for r in redacoes_com_ia:
            if r.get('correcao_ia') and r['correcao_ia'].get('competencias'):
                for comp in r['correcao_ia']['competencias']:
                    nome_comp = comp.get('competencia')
                    if nome_comp in notas_por_competencia_ia:
                        notas_por_competencia_ia[nome_comp].append(comp.get('nota', 0))

        for nome, notas in notas_por_competencia_ia.items():
            if notas:
                print(f"{nome}: {np.mean(notas):.2f}")


    # --- Temas com mais e menos redações ---
    print(f"\n\n{'='*60}")
    print(" ANÁLISE DOS TEMAS")
    print(f"{'='*60}")
    
    contagem_redacoes_por_tema = {tema['tema_geral']: len(tema.get('redacoes', [])) for tema in dados}
    
    # Ordena os temas pela quantidade de redações, do maior para o menor
    temas_ordenados = sorted(contagem_redacoes_por_tema.items(), key=lambda item: item[1], reverse=True)
    
    print("\n--- Top 5 Temas com Mais Redações ---")
    for tema, contagem in temas_ordenados[:5]:
        print(f"{contagem} redações - {tema}")
        
    print("\n--- 5 Temas com Menos Redações ---")
    # Filtra temas com 0 redações para não poluir a lista
    temas_com_redacoes = [item for item in temas_ordenados if item[1] > 0]
    for tema, contagem in temas_com_redacoes[-5:]:
        print(f"{contagem} redações - {tema}")
        
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    try:
        # Tenta carregar o numpy, que é necessário para as estatísticas
        import numpy
    except ImportError:
        print("Erro: A biblioteca 'numpy' é necessária para executar esta análise.")
        print("Por favor, instale-a com o comando: pip install numpy")
        exit()

    try:
        with open(NOME_ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            print(f"Lendo o arquivo '{NOME_ARQUIVO_JSON}'...")
            dados_json = json.load(f)
        analisar_dados(dados_json)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{NOME_ARQUIVO_JSON}' não encontrado.")
        print("Verifique se o nome do arquivo está correto e se ele está na mesma pasta que este script.")
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{NOME_ARQUIVO_JSON}' parece estar corrompido ou não é um JSON válido.")