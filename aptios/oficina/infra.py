"""INFRAESTRUTURA DA OFICINA — onde os dados ficam e quem cobra o dinheiro."""
from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import asdict
from pathlib import Path

from aptios.oficina.dominio import Explorador, PacoteDeTokens, PecaColocada, RegraDaOficina


class ExploradoresSQLite:
    """REPOSITÓRIO em SQLite: um arquivo de banco de dados, sem servidor.

    Cada explorador vira uma linha: o código e os dados em JSON.
    """

    def __init__(self, caminho: str | Path = "aptios.db") -> None:
        self._db = sqlite3.connect(str(caminho), check_same_thread=False)
        self._trava = threading.Lock()
        with self._trava:
            self._db.execute("CREATE TABLE IF NOT EXISTS exploradores (codigo TEXT PRIMARY KEY, dados TEXT NOT NULL)")
            self._db.commit()

    def buscar(self, codigo: str) -> Explorador | None:
        with self._trava:
            linha = self._db.execute("SELECT dados FROM exploradores WHERE codigo = ?", (codigo,)).fetchone()
        if not linha:
            return None
        d = json.loads(linha[0])
        return Explorador(
            codigo=codigo,
            saldo=d["saldo"],
            pecas=set(d["pecas"]),
            desafios_feitos=set(d["desafios_feitos"]),
            robo=[PecaColocada(**c) for c in d["robo"]],
        )

    def salvar(self, e: Explorador) -> None:
        dados = json.dumps({
            "saldo": e.saldo,
            "pecas": sorted(e.pecas),
            "desafios_feitos": sorted(e.desafios_feitos),
            "robo": [asdict(c) for c in e.robo],
        })
        with self._trava:
            self._db.execute(
                "INSERT INTO exploradores (codigo, dados) VALUES (?, ?) "
                "ON CONFLICT(codigo) DO UPDATE SET dados = excluded.dados",
                (e.codigo, dados),
            )
            self._db.commit()


class ExploradoresEmMemoria:
    """REPOSITÓRIO de mentirinha, para os testes."""

    def __init__(self) -> None:
        self._dados: dict[str, Explorador] = {}

    def buscar(self, codigo: str) -> Explorador | None:
        return self._dados.get(codigo)

    def salvar(self, explorador: Explorador) -> None:
        self._dados[explorador.codigo] = explorador


class PagamentoDesativado:
    """Por enquanto, a compra com dinheiro está DESLIGADA.

    Antes de ligar, é preciso:
    1. Uma conta de responsável (pai, mãe) com login, porque quem paga é o adulto.
    2. Um provedor de pagamento (Mercado Pago, Stripe) e um webhook que avise
       quando o pagamento foi aprovado. Só então chamamos
       Explorador.creditar_compra(), nunca antes.
    3. Cumprir a LGPD e o ECA Digital (Lei 15.211/2025) para produtos
       usados por crianças.
    Quando estiver pronto, crie uma classe PagamentoMercadoPago com o
    mesmo método iniciar() e troque aqui. O domínio não muda nada.
    """

    def iniciar(self, explorador: Explorador, pacote: PacoteDeTokens) -> str:
        raise RegraDaOficina(
            "a compra de tokens ainda não está disponível. Por enquanto, ganhe tokens resolvendo desafios! 🧩"
        )
