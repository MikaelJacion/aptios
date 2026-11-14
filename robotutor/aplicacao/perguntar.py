"""APLICAÇÃO — o caso de uso "o estudante faz uma pergunta ao tutor".

Esta camada é o "maestro": usa as regras do domínio na ordem certa,
mas não sabe nada de site, de HTTP ou de qual IA está respondendo.
"""
from __future__ import annotations

from typing import AsyncIterator, Iterable, Mapping

from robotutor.dominio.modelos import Conversa, Kit, Mensagem, MensagemInvalida, Tutor


def montar_conversa(kit: str, historico: Iterable[Mapping[str, str]], pergunta: str) -> Conversa:
    """Reconstrói a conversa a partir do que o navegador mandou e valida tudo.

    O servidor não guarda conversas: elas ficam só no navegador do estudante.
    Isso protege a privacidade das crianças. Por isso o histórico chega junto
    com cada pergunta, e aqui conferimos se ele obedece às regras.
    """
    try:
        conversa = Conversa(Kit(kit))
    except ValueError as erro:
        raise MensagemInvalida(f"kit desconhecido: {kit!r}") from erro
    for item in historico:
        conversa.adicionar(Mensagem(item.get("autor", ""), item.get("texto", "")))  # type: ignore[arg-type]
    conversa.perguntar(pergunta)
    return conversa


async def perguntar(conversa: Conversa, tutor: Tutor) -> AsyncIterator[str]:
    async for pedaco in tutor.responder(conversa):
        yield pedaco
