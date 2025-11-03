import json
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# URL da página principal com a lista de redações
THEME_URL = "https://educacao.uol.com.br/bancoderedacoes/propostas/qualificacao-e-o-futuro-do-emprego.htm"

def get_page_content(page, url):
    """Navega até uma URL usando o objeto 'page' do Playwright e retorna o HTML."""
    try:
        # Aumentamos o timeout para dar tempo da página carregar completamente
        page.goto(url, timeout=60000) 
        # Espera por um elemento específico da tabela para garantir que o conteúdo dinâmico carregou
        page.wait_for_selector('section.results-table', timeout=30000)
        return page.content()
    except PlaywrightTimeoutError:
        print(f"Erro de Timeout: A página {url} demorou muito para carregar ou o seletor não foi encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao acessar a URL {url} com Playwright: {e}")
        return None

def scrape_essay_page(page, essay_url):
    """Extrai todas as informações de uma única página de redação usando Playwright + BeautifulSoup."""
    print(f"  > Extraindo dados de: {essay_url}")
    
    html_content = get_page_content(page, essay_url)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, 'html.parser')
    essay_data = {}

    # A lógica de extração com BeautifulSoup permanece a mesma
    composition_div = soup.find('div', class_='text-composition')
    essay_data['texto_redacao_html'] = str(composition_div) if composition_div else "Não encontrado"
    
    comments_div = soup.find('div', class_='text')
    if comments_div:
        general_comment_h3 = comments_div.find('h3', string='Comentário geral')
        essay_data['comentario_geral'] = general_comment_h3.find_next_sibling('p').get_text(strip=True) if general_comment_h3 and general_comment_h3.find_next_sibling('p') else "Não encontrado"
        
        competencies_h3 = comments_div.find('h3', string='Competências')
        if competencies_h3 and competencies_h3.find_next_sibling('ul'):
            competencies_list = competencies_h3.find_next_sibling('ul').find_all('li')
            essay_data['comentarios_competencias'] = [li.get_text(strip=True) for li in competencies_list]
        else:
            essay_data['comentarios_competencias'] = []
    else:
        essay_data['comentario_geral'] = "Não encontrado"
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

def main():
    """Função principal que orquestra o scraping usando Playwright."""
    with sync_playwright() as p:
        # Inicia o navegador em modo "headless" (invisível)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print(f"Iniciando o scraping para o tema na URL: {THEME_URL}\n")
        
        html_content = get_page_content(page, THEME_URL)
        if not html_content:
            browser.close()
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        theme_title = soup.find('i', class_='custom-title').get_text(strip=True)
        print(f"Tema encontrado: {theme_title}\n")

        final_data = {'tema_geral': theme_title, 'redacoes': []}
        results_table = soup.find('section', class_='results-table')
        essay_links = results_table.find_all('div', class_='rt-line-option')

        for link_div in essay_links:
            link_tag = link_div.find('a')
            if not link_tag or not link_tag.has_attr('href'):
                continue
            
            essay_url = link_tag['href']
            essay_title = link_tag.find('span', class_='topic').get_text(strip=True)
            essay_score = link_tag.find('span', class_='points').get_text(strip=True)
            
            print(f"Processando redação: '{essay_title}' (Nota: {essay_score})")
            
            # Reutilizamos a mesma 'page' para visitar cada link
            detailed_data = scrape_essay_page(page, essay_url)
            
            if detailed_data:
                complete_essay_info = {
                    'titulo': essay_title,
                    'nota_final': int(essay_score) if essay_score.isdigit() else 0,
                    'url': essay_url,
                    **detailed_data
                }
                final_data['redacoes'].append(complete_essay_info)
            
            time.sleep(1) 
            print("-" * 30)

        browser.close() # Fecha o navegador ao final de tudo
        print("\nScraping concluído com sucesso!")

        file_name = "redacoes_uol.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"\nDados salvos com sucesso no arquivo '{file_name}'")

if __name__ == "__main__":
    main()