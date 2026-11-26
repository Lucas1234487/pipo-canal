# PipoPop

Canal de vídeos curtos (YouTube Shorts @pipopo.88, Instagram Reels @pipo.pop88, página do Facebook "PipoPop"), feito em 2D por código e comandado por agentes. O dono do negócio no dia a dia é o **Diretor**; o Lucas só veta e decide o que é drástico.

## Comece aqui (qualquer agente)
1. `docs/sistema/00_LEIA_PRIMEIRO.md` (índice de tudo)
2. `docs/sistema/02_GUARDRAILS.md` (o que nunca, o que sempre, piso de qualidade)
3. `docs/sistema/ARQUITETURA.md` (o mapa: peças, fluxo do dia, dados, publicação)
4. O briefing/spec do seu papel em `docs/sistema/specs/` + o seu caderno em `docs/diretor/cadernos/`
5. Diretor: o último handover em `docs/diretor/handovers/` e `docs/diretor/DECISOES_LUCAS.md`

## O que o Lucas pediu (as palavras dele, para entender o sentimento)
`docs/diretor/pedidos_lucas/`: melhora contínua, furar a bolha, transcender. O objetivo nº 1 é crescer e chegar na monetização nas 3 redes (`docs/sistema/06_CRESCIMENTO.md`).

## Documentos do sistema
| Arquivo | Para quê |
|---|---|
| 02_GUARDRAILS | regras e piso de qualidade |
| 03_CICLO | o que acontece todo dia e toda semana; slots de horário |
| 04_MELHORA_CONTINUA | revisão semanal rígida, boletim por papel, base que evolui |
| 05_CONTINUIDADE | o canal nunca para: cadeia de fallback, trava, avisos ao Lucas |
| 06_CRESCIMENTO | metas de monetização, detector de estagnação, carteira diária, 5 perguntas de todo vídeo |
| 07_DADOS | tudo vira dado: por vídeo x rede x janela, análise semanal e mensal |
| BRIEFING_v3, ARQUITETURA, COMO_TRABALHAMOS | hierarquia e funcionamento |
| specs/G1..G7, O1..O4, QA_claude | o como de cada papel |
| diretor/APOSENTADORIA | passagem de bastão: contexto vazio, mas nunca burro |

## Código (`kit/`, `kit2d/`)
| Comando | O que faz |
|---|---|
| `python3 kit/tts.py WORK` | narração (edge-tts) |
| `python3 kit2d/render2d.py WORK [--previa]` | render 2D (pycairo) |
| `python3 kit/compose.py WORK` | montagem, legenda, som |
| `python3 kit/qa_check.py WORK pt` | QA técnico do vídeo |
| `python3 kit/gemini.py video ...` | QA-Gemini (plateia + pronúncia) |
| `python3 kit/guardrails.py <pasta>` | portão determinístico antes de agendar (saída 1 = não agenda) |
| `python3 kit/buffer.py agendar ...` | publicar pelo Buffer (caminho 2) |
| `python3 kit/dados.py video/post/metrica/tabela/analise` | base de dados do canal |
| `python3 kit/imagens.py`, `kit/checa_sons.py` | fotos CC0/NASA com proveniência; audibilidade dos sons |

## Onde fica cada coisa
- Vídeos prontos e publicados: branch `fila` (pastas `AAAA-MM-DD_M/H/C`, `arquivo/`, `social/`). Nunca apagar vídeo publicado.
- Dados: `dados/` (videos.jsonl, posts.jsonl, metricas.jsonl).
- Memória do Diretor: `docs/diretor/` (handovers, cadernos, boletins, análises, EXPERIMENTOS, MELHORIAS, PLACAR, DECISOES_LUCAS, redes/).
- Marca: `assets/marca/` (avatar, banner, capa).
- Segredos: NUNCA no git. Drive "PipoPop - segredos" (Gemini) e "PipoPop - segredos Buffer" -> `~/.pipo/` (chmod 600).

## Tarefas agendadas
Produção diária 03:37 · Vigia 09:23, 15:23, 20:23 · Semanal domingo 21:47 (horário de Brasília).

_Histórico: o canal começou em 3D (Blender) em 21/11/2026 e virou 2D em 24/11/2026; o kit 3D antigo continua em `kit/` só como referência._
