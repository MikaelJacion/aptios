# Links de afiliado na Oficina

Ideia do pai do Mikael: quando uma família quiser montar de verdade o robô que a
criança criou, a Aptios mostra onde comprar as peças. Se a compra for feita por
um link de afiliado, a Aptios recebe uma comissão, que ajuda a manter o projeto.

## Como já funciona

1. Cada peça do jogo tem uma **ficha técnica** do componente real (aba Peças e botão ⓘ na Loja).
2. Na aba **Robôs**, o botão **Ver lista de materiais** soma as peças do robô da bancada
   (por exemplo: 3 motores precisam de 2 drivers L298N) e mostra avisos de segurança.
3. A **Área do responsável** pede uma conta de multiplicar. Só depois aparecem os links,
   com o aviso de que são links de afiliado.
4. Sem links configurados, a área diz que ainda não há lojas parceiras.

## Como colocar os links

Crie o arquivo `~/.config/aptios/lojas.json` no servidor (fora do GitHub) e reinicie
o serviço (`systemctl --user restart aptios`). Só endereços `https://` são aceitos.

```json
{
  "hcsr04":      { "loja": "Nome da loja", "url": "https://..." },
  "arduino_uno": { "loja": "Nome da loja", "url": "https://..." }
}
```

Os nomes à esquerda são os `id` dos componentes em `aptios/oficina/componentes.py`
(por exemplo `arduino_uno`, `hcsr04`, `motor_tt`, `l298n`, `sg90`, `tcs34725`,
`mpu6050`, `esp32cam`, `suporte_18650`, `led_5mm`, `roda_65`, `esteira_kit`...).
Peças "só no jogo" (disco giratório e bobina de choque) nunca recebem link.

## Antes de ligar: lista para o adulto conferir

- [ ] Ler as regras do programa de afiliados escolhido. Alguns programas proíbem
      sites voltados para crianças ou pedem cuidados especiais.
- [ ] Publicidade dirigida a crianças tem regras próprias no Brasil (por exemplo,
      a Resolução 163/2014 do CONANDA e o ECA Digital, Lei 15.211/2025). Por isso
      os links ficam atrás da Área do responsável e nunca aparecem para a criança.
      Vale confirmar com alguém da área jurídica.
- [ ] Manter o aviso de transparência ("links de afiliado") visível junto dos links.
- [ ] Componentes com bateria de lítio ou ferramentas: manter o aviso de que um
      adulto deve acompanhar.
