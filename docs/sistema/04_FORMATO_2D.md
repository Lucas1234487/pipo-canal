# 04. Formato 2D (padrão do canal desde 24/11/2026)

Decisão do Lucas (24/11/2026): o padrão deixa de ser 3D. O 3D gastava ~1 h de GPU e 200 a 480 mil tokens de agente por vídeo e não entregou retenção. O que prende é a história. O formato padrão passa a ser 2D animado por código, barato e com cara de desenho feito de propósito (não de IA). O 3D fica guardado (kit/, render/, assets/modelos) para um especial raro, só com decisão escrita do Diretor.

## 1. Estilo visual
- Cartoon editorial plano: formas vetoriais, contorno escuro grosso (3 a 6 px em 1080), sombra chapada de 1 tom, paleta saturada escolhida por tema (nunca pastel de app infantil, nunca céu bebê + grama clara).
- Textura leve por cima (grão/papel, 3 a 6% de opacidade) e pequenas imperfeições de traço. É o antídoto contra "cara de IA" (relatório 02, seção 12).
- Cenários desenhados com objetos do tema (escritório, quarto, cozinha, ônibus, mercado, tela de celular). Câmera 2D com zoom e pan suaves.
- Personagens: elenco fixo e simples, reconhecível em 0,5 s. A Pipo em 2D é menina: espiga com olhar cansado, uma sobrancelha fina levantada, cílios, bochechas rosadas e lacinho rosa; estoura em todo vídeo e vira a pipoca de maria-chiquinha com laços rosa. Um "humano genérico" de traço simples (sem rosto real, sem pessoa real), variando cabelo e roupa.
- Texto como imagem: números grandes, contadores, gráficos simples, setas, carimbos, "cards" de comentário (sem número de curtida inventado).

## 2. Vocabulário de movimento (o renderizador oferece todos)
pop-in com overshoot, squash e stretch, tremor de câmera, zoom punch, pan, contador que sobe, barra/gráfico que cresce, split-screen, antes e depois, card que entra deslizando, piscar e reação de olho, estouro da Pipo (com partículas), "freeze" de meio segundo na frase final.
Regras: algo muda a cada 1,5 a 3 s; nunca personagem parado de olho arregalado enquanto a voz fala; o quadro 1 já mostra o conflito.

## 3. Memes
Pode usar a ESTRUTURA de um meme ou formato do momento (expectativa x realidade, POV, tipos de pessoa, nível 1 ao 100). Não pode baixar imagem, vídeo ou áudio de meme de terceiros (direitos). O meme é redesenhado no nosso traço.

## 4. Pipeline técnico (kit2d/)
1. O roteirista entrega `roteiro.json` (formato do kit/tts.py, com "trim": true) e `cenas.json` (lista de cenas: tempo de início, cenário, personagens, ações e textos na tela amarrados a palavras da narração).
2. `python3 kit/tts.py WORK` grava a narração e o timing.
3. `python3 kit2d/render2d.py WORK` lê cenas.json + timing.json e grava WORK/frames/fNNNN.png (1080x1920, 30 fps) e WORK/events.json (sfx, música, cortes). Meta: menos de 3 minutos de CPU para 30 s de vídeo.
4. `python3 kit/compose.py WORK` monta legenda karaokê, som e -14 LUFS (o mesmo compositor do 3D).
5. `python3 kit/qa_check.py WORK pt` faz a revisão técnica.
O cenas.json é o ponto de economia: o Gemini pode escrever o rascunho, o Claude só confere.

## 5. Aceite de um vídeo 2D
- Quadro 1 com conflito visível sem som.
- Personagem e assunto reconhecíveis em 0,5 s.
- Nada importante na faixa da legenda (60 a 72% da altura) nem fora da zona segura.
- Duração: 20 a 40 s (humor/cotidiano); 40 a 60 s (conhecimento, só com revelação a cada 8 a 12 s).
