import json, argparse, sys, time
from pathlib import Path
from typing import Any, Dict, List

"""
Gera um array plano de redações a partir do JSON unificado.
Para cada redação, copia campos internos e injeta:
  - tema_geral (do nível superior se existir)
  - url_tema (do nível superior se existir; pode estar como 'url' do tema)
  - fonte (origem do conjunto, se existir)

Estrutura esperada simplificada (exemplos possíveis):
[
  {
    "tema_geral": "Violência nas escolas",
    "url_tema": "https://.../tema/violencia",
    "fonte": "uol",
    "redacoes": [ {"url": "...", "texto_original_recuperado": "...", "correcoes": [...]}, ... ]
  },
  ...
]
Ou objeto raiz com chave 'temas' => lista acima.

O script detecta automaticamente se o topo é lista ou dict com chave única.
"""

def iter_temas(root: Any) -> List[Dict[str, Any]]:
    if isinstance(root, list):
        return [t for t in root if isinstance(t, dict)]
    if isinstance(root, dict):
        # tenta descobrir lista de temas dentro de chaves conhecidas
        for k in ['temas', 'data', 'items']:
            v = root.get(k)
            if isinstance(v, list):
                return [t for t in v if isinstance(t, dict)]
        # se já parece ser um tema único com redacoes
        return [root]
    return []


def flatten(input_path: Path, output_path: Path, progress_every: int) -> int:
    raw = json.loads(input_path.read_text(encoding='utf-8'))
    temas = iter_temas(raw)
    plano = []
    start = time.time()
    count = 0
    for tema in temas:
        tema_geral = tema.get('tema_geral') or tema.get('tema') or tema.get('titulo')
        url_tema = tema.get('url_tema') or tema.get('url')
        fonte = tema.get('fonte') or tema.get('origem')
        redacoes = tema.get('redacoes') or tema.get('items') or []
        if not isinstance(redacoes, list):
            continue
        for r in redacoes:
            if not isinstance(r, dict):
                continue
            flat_r = dict(r)  # copia
            # injeta se não existir dentro da redação
            if 'tema_geral' not in flat_r:
                flat_r['tema_geral'] = tema_geral
            if 'url_tema' not in flat_r:
                flat_r['url_tema'] = url_tema
            if 'fonte' not in flat_r and fonte:
                flat_r['fonte'] = fonte
            plano.append(flat_r)
            count += 1
            if progress_every > 0 and count % progress_every == 0:
                elapsed = time.time() - start
                rate = count / elapsed if elapsed else 0
                print(f"[progress] {count} redações - {rate:.1f} it/s", file=sys.stderr)
    output_path.write_text(json.dumps(plano, ensure_ascii=False, indent=2), encoding='utf-8')
    elapsed = time.time() - start
    print(f"[done] Total redações: {count} em {elapsed:.2f}s ({count/elapsed if elapsed else 0:.1f} it/s)", file=sys.stderr)
    return count


def main():
    ap = argparse.ArgumentParser(description='Flatten temas/redações em um array plano de redações.')
    ap.add_argument('-i', '--input', default='base_de_dados/DADOS_UNIFICADOS_original_preservado.json', help='JSON unificado de entrada.')
    ap.add_argument('-o', '--output', default='base_de_dados/redacoes_flat.json', help='Arquivo JSON de saída (array).')
    ap.add_argument('--progress-every', type=int, default=2000, help='Log de progresso a cada N redações.')
    args = ap.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Arquivo de entrada não encontrado: {input_path}", file=sys.stderr)
        sys.exit(1)
    output_path = Path(args.output)

    flatten(input_path, output_path, args.progress_every)
    print(f"Salvo: {output_path}")

if __name__ == '__main__':
    main()
