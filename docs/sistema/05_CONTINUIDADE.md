# 05. Continuidade: o canal não para (pedido do Lucas, 26/11)

Princípio: o dia a dia NUNCA para por falta de decisão do Lucas ou por uma ferramenta caída. O Diretor é o PO: decide, aplica e registra. Só decisão drástica para o negócio vai para docs/diretor/DECISOES_LUCAS.md, e mesmo assim o dia segue com a alternativa mais segura até ele responder.

## Portão determinístico
`python3 kit/guardrails.py <pasta>` antes de QUALQUER agendamento (qualquer rede, qualquer caminho). Saída 1 = não agenda; corrige pelo organizador certo ou usa a reserva. `--todas fila/` confere tudo que está pendente.

## Rotina e redes de segurança (tarefas agendadas)
| Hora | Tarefa | Papel |
|---|---|---|
| 03:37 | Produção diária | principal: produz, aprova e agenda os 3 do dia |
| 08:41 | Publicação em lote | rede 1: agenda o que ficou sem agendar, confere status, comentários |
| 09:23, 15:23, 20:23 | Vigia (sync + fallback) | rede 2: confere tudo; se algo falhou, aciona o próximo caminho |
| dom 21:47 | Semanal | melhora contínua |

Trava contra trabalho duplicado: quem começa a produzir grava `fila/_trava_producao.json` ({"inicio": ISO, "sessao": ...}). Outra sessão só produz se a trava não existe ou tem mais de 5 h. Ao terminar, apaga a trava.

## Cadeia de fallback
Produção:
1. Produção das 03:37.
2. Vigia: se às 09:23 faltar pilar do dia na fila e não houver trava válida, o Vigia produz o pilar que falta (mesma hierarquia, mesmo portão), começando pelo próximo horário.
3. Sem tempo para o horário: o vídeo vai para o próximo slot livre; nunca pula o dia inteiro. Reserva: pauta já pronta mais simples (C de curiosidade curta).

Publicação (para cada rede, em ordem):
1. Metricool (createScheduledPost). Atenção ao LIMITE do plano (ver abaixo).
2. API direta da plataforma (YouTube Data API v3; Meta Graph API para Instagram e página do Facebook), com tokens no arquivo "PipoPop - segredos" do Drive, quando existirem.
3. Claude in Chrome no Chrome pessoal do Lucas: YouTube Studio (receita em G5) e Meta Business Suite (business.facebook.com, publicar Reel no Instagram e na página).
4. Nada funcionou: o vídeo fica na fila, o Vigia tenta de novo no próximo horário, e o Lucas recebe UMA mensagem curta dizendo o que travou e o que ele pode fazer (sem pedir decisão que o Diretor pode tomar).
Conferência: depois do horário, getScheduledPosts/analytics; post com status de erro volta para a cadeia a partir do caminho seguinte.

## Limite do Metricool (plano grátis)
O plano grátis publica no máximo 20 posts por mês, contando cada rede separadamente (1 vídeo em YouTube + Instagram + Facebook = 3). Nosso ritmo (3 vídeos x 3 redes + stories) passa de 250 por mês. Enquanto o plano for o grátis:
- Prioridade dos 20 do Metricool: vídeos novos no YouTube > vídeos novos no Instagram > Facebook > stories > arquivo.
- O resto vai pelo caminho 2 ou 3. Isso está em DECISOES_LUCAS.md.
