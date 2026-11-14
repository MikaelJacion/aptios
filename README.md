# 🤖 RoboTutor

> Um tutor de robótica e programação com IA para crianças de 8 a 12 anos. Ensina **Scratch**, **LEGO SPIKE**, **LEGO EV3** e **Arduino** passo a passo, em português.

## ✨ O que ele faz

- O estudante escolhe o kit e conversa com o tutor.
- O tutor dá dicas antes da resposta pronta, para a criança pensar, e termina com um mini-desafio.
- Respostas curtas, em linguagem simples, com código comentado em português.
- **Regras de segurança** embutidas: nada de tomada, adulto junto com solda, ferramentas e baterias LiPo, e nenhum pedido de dados pessoais.
- **Privacidade:** as conversas ficam só no navegador. O servidor não guarda nada.
- **Limite de perguntas** por computador, porque cada resposta da IA custa dinheiro.

## 🚀 Como rodar

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # pegue em console.anthropic.com
venv/bin/uvicorn robotutor.interface.web:app --reload
```

Depois abra http://localhost:8000. Sem a chave, o site abre, mas o tutor avisa que não foi configurado.

**Testes**, sem internet e sem custo: `venv/bin/pytest`

## 🗂️ Arquitetura (DDD)

```
robotutor/
├── dominio/      # REGRAS: Kit, Mensagem, Conversa e a porta Tutor. Não depende de nada.
├── aplicacao/    # CASO DE USO: "o estudante faz uma pergunta"
├── infra/        # DETALHES TÉCNICOS: o Claude (tutor_claude.py) e as instruções (prompt.py)
└── interface/    # O SITE: FastAPI (web.py) + página do chat (static/index.html)
tests/            # Usam um TutorFalso, para provar as regras sem chamar a IA
```

Leia [docs/ARQUITETURA.md](docs/ARQUITETURA.md) para entender o porquê de cada camada.

## 🧠 IA

Usa o modelo `claude-opus-5-5` da Anthropic com `effort: "low"`, que deixa as respostas rápidas e mais baratas para chat. O fallback do servidor está ligado: se o modelo recusar uma resposta por segurança, a API tenta de novo com um modelo reserva.

Para mudar o jeito do tutor falar, edite só `robotutor/infra/prompt.py`.
