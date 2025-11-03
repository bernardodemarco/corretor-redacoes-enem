import json
import re
import time
import concurrent.futures # Para processamento paralelo
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- CONFIGURAÇÃO ---
INDEX_URL = "https://educacao.uol.com.br/bancoderedacoes/"
# Número de "robôs" (workers) para rodar em paralelo.
# Para 2 temas, 2 workers é o ideal.
MAX_WORKERS = 2 
# ---------------------

def intercept_route(route):
    """Bloqueia o download de recursos desnecessários para acelerar a navegação."""
    if route.request.resource_type in ["image", "stylesheet", "font"]:
        route.abort()
    else:
        route.continue_()

def get_page_content(page, url):
    """Navega até uma URL, lida com o banner de cookies e retorna o HTML."""
    try:
        page.goto(url, timeout=45000, wait_until='domcontentloaded')
        try:
            cookie_button = page.get_by_role('button', name='Aceitar e fechar')
            cookie_button.wait_for(timeout=7000)
            cookie_button.click()
            page.wait_for_timeout(1000)
        except PlaywrightTimeoutError:
            pass
        
        page.wait_for_selector('.custom-title', timeout=20000)
        return page.content()
    except Exception:
        return None

def scrape_essay_page(page, essay_url):
    """Extrai todas as informações de uma única página de redação."""
    html_content = get_page_content(page, essay_url)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, 'html.parser')
    essay_data = {}
    composition_div = soup.find('div', class_='text-composition')
    essay_data['texto_redacao_html'] = str(composition_div) if composition_div else "Não encontrado"
    general_comment_h3 = soup.find('h3', string='Comentário geral')
    if general_comment_h3 and general_comment_h3.find_next_sibling('p'):
        essay_data['comentario_geral'] = general_comment_h3.find_next_sibling('p').get_text(strip=True)
    else:
        essay_data['comentario_geral'] = "Não encontrado"
    competencies_h3 = soup.find('h3', string='Competências')
    if competencies_h3 and competencies_h3.find_next_sibling('ul'):
        competencies_list = competencies_h3.find_next_sibling('ul').find_all('li')
        essay_data['comentarios_competencias'] = [li.get_text(strip=True) for li in competencies_list]
    else:
        essay_data['comentarios_competencias'] = []
    score_table_header = soup.find('h4', string='Competências avaliadas')
    if score_table_header:
        score_table = score_table_header.find_parent('section', class_='results-table')
        score_lines = score_table.find_all('div', class_='rt-line-option')
        scores = []
        for line in score_lines:
            competency = line.find('span', class_='topic').get_text(strip=True)
            points = line.find('span', class_='points').get_text(strip=True)
            scores.append({'competencia': competency, 'nota': int(points) if points.isdigit() else 0})
        essay_data['notas_competencias'] = scores
    else:
        essay_data['notas_competencias'] = []
    return essay_data

def scrape_tema(page, theme_url):
    """Função que extrai todas as redações de um único tema."""
    print(f"\n{'='*50}\nIniciando extração para o tema: {theme_url}\n{'='*50}")
    
    html_content = get_page_content(page, theme_url)
    if not html_content:
        print(f"  [ERRO] Não foi possível obter o conteúdo do tema: {theme_url}")
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    theme_title = soup.find('i', class_='custom-title').get_text(strip=True)
    print(f"Tema encontrado: {theme_title}")

    theme_data = {'tema_geral': theme_title, 'url_tema': theme_url, 'redacoes': []}
    results_table = soup.find('section', class_='results-table')
    if not results_table:
        print(f"  -> AVISO: Nenhuma tabela de redações encontrada para o tema '{theme_title}'.")
        return theme_data

    essay_links = results_table.find_all('div', class_='rt-line-option')
    for link_div in essay_links:
        link_tag = link_div.find('a')
        if not link_tag or not link_tag.has_attr('href'): continue
        
        essay_url = link_tag['href']
        essay_title = link_tag.find('span', class_='topic').get_text(strip=True)
        essay_score = link_tag.find('span', class_='points').get_text(strip=True)
        
        print(f"\n  Processando redação: '{essay_title}' (Nota: {essay_score})")
        detailed_data = scrape_essay_page(page, essay_url)
        
        if detailed_data:
            print(f"    -> Sucesso ao extrair dados para: '{essay_title}'")
            complete_essay_info = {'titulo': essay_title, 'nota_final': int(essay_score) if essay_score.isdigit() else 0, 'url': essay_url, **detailed_data}
            theme_data['redacoes'].append(complete_essay_info)
        else:
            print(f"    -> Falha ao extrair dados para: '{essay_title}'")
        
    print(f"Finalizada a extração para o tema: {theme_title} ({len(theme_data['redacoes'])} redações encontradas)")
    return theme_data

def main():
    """Função principal que encontra todos os temas e orquestra a extração."""
    with sync_playwright() as p:
        # --- ETAPA 1: O SCRAPER "MESTRE" COLETA TODOS OS LINKS ---
        print("--- ETAPA 1: Coletando a lista de todos os temas ---")
        master_browser = p.chromium.launch(channel="chrome", headless=True)
        master_context = master_browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
        master_page = master_context.new_page()
        master_page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"Acessando a página principal de temas: {INDEX_URL}")
        master_page.goto(INDEX_URL, timeout=60000, wait_until='networkidle')
        try:
            master_page.get_by_role('button', name='Aceitar e fechar').click(timeout=15000)
            print("Banner de cookies da página principal aceito.")
            master_page.wait_for_timeout(2000)
        except PlaywrightTimeoutError:
            print("Banner de cookies não encontrado na página principal, continuando...")
        
        while True:
            try:
                master_page.wait_for_selector('button.ver-mais', state='visible', timeout=5000)
                master_page.locator('button.ver-mais').click()
                print("Clicou em 'ver mais'... aguardando novos temas.")
                master_page.wait_for_load_state('networkidle', timeout=5000)
            except PlaywrightTimeoutError:
                print("Botão 'ver mais' não encontrado. Todos os temas foram carregados.")
                break
                
        soup = BeautifulSoup(master_page.content(), 'html.parser')
        theme_urls = [link['href'] for link in soup.select('div.thumbnails-item a') if link.has_attr('href')]
        master_browser.close()
        print(f"--- ETAPA 1 CONCLUÍDA: {len(theme_urls)} temas encontrados no total ---\n")

        if not theme_urls:
            print("Nenhum tema foi encontrado. Encerrando o script.")
            return

        # --- ALTERAÇÃO PARA TESTE: Limita a lista a apenas 2 temas ---
        print("!!! MODO DE TESTE: Processando apenas os 2 primeiros temas. !!!")
        theme_urls = theme_urls[:2]
        print(f"Lista de temas reduzida para {len(theme_urls)} para o teste.\n")
        # -----------------------------------------------------------

        # --- ETAPA 2: OS SCRAPERS "TRABALHADORES" PROCESSAM OS LINKS EM PARALELO ---
        print(f"--- ETAPA 2: Iniciando a extração paralela com {MAX_WORKERS} workers ---")
        all_data = []
        start_time = time.time()

        def worker(theme_url):
            """Um worker autônomo que abre seu próprio navegador para extrair um único tema."""
            browser = p.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            page.route(re.compile(r"\.(jpg|png|webp|css|woff)"), intercept_route)
            
            result = scrape_tema(page, theme_url)
            
            browser.close()
            return result

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = executor.map(worker, theme_urls)
            all_data = [res for res in results if res is not None]

        end_time = time.time()
        total_time = end_time - start_time
        print(f"\n{'='*50}\nEXTRAÇÃO DE TESTE COMPLETA!\n{'='*50}")
        print(f"Tempo total de execução: {total_time:.2f} segundos.")

        file_name = "teste_2_temas.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"\nTodos os dados foram salvos com sucesso no arquivo '{file_name}'")

if __name__ == "__main__":
    main()