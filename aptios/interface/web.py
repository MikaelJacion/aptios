"""INTERFACE — o site da Aptios: o tutor (/) e a oficina 3D (/oficina).

Rodar:  uvicorn aptios.interface.web:app --reload
"""
from __future__ import annotations

import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from aptios.oficina.aplicacao import ExploradorNaoEncontrado, Oficina
from aptios.oficina.dominio import RegraDaOficina
from aptios.pista.aplicacao import dados_da_pista
from aptios.tutor.aplicacao import montar_conversa, perguntar
from aptios.tutor.dominio import MensagemInvalida, Tutor

PASTA_ESTATICA = Path(__file__).parent / "static"


# ── formatos dos pedidos (o que o navegador manda) ────────────────

class ItemHistorico(BaseModel):
    autor: str
    texto: str


class Pedido(BaseModel):
    kit: str
    pergunta: str
    historico: list[ItemHistorico] = Field(default_factory=list, max_length=60)


class Resposta(BaseModel):
    resposta: int


class PecaNoRobo(BaseModel):
    peca_id: str
    x: int
    y: int
    z: int
    giro: int


class NomeDoRobo(BaseModel):
    nome: str = Field(max_length=60)


class Robo(BaseModel):
    pecas: list[PecaNoRobo] = Field(max_length=300)


class LimiteDePerguntas:
    """Cada computador pode fazer até N pedidos a cada X minutos.

    Cada resposta da IA custa dinheiro. Isso impede que alguém gaste
    tudo de uma vez (de propósito ou sem querer).
    """

    def __init__(self, maximo: int = 30, janela_segundos: int = 600) -> None:
        self.maximo, self.janela = maximo, janela_segundos
        self._pedidos: dict[str, deque[float]] = defaultdict(deque)

    def permitir(self, quem: str) -> bool:
        agora = time.monotonic()
        fila = self._pedidos[quem]
        while fila and agora - fila[0] > self.janela:
            fila.popleft()
        if len(fila) >= self.maximo:
            return False
        fila.append(agora)
        return True


def _quem(request: Request) -> str:
    return request.client.host if request.client else "?"


def criar_app(tutor: Tutor, oficina: Oficina, limite: LimiteDePerguntas | None = None) -> FastAPI:
    """Monta o site com as peças que forem passadas.

    Isso é INJEÇÃO DE DEPENDÊNCIA: nos testes, passamos versões falsas.
    """
    app = FastAPI(title="Aptios")
    limite = limite or LimiteDePerguntas()
    limite_cadastro = LimiteDePerguntas(maximo=10, janela_segundos=3600)

    # ── páginas ──
    @app.get("/")
    async def pagina_inicio() -> FileResponse:
        return FileResponse(PASTA_ESTATICA / "inicio.html")

    @app.get("/ia")
    async def pagina_ia() -> FileResponse:
        return FileResponse(PASTA_ESTATICA / "ia.html")

    @app.get("/oficina")
    async def pagina_oficina() -> FileResponse:
        return FileResponse(PASTA_ESTATICA / "oficina.html")

    @app.get("/pista")
    async def pagina_pista() -> FileResponse:
        return FileResponse(PASTA_ESTATICA / "pista.html")

    # ── pista ── (a página faz a física ao vivo; aqui vai a ficha "oficial")
    @app.get("/api/pista/carro")
    async def carro() -> dict:
        return dados_da_pista(PASTA_ESTATICA / "modelos")

    # ── tutor ──
    @app.post("/api/perguntar")
    async def api_perguntar(pedido: Pedido, request: Request) -> StreamingResponse:
        if not limite.permitir(_quem(request)):
            raise HTTPException(429, "Muitas perguntas seguidas! Descanse uns minutinhos. 😊")
        try:
            conversa = montar_conversa(
                pedido.kit, [i.model_dump() for i in pedido.historico], pedido.pergunta
            )
        except MensagemInvalida as erro:
            raise HTTPException(400, str(erro)) from erro
        return StreamingResponse(perguntar(conversa, tutor), media_type="text/plain; charset=utf-8")

    # ── oficina ──
    # O código do explorador vai no cabeçalho X-Explorador, e não no endereço,
    # para não aparecer no histórico do navegador nem nos registros do servidor.
    def executar(acao, *args: Any) -> Any:
        try:
            return acao(*args)
        except ExploradorNaoEncontrado as erro:
            raise HTTPException(404, str(erro)) from erro
        except RegraDaOficina as erro:
            raise HTTPException(400, str(erro)) from erro

    @app.get("/api/oficina/catalogo")
    async def catalogo() -> dict:
        return oficina.catalogo_publico()

    @app.post("/api/oficina/exploradores")
    async def novo_explorador(request: Request) -> dict:
        if not limite_cadastro.permitir(_quem(request)):
            raise HTTPException(429, "Muitos cadastros seguidos. Tente mais tarde.")
        return oficina.novo_explorador()

    @app.get("/api/oficina/eu")
    async def estado(x_explorador: str = Header("")) -> dict:
        return executar(oficina.estado, x_explorador)

    @app.post("/api/oficina/desafios/{desafio_id}")
    async def desafio(desafio_id: str, corpo: Resposta, x_explorador: str = Header("")) -> dict:
        return executar(oficina.resolver_desafio, x_explorador, desafio_id, corpo.resposta)

    @app.post("/api/oficina/pecas/{peca_id}")
    async def comprar(peca_id: str, x_explorador: str = Header("")) -> dict:
        return executar(oficina.comprar_peca, x_explorador, peca_id)

    @app.put("/api/oficina/robo")
    async def robo(corpo: Robo, x_explorador: str = Header("")) -> dict:
        return executar(oficina.salvar_robo, x_explorador, [p.model_dump() for p in corpo.pecas])

    # coleção de robôs: o nome vai no corpo (e não no endereço) por causa de espaços e acentos
    @app.post("/api/oficina/robos/guardar")
    async def guardar(corpo: NomeDoRobo, x_explorador: str = Header("")) -> dict:
        return executar(oficina.guardar_robo, x_explorador, corpo.nome)

    @app.post("/api/oficina/robos/carregar")
    async def carregar(corpo: NomeDoRobo, x_explorador: str = Header("")) -> dict:
        return executar(oficina.carregar_robo, x_explorador, corpo.nome)

    @app.post("/api/oficina/robos/apagar")
    async def apagar(corpo: NomeDoRobo, x_explorador: str = Header("")) -> dict:
        return executar(oficina.apagar_robo, x_explorador, corpo.nome)

    @app.get("/api/oficina/materiais")
    async def materiais(x_explorador: str = Header("")) -> dict:
        return executar(oficina.materiais, x_explorador)

    @app.get("/api/oficina/arena")
    async def arena(x_explorador: str = Header("")) -> dict:
        return executar(oficina.arena, x_explorador)

    @app.post("/api/oficina/batalhas/{rival_id}")
    async def batalha(rival_id: str, request: Request, x_explorador: str = Header("")) -> dict:
        if not limite.permitir(_quem(request)):
            raise HTTPException(429, "Muitas batalhas seguidas! Deixe os robôs descansarem um pouco. 🔋")
        return executar(oficina.batalhar, x_explorador, rival_id)

    @app.post("/api/oficina/tokens/{pacote_id}")
    async def tokens(pacote_id: str, x_explorador: str = Header("")) -> dict:
        return executar(oficina.comprar_tokens, x_explorador, pacote_id)

    # Modelos 3D (.glb) feitos no Meshy ficam em static/modelos/
    app.mount("/static", StaticFiles(directory=PASTA_ESTATICA), name="static")
    return app


def _app_padrao() -> FastAPI:
    from aptios.oficina.catalogo import CATALOGO, PACOTES, RIVAIS
    from aptios.oficina.infra import ExploradoresSQLite, LinksDeAfiliado, PagamentoDesativado
    from aptios.tutor.claude import TutorClaude

    oficina = Oficina(CATALOGO, ExploradoresSQLite(os.environ.get("APTIOS_DB", "aptios.db")),
                      PagamentoDesativado(), PACOTES, RIVAIS,
                      LinksDeAfiliado(os.environ.get("APTIOS_LOJAS", os.path.expanduser("~/.config/aptios/lojas.json"))))
    return criar_app(TutorClaude(), oficina)


app = _app_padrao()
