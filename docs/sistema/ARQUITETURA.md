# Arquitetura do PipoPop (o mapa de como tudo se liga)

## Peças
| Peça | Onde | O que faz |
|---|---|---|
| Regras | docs/sistema/02_GUARDRAILS.md, BRIEFING_v3.md | o que nunca/sempre; estrutura; veto |
| Personalidade do Diretor | docs/diretor/BRIEFING_DIRETOR.md | palavras do Lucas, não editar o sentido |
| Papéis | docs/sistema/specs/ (G1..G6, O1..O4, QA_claude) | o que cada agente faz e entrega |
| Memória por papel | docs/diretor/cadernos/<papel>.md | lições datadas, lidas antes de começar |
| Memória do dia | docs/diretor/handovers/ | o que saiu, o que deu errado, o que fica |
| Memória de decisão | docs/BASE_CONHECIMENTO.md, docs/diretor/EXPERIMENTOS.md, docs/diretor/PLACAR.md, docs/historico.csv | o que sabemos, o que estamos testando, como foi |
| Pautas | docs/sistema/PAUTAS.md, docs/diretor/RESGATE_PESQUISA.md, docs/pesquisa/ | o que falar |
| Motor de voz | kit/tts.py (edge-tts, Francisca/Antonio) | roteiro.json -> narração + timing.json |
| Motor 2D | kit2d/: render2d.py (tempo, câmera, reações, transições), biblioteca.py (Pipo e elementos), cenarios2.py (24+ cenários em camadas com vida e âncoras), fundos.py (14 fundos animados, foto em tela cheia, mergulho), humano2.py + elenco.py (humano com assinatura e 13 personagens fixos), memes.py (20 memes da Pipo), CENAS.md (cardápio) | cenas.json -> quadros PNG + QA de cena |
| Sons | assets/sfx (CC0, com proveniência), assets/sfx/memes (reações), kit/gera_fa.py, kit/checa_sons.py (som some no celular?) | efeitos e reações |
| Imagens reais | kit/imagens.py | busca CC0/domínio público com proveniência |
| Montagem | kit/compose.py, kit/qa_check.py | legenda, som, mixagem, revisão automática |
| Gemini | kit/gemini.py (chave em ~/.pipo/gemini_key, vem do Drive "PipoPop - segredos") | pesquisa com busca, plateia que assiste ao vídeo, pronúncia |
| Fila | branch git `fila` | AAAA-MM-DD_M/_H/_C com upload.mp4, meta.json, relatórios, agendado.json ou segurar.json |
| Tarefas agendadas | Claude (produção 3h37, publicação 8h41, semanal dom 21h47) | rodam o ciclo sem o Lucas |
| Publicação | Claude in Chrome no Chrome pessoal do Lucas -> YouTube Studio | agenda, vídeo relacionado, comentário fixado |

## Fluxo de um dia
```
03h37 Produção (sessão do Diretor)
  posse -> lê placar/experimentos -> G1 pautas (Gemini) -> escolhe M, H, C
  para cada vídeo:
    Gerente de Produção (agente) planeja -> briefings O1..O4
    Diretor contrata O1 -> gerente confere -> Diretor aprova o texto
    Diretor contrata O2 e O3 em paralelo -> gerente confere
    Diretor contrata O4 -> gerente confere
    QA-Claude (agente novo) + QA-Gemini (script) -> 1 rodada de correção se preciso
  fila (push) -> agenda no Studio se o Chrome responder -> manda os vídeos ao Lucas
  handover + cadernos + placar + push
08h41 Publicação em lote: agenda o que ficou na fila (sem segurar.json), comentários, comentário fixado
Dom 21h47 Semanal: G1 completo (pautas), G6 (métricas), mudança da semana, enxuga cadernos
```

## Por que é assim
- Subagente não consegue abrir subagente (testado em 24/11), então o Diretor faz a ponte e o gerente continua vivo para conferir.
- Script e Gemini fazem o volume; agentes Claude fazem julgamento.
- Tudo que alguém aprendeu vira arquivo no git, porque cada sessão começa do zero.
