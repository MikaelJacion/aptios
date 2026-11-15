"""Baixa um modelo 3D (.glb) que você fez no Meshy e coloca na Aptios.

Uso:  venv/bin/python ferramentas/baixar_modelo_meshy.py <id-da-tarefa> <nome>
      ex.: ... 01a1ded3-56b8-756e-8340-f57cd9110167 roadster

A chave da API do Meshy fica em ~/.config/aptios/env (MESHY_API_KEY=...),
NUNCA no código nem no chat. Este script lê a chave de lá.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "aptios/interface/static/modelos"


def chave() -> str:
    if os.environ.get("MESHY_API_KEY"):
        return os.environ["MESHY_API_KEY"]
    env = Path.home() / ".config/aptios/env"
    for linha in env.read_text().splitlines() if env.exists() else []:
        if linha.startswith("MESHY_API_KEY="):
            return linha.split("=", 1)[1].strip()
    sys.exit("Falta a MESHY_API_KEY em ~/.config/aptios/env")


def main(tarefa: str, nome: str) -> None:
    k = chave()
    if not k:
        sys.exit("A MESHY_API_KEY está vazia em ~/.config/aptios/env")
    for tipo in ("image-to-3d", "text-to-3d", "multi-image-to-3d"):
        pedido = urllib.request.Request(f"https://api.meshy.ai/openapi/v1/{tipo}/{tarefa}",
                                        headers={"Authorization": f"Bearer {k}"})
        try:
            with urllib.request.urlopen(pedido, timeout=30) as r:
                dados = json.load(r)
            break
        except urllib.error.HTTPError as erro:
            if erro.code != 404:
                sys.exit(f"O Meshy respondeu {erro.code}: {erro.read()[:200]!r}")
    else:
        sys.exit("Não achei essa tarefa no Meshy.")
    if dados.get("status") != "SUCCEEDED":
        sys.exit(f"O modelo ainda não está pronto (status: {dados.get('status')}, {dados.get('progress')}%).")
    url = (dados.get("model_urls") or {}).get("glb")
    if not url:
        sys.exit("Essa tarefa não tem arquivo .glb.")
    PASTA.mkdir(exist_ok=True)
    destino = PASTA / f"{nome}.glb"
    with urllib.request.urlopen(url, timeout=120) as r:
        conteudo = r.read()
    if conteudo[:4] != b"glTF":
        sys.exit("O arquivo baixado não é um .glb válido.")
    destino.write_bytes(conteudo)
    print(f"✅ Salvo em {destino} ({len(conteudo) // 1024} KB)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
