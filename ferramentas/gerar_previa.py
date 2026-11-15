"""Gera uma prévia da oficina que funciona sem servidor (modo demonstração).

Uso:  venv/bin/python ferramentas/gerar_previa.py saida.html          (oficina)
      venv/bin/python ferramentas/gerar_previa.py saida.html pista    (simulador)
"""
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from aptios.oficina.aplicacao import Oficina  # noqa: E402
from aptios.oficina.catalogo import CATALOGO, PACOTES, RIVAIS  # noqa: E402
from aptios.oficina.infra import ExploradoresEmMemoria, PagamentoDesativado  # noqa: E402

from aptios.pista.fisica import ROADSTER, ficha  # noqa: E402

qual = sys.argv[2] if len(sys.argv) > 2 else "oficina"
pagina = (Path(__file__).resolve().parent.parent / f"aptios/interface/static/{qual}.html").read_text(encoding="utf-8")
if qual == "pista":
    variavel, demo = "APTIOS_PISTA", {"carro": asdict(ROADSTER), "ficha": ficha(ROADSTER),
                                       "ficha_foguete": ficha(ROADSTER, foguete=True)}
else:
    oficina = Oficina(CATALOGO, ExploradoresEmMemoria(), PagamentoDesativado(), PACOTES)
    variavel, demo = "APTIOS_DEMO", {
        "catalogo": oficina.catalogo_publico(),
        "respostas": {d.id: {"correta": d.correta, "explicacao": d.explicacao} for d in CATALOGO.desafios.values()},
        "rivais": [{**asdict(r), "pecas": [asdict(c) for c in r.pecas]} for r in RIVAIS],
    }
pega = lambda padrao: re.search(padrao, pagina, re.S).group(0)
partes = [
    pega(r"<title>.*?</title>"),
    pega(r'<meta name="claude:viewport-fit-sides"[^>]*>'),
    pega(r'<link rel="stylesheet"[^>]*>'),
    pega(r"<style>.*?</style>"),
    f"<script>window.{variavel} = {json.dumps(demo, ensure_ascii=False)};</script>",
    pega(r'<script type="importmap">.*?</script>'),
    re.search(r"<body>(.*)</body>", pagina, re.S).group(1),
]
Path(sys.argv[1]).write_text("\n".join(partes), encoding="utf-8")
print("prévia gerada:", sys.argv[1])
