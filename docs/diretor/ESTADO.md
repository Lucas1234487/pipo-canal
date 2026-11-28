# ESTADO do PipoPop (gerado por kit/estado.py em 28/11 17:20; não editar)

## Agora
- produzir: - · agendar: - · trava ativa: False · comentários pendentes: 31

## Fila, últimos 7 dias (evite repetir tema)
| pasta | tema | aposta | Gemini | QA-Claude | agendado |
|---|---|---|---|---|---|
| 2026-11-25_C | Dá pra ver o Natal do espaço 🛰️ | - | 7.5 | APROVA | NÃO |
| 2026-11-25_H | A casa dela foi a única da rua que apagou 💡 | - | 7.4 | CORRIGE | NÃO |
| 2026-11-25_M | 13º cai até segunda. A promoção, na sexta 💸 | - | 8.4 | - | NÃO |
| 2026-11-26_C | Por que o sorvete dói na testa? 🍦 | - | 8.6 | APROVA | NÃO |
| 2026-11-26_H | animais com olhos pra frente: o cotidiano | ousado | 9.0 | APROVA | sim |
| 2026-11-26_M | black_friday_preco_antes | seguro | 8.8 | APROVA | sim |
| 2026-11-27_C | comida de fim de ano / ciência do panetone | evolucao | 8.0 | APROVA | sim |
| 2026-11-28_C | de onde vem a poeira de casa | seguro | 8.6 | APROVA | sim |
| 2026-11-28_H | olhos pra frente parte 2: dinossauros | evolucao | 8.4 | APROVA | sim |

## Pedidos do Lucas (prioridade)
- Série H em 3 partes, dias seguidos (parte 1 = ep013, 26/11; parte 2 = ep015, 28/11 19h06 (o H de 27/11 não saiu); parte 3 = próximo H, 29/11): "E se os animais tivessem olhos pra frente?" (cotidiano, dinossauros, evolução até a sociedade). Brief completo em docs/diretor/series/olhos_pra_frente.md.

## Pautas usadas (últimas 12)
| Data | Vídeo | Pauta |
|---|---|---|
| 2026-11-21 | dinossauros (parte 1) | Asteroide extinguiu os dinossauros. Mas nem todos |
| 2026-11-21 | Black Friday (2 versões) | Metade do dobro |
| 2026-11-21 | ep002 | A vontade de abrir o presente antes do Natal |
| 2026-11-24 | ep004 | O ossinho da sorte do Natal é de dinossauro |
| 2026-11-24 | ep006 (em produção, teste do 2D) | Quanto tempo de vida você passou rolando o feed esse ano |
| descartada | ep005 | "Fica parado que o T. rex não te vê" (fato batido; o Lucas achou tosco) |
| 2026-11-26 | ep012 M | Véspera da Black Friday: tira print do preço hoje |
| 2026-11-26 | ep013 H | Série olhos pra frente, parte 1 (pedido do Lucas) |
| 2026-11-27 | ep014 C | Por que o panetone demora pra mofar (fila #19) |
| 2026-11-28 | ep015 H | Série olhos pra frente, parte 2: dinossauros (pedido do Lucas) |

## Decisões do Lucas
Só entra aqui o que é drástico para o negócio (dinheiro, mudar identidade do canal, apagar coisa pública, contas novas, risco legal). O resto o Diretor decide. Enquanto o Lucas não responde, vale a "alternativa enquanto isso". Quando ele perguntar "tem decisão pra mim?", o Diretor traz esta lista em poucas linhas.

| Data | Decisão | Opções | Recomendação do Diretor | Alternativa enquanto isso | Status |
|---|---|---|---|---|---|
| 26/11 | Limite do Metricool grátis (20 posts/mês, por rede) | A) Starter, cerca de US$ 25/mês, sem limite; B) API direta grátis do YouTube e da Meta (o Lucas cria as chaves uma vez, ~15 min com o Claude guiando no Chrome); C) depender do Chrome dele aberto | B (grátis e funciona sem o PC); A se quiser zero manutenção | Metricool só para os vídeos novos do YouTube e Instagram; resto pelo Chrome quando ele estiver aberto | aberta |
| 26/11 | Apagar a tarefa antiga "Pipo - publicação em lote (Studio)" de 24/11 (08:41) | o Lucas apagou por engano as novas; a semanal antiga foi reescrita pelo Claude; a de lote antiga não pôde ser reescrita | apagar no painel | o Vigia das 09:23 cobre o lote | FEITO (Lucas apagou, 26/11) |
| 26/11 | Modo enxuto (o limite de uso de 5 h estourou 3x com cerca de 25 agentes/dia) | A) gerente + O1 principal + 1 organizador de produção leve + QAs; B) estrutura completa com 2 vídeos/dia; C) tudo como está, aceitando atrasos | A | a produção de 27/11 roda o A se ele não responder | APLICADO 28/11 com OK do Lucas (produção enxuta; vigia 1x/dia sonnet); lapidação na Fase B do Órion de Vídeo (branch orion-video) |

## Último handover (0010_2026-11-28_producao-enxuta-H-parte2.md)

## Lições vivas do Diretor
Lições datadas, 1 a 3 linhas cada. Leia antes de começar; acrescente 1 no fim.
- 24/11 noite: o Lucas avalia bem quando vê tudo numa página com Gostei/Talvez/Não gostei e copia a resposta. Repetir sempre que o motor ganhar coisa nova (página "PipoPop: o que fica").
- 24/11: pedido de paródia de pessoa real/futebol ("Neymaro") recusado com alternativa; explicar o porquê em uma linha.
- 26/11: 10 agentes em paralelo estouraram o limite de 5 h da conta (3 paradas no dia). Um vídeo por vez, organizadores mecânicos no modelo leve, e checar o horário do reset antes de abrir uma leva grande.
- 28/11 (ep015 H): 215 palavras na voz Antonio deram 81 s (2,7 palavras/s), não 65. Para H de 45-65 s, roteiro com até ~170 palavras e rate +10%; conte antes de mandar ao produtor.

## Sob demanda (não leia na posse)
Bíblia e regras de roteiro: docs/biblia_do_canal.md §5-8 · crescimento: docs/sistema/06_CRESCIMENTO.md · dados: 07_DADOS.md · experimentos: docs/diretor/EXPERIMENTOS.md · placar: docs/diretor/PLACAR.md · cadernos dos papéis: docs/diretor/cadernos/
