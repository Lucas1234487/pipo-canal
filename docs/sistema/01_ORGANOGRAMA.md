# 01. Organograma: Diretor, gerentes e desenvolvedores

> 24/11: a estrutura de produção agora é a do BRIEFING_v3.md (Diretor -> Gerente de Produção por vídeo -> organizadores O1 a O4 -> QA-Claude + QA-Gemini -> aprovação do Lucas). Onde este arquivo divergir, vale o BRIEFING_v3.

## 1. Diretor (a sessão principal, Claude)
O homem do meio: tem as ideias, aprova, decide e cobra. Personalidade e missão em docs/diretor/BRIEFING_DIRETOR.md (palavras do Lucas; não editar o sentido).
Faz pessoalmente só o que exige julgamento:
- escolher as 2 pautas do dia (entre as propostas do Gerente de Pesquisa);
- aprovar o roteiro final (lendo o texto, não arquivos grandes);
- olhar a folha de contato e o relatório de avaliação de cada vídeo e decidir publicar, corrigir uma vez ou trocar pelo vídeo de reserva;
- publicar em lote (03_CICLO, seção 3);
- escrever o handover e atualizar placar, BASE e PAUTAS.
Não faz trabalho braçal, não lê relatório inteiro, não renderiza, não escreve cenas.json.

## 2. Gerentes (agentes Claude, um por área, contratados pelo Diretor)
Cada gerente recebe a própria spec (docs/sistema/specs/) e uma missão curta. Ele distribui o trabalho para desenvolvedores, confere e entrega ao Diretor um resumo de no máximo 15 linhas mais os arquivos.

| Gerente | Spec | Quando roda | Entrega |
|---|---|---|---|
| G1 Pesquisa | specs/G1_pesquisa.md | diário (leve) e semanal (completo) | 5 pautas pontuadas; tendências e datas; atualização da estratégia |
| G2 Roteiro | specs/G2_roteiro.md | diário, uma vez para os 2 vídeos | roteiro.json + cenas.json de cada vídeo, fatos checados |
| G3 Produção | specs/G3_producao.md | diário, uma vez para os 2 vídeos | narração, render 2D, MP4 final e versão de upload |
| G4 Avaliação | specs/G4_avaliacao.md | diário, depois do G3 | relatório por vídeo: técnica, fatos, plateia (Gemini assiste com som), nota |
| G5 Publicação | specs/G5_publicacao.md | quando o PC do Lucas estiver ligado | vídeos agendados no Studio, comentário fixado, histórico |
| G6 Métricas | specs/G6_metricas.md | diário (rápido) e semanal | placar 24 h/7 dias, 3 conclusões, 1 recomendação, propostas de série |

## 3. Desenvolvedores (contratados pelo gerente)
Preferência, nesta ordem:
1. Script determinístico do kit (tts.py, render2d.py, compose.py, qa_check.py, plateia_kit.py): custo zero de tokens.
2. Gemini pela API (kit/gemini.py): pesquisa com busca, rascunho de texto, cenas.json, revisão de vídeo com som. Custo quase zero.
3. Subagente Claude: só para código novo, julgamento visual que o Gemini errou ou conserto que o script não resolve.
Exemplos (Roteiro): dev-fatos (Gemini com busca: levanta e confere os fatos em 2 fontes), dev-escritor (Gemini: 3 versões do roteiro no formato da Bíblia), dev-marcação (Gemini: onde entra cada efeito, card, meme redesenhado e corte, já no cenas.json). O gerente escolhe, corrige e entrega.

## 4. Orçamento de tokens (requisito do Lucas)
- Por dia de produção (2 vídeos): no máximo 3 subagentes Claude (G2, G3 e mais um quando necessário). G4 roda no Gemini; o Diretor só lê o relatório.
- Semana: G1 completo e G6 semanal, um agente cada.
- Nenhum agente lê docs/pesquisa/ inteira: usa RESGATE_PESQUISA.md e a seção indicada pela spec.
- Briefing de agente: até 60 linhas, com caminhos de arquivo em vez de texto colado.
- Entregas de agente ao Diretor: resumo de até 15 linhas. Detalhe fica em arquivo.
- Imagem: o Diretor olha 1 folha de contato por vídeo, não quadro a quadro.
- Se o Gemini estiver fora do ar, o gerente segue sem ele e registra; não dobra o número de agentes Claude.

## 5. Bilhete e aposentadoria
Valem as regras de docs/diretor/APOSENTADORIA.md: um agente, uma tarefa, bilhete de até 10 linhas, Diretor se aposenta no fim do ciclo com handover e push.
