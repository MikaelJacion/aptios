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
    dados = c.get("/api/pista/carro").json()
    assert dados["carro"]["nome"] == "Roadster Elétrico"
    assert dados["ficha_foguete"]["zero_a_cem_s"] < dados["ficha"]["zero_a_cem_s"]
    assert "Pista Aptios" in c.get("/pista").text
