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

## Instagram @pipo.pop88 e página do Facebook "PipoPop" pelo Metricool (conectados em 26/11)
- Metricool brand 8272438 tem youtubeData, instagramData (pipo.pop88) e facebookData (página PipoPop 1491381724050961).
- Cada vídeo agendado no YouTube ganha um 2º post no Metricool, no MESMO horário, com providers [{"network":"instagram"},{"network":"facebook"}]: instagramData {"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}, facebookData {"type":"REEL","title": título do meta.json}, media = mesma URL raw do upload.mp4, text = título + descrição do meta.json (hashtags no fim, até 5), firstCommentText = comentario_fixado.
- Gravar o id em agendado.json (campo "meta_ig_fb"). Se o vídeo já estava agendado só no YouTube, agendar o post do Instagram/Facebook também (se o horário passou, o próximo slot livre do dia).
- Se getBrandSettings não tiver instagramData ou facebookData, a conexão caiu: seguir com o que estiver conectado e anotar no handover para o Lucas reconectar.
- Só @pipo.pop88 e a página PipoPop. Nunca a conta pessoal do Lucas.

## Hashtags obrigatórias (pedido do Lucas, 26/11)
Toda descrição (YouTube) e toda legenda (Instagram/Facebook) termina com as hashtags do meta.json (3 a 5, com #PipoPop). Antes de agendar, conferir no texto enviado ao Metricool/Studio que elas estão lá; sem hashtag não agenda.

## CAMINHO PRINCIPAL: Metricool (sem PC, testado em 25/11)
O YouTube do canal está conectado no Metricool (marca 8272438, fuso America/Sao_Paulo). Qualquer sessão, mesmo na nuvem e com o PC do Lucas desligado, agenda assim:
- Depois do push na `fila`, a URL pública do vídeo é https://raw.githubusercontent.com/Lucas1234487/pipo-canal/fila/<PASTA>/upload.mp4 (o repositório é público; o Metricool baixa e guarda).
- Ferramenta createScheduledPost: blogId "8272438", date = horário do meta.json; info = {autoPublish: true, draft: false, descendants: [], providers: [{network: "youtube"}], media: [<URL acima>], mediaAltText: [], text: <descrição do meta.json>, firstCommentText: <comentario_fixado do meta.json>, publicationDate: {dateTime: "AAAA-MM-DDTHH:MM:00", timezone: "America/Sao_Paulo"}, shortener: false, smartLinkData: {ids: []}, youtubeData: {title: <titulo>, type: "short", privacy: "public", tags: [3 a 5 palavras], madeForKids: false, isAiGeneratedContent: false, category: "ENTERTAINMENT" (ou "EDUCATION" no pilar C)}}.
- Grave agendado.json com {"via": "metricool", "metricool_id", "plannerUrl", "horario"}; o id do YouTube aparece depois da publicação em getScheduledPosts (providers[0].id).
- O primeiro comentário é postado pelo próprio canal na hora da publicação (em vídeo privado falha; em público funciona). Fixar continua precisando do Chrome do Lucas (tarefa da noite, publicação em lote ou qualquer sessão com o Chrome aberto).
- Teste de 25/11: vídeo privado "TESTE privado Metricool" (uafsXtjCn8E) subiu certo; o comentário falhou só por ser privado. Pode ser apagado pelo Lucas.
- Claude in Chrome no Studio vira o caminho alternativo (quando precisar de vídeo relacionado ou o Metricool falhar).
