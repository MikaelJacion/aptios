"""Desenha os ícones do app da Aptios (PNG) pixel por pixel, sem biblioteca nenhuma.

Uso:  venv/bin/python ferramentas/gerar_icones.py

Um PNG por dentro é: uma assinatura, um cabeçalho (IHDR) com largura e altura,
os pixels comprimidos com zlib (IDAT) e um fim (IEND). Cada pedaço tem um CRC,
que é uma "conta de conferência" para saber se o arquivo chegou inteiro.
"""
import struct
import zlib
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent / "aptios/interface/static"
AZUL, AMARELO, TINTA, BRANCO = (42, 91, 215), (255, 207, 51), (27, 36, 48), (255, 255, 255)


def dentro_arredondado(x, y, x0, y0, x1, y1, r):
    """O ponto (x, y) está dentro de um retângulo de cantos arredondados?"""
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return False
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def cor_do_pixel(u, v, escala):
    """u, v vão de 0 a 1. 'escala' encolhe o desenho (o ícone 'maskable' precisa de margem)."""
    # leva o ponto para um sistema em que o desenho ocupa o centro
    x, y = (u - .5) / escala + .5, (v - .5) / escala + .5
    if (x - .5) ** 2 + (y - .17) ** 2 <= .045 ** 2:                 # bolinha da antena
        return AMARELO
    if abs(x - .5) <= .015 and .17 <= y <= .3:                       # haste da antena
        return AMARELO
    if dentro_arredondado(x, y, .2, .3, .8, .78, .1):               # cabeça do robô
        for ox in (.37, .63):                                        # olhos
            if (x - ox) ** 2 + (y - .5) ** 2 <= .075 ** 2:
                return BRANCO if (x - ox - .02) ** 2 + (y - .49) ** 2 > .035 ** 2 else TINTA
        if dentro_arredondado(x, y, .36, .62, .64, .68, .03):        # boca
            return TINTA
        return AMARELO
    return AZUL


def png(tamanho, escala, arredondar):
    linhas = bytearray()
    for j in range(tamanho):
        linhas.append(0)  # filtro 0 = "sem filtro" no começo de cada linha
        for i in range(tamanho):
            u, v = (i + .5) / tamanho, (j + .5) / tamanho
            if arredondar and not dentro_arredondado(u, v, 0, 0, 1, 1, .2):
                linhas += bytes((0, 0, 0, 0))                         # canto transparente
            else:
                linhas += bytes((*cor_do_pixel(u, v, escala), 255))

    def pedaco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados))

    cabecalho = struct.pack(">IIBBBBB", tamanho, tamanho, 8, 6, 0, 0, 0)   # 8 bits, RGBA
    return b"\x89PNG\r\n\x1a\n" + pedaco(b"IHDR", cabecalho) + pedaco(b"IDAT", zlib.compress(bytes(linhas), 9)) + pedaco(b"IEND", b"")


if __name__ == "__main__":
    for nome, tamanho, escala, arredondar in [("icone-192.png", 192, 1, True), ("icone-512.png", 512, 1, True),
                                              ("icone-maskable-512.png", 512, .72, False), ("apple-touch-icon.png", 180, .9, False)]:
        (PASTA / nome).write_bytes(png(tamanho, escala, arredondar))
        print("✅", nome)
