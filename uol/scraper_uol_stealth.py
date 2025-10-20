import json
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# URL da página principal
THEME_URL = "https://educacao.uol.com.br/bancoderedacoes/propostas/qualificacao-e-o-futuro-do-emprego.htm"

def get_page_content(page, url):
    """Navega até uma URL, lida com o banner de cookies e retorna o HTML."""
    print(f"  Navegando para: {url}")
    try:
        page.goto(url, timeout=60000, wait_until='domcontentloaded')

        # --- NOVO BLOCO PARA LIDAR COM O BANNER DE COOKIES ---
        try:
            # O seletor busca um botão com o texto exato "Aceitar e fechar"
            # Este é o passo mais importante para desbloquear a página.
            print("  Procurando pelo banner de cookies para aceitar...")
            cookie_button = page.get_by_role('button', name='Aceitar e fechar')
            
            # Espera o botão estar visível e clica nele
            cookie_button.wait_for(timeout=10000) # Espera até 10s pelo banner
            cookie_button.click()
            print("  Banner de cookies aceito com sucesso!")
            
            # Espera um momento para a página se reajustar após o clique
            page.wait_for_timeout(2000) 
            
        except PlaywrightTimeoutError:
            # Se o botão não aparecer em 10 segundos, assume que não há banner.
            print("  Banner de cookies não encontrado, prosseguindo...")
        
        # Agora que o banner foi tratado, esperamos pelo seletor principal
        page.wait_for_selector('.custom-title', timeout=30000)
        return page.content()
        
    except PlaywrightTimeoutError:
        print(f"  [ERRO] Timeout final ao esperar pelo seletor '.custom-title'.")
        return None
    except Exception as e:
        print(f"  [ERRO] Ocorreu um erro inesperado ao acessar {url}: {e}")
        return None

# Nenhuma mudança necessária nas funções abaixo
def scrape_essay_page(page, essay_url):
    """Extrai todas as informações de uma única página de redação."""
    print(f"\nProcessando redação...")
    html_content = get_page_content(page, essay_url)
    if not html_content:
        return None
        
    soup = BeautifulSoup(html_content, 'html.parser')
    essay_data = {}
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
    """Função principal que orquestra o scraping."""
    # É MUITO IMPORTANTE rodar com headless=False para ver o que acontece na tela
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=False)
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36', viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"Iniciando o scraping com tratamento de cookies...")
        html_content = get_page_content(page, THEME_URL)
        if not html_content:
            browser.close()
            return

        soup = BeautifulSoup(html_content, 'html.parser')
        theme_title = soup.find('i', class_='custom-title').get_text(strip=True)
        print(f"\nTema encontrado: {theme_title}\n" + "="*40)

        final_data = {'tema_geral': theme_title, 'redacoes': []}
        results_table = soup.find('section', class_='results-table')
        if not results_table:
             print("[ERRO FINAL] Não foi possível encontrar a tabela de redações.")
             browser.close()
             return

        essay_links = results_table.find_all('div', class_='rt-line-option')
        for link_div in essay_links:
            link_tag = link_div.find('a')
            if not link_tag or not link_tag.has_attr('href'): continue
            
            essay_url = link_tag['href']
            essay_title = link_tag.find('span', class_='topic').get_text(strip=True)
            essay_score = link_tag.find('span', class_='points').get_text(strip=True)
            
            detailed_data = scrape_essay_page(page, essay_url)
            
            if detailed_data:
                print(f"  -> Sucesso ao extrair dados para: '{essay_title}' (Nota: {essay_score})")
                complete_essay_info = {'titulo': essay_title, 'nota_final': int(essay_score) if essay_score.isdigit() else 0, 'url': essay_url, **detailed_data}
                final_data['redacoes'].append(complete_essay_info)
            else:
                print(f"  -> Falha ao extrair dados para: '{essay_title}'")
            
            time.sleep(1)
            print("-" * 40)

        browser.close()
        print("\nScraping concluído com sucesso!")

        file_name = "redacoes_uol_final.json"
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print(f"\nDados salvos com sucesso no arquivo '{file_name}'")

if __name__ == "__main__":
    main()