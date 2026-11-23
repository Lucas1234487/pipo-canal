# Handover 0004 — 2026-11-23 — ep004 v2 renderizado e reprovado; comparativo Claude x Gemini
Diretor: mandato 3  ·  Ciclo: posse, ep004 v2 (roteiro, voz, cena, render, plateia), comparativo Claude x Gemini pedido pelo Lucas

## Estado em uma frase
Ainda estagnado: nada novo publicado. O ep004 v2 (23 s, abrindo na ceia) foi renderizado em 1080 no Kaggle e a plateia deu 4,6, a mesma nota do v1. O Lucas recebeu o MP4 e ainda não deu a nota dele.

## O que publiquei
Nada.

## O que fiz
1. Roteiro e voz do v2 (eu, sem agente): 9 frases, Antonio +12%, 22,3 s. kit/tts.py ganhou "trim" (corta o silêncio do fim das frases: 28 s viraram 22 s com o mesmo texto).
2. Cena 3D do v2 (1 agente, ~16 min, QA zero): ceia com mãos CC0 (assets/modelos/maos_arms_lowpoly), cinzas com o V no alto do peito, quintal com a galinha e o card do Niko sem número, tela dividida rex x galinha, estalo e pop da Pipo no quadro 575. Eu corrigi depois: mãos saindo do quadro no estalo, mão cortada no final, enquadramento da galinha (3 rodadas de QA). Branch render/ep004v2; quadros em render-out/ep004v2-c00..c02.
3. Render no Kaggle (Save Version "ep004v2 render 1080", T4 x2, sem fila segunda 08h20): ~55 min para 690 quadros. Montagem com som (events.json = cena + som.json) e qa_check aprovado.
4. Bug achado: o .gitignore "sfx/" escondia assets/sfx. Os efeitos CC0 nunca tinham ido ao repo. Corrigido e rebaixados com a licença conferida.
5. Comparativo Claude x Gemini pedido pelo Lucas: https://claude.ai/artifact/HAFoUh55EYpedP8JM9diKA (empate em roteiro e 3D; o Gemini ganha em ouvir áudio e assistir vídeo).
6. v1 remontado com som (docs: ep004_v1_teste_gemini.mp4 foi enviado ao Lucas) para ele testar o Gemini como Plateia no celular. Resposta ainda não veio.

## Por que o v2 reprovou (plateia, 4,6; votos em docs/diretor/ciclos/2026-11-23/ep004v2_plateia.md)
1. 0 a 2,5 s: o primeiro quadro é bonito, mas não tem ameaça. Mãos e osso com coração lento parecem "fio de queijo". O dinossauro só chega aos 2,5 s. "Ceia" em novembro não pega, e o vídeo nunca diz "ossinho da sorte" (o nome que todo mundo conhece). Davi sai aos 2 s.
2. 11 a 15,4 s: repete a ideia do segundo 3. A sobreposição dos dois V vira uma linha borrada. Renata sai aos 14 s.
3. Final morno: ninguém "ganha" de forma engraçada; o último segundo está quase em silêncio.
Fatos: a fúrcula do T. rex é larga, em forma de bumerangue (não um V fino igual ao da galinha): "um igual" exagera. "Prima" é melhor como "parente distante" (os dois são terópodes celurossauros; as aves vêm dos maniraptores).
Acerto: Júlio e Carla ficaram até o fim e comentaram; a Carla mandaria no grupo da família em dezembro. O ângulo da ceia ainda é o melhor ativo, mas o vídeo cai bem no Natal, não em novembro.

## Decisões que tomei e por quê
- Não publicar. Padrão 10.
- Não renderizar na CPU: 9,7 h. Kaggle é o caminho.
- Parei de usar o Chrome a pedido do Lucas (é o PC da EMS e ele bloqueia sites de IA). Registrado na BASE seção 18.
- Agentes no ciclo: 3 (3D parado pelo Lucas, 3D, plateia). Dentro do limite.

## O que falhou e de quem foi a culpa
- Minha: aceitei abrir com as mãos sem nada grande no quadro. O handover 0003 pediu "abrir na ceia", e eu segui sem perguntar o que faz alguém parar o dedo em 1 s. A ceia é identificação, não ameaça. Devia ter posto o rex (ou o rugido e a sombra dele) no quadro 1 junto com o osso.
- Minha: "um igual" foi escrito por mim, sem checar a forma da fúrcula do T. rex.

## Onde parei / próximo ciclo
1. Esperar a nota do Lucas no v2 e a resposta do Gemini ao v1. Comparar: se o Gemini acertar a nota do Lucas melhor que a nossa plateia, propor o Gemini como Plateia (chave de API = decisão dele).
2. ep004 v3, só se valer a pena, ~20 s, para publicar perto do Natal (de 15 a 24/12):
   - Quadro 1: o T. rex enorme atrás da mesa da ceia (ou a sombra dele cobrindo a mesa) e as mãos puxando o osso; frase "Esse ossinho da sorte que você disputa no Natal... vem dos dinossauros."
   - Fúrcula do rex larga (bumerangue), a da galinha em V: "o T. rex também tinha uma, só que gigante".
   - "Parente distante", não "prima". Cortar a sobreposição dos V.
   - Final com recompensa (quem ficou com o pedaço maior + piada) e som até o último quadro.
   - A cena do v2 está em render/ep004v2 (ep.py, maos.py, blends): é só mexer nos planos.
3. Considerar um vídeo novo e curto que não dependa do Natal para publicar ainda em novembro (o canal está parado há 2 dias).

## Mensagem de posse para o próximo Diretor
```
Você é o Diretor do PipoPop, mandato 4. Tome posse lendo o repositório Lucas1234487/pipo-canal (adicione e clone) na ordem: README.md, docs/diretor/BRIEFING_DIRETOR.md, docs/BASE_CONHECIMENTO.md (seções 14 a 18), docs/diretor/PLACAR.md, docs/diretor/handovers/0004 e 0003, docs/diretor/FUNCOES.md e assets/LICENCAS.md.
Situação: o ep004 v2 (23 s, abrindo na ceia) foi renderizado e a plateia deu 4,6. O gancho não tem ameaça no quadro 1 e há dois exageros de fato (fúrcula "igual" e "prima"). Não use o Chrome do PC da EMS. Decida, com a minha nota do v2 e o teste do Gemini, entre o ep004 v3 para o Natal ou um vídeo novo para já.
Regras: no máximo 3 ou 4 agentes por ciclo; plateia num agente só. Me mostre o vídeo antes de publicar. No fim, handover 0005 e push.
```
