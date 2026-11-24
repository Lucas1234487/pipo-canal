# Sistema PipoPop (versão 2, 24/11/2026)

**Leia primeiro: docs/sistema/BRIEFING_v3.md (24/11). Ele manda na estrutura, na aprovação do Lucas e na memória entre agentes.**

Este é o manual de funcionamento do canal. Foi escrito a pedido do Lucas para o canal rodar sem ele corrigir o Diretor todo dia. Toda sessão de trabalho começa aqui.

## Ordem de leitura (Diretor, ao tomar posse)
1. Este arquivo.
2. docs/diretor/BRIEFING_DIRETOR.md (quem você é; a personalidade é do Lucas e não muda).
3. docs/sistema/02_GUARDRAILS.md (o que nunca se faz).
4. docs/sistema/01_ORGANOGRAMA.md (Diretor, gerentes, desenvolvedores, quem usa Claude e quem usa Gemini).
5. docs/sistema/03_CICLO.md (o que acontece todo dia e toda semana).
6. O último handover em docs/diretor/handovers/ e docs/diretor/PLACAR.md.
Os gerentes leem só a própria spec em docs/sistema/specs/ e os arquivos que ela aponta. Os desenvolvedores leem só o briefing que o gerente escreve.

## O que vale sobre o quê (em caso de conflito)
1. Mensagem do Lucas na sessão atual.
2. docs/sistema/02_GUARDRAILS.md.
3. Decisões do Lucas datadas (este sistema, de 24/11/2026; depois a Bíblia seção 0.1; depois a BASE seções 10 a 18).
4. As specs em docs/sistema/specs/.
5. docs/biblia_do_canal.md e docs/pesquisa/ (fundamentos; o que contradiz os itens acima está superado).

## Mudanças de 24/11/2026 (decisões do Lucas, valem sobre o que estiver escrito antes)
- Formato padrão: 2D animado por código (docs/sistema/04_FORMATO_2D.md). O 3D só volta como especial raro com motivo escrito.
- História primeiro: o que prende é a história e a identificação, não o acabamento. Nicho da pesquisa: curiosidade e situações do cotidiano adulto com alguém para quem mandar (docs/diretor/RESGATE_PESQUISA.md).
- Constância vale mais que perfeição: postar 2 vídeos por dia. Vídeo que passa no piso mínimo (02_GUARDRAILS, seção 3) é publicado, mesmo sem nota 10. O padrão 10 continua sendo a meta de melhoria, não uma trava de publicação.
- O Lucas não aprova vídeo antes de publicar. Ele recebe o relatório do dia.
- Gemini entra como mão de obra barata (pesquisa, rascunhos, revisão de vídeo com som), pela chave da API (docs/sistema/05_GEMINI.md). O Claude decide, confere e escreve código.
- Publicação em lote pelo agendamento do YouTube Studio quando o PC pessoal do Lucas estiver ligado (03_CICLO).
- Economia de tokens é requisito, não detalhe (01_ORGANOGRAMA, seção 4).
- O Chrome do PC do trabalho (EMS) nunca é usado para o canal.

## Onde está cada coisa
| O quê | Onde |
|---|---|
| Personalidade e missão do Diretor | docs/diretor/BRIEFING_DIRETOR.md |
| Regras duras | docs/sistema/02_GUARDRAILS.md |
| Quem faz o quê | docs/sistema/01_ORGANOGRAMA.md e docs/sistema/specs/ |
| Rotina | docs/sistema/03_CICLO.md |
| Formato 2D e motor | docs/sistema/04_FORMATO_2D.md, kit2d/ |
| Gemini | docs/sistema/05_GEMINI.md, kit/gemini.py |
| Pesquisa de mercado (16 relatórios) e o que se perdeu dela | docs/pesquisa/, docs/diretor/RESGATE_PESQUISA.md |
| Regras de roteiro, legenda, som e proibições de estilo | docs/biblia_do_canal.md (seções 5 a 8) |
| Memória de longo prazo | docs/BASE_CONHECIMENTO.md |
| Diário de cada mandato | docs/diretor/handovers/ |
| Números | docs/diretor/PLACAR.md, docs/historico.csv |
| Pautas usadas e fila de pautas | docs/sistema/PAUTAS.md |
| Kit 3D (arquivado) | kit/, render/, assets/modelos/ |
