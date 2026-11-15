"""Testes da oficina: tokens, loja, desafios e montagem."""
import pytest
from fastapi.testclient import TestClient

from aptios.interface.web import criar_app
from aptios.oficina.aplicacao import ExploradorNaoEncontrado, Oficina
from aptios.oficina.catalogo import CATALOGO, PACOTES
from aptios.oficina.dominio import Explorador, PecaColocada, RegraDaOficina
from aptios.oficina.infra import ExploradoresEmMemoria, ExploradoresSQLite, PagamentoDesativado


def oficina(repo=None):
    return Oficina(CATALOGO, repo or ExploradoresEmMemoria(), PagamentoDesativado(), PACOTES)


# ── Domínio ──────────────────────────────────────────────────────

def test_explorador_novo_ganha_as_pecas_de_presente_e_zero_tokens():
    e = Explorador("abc")
    e.receber_presentes(CATALOGO)
    assert e.saldo == 0
    assert {"bloco_2x2", "controlador", "roda_pequena"} <= e.pecas
    assert "motor" not in e.pecas


def test_desafio_certo_paga_uma_vez_so():
    e = Explorador("abc")
    d = CATALOGO.desafio("arduino_1")
    assert e.resolver_desafio(d, d.correta) is True
    assert e.saldo == d.recompensa
    with pytest.raises(RegraDaOficina):
        e.resolver_desafio(d, d.correta)


def test_desafio_errado_nao_paga_e_pode_tentar_de_novo():
    e = Explorador("abc")
    d = CATALOGO.desafio("scratch_1")
    assert e.resolver_desafio(d, (d.correta + 1) % len(d.opcoes)) is False
    assert e.saldo == 0
    assert e.resolver_desafio(d, d.correta) is True


def test_nao_compra_sem_saldo_e_nao_compra_duas_vezes():
    e = Explorador("abc", saldo=30)
    motor = CATALOGO.peca("motor")
    with pytest.raises(RegraDaOficina):
        Explorador("pobre", saldo=5).comprar(motor)
    e.comprar(motor)
    assert e.saldo == 0 and "motor" in e.pecas
    with pytest.raises(RegraDaOficina):
        e.comprar(motor)


def test_so_monta_com_pecas_que_tem():
    e = Explorador("abc")
    e.receber_presentes(CATALOGO)
    e.montar([PecaColocada("bloco_2x2", 0, 0, 0, 0)])
    with pytest.raises(RegraDaOficina):
        e.montar([PecaColocada("garra", 0, 0, 0, 0)])


def test_peca_so_gira_de_90_em_90():
    with pytest.raises(RegraDaOficina):
        PecaColocada("bloco_2x2", 0, 0, 0, 45)


# ── Aplicação e repositório ──────────────────────────────────────

def test_catalogo_publico_nao_entrega_as_respostas():
    for d in oficina().catalogo_publico()["desafios"]:
        assert "correta" not in d and "explicacao" not in d


def test_codigo_errado_nao_entra():
    with pytest.raises(ExploradorNaoEncontrado):
        oficina().estado("nao-existe")


def test_compra_com_dinheiro_esta_desligada():
    o = oficina()
    codigo = o.novo_explorador()["codigo"]
    with pytest.raises(RegraDaOficina):
        o.comprar_tokens(codigo, "p100")


def test_sqlite_guarda_e_devolve_tudo(tmp_path):
    repo = ExploradoresSQLite(tmp_path / "teste.db")
    o = oficina(repo)
    codigo = o.novo_explorador()["codigo"]
    d = CATALOGO.desafio("ev3_2")
    o.resolver_desafio(codigo, d.id, d.correta)
    o.salvar_robo(codigo, [{"peca_id": "bloco_2x4", "x": 1, "y": 0, "z": 2, "giro": 90}])
    de_novo = ExploradoresSQLite(tmp_path / "teste.db").buscar(codigo)
    assert de_novo.saldo == d.recompensa
    assert de_novo.desafios_feitos == {"ev3_2"}
    assert de_novo.robo == [PecaColocada("bloco_2x4", 1, 0, 2, 90)]


# ── Site ─────────────────────────────────────────────────────────

class TutorQueNaoFala:
    async def responder(self, conversa):
        yield ""


def test_fluxo_completo_pelo_site():
    c = TestClient(criar_app(TutorQueNaoFala(), oficina()))
    codigo = c.post("/api/oficina/exploradores").json()["codigo"]
    h = {"X-Explorador": codigo}

    assert c.post("/api/oficina/pecas/motor", headers=h).status_code == 400  # sem saldo

    for id_ in ("arduino_1", "robo_1", "spike_1"):  # 10 tokens cada
        r = c.post(f"/api/oficina/desafios/{id_}", headers=h, json={"resposta": CATALOGO.desafio(id_).correta})
        assert r.json()["acertou"] is True
    assert c.get("/api/oficina/eu", headers=h).json()["saldo"] == 30

    assert c.post("/api/oficina/pecas/motor", headers=h).json()["saldo"] == 0
    r = c.put("/api/oficina/robo", headers=h, json={"pecas": [{"peca_id": "motor", "x": 0, "y": 0, "z": 0, "giro": 0}]})
    assert r.status_code == 200 and len(r.json()["robo"]) == 1

    assert c.get("/api/oficina/eu", headers={"X-Explorador": "chute"}).status_code == 404
