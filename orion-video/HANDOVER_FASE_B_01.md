# Handover Fase B 01 (28/11/2026, sessão Opus)

## Feito (branch orion-video, testado: python3 kit/testes/test_guardas.py = 13 ok)
- kit/guardrails.py: "QA-Claude dispensado: motivo" passa só sem gatilho (gatilhos_qa: nota Gemini < 7,5, erro grave, ousado, formato/tema sensível, aviso do qa_check).
- kit/buffer.py: agendar --video exige --pasta e guardrails = 0 (falha fechada, sai 2).
- kit/tem_trabalho.py: triagem da vigia (sai 0 = nada a fazer). Fuso America/Sao_Paulo.
- kit/estado.py: docs/diretor/ESTADO.md (~1,4 mil tokens, teto 14 mil caracteres).
- 03_CICLO §0; custo/medicoes.csv; cartões das skills producao, publicacao e diretor.

## Achados
- BUG AO VIVO: o prompt da produção (03:37) manda escrever "QA-Claude dispensado", mas o guardrails da main reprova isso (veredito não encontrado). Sem correção, nada da madrugada de 29/11 agenda.
- QA-Claude pegou problema real em 3 dos últimos 5 vídeos (25/11 H, 26/11 M, 27/11 C), com o Gemini dando 7,4 a 8,8: sobreposição na Pipo, foto parecendo mofo, som em cima da palavra-chave, título absoluto, cartão do quadro 1. Decisão: QA-Claude Sonnet SEMPRE até essas classes virarem script.
- Push na main foi bloqueado pelo classificador de ações: precisa OK explícito do Lucas na conversa.
- 27 comentários pendentes (feito=false).
- Semanal roda amanhã (dom 21:47) em Opus lendo ~15 docs + pesquisa ampla: maior gasto da semana, lapidar antes.

## Próximos 3 passos
1. Com OK: mesclar orion-video na main e atualizar prompts (produção: posse via estado.py, QA-Claude sempre, --pasta; vigia: tem_trabalho.py; semanal: pesquisa no Gemini).
2. Guardas novas a partir dos achados do QA-Claude: SFX sobre palavra-chave (timestamps), sobreposição com a Pipo, título x fala (Gemini).
3. Medir: prints 28/11 noite e 29/11 08:00 -> custo/medicoes.csv.

## Atualização 15:18 (OK do Lucas: "pode fazer o que quiser")
- main = orion-video mesclada (13f7ce7). Prompts novos: produção (posse via estado.py, QA-Claude sonnet sempre, buffer --pasta), vigia (tem_trabalho.py primeiro), semanal (pesquisa e pautas no Gemini, custo no boletim).
- Produção disparada às 15:17: 2026-11-28_C às 19:06 e 2026-11-28_H (série olhos, parte 2) às 21:13.
- Pendente: Lucas apagar pipo-pesquisa e pipo-revisao e salvar os cartões; prints de uso hoje à noite e 29/11 08:00.
