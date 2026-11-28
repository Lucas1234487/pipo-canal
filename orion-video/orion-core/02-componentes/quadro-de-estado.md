# Modelo · Quadro de estado e base de lições (skill + script CLI)

- **Papel:** contrato único de leitura/escrita do estado. Um script CLI com trava de arquivo e gravação atômica; ninguém edita JSON à mão.
- **Acionado:** sempre que registrar progresso, pendência, promessa, decisão, abertura/aposentadoria de sessão, métrica, lição.
- **Entidades:** item · decisão · sessão · métrica · ramo criado pelo sistema · registro de verificação · lista "não é comigo" · lição (modelos em 03 §4).
- **Status de item ({{STATUS}}):** novo, lendo, passo1, proposta, aguardando-aprovacao, implementando, verificando, analise, corrigindo, evidencias, plano-de-entrega, empacotando, relatorio, entrega-aberta, em-revisao + bloqueado, verificar, feito, nao-e-comigo. "Precisa do dono": passo1, aguardando-aprovacao, analise, plano-de-entrega, bloqueado, verificar.

## Comandos (por função)
- `resumo [--frente]` · `listar [filtros]` · `upsert <chave> [campos] [--nota] [--conferido]` · `fechar <chave>`
- `decisao-add` (pergunta, opções "a) …|b) …", recomendação, frente, origem, prazo → id) · `decisao-resolver --id --escolha [--unidade]` (grava no arquivo de decisões da unidade; se cita outra unidade, anota nas entradas dela)
- `sessao` (id, frente, título, ativo|aposentando|aposentado, handover) · `metrica` · `ramo` · `verificacao` (exige selo de qualidade) · `aprovacao --chave --resposta permitir|negar` · `nao-e-comigo` / `reabrir`
- Lições: `adicionar` · `reincidiu` · `garantir --onde --teste` · `aposentar` · `resumo --max 12` · `verificar` · `limpar --dias 30` · `listar`

## Pré-condições (falham fechadas)
- Recusa regredir item ("falta entrega", etapa anterior) se o quadro ou a fonte remota já mostram avanço, salvo `--conferido`.
- Recusa verificação sem selo; decisão ou item inexistente; resposta de aprovação fora de permitir|negar.

## Regras
- Responder "onde paramos?" do `resumo`, nunca da memória. `--proxima` é uma ação curta.
- Sem segredo, e-mail ou telefone no estado. Pendência inativa > 14 dias expira. Lições aposentadas > 30 dias vão a arquivo morto.
- Raiz do estado por variável de ambiente (testes usam pasta temporária).

- **Saída:** JSON atualizado + linha de resultado; `resumo` em texto curto (abertos por status, precisa do dono ≤ 12, decisões ≤ 12, sessões ativas, métricas).
- **Pronto:** escrita aceita (exit 0).
- **Modelo:** nenhum (script). **Custo:** quase zero; o ganho é não reler conversa.
- **Placeholders:** {{PASTA_DE_ESTADO}}, {{STATUS}}, {{CHAVES_ESTAVEIS}}, {{CONSULTA_REMOTA}}.
