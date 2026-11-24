# 03. Ciclo: o que acontece todo dia e toda semana

## 1. Produção diária (tarefa agendada na nuvem, de madrugada, sem o Lucas)
Uma sessão do Diretor produz os 2 vídeos do dia seguinte (A = cotidiano/humor, 20 a 35 s; B = curiosidade/conhecimento, 35 a 60 s).
1. Posse rápida: 00_LEIA_PRIMEIRO, GUARDRAILS, último handover, PAUTAS.md.
2. G1 Pesquisa (modo diário, de preferência só Gemini): 5 pautas pontuadas para o dia, cada uma com destinatário ("manda pro grupo da firma"), gancho de quadro 1 e pergunta final com lado. Respeita a fila de PAUTAS.md e o calendário (datas dos próximos 7 dias).
3. Diretor escolhe 2 pautas (uma A, uma B), em até 5 linhas de justificativa.
4. G2 Roteiro: roteiro.json + cenas.json + fatos.md de cada vídeo. Diretor lê os 2 roteiros (texto puro) e aprova ou manda 1 correção.
5. G3 Produção: narração, render 2D, compose, qa_check, versão de upload (720p, até 3,8 MB), metadados (título até 50 caracteres com palavra-chave no começo, descrição de 2 a 4 frases, 3 a 5 hashtags com #PipoPop, comentário fixado).
6. G4 Avaliação: Gemini assiste aos 2 MP4 com som (5 perfis de público, fatos, som). Relatório curto em WORK/avaliacao.md.
7. Diretor aplica o piso (GUARDRAILS seção 3): publica, corrige uma vez ou usa a reserva.
8. Os aprovados vão para a fila de publicação: branch git `fila` (pasta AAAA-MM-DD_A e _B, com o MP4 de upload e meta.json), com push.
9. Handover curto do dia (o que saiu, notas, 1 lição) e push. Fim.

## 2. Vídeo de reserva
Manter sempre 2 vídeos evergreen prontos na branch `fila` (pasta reserva/). Se um dia der errado, publica a reserva e produz uma nova no dia seguinte.

## 3. Publicação em lote (decisão do Lucas: agendar em lote quando o PC estiver ligado)
Uma tarefa agendada que exige o PC pessoal do Lucas (Claude in Chrome no Chrome pessoal, nunca o da EMS) roda todo dia de manhã, e o Lucas também pode pedir "publica a fila" a qualquer hora.
1. Puxa a branch `fila`, pega tudo que ainda não foi agendado.
2. G5 sobe cada vídeo no YouTube Studio com o AGENDAMENTO do próprio Studio nos horários da tabela abaixo, preenche título, descrição, "não é para crianças", vídeo relacionado e declaração de IA (GUARDRAILS seção 2), e registra o link.
3. O comentário fixado é postado depois que o vídeo vai ao ar (próxima sessão com o PC ligado), junto com a rodada de comentários (curtir, responder, ocultar spam).
4. Se o PC estiver desligado, nada se perde: a fila acumula e a próxima sessão agenda os atrasados nos próximos horários livres.
Horários (Brasília, minuto quebrado, a partir do relatório 08):
| Dia | Vídeo A | Vídeo B |
|---|---|---|
| Seg a qui | 12h07 | 18h33 |
| Sexta | 11h37 | 17h04 |
| Sábado | 10h41 | 18h06 |
| Domingo | 11h13 | 18h09 |
Instagram (@pipo.pop88): mesmo vídeo, 15 a 45 min depois, quando o login no Chrome pessoal estiver ativo. Se não estiver, deixa a aba de login aberta e segue.

## 4. Métricas
- Diário (na sessão de publicação, 5 min): G6 lê no Studio os vídeos de 24 h e 7 dias e atualiza PLACAR.md.
- Semanal (domingo à noite): G6 completo (o que os 2 melhores têm em comum e os 2 piores não têm; projeção dos marcos de monetização) e propostas de série a partir dos mais engajados.

## 5. Pesquisa semanal (domingo à noite)
G1 completo: tendências e formatos da semana, datas das próximas 4 semanas, 3 concorrentes ganhando agora e por quê, e reabastece PAUTAS.md com 14 pautas novas. Usa Gemini com busca para o volume; o Claude filtra e pontua.

## 6. Melhoria contínua
Toda segunda, o Diretor escolhe 1 mudança para a semana (uma só), baseada no placar, e escreve na BASE com data. Exemplos: trocar a voz, mudar a duração, testar um formato fixo novo.
