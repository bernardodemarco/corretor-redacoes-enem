import json
import re
import time
import concurrent.futures # Importa a biblioteca para processamento paralelo
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- CONFIGURAÇÃO ---
INDEX_URL = "https://vestibular.brasilescola.uol.com.br/corrige-aqui/temas-anteriores.htm"

# --- FLAG DE TESTE ---
MODO_TESTE = False
MAX_TEMAS_TESTE = 2
MAX_REDACOES_POR_TEMA_TESTE = 3
# ---------------------

CHECKPOINT_FILE = "teste_brasilescola.json" if MODO_TESTE else "dados_completos_brasilescola.json"
MAX_WORKERS = 2 if MODO_TESTE else 4
# --------------------------------------------------------------------


def intercept_route(route):
    """Bloqueia o download de recursos desnecessários para acelerar a navegação."""
    if route.request.resource_type in ["image", "stylesheet", "font"]:
        route.abort()
    else:
        route.continue_()

def get_page_content(page, url):
    """Navega até uma URL, lida com o banner de cookies e retorna o HTML."""
    try:
        page.goto(url, timeout=60000, wait_until='domcontentloaded')
        try:
            cookie_button = page.get_by_role('button', name='Aceitar e fechar')
            cookie_button.wait_for(timeout=7000)
            cookie_button.click()
        except PlaywrightTimeoutError:
            pass
        page.wait_for_selector('h1', timeout=30000)
        return page.content()
    except Exception as e:
        print(f"  [ERRO] Não foi possível processar a página {url}. Erro: {e}")
        return None

def scrape_individual_essay(page, essay_url):
    """Extrai todas as informações de uma única página de redação."""
    print(f"    -- Extraindo redação: {essay_url}")
    html_content = get_page_content(page, essay_url)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, 'html.parser')
    essay_data = {'url_redacao': essay_url}

    essay_data['titulo_redacao'] = soup.select_one('h1.titulo-conteudo').get_text(strip=True) if soup.select_one('h1.titulo-conteudo') else 'Sem Título'
    
    text_block = soup.find('div', class_='area-redacao-corrigida')
    essay_data['texto_html_corrigido'] = str(text_block) if text_block else "Não encontrado"
    
    ai_block = soup.find('div', class_='area_correcao_ia')
    if ai_block:
        correcao_ia = {'competencias': []}
        ai_table = ai_block.find('table', id='tabela-export')
        if ai_table:
            for row in ai_table.find('tbody').find_all('tr'):
                cols = row.find_all('td')
                if len(cols) == 3:
                    competencia, nota, observacao = [c.get_text(strip=True) for c in cols]
                    if "Nota final" in competencia:
                        correcao_ia['nota_final_ia'] = int(nota) if nota.isdigit() else 0
                        correcao_ia['comentario_geral_ia'] = observacao
                    else:
                        correcao_ia['competencias'].append({'competencia': competencia, 'nota': int(nota) if nota.isdigit() else 0, 'observacao': observacao})
        essay_data['correcao_ia'] = correcao_ia
    else:
        essay_data['correcao_ia'] = None

    trad_header = soup.find('h2', string=re.compile(r'Dados correção tradicional'))
    if trad_header:
        correcao_tradicional = {'competencias': []}
        comment_label = trad_header.find_next('label', string='Comentários do corretor')
        if comment_label and comment_label.find_next_sibling('div'):
            correcao_tradicional['comentario_geral'] = comment_label.find_next_sibling('div').get_text(strip=True)
        
        trad_table = trad_header.find_next('table')
        if trad_table:
            for row in trad_table.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) == 3 and "Competência" not in cols[0].get_text():
                    competencia, nota, motivo = [c.get_text(strip=True) for c in cols]
                    correcao_tradicional['competencias'].append({'competencia': competencia, 'nota': int(nota) if nota.isdigit() else 0, 'motivo': motivo})
                elif "NOTA FINAL" in row.get_text():
                    nota_final_text = row.get_text(strip=True).replace('NOTA FINAL:', '').strip()
                    correcao_tradicional['nota_final'] = int(nota_final_text) if nota_final_text.isdigit() else 0
        essay_data['correcao_tradicional'] = correcao_tradicional
    else:
        essay_data['correcao_tradicional'] = None
        
    return essay_data

def scrape_tema_e_redacoes(page, theme_url):
    """Visita um tema, pega os links das redações e extrai os dados de cada uma."""
    print(f"\n{'='*50}\nProcessando tema: {theme_url}\n{'='*50}")
    
    html_content = get_page_content(page, theme_url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    theme_title_element = soup.select_one('h1.titulo-conteudo, p.redacao_tema strong')
    theme_title = theme_title_element.get_text(strip=True).replace('Redações corrigidas do tema :', '').strip() if theme_title_element else "Tema Desconhecido"
    
    print(f"Tema encontrado: {theme_title}")
    
    theme_data = {'tema_geral': theme_title, 'url_tema': theme_url, 'redacoes': []}
    
    table = soup.find('table', id='redacoes_corrigidas')
    if not table:
        print(f"  -> AVISO: Nenhuma tabela de redações encontrada para o tema '{theme_title}'.")
        return theme_data
        
    essay_urls = [link['href'] for link in table.find_all('a') if link.has_attr('href') and '/corrige-aqui/' in link['href']]
    print(f"  -> {len(essay_urls)} redações encontradas. Iniciando extração individual...")

    if MODO_TESTE:
        print(f"    !!! MODO DE TESTE: Limitando a {MAX_REDACOES_POR_TEMA_TESTE} redações por tema. !!!")
        essay_urls = essay_urls[:MAX_REDACOES_POR_TEMA_TESTE]

    for essay_url in essay_urls:
        detailed_data = scrape_individual_essay(page, essay_url)
        if detailed_data:
            theme_data['redacoes'].append(detailed_data)
        time.sleep(0.2) 

    print(f"Finalizada a extração para o tema: {theme_title} ({len(theme_data['redacoes'])} redações salvas)")
    return theme_data

def load_checkpoint(filename):
    """Carrega os dados de um arquivo de checkpoint se ele existir."""
    if MODO_TESTE:
        print("Modo de teste ativo. Ignorando checkpoint e começando do zero.")
        return [], set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        scraped_urls = {item['url_tema'] for item in data}
        print(f"Checkpoint encontrado. {len(data)} temas já foram salvos.")
        return data, scraped_urls
    except (FileNotFoundError, json.JSONDecodeError):
        print("Nenhum checkpoint válido encontrado. Começando do zero.")
        return [], set()

def save_checkpoint(filename, data):
    """Salva os dados no arquivo de checkpoint."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- INÍCIO DA CORREÇÃO ---
# A função 'worker' agora está fora da 'main' para ser usada pelo ProcessPoolExecutor.
def worker(theme_url):
    """
    Um worker autônomo que abre sua própria instância do Playwright e navegador.
    Isso é necessário para o ProcessPoolExecutor.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.route(re.compile(r"\.(jpg|png|webp|css|woff)"), intercept_route)
        
        result = scrape_tema_e_redacoes(page, theme_url)
        
        browser.close()
        return result
# --- FIM DA CORREÇÃO ---

def main():
    """Função principal que orquestra todo o processo de scraping."""
    all_data, scraped_theme_urls = load_checkpoint(CHECKPOINT_FILE)

    print("\n--- ETAPA 1: Coletando a lista de todos os temas ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        page.goto(INDEX_URL, timeout=90000, wait_until='domcontentloaded')
        soup = BeautifulSoup(page.content(), 'html.parser')
        theme_urls = [link['href'] for link in soup.select('a.ver-correcao') if link.has_attr('href')]
        browser.close()
    
    print(f"--- ETAPA 1 CONCLUÍDA: {len(theme_urls)} temas encontrados no total ---\n")
    
    if MODO_TESTE:
        print("!!! MODO DE TESTE: Processando apenas os primeiros temas. !!!")
        theme_urls = theme_urls[:MAX_TEMAS_TESTE]
        print(f"Lista de temas reduzida para {len(theme_urls)} para o teste.\n")

    urls_to_scrape = [url for url in theme_urls if url not in scraped_theme_urls]
    print(f"Temas restantes para processar: {len(urls_to_scrape)}")
    
    if not urls_to_scrape:
        print("Nenhum tema novo para extrair. Trabalho concluído!")
        return

    print(f"--- ETAPA 2: Iniciando a extração paralela com {MAX_WORKERS} workers ---")
    start_time = time.time()

    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(worker, url): url for url in urls_to_scrape}
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            if result:
                all_data.append(result)
                # Salva o progresso a cada tema concluído
                save_checkpoint(CHECKPOINT_FILE, all_data)
                print(f"Progresso: {i+1}/{len(urls_to_scrape)} | Tema salvo: {result['tema_geral']}")

    end_time = time.time()
    total_time = end_time - start_time
    
    # Define a mensagem de conclusão com base no modo de teste
    completion_message = "EXTRAÇÃO DE TESTE COMPLETA!" if MODO_TESTE else "EXTRAÇÃO COMPLETA!"
    
    print(f"\n{'='*50}\n{completion_message}\n{'='*50}")
    print(f"Tempo total de execução nesta sessão: {total_time:.2f} segundos.")
    print(f"Total de temas no arquivo final: {len(all_data)}")
    # A linha abaixo foi removida, pois o salvamento já é feito no loop.
    # save_checkpoint(CHECKPOINT_FILE) <--- LINHA REMOVIDA
    print(f"\nTodos os dados foram salvos com sucesso no arquivo '{CHECKPOINT_FILE}'")

if __name__ == "__main__":
    main()