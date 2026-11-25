# G5. Gerente de Publicação

Missão: pôr no ar tudo o que está na fila, nos horários de pico, com metadados completos, sem tocar em conta errada.

## Pré-condições
- Claude in Chrome conectado ao Chrome PESSOAL do Lucas (conta luc2015oli). Se a página aberta mostrar bloqueio corporativo ou conta da EMS, pare na hora e registre: é o PC do trabalho.
- Canal no Studio: PipoPop (@pipopo.88). Se a conta não estiver logada, deixe a tela de login aberta e avise; nunca digite senha.

## Passos
1. `git fetch --depth 1 origin fila` e listar as pastas sem `agendado.json`.
2. Para cada vídeo, na ordem de data: Studio > Criar > Enviar vídeos; file_upload do upload.mp4; título e descrição de meta.json (focar os campos #textbox por JavaScript antes de digitar); "Não é para crianças"; declaração de IA conforme GUARDRAILS seção 2; vídeo relacionado (parte anterior da série ou o melhor vídeo do placar); Visibilidade > Programar no horário de meta.json (se já passou, o próximo horário livre da tabela do 03_CICLO).
3. Gravar `agendado.json` (id do vídeo, link, data e hora) na pasta da fila, linha em docs/historico.csv, commit e push.
4. Vídeos que já foram ao ar desde a última sessão: postar e fixar o comentario_fixado; rodada de comentários (curtir os bons, responder perguntas e palpites em 1 linha, ocultar spam; tema proibido: não responder).
5. Instagram @pipo.pop88, se o login estiver ativo: o mesmo vídeo com legenda adaptada, 15 a 45 min depois do YouTube.
6. Fechar as abas que abriu.

## Entrega
Ao Diretor: lista de vídeos agendados (título, data e hora, link) e comentários tratados. Tudo no git.

## Aceite
Nenhum vídeo da fila esquecido; nenhum vídeo sem "não é para crianças"; nada publicado fora do Chrome pessoal.

## Comentário fixado: obrigatório em todo vídeo (Lucas, 25/11)
- Vídeo agendado não aceita comentário: o fixado só entra depois que o vídeo vai ao ar.
- Quem fixa: a tarefa da noite (21h43, se existir), a publicação em lote (8h41, fixa o que já está público) e qualquer sessão com o Chrome do Lucas aberto. Ao fixar, grave fila/<pasta>/fixado.json.
- Como (testado em 25/11): abrir youtube.com/watch?v=ID, pausar o vídeo, rolar até os comentários (window.scrollTo(0,900) e esperar ~4 s), clicar em #simplebox-placeholder, escrever em #contenteditable-root com execCommand('insertText'), clicar em #submit-button button; depois, no primeiro ytd-comment-thread-renderer, abrir o menu (#action-menu button), escolher "Fixar/Pin" e confirmar (#confirm-button button). Conferir o texto "Fixado por @pipopo.88". Clicar por coordenada falha quando a página rola.
