# Pesquisa 24/11/2026: memes, sonoplastia e imagens livres (agente de pesquisa, só web)

## Conclusões que viraram regra
1. Foto original de meme famoso: NÃO usar. Riscos somados: strike por pedido manual (3 strikes encerram o canal), dano moral por direito de imagem (Código Civil art. 20, Súmula 403 do STJ, vale até para foto que já circula como meme), direito autoral do fotógrafo/emissora (Lei 9.610/98). Não existe "fair use" como defesa no Brasil. Fontes: support.google.com/youtube/answer/13823830, canaltech.com.br/legislacao/o-impacto-dos-memes-no-direito-de-imagem/
2. ALERTA YPP (monetização): desde 15/07/2025 a política de "conteúdo inautêntico" mira "roteiros em template", slideshows e conteúdo de IA "com templates genéricos que dão impressão de produção em massa" (support.google.com/youtube/answer/1311392; searchenginejournal.com/youtube-monetization-update-spam-not-reaction-channels/550755/). Para um canal com produção diária automatizada, VARIAR estrutura, roteiro, ritmo e enquadramento de verdade importa mais que o risco dos memes. -> regra de variedade no GUARDRAILS.
3. Meme como estrutura redesenhada (seguro): ninguém/eu, expectativa x realidade, aprova/reprova, POV, plot twist, eu explicando x eles, como começou x como está indo, cérebro em níveis, mão estendida ("divas estendendo a mão", 2025), "fulano atrasado" (2025), torcida de Copa para coisa banal (2025), olho único "tô de olho" (2025). Tendências 2025: cnnbrasil.com.br/pop/marisa-maio-e-mais-relembre-os-memes-que-marcaram-2025/
4. Sonoplastia: pausa de 0,3 a 0,5 s antes da revelação; riser de 1 a 2 s antes dela; hit + whoosh no corte; pop/click em cada texto; música 18 a 24 dB abaixo da voz durante a fala, com ducking de 3 a 6 dB e volta nas pausas; troca de faixa ou de stem quando a emoção muda; master -14 LUFS, true peak -1 dBTP. Efeito cartunesco demais chama atenção para si. Fontes: descript.com/blog/article/how-to-sound-design-a-youtube-video, overseeros.com/blog/background-music-volume-under-voiceover, workflow.frame.io/guide/loudness-for-youtube, fluxnote.io/guides/faceless-shorts-retention-tips-2026 (números de retenção desta última sem base independente).

## Fontes de imagem e som (licença / download sem login)
| Fonte | Licença | Sem login? | API |
|---|---|---|---|
| Met Museum | CC0 (isPublicDomain) | sim, até 80 req/s (daqui deu 410: bloqueado no proxy) | collectionapi.metmuseum.org/public/collection/v1/ |
| NASA Images | sem copyright nos EUA (exceções: logos, terceiros, pessoas identificáveis, sugerir endosso) | sim | images-api.nasa.gov |
| Openverse imagem/áudio | filtrar license=cc0,pdm | sim, ~1 req/s, proibido scraping | api.openverse.org/v1/images/ e /v1/audio/ |
| Library of Congress "Free to Use" | domínio público | sim, 20 req/min JSON | loc.gov/free-to-use/?fo=json |
| Art Institute of Chicago | maior parte CC0 | sim | api.artic.edu |
| Cleveland Museum | campo CC0 | sim | openaccess-api.clevelandart.org |
| Wikimedia Commons | por arquivo | sim, com User-Agent identificado | commons API (aqui o proxy bloqueou upload.wikimedia.org) |
| Smithsonian | CC0 nos liberados | precisa key grátis | api.si.edu |
| Freesound | por arquivo | original exige OAuth | freesound.org/apiv2/ |
| OpenGameArt | por item (só CC0 é livre) | links diretos | sem API |
| Pixabay | NÃO é CC0; parte da música tem Content ID | key com login | evitar |
| Sonniss GDC | royalty-free próprio, não CC0 | manual | evitar no automático |
