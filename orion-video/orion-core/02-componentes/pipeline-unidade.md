# Modelo · Pipeline de uma unidade de trabalho (skill do gerente)

- **Papel:** roteiro único de uma unidade, do passo 1 ao anúncio. Encaixa nas regras do repositório ({{DOC_REGRAS_REPO}}), sem substituí-las.
- **Acionado:** "fazer a unidade X", nova unidade na fila do gerente.
- **Entrada:** unidade (texto ou caminho), repositório, estado.
- **Saída:** pasta da unidade `{{PASTA_PLANOS}}/<chave>/` com PROPOSTA, relatórios por rodada, CONSOLIDADO, ANALISE, DECISOES, plano de entrega, relatório final; quadro atualizado a cada etapa.

## Etapas (detalhe em 01 §2)
0 ler regras · 1 passo 1 + trilha **[dono]** · 2 proposta · 3 aprovação **[dono]** · 4 implementar até gate verde · 5 verificar (novos) · 6 análise **[dono aprova correções + regressão na mesma pergunta]** · 7 corrigir · 8 evidências reais · 9 plano de entrega **[dono, registrado no quadro]** · 10 empacotar · 11 relatório · 12 abrir entrega · 12b pré-voo · 13 anúncio só após pré-voo; integração final é do dono.

## Trilhas
{{TRILHAS}} — padrão: T0 doc · T1 defeito pontual · T2 normal · T3 grande/arriscada. Tabela etapa × trilha em 01 §2.
- Sobe sozinha e avisa; nunca desce sem novo passo 1. Registrar subida como métrica.
- Parada: 2 correções falhas no mesmo ponto ou regressão na 3ª rodada → moderador + júri + pergunta ao dono.

## Brief-modelo de verificação (só caminhos, nunca opinião do gerente)
`{{VERIFICADOR}} <chave> R<n> (explora|regressão). Unidade: … Proposta aprovada: … Diff: <base>..<ramo>. Evidências: … Relatórios anteriores: … Itens aprovados: … Saída: <pasta>/RELATORIO_{{VERIFICADOR}}_R<n>.md`

## Regras
- Textos ao usuário final: base e versão calorosa lado a lado.
- Executor **novo** por rodada de correção, com brief curto (lição de custo; a origem começou reaproveitando).
- Regressão pura: 1 QA em {{MODELO_MECANICO}}, sem moderador nem revisor.
- Evidências e bancada numa passada por unidade, no fim.
- Desvio entre unidade e código: uma linha no doc do repositório (o que pede, o que faz, porquê, quem decidiu).
- Empacotamento: uma mudança por responsabilidade; {{PADRAO_MENSAGEM}}; nunca stage em massa; nunca credenciais.

- **Nunca:** pular aprovação; descer trilha; anunciar sem pré-voo; integrar; tocar {{AMBIENTE_PROIBIDO}}.
- **Pronto:** entrega aberta, pré-voo registrado, anúncio pronto para o dono enviar.
- **Custo:** T0 < 50 mil · T1 0,5–1 M · T2 2,5–4 M · T3 > 4 M (05 §d).
- **Placeholders:** {{TIPO_DE_ENTREGA}}, {{CRITERIO_DE_QUALIDADE}}, {{COMANDO_GATE}}, {{EVIDENCIAS}}, {{BANCADA_LLM}}, {{STATUS_EXTERNOS}}.
