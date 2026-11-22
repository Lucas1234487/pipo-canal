# Handover 0002 — 2026-11-22 — Parte 2 dos dinossauros reprovada; pipeline de GPU pronto
Diretor: mandato 1  ·  Ciclo: posse, placar real, metadados dos 4 Shorts, render na GPU do Kaggle e o ep003 (não publicado)

## Estado em uma frase
Estagnado: 4 Shorts, ~3.100 views, 1,3% de curtida, 70% desliza antes de assistir (meta: 3% e 30%). Não publiquei nada novo: o ep003 tirou 3 do Lucas e entre 3 e 6 da plateia.

## O que publiquei
Nada de vídeo novo. No canal existente:
- Títulos, descrições, hashtags e "não é para crianças" nos 4 Shorts (decisão do Lucas: não é para crianças).
- Curtida, coração e resposta no único comentário real (@Niko_com_k "A galinha eu acho", no vídeo dos dinossauros).
- Placar real preenchido em docs/diretor/PLACAR.md.

## O ep003 (parte 2 dos dinossauros), por que foi reprovado
- v1 (63 s): plateia 5, 5, 6, 5, 5. Todos deslizam entre 35 e 42 s (o meio vira aula: proteína do osso, florestas, fóssil). O Thiago desliza aos 18 s (pausa parada da gag da Pipo).
- Lucas: nota 3. "Sem foco, sem qualidade nas imagens, efeitos sonoros péssimos; o único ponto alto é o gráfico." (Perguntei se "gráfico" é estilo/cores e "sem qualidade" é nitidez; ele ainda não respondeu. Pergunte de novo.)
- v2 (45 s, reedição sem render, ep003b, docs/diretor/ciclos/2026-11-22/reedit.py): Davi 3 (desliza aos 17,5 s: "galinha come milho... e daí?"), Thiago 4. O corte não salvou. O problema é de premissa e de acabamento, não só de duração.
- Fato: o Thiago apontou que "Você comeu um desses" com um T. rex na tela e "Virou almoço" sugerem que a galinha descende do T. rex, o que é falso (são primos terópodes). E o estudo do colágeno de 2007 é contestado. Não use nenhum dos dois como fato limpo.
- Assets: os quadros 720p estão no branch render-out/ep003 (MP4 CRF 14 + info.json); a cena em render/ep003 (os .blend, o ep.py e o mundos.py). Votos em docs/diretor/ciclos/2026-11-22/plateia_v1 e plateia_v2.

## O que aprendi (com evidência)
- Gancho respondido cedo mata o vídeo. "Galinha" chega aos 13 s, e depois disso "por que eu fico?" (Davi v2). Evidência: todos os votos.
- Uma ideia por vídeo. O ep003 tinha 6 fios (asteroide, Niko, Pipo, fúrcula, florestas, Bélgica). O único momento "caramba" de todos foi o raio-x da fúrcula (24 a 30 s). Esse sozinho seria o vídeo.
- Modelo procedural de perto não segura. O T. rex virou "urso", "capivara" e "jacaré com corpo de batata" em 4 dos 5 votos. O olho oco (9,5 a 10,5 s) parece bug.
- SFX procedural é ruim (Lucas). O Kaggle tem internet: dá para trazer bancos grátis com licença comercial. CONFERIR A LICENÇA antes de usar.
- Qualidade: 720p com 10 amostras ampliado para 1080 fica borrado. O Kaggle aguenta 1080 nativo.
- A plateia de agentes concorda com o Lucas na direção, mas é mais branda (5 a 6 contra 3). Some 2 pontos de desconto mental.
- A gag "Pipo foge porque galinha come milho" não ganhou ninguém fora da Carla ("fofo"): "e daí?" (Davi). A Pipo precisa entrar sem quebrar a linha da história.

## Decisões que tomei e por quê
- Não publicar o ep003 (nem a v1 nem a v2). Padrão 10: nenhuma das duas passa, e o Lucas deu 3.
- Render na GPU do Kaggle (2 T4 grátis, 30 h/semana): ~1,65 s/quadro em 720p com 10 amostras nas 2 GPUs (51 min para 1.912 quadros). O fluxo está na BASE seção 14.
- render_kaggle.py agora envia em pedaços de 240 quadros (branches render-out/<ep>-cNN) e retoma o que falta. Rodar SEMPRE como "Save Version" (job em segundo plano), nunca na sessão interativa: o Lucas recarregou a página e quase perdemos 50 min. O render/run_ep.py é a célula pronta.

## O que falhou e de quem foi a culpa (inclusive minha)
- Minha: aprovei uma premissa com gancho que se resolve em 13 s e deixei 6 fios num vídeo de 63 s. Aprovei a prévia do cenário olhando beleza, não legibilidade do bicho.
- Minha: usei agentes demais. A cota de 5 horas do Lucas estourou duas vezes neste ciclo (diretor de arte e plateia v2 cortados no meio). Plateia agora vai num agente só, com as 5 personas.
- Minha: deixei o render sem envio parcial e numa sessão interativa.

## Funcionários
- Roteirista: bom diagnóstico (abertura sem bicho), mas eu tive que corrigir 3 fatos (ossinho, florestas, "três por pessoa"). Próximo briefing: no máximo 3 revelações, e o gancho só se resolve no último terço.
- Diretor de arte: entregou rápido e cumpriu as notas, mas o T. rex procedural não convence. Próximo briefing: legibilidade da silhueta em 0,5 s de longe é critério de aceite.
- Animador: impecável tecnicamente (QA zero, match cut exato, .blend portáveis). Sem crítica.
- Plateia: útil e consistente; branda demais em relação ao Lucas.

## Discordâncias com o Lucas
Nenhuma. Ele tinha razão na nota 3. As sugestões dele (Pipo como lente do canal, a Pipo que às vezes é o drama, easter egg no fundo com arcos curtos de 3 a 7 vídeos, erro proposital com trava, comentário que volta no vídeo seguinte) estão na BASE, seções 10 a 13.

## Próximo ciclo: o que eu faria primeiro
1. RESPONDIDO pelo Lucas: a luz e o visual estão bonitos; os modelos 3D é que estão mal feitos. Prioridade: modelos melhores (BASE seção 16).
2. Montar um banco de SFX e trilhas reais pelo Kaggle (internet ligada), com licença comercial verificada e o arquivo de licença no repositório. Testar um vídeo curto só para medir o ganho de som.
3. Refazer a parte 2 como UMA ideia: "o T. rex tinha ossinho da sorte", com abertura no raio-x da fúrcula, ~30 s, 1080 nativo e um T. rex de silhueta inconfundível. A pergunta final com lado de verdade.
Alternativa: um "E se..." curto com narrador + Pipo (formato novo do Lucas), numa ideia só.

## Pendências e coisas que só o Lucas pode fazer
- Verificação do canal: o Lucas já enviou o vídeo de verificação; está em análise no YouTube.
- As 3 tarefas agendadas antigas continuam pausadas e não foram reescritas.

## Séries abertas
- Dinossauros: a parte 1 prometeu a continuação e eu respondi ao @Niko_com_k "A parte 2 conta o resto". A parte 2 ainda NÃO saiu. Prazo moral: o quanto antes. Não publicar algo ruim só para cumprir.
- Arco da Pipo 1 ("A galinha quer a Pipo"): NÃO começou, porque o ep003 não foi publicado. Reavaliar a gag antes de abrir o arco.
