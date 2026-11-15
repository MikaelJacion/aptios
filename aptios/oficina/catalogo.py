"""Os dados da oficina: peças, desafios e pacotes de tokens.

👉 MIKAEL: para criar uma peça nova, copie uma linha de Peca(...), troque
os valores e gere o modelo no Meshy. Salve o .glb em
aptios/interface/static/modelos/<id>.glb. Pronto!
"""
from aptios.oficina.dominio import Catalogo, Desafio, PacoteDeTokens, Peca

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
]

PACOTES = [
    PacoteDeTokens("p100", 100, 490),
    PacoteDeTokens("p250", 250, 990),
    PacoteDeTokens("p600", 600, 1990),
]

CATALOGO = Catalogo(
    pecas={p.id: p for p in PECAS},
    desafios={d.id: d for d in DESAFIOS},
)
