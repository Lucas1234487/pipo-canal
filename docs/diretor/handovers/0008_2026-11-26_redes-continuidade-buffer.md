# Handover 0008 — 2026-11-26 — redes, continuidade e Buffer
Diretor: sessão com o Lucas (madrugada de 25 para 26/11)  ·  Ciclo: configuração, sem vídeo novo

## Estado em uma frase
Canal pronto para rodar sozinho nas 3 redes (YouTube, Instagram @pipo.pop88, página do Facebook PipoPop), catálogo completo sincronizado em 26/11.

## O que mudou (tudo no git)
- Instagram virou Criador; página do Facebook "PipoPop" criada e ligada; Metricool com YT+IG+FB; Buffer grátis com YT+IG+FB (kit/buffer.py, chave no Drive "PipoPop - segredos Buffer").
- Perfis padronizados nas 3 redes (avatar 2D, banner, capa, bios): docs/diretor/redes/perfis.md, assets/marca/.
- Specs novas: G7_redes (redes, stories, memes, comentários, voz), 04_MELHORA_CONTINUA, 05_CONTINUIDADE (cadeia Metricool -> Buffer -> Chrome; trava de produção), DECISOES_LUCAS.md, pedidos_lucas/ (palavra por palavra).
- kit/guardrails.py: portão determinístico antes de qualquer agendamento.
- Todo vídeo publicado fica no git (fila/ e fila/arquivo/); os 11 do YouTube estão lá.
- Tarefas: produção 03:37, vigia 09:23/15:23/20:23, semanal dom 21:47. As antigas foram apagadas.

## Pendências
- comentarios_pendentes.json: 20 primeiros comentários dos Reels de arquivo (Buffer não posta) para o próximo uso do Chrome.
- Metricool grátis: ~20 posts/mês por rede somada; os 10 rascunhos de arquivo no Metricool NÃO devem ser publicados (já saíram pelo Buffer).
- Série "olhos pra frente" (pedido do Lucas) na próxima H livre.

## Próximos passos
Produção de 26/11 (M e H) às 03:37; primeira semanal no formato novo em 29/11.

## Vigia 26/11 20:23
- Sync: 26_M/_H/_C na fila; trava de 15:24 apagada (produção concluída). Nada com erro no Buffer nem no Metricool nas últimas 24 h; 26_M no ar nas 3 redes; 26_H agendado para 21:17 (YT Metricool 443744187, IG/FB+stories Buffer).
- PORTÃO: guardrails.py dá BLOQUEADO no 26_H só por leitura: o regex do veredito exige "VEREDITO:" maiúsculo e o qa_claude.md usa "Veredito:" (o último é APROVA, reconferência das 20h); notas do Gemini no formato "Nota de 0 a 10: 9" também não são lidas (média real 9,2). O "O estourou" apontado pelo Gemini aos 0:42 é falso positivo: a legenda mostra "O ESTOURO ASSUSTOU" (conferi o quadro). Não mexi no portão nesta rodada (mudar regra de aprovação fica para a produção/semanal): corrigir o parser para pegar o ÚLTIMO veredito sem diferenciar maiúsculas e aceitar "Nota de 0 a 10: X".
- 26_H sai às 21:17 junto com 3 Reels de arquivo (presente_natal, ossinho, 25_H) no IG e no FB no mesmo minuto (o mesmo aconteceu às 18:33 com o 26_M). Comparar o alcance do 26_M/26_H com o de dias de 1 Reel só; se cair, espaçar o arquivo.
- Dados: dados/posts.jsonl criado (39 posts: YT, IG, FB de 12 vídeos). videos.jsonl com 26_M e 26_H. Métricas do YouTube por vídeo: Metricool ainda sem números; Buffer tem uma foto das 01:13 de 26/11, gravada como janela "parcial_Nh" (idade real), não como 24h/72h: 24_A 1260 views (38 h), 24_B 1152 (31 h), 25_C 1100 (13 h), 25_M 1138 (7 h), 25_H 871 (4 h). Nenhum vídeo 3x acima da média.
- Chrome indisponível nesta rodada (nuvem): 25 comentários pendentes (incluí 26_C no YouTube e 26_M/26_H no IG/FB); retenção e "Visualizado vs. Deslizado" seguem sem coleta.
