# Modelo · Validador, o "doctor" (skill)

- **Papel:** validar o plugin e cada peça depois de mudar skill, agente, gancho ou constituição.
- **Acionado:** após criar/mudar peça; "valida", "confere se está certo".
- **Passos (1–3 numa só mensagem):**
  1. Validação estrutural estrita do plugin e do catálogo, zero avisos (`{{COMANDO_VALIDAR_PLUGIN}}`) `[CC 2026-11-28/2.1.288]`.
  2. Todas as suítes de teste das guardas e do estado; todos os casos passam.
  3. Linter de orçamento: constituição ≤ 200 linhas · skill ≤ 300 · agente ≤ 120 · descrição ≤ 1024 caracteres (05 §f).
  4. Comportamento (custa tokens — **perguntar antes**): eval do plugin com juiz {{MODELO_MECANICO}}, sem publicar, 1 rodada, limiar {{LIMIAR_EVAL}} (origem 0,7). O padrão da ferramenta usa juiz menor e publica — sobrescrever `[CC 2026-11-28/2.1.288]`.
  5. Diagnóstico interativo: o dono roda e cola o resultado.
  6. Gravar `{{PASTA_DE_ESTADO}}/validacoes/<data>.md` com resultado e correções propostas.
- **Saída:** relatório de validação + resposta curta com o que falhou.
- **Nunca:** corrigir regra de repositório de trabalho (só o que é do sistema).
- **Pronto:** passos 1–3 limpos; 4–5 rodados ou registrados como não rodados.
- **Modelo:** o da sessão; tudo é shell.
- **Custo:** 1–3 quase zero; 4 custa uma execução de eval por caso.
- **Placeholders:** {{COMANDO_VALIDAR_PLUGIN}}, {{SUITES}}, {{LIMIAR_EVAL}}, limites do orçamento.
