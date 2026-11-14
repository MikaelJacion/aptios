"""INTERFACE — o site: recebe a pergunta pela internet e devolve a resposta.

Rodar:  uvicorn robotutor.interface.web:app --reload
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from robotutor.aplicacao.perguntar import montar_conversa, perguntar
from robotutor.dominio.modelos import MensagemInvalida, Tutor

PASTA_ESTATICA = Path(__file__).parent / "static"


class ItemHistorico(BaseModel):
    autor: str
    texto: str


class Pedido(BaseModel):
    kit: str
    pergunta: str
    historico: list[ItemHistorico] = Field(default_factory=list, max_length=60)


class LimiteDePerguntas:
    """Cada computador pode fazer até N perguntas a cada X minutos.

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


def criar_app(tutor: Tutor, limite: LimiteDePerguntas | None = None) -> FastAPI:
    """Monta o site com o tutor que for passado.

    Isso é INJEÇÃO DE DEPENDÊNCIA: nos testes, passamos um tutor falso.
    """
    app = FastAPI(title="RoboTutor")
    limite = limite or LimiteDePerguntas()

    @app.get("/")
    async def pagina() -> FileResponse:
        return FileResponse(PASTA_ESTATICA / "index.html")

    @app.post("/api/perguntar")
    async def api_perguntar(pedido: Pedido, request: Request) -> StreamingResponse:
        quem = request.client.host if request.client else "?"
        if not limite.permitir(quem):
            raise HTTPException(429, "Muitas perguntas seguidas! Descanse uns minutinhos. 😊")
        try:
            conversa = montar_conversa(
                pedido.kit, [i.model_dump() for i in pedido.historico], pedido.pergunta
            )
        except MensagemInvalida as erro:
            raise HTTPException(400, str(erro)) from erro
        return StreamingResponse(perguntar(conversa, tutor), media_type="text/plain; charset=utf-8")

    return app


def _app_padrao() -> FastAPI:
    from robotutor.infra.tutor_claude import TutorClaude

    return criar_app(TutorClaude())


app = _app_padrao()
