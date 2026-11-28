# 05 · Custo e uso (a parte mais importante)

`[CC]` = conferido em 2026-11-28/2.1.288 (comportamento em uso na origem; reconferir na documentação atual). Números são faixas observadas, sem identificar unidades; M = milhão de tokens. "est." = estimativa somada; "med." = medido em log/painel.

---
## a) Como mede contexto e uso

**Contexto — três fontes, em ordem de preferência**
1. **Linha de status** `[CC]`: o cliente chama um script a cada atualização, com JSON no stdin. Usa a porcentagem pronta da janela de contexto; na falta, soma tokens de entrada + criação de cache + leitura de cache da chamada atual ÷ tamanho da janela (não soma saída). Grava por sessão: `{pct, pasta, modelo, quando, avisado}`, teto de 60 sessões, gravação atômica, falha silenciosa. Mostra "contexto N%" e "hora de aposentar" ≥ 60%.
2. **Transcript** (usado pelos ganchos, que **não recebem % de contexto** `[CC]`): última mensagem do assistente da sessão principal (ignora mensagens de subagente) → soma entrada + criação de cache + leitura de cache + saída (= o que a próxima chamada reenvia) ÷ janela (padrão 1 M; calibrada). Lê só a cauda: blocos de 512 KB de trás para frente, até 16 MB (o arquivo passa de 10 MB num dia).
3. **Ferramenta de uso da sessão** `[CC]` (do app, não do gancho): devolve tokens usados, janela e %. Exata; usada para calibrar a janela.
- Precedência no gancho: linha de status se gravada há < 180 s; senão transcript.

**Uso do plano (janela de 5 h e semanal)**
- Fonte: a mesma ferramenta de uso `[CC]`, lista de janelas com rótulo e %. Reconhece "5 horas" e "semanal (todos os modelos)" pelo rótulo.
- Gravação: gancho pós-ferramenta assíncrono vê a chamada e grava `uso = {quando, cincoH, semanal}` + janela de contexto da sessão, sob trava.
- Frequência: **sob demanda** (só quando alguém consulta). Validade para decisão: 30 min; dado velho → a guarda nega e manda consultar.

**Limitações encontradas**
- Ganchos dependem de efeito colateral (transcript, pós-ferramenta) para saber contexto e uso.
- A linha de status só roda no terminal; no app de desktop o arquivo dela nem existe → transcript é a fonte real `[CC]`.
- Transcript atrasa ~1 turno. Conferência: transcript ~750 mil ≈ 75% de 1 M, coerente com a ferramenta.
- Depois da compactação a % cai → "1ª compactação" virou gatilho próprio (marcador gravado no início de sessão pós-compactação `[CC]`).
- Retomada agendada por suposição de horário falhou → agendar pelo horário de reset informado pelo erro ou pela ferramenta, com folga.

---
## b) Regras de decisão por uso e contexto

| Condição | Efeito | Quem aplica | Teste (prosa) |
|---|---|---|---|
| contexto < 60% | nada | — | 50% → sem instrução |
| ≥ 60% | instrução firme de aposentar em todo pedido e em todo uso de agente/edição; **não bloqueia** | gancho de pedido + pré-ferramenta (injeção) | 65% → instrução; criar agente passa com contexto |
| ≥ 70% ou após 1ª compactação | nega criar agente, abrir sessão, editar fora de handovers; segura o fim do turno (uma vez) até handover válido; shell e mensagens seguem livres | pré-ferramenta + fim de turno | 75% sem handover → negado; escrever handover passa; com handover libera |
| "adiar aposentar" | 60 min; só texto do dono | gancho de pedido | vindo de outra sessão → não vale |
| 5 h < 50% **e** semanal < 80% | até 2 unidades em paralelo | gancho em criação de executor | 2º executor com uso 40/60 → passa |
| acima disso | 1 por vez | idem | 5 h = 64% → nega "1 por vez" |
| 1 executor de outra unidade ativo e sem consulta de uso em 30 min | nega: "consulte o uso e repita" | idem | sem consulta → nega |
| ≥ 2 executores ativos | **pergunta** (não nega: registro velho pode contar a mais) | idem | 3º → pergunta |
| 5 h ≥ 85% | etapa pesada nova (bancada, QA) só com OK | texto | — |
| mesma unidade (rodada de correção) | passa | gancho | — |

- Parâmetros (arquivo de configuração, sobrescreve padrões do código): `contexto.{instruir 60, bloquear 70, janela 1M, adiar_min 60}`, `paralelismo.{max 2, executor_ativo_h 2, cinco_h 50, semanal 80, validade_min 30}`, `entregas.teto_dia 2`.
- Meta semanal (só texto): ~20% do semanal por dia útil, sem teto seco (sobra passa adiante); não parar entrega quase pronta; defeito urgente passa por cima; avisar se a projeção estourar.
- Um gerente ativo por frente (2º gerente dobra o gasto) — guarda pergunta.

---
## c) Política de modelo por papel

| Camada (mapa atual `[CC]`) | Uso |
|---|---|
| forte (Opus) | **padrão** de todo agente e verificador |
| intermediário (Sonnet) | só tarefa mecânica: formatar, extrair, contar, rodar exemplos, relatório em modelo, **QA de regressão pura**; juiz do eval |
| topo (Fable) | só perguntando antes; exceção: assento cético do júri (pré-aprovado) |
| menor (Haiku) | **nunca**; exceção: assento prático do júri |
- Agentes embutidos de busca/guia caem no modelo menor por padrão `[CC]` → guarda nega a chamada sem modelo explícito.
- Aplicação: gancho pré-criação de agente (nega menor fora do júri e embutido sem modelo; pergunta topo fora do júri). "Intermediário só se simples" é julgamento → **sem guarda**.
- **Custo do júri misto:** ~80–90 mil tokens e ~2 min por jurado → **0,4–0,6 M por júri**; via moderador **0,6–0,8 M** e 15–20 min (moderador sozinho ~230 mil, ~50 chamadas, ~15 min no 1º uso). Proposto e não aplicado: moderador com teto de 25 chamadas antes de enquadrar, 8 min, e reuso da evidência de júri anterior da mesma unidade.

---
## d) O que cada trilha corta e quanto custa

| Trilha | Corta (vs. T2) | Custo |
|---|---|---|
| T0 | proposta, eficiência, testes, verificação, sucessor | < 50 mil (est.), dentro da sessão aberta |
| T1 | proposta completa, revisor, moderador, rodadas além de 1, bancada (salvo gatilho) | 0,5–1 M (est.: executor 150–300 mil + 1–2 QAs 130–290 mil + pré-voo) |
| T2 | — (referência) | 2,5–4 M (est.: planejador + executor + R1 com 3 verificadores + moderador + regressões) |
| T3 | nada; acrescenta contrato, eficiência por etapa, bancada ×3 | executor chegou a ~0,9 M em 7 rodadas (med.); bancada externa ~3–4× a de T2 (med.); + ~0,6 M por júri |

---
## e) Ordens de grandeza observadas

| Item | Faixa |
|---|---|
| Planejador | 0,35–0,43 M |
| Executor reaproveitado por 6–7 rodadas | até ~0,9 M (cresce a cada rodada) |
| QA / revisor, cada | 0,13–0,29 M |
| Jurado | 0,08–0,09 M |
| Gerente de frente | ~50% de contexto após ~1,5 entregas |
| Rodadas por unidade (T2/T3) | 3–5 (R1 + 2–4 regressões). Achados R1: 10–20 típicos (pico 23); R2: 0–2; R3: 0–1 |
| Pré-voo da própria entrega | 0–2 achados |
| Resposta de rastreador sem filtro de campos | ~12 mil por chamada |
| Uso do plano | dia com 2 unidades em paralelo ≈ 29 pontos do semanal; semana pesada ≈ 78% |
| Abrir sessão nova (leitura inicial) | **não medido**; estimativa de bastidor: dezenas a poucas centenas de mil |
| Sucessor aberto à toa | uma leitura inicial inteira para trabalho de minutos (caso: 2 linhas de doc + anúncio) |
| Troca de gerente no meio da verificação | ~10 chamadas extras para formalizar opinião dada só em chat |

---
## f) Linter de orçamento de contexto

Contagem estática (sem tokenizar), sai com erro se passar: **constituição ≤ 200 linhas · cada skill ≤ 300 · cada agente ≤ 120 · cada descrição ≤ 1024 caracteres**. Soma das descrições ÷ 4 ≈ tokens por turno gastos na listagem. Também acusa descrição ausente e descrição com ": " sem aspas (quebra o YAML e o validador do plugin não acusa `[CC]`). Observado: constituição ~110–135 linhas, maior skill ~220, maior agente ~50, descrições ≤ ~720 caracteres.

---
## g) Gasto à toa e como foi cortado

1. Decisão miúda virava volta inteira dono↔orquestrador↔gerente (~14/dia: "rodo regressão?") → pergunta da regressão junto da aprovação das correções, com teto por trilha.
2. Executor reaproveitado em todas as rodadas (~0,9 M) → executor **novo** com brief curto por rodada; regressão pura = 1 QA intermediário com brief-modelo, sem moderador nem revisor.
3. Pré-voo re-rodado em mudança só de doc → guarda nega 2º pré-voo da mesma entrega salvo "código mudou"; T0 = busca.
4. Sucessor aberto para 2 linhas → terminar o que está no fim antes de aposentar; T0 com gerente vivo.
5. Moderador com 1 verificador → sem moderador; brief só com caminhos.
6. Dois gerentes na mesma frente → um ativo por vez.
7. Despacho periódico a cada 10 min → só ao fim das 3 rotinas diárias ou sob pedido; guarda nega religar.
8. Listar transições/ids do rastreador a cada movimento → ids fixos; sempre pedir campos curtos.
9. Mensagens de status entre sessões acordando aposentados → guarda (só decisão/bloqueio/entrega).
10. Proposta (~80 KB) relida várias vezes porque a pesquisa que a decisão exigia chegou depois → pesquisas rodam junto do planejador.
11. Bancada e exemplos em várias passadas → uma passada por unidade, no fim.
12. Propostos, não aplicados: bloco "achados em 1 linha" no topo de relatórios longos (~370 linhas); painel ao vivo com 1 chamada por evento em vez de 2; teto do moderador; ambiente de bancada fixo.

---
## h) O que não foi medido bem (fazer melhor no destino)

- Tokens por papel foram anotados à mão; **coletar automaticamente** por subagente (o gancho de fim de subagente pode somar o uso do transcript do subagente).
- Custo de abrir sessão nova e de sucessor: sem número. Medir a leitura inicial com a mesma soma do transcript após o 1º turno.
- Uso do plano: só o último ponto é guardado → manter **série temporal** e projeção semanal com alerta.
- A série de métricas mistura %, tokens, segundos e contagens num só arquivo → separar custo de qualidade.
- Júri: 1–2 amostras. Custos por trilha T0/T1 são só estimativas.
- Política "intermediário só em tarefa simples" não tem verificação.
- Eval de comportamento e diagnóstico interativo quase nunca rodaram (custam tokens / exigem o dono).
