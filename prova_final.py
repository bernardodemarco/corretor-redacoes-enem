import json
import numpy as np

NOME_ARQUIVO_JSON = "DADOS_UNIFICADOS.json"

def visualizar_distribuicao_completa(dados):
    diferencas = []
    
    for tema in dados:
        if tema.get('fonte') == 'Brasil Escola':
            for redacao in tema.get('redacoes', []):
                correcoes = redacao.get('correcoes', [])
                nota_ia, nota_trad = None, None
                
                for c in correcoes:
                    if c.get('tipo') == 'IA': nota_ia = c.get('nota_final')
                    if c.get('tipo') == 'Tradicional': nota_trad = c.get('nota_final')

                if nota_ia is not None and nota_trad is not None:
                    try:
                        diferenca = int(nota_ia) - int(nota_trad)
                        diferencas.append(diferenca)
                    except (ValueError, TypeError):
                        continue

    if not diferencas:
        print("Nenhuma redação comparável encontrada.")
        return

    # Ordena a lista de diferenças
    diferencas_ordenadas = sorted(diferencas)

    print(f"\nTotal de amostras analisadas: {len(diferencas_ordenadas)}")

    print(f"\n{'='*70}")
    print(" ANÁLISE DOS CASOS EXTREMOS (OUTLIERS)")
    print(f"{'='*70}")

    print("\n--- As 15 MAIORES diferenças negativas (IA mais rígida) ---")
    print(diferencas_ordenadas[:15])

    print("\n--- As 15 MAIORES diferenças positivas (IA mais generosa) ---")
    print(diferencas_ordenadas[-15:])

    # Recalcula as métricas para confirmar
    media = np.mean(diferencas)
    mediana = np.median(diferencas)
    
    print(f"\n{'='*70}")
    print(" MÉTRICAS CONFIRMADAS")
    print(f"{'='*70}")
    print(f"  - Média:   {media:.2f}")
    print(f"  - Mediana: {mediana:.2f}")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    try:
        with open(NOME_ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            print(f"Lendo e analisando o arquivo '{NOME_ARQUIVO_JSON}'...")
            dados_json = json.load(f)
        visualizar_distribuicao_completa(dados_json)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{NOME_ARQUIVO_JSON}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")