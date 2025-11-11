# coding: utf-8
from sklearn.metrics import cohen_kappa_score
from scipy.stats import pearsonr
import numpy as np

def calculate_qwk(human_scores, llm_scores):
    """
    Calcula o Quadratic Weighted Kappa (QWK).
    Espera duas listas de notas (int ou float).
    """
    try:
        # Garante que os dados sejam numpy arrays
        human_scores = np.array(human_scores)
        llm_scores = np.array(llm_scores)
        
        # 'quadratic' é o que define o QWK
        return cohen_kappa_score(human_scores, llm_scores, weights='quadratic')
    except Exception as e:
        print(f"Erro ao calcular QWK: {e}")
        return None

def calculate_pearson(human_scores, llm_scores):
    """
    Calcula o Coeficiente de Correlação de Pearson (r).
    Espera duas listas de notas (int ou float).
    """
    try:
        # Garante que os dados sejam numpy arrays
        human_scores = np.array(human_scores)
        llm_scores = np.array(llm_scores)
        
        # Retorna o coeficiente (r) e o p-valor
        r, p_value = pearsonr(human_scores, llm_scores)
        return r, p_value
    except Exception as e:
        print(f"Erro ao calcular Pearson: {e}")
        return None

def calculate_adjacent_agreement(human_scores, llm_scores, threshold=100):
    """
    Calcula a Proporção de Adjacent Agreement.
    Verifica a % de notas onde a diferença absoluta é <= threshold.
    
    Para notas de competência, usaremos threshold=80 (conforme seu relatório).
    Para a nota final, usaremos threshold=100.
    """
    try:
        human_scores = np.array(human_scores)
        llm_scores = np.array(llm_scores)
        
        diff = np.abs(human_scores - llm_scores)
        agreement_count = np.sum(diff <= threshold)
        
        proportion = agreement_count / len(human_scores)
        return proportion
    except Exception as e:
        print(f"Erro ao calcular Adjacent Agreement: {e}")
        return None

# Teste local
if __name__ == "__main__":
    # Notas de exemplo (5 competências)
    notas_humanas = [160, 200, 120, 160, 200] # Total: 840
    notas_llm_boas = [160, 160, 160, 160, 160] # Total: 800
    
    print("--- Testando Módulo de Métricas ---")
    
    # QWK
    qwk = calculate_qwk(notas_humanas, notas_llm_boas)
    print(f"QWK: {qwk:.4f}") # Esperado: ~0.4 (Moderado)
    
    # Pearson
    r, p = calculate_pearson(notas_humanas, notas_llm_boas)
    print(f"Pearson (r): {r:.4f} (p-value: {p:.4f})") # Esperado: ~0.5
    
    # Adjacent Agreement (Competências, threshold=80)
    # Diferenças: [0, 40, 40, 0, 40]
    # Todas as diferenças são <= 80, então deve ser 100% (ou 1.0)
    adj_comp = calculate_adjacent_agreement(notas_humanas, notas_llm_boas, threshold=80)
    print(f"Adjacent Agreement (Competências, 80pts): {adj_comp:.2%}")
    
    # Adjacent Agreement (Nota Final, threshold=100)
    # Diferença: |840 - 800| = 40
    # A diferença é <= 100, então deve ser 100% (ou 1.0)
    adj_final = calculate_adjacent_agreement([840], [800], threshold=100)
    print(f"Adjacent Agreement (Nota Final, 100pts): {adj_final:.2%}")