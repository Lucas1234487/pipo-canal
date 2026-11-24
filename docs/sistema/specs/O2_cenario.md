# O2 Cenário (organizador)
Antes: leia docs/diretor/cadernos/O2.md, kit2d/CENAS.md (cardápio completo), specs/G3_producao.md (backlog de fundos) e o roteiro.json/timing.json do O1.
Entrega: WORK/cenas.json (sem a parte de som: deixe "musica", "sfx", "silencios" e os "som" das ações para o O3) e WORK/previa.jpg (`python3 kit2d/render2d.py WORK --previa`).
- Quadro 1 mostra o conflito sem som. Corte a cada 2 a 3 s, troca de paleta, nada parado mais de 3 s.
- Fundo com camadas e personagem interagindo com ele (sofá, porta, mesa, janela) sempre que o motor permitir; se faltar algo no motor, anote no bilhete para o Diretor (vira tarefa de código).
- Clima conta a história: tenso = noite/petroleo + chuva; virada = paletas quentes + raios.
- Foto real quando um fato ganha força com a coisa de verdade (osso, planeta, lugar, bicho): `python3 kit/imagens.py buscar "termo em inglês" WORK`, olhe WORK/img/candidatas.jpg, `usar WORK n`, elemento "foto" com crédito. Só CC0/domínio público. Não em todo vídeo.
- Zona segura e legenda: rode a prévia e o render até o QA de cena zerar reprovações.
Bilhete em WORK/bilhetes/O2.md. 1 lição no caderno.

## Fundo condizente com a história (Lucas, 24/11 15h33)
- Fundo dinâmico = fundo que É o lugar da história e tem coisas acontecendo nele (casa de Natal com pisca-pisca piscando e o vizinho exagerado ao lado; loja com placas de desconto piscando; praia com ondas). Use os cenários temáticos do CENAS.md.
- Fundo abstrato animado (gradiente, bokeh, raios, espiral...) só em cena de dado/explicação, revelação ou meme. Cor lisa ou listra parada: não.
- Memes da Pipo (elemento "meme") e reações de meme (ação "reacao") entram em momentos de piada, no máximo 2 por vídeo.

- Imersão: quando houver foto real, prefira começar com ela em tela cheia (`fundo_foto`, Ken Burns/parallax) e `mergulho` para o mundo 2D; a foto em polaroide é a opção mais simples, não a padrão.
