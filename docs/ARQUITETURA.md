# Arquitetura do RoboTutor

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

## Próximos passos sugeridos

1. **Foto do circuito:** a criança manda uma foto da montagem e o tutor ajuda a achar o erro. O Claude entende imagens.
2. **Contas de turma:** o professor cria uma turma e acompanha o uso. Isso exige guardar dados, então seria preciso revisar o ADR-001.
3. **Publicar na internet**, por exemplo no Render ou no Railway, com a chave guardada como variável de ambiente.
