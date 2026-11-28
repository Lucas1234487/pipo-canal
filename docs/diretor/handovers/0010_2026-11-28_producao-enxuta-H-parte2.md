# Handover 0010 — produção diária 28/11 (modo enxuto), sessão das 15h20

**Estado em uma frase:**
Saiu 1 vídeo (ep015, H, série olhos pra frente parte 2, dinossauros) agendado para hoje 19h06 nas 3 redes + story; os outros pilares de 27/11 (M, H) e de 28/11 (C, M) não foram produzidos.

**O que aconteceu:**
- A trava das 09h25 (vigia) estava vencida e nada tinha sido produzido. Às 15h20 só o slot das 19h06 cabia (C 10h41 passou; M 15h52 sem tempo). Pedido do Lucas primeiro: a parte 2 da série (o H de 27/11 nunca saiu) foi para as 19h06.
- Gemini: 8,4 (2.5-flash; os outros modelos deram 429). Pronúncia: sem problema. QA-Claude: CORRIGE na 1ª passada (quadro 1 sem conflito legível, PARTE 2 encostando, carimbo REGRA minúsculo, Pipo cortada na borda) -> 1 rodada de correção -> reconferência do Diretor nos quadros em resolução cheia -> APROVA.
- Agendado: YouTube via Metricool (id 445754912), IG/FB Reel via Buffer, stories IG/FB 19h14 via Buffer. Sem Chrome (sessão na nuvem): comentários pendentes (29) e fixar comentário ficam para uma sessão com o PC.
- Motor novo: bicho.py ganhou tiranossauro e bicodepato (olhos lado/frente), cenário cretaceo, icones.py, correção do `espelha` no render2d (CENAS.md 4.6).
- Correções de código: tem_trabalho.py usava a ordem M,H,C nos slots (errado: 03_CICLO é C 1º, M 2º, H 3º) -> agora CMH, teste ajustado. Achado do QA-Claude repetido 2x (quadro 1 sem conflito: ep012 e ep015) virou checagem `quadro1` no guardrails.py (texto de 3+ palavras na tela até 0,3 s; exige cenas.json na pasta da fila) com 2 testes. 15 testes ok.

**CUSTO do dia:**
- Agentes: 1 web-fetch (modelo padrão, conferência de 5 fontes); 1 produtor Sonnet (3 rodadas no mesmo agente: produção, corte de duração pré-QA, correção pós-QA); 1 QA-Claude Sonnet (novo). Total 3 agentes, nunca em paralelo.
- Rodadas de correção: 1 pré-QA (duração 81 s -> 64 s, decisão do Diretor) + 1 pós-QA (4 achados do QA-Claude, todos visuais).
- Gemini: 2 chamadas de vídeo + 1 texto com busca (fora do limite do Claude).

**Pendências:**
- Parte 3 da série no H de 29/11 (dom 19h09); ligar ep015 como vídeo relacionado da parte 3 e o ep013 como relacionado do ep015 (precisa do Studio/Chrome).
- O ambiente da nuvem estava sem edge-tts e pycairo (o produtor instalou com pip): a produção da madrugada deve rodar o setup antes.
- Gemini: os modelos 3.x/4 deram 429 o dia todo; só o 2.5-flash respondeu. Se continuar, avaliar a chave/cota.
- Metricool grátis: +1 YouTube hoje.

**1 lição:**
Contar palavras antes de mandar o roteiro: 215 palavras na voz Antonio viraram 81 s. Para H, ~170 palavras com rate +10%.

## Rodada extra (disparo manual das 15h17, pedido do Lucas: vídeo hoje)
- O H (parte 2) já estava agendado às 19h06; não mexi. Produzi o C: ep016 "De onde vem a poeira que volta todo dia? 🧹" (aposta seguro, 33,8 s, voz Francisca), agendado às 21h13 (fora da tabela, horário pedido): YouTube Metricool 445781874, IG/FB Reel Buffer, stories 21h20.
- Fato: estudo Layton e Beamer (ES&T 2009): mais de 60% da poeira de casa vem de fora (modelo, casas do Meio-Oeste). O Gemini --busca afirmou o contrário sem fonte; descartado após abrir as páginas.
- Gemini 8,6 (pronúncia: falsos positivos de fonética normal). QA-Claude: CORRIGE (6 achados: quadro 1 sem poeira visível, estouro sob a voz, legenda na base da Pipo, MITO borrando, etiquetas sem contraste, fontes do mesmo comunicado) -> 1 rodada -> reconferência do Diretor -> APROVA com ressalva (poeira do quadro 1 ainda fraca; texto carrega o conflito). Pico 0,1 dBFS no upload: limitador aplicado pelo Diretor.
- "Quadro 1 fraco no desenho" REINCIDIU (ep012, ep015, ep016): lição no caderno do O2. "Pipo na borda/legenda" 2x (ep015, ep016) virou checagem no qa_check.py (Pipo cortada na borda; legenda cobrindo >35% do corpo) com 3 testes (18 ok).
- CUSTO da rodada: 1 produtor Sonnet novo (2 rodadas: produção + correção), 1 QA-Claude Sonnet novo, 1 retomada do web-fetch (fontes da poeira). Gemini: 1 texto com busca + 2 vídeos.
- Hoje no ar: 19h06 H parte 2 e 21h13 C poeira. M de 27 e 28/11 não saiu.
