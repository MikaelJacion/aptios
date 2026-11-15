"""Testes: provam que as regras funcionam, sem internet e sem gastar nada.

Rodar:  venv/bin/pytest
"""
import pytest
from fastapi.testclient import TestClient

from aptios.tutor.aplicacao import montar_conversa
from aptios.tutor.dominio import Conversa, Kit, Mensagem, MensagemInvalida
from aptios.tutor.prompt import prompt_do_sistema
from aptios.interface.web import LimiteDePerguntas, criar_app
from aptios.oficina.aplicacao import Oficina
from aptios.oficina.catalogo import CATALOGO, PACOTES
from aptios.oficina.infra import ExploradoresEmMemoria, PagamentoDesativado


def nova_oficina():
    return Oficina(CATALOGO, ExploradoresEmMemoria(), PagamentoDesativado(), PACOTES)


class TutorFalso:
    """Um tutor de mentirinha: responde sempre a mesma coisa, em pedaços."""

    def __init__(self):
        self.ultima_conversa = None

    async def responder(self, conversa):
        self.ultima_conversa = conversa
        for pedaco in ["Olá, ", "engenheiro!"]:
            yield pedaco


# ── Domínio ──────────────────────────────────────────────────────

def test_pergunta_vazia_nao_vale():
    with pytest.raises(MensagemInvalida):
        Mensagem("estudante", "   ")


def test_pergunta_gigante_nao_vale():
    with pytest.raises(MensagemInvalida):
        Mensagem("estudante", "a" * 1001)


def test_conversa_comeca_pelo_estudante_e_reveza():
    conversa = Conversa(Kit.ARDUINO)
    with pytest.raises(MensagemInvalida):
        conversa.adicionar(Mensagem("tutor", "oi"))
    conversa.perguntar("Como piscar um LED?")
    with pytest.raises(MensagemInvalida):
        conversa.perguntar("e outra pergunta?")


def test_tutor_so_lembra_das_ultimas_mensagens_e_comeca_pelo_estudante():
    conversa = Conversa(Kit.SCRATCH)
    for i in range(15):
        conversa.perguntar(f"pergunta {i}")
        conversa.adicionar(Mensagem("tutor", f"resposta {i}"))
    conversa.perguntar("última")
    recentes = conversa.recentes()
    assert len(recentes) <= Conversa.MEMORIA
    assert recentes[0].autor == "estudante"
    assert recentes[-1].texto == "última"


def test_cada_kit_tem_suas_instrucoes():
    for kit in Kit:
        assert kit.nome.split()[0].upper() in prompt_do_sistema(kit).upper()


# ── Aplicação ────────────────────────────────────────────────────

def test_kit_desconhecido_e_recusado():
    with pytest.raises(MensagemInvalida):
        montar_conversa("minecraft", [], "oi")


def test_historico_fora_de_ordem_e_recusado():
    with pytest.raises(MensagemInvalida):
        montar_conversa("scratch", [{"autor": "tutor", "texto": "oi"}], "oi")


# ── Interface (site) ─────────────────────────────────────────────

def test_site_responde_em_pedacos_com_o_tutor():
    tutor = TutorFalso()
    cliente = TestClient(criar_app(tutor, nova_oficina()))
    r = cliente.post("/api/perguntar", json={
        "kit": "lego_spike",
        "pergunta": "Como andar para frente?",
        "historico": [{"autor": "estudante", "texto": "oi"}, {"autor": "tutor", "texto": "Olá!"}],
    })
    assert r.status_code == 200
    assert r.text == "Olá, engenheiro!"
    assert tutor.ultima_conversa.kit is Kit.LEGO_SPIKE
    assert len(tutor.ultima_conversa.mensagens) == 3


def test_site_recusa_pergunta_invalida():
    cliente = TestClient(criar_app(TutorFalso(), nova_oficina()))
    r = cliente.post("/api/perguntar", json={"kit": "scratch", "pergunta": ""})
    assert r.status_code == 400


def test_limite_de_perguntas():
    cliente = TestClient(criar_app(TutorFalso(), nova_oficina(), LimiteDePerguntas(maximo=2)))
    pedido = {"kit": "scratch", "pergunta": "oi"}
    assert cliente.post("/api/perguntar", json=pedido).status_code == 200
    assert cliente.post("/api/perguntar", json=pedido).status_code == 200
    assert cliente.post("/api/perguntar", json=pedido).status_code == 429


def test_pagina_inicial_abre():
    c = TestClient(criar_app(TutorFalso(), nova_oficina()))
    inicio = c.get("/").text
    assert all(link in inicio for link in ('href="/ia"', 'href="/oficina"', 'href="/pista"'))
    ia = c.get("/ia")
    assert ia.status_code == 200 and "IA da Aptios" in ia.text and 'data-kit="pista"' in ia.text
    assert "Oficina Aptios" in TestClient(criar_app(TutorFalso(), nova_oficina())).get("/oficina").text


def test_app_de_celular():
    c = TestClient(criar_app(TutorFalso(), nova_oficina()))
    m = c.get("/manifest.webmanifest")
    assert m.headers["content-type"].startswith("application/manifest+json")
    assert {i["sizes"] for i in m.json()["icons"]} >= {"192x192", "512x512"}
    sw = c.get("/sw.js")
    assert "javascript" in sw.headers["content-type"] and "/api/" in sw.text
    for pagina in ("/", "/ia", "/oficina", "/pista"):
        assert 'rel="manifest"' in c.get(pagina).text
    assert c.get("/static/icone-512.png").content[:4] == b"\x89PNG"
