# Como a Aptios está publicada

A Aptios roda no servidor `vps-claude` como **serviço do usuário** do systemd e aparece na internet pelo **Tailscale Funnel**, que cuida do HTTPS.

```
internet ──HTTPS──► Tailscale Funnel ──► 127.0.0.1:8770 (uvicorn) ──► aptios.db
```

| O quê | Onde |
|---|---|
| Serviço | `~/.config/systemd/user/aptios.service` (cópia em `deploy/aptios.service`) |
| Chave da IA e caminho do banco | `~/.config/aptios/env`, com permissão 600 e **fora do Git** |
| Banco da oficina | `~/.local/share/aptios/aptios.db` |

## Comandos do dia a dia

```bash
systemctl --user status aptios      # está rodando?
systemctl --user restart aptios     # depois de um git pull ou de trocar a chave
journalctl --user -u aptios -f      # ver os registros ao vivo
tailscale funnel status             # qual é o endereço público
```

## Atualizar o site depois de um push

```bash
cd ~/robotutor && git pull && venv/bin/pip install -r requirements.txt && systemctl --user restart aptios
```

## Por que `--proxy-headers`?

Pelo Funnel, todo pedido chega ao uvicorn vindo de `127.0.0.1`. Sem essa opção, o limite de perguntas acharia que todas as crianças são um computador só e bloquearia todo mundo junto. Com ela, o uvicorn lê o endereço verdadeiro no cabeçalho `X-Forwarded-For`, mas só confia nesse cabeçalho quando o pedido vem do próprio servidor (`--forwarded-allow-ips 127.0.0.1`).
