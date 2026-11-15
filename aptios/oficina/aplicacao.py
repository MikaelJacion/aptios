"""APLICAÇÃO DA OFICINA — os casos de uso, um método para cada ação da criança.

Repare no padrão de todos: 1) buscar o explorador, 2) pedir para o
DOMÍNIO aplicar a regra, 3) salvar. A regra mora no domínio, nunca aqui.
"""
from __future__ import annotations

import secrets
from dataclasses import asdict
from typing import Any, Iterable, Mapping

from aptios.oficina.batalha import MOVIMENTOS, Rival, calcular_atributos, lutar
from aptios.oficina.dominio import (
    Catalogo, Explorador, Exploradores, PacoteDeTokens, Pagamentos, PecaColocada, RegraDaOficina,
)


class ExploradorNaoEncontrado(LookupError):
    pass


class Oficina:
    def __init__(self, catalogo: Catalogo, exploradores: Exploradores,
                 pagamentos: Pagamentos, pacotes: Iterable[PacoteDeTokens],
                 rivais: Iterable[Rival] = ()) -> None:
        self.catalogo = catalogo
        self.exploradores = exploradores
        self.pagamentos = pagamentos
        self.pacotes = {p.id: p for p in pacotes}
        self.rivais = {r.id: r for r in rivais}

    # ── consultas ───────────────────────────────────────────────
    def catalogo_publico(self) -> dict[str, Any]:
        """O que o site pode mostrar. As respostas certas NÃO vão junto!"""
        return {
            "pecas": [asdict(p) for p in self.catalogo.pecas.values()],
            "desafios": [
                {k: v for k, v in asdict(d).items() if k not in ("correta", "explicacao")}
                for d in self.catalogo.desafios.values()
            ],
            "pacotes": [asdict(p) for p in self.pacotes.values()],
            "golpes": {k: asdict(m) for k, m in MOVIMENTOS.items()},
        }

    def estado(self, codigo: str) -> dict[str, Any]:
        return self._publico(self._buscar(codigo))

    # ── ações ───────────────────────────────────────────────────
    def novo_explorador(self) -> dict[str, Any]:
        explorador = Explorador(codigo=secrets.token_urlsafe(18))
        explorador.receber_presentes(self.catalogo)
        self.exploradores.salvar(explorador)
        return {"codigo": explorador.codigo, **self._publico(explorador)}

    def resolver_desafio(self, codigo: str, desafio_id: str, resposta: int) -> dict[str, Any]:
        explorador = self._buscar(codigo)
        desafio = self.catalogo.desafio(desafio_id)
        acertou = explorador.resolver_desafio(desafio, resposta)
        self.exploradores.salvar(explorador)
        return {
            "acertou": acertou,
            "explicacao": desafio.explicacao if acertou else "Quase! Pense mais um pouquinho e tente de novo.",
            **self._publico(explorador),
        }

    def comprar_peca(self, codigo: str, peca_id: str) -> dict[str, Any]:
        explorador = self._buscar(codigo)
        explorador.comprar(self.catalogo.peca(peca_id))
        self.exploradores.salvar(explorador)
        return self._publico(explorador)

    def salvar_robo(self, codigo: str, pecas: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
        explorador = self._buscar(codigo)
        robo = []
        for p in pecas:
            self.catalogo.peca(str(p["peca_id"]))  # a peça precisa existir
            robo.append(PecaColocada(str(p["peca_id"]), int(p["x"]), int(p["y"]), int(p["z"]), int(p["giro"])))
        explorador.montar(robo, self.catalogo)
        self.exploradores.salvar(explorador)
        return self._publico(explorador)

    def guardar_robo(self, codigo: str, nome: str) -> dict[str, Any]:
        explorador = self._buscar(codigo)
        explorador.guardar_robo(nome)
        self.exploradores.salvar(explorador)
        return self._publico(explorador)

    def carregar_robo(self, codigo: str, nome: str) -> dict[str, Any]:
        explorador = self._buscar(codigo)
        explorador.carregar_robo(nome, self.catalogo)
        self.exploradores.salvar(explorador)
        return self._publico(explorador)

    def apagar_robo(self, codigo: str, nome: str) -> dict[str, Any]:
        explorador = self._buscar(codigo)
        explorador.apagar_robo(nome)
        self.exploradores.salvar(explorador)
        return self._publico(explorador)

    def arena(self, codigo: str) -> dict[str, Any]:
        explorador = self._buscar(codigo)
        try:
            meus, problema = asdict(calcular_atributos(explorador.robo, self.catalogo)), None
        except RegraDaOficina as erro:
            meus, problema = None, str(erro)
        return {
            "meus_atributos": meus,
            "problema": problema,
            "rivais": [
                {"id": r.id, "nome": r.nome, "nivel": r.nivel, "premio": r.premio, "descricao": r.descricao,
                 "atributos": asdict(calcular_atributos(r.pecas, self.catalogo)),
                 "pecas": [asdict(c) for c in r.pecas], "vencido": r.id in explorador.vitorias}
                for r in self.rivais.values()
            ],
        }

    def batalhar(self, codigo: str, rival_id: str) -> dict[str, Any]:
        """A luta é decidida AQUI no servidor, com o robô que está salvo."""
        explorador = self._buscar(codigo)
        rival = self.rivais.get(rival_id)
        if not rival:
            raise RegraDaOficina("rival desconhecido")
        voce = calcular_atributos(explorador.robo, self.catalogo)
        dele = calcular_atributos(rival.pecas, self.catalogo)
        golpes, vencedor = lutar(voce, dele, semente=secrets.randbelow(2**31))
        premio = explorador.registrar_vitoria(rival.id, rival.premio) if vencedor == "voce" else 0
        self.exploradores.salvar(explorador)
        return {
            "voce": asdict(voce), "rival": asdict(dele),
            "golpes": [asdict(g) for g in golpes], "vencedor": vencedor, "premio": premio,
            **self._publico(explorador),
        }

    def comprar_tokens(self, codigo: str, pacote_id: str) -> dict[str, str]:
        explorador = self._buscar(codigo)
        pacote = self.pacotes.get(pacote_id)
        if not pacote:
            raise RegraDaOficina("pacote desconhecido")
        return {"link_pagamento": self.pagamentos.iniciar(explorador, pacote)}

    # ── ajudantes ───────────────────────────────────────────────
    def _buscar(self, codigo: str) -> Explorador:
        explorador = self.exploradores.buscar(codigo) if codigo else None
        if explorador is None:
            raise ExploradorNaoEncontrado("explorador não encontrado")
        return explorador

    @staticmethod
    def _publico(e: Explorador) -> dict[str, Any]:
        return {
            "saldo": e.saldo,
            "pecas": sorted(e.pecas),
            "desafios_feitos": sorted(e.desafios_feitos),
            "robo": [asdict(c) for c in e.robo],
            "vitorias": sorted(e.vitorias),
            "robos_salvos": [{"nome": n, "pecas": len(r)} for n, r in e.robos_salvos.items()],
        }
