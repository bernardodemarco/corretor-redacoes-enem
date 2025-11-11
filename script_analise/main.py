# coding: utf-8
from data_loader import DataLoader
from llm_provider import GeminiProvider, OpenAIProvider # Importamos os provedores
import metrics # Importamos nosso novo módulo de métricas
import json
import os
import pandas as pd
import time

# --- CONFIGURAÇÕES DA EXECUÇÃO ---
# Ajuste o nome do seu arquivo JSON principal aqui
NOME_ARQUIVO_DB = "base_dados.json"
# Quantas redações aleatórias você quer testar neste lote?
N_AMOSTRAS_TESTE = 5 
# Arquivo de saída para os resultados
ARQUIVO_SAIDA_CSV = "evaluation_results.csv"
# Delay entre chamadas de API (em segundos) para evitar "Rate Limiting"
DELAY_ENTRE_CHAMADAS_API = 1.0 

def carregar_prompt(nome_arquivo):
    """Lê um arquivo de prompt da pasta /prompts."""
    caminho = os.path.join("prompts", nome_arquivo)
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Erro ao carregar prompt: {caminho}. {e}")
        return None

def run_evaluation_batch(n_samples, output_csv):
    """
    Função principal (Fase 6 - Lote).
    Avalia N redações por completo (C1 a C5) e calcula as métricas agregadas.
    """
    
    print("Iniciando execução em lote (Fase 6)...")
    
    # --- 1. Carregar Dados ---
    print(f"\n--- Carregando {n_samples} redações de '{NOME_ARQUIVO_DB}' ---")
    loader = DataLoader(NOME_ARQUIVO_DB)
    amostra_redacoes = loader.get_sample(n=n_samples)
    
    if not amostra_redacoes:
        print("Não foi possível carregar amostra. Verifique o DataLoader e o JSON. Abortando.")
        return
    
    print(f"[OK] {len(amostra_redacoes)} redações carregadas.")

    # --- 2. Inicializar Modelos ---
    modelos_para_testar = [
        GeminiProvider(),
        OpenAIProvider()
    ]

    # --- 3. Loop de Execução ---
    
    # Listas mestras para armazenar TODOS os resultados para o CSV final
    lista_resultados_finais = []
    
    # Listas para métricas agregadas (notas de competências individuais)
    # Vamos armazenar cada par (humano, llm)
    master_scores_competencias = []
    # Lista para métricas de nota final
    master_scores_finais = []

    start_time_total = time.time()
    
    # Loop Principal (N Redações)
    for i, redacao_teste in enumerate(amostra_redacoes):
        input_data = redacao_teste['input']
        ground_truth = redacao_teste['ground_truth']
        redacao_id = input_data['id']
        
        print(f"\n--- [Redação {i+1}/{len(amostra_redacoes)}] ID: {redacao_id} ---")

        # Loop de Modelos (Gemini, GPT, etc)
        for modelo in modelos_para_testar:
            print(f"Avaliando com: {modelo.__class__.__name__} ({modelo.model_name})")
            
            notas_llm_redacao = []
            notas_humano_redacao = []

            # Loop de Competências (C1 a C5)
            for comp_id in range(1, 6):
                # print(f"  Avaliando Competência {comp_id}...") # Log muito verboso
                
                # 3a. Carregar o prompt
                nome_prompt = f"c{comp_id}_zero_shot.txt"
                prompt_texto = carregar_prompt(nome_prompt)
                if not prompt_texto:
                    print(f"[FALHA] Prompt {nome_prompt} não encontrado. Pulando C{comp_id}.")
                    continue
                
                # Adiciona delay para não bater o limite da API
                time.sleep(DELAY_ENTRE_CHAMADAS_API)

                # 3b. Chamar a API
                resultado_json = modelo.get_correction(prompt_texto, input_data['texto'])
                
                if not resultado_json:
                    print(f"[FALHA] API falhou para C{comp_id}. Pulando.")
                    continue

                # 3c. Coletar resultados
                nota_llm = int(resultado_json.get('nota_atribuida', 0))
                nota_h = int(ground_truth['competencias'][comp_id]['nota'])
                
                notas_llm_redacao.append(nota_llm)
                notas_humano_redacao.append(nota_h)
                
                # Adiciona o par de notas à lista mestra de competências
                master_scores_competencias.append({
                    "modelo": modelo.model_name,
                    "humano": nota_h,
                    "llm": nota_llm
                })
                
                # Salva o resultado detalhado para o CSV
                lista_resultados_finais.append({
                    "redacao_id": redacao_id,
                    "modelo": modelo.model_name,
                    "prompt": nome_prompt,
                    "competencia": f"C{comp_id}",
                    "nota_humano": nota_h,
                    "nota_llm": nota_llm,
                    "diferenca": nota_llm - nota_h,
                    "raciocinio_cot": resultado_json.get('raciocinio_cot'),
                    "justificativa_aluno": resultado_json.get('justificativa_para_aluno')
                })
            
            # Fim do loop de competências (C1-C5)
            if len(notas_llm_redacao) == 5:
                # Se todas as 5 competências foram avaliadas, calcula os totais
                total_humano = sum(notas_humano_redacao)
                total_llm = sum(notas_llm_redacao)
                
                # Adiciona os totais à lista mestra de notas finais
                master_scores_finais.append({
                    "modelo": modelo.model_name,
                    "humano": total_humano,
                    "llm": total_llm
                })
                print(f"  -> Concluído. Nota Humano: {total_humano} | Nota LLM: {total_llm}")
            else:
                print(f"  -> Incompleto. Não foi possível calcular nota final.")
    
    # --- 4. Fim dos Loops (Salvando Resultados) ---
    end_time_total = time.time()
    print(f"\n--- Execução em Lote Concluída ---")
    print(f"Tempo total: {end_time_total - start_time_total:.2f} segundos")
    print(f"Total de redações avaliadas: {len(amostra_redacoes)}")
    print(f"Total de avaliações de competências: {len(lista_resultados_finais)}")

    if not lista_resultados_finais:
        print("Nenhum resultado foi gerado. Abortando.")
        return

    # 4a. Criar e Salvar o DataFrame
    df = pd.DataFrame(lista_resultados_finais)
    try:
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"\n[OK] Resultados detalhados salvos em '{output_csv}'")
    except Exception as e:
        print(f"\n[FALHA] Não foi possível salvar o CSV: {e}")

    # --- 5. Exibir Métricas Agregadas ---
    print("\n--- Métricas de Desempenho Agregadas (vs. Humano) ---")
    
    # Agrupamos por modelo para calcular as métricas
    df_scores_comp = pd.DataFrame(master_scores_competencias)
    df_scores_final = pd.DataFrame(master_scores_finais)
    
    for modelo_nome in df_scores_comp['modelo'].unique():
        print(f"\nModelo: {modelo_nome}")
        
        # Filtra os scores para este modelo
        scores_comp_modelo = df_scores_comp[df_scores_comp['modelo'] == modelo_nome]
        scores_final_modelo = df_scores_final[df_scores_final['modelo'] == modelo_nome]
        
        # Listas de notas
        human_comp_scores = scores_comp_modelo['humano']
        llm_comp_scores = scores_comp_modelo['llm']
        human_final_scores = scores_final_modelo['humano']
        llm_final_scores = scores_final_modelo['llm']

        if len(human_comp_scores) > 1 and len(human_final_scores) > 0:
            # Métricas (Competências)
            qwk = metrics.calculate_qwk(human_comp_scores, llm_comp_scores)
            r, p = metrics.calculate_pearson(human_comp_scores, llm_comp_scores)
            adj_comp = metrics.calculate_adjacent_agreement(human_comp_scores, llm_comp_scores, threshold=80)
            
            n_comp = len(human_comp_scores)
            print(f"  Resultados (Nível Competência, n={n_comp}):")
            print(f"    QWK:                 {qwk:.4f}")
            print(f"    Pearson (r):         {r:.4f}")
            print(f"    Adjacent Agr. (80p): {adj_comp:.2%}")

            # Métricas (Nota Final)
            adj_final = metrics.calculate_adjacent_agreement(human_final_scores, llm_final_scores, threshold=100)
            
            n_final = len(human_final_scores)
            print(f"  Resultados (Nível Nota Final, n={n_final}):")
            print(f"    Adjacent Agr. (100p):{adj_final:.2%}")
            
            # Pearson da nota final (só se tivermos > 1 redação)
            if n_final > 1:
                r_final, p_final = metrics.calculate_pearson(human_final_scores, llm_final_scores)
                print(f"    Pearson (r) Final:   {r_final:.4f}")
        else:
            print("  Dados insuficientes para calcular métricas agregadas.")


if __name__ == "__main__":
    # Certifique-se que o nome do arquivo JSON está correto
    if not os.path.exists(NOME_ARQUIVO_DB):
        print(f"Erro: Arquivo '{NOME_ARQUIVO_DB}' não encontrado.")
        print(f"Por favor, renomeie '{NOME_ARQUIVO_DB}' no script 'main.py' para o nome correto.")
    else:
        run_evaluation_batch(n_samples=N_AMOSTRAS_TESTE, output_csv=ARQUIVO_SAIDA_CSV)