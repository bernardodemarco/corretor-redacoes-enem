# Corretor Automatizado de Redações do ENEM - Script de Avaliação

Este é um Evaluation Harness (script de avaliação) em Python, projetado para o projeto de INE5687 (Grupo EF).

O objetivo deste script é automatizar a avaliação e comparação de diferentes LLMs (Large Language Models) na tarefa de correção de redações do ENEM.

## Funcionalidades

- Carrega redações e gabaritos (correções humanas) de um banco de dados JSON (db.json).
- Executa um lote de redações contra múltiplos provedores de API (ex: Google Gemini, OpenAI GPT).
- Utiliza prompts modulares (armazenados em /prompts) para avaliar cada uma das 5 competências do ENEM separadamente.
- Força a saída das LLMs em um formato JSON estruturado e padronizado.
- Calcula métricas de performance (QWK, Correlação de Pearson, Adjacent Agreement) comparando as notas da LLM com as notas humanas.
- Salva um relatório detalhado em evaluation_results.csv para análise offline.

### 1. Como Configurar

Antes de executar, siga estes passos:

#### Banco de Dados:

- Coloque o arquivo JSON do banco de dados de redações na raiz deste projeto.
- Renomeie o arquivo para base_dados.json ou atualize a variável NOME_ARQUIVO_DB no topo do main.py.

#### Dependências:

Instale todas as bibliotecas Python necessárias:

- pip install -r requirements.txt

#### Chaves de API (.env):

- Crie um arquivo chamado .env na raiz do projeto (você pode copiar/renomear o .env.example).
- Adicione suas chaves de API ao arquivo .env. O script irá carregá-las automaticamente

```
GOOGLE_API_KEY=SUA_CHAVE_GEMINI_AQUI
OPENAI_API_KEY=SUA_CHAVE_OPENAI_AQUI
# Adicione outras chaves de API aqui (ex: MARITACA_API_KEY)
```

### 2. Como Executar

#### Ajuste do Lote (Opcional):

- Abra o main.py e ajuste as variáveis de configuração no topo conforme necessário:
  - N_AMOSTRAS_TESTE: (ex: 10) O número de redações aleatórias a serem testadas.
  - DELAY_ENTRE_CHAMADAS_API: (ex: 1.0) O tempo em segundos de espera entre chamadas de API, para evitar erros de Rate Limit.
- Execute o Script:
  - Rode o main.py pelo seu terminal:

```
python main.py
```

#### Analise os Resultados:

- O script exibirá o progresso no terminal e, ao final, imprimirá um resumo das métricas agregadas (QWK, Pearson, etc.) para cada modelo.
- Um arquivo detalhado, evaluation_results.csv, será gerado na raiz do projeto. Este arquivo contém cada avaliação de competência, incluindo as justificativas e o Chain-of-Thought (CoT) de cada LLM.

### 3. Como Adicionar Novas LLMs

O framework é modular (graças ao llm_provider.py). Para adicionar um novo modelo (ex: Sabiá/Maritaca):

#### requirements.txt: Adicione a biblioteca Python do novo provedor (ex: maritaca-ai) e instale-a.

#### llm_provider.py:

- Importe a biblioteca do novo provedor.
- Crie uma nova classe que herde de AbstractLLMProvider (ex: class SabiaProvider(AbstractLLMProvider):).
- Implemente o **init** para carregar a chave de API do .env e inicializar o cliente da API.
- Implemente o método get_correction(self, system_prompt, redacao_texto).
- **Crucial**: Dentro do get_correction, você deve chamar a API da LLM e garantir que ela retorne um JSON com a estrutura exata:

```
{
  "nota_atribuida": 160,
  "raciocinio_cot": "O raciocínio do modelo aqui...",
  "justificativa_para_aluno": "O feedback para o aluno aqui..."
}
```

#### main.py:

- Importe sua nova classe no topo: from llm_provider import SabiaProvider.
- Adicione uma instância da sua classe à lista modelos_para_testar:

```
modelos_para_testar = [
    GeminiProvider(),
    OpenAIProvider(),
    SabiaProvider() # Adicione o seu aqui
]
```

Pronto. Ao rodar main.py novamente, o script executará sua nova LLM contra o mesmo lote de redações, permitindo uma comparação direta.
