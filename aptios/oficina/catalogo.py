"""Os dados da oficina: peças, desafios e pacotes de tokens.

👉 MIKAEL: para criar uma peça nova, copie uma linha de Peca(...), troque
os valores e gere o modelo no Meshy. Salve o .glb em
aptios/interface/static/modelos/<id>.glb. Pronto!
"""
from aptios.oficina.batalha import Rival
from aptios.oficina.dominio import Catalogo, Desafio, PacoteDeTokens, Peca, PecaColocada

PECAS = [
    # ── de presente (preço 0) ──
    Peca("bloco_2x2", "Bloco 2×2", "estrutura", 0, "#e5484d", (2, 1, 2), "O bloco básico de qualquer robô."),
    Peca("bloco_2x4", "Bloco 2×4", "estrutura", 0, "#3e63dd", (2, 1, 4), "Bloco comprido para fazer o corpo."),
    Peca("placa_4x6", "Placa 4×6", "estrutura", 0, "#8d8d86", (4, 1, 6), "Chassi: a base onde tudo se encaixa."),
    Peca("roda_pequena", "Roda pequena", "roda", 0, "#2b2b2b", (1, 2, 2), "Roda simples para os primeiros carrinhos."),
    Peca("controlador", "Controlador", "controlador", 0, "#f5d90a", (2, 2, 3), "O cérebro do robô. Lê os sensores e liga os motores."),
    # ── da loja ──
    Peca("bloco_1x2", "Bloco 1×2", "estrutura", 10, "#30a46c", (1, 1, 2), "Pecinha para detalhes e acabamento."),
    Peca("viga_1x6", "Viga 1×6", "estrutura", 15, "#f76b15", (1, 1, 6), "Viga longa: deixa o robô mais firme."),
    Peca("roda_grande", "Roda grande", "roda", 25, "#2b2b2b", (1, 3, 3), "Anda mais rápido e passa por cima de obstáculos."),
    Peca("esteira", "Esteira", "roda", 40, "#3a3a3a", (1, 2, 6), "Igual a de um trator: anda em qualquer terreno."),
    Peca("motor", "Motor", "motor", 30, "#6f6e77", (2, 2, 2), "Gira as rodas. Sem motor, o robô não sai do lugar!"),
    Peca("servo", "Servo motor", "motor", 35, "#4c5155", (1, 2, 2), "Motor que vira até um ângulo exato. Ótimo para braços."),
    Peca("sensor_distancia", "Sensor de distância", "sensor", 30, "#0090ff", (2, 1, 1), "Mede a distância com som, como um morcego."),
    Peca("sensor_cor", "Sensor de cor", "sensor", 30, "#8e4ec6", (1, 1, 1), "Enxerga cores. Serve para seguir linhas no chão."),
    Peca("sensor_toque", "Sensor de toque", "sensor", 20, "#d6409f", (1, 1, 1), "Um botão: avisa quando o robô bate em algo."),
    Peca("garra", "Garra", "motor", 45, "#ffc53d", (2, 2, 2), "Pega e solta objetos."),
    Peca("led", "LED", "enfeite", 10, "#ff4d4f", (1, 1, 1), "Luzinha para o robô dar sinais."),
    Peca("antena", "Antena", "enfeite", 15, "#bdbdbd", (1, 3, 1), "Deixa o robô com cara de robô de verdade."),
]

DESAFIOS = [
    Desafio("scratch_1", "scratch", "Começando no Scratch",
            "Qual bloco faz o programa começar quando você clica na bandeira verde?",
            ("mova 10 passos", "quando 🏳️ for clicado", "sempre", "diga Olá!"), 1, 10,
            "Os blocos de Eventos, os amarelos, são os que dão a largada no programa."),
    Desafio("scratch_2", "scratch", "Repetir para sempre",
            "Você quer que o gato ande sem parar. Qual bloco você usa?",
            ("se então", "espere 1 segundo", "sempre", "pare tudo"), 2, 15,
            "O bloco 'sempre' repete o que está dentro dele até o programa parar."),
    Desafio("scratch_3", "scratch", "Tomando decisões",
            "Para o personagem pular SÓ quando a seta for apertada, você usa…",
            ("se <tecla seta pressionada?> então", "sempre", "mova 10 passos", "mude a cor"), 0, 20,
            "O 'se… então' é uma decisão: só faz a ação quando a condição é verdadeira."),
    Desafio("spike_1", "lego_spike", "Portas do hub",
            "No LEGO SPIKE, as portas do hub onde ligamos motores e sensores têm nomes de…",
            ("1 a 6", "A a F", "vermelho a azul", "X, Y e Z"), 1, 10,
            "As portas vão de A até F. Você precisa saber em qual porta cada peça está."),
    Desafio("spike_2", "lego_spike", "Seguidor de linha",
            "Qual sensor ajuda o robô a seguir uma linha preta no chão?",
            ("Sensor de força", "Sensor de cor", "Sensor de distância", "Nenhum"), 1, 20,
            "O sensor de cor percebe a diferença entre a linha preta e o chão claro."),
    Desafio("ev3_1", "lego_ev3", "Desviando de obstáculos",
            "Que sensor do EV3 mede a distância até uma parede?",
            ("Toque", "Ultrassônico", "Giroscópio", "Cor"), 1, 15,
            "O ultrassônico manda um som e mede quanto tempo o eco demora para voltar."),
    Desafio("ev3_2", "lego_ev3", "Girando certinho",
            "Qual sensor ajuda o robô a virar exatamente 90 graus?",
            ("Giroscópio", "Toque", "Cor", "Microfone"), 0, 20,
            "O giroscópio mede quanto o robô girou."),
    Desafio("arduino_1", "arduino", "O primeiro programa",
            "No Arduino, qual função roda sem parar, repetindo para sempre?",
            ("setup()", "loop()", "start()", "repeat()"), 1, 10,
            "setup() roda uma vez no começo. loop() repete para sempre."),
    Desafio("arduino_2", "arduino", "Protegendo o LED",
            "Para o LED não queimar, colocamos junto com ele um…",
            ("Resistor", "Motor", "Sensor", "Ímã"), 0, 15,
            "O resistor (por exemplo, de 220 Ω) limita a corrente que passa pelo LED."),
    Desafio("arduino_3", "arduino", "Segurança em primeiro lugar",
            "Onde é SEGURO ligar o seu Arduino?",
            ("Na tomada da parede", "Na porta USB do computador", "No chuveiro", "Em qualquer fio"), 1, 25,
            "Use só a porta USB ou pilhas. A tomada da parede é perigosa: nunca!"),
    Desafio("robo_1", "robotica", "Partes do robô",
            "Num robô, qual peça funciona como o 'cérebro'?",
            ("A roda", "O controlador", "A antena", "O LED"), 1, 10,
            "O controlador lê os sensores, decide o que fazer e manda os motores agirem."),
    Desafio("robo_2", "robotica", "Sentidos do robô",
            "Os sensores servem para o robô…",
            ("Andar mais rápido", "Perceber o mundo ao redor", "Ficar mais bonito", "Gastar bateria"), 1, 10,
            "Sensores são como os olhos, os ouvidos e o tato do robô."),

    # ── MÉDIOS (30 tokens) ──
    Desafio("scratch_m", "scratch", "Contando pontos",
            "A variável 'pontos' começa em 0. O script faz: repita 5 vezes → adicione 2 a pontos. Quanto vale 'pontos' no fim?",
            ("5", "7", "10", "2"), 2, 30,
            "Cada volta soma 2. São 5 voltas: 2 + 2 + 2 + 2 + 2 = 10.", "medio"),
    Desafio("spike_m", "lego_spike", "Parando na parede",
            "O robô deve andar e parar a 10 cm de uma parede. Qual é a melhor ideia?",
            ("Sensor de cor e esperar ver vermelho", "Sensor de distância e esperar até a distância ser menor que 10 cm",
             "Girar o motor 10 vezes e torcer", "Sensor de força apertado"), 1, 30,
            "O sensor de distância mede quanto falta até a parede. Quando ficar menor que 10 cm, desligue os motores.", "medio"),
    Desafio("ev3_m", "lego_ev3", "Matemática das rodas",
            "Uma volta da roda anda 18 cm. Quantas rotações o motor precisa dar para o robô andar 54 cm?",
            ("2", "3", "6", "9"), 1, 30,
            "54 ÷ 18 = 3. Uma rotação do motor é uma volta inteira da roda.", "medio"),
    Desafio("arduino_m", "arduino", "Esperando um pouco",
            "O que o comando delay(1000) faz no Arduino?",
            ("Espera 1 segundo", "Espera 1000 segundos", "Liga o pino 1000", "Repete 1000 vezes"), 0, 30,
            "O delay conta em milissegundos. 1000 milissegundos = 1 segundo.", "medio"),
    Desafio("robo_m", "robotica", "O ciclo do robô",
            "Todo robô repete três passos sem parar. Quais são?",
            ("Sentir → Pensar → Agir", "Ligar → Desligar → Ligar", "Pintar → Montar → Vender", "Andar → Pular → Voar"), 0, 30,
            "O robô SENTE com os sensores, PENSA no controlador e AGE com os motores. E repete!", "medio"),

    # ── DIFÍCEIS (50 tokens) ──
    Desafio("scratch_d", "scratch", "Atores que conversam",
            "Qual bloco faz um ator AVISAR os outros que algo aconteceu, para eles reagirem?",
            ("transmita [mensagem]", "mova (10) passos", "diga [Olá!]", "mude para o traje"), 0, 50,
            "'Transmita' manda um recado para todos. Quem tem o bloco 'quando eu receber' começa a agir.", "dificil"),
    Desafio("spike_d", "lego_spike", "Seguidor de linha esperto",
            "No seguidor de linha com 1 sensor: quando vê PRETO, o robô vira para a esquerda. Quando vê BRANCO, ele deve…",
            ("Parar", "Virar para a direita", "Ir reto para sempre", "Dar ré"), 1, 50,
            "Ele vai em zigue-zague pela beirada da linha: no preto vira para um lado, no branco vira para o outro.", "dificil"),
    Desafio("ev3_d", "lego_ev3", "Girando no lugar",
            "Para o robô girar no mesmo lugar, sem sair do ponto, as duas rodas devem girar…",
            ("Na mesma direção", "Em direções opostas", "Só uma, a outra parada", "As duas paradas"), 1, 50,
            "Uma roda para frente e a outra para trás: o robô gira em volta do próprio centro.", "dificil"),
    Desafio("arduino_d", "arduino", "Lendo um botão",
            "Para saber se um botão ligado no pino 2 está apertado, usamos…",
            ("digitalWrite(2, HIGH)", "digitalRead(2)", "analogWrite(2, 255)", "pinMode(2, OUTPUT)"), 1, 50,
            "digitalRead(2) devolve HIGH ou LOW. Antes, no setup, use pinMode(2, INPUT_PULLUP).", "dificil"),
    Desafio("robo_d", "robotica", "Rodas grandes",
            "Por que um robô com rodas MAIORES anda mais longe a cada volta do motor?",
            ("Porque é mais pesado", "Porque a roda maior tem uma volta (circunferência) maior",
             "Porque a bateria é maior", "Ele não anda mais longe"), 1, 50,
            "A cada volta, a roda anda o tamanho da sua circunferência. Roda maior = volta maior = mais longe!", "dificil"),
]

PACOTES = [
    PacoteDeTokens("p100", 100, 490),
    PacoteDeTokens("p250", 250, 990),
    PacoteDeTokens("p600", 600, 1990),
]

def _robo(*pecas: tuple) -> tuple[PecaColocada, ...]:
    return tuple(PecaColocada(*p) for p in pecas)


# Rivais da Arena. Cada um paga o prêmio só na primeira vitória.
RIVAIS = [
    Rival("lata_velha", "Lata Velha", "facil", 20, "Um carrinho simples. Ótimo para treinar!", _robo(
        ("placa_4x6", -2, 0, -3, 0), ("controlador", -1, 1, -2, 0),
        ("roda_pequena", -3, 0, -3, 0), ("roda_pequena", 2, 0, -3, 0),
        ("roda_pequena", -3, 0, 1, 0), ("roda_pequena", 2, 0, 1, 0))),
    Rival("trator_bravo", "Trator Bravo", "medio", 40, "Esteiras e muita vida. Difícil de derrubar.", _robo(
        ("placa_4x6", -2, 0, -3, 0), ("esteira", -3, 0, -3, 0), ("esteira", 2, 0, -3, 0),
        ("controlador", -1, 1, -3, 0), ("motor", -2, 1, 0, 0), ("motor", 0, 1, 0, 0),
        ("bloco_2x4", -2, 3, -1, 0), ("bloco_2x4", 0, 3, -1, 0), ("garra", -1, 1, 2, 0))),
    Rival("mega_garra", "Mega Garra", "dificil", 80, "Rápido, mira certeira e duas garras. O chefão da Arena!", _robo(
        ("placa_4x6", -2, 0, -3, 0),
        ("roda_grande", -3, 0, -3, 0), ("roda_grande", 2, 0, -3, 0), ("roda_grande", -3, 0, 0, 0), ("roda_grande", 2, 0, 0, 0),
        ("controlador", -1, 1, -3, 0), ("motor", -2, 1, 0, 0), ("motor", 0, 1, 0, 0), ("motor", -1, 3, -3, 0),
        ("garra", -2, 1, 2, 0), ("garra", 0, 1, 2, 0), ("servo", -2, 1, -3, 0),
        ("sensor_distancia", -1, 1, -4, 0), ("sensor_cor", 1, 1, -3, 0),
        ("bloco_2x4", -2, 3, -1, 0), ("bloco_2x4", 0, 3, -1, 0), ("bloco_2x2", -1, 5, -3, 0))),
]

CATALOGO = Catalogo(
    pecas={p.id: p for p in PECAS},
    desafios={d.id: d for d in DESAFIOS},
)
