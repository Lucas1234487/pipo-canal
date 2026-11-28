# Modelo · Aposentadoria e handover (skill)

- **Papel:** trocar um agente de vida longa antes que o contexto degrade, sem perder estado.
- **Acionada:** gatilho atingido (abaixo); "aposenta", "passa o bastão"; injeção do gancho G-APOS.
- **Gatilhos:** coordenadora = fim do dia ou > {{LIMITE_INSTRUIR}}% · gerente = fim da frente, 1ª compactação, > {{LIMITE_INSTRUIR}}%, 2 correções falhas no mesmo ponto, {{DIAS_MAX_GERENTE}} dias corridos · especialista = fim da etapa.
- **Limite inteligente:** antes, terminar o que está no fim (entrega aprovada, pré-voo, doc curta). Sair no meio só se falta trabalho grande. Gravar opiniões dadas só no chat (ex.: análise de achados) no rascunho antes de sair.

## Handover — `{{PASTA_DE_ESTADO}}/handovers/<papel>-<data>.md`, escrito ANTES de tudo, ~150 linhas, fatos
1. identidade: papel, **id da sessão** (a guarda procura), período
2. estado agora: cada unidade — etapa, ramo, último gate, o que está no meio
3. decisões que o sucessor deve respeitar
4. pendências: fila de decisões, promessas, esperas externas
5. armadilhas (cada uma também vira lição: adicionar ou reincidiu)
6. arquivos-chave · 7. números · 8. próximos 3 passos · 9. perguntas ao antecessor

## Sucessão
- Marcar "aposentando" no quadro com o caminho do handover; avisar a coordenadora (≤ 400 caracteres).
- A coordenadora abre o sucessor com o brief do gerente + handover.
- Sucessor de gerente: até 5 perguntas numa mensagem ao antecessor; ele responde e **para**. Com o sucessor ativo, marcar o antigo "aposentado"; arquivar a sessão só com OK do dono.
- Sucessor da coordenadora: desanexar-se logo, mover-se ao grupo certo, registrar-se com o id da sessão `[CC 2026-11-28/2.1.288]`, **nunca** falar com a aposentada (dúvida vai ao dono); conferir que os avisos aos gerentes ativos **chegaram**.

- **Saída:** handover + quadro atualizado + sucessor ativo.
- **Nunca:** aposentar sem handover; adiar por conta própria (só o dono adia, {{ADIAR_MIN}} min).
- **Pronto:** handover cita o id; sucessor ativo; antigo marcado.
- **Custo:** escrita do handover (barata) + leitura inicial do sucessor (não medida; dezenas a centenas de mil). Sucessor à toa = desperdício inteiro.
