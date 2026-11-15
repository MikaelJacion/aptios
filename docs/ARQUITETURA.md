# Arquitetura da Aptios

## Dois contextos delimitados

A Aptios tem dois **contextos delimitados**: o **Tutor** e a **Oficina**. Cada um tem o próprio domínio e o próprio vocabulário. Um não importa nada do outro. Se o tutor mudar, a oficina continua funcionando.

Um exemplo do porquê: a palavra **"token"**. Na Oficina, é a moeda que a criança ganha. No mundo da IA, "token" é um pedaço de palavra. Se tudo estivesse misturado, essa palavra teria dois sentidos no mesmo código. Separando os contextos, cada palavra tem um sentido só dentro do seu contexto. Isso é a **Linguagem Ubíqua**.

## A Oficina

| Peça | Tipo no DDD | Por quê |
|---|---|---|
| `Explorador` | **Agregado** (raiz) | Saldo, peças, desafios e robô só mudam pelos métodos dele. Assim ninguém aumenta o saldo sem passar pelas regras. |
| `Peca`, `Desafio`, `PecaColocada` | **Value Objects** | Não mudam depois de criados. `PecaColocada` recusa giro de 45° e peça fora da bancada. |
| `Exploradores` | **Repositório** (porta) | Hoje é SQLite. Nos testes, fica em memória. |
| `Pagamentos` | **Porta** | Hoje é `PagamentoDesativado`. Amanhã pode ser o Mercado Pago, sem mexer no domínio. |
| `Oficina` | **Serviço de aplicação** | Todo caso de uso segue os mesmos passos: buscar o explorador, aplicar a regra e salvar. |

**Regra de ouro:** as respostas dos desafios **nunca** vão para o navegador (`catalogo_publico`). Quem confere a resposta é o servidor. Se fosse o navegador, qualquer criança poderia abrir o código da página e ver a resposta.

**A mesma porta com dois adaptadores, também no JavaScript:** a página da oficina tem `apiServidor()`, que fala com o Python, e `apiDemo()`, que roda tudo no navegador e serve só para a prévia. O resto da página não sabe qual dos dois está em uso.

# O Tutor

## A regra da dependência

```
interface  ──►  aplicacao  ──►  dominio  ◄──  infra
 (site)        (caso de uso)    (regras)      (Claude)
```

As setas mostram quem **conhece** quem. O **domínio fica no centro e não conhece ninguém**. A infra *implementa* a porta `Tutor` que o domínio define. Isso se chama **inversão de dependência**: o detalhe técnico depende da regra, nunca o contrário.

## As peças, com os nomes do DDD

| Peça | Tipo no DDD | Por quê |
|---|---|---|
| `Kit` | Enumeração do domínio | Só existem 4 kits. Um kit inventado, como `"minecraft"`, é recusado. |
| `Mensagem` | **Value Object** | É definida pelo valor (autor + texto) e não muda depois de criada (`frozen=True`). |
| `Conversa` | **Entidade** | Tem regras próprias: começa pelo estudante, os autores se revezam e o tutor lembra só as 20 últimas mensagens. |
| `Tutor` | **Porta** (interface) | Diz *o que* o domínio precisa ("responder a uma conversa"), sem dizer *como*. |
| `TutorClaude` | **Adaptador** | Encaixa o Claude na porta `Tutor`. |
| `TutorFalso` (testes) | Adaptador de teste | Prova as regras sem internet e sem custo. |
| `montar_conversa` / `perguntar` | **Serviço de aplicação** | Organiza o passo a passo do caso de uso. |

## Decisões (ADRs)

- **ADR-001: as conversas não ficam no servidor.** O público são crianças. Guardar o que elas escrevem exigiria cuidado com a LGPD e com o consentimento dos pais. O navegador manda o histórico a cada pergunta, e o domínio o valida de novo, porque **nunca confiamos no que vem de fora**.
- **ADR-002: respostas em streaming.** O texto aparece enquanto é escrito, então a criança não fica olhando uma tela parada.
- **ADR-003: limite de perguntas na interface.** É uma regra de custo e de abuso, não de robótica. Por isso fica fora do domínio.
- **ADR-004: o prompt fica num arquivo separado (`infra/prompt.py`).** Ele muda com frequência e não deve se misturar com o código que chama a API.

- **ADR-005: o código do explorador vai no cabeçalho `X-Explorador`.** Ele não vai no endereço, para não aparecer no histórico do navegador nem nos registros do servidor. Também não pedimos nome nem e-mail da criança.
- **ADR-006: a compra com dinheiro está desligada.** Para vender a menores, é preciso uma conta e autorização do responsável, a confirmação do pagamento por webhook e cumprir a LGPD e o ECA Digital. O domínio já tem `creditar_compra()`, e só falta o adaptador.

## Próximos passos sugeridos

1. **Foto do circuito:** a criança manda uma foto da montagem e o tutor ajuda a achar o erro. O Claude entende imagens.
2. **Contas de turma:** o professor cria uma turma e acompanha o uso. Isso exige guardar dados, então seria preciso revisar o ADR-001.
3. **Publicar na internet**, por exemplo no Render ou no Railway, com a chave guardada como variável de ambiente.
