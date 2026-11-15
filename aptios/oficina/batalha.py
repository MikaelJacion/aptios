"""DOMÍNIO DA BATALHA — quanto o robô é forte, e quem ganha a luta.

São funções PURAS: a mesma entrada dá sempre a mesma saída. Até o
"sorteio" é previsível, porque usa uma semente. Por isso dá para testar
uma batalha inteira e repetir exatamente a mesma luta na tela.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterable

from aptios.oficina.dominio import Catalogo, PecaColocada, RegraDaOficina


@dataclass(frozen=True)
class Atributos:
    """VALUE OBJECT: a "ficha" do robô, calculada a partir das peças."""

    vida: int
    ataque: int
    defesa: int
    velocidade: int
    precisao: int  # chance de acertar, em %


@dataclass(frozen=True)
class Rival:
    id: str
    nome: str
    nivel: str
    premio: int
    descricao: str
    pecas: tuple[PecaColocada, ...] = field(default_factory=tuple)


def calcular_atributos(robo: Iterable[PecaColocada], catalogo: Catalogo) -> Atributos:
    """Cada peça soma alguma coisa, como na vida real:

    estrutura = mais vida e defesa · garra/servo/motor = ataque
    motores e rodas = velocidade · sensores = mira (precisão)
    """
    pecas = [catalogo.peca(c.peca_id) for c in robo]
    conta = lambda *ids: sum(1 for p in pecas if p.id in ids)
    if not any(p.categoria == "controlador" for p in pecas):
        raise RegraDaOficina("o robô precisa de um controlador para lutar")
    if conta("roda_pequena", "roda_grande") < 2 and not conta("esteira"):
        raise RegraDaOficina("o robô precisa de rodas (2 ou mais) ou de uma esteira para lutar")

    estrutura = [p for p in pecas if p.categoria == "estrutura"]
    blocos = sum(p.tamanho[0] * p.tamanho[2] for p in estrutura)  # área de "pinos"
    motores = conta("motor")
    return Atributos(
        vida=min(60 + blocos * 2 + conta("esteira") * 15, 200),
        ataque=min(6 + conta("garra") * 9 + conta("servo") * 5 + motores * 3, 60),
        defesa=min(len(estrutura) * 2 + conta("esteira") * 4, 30),
        velocidade=min(2 + motores * 3 + conta("roda_grande") * 2 - conta("esteira"), 20),
        precisao=min(55 + conta("sensor_distancia") * 15 + conta("sensor_cor") * 8 + conta("sensor_toque") * 4, 95),
    )


@dataclass(frozen=True)
class Golpe:
    atacante: str  # "voce" ou "rival"
    acertou: bool
    dano: int
    vida_voce: int
    vida_rival: int


def lutar(voce: Atributos, rival: Atributos, semente: int, max_rodadas: int = 24) -> tuple[list[Golpe], str]:
    """Simula a luta golpe a golpe. Devolve os golpes e o vencedor."""
    sorte = random.Random(semente)
    vida = {"voce": voce.vida, "rival": rival.vida}
    ficha = {"voce": voce, "rival": rival}
    # Quem é mais rápido ataca primeiro. No empate, decide a moeda.
    vez = "voce" if (voce.velocidade, sorte.random()) > (rival.velocidade, .5) else "rival"
    golpes: list[Golpe] = []
    for _ in range(max_rodadas):
        alvo = "rival" if vez == "voce" else "voce"
        a, d = ficha[vez], ficha[alvo]
        esquiva = min(d.velocidade * 1.5, 25)  # robô rápido desvia mais
        acertou = sorte.uniform(0, 100) < a.precisao - esquiva
        dano = max(2, a.ataque - d.defesa // 3 + sorte.randint(0, 4)) if acertou else 0
        vida[alvo] = max(0, vida[alvo] - dano)
        golpes.append(Golpe(vez, acertou, dano, vida["voce"], vida["rival"]))
        if vida[alvo] == 0:
            break
        vez = alvo
    vencedor = "voce" if vida["voce"] > vida["rival"] else "rival" if vida["rival"] > vida["voce"] else "empate"
    return golpes, vencedor
