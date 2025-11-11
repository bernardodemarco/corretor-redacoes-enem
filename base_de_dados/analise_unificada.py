import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# --- CONFIGURAÇÃO ---
NOME_ARQUIVO_JSON = "DADOS_UNIFICADOS.json"
NOME_GRAFICO_FONTES = "boxplot_fontes.png"
NOME_GRAFICO_COMPETENCIAS = "boxplot_competencias.png"
# --------------------


def imprimir_estatisticas_notas(titulo, notas):
    """Função auxiliar para imprimir um bloco de estatísticas de uma lista de notas."""
    if not notas:
        print(f"  Nenhuma nota encontrada para '{titulo}'.")
        return
    
    print(f"--- {titulo} ---")
    print(f"  - Média:            {np.mean(notas):.2f}")
    print(f"  - Mediana:          {np.median(notas):.2f}")
    print(f"  - Desvio Padrão:    {np.std(notas):.2f}")
    print(f"  - Maior Nota:       {np.max(notas)}")
    print(f"  - Menor Nota:       {np.min(notas)}")
    print(f"  - Total de Amostras: {len(notas)}")

def gerar_boxplot_por_fonte(notas_uol, notas_be):
    """Gera e salva um boxplot comparando as notas das duas fontes."""
    print(f"\n--- GERANDO BOXPLOT (FONTES) ---")
    
    dados_uol = pd.DataFrame({'nota_final': notas_uol, 'fonte': 'UOL Educação'})
    dados_be = pd.DataFrame({'nota_final': notas_be, 'fonte': 'Brasil Escola'})
    df_completo = pd.concat([dados_uol, dados_be])

    plt.figure(figsize=(10, 6))
    sns.boxplot(x='fonte', y='nota_final', data=df_completo, palette="pastel")
    plt.title('Distribuição das Notas Finais por Fonte (Correção Tradicional)', fontsize=16)
    plt.xlabel('Fonte dos Dados', fontsize=12)
    plt.ylabel('Nota Final (0-1000)', fontsize=12)
    
    try:
        plt.savefig(NOME_GRAFICO_FONTES, dpi=300, bbox_inches='tight')
        print(f"  - Sucesso! Gráfico salvo como '{NOME_GRAFICO_FONTES}'")
    except Exception as e:
        print(f"  - Erro ao salvar gráfico: {e}")
    plt.close() # Fecha a figura para liberar memória

def gerar_boxplot_por_competencia(notas_por_comp_geral):
    """
    NOVA FUNÇÃO: Gera e salva um boxplot comparando as notas das 5 competências.
    """
    print(f"\n--- GERANDO BOXPLOT (COMPETÊNCIAS) ---")
    
    # 1. Preparar os dados para o Seaborn (converter dict para DataFrame longo)
    dados_comps = []
    for i, notas in notas_por_comp_geral.items():
        if notas:
            dados_comps.append(pd.DataFrame({
                'Nota': notas,
                'Competência': f'C{i}' # Adiciona o "C" para C1, C2...
            }))
    
    if not dados_comps:
        print("  - Nenhum dado de competência encontrado para gerar o gráfico.")
        return
        
    df_completo = pd.concat(dados_comps)

    # 2. Criar o gráfico
    plt.figure(figsize=(12, 7))
    sns.boxplot(
        x='Competência', 
        y='Nota', 
        data=df_completo,
        palette="viridis"
    )
    
    # 3. Adicionar títulos e labels
    plt.title('Distribuição das Notas por Competência (Geral)', fontsize=16)
    plt.xlabel('Competências do ENEM', fontsize=12)
    plt.ylabel('Nota da Competência (0-200)', fontsize=12)
    plt.ylim(0, 200) # Fixa o eixo Y na escala correta de 0-200
    
    # 4. Salvar e mostrar
    try:
        plt.savefig(NOME_GRAFICO_COMPETENCIAS, dpi=300, bbox_inches='tight')
        print(f"  - Sucesso! Gráfico salvo como '{NOME_GRAFICO_COMPETENCIAS}'")
    except Exception as e:
        print(f"  - Erro ao salvar gráfico: {e}")
    plt.close() # Fecha a figura


def analisar_dados(dados):
    """
    Função principal que recebe os dados carregados e gera o relatório estatístico completo.
    """
    # 1. Pré-processamento
    todas_redacoes = []
    for tema in dados:
        for redacao in tema.get('redacoes', []):
            redacao_plana = redacao.copy()
            redacao_plana['fonte'] = tema['fonte']
            redacao_plana['tema_geral'] = tema['tema_geral']
            todas_redacoes.append(redacao_plana)
            
    total_temas = len(dados)
    total_redacoes = len(todas_redacoes)
    redacoes_uol = [r for r in todas_redacoes if r['fonte'] == 'UOL Educação']
    redacoes_be = [r for r in todas_redacoes if r['fonte'] == 'Brasil Escola']

    # --- INÍCIO DO RELATÓRIO ---
    print(f"\n{'='*70}")
    print(" ANÁLISE ESTATÍSTICA COMPLETA DO DATASET UNIFICADO")
    print(f"{'='*70}")

    # 2. Balanço Geral
    print("\n--- 1. BALANÇO GERAL DA COLETA ---")
    print(f"Total de Temas no Dataset: {total_temas}")
    print(f"Total de Redações no Dataset: {total_redacoes}")
    print(f"  - Redações de 'UOL Educação': {len(redacoes_uol)}")
    print(f"  - Redações de 'Brasil Escola': {len(redacoes_be)}")

    # 3. Análise de Notas (Tradicional)
    print("\n--- 2. ANÁLISE DAS NOTAS FINAIS (CORREÇÃO TRADICIONAL) ---")
    notas_trad_uol = [c['nota_final'] for r in redacoes_uol for c in r.get('correcoes', []) if c.get('tipo') == 'Tradicional' and c.get('nota_final') is not None]
    notas_trad_be = [c['nota_final'] for r in redacoes_be for c in r.get('correcoes', []) if c.get('tipo') == 'Tradicional' and c.get('nota_final') is not None]
    notas_trad_total = notas_trad_uol + notas_trad_be
    
    # ... (impressão das estatísticas) ...
    imprimir_estatisticas_notas("Geral (Todas as Fontes)", notas_trad_total)
    print("-" * 20)
    imprimir_estatisticas_notas("Fonte: UOL Educação", notas_trad_uol)
    print("-" * 20)
    imprimir_estatisticas_notas("Fonte: Brasil Escola", notas_trad_be)
    
    # CHAMADA DO GRÁFICO 1
    gerar_boxplot_por_fonte(notas_trad_uol, notas_trad_be)


    # 4. Análise por Competências (Tradicional)
    print("\n--- 3. ANÁLISE DAS NOTAS POR COMPETÊNCIA (CORREÇÃO TRADICIONAL) ---")
    notas_por_comp = {'Geral': {i: [] for i in range(1, 6)}, 'UOL Educação': {i: [] for i in range(1, 6)}, 'Brasil Escola': {i: [] for i in range(1, 6)}}
    for r in todas_redacoes:
        for c in r.get('correcoes', []):
            if c.get('tipo') == 'Tradicional':
                for i, detalhe_comp in enumerate(c.get('detalhes_competencias', [])):
                    if i < 5 and isinstance(detalhe_comp.get('nota'), int):
                        notas_por_comp['Geral'][i + 1].append(detalhe_comp['nota'])
                        notas_por_comp[r['fonte']][i + 1].append(detalhe_comp['nota'])
    
    # ... (impressão das estatísticas) ...
    print("--- Média Geral por Competência ---")
    for i, notas in notas_por_comp['Geral'].items():
        if notas: print(f"  - Competência {i}: {np.mean(notas):.2f}")
    
    # CHAMADA DO GRÁFICO 2
    gerar_boxplot_por_competencia(notas_por_comp['Geral'])
        
    print("\n--- Média por Competência (Por Fonte) ---")
    for i in range(1, 6):
        media_uol = np.mean(notas_por_comp['UOL Educação'][i]) if notas_por_comp['UOL Educação'][i] else 'N/A'
        media_be = np.mean(notas_por_comp['Brasil Escola'][i]) if notas_por_comp['Brasil Escola'][i] else 'N/A'
        if isinstance(media_uol, float) and isinstance(media_be, float):
            print(f"  - Competência {i}: UOL ({media_uol:.2f}) vs. Brasil Escola ({media_be:.2f})")
        else:
             print(f"  - Competência {i}: UOL ({media_uol}) vs. Brasil Escola ({media_be})")

    # 5. Análise Completa da Correção por IA ...
    # ... (O resto do script continua igual) ...
    print("\n--- 4. ANÁLISE APROFUNDADA DA EFICÁCIA DA IA vs. TRADICIONAL ---")
    dados_comparativos = []
    for r in redacoes_be:
        correcoes = r.get('correcoes', [])
        corr_ia = next((c for c in correcoes if c.get('tipo') == 'IA'), None)
        corr_trad = next((c for c in correcoes if c.get('tipo') == 'Tradicional'), None)
        if corr_ia and corr_trad and corr_ia.get('nota_final') is not None and corr_trad.get('nota_final') is not None:
            dados_comparativos.append({'url': r.get('url'), 'nota_ia': corr_ia['nota_final'], 'nota_trad': corr_trad['nota_final'], 'comps_ia': corr_ia.get('detalhes_competencias', []), 'comps_trad': corr_trad.get('detalhes_competencias', [])})

    print(f"(Baseado em {len(dados_comparativos)} redações com ambas as correções do Brasil Escola)")
    
    if dados_comparativos:
        diferencas = [d['nota_ia'] - d['nota_trad'] for d in dados_comparativos]
        print("\n--- 4.1 Métricas Gerais de Comparação ---")
        imprimir_estatisticas_notas("Notas Finais da IA", [d['nota_ia'] for d in dados_comparativos])
        print("\n  --- Diferença (IA - Tradicional) ---")
        print(f"    - Média da Diferença:   {np.mean(diferencas):+.2f} pontos")
        print(f"    - Mediana da Diferença: {np.median(diferencas):+.2f} pontos")
        
        concordancia_nota_final = sum(1 for d in dados_comparativos if d['nota_ia'] == d['nota_trad'])
        print("\n--- 4.2 Análise de Concordância Absoluta (Nota Exata) ---")
        print(f"  - Nota Final Idêntica: {concordancia_nota_final} vezes ({concordancia_nota_final/len(dados_comparativos):.2%})")
        for i in range(5):
            concordancia_comp = sum(1 for d in dados_comparativos if len(d['comps_ia']) > i and len(d['comps_trad']) > i and d['comps_ia'][i].get('nota') == d['comps_trad'][i].get('nota'))
            print(f"  - Competência {i+1} Idêntica: {concordancia_comp} vezes ({concordancia_comp/len(dados_comparativos):.2%})")

        print("\n--- 4.3 Discrepância Média por Competência (IA - Tradicional) ---")
        for i in range(5):
            diferencas_comp = [d['comps_ia'][i].get('nota', 0) - d['comps_trad'][i].get('nota', 0) for d in dados_comparativos if len(d['comps_ia']) > i and len(d['comps_trad']) > i]
            if diferencas_comp: print(f"  - Competência {i+1}: {np.mean(diferencas_comp):+.2f} pontos")

        print("\n--- 4.4 Maiores Discordâncias Encontradas (Outliers) ---")
        diferencas_ordenadas = sorted(dados_comparativos, key=lambda x: x['nota_ia'] - x['nota_trad'])
        if diferencas_ordenadas:
            maior_negativa = diferencas_ordenadas[0]
            maior_positiva = diferencas_ordenadas[-1]
            print(f"  - Maior discordância (IA mais rígida): {maior_negativa['nota_ia'] - maior_negativa['nota_trad']} pontos no link: {maior_negativa['url']}")
            print(f"  - Maior discordância (IA mais generosa): {maior_positiva['nota_ia'] - maior_positiva['nota_trad']:+} pontos no link: {maior_positiva['url']}")

    print("\n--- 5. ANÁLISE DOS TEMAS ---")
    contagem_temas = Counter(r['tema_geral'] for r in todas_redacoes)
    print("\n--- Top 10 Temas com Mais Redações ---")
    for tema, contagem in contagem_temas.most_common(10):
        print(f"  {contagem} redações - {tema}")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        import numpy
        import pandas
        import matplotlib
        import seaborn
    except ImportError as e:
        print(f"Erro: Biblioteca necessária não encontrada: {e}")
        print("Instale com: pip install numpy pandas matplotlib seaborn")
        exit()
        
    try:
        with open(NOME_ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            print(f"Lendo e analisando o arquivo '{NOME_ARQUIVO_JSON}'...")
            dados_json = json.load(f)
        analisar_dados(dados_json)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{NOME_ARQUIVO_JSON}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")