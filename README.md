# Corretor Redações ENEM

## Instruções para execução local

### Execução da UI

Para executar a UI, é necessário primeiramente realizar a configuração do servidor _proxy_. Para isso, deve-se:

1. Acessar a pasta `proxy-server`
2. Criar um arquivo `.env` e inserir a chave de API do Maritaca AI, conforme exemplificado pelo `.env.example`
3. Instalar as dependências
4. Executar o servidor

```bash
cd proxy-server
touch .env
echo "MARITACA_API_KEY=<SUA_CHAVE_AQUI>" > .env
npm i
node --env-file=.env server.js
```

Após, para execução da UI, os seguintes passos devem ser seguidos:

1. Acessar a pasta `ui`
2. Criar um arquivo `.env` e inserir a chave de API do Google Gemini, conforme exemplificado pelo `.env.example`
3. Instalar as dependências
4. Executar a UI

```bash
cd ui
touch .env
echo "VITE_GOOGLE_API_KEY=<SUA_CHAVE_AQUI>" > .env
npm i
npm run dev
```

### Execução da automatização dos testes

Para execução das automatizações dos testes, deve-se:

1. Acessar a pasta `script_analise`
2. Criar um _virtual environment_ do Python
3. Ativar _virtual environment_
4. Instalar as dependências
5. Criar um arquivo `.env` e inserir as chaves de API do Maritaca AI e do Google Gemini
6. Executar o arquivo `main.py`

```bash
cd script_analise
python3 -m venv <nome-do-venv>
source <nome-do-venv>/bin/activate
pip install -r ./requirements.txt
touch .env
echo "MARITACA_API_KEY=<SUA_CHAVE_AQUI>" >> .env
echo "GOOGLE_API_KEY=<SUA_CHAVE_AQUI>" >> .env
python3 main.py
```
