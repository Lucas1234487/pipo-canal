# 05. Anti-esquecimento: como fazer os vídeos não morrerem em 48 h

Agente 5, ShoShortz. Data: 21/11/2026.

## 0. A verdade que muda o plano

1. **YouTube Shorts tem prazo de validade de uns 30 dias.** Desde setembro de 2025, analistas de canais grandes veem uma queda forte de impressões nos Shorts com mais de 28 a 30 dias. O YouTube não confirmou, mas o padrão se repetiu em vários canais e em 2026 continua. Muitos criadores de conteúdo "evergreen" viram os vídeos antigos despencarem. Então a meta realista é outra: em vez de "viver para sempre", o vídeo precisa durar o mês inteiro, e não só 48 h. Depois disso, cauda longa só vem por busca, por séries, playlists e vídeo relacionado.
2. **Shorts ainda têm vida depois de 30 dias, mas só por três caminhos:** (a) busca, quando o vídeo responde algo que as pessoas pesquisam; (b) ressurgimento, quando um vídeo novo do mesmo tema explode e puxa os antigos junto, ou quando chegam inscritos novos que vão olhar o catálogo; (c) sessões encadeadas, via playlist, série e vídeo relacionado.
3. **No Instagram, os 3 sinais oficiais** que o próprio Instagram citou são tempo de visualização, envios por alcance (quantas pessoas mandam no direct, proporcional a quantas viram) e curtidas por alcance. Para quem ainda não segue o perfil, o envio por direct é o sinal que mais pesa. Salvamentos e comentários com conteúdo ajudam. Curtida sozinha mexe pouco.
4. **No YouTube, o primeiro filtro é "exibido vs. deslizado".** Cada Short vai primeiro para um público pequeno de teste. Se muita gente desliza logo, a distribuição para ali. Depois vem a retenção (porcentagem média assistida, com replay contando) e só então curtidas, comentários e compartilhamentos.
5. **O que mudou em 2026 e afeta a gente diretamente:**
   - Desde 31/08/2026, **comentários de Shorts não aceitam mais link clicável**, nem do criador, nem do público. O comentário fixado continua útil, mas só para texto: pergunta, contexto, aviso da próxima parte.
   - O YouTube lançou o **Shorts Series** (temporadas e episódios, com reprodução em sequência, no celular, na web e na TV). Ele está sendo liberado só para quem já está no Programa de Parcerias (YPP). Até a gente monetizar, a série precisa ser montada "na mão" com playlist e vídeo relacionado.
   - No Instagram, o **Reels vinculado** (botão "próxima parte" no canto inferior esquerdo) já está liberado no mundo todo e dá para aplicar em Reels antigos pelo menu de três pontos.
   - O Instagram agora aceita **no máximo 5 hashtags** por post/Reel. Legenda com palavra-chave rende mais que um monte de hashtag.
   - O Instagram pune **conteúdo repostado/não original**: perfil que posta principalmente coisa reaproveitada vira "agregador" e perde alcance para não seguidores. Vídeo com marca d'água de outra plataforma também é rebaixado. Isso pesa a nosso favor, porque nosso 3D é 100% original, mas pede cuidado na hora de repostar os nossos próprios vídeos.
   - O YouTube avisa que reenviar o mesmo Short várias vezes pode ser tratado como spam.

## 1. Sinais do algoritmo traduzidos em regras de produção

### 1.1 Exibido vs. deslizado (o vídeo nasce ou morre aqui)
- Os primeiros 1 a 2 s têm que mostrar o assunto e já trazer movimento. Nada de logo, vinheta longa nem "e aí, pessoal".
- O primeiro quadro precisa funcionar como capa: objeto 3D grande no centro, contraste alto, algo estranho ou incompleto que gere pergunta.
- Texto na tela no primeiro segundo com a promessa ("Por que o polvo tem 3 corações?"), dentro da zona segura.
- Regra para o agente de roteiro: a primeira frase falada é a pergunta ou o fato mais surpreendente do vídeo. O contexto vem depois.

### 1.2 Retenção e rewatch
- Hoje a média de tempo assistido por Short caiu para uns 16 s. Vídeo de 60 a 90 s só segura se tiver "degraus": uma revelação nova a cada 8 a 12 s.
- **Loop perfeito**: o último quadro e a última frase emendam no primeiro. Exemplo: o vídeo termina com "...e é por isso que" e recomeça em "o polvo tem três corações". No 3D isso é barato: a câmera termina na mesma posição e no mesmo enquadramento do quadro 1, e o personagem volta à pose inicial.
- Corte toda pausa morta da narração (TTS gera silêncio no começo e no fim: aparar com FFmpeg, silenceremove).
- Revelação adiada: segurar o "pagamento" até perto do fim, mas sem enrolar no meio.
- Coisas pequenas para rever: detalhe escondido no cenário (um easter egg 3D por vídeo, tipo o mascote aparecendo no fundo) que faz a pessoa voltar. Pode até virar quadro fixo: "achou o mascote?".

### 1.3 Envios (shares/sends), o sinal mais forte para alcançar quem não segue
Envio acontece quando o vídeo serve para falar com alguém. Roteirizar pensando em "pra quem a pessoa vai mandar":
- "Manda pra quem..." implícito no tema: fato que vira assunto ("isso explica seu amigo que dorme 12 h").
- Comparações e rankings que geram discussão entre amigos.
- Curiosidade que dá vontade de testar com outra pessoa (pergunta, desafio visual, ilusão de ótica 3D).
- Evitar pedir "compartilha" em voz alta: soa como isca. Melhor deixar o tema fazer isso.

### 1.4 Salvamentos
- Conteúdo de "consultar depois": listas, passo a passo, "3 coisas que...", dicas práticas. Um fecho tipo "a terceira é a mais útil" segura até o final e gera salvamento.
- Vídeos de conhecimento (60 a 90 s) são os que mais salvam. Vídeo de humor de 30 s rende mais envio do que salvamento.

### 1.5 Comentários reais
Ver seção 5.

## 2. Evergreen vs. tendência: a mistura

Por causa do prazo de uns 30 dias nos Shorts, tendência e evergreen têm funções diferentes:
- **Tendência** dá pico rápido e inscritos novos. Esses inscritos depois vão olhar o catálogo antigo, e é aí que o evergreen volta a ganhar view.
- **Evergreen pesquisável** é o único tipo que continua gerando view depois de 30 dias (via busca) e que ressurge quando o tema volta à moda.

Proposta de mix para os 2 vídeos diários (14 por semana):
- **~60% evergreen pesquisável** (curiosidades, "por que X acontece", "como funciona Y", ciência do dia a dia), com título que é exatamente a pergunta que a pessoa digitaria.
- **~30% tendência adaptada** (formato ou assunto em alta, recriado em 3D no nosso estilo). Como o render demora cerca de 1 h por minuto de vídeo, a tendência precisa ser curta (≈30 s) e entrar em até 24 a 48 h.
- **~10% experimento** (formato novo, gancho diferente, duração diferente) para descobrir o próximo formato vencedor.

Regras para o evergreen durar:
- Nada de data, "hoje", "essa semana" ou referência a notícia no áudio ou no texto queimado. Se precisar, coloca só no título, que dá para editar depois.
- Título no formato de busca: "Por que o céu é azul?" funciona melhor que "Você não vai acreditar nisso 😱".
- Descrição com 1 a 2 frases contendo a palavra-chave e sinônimos. No YouTube não precisa usar #Shorts. Hashtag pode tirar um pouco de view e dar um pouco mais de engajamento, então usar no máximo 2 a 3, e só com termo específico.
- Categoria Educação nos vídeos de conhecimento.

## 3. Séries e numeração de episódios

### 3.1 Por que séries
Série cria motivo para assistir o próximo, ajuda a montar playlist e sessão, e faz um episódio que viraliza puxar os outros (o ressurgimento por tema relacionado). Também deixa o trabalho do agente de engajamento bem mais claro: uma série que funciona ganha mais episódios.

### 3.2 Como montar série que funciona mesmo se a pessoa ver a parte 3 primeiro
- **Cada episódio se sustenta sozinho**: um fato ou piada completa, com começo, meio e fim. A série é um "guarda-chuva" temático, não uma novela com cliffhanger obrigatório.
- **Formato fixo de série, numeração no título e no canto da tela**: "Animais absurdos #7". O número mostra que existe mais, sem exigir que a pessoa tenha visto o anterior.
- **Nada de "como vimos na parte 2"**. Se precisar de contexto, recap de no máximo 1 s ("o bicho que não morre, de novo").
- **Gancho para o próximo episódio nos últimos 2 s, sem pedir**: "o #8 é ainda mais bizarro". Melhor que "segue para a parte 2", que derruba a retenção perto do fim.
- **Identidade visual por série**: cor de fundo, cenário base e mascote com acessório específico. Isso também é ótimo para o render: o cenário da série é modelado uma vez e reaproveitado (só troca o objeto central).
- **Série "fechada" de vez em quando** (ex.: 5 episódios), que vira uma compilação depois (ver 6.4).
- **Episódio 1 é o mais forte**: quando a série decola, é ele que mais vai receber gente vinda do perfil. Se um episódio do meio viralizar, ele vira "porta de entrada": fixar no topo do canal/perfil.

### 3.3 Mecânica por plataforma
- **YouTube (antes do YPP)**: uma playlist pública por série, com nome igual ao da série; todo episódio novo entra na playlist no momento do upload (a API permite). Em cada Short novo, o **vídeo relacionado** aponta para o episódio anterior mais forte, ou para o ep. 1 da série. Num episódio que viralizou, trocar o relacionado para o episódio seguinte.
- **YouTube (depois do YPP)**: migrar as playlists para o **Shorts Series**, com temporadas e episódios.
- **Instagram**: usar **Reels vinculado** em todo episódio (aponta para a próxima parte; dá para aplicar nos antigos depois que a próxima sair). Agrupar a série num destaque ou no grid fixado.

## 4. Vídeo relacionado, playlists e perfil como máquina de recirculação

- **Todo Short sai com vídeo relacionado preenchido.** Regra do pipeline: (1) se faz parte de uma série, aponta para o melhor episódio da série; (2) se não, aponta para o vídeo do canal com melhor retenção no mesmo tema nos últimos 30 dias; (3) quando existir vídeo longo/compilação, aponta para ele.
- **Revisão semanal do relacionado**: o vídeo que está explodindo na semana passa a ser apontado pelos vídeos novos (e o relacionado dele aponta para o próximo da série). Isso transforma o pico de um vídeo em view para os outros.
- **Playlists temáticas além das séries** ("Curiosidades de animais", "Corpo humano"): ajudam a montar sessões e o ressurgimento por tema.
- **Página do canal/perfil**: fixar no topo os 3 vídeos/séries de melhor retenção, e trocar a cada 2 semanas. Quem chega por um vídeo viral olha o perfil, e o perfil precisa converter essa visita em mais views.
- **Link**: como comentário de Short não aceita mais link, se um dia houver link (afiliado etc.), ele vai na descrição, no perfil ou num vídeo longo ligado ao Short.

## 5. Perguntas que geram comentário de verdade (sem cara de isca)

O que funciona:
- **Escolha com consequência**: "Você preferiria ter memória perfeita ou nunca mais sentir sono?". Perguntas com "qual" e "o que" rendem bem mais resposta que "você já...?" de sim ou não.
- **Palpite antes da revelação**: no meio do vídeo, "chuta quantos... antes de eu contar". A pessoa comenta o chute, e quem acertou volta para conferir.
- **Erro proposital pequeno e inofensivo** (um detalhe "errado" no cenário 3D que dá para apontar, tipo um relógio com 13 horas). Gera correção nos comentários. Usar com moderação, no máximo 1 em cada 5 vídeos, e nunca errar o fato principal, para não perder credibilidade.
- **Ranking com opinião**: "esse é o 3º mais estranho, qual seria o 1º para você?".
- **O público escolhe o próximo episódio**: "o tema mais curtido aqui vira o #8". E **cumprir de verdade**, citando no vídeo ("vocês pediram"). Isso cria um ciclo real e alimenta o agente de engajamento.
- **Experiência pessoal** ligada ao tema ("qual a coisa mais estranha que seu cachorro já fez?").

O que evitar (cara de isca ou de baixa qualidade):
- "COMENTA AÍ", "comenta 1 se...", "digita sim se você...".
- Pergunta genérica no fim ("o que vocês acharam?").
- Polêmica com os temas proibidos (política, religião, futebol). Mesmo de leve, não pode.

Como posicionar:
- Pergunta principal falada por volta de 80% do vídeo (não no último segundo, que é do loop) e repetida no texto na tela.
- **Comentário fixado** com a mesma pergunta ou um "bônus" que não está no vídeo (um fato extra). Depois de 24 h, trocar o fixado pela melhor resposta do público.
- **Responder nas primeiras horas**: os primeiros 10 a 20 comentários respondidos nas 2 primeiras horas, com resposta específica que termina em outra pergunta. Depois de 24 h a distribuição inicial já se definiu e comentário mexe menos.
- Ser honesto sobre o limite da automação: a API do YouTube permite publicar comentário como o canal e responder, mas não permite fixar. No Instagram também não há como fixar pela API de forma confiável. O fixar fica como tarefa manual de 1 minuto no app (ou o agente deixa o texto pronto numa notificação para o Lucas só colar e fixar). Respostas automáticas precisam soar humanas e não podem ser em massa nem repetidas, senão viram spam.

## 6. Repostagem, remix e ressuscitar vídeos antigos

### 6.1 Regras gerais
- **Nunca apagar** vídeo que flopou e **nunca reenviar o arquivo idêntico**. Reenvio repetido pode ser tratado como spam no YouTube, e o Instagram reconhece o arquivo e limita o alcance de conteúdo já publicado.
- Reenvio só é permitido para corrigir erro real (áudio cortado, enquadramento errado, legenda errada) e, nesse caso, deixar o original privado.
- **Remake ≠ repost**: mudar gancho, primeiros 2 s, ângulo de câmera, narração, ritmo e título. No 3D isso é barato porque a cena já existe: o agente reaproveita o .blend, muda câmera, cores e o primeiro bloco do roteiro, e renderiza de novo só o que mudou.

### 6.2 Ressuscitar vídeos com mais de 30 dias (rotina mensal)
1. Listar vídeos com mais de 30 dias que tiveram **boa retenção mas pouco alcance**, e vídeos que tiveram pico e caíram.
2. **Retitular para busca**: trocar título vago por pergunta exata que o público pesquisa, e melhorar a descrição. O conteúdo é o mesmo, só a embalagem muda.
3. **Pôr na playlist/série certa** e apontar o vídeo relacionado de vídeos NOVOS para eles.
4. **Fazer uma continuação**: "Parte 2" ou "versão ainda mais bizarra" de um vídeo antigo que foi bem. A continuação aponta para o original. Se a continuação estourar, o original ressurge junto.
5. **Remake de 60 a 90 dias depois** para os campeões: mesmo tema, novo gancho e nova abertura. Os campeões são a nossa matéria-prima mais segura.
6. **Datas e sazonalidade**: manter um calendário de temas que voltam (férias, Natal, calor, volta às aulas, Halloween, eclipses e eventos astronômicos). Na véspera, retitular e reforçar os vídeos antigos daquele tema e postar um novo que aponte para eles.

### 6.3 Instagram
- **Trial Reels** (testar para não seguidores antes de mostrar aos seguidores; liberado para contas profissionais públicas, em geral a partir de uns 1.000 seguidores): usar para testar 2 a 3 ganchos diferentes do mesmo vídeo. Escolher o vencedor depois de pelo menos 24 h e publicar para os seguidores. Comparar as versões de teste entre si, não com Reels normais.
- Reaproveitar um Reel antigo só como versão nova (gancho, corte, capa e narração diferentes), nunca o mesmo arquivo.
- Nunca subir o arquivo exportado com marca d'água de outro app. Sempre o MP4 limpo do nosso pipeline.
- Compartilhar Reel antigo que tem a ver com um assunto do momento nos Stories.

### 6.4 Compilações e vídeo longo
- Quando uma série chega a 5 a 8 episódios, montar uma **compilação** (vídeo longo, 3 a 8 min) só com FFmpeg, sem render novo. No YouTube, ela vira o vídeo relacionado dos episódios e leva link na descrição. Os episódios levam gente para a compilação, e a compilação leva de volta para os Shorts. Isso dá ao canal uma segunda fonte de views, longe do limite de 30 dias.
- Verificar com o agente de políticas (12) se compilação de material próprio conta como "conteúdo reutilizado". Material 100% nosso, com organização e narração de ligação nova, tende a ser aceito.

## 7. Frequência ideal

O que os dados mostram:
- Volume aumenta a chance de um vídeo "outlier" estourar. Em canais novos, o Short típico não melhora muito do 1º para o 10º, mas o melhor dos 10 primeiros fez cerca de 6,5 vezes a view do primeiro. Ou seja, o canal vive dos acertos, e cada post é um bilhete.
- Por outro lado, em contas de marca o desempenho **por Short** é melhor com 2 a 4 por semana, e no Instagram postar muita coisa fraca derruba o engajamento por alcance (que é sinal de ranking).
- Canais com centenas de Shorts publicados têm crescimento mais estável.

Recomendação para nós:
- **YouTube: manter 2 por dia**, desde que a qualidade não caia. Intervalo mínimo de 4 a 6 h entre os dois. Volume no YouTube compensa porque é bilhete de loteria e não "suja" o perfil do mesmo jeito.
- **Instagram: começar com 1 por dia** (o melhor dos dois) e usar o segundo como **Trial Reel** quando disponível. Subir para 2 por dia só se o engajamento por alcance não cair por 2 semanas seguidas.
- **Regra de qualidade mínima**: se o vídeo não passar no checklist de gancho e loop (seção 9), ele não entra na agenda. Melhor pular um horário do que postar algo fraco.
- Não apagar nem esconder vídeos para "limpar" o canal.

## 8. Protocolo para vídeo que flopou

Janela: não julgar antes de **48 a 72 h** (Shorts e Reels às vezes pegam tração dias depois).

Diagnóstico automático (agente de engajamento):
1. **Exibido vs. deslizado baixo** (muita gente desliza logo): problema de gancho, de primeiro quadro ou de público errado. Ação: remake só da abertura (novo primeiro quadro e nova primeira frase).
2. **Muita gente fica, mas a curva cai no meio**: problema de ritmo, de vídeo longo demais ou de revelação atrasada. Ação: versão mais curta (corte na edição, quase sem render novo).
3. **Retenção boa, mas alcance baixo**: o conteúdo é bom e a embalagem/distribuição falhou. Ação: novo título, nova capa e, depois de 2 a 4 semanas, remake com gancho novo, ou teste no Instagram como Trial Reel.
4. **Vem de busca mas com retenção baixa**: o título prometeu outra coisa. Ação: ajustar título para combinar com o conteúdo.
5. **Retenção ruim em todo mundo**: o tema não funciona. Ação: arquivar o tema na lista negra do agente de roteiro, não insistir.

Limite: **no máximo 2 tentativas por ideia** (original + 1 remake). Se as duas floparem, a ideia morre.

O que nunca fazer: apagar, reenviar idêntico, comprar view, pedir view em comentário de outro canal.

## 9. Checklist aplicado ao fluxo automatizado

### Agente de tendências / pauta (diário)
- [ ] Separar a pauta do dia em evergreen pesquisável, tendência e experimento, respeitando o mix ~60/30/10 na semana.
- [ ] Para tendência: só aceitar se der para renderizar e postar em até 24 a 48 h, em vídeo de ~30 s.
- [ ] Para evergreen: escrever a pergunta de busca exata que vira título.
- [ ] Verificar se a pauta cabe em uma série existente; se 3 vídeos soltos do mesmo tema foram bem, propor série nova.
- [ ] Checar o calendário sazonal: tem data chegando? Agendar ressurreição dos vídeos antigos do tema.

### Agente de roteiro
- [ ] Primeira frase = pergunta ou fato mais surpreendente (sem saudação, sem logo).
- [ ] Texto de gancho na tela no 1º segundo, na zona segura.
- [ ] Uma revelação nova a cada 8 a 12 s nos vídeos de 60 a 90 s.
- [ ] Fim que emenda com o começo (loop) na fala e na imagem.
- [ ] Pergunta para comentário por volta de 80% do vídeo, do tipo "qual/o que/preferiria" ou palpite.
- [ ] Se for série: número do episódio, nenhum "como vimos antes", gancho de 2 s para o próximo sem pedir para seguir.
- [ ] Pensar "para quem a pessoa vai mandar isso?"; se não houver resposta, reforçar o ângulo social.
- [ ] Nada datado no áudio e no texto queimado dos evergreen.
- [ ] Easter egg visual (mascote escondido) quando couber.
- [ ] Gerar junto: título de busca, descrição com palavra-chave, até 3 hashtags no YouTube e até 5 no Instagram, texto do comentário fixado e texto da pergunta.

### Agentes de 3D / voz / edição
- [ ] Primeiro quadro funciona como capa (objeto grande, contraste, curiosidade).
- [ ] Câmera e pose do último quadro iguais às do primeiro (loop).
- [ ] Cenário base da série salvo como .blend reaproveitável.
- [ ] Renderizar o gancho (primeiros 2 a 3 s) como segmento separado, para que remake de abertura custe só alguns minutos de CPU.
- [ ] Aparar silêncio do TTS no começo e no fim.
- [ ] Exportar MP4 limpo, sem marca d'água.

### Agendamento / publicação (Metricool e APIs)
- [ ] YouTube: 2 por dia com intervalo de 4 a 6 h; Instagram: 1 por dia + Trial Reel quando disponível.
- [ ] No upload do YouTube: adicionar à playlist da série/tema e preencher o vídeo relacionado (regra da seção 4). Se o Metricool não fizer isso, rodar pela API do YouTube logo após a publicação.
- [ ] No Instagram: vincular ao episódio anterior (Reels vinculado). Se não der por ferramenta, entra na lista manual do dia.
- [ ] Publicar o comentário do canal com a pergunta/bônus logo após a publicação; avisar o Lucas para fixar (tarefa manual de 1 min).

### Agente de engajamento (diário e semanal)
- [ ] Coletar métricas em 1 h, 24 h, 48 h, 7 d e 30 d: exibido vs. deslizado, % médio assistido, envios/compartilhamentos, salvamentos, comentários e inscritos/seguidores ganhos por 1.000 views.
- [ ] Nas primeiras 2 h: responder (de forma específica e variada) os primeiros comentários e sugerir o melhor para virar fixado depois de 24 h.
- [ ] Com 48 a 72 h: classificar cada vídeo no protocolo de flop (seção 8) e gerar a ação.
- [ ] Toda semana: escolher o vídeo "locomotiva" (que mais cresceu) e apontar para ele o vídeo relacionado dos novos; criar continuação dele em até 7 dias.
- [ ] Toda semana: ler os comentários pedindo tema e transformar o mais pedido em episódio ("vocês pediram").
- [ ] Toda semana: atualizar a lista negra de temas que floparam 2 vezes e a lista de campeões para remake.
- [ ] Toda semana: trocar os vídeos fixados no topo do canal e do perfil.

### Rotina mensal (ressurreição)
- [ ] Vídeos com mais de 30 dias e boa retenção: retitular para busca, colocar em playlist, apontar relacionados novos para eles.
- [ ] Campeões com 60 a 90 dias: produzir remake com gancho novo (reaproveitando o .blend).
- [ ] Séries com 5 a 8 episódios: montar compilação longa por FFmpeg e ligar episódios e compilação (relacionado + descrição).
- [ ] Rever a frequência: se o engajamento por alcance no Instagram caiu 2 semanas seguidas, voltar para 1 por dia; se ficou estável, testar 2.

## 10. Métricas-alvo indicativas (para o agente saber se está bom)

São referências práticas do mercado, não números oficiais. Ajustar depois que o canal tiver um mês de dados próprios.
- Exibido (ficou para assistir) acima de 70%.
- Porcentagem média assistida acima de 80% nos vídeos de 30 s e acima de 50 a 60% nos de 60 a 90 s (acima de 100% significa que está havendo replay, o ideal).
- Envios/compartilhamentos: qualquer vídeo com compartilhamento por 1.000 views bem acima da média do canal é candidato a série.
- Comparar cada vídeo com a mediana dos últimos 14 vídeos do próprio canal, não com canais grandes.
