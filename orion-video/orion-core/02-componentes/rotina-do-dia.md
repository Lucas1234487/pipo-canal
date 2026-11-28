# Modelo · Rotina do dia (skill da coordenadora que renasce)

- **Papel:** montar o dia do dono a partir de arquivos: handover de ontem + leituras frescas das fontes → quadro → briefing.
- **Acionada:** saudação de início de dia, "o que tenho hoje", "me atualiza", ou tarefa agendada em {{HORARIOS_DAS_ROTINAS}} (agendada só lê e grava estado próprio; travaria em permissão `[CC 2026-11-28/2.1.288]`).

## Passos
1. Contexto mínimo: data, handover mais recente, resumo do quadro. Nunca reler transcrições.
2. Período = desde a última rotina (início da semana pega o fim de semana).
3. Disparar **um leitor por fonte numa única mensagem** ({{FONTES}}), com brief fixo: fonte, roteiro, período, data, caminhos de saída md/json, caminho do quadro.
4. Consolidar: primeiro o script mecânico; depois só os `.json` para julgamento. Item aberto que sumiu da fonte → "verificar", nunca fechar. Escolha do dono → fila de decisões.
5. Briefing em `{{PASTA_DE_ESTADO}}/briefings/<data>.md`, nesta ordem: agenda · precisa de você agora (≤ 5, com porquê) · decisões abertas (recomendação primeiro) · quem espera resposta · o que mudou · riscos · plano em 3 blocos · o que não foi lido.
6. Responder ao dono em ≤ 25 linhas: itens 1–4 + primeira decisão.

- **Entrada:** nenhuma além do estado.
- **Saída:** briefing + quadro atualizado + resposta curta.
- **Nunca:** escrever em fonte; fechar item sozinho; citar o que está em "não é comigo".
- **Pronto:** briefing gravado, falhas de leitura listadas em "não lido".
- **Modelo:** leitores em {{MODELO_PADRAO}} (julgam relevância e conferem estado).
- **Custo:** N leitores × leitura de fonte; a coordenadora fica pequena porque só lê caminhos e JSON.
- **Placeholders:** {{FONTES}}, {{HORARIOS_DAS_ROTINAS}}, {{FILTRO_DE_RELEVANCIA}} (ex.: "o dono ganha, participa ou é pedido a ele"), {{ARQUIVO_IGNORADOS}}.
