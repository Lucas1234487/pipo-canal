# O3 Sonoplastia (organizador)
Antes: leia docs/diretor/cadernos/O3.md, kit2d/CENAS.md (sons, músicas, "silencios", "sfx") e assets/LICENCAS.md.
Entrega: as chaves de som no WORK/cenas.json (musica, musica_inicio, silencios, sfx, whoosh_nos_cortes, e "som"/"volume" nas ações) e um bilhete com o mapa de som (segundo: o que toca e por quê).
- Som que intriga: o clima muda com a história (mistério no tenso; corte seco de música antes da virada; música nova ou impacto na explosão).
- Todo elemento que entra tem som; nenhum som repetido 3 vezes seguidas; o estouro da Pipo sempre audível.
- Só arquivos CC0 de assets/. Falta um som? Procure CC0 (OpenGameArt, Openverse áudio), registre a proveniência e avise no bilhete.
- Depois do O4 montar, ouça o resultado pelo relatório do QA de áudio (-14 LUFS, voz por cima da música).
Bilhete em WORK/bilhetes/O3.md. 1 lição no caderno.

## Receita de retenção (pesquisa 24/11, docs/pesquisa/2026-11-24_memes_som_imagens.md)
- Riser de 1 a 2 s antes da revelação; silêncio de 0,3 a 0,5 s logo antes dela; hit + whoosh no corte.
- Pop/click em cada texto que entra; efeito cartunesco demais chama atenção para si (dose).
- Música 18 a 24 dB abaixo da voz durante a fala; ela volta nas pausas. Troque de faixa (silencios + sfx) quando a emoção muda.
- Master -14 LUFS, true peak -1 dBTP (o compose já normaliza; confira no relatório do qa_check).

## Todo som tem que aparecer no celular (Lucas, 24/11: "o Boom não teve som nenhum")
- Alto-falante de celular quase não toca grave: um "boom" só de grave some. Todo efeito precisa de corpo entre 200 Hz e 3 kHz.
- Antes de usar um som novo, rode `python3 kit/checa_sons.py assets/sfx/<pasta>`: ele simula o celular e acusa o que some. Som acusado é consertado (saturação + passa-alta + realce de médios) ou trocado.
- O Lucas gosta de MUITO efeito sonoro (o ep006, com vidro quebrando e impactos, é a referência): som em toda entrada, corte e virada.
