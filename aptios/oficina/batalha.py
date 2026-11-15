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
    golpes: tuple[str, ...] = ("encontrao",)  # os golpes que as peças permitem


@dataclass(frozen=True)
class Movimento:
    """VALUE OBJECT: um TIPO de golpe. Cada peça especial destrava um."""

    nome: str
    emoji: str
    peca: str          # a peça que destrava o golpe ("" = todo robô tem)
    dano: float        # multiplica o ataque
    mira: int          # soma (ou tira) da chance de acertar
    descricao: str


MOVIMENTOS: dict[str, Movimento] = {
    "encontrao": Movimento("Encontrão", "💥", "", 1.0, 0, "Todo robô sabe: acelerar e trombar!"),
    "garrada": Movimento("Garrada", "🦀", "garra", 1.5, -10, "Belisca forte e passa por cima da defesa."),
    "martelada": Movimento("Martelada", "🔨", "servo", 1.1, 0, "O braço bate de cima. Pode deixar o rival tonto (perde a vez)."),
    "turbo": Movimento("Investida turbo", "🚀", "motor", 1.0, -5, "Com 2 motores ou mais: quanto mais rápido, mais dói."),
    "atropelar": Movimento("Atropelar", "🚜", "esteira", 1.3, -5, "Passa por cima do rival, igual a um trator."),
    "laser": Movimento("Mira laser", "🎯", "sensor_distancia", 1.0, 15, "Mede a distância e mira no ponto fraco: pode ser golpe crítico (dano dobrado)."),
    "pisca": Movimento("Pisca-pisca", "✨", "led", 0.5, 20, "Dano pequeno, mas ofusca: o próximo ataque do rival erra mais."),
    "giro": Movimento("Disco giratório", "🌀", "disco", 1.8, -20, "O golpe mais forte de todos, mas erra bastante."),
    "rasante": Movimento("Voo rasante", "🚁", "helice", 1.2, 10, "A hélice levanta o robô e ele ataca por cima."),
    "choque": Movimento("Choque", "⚡", "bobina", 0.8, 5, "Faíscas! Muitas vezes deixa o rival tonto (perde a vez)."),
}


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

    estrutura e blindagem = mais vida e defesa · garra/servo/motor/disco = ataque
    motores, rodas e bateria = velocidade · sensores, câmera e giroscópio = mira (precisão)
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
    golpes = tuple(g for g, m in MOVIMENTOS.items()
                   if not m.peca or (conta(m.peca) >= (2 if m.peca == "motor" else 1)))
    return Atributos(
        vida=min(60 + blocos * 2 + conta("esteira") * 15 + conta("bateria") * 10, 200),
        ataque=min(6 + conta("garra") * 9 + conta("servo") * 5 + motores * 3
                   + conta("disco") * 10 + conta("helice") * 3 + conta("bobina") * 4, 60),
        defesa=min(len(estrutura) * 2 + conta("esteira") * 4 + conta("blindagem") * 4 + conta("giroscopio") * 2, 30),
        velocidade=min(2 + motores * 3 + conta("roda_grande") * 2 - conta("esteira") + conta("bateria") * 3, 20),
        precisao=min(55 + conta("sensor_distancia") * 15 + conta("sensor_cor") * 8 + conta("sensor_toque") * 4
                     + conta("camera") * 12 + conta("giroscopio") * 6, 95),
        golpes=golpes,
    )


@dataclass(frozen=True)
class Golpe:
    atacante: str  # "voce" ou "rival"
    golpe: str     # qual movimento foi usado (chave de MOVIMENTOS)
    acertou: bool
    dano: int
    vida_voce: int
    vida_rival: int
    efeito: str = ""  # "critico", "tonto" ou "ofuscado"


def lutar(voce: Atributos, rival: Atributos, semente: int, max_rodadas: int = 24) -> tuple[list[Golpe], str]:
    """Simula a luta golpe a golpe. Devolve os golpes e o vencedor.

    A cada vez, o robô sorteia um dos golpes que as peças dele permitem.
    """
    sorte = random.Random(semente)
    vida = {"voce": voce.vida, "rival": rival.vida}
    ficha = {"voce": voce, "rival": rival}
    ofuscado = {"voce": False, "rival": False}
    # Quem é mais rápido ataca primeiro. No empate, decide a moeda.
    vez = "voce" if (voce.velocidade, sorte.random()) > (rival.velocidade, .5) else "rival"
    golpes: list[Golpe] = []
    for _ in range(max_rodadas):
        alvo = "rival" if vez == "voce" else "voce"
        a, d = ficha[vez], ficha[alvo]
        nome = sorte.choice(a.golpes)
        mov = MOVIMENTOS[nome]
        esquiva = min(d.velocidade * 1.5, 25)  # robô rápido desvia mais
        chance = a.precisao + mov.mira - esquiva - (25 if ofuscado[vez] else 0)
        ofuscado[vez] = False
        acertou = sorte.uniform(0, 100) < chance
        dano, efeito = 0, ""
        if acertou:
            defesa = 0 if nome == "garrada" else d.defesa // 3      # a garra ignora a defesa
            extra = a.velocidade // 2 if nome == "turbo" else 0     # turbo: velocidade vira dano
            dano = max(2, round(a.ataque * mov.dano) + extra - defesa + sorte.randint(0, 4))
            if nome == "laser" and sorte.random() < .3:
                dano, efeito = dano * 2, "critico"
            elif (nome == "martelada" and sorte.random() < .3) or (nome == "choque" and sorte.random() < .5):
                efeito = "tonto"
            elif nome == "pisca":
                efeito, ofuscado[alvo] = "ofuscado", True
        vida[alvo] = max(0, vida[alvo] - dano)
        golpes.append(Golpe(vez, nome, acertou, dano, vida["voce"], vida["rival"], efeito))
        if vida[alvo] == 0:
            break
        if efeito != "tonto":  # tonto = o rival perde a vez, e quem bateu ataca de novo
            vez = alvo
    vencedor = "voce" if vida["voce"] > vida["rival"] else "rival" if vida["rival"] > vida["voce"] else "empate"
    return golpes, vencedor
