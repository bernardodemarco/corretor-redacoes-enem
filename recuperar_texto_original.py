import json, re, html, argparse, sys, time
from pathlib import Path
from typing import Any

# Script preserva a estrutura original do JSON de entrada.
# Para cada dict que contém 'texto_html_corrigido', adiciona o campo
# 'texto_original_recuperado' com o texto limpo (removendo correções verdes).
# Flags:
#  - --no-normalize : não normaliza espaços
#  - --progress-every K : loga progresso a cada K ocorrências processadas
#  - --output : arquivo de saída
#  - --input : arquivo de entrada

SPAN_GREEN = re.compile(r'<span[^>]*style="[^\"]*color:#00b050[^\"]*"[^>]*>.*?</span>', re.DOTALL)
SPAN_RED_OPEN = re.compile(r'<span[^>]*style="[^\"]*color:red[^\"]*"[^>]*>', re.DOTALL)
SPAN_BLACK_OPEN = re.compile(r'<span[^>]*style="[^\"]*color:black[^\"]*"[^>]*>', re.DOTALL)
CLOSE_SPAN = re.compile(r'</span>')
TAG_RE = re.compile(r'<[^>]+>')


def html_to_original_text(html_corrigido: str, normalize_spaces: bool = True) -> str:
    if not html_corrigido:
        return ''
    s = html_corrigido
    s = SPAN_GREEN.sub('', s)
    s = SPAN_RED_OPEN.sub('', s)
    s = SPAN_BLACK_OPEN.sub('', s)
    s = CLOSE_SPAN.sub('', s)
    s = s.replace('</p>', '\n\n')
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = TAG_RE.sub('', s)
    s = html.unescape(s)
    if normalize_spaces:
        s = re.sub(r'[ \t]+', ' ', s)
        lines = [line.strip() for line in s.split('\n')]
        s = '\n'.join(lines)
    return s.strip('\n')


def process_in_place(obj: Any, normalize_spaces: bool, counter: dict, progress_every: int):
    if isinstance(obj, dict):
        if 'texto_html_corrigido' in obj and 'texto_original_recuperado' not in obj:
            obj['texto_original_recuperado'] = html_to_original_text(obj['texto_html_corrigido'], normalize_spaces)
            counter['n'] += 1
            if progress_every > 0 and counter['n'] % progress_every == 0:
                elapsed = time.time() - counter['start']
                rate = counter['n'] / elapsed if elapsed else 0
                print(f"[progress] {counter['n']} ocorrências processadas - {rate:.1f} it/s", file=sys.stderr)
        for k, v in list(obj.items()):  # list() para evitar issues se modificarmos
            process_in_place(v, normalize_spaces, counter, progress_every)
    elif isinstance(obj, list):
        for item in obj:
            process_in_place(item, normalize_spaces, counter, progress_every)


def main():
    ap = argparse.ArgumentParser(description='Adiciona texto_original_recuperado preservando estrutura.')
    ap.add_argument('-i', '--input', default='DADOS_UNIFICADOS.json')
    ap.add_argument('-o', '--output', default='DADOS_UNIFICADOS_original_preservado.json')
    ap.add_argument('--no-normalize', action='store_true', help='Não normaliza espaços internos.')
    ap.add_argument('--progress-every', type=int, default=1000, help='Loga progresso a cada K ocorrências.')
    args = ap.parse_args()

    path_in = Path(args.input)
    data = json.loads(path_in.read_text(encoding='utf-8'))

    counter = {'n': 0, 'start': time.time()}
    process_in_place(data, not args.no_normalize, counter, args.progress_every)
    elapsed = time.time() - counter['start']
    print(f"[done] Total ocorrências com campo adicionado: {counter['n']} em {elapsed:.2f}s ({counter['n']/elapsed if elapsed else 0:.1f} it/s)", file=sys.stderr)

    Path(args.output).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Salvo: {args.output}')


if __name__ == '__main__':
    main()
