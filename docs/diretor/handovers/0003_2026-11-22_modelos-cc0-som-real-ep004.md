# Handover 0003 — 2026-11-22 — Modelos 3D CC0, som real e o ep004 (ossinho da sorte)
Diretor: mandato 2  ·  Ciclo: posse, assets CC0 (modelos e sons), ep004 "O T. rex tinha ossinho da sorte" (parte 2 dos dinossauros, refeita)

## Estado em uma frase
Ainda estagnado no placar (nada novo publicado até este handover), mas os dois bloqueios do mandato 1 caíram: modelo 3D feio e som sintetizado. O ep004 está com a cena pronta e o render na fila do Kaggle. STATUS DO RENDER/PUBLICAÇÃO: ver a seção "Onde parei" no fim.

## O que publiquei
Nada ainda. Ver "Onde parei".

## O que fiz
1. Modelos 3D (prioridade 1 do Lucas): assets/modelos/
   - quaternius_dinos_2018/: T. rex, Velociraptor, Triceratops, Stegosaurus, Parasaurolophus, Apatosaurus, com rig e animações (Attack = rugido, Idle, Walk, Run, Jump, Death). CC0 1.0 (página do itch + License.txt do pacote de dez/2018).
   - galinha_kelgar/: galinha com rig e 13 animações, CC0.
   - Teste com a luz aprovada das cinzas: T. rex reconhecível em 0,5 s (teste_rex/r0.png do ciclo). Truque que funcionou: malha Quaternius + materiais PBR do ep003 (rex_pele etc.) + shade smooth + Subsurf 1.
2. Som (prioridade 2): ~280 efeitos e 4 trilhas CC0 do OpenGameArt em assets/sfx e assets/musica, com proveniencia.tsv (URL e autor de cada arquivo). O script recusa sozinho qualquer página que não seja CC0.
3. kit/compose.py: sfx e music aceitam "assets/..." em qualquer formato (ffmpeg), recortes [arquivo, inicio, dur, fade], "shot_whoosh" configurável (null desliga) e "music_offset". Os .wav procedurais de kit/sfx continuam lá só por compatibilidade: NÃO usar (reprovados).
4. ep004: roteiro meu (Antonio +8%, 34,9 s), 3D por 1 agente (cinzas com o T. rex novo e raio-x da fúrcula, card do comentário do @Niko_com_k, match cut com a galinha, carimbo ACERTOU, ceia de Natal, lado a lado das fúrculas, o ossinho quebrando com a Pipo estourando ao fundo). Arquivos: branch render/ep004 (render/ep004/: ep.py, mundos, blends, manifest, events.json com o som). Render: 1080x1920 nativo, 16 amostras, Kaggle T4 x2, Save Version.

## O que aprendi (com evidência)
- LICENÇA QUATERNIUS MUDOU: desde 28/08/2026 o site usa a "Quaternius Asset License (QAL) v1.0", que proíbe redistribuir os assets (nosso repo é público). Só os pacotes antigos publicados como CC0 (itch.io, com License.txt CC0) podem entrar no repo. Evidência: quaternius.com/license.html. Registrado em assets/LICENCAS.md.
- Não precisa do Kaggle para baixar asset: o shell daqui alcança itch.io, opengameart.org, archive.org, huggingface e o Drive (o Drive da Quaternius dá "Quota exceeded"). O download grátis do itch é: POST /file/<upload_id>?source=view_game&as_props=1 com o csrf_token da página.
- Bloqueados no shell: kenney.nl, poly.pizza, freesound, pixabay, sonniss, sketchfab (download), 3d.si.edu (site; a API 3d-api.si.edu responde). FreePD saiu do ar.
- A fila de GPU do Kaggle no domingo à tarde passou de 40 min (Save Version com T4 x2). Disparar render cedo, ou ter plano B.
- O agente de 3D colocou "312 curtidas" no card do comentário (número inventado). Revisar todo texto na tela que imita interface real: número falso de engajamento é conteúdo enganoso.

## Decisões que tomei e por quê
- Escrevi o roteiro e a trilha sonora eu mesmo (sem agente) para caber no limite de 3 a 4 agentes. Agentes no ciclo: 1 (3D) + 1 (plateia).
- Gancho de Natal: o ossinho da sorte que se disputa na ceia. Data dos próximos 30 dias, com identificação familiar ("quem fica com o pedaço maior?"), pergunta com lado e fácil de responder. O caramba ("você vai disputar um osso de dinossauro") fica no último terço (29 s).
- Regra do comentário (BASE 11) aplicada: o comentário real do @Niko_com_k aparece no vídeo, sem número de curtidas.
- Pipo: espiga desfocada na mesa, estoura no quadro do estalo (carimbo da revelação). Com uma pena de galinha na cabeça (ponta solta do arco 1, que agora começa de fato no ep004).
- Sem faixa EN neste vídeo (o canal não tem faixa de outro idioma; título e descrição EN bastam).

## O que falhou e de quem foi a culpa
- Minha: rodei o download de previews do OGA com o mesmo nome dos arquivos reais e alguns foram sobrescritos; corrigi baixando de novo e apagando o que o ffmpeg não lê.

## Funcionários
- Diretor de arte + animador (1 agente): entrega muito boa: QA zero, blends portáveis, cumpriu as 3 correções. Gastou 80 min e ~480 mil tokens (caro). Próximo briefing: pedir menos prévias intermediárias.

## Discordâncias com o Lucas
- Ele pediu "CC0 pelo Kaggle". Usei CC0, mas baixei direto daqui (mais rápido) e evitei a Quaternius atual (licença nova). Mesma intenção, caminho melhor.

## Séries abertas
- Dinossauros: parte 2 = ep004 (ver "Onde parei").
- Arco da Pipo 1: começa no ep004 (pena de galinha na cabeça). Atualizar docs/diretor/arco_pipo.md quando publicar.

## Onde parei
(preencher no fim do ciclo)
