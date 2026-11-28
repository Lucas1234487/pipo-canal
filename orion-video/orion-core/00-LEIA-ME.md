# Pacote do método — LEIA-ME

Método de um sistema pessoal de orquestração multiagente sobre o Claude Code: uma coordenadora que renasce todo dia, um gerente por frente dono do contexto, especialistas efêmeros que devolvem caminho de arquivo, guardas determinísticas com teste e medição de contexto e uso. **Não traz código nem texto da origem**: descreve comportamento para que outra sessão escreva o código novo.

Vocabulário: unidade de trabalho · entrega · frente · dono (o humano). `{{ASSIM}}` = ponto onde entra o domínio.

**`[CC]` = "conferido em 2026-11-28/2.1.288"**: recurso do Claude Code (ganchos, subagentes, memória, plugins, comandos) como estava em uso na origem nessa data e versão. **Não foi reconferido na documentação oficial — o destino deve reconferir.**

## Ordem de leitura
1. **00** (este) → 2. **07** mapa → 3. **05** custo e uso → 4. **01** arquitetura → depois sob demanda.

| Arquivo | Conteúdo |
|---|---|
| 01-arquitetura-generica.md | hierarquia, fluxo com trilhas T0–T3, estado, sucessão, júri, conversa com o dono |
| 02-componentes/ | 15 modelos (≤ 60 linhas): constituição, rotina do dia, leitor de fontes, gerente, pipeline, planejador, executor, crítico de eficiência, verificador, moderador+júri, criador, retro, validador, aposentadoria, quadro |
| 03-guardas-e-testes.md | princípio · aplicação · evento · parâmetros · testes em prosa · falha · classe |
| 04-dependencias-externas.md | o que a origem lê/chama fora do repositório, classificado |
| 05-custo-e-uso.md | medição de contexto e uso, limiares, política de modelo, custo por trilha e por papel, desperdícios |
| 06-licoes-e-fundamentos.md | lições generalizadas, diário de processo, pesquisa → desenho |
| 07-mapa-peca-funcao.md | peça de origem → função → destino |
| 08-descartados-e-sanitizacao.md | o que ficou de fora e resultado da busca de sanitização |

## Pré-requisito
Buscar e instalar as skills de terceiros `the-jury` e `learning-opportunities` (CC-BY-4.0, manter atribuição) — referências em 04 §1.

## Por onde começar a construir (sugestão)
quadro de estado + base de lições → guardas G-APOS, G-SAIDA, G-ASK com testes → linha de status + leitura de uso → gerente + pipeline T1/T2 → o resto.
