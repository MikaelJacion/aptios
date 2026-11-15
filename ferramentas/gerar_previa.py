"""Gera uma prévia da oficina que funciona sem servidor (modo demonstração).

Uso:  venv/bin/python ferramentas/gerar_previa.py saida.html
"""
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from aptios.oficina.aplicacao import Oficina  # noqa: E402
from aptios.oficina.catalogo import CATALOGO, PACOTES  # noqa: E402
from aptios.oficina.infra import ExploradoresEmMemoria, PagamentoDesativado  # noqa: E402

pagina = (Path(__file__).resolve().parent.parent / "aptios/interface/static/oficina.html").read_text(encoding="utf-8")
oficina = Oficina(CATALOGO, ExploradoresEmMemoria(), PagamentoDesativado(), PACOTES)
demo = {
    "catalogo": oficina.catalogo_publico(),
    "respostas": {d.id: {"correta": d.correta, "explicacao": d.explicacao} for d in CATALOGO.desafios.values()},
}
pega = lambda padrao: re.search(padrao, pagina, re.S).group(0)
partes = [
    pega(r"<title>.*?</title>"),
    pega(r'<meta name="claude:viewport-fit-sides"[^>]*>'),
    pega(r'<link rel="stylesheet"[^>]*>'),
    pega(r"<style>.*?</style>"),
    f"<script>window.APTIOS_DEMO = {json.dumps(demo, ensure_ascii=False)};</script>",
    pega(r'<script type="importmap">.*?</script>'),
    re.search(r"<body>(.*)</body>", pagina, re.S).group(1),
]
Path(sys.argv[1]).write_text("\n".join(partes), encoding="utf-8")
print("prévia gerada:", sys.argv[1])
