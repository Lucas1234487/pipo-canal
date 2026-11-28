# 07 · Mapa peça → função

Destino: **E** exportada (modelo em 02) · **A** adaptável (exportar o princípio, refazer por domínio) · **D** descartada (ver 08). Nomes das peças já generalizados.

| Peça de origem | Função abstrata | O que muda por domínio | Destino |
|---|---|---|---|
| constituição da coordenadora | regras inegociáveis, roteamento de pedidos, política de modelo, limites | regras do domínio, limites, idioma | E → `02/constituicao.md` |
| rotina de início do dia | renascer: ler handover, leitores em paralelo, consolidar, briefing | fontes, horários, filtros | E → `02/rotina-do-dia.md` |
| leitor de fonte | ler 1 fonte, gravar digest md+json, só leitura | conectores e esquema por fonte | E → `02/leitor-de-fontes.md` |
| roteiros por fonte (rastreador, chat, e-mail/agenda, código) | o que cobrir e esquema de cada fonte | inteiro | A (exemplo no modelo do leitor) |
| gerente de frente | dono do contexto; conduz unidades; briefs; leva só decisões | frente, repositório, teto | E → `02/gerente-de-frente.md` |
| pipeline da unidade | etapas, trilhas T0–T3, gates, parada | etapas de domínio, gate, evidências | E → `02/pipeline-unidade.md` |
| planejador | proposta: contratos, testes com bordas primeiro, decisões A/B | formato de contrato, critério de qualidade | E → `02/planejador.md` |
| executor | implementa até o gate verde | comando de gate, padrão de versionamento | E → `02/executor.md` |
| crítico de eficiência | crítica só-leitura do plano e do diff | critérios em ordem de peso | E → `02/critico-eficiencia.md` |
| QA independente | verificador novo por rodada; 1ª explora | ambientes, evidências | E → `02/verificador.md` |
| revisor de código | 2º verificador com critério de código | checklist | A (variante do verificador) |
| verificador de contrato com cliente | 3º verificador quando muda contrato | consumidores do contrato | A (variante do verificador) |
| moderador | enquadra contestação, roda júri, consolida verificação, não decide | pasta, siglas permitidas | E → `02/moderador-juri.md` |
| júri padrão | 5 assentos, voto cego, calibração | personas de domínio | E → `02/moderador-juri.md` |
| criador | tarefa sem dono → novo agente/skill validado, sem adotar | catálogo | E → `02/criador.md` |
| melhorias | retro semanal, fila de propostas, base de lições | cadência | E → `02/retro-melhorias.md` |
| validar | "doctor": validação estrita, testes, orçamento, eval | comandos | E → `02/validador.md` |
| aposentar | gatilhos, handover, sucessão | limiares | E → `02/aposentadoria-handover.md` |
| quadro (skill + script) | estado em arquivo com trava e pré-condições | status e entidades | E → `02/quadro-de-estado.md` |
| base de lições (script) | adicionar/reincidiu/garantir/verificar/limpar | — | E → `02/quadro-de-estado.md` + 03 |
| consolidador | fonte à frente vence; ignorados não entram | mapa de status externo | E (descrito em 03 §4) |
| guarda de política | modelo, saída externa, produção, banco | listas de ferramentas, marcadores | E → 03 |
| guarda de disciplina | aposentadoria, mensagens, paralelismo, gerente único, agendas, ignorados, publicação | limiares | E → 03 |
| registro de agentes ao vivo | telemetria de subagentes + injeção no início de sessão | — | só a injeção E; resto D |
| linha de status | mede contexto | — | E → 05 §a |
| linter de orçamento | limites de tamanho | limites | E → 05 §f |
| evals | comportamento de skills de texto | casos | E → 03 §5 |
| guardas de git/entrega/rastreador/navegador | — | — | D (só princípio, 03 §2) |
| painel móvel, despacho, sincronização do painel, painel ao vivo, histórico motivacional | visualização e atendimento pelo celular | — | D (1 linha de conceito em 08) |
| revisão de entrega alheia, resposta a revisão, revisor de entrega | — | — | D |
| analisador estático de terceiros (pré-voo e correção) | — | — | D |
| relatório da entrega, demo quinzenal, status do dia, interpessoal | — | — | D |
| revisão de UX (skill e agente), integração com front | — | — | D |
| criação de unidades no rastreador (skill e agente) | — | — | D |
| tarefas agendadas | disparar rotinas | horários | A (04 §2) |
| memória de agente por papel | aprendizado do papel | conteúdo | A (estrutura só) |
| regras de processo dos repositórios de trabalho | passo 1, proposta, gate, QA, fechamento | comandos e estilo | A (04 §6; modelo em `02/constituicao.md`) |
