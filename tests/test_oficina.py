"""Testes da oficina: tokens, loja, desafios e montagem."""
import pytest
from fastapi.testclient import TestClient

from aptios.interface.web import criar_app
from aptios.oficina.aplicacao import ExploradorNaoEncontrado, Oficina
from aptios.oficina.batalha import Atributos, calcular_atributos, lutar
from aptios.oficina.catalogo import CATALOGO, PACOTES, RIVAIS
from aptios.oficina.dominio import Explorador, PecaColocada, RegraDaOficina
from aptios.oficina.infra import ExploradoresEmMemoria, ExploradoresSQLite, PagamentoDesativado


def oficina(repo=None):
    return Oficina(CATALOGO, repo or ExploradoresEmMemoria(), PagamentoDesativado(), PACOTES, RIVAIS)


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
    e.montar([PecaColocada("bloco_2x2", 0, 0, 0, 0)], CATALOGO)
    with pytest.raises(RegraDaOficina):
        e.montar([PecaColocada("garra", 0, 0, 0, 0)], CATALOGO)


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


# ── Encaixe, níveis e batalha ────────────────────────────────────

def test_pecas_nao_podem_ocupar_o_mesmo_lugar_nem_sair_da_bancada():
    e = Explorador("abc")
    e.receber_presentes(CATALOGO)
    with pytest.raises(RegraDaOficina):
        e.montar([PecaColocada("bloco_2x2", 0, 0, 0, 0), PecaColocada("bloco_2x2", 1, 0, 1, 0)], CATALOGO)
    with pytest.raises(RegraDaOficina):
        e.montar([PecaColocada("bloco_2x4", 11, 0, 0, 0)], CATALOGO)
    e.montar([PecaColocada("bloco_2x2", 0, 0, 0, 0), PecaColocada("bloco_2x2", 0, 1, 0, 0)], CATALOGO)  # empilhar pode


def test_tem_desafios_dos_tres_niveis_e_os_dificeis_pagam_mais():
    por_nivel = {}
    for d in CATALOGO.desafios.values():
        por_nivel.setdefault(d.nivel, []).append(d.recompensa)
    assert set(por_nivel) == {"facil", "medio", "dificil"}
    assert max(por_nivel["facil"]) < min(por_nivel["medio"]) < min(por_nivel["dificil"])


def test_rivais_sao_robos_validos_e_ficam_mais_fortes():
    forca = []
    for r in RIVAIS:
        from aptios.oficina.dominio import validar_encaixe
        validar_encaixe(list(r.pecas), CATALOGO)
        a = calcular_atributos(r.pecas, CATALOGO)
        forca.append(a.vida + a.ataque * 4 + a.velocidade * 3 + a.precisao)
    assert forca == sorted(forca)


def test_robo_sem_controlador_nao_luta():
    with pytest.raises(RegraDaOficina):
        calcular_atributos([PecaColocada("bloco_2x2", 0, 0, 0, 0)], CATALOGO)


def test_mesma_semente_mesma_luta():
    forte = Atributos(vida=150, ataque=40, defesa=10, velocidade=15, precisao=90)
    fraco = Atributos(vida=80, ataque=6, defesa=2, velocidade=2, precisao=55)
    assert lutar(forte, fraco, 7) == lutar(forte, fraco, 7)
    vitorias = sum(lutar(forte, fraco, s)[1] == "voce" for s in range(50))
    assert vitorias >= 45  # o mais forte quase sempre ganha


def test_premio_da_vitoria_so_na_primeira_vez():
    e = Explorador("abc")
    assert e.registrar_vitoria("lata_velha", 20) == 20
    assert e.registrar_vitoria("lata_velha", 20) == 0
    assert e.saldo == 20


def test_batalha_pelo_site():
    c = TestClient(criar_app(TutorQueNaoFala(), oficina()))
    h = {"X-Explorador": c.post("/api/oficina/exploradores").json()["codigo"]}
    assert c.get("/api/oficina/arena", headers=h).json()["problema"]  # robô vazio
    carrinho = [{"peca_id": p, "x": x, "y": y, "z": z, "giro": 0} for p, x, y, z in [
        ("placa_4x6", -2, 0, -3), ("controlador", -1, 1, -2), ("roda_pequena", -3, 0, -3),
        ("roda_pequena", 2, 0, -3), ("roda_pequena", -3, 0, 1), ("roda_pequena", 2, 0, 1)]]
    assert c.put("/api/oficina/robo", headers=h, json={"pecas": carrinho}).status_code == 200
    arena = c.get("/api/oficina/arena", headers=h).json()
    assert arena["meus_atributos"] and len(arena["rivais"]) == 9
    r = c.post("/api/oficina/batalhas/lata_velha", headers=h).json()
    assert r["vencedor"] in ("voce", "rival", "empate") and r["golpes"]
    assert r["saldo"] == r["premio"]


def test_pecas_destravam_golpes():
    from aptios.oficina.catalogo import RIVAIS
    golpes = {r.id: calcular_atributos(r.pecas, CATALOGO).golpes for r in RIVAIS}
    assert golpes["lata_velha"] == ("encontrao",)
    assert {"garrada", "martelada", "turbo", "laser"} <= set(golpes["mega_garra"])
    luta, _ = lutar(calcular_atributos(RIVAIS[7].pecas, CATALOGO), calcular_atributos(RIVAIS[0].pecas, CATALOGO), 3)
    assert all(g.golpe in golpes["mega_garra"] for g in luta if g.atacante == "voce")


def test_pecas_novas_destravam_golpes_novos():
    robo = [PecaColocada("placa_6x8", -3, 0, -4, 0), PecaColocada("controlador", -1, 1, -1, 0),
            PecaColocada("roda_grande", -4, 0, -4, 0), PecaColocada("roda_grande", 3, 0, -4, 0),
            PecaColocada("disco", -3, 1, 2, 0), PecaColocada("helice", 1, 1, 2, 0), PecaColocada("bobina", -3, 1, -4, 0),
            PecaColocada("blindagem", 1, 1, -4, 0), PecaColocada("camera", -1, 1, -4, 0)]
    from aptios.oficina.dominio import validar_encaixe
    validar_encaixe(robo, CATALOGO)
    a = calcular_atributos(robo, CATALOGO)
    assert {"giro", "rasante", "choque"} <= set(a.golpes)
    assert a.precisao >= 55 + 12 and a.defesa >= 4



def test_guardar_carregar_e_apagar_robos():
    from aptios.oficina.dominio import Explorador
    e = Explorador("x"); e.receber_presentes(CATALOGO)
    carrinho = [PecaColocada("placa_4x6", -2, 0, -3, 0), PecaColocada("controlador", -1, 1, -2, 0)]
    with pytest.raises(RegraDaOficina):
        e.guardar_robo("vazio")                          # bancada vazia não guarda
    e.montar(carrinho, CATALOGO); e.guardar_robo("  Meu   Carrinho ")
    assert list(e.robos_salvos) == ["Meu Carrinho"]      # espaços extras somem
    e.montar([], CATALOGO); e.carregar_robo("Meu Carrinho", CATALOGO)
    assert e.robo == carrinho
    for i in range(Explorador.MAX_ROBOS_SALVOS - 1):
        e.guardar_robo(f"robo {i}")
    with pytest.raises(RegraDaOficina):
        e.guardar_robo("um a mais")                      # coleção cheia
    e.guardar_robo("Meu Carrinho")                       # mas atualizar um que já existe pode
    e.apagar_robo("Meu Carrinho")
    assert "Meu Carrinho" not in e.robos_salvos
    with pytest.raises(RegraDaOficina):
        e.guardar_robo("x" * 31)


def test_robos_salvos_sobrevivem_no_banco(tmp_path):
    from aptios.oficina.infra import ExploradoresSQLite
    repo = ExploradoresSQLite(str(tmp_path / "t.db"))
    of = oficina(repo)
    cod = of.novo_explorador()["codigo"]
    of.salvar_robo(cod, [{"peca_id": "placa_4x6", "x": 0, "y": 0, "z": 0, "giro": 0}])
    estado = of.guardar_robo(cod, "Tanque")
    assert estado["robos_salvos"] == [{"nome": "Tanque", "pecas": 1}]
    assert repo.buscar(cod).robos_salvos["Tanque"][0].peca_id == "placa_4x6"



def test_toda_peca_tem_componente_de_verdade():
    from aptios.oficina.componentes import COMPONENTES, PECA_PARA_COMPONENTES
    assert set(PECA_PARA_COMPONENTES) == set(CATALOGO.pecas)            # nenhuma peça esquecida
    assert all(c in COMPONENTES for v in PECA_PARA_COMPONENTES.values() for c, _ in v)
    assert all(c.seguranca for c in COMPONENTES.values() if not c.comprar and c.id != "enfeite")


def test_lista_de_materiais_soma_e_ensina():
    from aptios.oficina.componentes import lista_de_materiais
    robo = [PecaColocada(p, 0, 0, 0, 0) for p in
            ("placa_4x6", "bloco_2x2", "controlador", "roda_pequena", "roda_pequena", "motor", "motor", "motor", "esteira", "garra", "disco")]
    itens, avisos = lista_de_materiais(robo)
    q = {i.componente.id: i.quantidade for i in itens}
    assert q["chassi"] == 1 and q["arduino_uno"] == 1             # 1 por robô, não importa quantas peças
    assert q["l298n"] == 2                                         # 3 motores → 2 drivers (cada um controla 2)
    assert q["esteira_kit"] == 1 and q["sg90"] == 1                # meia esteira arredonda para 1 kit
    assert not itens[-1].componente.comprar                        # "só no jogo" vai para o fim da lista
    assert any("bateria" in a for a in avisos)
    _, avisos = lista_de_materiais([PecaColocada("roda_pequena", 0, 0, 0, 0)])
    assert any("controlador" in a for a in avisos) and any("motores" in a for a in avisos)


def test_links_de_afiliado_so_https_e_so_o_que_se_compra(tmp_path):
    import json
    from aptios.oficina.infra import LinksDeAfiliado
    arq = tmp_path / "lojas.json"
    arq.write_text(json.dumps({"hcsr04": {"loja": "Loja X", "url": "https://loja.example/hc"},
                               "motor_tt": {"loja": "Loja Y", "url": "http://inseguro.example"},
                               "disco_jogo": {"loja": "Loja Z", "url": "https://loja.example/disco"}}))
    lojas = LinksDeAfiliado(str(arq))
    assert lojas.link("hcsr04")["loja"] == "Loja X" and lojas.link("motor_tt") is None
    of = Oficina(CATALOGO, ExploradoresEmMemoria(), PagamentoDesativado(), PACOTES, RIVAIS, lojas)
    cod = of.novo_explorador()["codigo"]
    of.salvar_robo(cod, [{"peca_id": "controlador", "x": 0, "y": 0, "z": 0, "giro": 0}])
    assert of.materiais(cod)["itens"][0]["link"] is None           # arduino não tem link configurado
    assert LinksDeAfiliado(None).link("hcsr04") is None            # sem arquivo, sem links
