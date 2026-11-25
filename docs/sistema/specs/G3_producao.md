# G3. Gerente de Produção

Missão: transformar roteiro.json + cenas.json em MP4 pronto, rápido e sem defeito técnico. Quase tudo aqui é script: o custo de tokens deve ser mínimo.

## Leia
docs/sistema/04_FORMATO_2D.md, kit2d/CENAS.md, docs/BASE_CONHECIMENTO.md seção 6.4 (armadilhas).

## Passos (por vídeo, WORK = /home/claude/AAAA-MM-DD_A ou _B)
1. `bash kit/setup.sh` (uma vez por sessão).
2. `python3 kit/tts.py WORK` (narração; confira a duração).
3. `python3 kit2d/render2d.py WORK` (quadros 2D + events.json).
4. `python3 kit/compose.py WORK` (legenda karaokê, som, -14 LUFS) e `python3 kit/qa_check.py WORK pt`.
5. Olhe WORK/qa_sheet_pt.jpg uma vez. Defeito visual (personagem cortado, texto sobre texto, quadro vazio): corrija o cenas.json e renderize só de novo; no máximo 2 voltas.
6. Versão de upload: `ffmpeg -i WORK/final_pt.mp4 -vf scale=720:1280 -c:v libx264 -b:v 800k -maxrate 900k -bufsize 1600k -preset veryfast -c:a aac -b:a 96k WORK/upload.mp4` (precisa ficar abaixo de 3,8 MB; se passar, baixe o bitrate).
7. WORK/meta.json: titulo (até 50 caracteres, palavra-chave no começo), descricao (2 a 4 frases + 3 a 5 hashtags com #PipoPop, nunca #viral/#fyp), comentario_fixado (a pergunta do vídeo), horario_sugerido (03_CICLO), titulo_en e descricao_en.

## Desenvolvedores
Subagente Claude só para bug do kit2d ou recurso visual novo que o cenas.json não consegue expressar. Nesse caso, o subagente corrige o kit2d (com teste) e o conserto vai para o git.

## Entrega
WORK/final_pt.mp4, WORK/upload.mp4, WORK/meta.json, WORK/qa_sheet_pt.jpg e o relatório do qa_check. Ao Diretor: 4 linhas por vídeo (duração, tamanho do upload, qa_check, o que corrigiu).

## Aceite
qa_check aprovado; upload abaixo de 3,8 MB; render 2D de um vídeo em menos de 5 min.

## Próximo passo de qualidade (Lucas, 24/11: "os fundos podem ser mais complexos e as pessoas interagirem com o fundo")
Backlog do kit2d, por ordem:
1. Cenários com profundidade: 3 camadas (fundo, meio, frente), objetos que se mexem (cortina, vapor do café, chuva na janela, carro passando), luz da cena (dia, fim de tarde, noite com abajur).
2. Interação: personagem senta no sofá, abre a porta, deita na cama, pega o celular da mesa, olha pela janela, fica atrás da mesa (camada da frente cobre as pernas).
3. Humano mais bonito: rosto mais expressivo, cabelo longo que não pareça véu (o Gemini leu a ruiva como hijab), criança com proporção de criança.
4. Novos cenários: rua/trânsito, cozinha, carro, ônibus, escola.

## Estado do motor em 24/11 noite
Feito: cenários em camadas com vida e âncoras, temáticos (Natal, loja, praia, festa, cidade, espaço...), fundos animados, foto em tela cheia com mergulho, humano novo com assinatura e elenco fixo, 20 memes da Pipo, 7 reações de meme com som.
Backlog FEITO na dev-back (24/11): brilho de cena, chuva em qualquer cenário, split, pisca com brilho, braços da pipoca, mapa, árvore e casa soltas; mais os ajustes do dono (pés no sofá, ônibus refeito, carro, supermercado, academia, cidade_noite_alto, celular moderno). Pedido original: chuva no cidade_noite_alto; controle de brilho/escurecer do cenário (hoje é um bloco com alpha); tela dividida (split-screen com duas mini-cenas); "pisca" com brilho em vez de sumir; braço na Pipo pipoca; mapa estilizado (Brasil/mundo); árvore e casa como elementos soltos.
- (24/11) compose: o loudnorm de uma passada achata os transientes (o estouro perdeu ~2 dB no master). Trocar por loudnorm em 2 passadas (medir e aplicar linear) ou ganho + limiter.
- (24/11) ônibus e carro ficaram 16-22% mais lentos; cachear partes paradas.
