"""DOMÍNIO DA OFICINA — peças, tokens, desafios e robôs montados.

É outro CONTEXTO DELIMITADO, separado do tutor. Aqui "token" quer dizer
a moeda da oficina. Nada a ver com os "tokens" que a IA usa para contar
palavras. Em cada contexto, cada palavra tem um sentido só.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol

Categoria = Literal["estrutura", "roda", "motor", "sensor", "controlador", "enfeite"]


class RegraDaOficina(ValueError):
    """Alguma regra foi quebrada. A mensagem é mostrada para a criança."""


@dataclass(frozen=True)
class Peca:
    """VALUE OBJECT: uma peça do catálogo.

    O modelo 3D vem do Meshy: exporte em .glb e salve como
    aptios/interface/static/modelos/<id>.glb. Sem o arquivo, a oficina
    desenha uma forma simples no lugar.
    """

    id: str
    nome: str
    categoria: Categoria
    preco: int  # em tokens; 0 = já vem de presente
    cor: str  # cor da forma simples, em hexadecimal (#rrggbb)
    tamanho: tuple[int, int, int]  # largura, altura, profundidade, em "pinos" da grade
    descricao: str


@dataclass(frozen=True)
class Desafio:
    """VALUE OBJECT: uma pergunta que vale tokens. Cada um só paga uma vez."""

    id: str
    trilha: str  # scratch, lego_spike, lego_ev3, arduino
    titulo: str
    pergunta: str
    opcoes: tuple[str, ...]
    correta: int  # índice da opção certa
    recompensa: int
    explicacao: str
    nivel: Literal["facil", "medio", "dificil"] = "facil"


@dataclass(frozen=True)
class PecaColocada:
    """VALUE OBJECT: onde uma peça foi colocada no robô."""

    peca_id: str
    x: int
    y: int
    z: int
    giro: int  # 0, 90, 180 ou 270 graus

    def __post_init__(self) -> None:
        if self.giro not in (0, 90, 180, 270):
            raise RegraDaOficina("a peça só gira de 90 em 90 graus")
        if not (-20 <= self.x <= 20 and 0 <= self.y <= 40 and -20 <= self.z <= 20):
            raise RegraDaOficina("a peça saiu da bancada")


@dataclass
class Explorador:
    """ENTIDADE (e raiz do agregado): o estudante dentro da oficina.

    É a ÚNICA porta para mudar saldo, peças e robô. Assim ninguém consegue
    "dar um jeitinho" e aumentar o saldo sem passar pelas regras.
    Não guardamos nome nem dados pessoais: só um código secreto.
    """

    codigo: str
    saldo: int = 0
    pecas: set[str] = field(default_factory=set)
    desafios_feitos: set[str] = field(default_factory=set)
    robo: list[PecaColocada] = field(default_factory=list)
    vitorias: set[str] = field(default_factory=set)  # rivais que já venceu

    MAX_PECAS_NO_ROBO = 300

    def receber_presentes(self, catalogo: Catalogo) -> None:
        self.pecas |= {p.id for p in catalogo.pecas.values() if p.preco == 0}

    def resolver_desafio(self, desafio: Desafio, resposta: int) -> bool:
        if desafio.id in self.desafios_feitos:
            raise RegraDaOficina("você já ganhou os tokens deste desafio")
        if resposta != desafio.correta:
            return False
        self.desafios_feitos.add(desafio.id)
        self.saldo += desafio.recompensa
        return True

    def comprar(self, peca: Peca) -> None:
        if peca.id in self.pecas:
            raise RegraDaOficina("você já tem esta peça. Pode usar quantas vezes quiser!")
        if self.saldo < peca.preco:
            raise RegraDaOficina(f"faltam {peca.preco - self.saldo} tokens para esta peça")
        self.saldo -= peca.preco
        self.pecas.add(peca.id)

    def creditar_compra(self, tokens: int) -> None:
        """Tokens comprados com dinheiro. Só o caso de uso de pagamento chama isto."""
        if tokens <= 0:
            raise RegraDaOficina("quantidade de tokens inválida")
        self.saldo += tokens

    def registrar_vitoria(self, rival_id: str, premio: int) -> int:
        """Vencer um rival paga tokens só na PRIMEIRA vez. Revanche vale pela glória!"""
        if rival_id in self.vitorias:
            return 0
        self.vitorias.add(rival_id)
        self.saldo += premio
        return premio

    def montar(self, robo: list[PecaColocada], catalogo: Catalogo) -> None:
        if len(robo) > self.MAX_PECAS_NO_ROBO:
            raise RegraDaOficina(f"o robô pode ter no máximo {self.MAX_PECAS_NO_ROBO} peças")
        faltando = {c.peca_id for c in robo} - self.pecas
        if faltando:
            raise RegraDaOficina(f"você ainda não tem: {', '.join(sorted(faltando))}")
        validar_encaixe(robo, catalogo)
        self.robo = list(robo)


@dataclass(frozen=True)
class Catalogo:
    pecas: dict[str, Peca]
    desafios: dict[str, Desafio]

    def peca(self, peca_id: str) -> Peca:
        try:
            return self.pecas[peca_id]
        except KeyError:
            raise RegraDaOficina(f"peça desconhecida: {peca_id}") from None

    def desafio(self, desafio_id: str) -> Desafio:
        try:
            return self.desafios[desafio_id]
        except KeyError:
            raise RegraDaOficina(f"desafio desconhecido: {desafio_id}") from None


LIMITE_BANCADA = 12  # a bancada vai de -12 a +12 pinos


def celulas(peca: Peca, c: PecaColocada) -> set[tuple[int, int, int]]:
    """Os "cubinhos" da grade que a peça ocupa. Girar 90° troca largura e profundidade."""
    w, h, d = peca.tamanho
    if c.giro % 180:
        w, d = d, w
    return {(c.x + i, c.y + j, c.z + k) for i in range(w) for j in range(h) for k in range(d)}


def validar_encaixe(robo: list[PecaColocada], catalogo: Catalogo) -> None:
    """Duas peças não ocupam o mesmo lugar, e nenhuma sai da bancada."""
    ocupado: set[tuple[int, int, int]] = set()
    for c in robo:
        cubos = celulas(catalogo.peca(c.peca_id), c)
        if any(not (-LIMITE_BANCADA <= x < LIMITE_BANCADA and -LIMITE_BANCADA <= z < LIMITE_BANCADA) for x, _, z in cubos):
            raise RegraDaOficina("uma peça saiu da bancada")
        if cubos & ocupado:
            raise RegraDaOficina("duas peças estão no mesmo lugar")
        ocupado |= cubos


# ── PORTAS: o que o domínio precisa do mundo lá fora ─────────────

class Exploradores(Protocol):
    """REPOSITÓRIO: guarda e busca exploradores (hoje em SQLite)."""

    def buscar(self, codigo: str) -> Explorador | None: ...
    def salvar(self, explorador: Explorador) -> None: ...


@dataclass(frozen=True)
class PacoteDeTokens:
    id: str
    tokens: int
    preco_centavos: int


class Pagamentos(Protocol):
    """Quem cobra o dinheiro de verdade (Mercado Pago, Stripe...)."""

    def iniciar(self, explorador: Explorador, pacote: PacoteDeTokens) -> str:
        """Devolve o link de pagamento, que um ADULTO precisa abrir."""
        ...
