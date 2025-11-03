import json
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# URL da página principal com a lista de todos os temas
INDEX_URL = "https://educacao.uol.com.br/bancoderedacoes/"

def get_page_content(page, url):
    """Navega até uma URL, lida com o banner de cookies e retorna o HTML."""
    print(f"  Navegando para: {url}")
    try:
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
    except PlaywrightTimeoutError:
        print(f"  [ERRO] Timeout final ao esperar pelo seletor '.custom-title'.")
        return None
    except Exception as e:
        print(f"  [ERRO] Ocorreu um erro inesperado ao acessar {url}: {e}")
        return None

def scrape_essay_page(page, essay_url):
    """Extrai todas as informações de uma única página de redação."""
    html_content = get_page_content(page, essay_url)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, 'html.parser')
    essay_data = {}

    # Extração do texto da redação (continua igual)
    composition_div = soup.find('div', class_='text-composition')
    essay_data['texto_redacao_html'] = str(composition_div) if composition_div else "Não encontrado"
    
    # Extração do comentário geral (continua igual)
    general_comment_h3 = soup.find('h3', string='Comentário geral')
    if general_comment_h3 and general_comment_h3.find_next_sibling('p'):
        essay_data['comentario_geral'] = general_comment_h3.find_next_sibling('p').get_text(strip=True)
    else:
        essay_data['comentario_geral'] = "Não encontrado"

    # Extração das competências (LÓGICA CORRIGIDA)
    # Buscamos o H3 diretamente no 'soup' e depois pegamos o próximo 'ul'
    competencies_h3 = soup.find('h3', string='Competências')
    if competencies_h3 and competencies_h3.find_next_sibling('ul'):
        competencies_list = competencies_h3.find_next_sibling('ul').find_all('li')
        essay_data['comentarios_competencias'] = [li.get_text(strip=True) for li in competencies_list]
    else:
        essay_data['comentarios_competencias'] = []

    # Extração da tabela de notas (continua igual)
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
        
        time.sleep(1)

    return theme_data

def main():
    """Função principal que encontra todos os temas e orquestra a extração."""
    with sync_playwright() as p:
        # headless=False é ótimo para ver o robô em ação. Mude para True para rodar em segundo plano.
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"Acessando a página principal de temas: {INDEX_URL}")
        page.goto(INDEX_URL, timeout=60000, wait_until='domcontentloaded')

        # Lida com o banner de cookies na página principal
        try:
            page.get_by_role('button', name='Aceitar e fechar').click(timeout=15000)
            print("Banner de cookies da página principal aceito.")
            page.wait_for_timeout(2000)
        except PlaywrightTimeoutError:
            print("Banner de cookies não encontrado na página principal, continuando...")

        # Loop para clicar no botão "ver mais" até que ele desapareça
        while True:
            try:
                ver_mais_button = page.locator('button.ver-mais')
                ver_mais_button.wait_for(timeout=5000) # Espera 5s para ver se o botão existe
                ver_mais_button.click()
                print("Clicou em 'ver mais'... aguardando novos temas.")
                page.wait_for_timeout(3000) # Espera o conteúdo carregar
            except PlaywrightTimeoutError:
                print("Botão 'ver mais' não encontrado. Todos os temas foram carregados.")
                break
        
        # Coleta todos os links dos temas da página
        print("\nColetando links de todos os temas...")
        soup = BeautifulSoup(page.content(), 'html.parser')
        theme_urls = []
        for link_tag in soup.select('div.thumbnails-item a'):
            if link_tag.has_attr('href'):
                theme_urls.append(link_tag['href'])
        
        print(f"Total de {len(theme_urls)} temas encontrados para extração.")
        
        # Inicia o processo de extração para cada tema
        all_data = []
        for i, url in enumerate(theme_urls):
            print(f"\n--- TEMA {i+1} de {len(theme_urls)} ---")
            theme_result = scrape_tema(page, url)
            if theme_result:
                all_data.append(theme_result)

        browser.close()
        print(f"\n{'='*50}\nEXTRAÇÃO COMPLETA!\n{'='*50}")

        file_name = "todas_as_redacoes_uol.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        print(f"\nTodos os dados foram salvos com sucesso no arquivo '{file_name}'")

if __name__ == "__main__":
    main()