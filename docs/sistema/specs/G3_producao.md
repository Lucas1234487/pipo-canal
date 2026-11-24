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
