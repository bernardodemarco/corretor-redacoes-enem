import json
import pandas as pd
import random
import sys

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
        brasil_escola_map = {
            "0-500": [],
            "501-800": [],
            "801-1000": []
        }
        educacao_uol_map = {
            "0-500": [],
            "501-800": [],
            "801-1000": []
        }
        for redacao in self.data:
            if not isinstance(redacao, dict):
                # print(f"Aviso: Item 'redacao' não é um dicionário. Pulando. Conteúdo: {redacao}")
                continue
            
            if not redacao.get('url'):
                continue

            for correcao in redacao.get('correcoes', []):
                if isinstance(correcao, dict) and correcao.get('tipo') == tipo_correcao:
                    # Adiciona uma checagem para garantir que os detalhes existem
                    if correcao.get('detalhes_competencias') and len(correcao.get('detalhes_competencias')) == 5 and correcao.get('nota_final'):
                        nota_final = correcao.get('nota_final')
                        fonte = redacao.get('url')
                        candidatos_map = brasil_escola_map
                        if 'educacao.uol' not in fonte:
                            candidatos_map = educacao_uol_map

                        if nota_final > 800:
                            candidatos_map.get('801-1000').append((redacao, correcao))
                        elif nota_final > 500:
                            candidatos_map.get('501-800').append((redacao, correcao))
                        else:
                            candidatos_map.get('0-500').append((redacao, correcao))

                        candidatos.append((redacao, correcao))                        
                        break # Pega a primeira correção 'Tradicional' que encontrar
        
        if not candidatos:
            print(f"Erro: Nenhuma redação com correção '{tipo_correcao}' e 5 competências foi encontrada.")
            return []

        if len(candidatos) < n:
            print(f"Aviso: Pediu {n} amostras, mas só {len(candidatos)} encontradas com correção '{tipo_correcao}' e 5 competências.")
            n = len(candidatos)
            
        cardinalidade_por_fonte_e_faixa = n // (2 * 3)
        amostra_aleatoria = []
        for key in brasil_escola_map:
            amostra_aleatoria += random.sample(brasil_escola_map[key], cardinalidade_por_fonte_e_faixa)
            print(f'DEBUG - fetched {cardinalidade_por_fonte_e_faixa} from range {key} from brasil_escola_map')
        for key in educacao_uol_map:
            amostra_aleatoria += random.sample(educacao_uol_map[key], cardinalidade_por_fonte_e_faixa)
            print(f'DEBUG - fetched {cardinalidade_por_fonte_e_faixa} from range {key} from educacao_uol_map')
        
        print(f'DEBUG - amostra_final = {amostra_aleatoria}')
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
    amostra = loader.get_sample(n=30)
    if not amostra:
        print('Nenhuma amostra válida encontrada')
        sys.exit()

    print("\n--- Exemplo de Amostra Corrigida ---")
    print(json.dumps(amostra[0], indent=2, ensure_ascii=False))

    print(f'DEBUG - verificando se as amostras foram coletadas respeitando as fontes e faixas de notas')
    for redacao in amostra:
        print(f'FONTE = {redacao.get('input').get('id')} & NOTA FINAL = {redacao.get('ground_truth').get('nota_final')}')
