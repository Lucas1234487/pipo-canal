# Arquitetura do PipoPop (atualizada 26/11/2026)

## Pessoas e papéis
- Lucas: dono. Só veta e decide o que é drástico (DECISOES_LUCAS.md). Passa no chat nos fins de semana.
- Diretor (PO, dono do negócio no dia a dia): escolhe pautas, aprova roteiro, cuida das 3 redes, dados e crescimento. Se aposenta a cada ciclo com handover.
- Gerente de Produção (1 por vídeo) -> Organizadores O1 Roteiro e Fala, O2 Cenário, O3 Sonoplastia, O4 Montagem.
- QA final: QA-Claude (agente novo a cada vídeo) + QA-Gemini (API) + portão determinístico kit/guardrails.py.
Cada papel tem spec (docs/sistema/specs/) e caderno (docs/diretor/cadernos/). Passagem de bastão: docs/diretor/APOSENTADORIA.md.

## Fluxo de um dia
1. 03:37 Produção: posse (lê specs + último handover) -> pautas (G1, PAUTAS.md, pedidos do Lucas primeiro) -> carteira do dia (seguro / ousado / evolução) -> por vídeo: Gerente -> O1..O4 -> QA-Claude + QA-Gemini -> guardrails.py -> fila (branch `fila`) -> dados/videos.jsonl -> agendamento nas 3 redes no mesmo horário -> stories -> handover.
2. 09:23 / 15:23 / 20:23 Vigia: confere se faltou vídeo (produz se precisar, com trava), se algum post falhou (cadeia de fallback), comentários (quando o Chrome do Lucas está aberto), e às 20:23 coleta métricas (24h/72h/7d).
3. Domingo 21:47 Semanal: comentários da semana, dados (tabela + análise; no 1º domingo do mês, análise profunda), pesquisa ampla, pautas, boletim por papel, mudanças aplicadas, mensagem ao Lucas.

## Publicação (05_CONTINUIDADE)
Para cada rede: 1) Metricool (marca 8272438; grátis = 20 posts/mês somando redes) -> 2) Buffer (grátis, 3 canais, até 10 na fila por canal; sem primeiro comentário) -> 3) Claude in Chrome (Studio / Meta Business Suite; só com o PC do Lucas ligado). Primeiro comentário que faltou vai para docs/diretor/redes/comentarios_pendentes.json e é feito na próxima sessão com Chrome.

## Dados (07_DADOS)
O que fizemos (dados/videos.jsonl) + onde postamos (posts.jsonl) + o que aconteceu (metricas.jsonl, por vídeo x rede x janela 24h/72h/7d/30d, e total). kit/dados.py gera a tabela e a análise. Decisões de crescimento (06_CRESCIMENTO) usam esses dados; mudança grande só quando o padrão se repete.

## Memória
- Permanente: specs, GUARDRAILS, 03..07, BASE_CONHECIMENTO.md.
- Por papel: cadernos (~40 linhas).
- Por ciclo: handovers (curtos), bilhetes dos agentes em docs/diretor/ciclos/.
- Do negócio: PLACAR, EXPERIMENTOS, MELHORIAS, DECISOES_LUCAS, boletins, análises, pedidos_lucas/.

## Por que é assim
Contexto cheio deixa agente burro: cada um começa vazio e lê só o seu pedaço, mas tudo que importa está escrito no git. O canal não pode parar por ferramenta caída nem por falta de decisão do Lucas: sempre existe um próximo caminho. E o que decide o rumo é o dado, não o gosto.
