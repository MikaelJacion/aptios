"""COMPONENTES REAIS — cada peça do jogo representa uma peça que existe de verdade.

Ideia do pai do Mikael: mostrar a ficha técnica de cada peça e, se a família
quiser montar o robô de verdade, gerar a LISTA DE MATERIAIS. Os links de compra
(de lojas parceiras/afiliadas) ficam numa PORTA (LojasParceiras) e só aparecem
para um adulto. Veja o ADR-009 em docs/ARQUITETURA.md.

Tudo aqui é puro: dados e uma função que soma as peças. Nada de internet.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Protocol

from aptios.oficina.dominio import PecaColocada


@dataclass(frozen=True)
class ComponenteReal:
    """VALUE OBJECT: um componente eletrônico ou mecânico de verdade."""

    id: str
    nome: str
    especificacoes: tuple[tuple[str, str], ...]
    aprender: str           # o que a criança aprende com ele
    seguranca: str = ""     # cuidado importante (vai em destaque)
    comprar: bool = True    # False = só existe no jogo, ou é "faça você mesmo"


def _c(id: str, nome: str, specs: dict[str, str], aprender: str, seguranca: str = "", comprar: bool = True) -> ComponenteReal:
    return ComponenteReal(id, nome, tuple(specs.items()), aprender, seguranca, comprar)


COMPONENTES = {c.id: c for c in [
    _c("arduino_uno", "Placa Arduino Uno (ou compatível)",
       {"Microcontrolador": "ATmega328P", "Tensão": "5 V", "Pinos digitais": "14 (6 com PWM)", "Entradas analógicas": "6", "Ligação": "USB"},
       "É o cérebro do robô: lê os sensores e liga os motores seguindo o programa que você escreve."),
    _c("protoboard", "Protoboard + jumpers (fios)",
       {"Protoboard": "400 ou 830 furos", "Jumpers": "macho-macho e macho-fêmea"},
       "Serve para ligar os fios sem solda. Dá para montar, testar e mudar à vontade."),
    _c("chassi", "Chassi de MDF ou acrílico (ou blocos de montar)",
       {"Material": "MDF 3 mm, acrílico ou blocos compatíveis", "Fixação": "parafusos M3 ou encaixe"},
       "É o esqueleto do robô. Na vida real, dá até para fazer com papelão grosso para testar."),
    _c("roda_65", "Roda de borracha 65 mm",
       {"Diâmetro": "65 mm", "Encaixe": "eixo do motor TT"},
       "Roda maior anda mais a cada volta: a distância de uma volta é o diâmetro × 3,14."),
    _c("roda_grande", "Roda de borracha grande (80 a 90 mm)",
       {"Diâmetro": "80 a 90 mm", "Encaixe": "eixo do motor TT ou cubo próprio"},
       "Passa melhor por cima de obstáculos, mas precisa de mais força do motor."),
    _c("esteira_kit", "Kit de esteiras (par)",
       {"Conteúdo": "2 esteiras, rodas dentadas e eixos", "Uso": "chassi tipo tanque"},
       "A esteira espalha o peso do robô e não atola: é por isso que tratores e tanques usam."),
    _c("motor_tt", "Motor DC com caixa de redução (motor TT)",
       {"Tensão": "3 a 6 V", "Velocidade": "cerca de 200 rpm a 6 V", "Eixo": "duplo"},
       "A caixa de redução troca velocidade por força: o motor gira rápido, e a roda gira devagar mas com força."),
    _c("l298n", "Driver de motor L298N",
       {"Motores": "2 motores DC", "Corrente": "até 2 A por canal", "Tensão dos motores": "5 a 35 V"},
       "O Arduino não aguenta a corrente de um motor. O driver é o 'músculo' que liga o motor quando o Arduino manda.",
       "Nunca ligue um motor direto no pino do Arduino: pode queimar a placa."),
    _c("sg90", "Micro servo SG90 (9 g)",
       {"Giro": "0° a 180°", "Tensão": "4,8 a 6 V", "Fios": "marrom (GND), vermelho (5 V), laranja (sinal)"},
       "O servo vira até um ângulo exato que você escolhe no programa. Ótimo para braços e garras."),
    _c("garra_kit", "Garra robótica (kit de acrílico ou metal)",
       {"Movimento": "abre e fecha com 1 servo", "Servo usado": "SG90 ou MG996R (ver o kit)"},
       "A garra transforma o giro do servo em abrir e fechar, usando engrenagens ou alavancas."),
    _c("hcsr04", "Sensor ultrassônico HC-SR04",
       {"Alcance": "2 a 400 cm", "Tensão": "5 V", "Pinos": "VCC, Trig, Echo, GND", "Ângulo": "cerca de 15°"},
       "Funciona como o morcego: manda um som agudo que a gente não ouve e mede quanto tempo o eco demora para voltar."),
    _c("tcs34725", "Sensor de cor TCS34725",
       {"Ligação": "I2C (SDA, SCL)", "Tensão": "3,3 a 5 V", "Mede": "vermelho, verde, azul e claridade"},
       "Ele mede quanto de cada cor a superfície reflete. Com isso, o robô consegue seguir uma linha no chão."),
    _c("microswitch", "Chave fim de curso (micro switch)",
       {"Contato": "normalmente aberto ou fechado", "Ligação": "pino digital com INPUT_PULLUP"},
       "É um botão que o robô aperta quando encosta em algo: o jeito mais simples de 'sentir' uma batida."),
    _c("mpu6050", "Giroscópio e acelerômetro MPU-6050",
       {"Eixos": "3 de giro + 3 de aceleração", "Ligação": "I2C", "Tensão": "3,3 a 5 V"},
       "Sente para onde o robô está virando e se ele está inclinado. Celulares têm um sensor parecido."),
    _c("esp32cam", "Módulo ESP32-CAM",
       {"Câmera": "OV2640 (2 MP)", "Comunicação": "Wi-Fi", "Tensão": "5 V"},
       "Uma plaquinha com câmera e Wi-Fi: dá para ver no celular o que o robô está vendo."),
    _c("suporte_18650", "Suporte para 2 baterias 18650 (com baterias)",
       {"Tensão": "cerca de 7,4 V (2 em série)", "Tipo": "lítio recarregável"},
       "A bateria guarda energia química e entrega energia elétrica. Quanto mais mAh, mais tempo o robô anda.",
       "Bateria de lítio só com um adulto por perto: use o carregador certo e nunca fure, amasse ou esquente."),
    _c("led_5mm", "LED 5 mm + resistor de 220 Ω",
       {"Tensão do LED": "cerca de 2 V", "Resistor": "220 Ω (limita a corrente)"},
       "O resistor protege o LED: sem ele, passa corrente demais e o LED queima na hora."),
    _c("helice_motor", "Motor coreless com hélice",
       {"Tensão": "3,7 V", "Uso": "minidrones"},
       "A hélice empurra o ar para baixo, e o ar empurra a hélice para cima: é a 3ª lei de Newton!",
       "A hélice gira muito rápido: use protetor de hélice e mantenha os dedos longe."),
    _c("disco_jogo", "Disco giratório",
       {"Onde existe": "só no jogo"},
       "Na Arena é divertido, mas um disco giratório de verdade é perigoso.",
       "Não monte um disco giratório de verdade. Ele só existe no jogo.", comprar=False),
    _c("bobina_jogo", "Bobina de choque",
       {"Onde existe": "só no jogo"},
       "Na Arena ela solta faíscas, mas alta tensão de verdade machuca.",
       "Nunca mexa com alta tensão nem com tomada. A bobina só existe no jogo.", comprar=False),
    _c("enfeite", "Enfeite (faça você mesmo)",
       {"Material": "papelão, canudo, tampinha, fita colorida"},
       "Enfeites deixam o robô com a sua cara. Use material reciclável!", comprar=False),
]}

# Peça do jogo → componentes de verdade (com a quantidade por peça).
PECA_PARA_COMPONENTES: dict[str, tuple[tuple[str, float], ...]] = {
    **{p: (("chassi", 1),) for p in ("bloco_2x2", "bloco_2x4", "placa_4x6", "bloco_1x2", "viga_1x6", "placa_6x8", "blindagem")},
    "roda_pequena": (("roda_65", 1),),
    "roda_grande": (("roda_grande", 1),),
    "esteira": (("esteira_kit", 0.5),),            # um kit vem com o par
    "controlador": (("arduino_uno", 1), ("protoboard", 1)),
    "motor": (("motor_tt", 1),),
    "servo": (("sg90", 1),),
    "garra": (("garra_kit", 1), ("sg90", 1)),
    "sensor_distancia": (("hcsr04", 1),),
    "sensor_cor": (("tcs34725", 1),),
    "sensor_toque": (("microswitch", 1),),
    "giroscopio": (("mpu6050", 1),),
    "camera": (("esp32cam", 1),),
    "bateria": (("suporte_18650", 1),),
    "led": (("led_5mm", 1),),
    "helice": (("helice_motor", 1),),
    "disco": (("disco_jogo", 1),),
    "bobina": (("bobina_jogo", 1),),
    "antena": (("enfeite", 1),),
    "bandeira": (("enfeite", 1),),
}
UMA_POR_ROBO = {"chassi", "protoboard", "arduino_uno", "enfeite"}   # não importa quantas peças: compra 1


@dataclass(frozen=True)
class ItemDaLista:
    componente: ComponenteReal
    quantidade: int


def lista_de_materiais(robo: Iterable[PecaColocada]) -> tuple[list[ItemDaLista], list[str]]:
    """Soma as peças do robô e devolve (itens para comprar, avisos para a criança)."""
    soma: dict[str, float] = {}
    for c in robo:
        for comp, qtd in PECA_PARA_COMPONENTES.get(c.peca_id, ()):
            soma[comp] = soma.get(comp, 0) + qtd
    for comp in UMA_POR_ROBO & soma.keys():
        soma[comp] = 1
    motores = soma.get("motor_tt", 0)
    if motores:
        soma["l298n"] = math.ceil(motores / 2)    # cada L298N controla 2 motores
    avisos = []
    if soma and "arduino_uno" not in soma:
        avisos.append("Falta um controlador: sem o 'cérebro', nada funciona.")
    if (soma.get("roda_65") or soma.get("roda_grande")) and not motores:
        avisos.append("Na vida real, as rodas precisam de motores para girar.")
    if motores and "suporte_18650" not in soma:
        avisos.append("Motores gastam muita energia: coloque uma bateria extra no robô (ou use pilhas).")
    itens = [ItemDaLista(COMPONENTES[k], math.ceil(v)) for k, v in soma.items()]
    itens.sort(key=lambda i: (not i.componente.comprar, i.componente.nome))
    return itens, avisos


class LojasParceiras(Protocol):
    """PORTA: onde comprar cada componente (links de afiliado). Hoje: um arquivo de configuração."""

    def link(self, componente_id: str) -> dict[str, str] | None: ...
