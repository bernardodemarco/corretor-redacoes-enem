import json
import pandas as pd
import random

class DataLoader:
    def __init__(self, json_path):
        """
        Carrega o banco de dados de redações do arquivo JSON.
        """
        try:
            # Tenta primeiro com 'utf-8-sig' para remover BOM (Byte Order Mark) se existir
            with open(json_path, 'r', encoding='utf-8-sig') as f:
                self.data = json.load(f)
        except UnicodeDecodeError:
            # Se falhar, tenta com 'utf-8' padrão
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.data = json.load()
            except Exception as e:
                print(f"Erro fatal ao ler o arquivo JSON: {e}")
                self.data = []
        except json.JSONDecodeError as e:
            print(f"Erro fatal ao decodificar o JSON. Verifique o arquivo em: {e}")
            self.data = []
        except Exception as e:
            print(f"Erro inesperado ao carregar o arquivo: {e}")
            self.data = []
            
        if self.data:
            print(f"Dataset carregado com sucesso. Total de redações: {len(self.data)}")

    def get_sample(self, n=10, tipo_correcao='Tradicional'):
        """
        Retorna uma amostra aleatória de 'n' redações que tenham 
        a correção humana (tipo_correcao).
        """
        if not self.data:
            print("Nenhum dado carregado. Abortando get_sample.")
            return []
            
        amostra_valida = []
        
        # Filtra redações que possuem a correção que queremos (Humana)
        candidatos = []
        for redacao in self.data:
            if not isinstance(redacao, dict):
                # print(f"Aviso: Item 'redacao' não é um dicionário. Pulando. Conteúdo: {redacao}")
                continue
                
            for correcao in redacao.get('correcoes', []):
                if isinstance(correcao, dict) and correcao.get('tipo') == tipo_correcao:
                    # Adiciona uma checagem para garantir que os detalhes existem
                    if correcao.get('detalhes_competencias') and len(correcao.get('detalhes_competencias')) == 5:
                        candidatos.append((redacao, correcao))
                        break # Pega a primeira correção 'Tradicional' que encontrar
        
        if not candidatos:
            print(f"Erro: Nenhuma redação com correção '{tipo_correcao}' e 5 competências foi encontrada.")
            return []

        if len(candidatos) < n:
            print(f"Aviso: Pediu {n} amostras, mas só {len(candidatos)} encontradas com correção '{tipo_correcao}' e 5 competências.")
            n = len(candidatos)
            
        amostra_aleatoria = random.sample(candidatos, n)
        
        # Prepara os dados de entrada e o ground truth
        amostra_final = []
        for redacao, correcao in amostra_aleatoria:
            input_data = {
                "id": redacao.get('url'), # Usando URL como ID único
                "tema": redacao.get('tema_geral'),
                "texto": redacao.get('texto_original_recuperado')
            }
            
            # Formata o ground truth para fácil acesso
            ground_truth = {
                "nota_final": correcao.get('nota_final'),
                "competencias": {}
            }
            
            # --- INÍCIO DA CORREÇÃO ---
            # Usamos enumerate para pegar o índice (0-4) do array de competências
            detalhes_comps = correcao.get('detalhes_competencias', [])
            for index, comp_detalhe in enumerate(detalhes_comps):
                # O array é 0-indexed (0 a 4), mas as competências são 1-indexed (1 a 5)
                comp_id = index + 1
                
                # Pega os valores de nota e observação do dicionário
                if isinstance(comp_detalhe, dict):
                    ground_truth["competencias"][comp_id] = {
                        "nota": comp_detalhe.get('nota'),
                        "observacao": comp_detalhe.get('observacao')
                    }
                else:
                     print(f"Aviso: 'comp_detalhe' não é um dicionário na redação {input_data['id']}")
            # --- FIM DA CORREÇÃO ---

            # Garante que não estamos adicionando amostras malformadas
            if len(ground_truth["competencias"]) == 5:
                amostra_final.append({
                    "input": input_data,
                    "ground_truth": ground_truth
                })
            else:
                print(f"Aviso: Redação {input_data['id']} pulada por não ter 5 competências detalhadas.")

        return amostra_final

# Exemplo de como usar (para testar se funciona)
if __name__ == "__main__":
    # Assumindo que seu JSON está no mesmo diretório
    # Renomeie 'seu_db_completo.json' para o nome real do seu arquivo
    loader = DataLoader('base_dados.json') 
    
    # Pega 1 redação de amostra
    amostra = loader.get_sample(n=1)
    
    if amostra:
        print("\n--- Exemplo de Amostra Corrigida ---")
        print(json.dumps(amostra[0], indent=2, ensure_ascii=False))
    else:
        print("\nNenhuma amostra válida foi retornada.")