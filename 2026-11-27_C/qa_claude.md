# QA-Claude ep014 C (panetone), 26/11/2026, revisor novo
Piso §3: qa_check aprovado (-15,1 LUFS); fatos.md com 2+ fontes por fato; nada da §1 (sem marca de panetone: só "PANETONE", rótulos inventados no mercado); §4 ok (sem "você sabia", interação nasce da história: come ou tira + marcar a tia).
Fatos: a fala não exagera ("prende a água/sobra menos", "levemente ácida", "mais lento", "às vezes conservante", "dura menos", "semanas"). Abri Stefanello 2019 (agris.fao.org: "became moldy faster" / "remained stable") e WebFoodCulture (artesanal "about one month", industrial com conservante 6-9 meses): conferem.
Continuidade: 5 caixas PANETONE na pilha (s1-4, completas a partir de ~2 s); "31 NOV" é o erro proposital, ok; Pipo espiga vira pipoca no estouro e segue pipoca até o fim.
Quadro 1 sem som: "5 PANETONES. NENHUM MOFA." + pilha + tia: afirmação curiosa legível, passa.
Fim na pergunta (come ou tira, s32-35) com split COME x TIRA. Story.jpg ok (ÁCIDA! + "come ou tira?"). Meta: hashtags no fim, crédito "Hartung, Wikimedia Commons, domínio público" bate com proveniencia.tsv (PD). Comentário fixado ok.
Gemini (média 8,0): sem erro grave; também achou o estouro de "ÁCIDA" alto/abrupto.

Correções:
1. s10,9-12,1 (O2 cena): a foto real do panetone entra em duotone "menta" (gen_cenas_O2.py, C4 estilo "duotone", paleta "menta") e com zoom de 1,3: a fatia fica verde-azulada e manchada, parece PÃO MOFADO num vídeo sobre mofo, e não se reconhece o panetone. Correção: tirar o duotone (foto nas cores naturais, ou duotone em paleta quente/creme) e reduzir o zoom (kb_de 1.0 -> kb_para 1.1) para o miolo com frutas aparecer.
2. s21,12-21,6 (O3 som): o estouro empilha 5 efeitos (hit_07 21,121, boom 21,141, pop2 21,141, vidro 21,171, items_01 21,301) EM CIMA da palavra "ácida" (21,14-21,59). Passa-alta 300 Hz: mix -18,6 dB contra -21 dB da voz sozinha; a palavra-gatilho some no celular. Correção: mover boom/pop2/vidro para 21,60 (logo depois de "ácida") e baixar o boom para 0,7; manter só o hit_07 antes, a 0,5.
3. Meta (O4): título "Panetone não mofa: o segredo é a massa ácida 🎄" afirma o absoluto que a fala evita ("mofo cresce bem mais lento"). Correção: "Por que o panetone demora tanto pra mofar? O segredo é a massa ácida 🎄" (e titulo_en "Why panettone takes so long to mold: the secret is acidic dough 🎄").
Fora do veredito: a tia está sentada atrás da pilha, não "carregando" como no roteiro; não atrapalha.

Veredito: CORRIGE

## Reconferência (26/11)
upload.mp4 novo (20:26): s11,5 a foto está em cores naturais, dá para ver o miolo dourado com frutas, sem cara de mofo; s21,8 o estouro da Pipo e o "ÁCIDA!" casam com a legenda "MASSA LEVEMENTE ÁCIDA". Áudio: aceito a medição do O4 (voz -17 dB contra efeitos -21,9 dB). Meta: título "Por que o panetone demora pra mofar? 🎄" (38 caracteres) já não exagera; titulo_en ajustado; hashtags no fim e crédito PD mantidos.
Veredito: APROVA
