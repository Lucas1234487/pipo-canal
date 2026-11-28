# Órion de Vídeo: Fase A (diagnóstico e plano) — 28/11/2026

## 0. Situação agora (urgente)
- Produção de 28/11 (03:37) e vigia das 09:23 **falharam por limite de uso** ("USAGE_LIMIT_REACHED"). Em 26/11 a produção estourou a janela de 5 h 3 vezes e só terminou às 20:30.
- Causa medida (handover 0009): ~25 agentes por dia, todos no modelo mais caro (Opus 5.5 nas 3 tarefas), 10 em paralelo, cada um com 100 a 190 mil tokens. Ordem de grandeza: 3 a 5 milhões de tokens por dia de produção. Somado à sessão de configuração (esta conversa, enorme), o semanal provavelmente acabou.
- Automação usa a assinatura (ANTHROPIC_API_KEY não está definida). Não consigo ler o indicador de uso daqui (sem /usage na nuvem): a medição precisa de prints seus (Parte B, 2).

## 1. Inventário (resumo)
| Item | Hoje |
|---|---|
| Onde roda | 3 tarefas na nuvem: produção 03:37, vigia 09:23/15:23/20:23, semanal dom 21:47; todas Opus 5.5 |
| Posse | produção lê ~20 docs, **~105 KB (~26 mil tokens)** antes de começar; cada agente filho relê spec + guardrails (~5–10 mil) |
| Sessões/dia | 1 produção + 3 vigias + agentes: ~25 contextos/dia |
| Vigia | relê ~8 docs mesmo quando não há nada a fazer |
| Já é script | tts, render2d, compose, qa_check, guardrails, dados, buffer, gemini |
| Depende do modelo | pauta, roteiro.json, cenas.json, meta, correções, comentários, decisões |
| Retrabalho | 3/3 vídeos de 26/11 tiveram CORRIGE no QA-Claude (1 rodada cada) |
| Divergências de skills | pipo-pesquisa e pipo-revisao (3D, 2 vídeos/dia): aposentar; pipo-producao (2/dia): atualizar ou aposentar; pipo-publicacao (Studio direto): atualizar para a cadeia Metricool -> Buffer -> Chrome; pipo-diretor: atualização já proposta |

## 2. Mapa Órion x Pipo
| Peça do Órion | Decisão | Por quê / ganho |
|---|---|---|
| Orquestrador que renasce com estado compacto | ADAPTAR: `ESTADO.md` gerado por script (~2–3 mil tokens) | corta ~20 mil tokens por sessão |
| Dividir por contexto, não por papel | ADOTAR: **1 produtor por vídeo** (faz O1–O4 com os scripts) | O2/O3/O4 são quase só JSON + scripts; hoje 5 contextos por vídeo |
| Verificador independente novo | MANTER QA-Gemini + qa_check + guardrails sempre; QA-Claude **por gatilho** | Gemini fica fora do limite do Claude |
| Trilhas por risco | ADAPTAR: V0 recorrente seguro, V1 normal, V2 formato/tema novo ou sensível; sobe sozinha | menos etapas no que já funciona |
| Guardas determinísticas | AMPLIAR: script de agendar recusa sem guardrails=0 e sem relatório do Gemini; `tem_trabalho.py` para a vigia | falha fechada, sem gastar modelo |
| Controle de uso | ADOTAR: teto de agentes por dia, sem paralelismo, pausa com reserva da fila | evita parar o dia inteiro |
| Lições com "reincidiu" | ADAPTAR nos cadernos | erro não se repete |
| Júri | DESCARTAR por ora (0,4–0,8 M por júri); se precisar, Gemini como juiz de outra família | caro |
| Linter de orçamento | ADOTAR (docs que entram na posse com teto) | posse não engorda de novo |

## 3. Matriz de modelos (a confirmar com bancada)
| Etapa | Hoje | Proposta | Validador que segura a qualidade |
|---|---|---|---|
| G1 pautas | Opus + Gemini | Gemini com busca; Claude só escolhe | — |
| G2 roteiro (gancho, humor) | Opus | **Opus** (gosto) | 5 perguntas + plateia Gemini |
| G3 cenas/som/montagem | Opus (4 agentes) | **Sonnet**, 1 agente | qa_check, guardrails, schema |
| G4 portão | Gemini + QA-Claude Opus | Gemini sempre; QA-Claude Sonnet por gatilho | qa_check |
| G5 publicação | Opus | script + Sonnet | buffer.py, guardrails |
| G6 métricas | Opus | script + Sonnet | dados.py |
| Comentários | Opus | Gemini rascunha, Sonnet revisa, 1 lote/dia no Chrome | lista de proibidos |
| Vigia | Opus x3 | Sonnet x1 (20:23) + saída cedo se nada a fazer | tem_trabalho.py |
| Semanal | Opus | Gemini pesquisa; Opus só decide | — |

## 4. Caminhos
| | 1. Atual com cortes | 2. Enxuta (recomendada) | 3. Em lote |
|---|---|---|---|
| Contextos/dia | ~12 | **~5** (diretor + 3 produtores + 1 vigia) | ~3 |
| Uso estimado | 25–35%/dia | **8–14%/dia** (a medir) | 6–10%/dia |
| Risco de qualidade | baixo | médio-baixo (QA-Gemini e scripts seguram) | médio (contexto cresce no lote) |
| Esforço | baixo | médio (2–3 sessões) | médio-alto |
Recomendo o 2: chega na sua meta de 10–12% e mantém os portões. Mudaria de ideia se a bancada mostrar o Sonnet reprovando 2x mais no QA, ou se a medição mostrar que o 2 ainda passa de 12%.

## 4b. Melhora contínua e dados continuam (pedido do Lucas)
Nada disso some; só fica mais barato: coleta de métricas e dados.py viram script (zero modelo); análise semanal e mensal seguem, com o Gemini fazendo a pesquisa ampla e o Opus só decidindo as mudanças; carteira seguro/ousado/evolução, 5 perguntas, detector de estagnação e "tudo vira dado" ficam iguais. Ganho extra: o custo de cada vídeo passa a ser dado também (para saber o que rende mais por % de uso).

## 5. Implementação (cada etapa reversível)
1. **Emergência (agora, com seu OK):** vigia passa a 1x/dia (20:23) no Sonnet; produção sem paralelismo e com O2+O3+O4 num agente Sonnet (o "modo enxuto A" que o Diretor já propôs). Reverter = voltar o prompt.
2. `ESTADO.md` por script + posse curta (só ESTADO + spec do papel). Teste: posse < 5 mil tokens.
3. `tem_trabalho.py` + agendar com falha fechada. Teste: rodar sem relatório do Gemini = recusa.
4. Produtor único por vídeo no C (menor risco) por 3 dias, comparando nota do Gemini, retrabalho e uso; vira padrão se empatar ou melhorar.
5. QA-Claude por gatilho; comentários via Gemini; semanal com pesquisa no Gemini.
6. Linter de orçamento e regra de pausa.

## Parte B — Precisa de você
1. **Emergência:** o canal parou hoje por falta de limite. Recomendo aplicar já a etapa 1 do item 5 (vigia 1x/dia no Sonnet e produção enxuta). Outras opções: esperar a semana virar sem mudar nada; ou reduzir para 2 vídeos/dia até a Fase B. **Recomendo aplicar a etapa 1.**
2. **Medição:** mande prints de Configurações > Uso agora e amanhã às 08:00 (depois da produção). Sem isso eu só estimo. Também me diga em que dia/hora o semanal reinicia.
3. **Esta conversa:** ela está enorme e cada mensagem aqui gasta muito. Recomendo continuar a Fase B numa conversa nova, que começa lendo este PLANO.md.
4. **Skills:** posso aposentar pipo-pesquisa e pipo-revisao e atualizar pipo-producao e pipo-publicacao (cartões para você salvar)?
