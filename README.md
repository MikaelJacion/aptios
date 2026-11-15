# 🤖 Aptios

> Plataforma para crianças de 8 a 12 anos aprenderem robótica e programação. Tem um **tutor com IA** e uma **oficina 3D** para montar robôs.

| | O que é | Endereço |
|---|---|---|
| 🤖 **Tutor** | Chat com IA que ensina **Scratch**, **LEGO SPIKE**, **LEGO EV3** e **Arduino** passo a passo, em português | `/` |
| 🧱 **Oficina 3D** | Bancada 3D para montar robôs com peças. Os tokens vêm dos desafios e compram peças novas na loja. | `/oficina` |

## ✨ Destaques

- **Tutor:** dá dicas antes da resposta pronta, sugere mini-desafios e segue regras de segurança (nada de tomada; adulto junto com solda, ferramentas e baterias LiPo). As conversas ficam só no navegador.
- **Oficina:** 17 peças (estrutura, rodas, motores, sensores, controlador e enfeites) e 12 desafios em 5 trilhas. As peças se encaixam numa grade de pinos e giram de 90 em 90 graus, e o robô é salvo automaticamente.
- **Modelos 3D do Meshy:** exporte em `.glb` e salve em `aptios/interface/static/modelos/<id da peça>.glb`. Sem o arquivo, a oficina desenha uma forma simples no lugar.
- **Tokens:** cada desafio paga uma vez só. A **compra com dinheiro** já tem estrutura pronta, mas está **desligada** até existir login de responsável e um provedor de pagamento. Veja `PagamentoDesativado` em `aptios/oficina/infra.py`.

## 🚀 Como rodar

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # só o tutor precisa da chave
venv/bin/uvicorn aptios.interface.web:app --reload
```

Depois abra http://localhost:8000 para o tutor ou http://localhost:8000/oficina para a oficina. Os dados da oficina ficam no arquivo `aptios.db`, que você pode trocar pela variável `APTIOS_DB`.

- **Testes**, sem internet e sem custo: `venv/bin/pytest`
- **Prévia sem servidor**, em modo demonstração: `venv/bin/python ferramentas/gerar_previa.py previa.html`

## 🗂️ Arquitetura (DDD)

```
aptios/
├── tutor/            # CONTEXTO "Tutor"
│   ├── dominio.py    #   Kit, Mensagem, Conversa e a porta Tutor
│   ├── aplicacao.py  #   caso de uso: perguntar
│   ├── prompt.py     #   as instruções do tutor
│   └── claude.py     #   adaptador: o Claude responde
├── oficina/          # CONTEXTO "Oficina"
│   ├── dominio.py    #   Peca, Desafio, Explorador (agregado), PecaColocada e as portas
│   ├── catalogo.py   #   peças, desafios e pacotes
│   ├── aplicacao.py  #   casos de uso: desafio, comprar, montar...
│   └── infra.py      #   SQLite e pagamento (desativado)
└── interface/        # O SITE: FastAPI + páginas em static/
```

Leia [docs/ARQUITETURA.md](docs/ARQUITETURA.md) para entender o porquê de cada peça.
