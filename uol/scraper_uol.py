import requests
import json
import time
from bs4 import BeautifulSoup

# URL da página principal com a lista de redações
THEME_URL = "https://educacao.uol.com.br/bancoderedacoes/propostas/qualificacao-e-o-futuro-do-emprego.htm"

# ==============================================================================
# ATUALIZAÇÃO: Headers mais completos para simular um navegador real
# Esta é a principal mudança para resolver o erro 403 Forbidden.
# ==============================================================================
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

def get_soup(url):
    """Função auxiliar para fazer a requisição e retornar um objeto BeautifulSoup."""
    try:
        # A única mudança aqui é que a variável HEADERS agora é mais completa
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a URL {url}: {e}")
        return None

def scrape_essay_page(essay_url):
    """Extrai todas as informações de uma única página de redação."""
    print(f"  > Extraindo dados de: {essay_url}")
    soup = get_soup(essay_url)
    if not soup:
        return None

    essay_data = {}

    # 1. Extrair o texto da redação
    composition_div = soup.find('div', class_='text-composition')
    essay_data['texto_redacao_html'] = str(composition_div) if composition_div else "Não encontrado"

    # 2. Extrair comentário geral e por competências
    comments_div = soup.find('div', class_='text')
    if comments_div:
        general_comment_h3 = comments_div.find('h3', string='Comentário geral')
        if general_comment_h3 and general_comment_h3.find_next_sibling('p'):
            essay_data['comentario_geral'] = general_comment_h3.find_next_sibling('p').get_text(strip=True)
        else:
            essay_data['comentario_geral'] = "Não encontrado"
        
        competencies_h3 = comments_div.find('h3', string='Competências')
        if competencies_h3 and competencies_h3.find_next_sibling('ul'):
            competencies_list = competencies_h3.find_next_sibling('ul').find_all('li')
            essay_data['comentarios_competencias'] = [li.get_text(strip=True) for li in competencies_list]
        else:
            essay_data['comentarios_competencias'] = []
    else:
        essay_data['comentario_geral'] = "Não encontrado"
        essay_data['comentarios_competencias'] = []

    # 3. Extrair a tabela de notas quantitativas
    score_table_header = soup.find('h4', string='Competências avaliadas')
    if score_table_header:
        score_table = score_table_header.find_parent('section', class_='results-table')
        score_lines = score_table.find_all('div', class_='rt-line-option')
        
        scores = []
        for line in score_lines:
            competency = line.find('span', class_='topic').get_text(strip=True)
            points = line.find('span', class_='points').get_text(strip=True)
            # Adiciona uma verificação para garantir que os pontos são numéricos
            scores.append({'competencia': competency, 'nota': int(points) if points.isdigit() else 0})
        essay_data['notas_competencias'] = scores
    else:
        essay_data['notas_competencias'] = []
        
    return essay_data

def main():
    """Função principal que orquestra o scraping."""
    print(f"Iniciando o scraping para o tema na URL: {THEME_URL}\n")
    
    soup = get_soup(THEME_URL)
    if not soup:
        return

    theme_title = soup.find('i', class_='custom-title').get_text(strip=True)
    print(f"Tema encontrado: {theme_title}\n")

    final_data = {
        'tema_geral': theme_title,
        'redacoes': []
    }

    results_table = soup.find('section', class_='results-table')
    essay_links = results_table.find_all('div', class_='rt-line-option')

    for link_div in essay_links:
        link_tag = link_div.find('a')
        if not link_tag:
            continue
        
        essay_url = link_tag['href']
        essay_title = link_tag.find('span', class_='topic').get_text(strip=True)
        essay_score = link_tag.find('span', class_='points').get_text(strip=True)
        
        print(f"Processando redação: '{essay_title}' (Nota: {essay_score})")

        detailed_data = scrape_essay_page(essay_url)
        
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

    print("\nScraping concluído com sucesso!")

    print("\nResultado final (JSON):")
    # Removido para não poluir o terminal, já que será salvo em arquivo
    # print(json.dumps(final_data, indent=2, ensure_ascii=False))
    
    file_name = "redacoes_uol.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    print(f"\nDados salvos com sucesso no arquivo '{file_name}'")


if __name__ == "__main__":
    main()