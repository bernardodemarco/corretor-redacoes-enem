# coding: utf-8
import os
import json
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

# Carrega as variáveis de ambiente (GOOGLE_API_KEY, OPENAI_API_KEY) do arquivo .env
load_dotenv()

class AbstractLLMProvider(ABC):
    """
    Interface abstrata para provedores de LLM. 
    Garante que todos os provedores tenham o método get_correction.
    """
    def __init__(self, model_name):
        self.model_name = model_name
        print(f"Inicializando provedor: {self.__class__.__name__} com modelo {self.model_name}")

    @abstractmethod
    def get_correction(self, system_prompt, redacao_texto):
        """
        Método principal para obter a correção.
        Deverá retornar um dicionário Python (parseado do JSON da LLM)
        ou None em caso de falha.
        """
        pass

class GeminiProvider(AbstractLLMProvider):
    """
    Implementação concreta para a API do Google Gemini.
    Utiliza o modo JSON para garantir a saída estruturada.
    """
    def __init__(self, model_name="gemini-2.5-flash-preview-09-2025"):
        super().__init__(model_name)
        
        # Configura a API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada no arquivo .env")
        genai.configure(api_key=api_key)
        
        # Define o SCHEMA JSON que vamos FORÇAR na LLM
        # (Corresponde ao que definimos no planejamento)
        self.json_schema = {
            "type": "OBJECT",
            "properties": {
                "nota_atribuida": {"type": "NUMBER"},
                "raciocinio_cot": {"type": "STRING"},
                "justificativa_para_aluno": {"type": "STRING"}
            },
            "required": ["nota_atribuida", "raciocinio_cot", "justificativa_para_aluno"]
        }
        
        # Configuração de geração da API
        self.generation_config = {
            "response_mime_type": "application/json",
            "response_schema": self.json_schema,
            "temperature": 0.2 # Baixa temperatura para consistência
        }

        # --- MUDANÇA ---
        # NÃO inicializamos o modelo aqui. 
        # Vamos inicializá-lo dentro do get_correction,
        # pois ele precisa do system_prompt.
        # self.model = None 

    def get_correction(self, system_prompt, redacao_texto):
        """
        Chama a API do Gemini com o prompt do sistema e a redação,
        forçando a resposta em JSON.
        """
        
        try:
            # --- INÍCIO DA CORREÇÃO ---
            # O modelo é inicializado AQUI, toda vez,
            # passando o system_prompt dinâmico.
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_prompt
            )
            
            # A API do Gemini usa o argumento principal para a entrada do usuário
            # (a redação) e NÃO aceita system_instruction aqui.
            response = model.generate_content(
                redacao_texto,
                generation_config=self.generation_config
            )
            # --- FIM DA CORREÇÃO ---
            
            if not response.candidates:
                raise Exception("Resposta da API vazia ou bloqueada (safety settings?).")
            
            # response.text já é o JSON string
            json_string = response.text
            
            # Parseia o JSON string para um dicionário Python
            json_data = json.loads(json_string)
            
            # Validação final para garantir que a nota existe
            if "nota_atribuida" not in json_data:
                raise ValueError("JSON retornado pela API não contém 'nota_atribuida'")
                
            return json_data

        except Exception as e:
            print(f"[GeminiProvider ERRO] Falha ao chamar API ou parsear JSON: {e}")
            print(f"   Contexto: Modelo={self.model_name}")
            # Se a resposta não for JSON, pode estar aqui
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"   Resposta recebida (se houver): {response.text[:200]}...")
            elif 'response' in locals() and hasattr(response, 'prompt_feedback'):
                 print(f"   Feedback do Prompt (possível bloqueio): {response.prompt_feedback}")
            return None

class OpenAIProvider(AbstractLLMProvider):
    """
    Implementação concreta para a API da OpenAI (GPT).
    """
    def __init__(self, model_name="gpt-4o-mini"): # gpt-4o-mini é rápido e barato
        super().__init__(model_name)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")
        # Inicializa o cliente da OpenAI
        self.client = OpenAI(api_key=api_key)

    def get_correction(self, system_prompt, redacao_texto):
        """
        Chama a API da OpenAI com o prompt do sistema e a redação,
        forçando a resposta em JSON.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": redacao_texto}
                ],
                # Esta é a "mágica" para forçar JSON no GPT
                response_format={"type": "json_object"},
                temperature=0.2 # Baixa temperatura para consistência
            )
            
            if not response.choices:
                 raise Exception("Resposta da API da OpenAI vazia.")

            # O JSON string está dentro da mensagem de resposta
            json_string = response.choices[0].message.content
            
            # Parseia o JSON string para um dicionário Python
            json_data = json.loads(json_string)
            
            # Validação final para garantir que a nota existe
            if "nota_atribuida" not in json_data:
                raise ValueError("JSON retornado pela API (OpenAI) não contém 'nota_atribuida'")

            return json_data

        except Exception as e:
            print(f"[OpenAIProvider ERRO] Falha ao chamar API ou parsear JSON: {e}")
            print(f"   Contexto: Modelo={self.model_name}")
            # Se a resposta não for JSON, pode estar aqui
            if 'response' in locals() and hasattr(response, 'choices'):
                print(f"   Resposta recebida (se houver): {response.choices[0].message.content[:200]}...")
            return None
