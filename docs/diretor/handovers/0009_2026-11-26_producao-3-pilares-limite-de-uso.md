# Handover 0009, 26/11/2026: produção diária (M, H, C) e o limite de uso
Diretor: produção diária das 03:37 (rodou até 20:30, com 3 paradas pelo limite de 5 h da conta)

## Estado em uma frase
Os 3 pilares saíram nas 3 redes, mas a estrutura completa (cerca de 25 agentes no dia) estourou o limite de uso 3 vezes. O Lucas recebeu a proposta do modo enxuto (DECISOES_LUCAS).

## O que saiu
| Pasta | ep | Tema | Horário | YouTube | IG/FB + story | Gemini | QA-Claude |
|---|---|---|---|---|---|---|---|
| 2026-11-26_M | ep012 | Black Friday: tira print do preço hoje (seguro, m_util_dica) | 26/11 18:33 | Metricool, V3MchhaJU0g (no ar) | Buffer (no ar) | 8,8 | CORRIGE -> APROVA |
| 2026-11-26_H | ep013 | Olhos pra frente, parte 1: o pombo (ousado, série) | 26/11 21:17 | Metricool 443744187 | Buffer | 9,2 | CORRIGE -> APROVA |
| 2026-11-27_C | ep014 | Por que o panetone demora pra mofar (evolução do ossinho) | 27/11 11:37 | Metricool 443758177 | Buffer | 8,0 | CORRIGE -> APROVA |

## O que os QAs apontaram e o que virou
- ep012: quadro 1 sem conflito visível sem som (cartão ganhou "AMANHÃ ELE VAI MENTIR"); plaquinha cobrindo a Pipo; comentário com "marca" no YouTube; o Gemini leu "DELESA" (pílula refeita em 3 linhas). Tudo corrigido.
- ep013: o ANTES x AGORA não mostrava a regra; pombo rosado; cachorro e coruja citados e não mostrados (o motor não tem: virou texto na tela, aceito); pombo da migalha com olho errado; gato parado no céu; crédito ampliado no mergulho. Tudo corrigido, menos o rosa de 3,03 a 3,55 s, que é o flash vermelho da reação boom (aceito: o motor não tem como desligar).
- ep013 (O4): o estouro não é o pico de amostra do mix, porque a voz chega a -0,9 dBFS. Aceito porque ele é o maior RMS fora da voz, que é o que se ouve.
- ep014: a foto em duotone menta parecia mofo (agora em cores naturais); o estouro cobria a palavra "ácida" (movido para 21,60); o título exagerava ("não mofa" -> "demora pra mofar"). Pronúncia: o Gemini achou a tônica de "panetone" um pouco plana. É leve, então não regravei; fica como lição do O1.

## Motor e processo
- kit2d ganhou o elemento "bicho" (6 espécies, olho lado/frente, 3 vistas, cone com zona cega), commit d6bd06c. Faltam cachorro e coruja, bicho atrás de vidro, pulo em arco, ícone de enviar e pílula de 2 linhas.
- kit/guardrails.py: o veredito do QA-Claude agora vale o ÚLTIMO do arquivo, sem diferenciar maiúsculas, e as notas "Nota de 0 a 10: X" são lidas. Isso resolve o falso bloqueio que o vigia das 20:23 apontou.
- Sons CC0 novos do Freesound em assets/sfx/olhos-cc0 com proveniência registrada.
- Openverse e Wikimedia deram limite diário. As fotos vieram do iNaturalist (CC0) e do Commons (PD), com proveniência.

## Limite de uso (o problema do dia)
- 03:38: o limite vinha da sessão de configuração da madrugada; voltou às 07:19. 08:00: 10 agentes em paralelo, cada um com 100 a 190 mil tokens, liberou às 12:10 (retomado 14:41). 15:40: caiu de novo, voltou às 19:40.
- Teste do dia: no ep014, O2, O3 e O4 rodaram no modelo leve (sonnet). Tiveram o mesmo número de apontamentos do QA que os outros (3) e gastaram menos.
- Proposta ao Lucas (modo enxuto A): gerente + O1 no modelo principal + 1 organizador de produção (O2+O3+O4) no modelo leve + QA-Claude + Gemini, com fichas curtas no lugar de 6 specs. Se ele não responder, a produção de 27/11 usa o A.

## Pendências
- Comentários do canal no IG e no FB (Buffer) em comentarios_pendentes.json, para quando o Chrome do Lucas estiver aberto.
- Série olhos pra frente: a parte 2 (dinossauros) é o H de 27/11; a parte 3 é o H de 28/11. O ep013 é o vídeo relacionado da parte 2.
- Metricool grátis: este mês foram usados 3 YouTube hoje, mais os anteriores. Estimativa de 10 a 13 usados de 20. Do dia 28 em diante, se acabar, o YouTube vai pelo Buffer (sem primeiro comentário).
- Métricas: Metricool sem dados por vídeo; o vigia gravou parciais do Buffer.

## 1 lição
Paralelismo grande queima o limite da conta e para o dia inteiro. Um vídeo por vez, com fichas curtas, entrega mais vídeos no fim do dia que 10 agentes ao mesmo tempo.
