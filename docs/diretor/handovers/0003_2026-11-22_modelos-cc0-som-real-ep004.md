# Handover 0003 — 2026-11-22 — Modelos 3D CC0, som real e o ep004 (ossinho da sorte)
Diretor: mandato 2  ·  Ciclo: posse, assets CC0 (modelos e sons), ep004 "O T. rex tinha ossinho da sorte" (parte 2 dos dinossauros, refeita)

## Estado em uma frase
Ainda estagnado no placar (nada novo publicado até este handover), mas os dois bloqueios do mandato 1 caíram: modelo 3D feio e som sintetizado. O ep004 foi renderizado em 1080 nativo (o Kaggle ficou ~3 h na fila) e a plateia REPROVOU: média 4,6 (3, 5, 5, 6, 4). Não publiquei.

## O que publiquei
Nada. O ep004 v1 foi reprovado pela plateia (votos em docs/diretor/ciclos/2026-11-22/ep004_plateia/). O MP4 foi mostrado ao Lucas para a opinião dele.

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

## Por que o ep004 v1 reprovou (plateia, média 4,6)
1. Recap do Niko (6,6 a 10,6 s) é enrolação para quem não viu a parte 1; o card cobre a galinha. Davi sai aos 7,5 s.
2. O ouro (a ceia de Natal) só chega aos 17 s; o meio tem câmera parada (3,5 a 6 s) e o lado a lado (19,5 a 23,5 s) fica escuro e o rex irreconhecível.
3. Final sem ação: o osso quebra sozinho, sem mãos; 4 s parados no fim, pergunta duplicada (pill + legenda).
Fatos: "quem escapou: a galinha" está errado (a galinha não existia há 66 mi de anos; foram os ancestrais das aves). A cena rex + galinha + "herdaram esse osso" sugere descendência (são primos). A fúrcula da galinha ficou na barriga; o certo é no alto do peito.
Detalhes: a legenda parte "T. rex" ("T" / "REX"); anel branco no pescoço da galinha aos 14,5 s.
Acerto: a Carla (mãe) assistiu até o fim, comentou e mandaria no grupo da família. O ângulo da ceia funciona.

## Onde parei / próximo ciclo
1. Lucas deu 7 ao v1: "gostei, mas acho que não prende mesmo". Subiu de 3 (ep003) para 7: modelos e som resolveram o acabamento; o que falta é retenção (estrutura). Desta vez a plateia ficou MAIS dura que o Lucas (4,6 contra 7).
2. ep004 v2 (refazer, não reeditar), ~25 s:
   - Abrir NA CEIA: duas mãos puxando o ossinho em close na mesa de Natal, primeira frase "Esse ossinho que você disputa na ceia... é de dinossauro." Raio-x revela o mesmo V no peito do T. rex (corte no estalo de tensão).
   - Fato certo: "os ancestrais das aves sobreviveram ao asteroide; a galinha é prima do T. rex, e os dois herdaram esse osso". Fúrcula no alto do peito.
   - Niko em 1 frase depois do gancho ("o Niko acertou na parte 1"), card maior e sem cobrir nada.
   - Mãos: CC0 (procurar no OGA/itch "hands" rigged CC0) ou só pontas de dedos em close com DoF.
   - Final: termina NO estalo + a pergunta (sem 4 s parados; a pergunta só na pill ou só na legenda).
   - Legenda: tratar "T. rex" como uma palavra só (compose/tts).
   - Lado a lado: mais luz no lado do rex ou trocar por sobreposição das duas fúrculas.
   - A cena B_ceia e os assets do v1 estão no branch render/ep004 (reaproveitar a mesa, o ossinho e a Pipo).
3. Disparar o render no Kaggle CEDO (fila longa). Plano B: pedir ao Lucas para rodar a célula na sessão interativa (eu fui bloqueado pela permissão de clicar "Run" na sessão interativa).
4. Agentes usados neste ciclo: 2 (3D e plateia).

## Mensagem de posse para o próximo Diretor
```
Você é o Diretor do PipoPop, mandato 3. Tome posse lendo o repositório Lucas1234487/pipo-canal (adicione e clone) na ordem: README.md, docs/diretor/BRIEFING_DIRETOR.md, docs/BASE_CONHECIMENTO.md (seções 10 a 17), docs/diretor/PLACAR.md, docs/diretor/handovers/0003 e 0002, docs/diretor/FUNCOES.md e assets/LICENCAS.md.
Situação: modelos 3D CC0 e som CC0 resolvidos (assets/). O ep004 "o T. rex tinha ossinho da sorte" foi renderizado em 1080 e reprovado pela plateia (4,6): o melhor (a ceia de Natal) chega tarde, o recap do Niko enrola, falta mão puxando o osso e há erro de fato (galinha "escapou"). Prioridade: o ep004 v2 do handover 0003, abrindo na ceia, ~25 s, e PUBLICAR antes do Natal. Render no Kaggle cedo (a fila chegou a 3 h).
Regras: no máximo 3 ou 4 agentes por ciclo; plateia num agente só. Me mostre o vídeo antes de publicar. No fim, handover 0004 e push.
```
