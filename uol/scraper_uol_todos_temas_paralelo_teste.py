import json
import time
import concurrent.futures # For parallel processing
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- CONFIGURATION ---
INDEX_URL = "https://educacao.uol.com.br/bancoderedacoes/"
# Number of parallel workers. Adjust based on your computer's power (e.g., 2, 4, 8)
MAX_WORKERS = 4 
# ---------------------

def get_page_content(page, url):
    """Navigates to a URL, handles the cookie banner, and returns the HTML."""
    print(f"  Navigating to: {url}")
    try:
        # Using 'domcontentloaded' is more reliable than 'networkidle' on this site
        page.goto(url, timeout=60000, wait_until='domcontentloaded')
        try:
            print("  Procurando pelo banner de cookies para aceitar...")
            cookie_button = page.get_by_role('button', name='Aceitar e fechar')
            cookie_button.wait_for(timeout=10000)
            cookie_button.click()
            print("  Banner de cookies aceito com sucesso!")
            page.wait_for_timeout(2000)
        except PlaywrightTimeoutError:
            print("  Banner de cookies não encontrado, prosseguindo...")
        
        page.wait_for_selector('.custom-title', timeout=30000)
        return page.content()
    except Exception as e:
        print(f"  [ERRO] Could not process page {url}. Error: {e}")
        return None

def scrape_essay_page(page, essay_url):
    """Extracts all information from a single essay page."""
    html_content = get_page_content(page, essay_url)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, 'html.parser')
    essay_data = {}

    composition_div = soup.find('div', class_='text-composition')
    essay_data['texto_redacao_html'] = str(composition_div) if composition_div else "Não encontrado"
    
    general_comment_h3 = soup.find('h3', string='Comentário geral')
    essay_data['comentario_geral'] = general_comment_h3.find_next_sibling('p').get_text(strip=True) if general_comment_h3 and general_comment_h3.find_next_sibling('p') else "Não encontrado"

    competencies_h3 = soup.find('h3', string='Competências')
    essay_data['comentarios_competencias'] = [li.get_text(strip=True) for li in competencies_h3.find_next_sibling('ul').find_all('li')] if competencies_h3 and competencies_h3.find_next_sibling('ul') else []

    score_table_header = soup.find('h4', string='Competências avaliadas')
    if score_table_header:
        score_table = score_table_header.find_parent('section', class_='results-table')
        score_lines = score_table.find_all('div', class_='rt-line-option')
        essay_data['notas_competencias'] = [{'competencia': line.find('span', class_='topic').get_text(strip=True), 'nota': int(line.find('span', class_='points').get_text(strip=True)) if line.find('span', class_='points').get_text(strip=True).isdigit() else 0} for line in score_lines]
    else:
        essay_data['notas_competencias'] = []
        
    return essay_data

def scrape_tema(page, theme_url):
    """Extracts all essays for a single theme."""
    print(f"Processing theme: {theme_url}")
    
    html_content = get_page_content(page, theme_url)
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')
    theme_title = soup.find('i', class_='custom-title').get_text(strip=True)
    theme_data = {'tema_geral': theme_title, 'url_tema': theme_url, 'redacoes': []}
    results_table = soup.find('section', class_='results-table')
    if not results_table:
        print(f"  -> WARNING: No essay table found for theme '{theme_title}'.")
        return theme_data

    essay_links = results_table.find_all('div', class_='rt-line-option')
    for link_div in essay_links:
        link_tag = link_div.find('a')
        if not link_tag or not link_tag.has_attr('href'): continue
        
        essay_url = link_tag['href']
        essay_title = link_tag.find('span', class_='topic').get_text(strip=True)
        essay_score = link_tag.find('span', class_='points').get_text(strip=True)
        
        detailed_data = scrape_essay_page(page, essay_url)
        
        if detailed_data:
            complete_essay_info = {'titulo': essay_title, 'nota_final': int(essay_score) if essay_score.isdigit() else 0, 'url': essay_url, **detailed_data}
            theme_data['redacoes'].append(complete_essay_info)
    
    print(f"Finished theme: {theme_title} ({len(theme_data['redacoes'])} essays found)")
    return theme_data

def main():
    """Main function to find all themes and orchestrate the parallel scraping."""
    
    # STAGE 1: Sequentially get all theme URLs
    print("--- STAGE 1: Collecting all theme URLs ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"Accessing main themes page: {INDEX_URL}")
        page.goto(INDEX_URL, timeout=60000, wait_until='domcontentloaded')
        
        try:
            page.get_by_role('button', name='Aceitar e fechar').click(timeout=15000)
            print("Main page cookie banner accepted.")
        except PlaywrightTimeoutError:
            print("Main page cookie banner not found, continuing...")
        
        while True:
            try:
                ver_mais_button = page.locator('button.ver-mais')
                ver_mais_button.wait_for(timeout=5000)
                ver_mais_button.click()
                print("Clicked 'ver mais'... waiting for new themes.")
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                print("'ver mais' button not found. All themes are loaded.")
                break
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        theme_urls = [link['href'] for link in soup.select('div.thumbnails-item a') if link.has_attr('href')]
        browser.close()
    
    print(f"--- STAGE 1 COMPLETE: {len(theme_urls)} themes found ---\n")

    if not theme_urls:
        print("No themes found. Exiting script.")
        return
    
    #  # --- ALTERAÇÃO PARA TESTE: Limita a lista a apenas 2 temas ---
    # print("!!! MODO DE TESTE: Processando apenas os 2 primeiros temas. !!!")
    # theme_urls = theme_urls[:2]
    # print(f"Lista de temas reduzida para {len(theme_urls)} para o teste.\n")
    # # -----------------------------------------------------------

    # STAGE 2: Scrape all theme URLs in parallel
    print(f"--- STAGE 2: Starting parallel scraping with {MAX_WORKERS} workers ---")
    all_data = []
    start_time = time.time()

    def worker(theme_url):
        """A self-contained worker that scrapes one theme URL."""
        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            result = scrape_tema(page, theme_url)
            
            browser.close()
            return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = executor.map(worker, theme_urls)
        all_data = [res for res in results if res is not None]

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n{'='*50}\nSCRAPING COMPLETE!\n{'='*50}")
    print(f"Total execution time: {total_time:.2f} seconds.")

    file_name = "todas_as_redacoes_uol_final.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
    print(f"\nAll data successfully saved to '{file_name}'")

if __name__ == "__main__":
    main()