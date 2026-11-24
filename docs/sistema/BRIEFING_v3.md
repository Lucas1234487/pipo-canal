# Briefing v3 (24/11/2026, palavras e decisões do Lucas). Vale sempre, sem exceção.

Este briefing tem precedência sobre 01_ORGANOGRAMA, 03_CICLO e as specs onde houver conflito. Ele não muda a personalidade do Diretor (docs/diretor/BRIEFING_DIRETOR.md).

## 1. O Diretor é o guardião
O Diretor existe para decidir quando o Lucas não está. Ele tem o olhar do canal: escolhe as pautas, cobra qualidade, decide o que melhora e protege os guardrails. Ele não segue o padrão no automático: a cada ciclo ele olha o que o público respondeu (PLACAR, métricas, comentários) e muda alguma coisa de propósito (seção 6).

## 2. A estrutura, todo dia, para todo vídeo
```
Diretor
 └─ Gerente de Produção (1 por vídeo: M momento, H história, C conhecimento)
     ├─ O1 Roteiro e Fala   (roteiro.json, fatos.md com 2 fontes, voz e pronúncia)
     ├─ O2 Cenário          (cenas.json: cenários, personagens, interação com o fundo, imagens reais)
     ├─ O3 Sonoplastia      (música, efeitos, silêncios, mixagem; som que intriga)
     └─ O4 Montagem         (render, compose, upload.mp4, meta.json, folha de prévia)
 └─ QA final (só com o vídeo pronto, nunca por etapa)
     ├─ QA-Claude: agente NOVO, que não participou do vídeo; revisão técnica e de conteúdo
     └─ QA-Gemini: assiste ao MP4 com som (plateia + passada de pronúncia)
 └─ Lucas aprova  ->  só então vai para agendamento
```
- Os organizadores são agentes (ferramenta Agent) contratados pelo gerente. Cada um tem a sua spec em docs/sistema/specs/O1..O4 e usa os scripts do kit e o Gemini como ferramentas.
- O1 vem primeiro. O2 e O3 trabalham em paralelo a partir do roteiro e do timing. O4 junta tudo por último.
- O gerente confere cada entrega e devolve ao Diretor 15 linhas + arquivos.
- Pesquisa (G1), publicação (G5) e métricas (G6) seguem como gerentes próprios.

## 3. Aprovação do Lucas (substitui "publicar sem mostrar")
- Nenhum vídeo é agendado sem o OK do Lucas.
- Depois do QA, o Diretor manda os vídeos ao Lucas (SendUserFile) com 3 linhas por vídeo: tema, nota do Gemini, o que o QA-Claude apontou.
- O vídeo fica em fila/AAAA-MM-DD_X/ sem aprovado_lucas.json. Quando o Lucas aprovar na conversa, a sessão grava aprovado_lucas.json (data, comentário dele) e dá push. Se ele pedir mudança, a sessão corrige e manda de novo.
- A publicação em lote só agenda pastas com aprovado_lucas.json.

## 4. O que o Lucas quer ver nos vídeos
- Três pilares por dia: assunto do momento, história com regra inventada (ligada a quem assiste: mãe, filho, namorada, trabalho) e conhecimento (como o ossinho de dinossauro).
- Roteiros complexos no sentido de interessantes: gancho forte, virada, sentimento, baseados nas pesquisas (docs/diretor/RESGATE_PESQUISA.md, docs/pesquisa/ pela seção indicada).
- Sonoplastia intrigante: clima que muda com a história, efeito em cada entrada, silêncio antes da virada.
- Fundos mais ricos e personagens que interagem com o fundo (backlog em specs/G3).
- Imagens reais da internet em alguns vídeos (não em todos): só CC0 ou domínio público, via kit/imagens.py (Openverse, NASA), com crédito e proveniência. Nunca pessoa real identificável, marca, obra de arte, filme, jogo ou esporte licenciado.
- Transições rápidas, a Pipo estoura em todo vídeo, a Pipo feminina.
- Voz que fala só português (Francisca/Antonio).

## 5. Memória: ninguém começa do zero
- Todo agente termina com um BILHETE (10 linhas) em WORK/bilhetes/<papel>.md: o que fez, o que deu errado, 1 lição.
- Cada papel tem um caderno em docs/diretor/cadernos/<papel>.md. O agente lê o caderno do seu papel antes de começar e acrescenta 1 lição datada no fim (máx. 3 linhas). O Diretor enxuga os cadernos uma vez por semana.
- O Diretor consolida os bilhetes no handover do dia (docs/diretor/handovers/) e se aposenta (docs/diretor/APOSENTADORIA.md). Tudo vai para o git com push.

## 6. Inteligência: melhorar de propósito
- Todo dia o Diretor lê o PLACAR (views 24 h, retenção quando houver, comentários) e escolhe até 2 experimentos pequenos para o lote do dia (ex.: gancho com número vs. com pergunta; foto real vs. só desenho; história à noite vs. à tarde).
- Cada experimento vai para docs/diretor/EXPERIMENTOS.md: hipótese, vídeo(s), o que medir, data de checar. Na data, escreve o resultado e o que muda.
- O que funcionou vira regra na spec do papel (com data). O que não funcionou também fica escrito, para ninguém repetir.
- A nota do Lucas pesa mais que a do Gemini. A do Gemini é generosa (desconte cerca de 2 pontos).

## 7. Custo
O Lucas liberou mais agentes porque o fluxo 2D ficou barato. Mesmo assim: briefings curtos com caminhos de arquivo, entregas de 15 linhas, 1 folha de prévia por vídeo, Gemini para volume. Um dia normal tem 3 gerentes + 12 organizadores + 3 QA-Claude.
