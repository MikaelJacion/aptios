"""DOMÍNIO DA PISTA — a física de um carro elétrico, sem tela e sem internet.

Todo carro, a cada instante, é empurrado e segurado por FORÇAS:

    empurram:  motor (limitado pela potência E pela aderência do pneu) e foguete
    seguram:   arrasto do ar (cresce com a velocidade AO QUADRADO!),
               rolamento dos pneus e freio

    aceleração = (forças que empurram − forças que seguram) ÷ massa   ← 2ª lei de Newton

São funções PURAS: dá para testar sem abrir o navegador.
A página da pista tem uma CÓPIA destas contas em JavaScript (para rodar a 60
quadros por segundo). Mudou aqui? Mude lá também.
"""
from __future__ import annotations

from dataclasses import dataclass

G = 9.81            # gravidade (m/s²)
DENSIDADE_AR = 1.2  # kg/m³
EFICIENCIA = 0.85   # parte da energia da bateria que vira movimento
GASTO_FIXO_KW = 2.0  # computador, faróis, ar-condicionado...
REGENERACAO = 0.5   # ao frear, o motor vira gerador e devolve metade da energia


@dataclass(frozen=True)
class CarroEletrico:
    """VALUE OBJECT: a ficha técnica (os números não mudam durante a corrida)."""

    nome: str
    massa_kg: float
    potencia_kw: float
    aderencia: float       # μ: quanto o pneu "gruda" no chão (borracha de corrida ≈ 1,4)
    arrasto_cda: float     # coeficiente de arrasto × área da frente (m²)
    rolamento: float       # coeficiente de rolamento do pneu
    bateria_kwh: float
    limite_kmh: float      # limitador eletrônico de velocidade
    foguete_n: float = 0   # empurrão extra dos propulsores (N)
    foguete_s: float = 0   # quantos segundos o ar comprimido dura


@dataclass(frozen=True)
class Estado:
    """VALUE OBJECT: uma "foto" do carro num instante."""

    t: float = 0.0          # tempo (s)
    x: float = 0.0          # distância (m)
    v: float = 0.0          # velocidade (m/s)
    energia_kwh: float = -1  # -1 = bateria cheia (preenchido no 1º passo)
    foguete_restante: float = -1


def forcas(carro: CarroEletrico, v: float, acelerador: float, freio: float, foguete: bool,
           foguete_restante: float) -> dict[str, float]:
    """As forças (em newtons) que agem no carro na velocidade v (m/s)."""
    peso = carro.massa_kg * G
    tracao_max = carro.aderencia * peso                       # mais que isso, o pneu patina
    pela_potencia = carro.potencia_kw * 1000 / max(v, 0.1)    # potência = força × velocidade
    arrasto = 0.5 * DENSIDADE_AR * carro.arrasto_cda * v * v
    rolamento = carro.rolamento * peso if v > 0 else 0
    motor = min(tracao_max, pela_potencia) * acelerador
    no_limite = v >= carro.limite_kmh / 3.6
    if no_limite:                                             # limitador: só mantém a velocidade
        motor = min(motor, arrasto + rolamento)
    tem_foguete = foguete and not no_limite and carro.foguete_n > 0 and foguete_restante > 0 and acelerador > 0
    return {
        "motor": motor,
        "foguete": carro.foguete_n if tem_foguete else 0,
        "arrasto": arrasto,
        "rolamento": rolamento,
        "freio": tracao_max * freio if v > 0 else 0,
    }


def passo(carro: CarroEletrico, e: Estado, dt: float, acelerador: float = 0, freio: float = 0,
          foguete: bool = False) -> Estado:
    """Avança o tempo um pouquinho (dt segundos) e devolve o novo estado."""
    energia = carro.bateria_kwh if e.energia_kwh < 0 else e.energia_kwh
    restante = carro.foguete_s if e.foguete_restante < 0 else e.foguete_restante
    f = forcas(carro, e.v, acelerador, freio, foguete, restante)
    a = (f["motor"] + f["foguete"] - f["arrasto"] - f["rolamento"] - f["freio"]) / carro.massa_kg
    v = max(0.0, e.v + a * dt)
    gasto_j = (f["motor"] * e.v / EFICIENCIA + GASTO_FIXO_KW * 1000 - f["freio"] * e.v * REGENERACAO) * dt
    return Estado(
        t=e.t + dt,
        x=e.x + (e.v + v) / 2 * dt,
        v=v,
        energia_kwh=min(carro.bateria_kwh, max(0.0, energia - gasto_j / 3.6e6)),
        foguete_restante=max(0.0, restante - dt) if f["foguete"] else restante,
    )


def ficha(carro: CarroEletrico, foguete: bool = False) -> dict[str, float]:
    """Mede o carro numa arrancada com o pé no fundo, igual a uma revista de carros."""
    e, dt = Estado(), 0.005
    zero_a_cem = quatrocentos_m = vel_400 = None
    while e.t < 60:
        e = passo(carro, e, dt, acelerador=1, foguete=foguete)
        if zero_a_cem is None and e.v >= 100 / 3.6:
            zero_a_cem = e.t
        if quatrocentos_m is None and e.x >= 400:
            quatrocentos_m, vel_400 = e.t, e.v * 3.6
    # Autonomia: andando a 100 km/h, sempre igual, sem parar
    v = 100 / 3.6
    f = forcas(carro, v, 0, 0, False, 0)
    kw = (f["arrasto"] + f["rolamento"]) * v / EFICIENCIA / 1000 + GASTO_FIXO_KW
    return {
        "zero_a_cem_s": round(zero_a_cem or 0, 2),
        "quatrocentos_m_s": round(quatrocentos_m or 0, 2),
        "velocidade_400m_kmh": round(vel_400 or 0),
        "velocidade_max_kmh": round(e.v * 3.6),
        "autonomia_km": round(carro.bateria_kwh / kw * 100),
    }


# Números APROXIMADOS das promessas anunciadas para o novo roadster elétrico
# (0 a 100 em ~2 s, mais de 400 km/h, ~1000 km de autonomia). O carro de verdade
# ainda pode mudar. O modo foguete é uma ideia anunciada, não confirmada.
ROADSTER = CarroEletrico(
    nome="Roadster Elétrico", massa_kg=2000, potencia_kw=950, aderencia=1.4,
    arrasto_cda=0.45, rolamento=0.012, bateria_kwh=200, limite_kmh=400,
    foguete_n=20000, foguete_s=8,
)



def velocidade_max_na_curva(carro: CarroEletrico, raio_m: float) -> float:
    """A maior velocidade (m/s) para fazer uma curva sem derrapar.

    Na curva, o pneu precisa puxar o carro para dentro. A força necessária é
    m·v²/r, e o máximo que o pneu aguenta é μ·m·g. Igualando:  v = √(μ·g·r)
    (repare que a massa some da conta!)
    """
    return (carro.aderencia * G * raio_m) ** 0.5
