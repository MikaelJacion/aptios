"""APLICAÇÃO DA PISTA — monta o que a página precisa saber sobre os carros.

Não guarda nada e não usa banco de dados: só junta o domínio (fisica.py).
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from aptios.pista.fisica import CARROS, ficha


def dados_da_pista(pasta_modelos: Path | None = None) -> dict[str, Any]:
    carros = []
    for c in CARROS:
        item: dict[str, Any] = {"carro": asdict(c), "ficha": ficha(c)}
        if c.foguete_n:
            item["ficha_foguete"] = ficha(c, foguete=True)
        # Modelo 3D do Meshy (opcional): static/modelos/<id>.glb
        if pasta_modelos and (pasta_modelos / f"{c.id}.glb").exists():
            item["modelo"] = f"/static/modelos/{c.id}.glb"
        carros.append(item)
    return {"carros": carros}
