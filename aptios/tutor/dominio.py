"""DOMÍNIO — as regras do RoboTutor, sem nenhuma tecnologia.

Aqui não existe internet, IA, nem site. Só as ideias do assunto:
um estudante conversa com um tutor sobre um kit de robótica.
Por isso este arquivo pode ser testado sem gastar nada e sem internet.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator, Literal, Protocol


class Kit(str, Enum):
    """Os kits que o tutor sabe ensinar (Linguagem Ubíqua: "kit")."""

    SCRATCH = "scratch"
    LEGO_SPIKE = "lego_spike"
    LEGO_EV3 = "lego_ev3"
    ARDUINO = "arduino"
    PISTA = "pista"  # o simulador de carros elétricos da Aptios

    @property
    def nome(self) -> str:
        return {
            Kit.SCRATCH: "Scratch",
            Kit.LEGO_SPIKE: "LEGO SPIKE",
            Kit.LEGO_EV3: "LEGO Mindstorms EV3",
            Kit.ARDUINO: "Arduino",
            Kit.PISTA: "Pista (física dos carros)",
        }[self]


class MensagemInvalida(ValueError):
    """Uma regra do domínio foi quebrada (ex.: pergunta vazia ou gigante)."""


Autor = Literal["estudante", "tutor"]


@dataclass(frozen=True)
class Mensagem:
    """VALUE OBJECT: duas mensagens com o mesmo autor e texto são iguais.

    `frozen=True` = depois de criada, não muda. Isso evita bugs do tipo
    "alguém alterou a mensagem no meio do caminho".
    """

    autor: Autor
    texto: str

    TAMANHO_MAXIMO = 1000  # caracteres por pergunta do estudante

    def __post_init__(self) -> None:
        if self.autor not in ("estudante", "tutor"):
            raise MensagemInvalida(f"autor desconhecido: {self.autor!r}")
        if not self.texto.strip():
            raise MensagemInvalida("a mensagem está vazia")
        if self.autor == "estudante" and len(self.texto) > self.TAMANHO_MAXIMO:
            raise MensagemInvalida(
                f"a pergunta pode ter no máximo {self.TAMANHO_MAXIMO} caracteres"
            )


@dataclass
class Conversa:
    """ENTIDADE: uma conversa entre o estudante e o tutor, sobre um kit.

    Ela protege as próprias regras: começa sempre pelo estudante,
    os autores se revezam, e só as últimas mensagens vão para o tutor.
    """

    kit: Kit
    mensagens: list[Mensagem] = field(default_factory=list)

    MEMORIA = 20  # quantas mensagens recentes o tutor "lembra"

    def adicionar(self, mensagem: Mensagem) -> None:
        esperado: Autor = "estudante" if not self.mensagens or self.mensagens[-1].autor == "tutor" else "tutor"
        if mensagem.autor != esperado:
            raise MensagemInvalida(f"era a vez do {esperado} falar")
        self.mensagens.append(mensagem)

    def perguntar(self, texto: str) -> None:
        self.adicionar(Mensagem("estudante", texto))

    def recentes(self) -> list[Mensagem]:
        """As últimas mensagens, sempre começando por uma do estudante."""
        janela = self.mensagens[-self.MEMORIA:]
        while janela and janela[0].autor != "estudante":
            janela = janela[1:]
        return janela


class Tutor(Protocol):
    """PORTA: o que o domínio precisa de um tutor, sem dizer COMO ele funciona.

    Hoje quem responde é o Claude (ver infra/tutor_claude.py). Nos testes,
    é um tutor falso. O domínio não sabe e não precisa saber a diferença.
    """

    def responder(self, conversa: Conversa) -> AsyncIterator[str]:
        """Devolve a resposta aos pedacinhos, conforme ela vai sendo escrita."""
        ...
