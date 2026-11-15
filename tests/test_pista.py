"""Testes da física da pista: dá para conferir Newton sem abrir o navegador!"""
from dataclasses import replace

from aptios.pista.fisica import ROADSTER, Estado, ficha, forcas, passo


def test_arrancada_parecida_com_a_anunciada():
    f = ficha(ROADSTER)
    assert 1.8 <= f["zero_a_cem_s"] <= 2.3
    assert f["velocidade_max_kmh"] == 400          # o limitador segura
    assert 900 <= f["autonomia_km"] <= 1400


def test_foguete_deixa_mais_rapido():
    assert ficha(ROADSTER, foguete=True)["zero_a_cem_s"] < ficha(ROADSTER)["zero_a_cem_s"] - 0.5


def test_arrasto_cresce_com_o_quadrado_da_velocidade():
    a50 = forcas(ROADSTER, 50, 0, 0, False, 0)["arrasto"]
    a100 = forcas(ROADSTER, 100, 0, 0, False, 0)["arrasto"]
    assert abs(a100 / a50 - 4) < 1e-9              # dobro da velocidade = 4× o arrasto


def test_pneu_patina_acima_da_aderencia():
    # parado, a potência daria uma força enorme, mas o pneu só aguenta μ·m·g
    assert forcas(ROADSTER, 0.5, 1, 0, False, 0)["motor"] == ROADSTER.aderencia * ROADSTER.massa_kg * 9.81


def test_carro_mais_pesado_acelera_menos():
    pesado = replace(ROADSTER, massa_kg=4000, aderencia=0.7)  # mesma força, o dobro da massa
    assert ficha(pesado)["zero_a_cem_s"] > ficha(ROADSTER)["zero_a_cem_s"]


def test_freio_para_o_carro_e_devolve_energia():
    e = Estado(v=30, energia_kwh=100)
    for _ in range(1000):
        e = passo(ROADSTER, e, 0.01, freio=1)
    assert e.v == 0 and e.t < 10
    andando = passo(ROADSTER, Estado(v=30, energia_kwh=100), 0.1, freio=1)
    assert andando.energia_kwh > 100 - 0.001       # frear recarrega um pouco (menos o gasto fixo)


def test_rota_da_pista():
    from fastapi.testclient import TestClient

    from aptios.interface.web import criar_app
    from tests.test_oficina import TutorQueNaoFala, oficina
    c = TestClient(criar_app(TutorQueNaoFala(), oficina()))
    carros = {c["carro"]["id"]: c for c in c.get("/api/pista/carro").json()["carros"]}
    assert carros["roadster"]["ficha_foguete"]["zero_a_cem_s"] < carros["roadster"]["ficha"]["zero_a_cem_s"]
    assert "ficha_foguete" not in carros["onibus"]          # só o roadster tem foguete
    assert "Pista Aptios" in c.get("/pista").text


def test_curva_mais_aberta_permite_mais_velocidade():
    from aptios.pista.fisica import velocidade_max_na_curva
    v50 = velocidade_max_na_curva(ROADSTER, 50)
    assert abs(velocidade_max_na_curva(ROADSTER, 200) / v50 - 2) < 1e-9   # raio 4× maior = 2× mais rápido
    gelo = replace(ROADSTER, aderencia=0.3)
    assert velocidade_max_na_curva(gelo, 50) < v50 / 2                     # no gelo, devagar!


def test_garagem_faz_sentido():
    from aptios.pista.fisica import CARROS
    f = {c.id: ficha(c) for c in CARROS}
    assert len({c.id for c in CARROS}) == len(CARROS)
    assert f["roadster"]["zero_a_cem_s"] < f["suv"]["zero_a_cem_s"] < f["hatch"]["zero_a_cem_s"]
    assert f["kart"]["zero_a_cem_s"] == 0 and f["onibus"]["zero_a_cem_s"] == 0   # nem chegam a 100 km/h!
    assert f["onibus"]["autonomia_km"] < f["roadster"]["autonomia_km"]           # ônibus é um caixote


def test_flutuar_custa_caro_e_cresce_com_o_peso():
    from aptios.pista.fisica import CARROS, potencia_para_flutuar_kw
    p = potencia_para_flutuar_kw(ROADSTER)
    assert p < ROADSTER.potencia_kw                      # o roadster consegue voar
    dobro = potencia_para_flutuar_kw(replace(ROADSTER, massa_kg=4000))
    assert abs(dobro / p - 2 ** 1.5) < 1e-9              # dobro do peso = 2,83× a potência
    assert dobro > ROADSTER.potencia_kw                  # pesado demais: não decola
    assert all(potencia_para_flutuar_kw(c) == float("inf") for c in CARROS if c.id != "roadster")
