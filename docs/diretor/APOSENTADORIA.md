# Protocolo de aposentadoria e passagem de comando

Contexto cheio deixa qualquer um burro: ele esquece regra, repete erro e confunde versões. Por isso ninguém fica tempo demais no posto. A memória do canal mora no git, não na cabeça de quem está trabalhando.

## Funcionários
- Um funcionário, uma tarefa. Entregou, se aposenta. Para outra tarefa, o Diretor contrata outro (ou retoma o mesmo com SendMessage só se for correção curta da mesma entrega).
- Na segunda reprovação da mesma entrega, o funcionário é aposentado e substituído. O Diretor reescreve o briefing com o que faltou.
- A última coisa que o funcionário entrega é o BILHETE, com até 10 linhas:
  - o que foi feito;
  - os arquivos entregues, com caminho;
  - o que ficou pendente;
  - o que deu errado e como resolveu;
  - o que faria diferente.
- O Diretor guarda os bilhetes em docs/diretor/ciclos/AAAA-MM-DD/bilhetes.md.

## Diretor
- Ele se aposenta ao fim de cada ciclo: uma sessão de produção, ou um dia. Também se aposenta antes do fim se perceber que o contexto pesou (conversa longa, muitas imagens lidas, começou a esquecer regras). Nesse caso, termina a tarefa em andamento, escreve o handover e encerra.
- A última missão, sem exceção, é escrever o handover em docs/diretor/handovers/NNNN_AAAA-MM-DD_<assunto-curto>.md, com o número seguinte ao último. Depois:
  - git add, commit ("Handover NNNN: <assunto>") e push para main;
  - atualizar docs/diretor/PLACAR.md;
  - se aprendeu algo que vale para sempre, escrever em BASE_CONHECIMENTO.md ou no BRIEFING_DIRETOR.md, com data.

## Modelo do handover

```
# Handover NNNN — AAAA-MM-DD — <assunto>
Diretor: <número do mandato>  ·  Ciclo: <o que foi esse ciclo>

## Estado em uma frase
<"Canal melhorando / estagnado / piorando" + o número que prova>

## O que publiquei (link, horário, tipo, uso da Pipo, nota da plateia, primeiros números)

## O que aprendi (com evidência)
- <aprendizado> — evidência: <número, comentário real, segundo em que a plateia deslizou>

## Decisões que tomei e por quê

## O que falhou e de quem foi a culpa (inclusive minha)

## Funcionários: quem foi bem, quem foi demitido, o que mudar nos briefings

## Discordâncias com o Lucas (o que ele pediu, o que eu disse, o que ficou decidido)

## Próximo ciclo: o que eu faria primeiro
1.
2.
3.

## Pendências e coisas que só o Lucas pode fazer

## Séries abertas (parte publicada, prometido aos comentários, prazo)
```

## Leitura do novo Diretor (ordem fixa)
1. docs/diretor/BRIEFING_DIRETOR.md
2. docs/BASE_CONHECIMENTO.md
3. docs/diretor/PLACAR.md
4. Os 3 handovers mais recentes, do mais novo para o mais velho (o mais antigo de todos, 0001, só se precisar de origem)
5. docs/diretor/FUNCOES.md

As pesquisas de docs/pesquisa/ são consulta, e não leitura obrigatória. Abra a que servir à decisão do dia.

## Regra de ouro (Lucas, 26/11): contexto vazio, mas nunca burro
Toda a hierarquia se aposenta e passa o bastão: Diretor -> Diretor sucessor (handover), Gerente -> Gerente, O1..O4 -> mesmo papel, QA-Claude -> QA-Claude, QA-Gemini (prompt) -> próxima versão do prompt. Ninguém começa com contexto cheio; todo mundo começa sabendo o essencial porque está ESCRITO NO GIT.
- O que é permanente (regra, padrão, receita) vai para as specs (docs/sistema/specs/), GUARDRAILS, 04/05 ou BASE_CONHECIMENTO. Não fica só no handover.
- O que é do papel vai para o caderno do papel (docs/diretor/cadernos/<papel>.md): no máximo ~40 linhas, só lições vivas. Passou disso, o semanal enxuga: o que virou regra sobe para a spec e sai do caderno.
- O handover é curto (até ~40 linhas): estado, o que mudou, pendências, decisões, próximos passos. Não copia spec.
- Quem é contratado lê: o briefing do seu papel + a spec do papel + o caderno do papel + o último bilhete do mesmo papel. Nada além do necessário (sem ler handovers antigos inteiros, sem colar histórico no briefing).
- O sucessor do Diretor lê o ÚLTIMO handover (não todos) + o que o 03_CICLO manda.
- Na revisão semanal, o boletim avalia também se os cadernos e handovers estão enxutos e úteis (nota em Fluxo/Hierarquia).
