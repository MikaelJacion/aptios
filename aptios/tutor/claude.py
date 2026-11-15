"""INFRAESTRUTURA — o tutor de verdade, feito com o Claude (API da Anthropic).

Este é um ADAPTADOR: ele "encaixa" o Claude na porta `Tutor` do domínio.
Se um dia trocarmos de IA, só este arquivo muda.
"""
from __future__ import annotations

import logging
from typing import AsyncIterator

import anthropic

from aptios.tutor.dominio import Conversa
from aptios.tutor.prompt import prompt_do_sistema

log = logging.getLogger(__name__)

MODELO = "claude-opus-5-5"

AVISO_RECUSA = "\n\n🤖 Hmm, sobre isso eu não posso ajudar. Que tal voltarmos ao seu robô?"
AVISO_FALHA = "\n\n🔧 Ops! Tive um probleminha para responder. Tente de novo daqui a pouco."
AVISO_CHAVE = "\n\n🔑 O tutor ainda não foi configurado. Peça para um adulto colocar a chave da API."


class TutorClaude:
    def __init__(self, cliente: anthropic.AsyncAnthropic | None = None) -> None:
        # Sem argumentos, o SDK lê a chave da variável ANTHROPIC_API_KEY.
        # NUNCA escreva a chave no código: ela iria parar no GitHub!
        # O cliente só é criado na primeira pergunta, assim o site abre mesmo sem chave.
        self._cliente = cliente

    async def responder(self, conversa: Conversa) -> AsyncIterator[str]:
        if self._cliente is None:
            try:
                self._cliente = anthropic.AsyncAnthropic()
            except anthropic.AnthropicError:
                yield AVISO_CHAVE
                return
        mensagens = [
            {"role": "user" if m.autor == "estudante" else "assistant", "content": m.texto}
            for m in conversa.recentes()
        ]
        try:
            async with self._cliente.beta.messages.stream(
                model=MODELO,
                max_tokens=16000,
                system=prompt_do_sistema(conversa.kit),
                messages=mensagens,
                # "low" = respostas rápidas e mais baratas, ótimo para um chat.
                output_config={"effort": "low"},
                cache_control={"type": "ephemeral"},
                # Se o modelo recusar por segurança, a API tenta um modelo reserva.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            ) as stream:
                async for texto in stream.text_stream:
                    yield texto
                final = await stream.get_final_message()
            if final.stop_reason == "refusal":
                yield AVISO_RECUSA
        except anthropic.AuthenticationError:
            yield AVISO_CHAVE
        except TypeError as erro:
            # O SDK avisa assim quando não acha nenhuma chave configurada.
            if "authentication" not in str(erro):
                raise
            yield AVISO_CHAVE
        except (anthropic.RateLimitError, anthropic.APIStatusError, anthropic.APIConnectionError):
            log.exception("Falha ao chamar a API da Anthropic")
            yield AVISO_FALHA
