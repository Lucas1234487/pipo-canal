Tenho um canal de Shorts, o PipoPop, que publica 3 vídeos por dia com a produção quase toda automatizada por você. A fonte da verdade do canal é o repositório git do Pipo (o mesmo que a skill pipo-diretor clona na "posse"); as skills são só a porta de entrada. Também tenho um método de trabalho, o Órion, feito para desenvolvimento de código, que funciona muito bem. Ele está documentado, já sem nenhum dado de empresa, na pasta orion-core/ (anexada). Comece pelo 00-LEIA-ME.md, depois leia 07, 05 e 01; o resto só sob demanda, para não gastar o meu limite à toa.

## Missão
Desenhar o "Órion de Vídeo": a melhor combinação dos dois mundos, não uma cópia.
- Do Órion quero o rigor: trilhas por risco, guardas determinísticas, controle de contexto e de uso, lições que não se repetem, verificação independente.
- Do Pipo quero o que já funciona e não pode piorar: o portão do Gemini (plateia e pronúncia), o QA-Claude independente, o qa_check.py, o guardrails.py, a cadeia e a estrutura de postagem, a identidade e o tom dos vídeos.
- Quero a mesma qualidade (ou melhor) gastando bem menos do meu limite do plano Pro.
Tudo que for específico de desenvolvimento de código (revisão de código, validação de integração com front, monitoramento, PR e commit, tickets, chat corporativo) fica de fora: o pacote já vem sem isso; se aparecer algo assim, ignore.

## O que já sei (confirme, não pergunte)
- Meu plano é o Claude Pro: tem limite de 5 h e limite semanal, compartilhados entre o app/chat e o Claude Code, então o que eu uso manualmente também conta. Não presuma quais modelos e recursos o plano inclui nem quais são os limites: verifique (/model, /status ou /usage, Configurações > Uso e a ajuda oficial), porque isso muda com o tempo.
- O Pipo já tem uma versão do método: Diretor, gerente de produção por vídeo, O1 Roteiro e Fala, O2 Cenário, O3 Sonoplastia, O4 Montagem, QA-Claude (agente novo) e QA-Gemini; portão do Gemini obrigatório antes de agendar; kit/ (gemini.py, tts.py, compose.py, qa_check.py, guardrails.py, dados.py, buffer.py) e kit2d/render2d.py; vídeo 2D animado por código; modos produção (madrugada), vigia (09:23, 15:23 e 20:23) e semanal; handover, aposentadoria, placar e histórico. O trabalho é descobrir o que o Órion acrescenta a isso, não recomeçar do zero.
- Divergências já visíveis nas skills (liste todas as outras que achar e proponha o que aposentar ou atualizar; onde divergirem, vale o git): pipo-pesquisa e pipo-revisao ainda falam de 3D e de 2 vídeos por dia, e o Diretor as declara substituídas pelas specs G1 e G4; a pipo-producao fala de 2 vídeos por dia, e o Diretor trabalha com 3 (momento, história, conhecimento); a pipo-publicacao descreve o agendamento direto pelo Chrome, com o Metricool só para métricas, e o Diretor descreve a cadeia Metricool, Buffer (kit/buffer.py), Chrome.
- Segredos (chaves do Gemini e do Buffer) ficam fora do git e do chat. Nunca imprima, copie nem comite chaves.
- Posso mandar mensagens por ditado, com erros de transcrição: interprete com bom senso e, se a dúvida mudar o resultado, pergunte numa linha.

## Regras de segurança (valem em toda a missão)
1. A Fase A não mexe no canal em produção: só leitura, medição e testes isolados. Não publique, não agende, não comente, não mexa em contas, nas tarefas agendadas nem no git de produção (main e fila). Vídeos de teste nunca entram na fila. Grave seus arquivos numa pasta orion-video/, em branch própria; push só com o meu OK.
2. Nada que gere gasto (API paga, créditos de uso do plano, assinatura) sem o meu OK. Confirme se a automação usa a assinatura e não uma chave de API: com ANTHROPIC_API_KEY definida, o Claude Code cobra pela API e não pelo plano. Se os créditos de uso estiverem ligados, me avise.
3. Nunca o PC, o Chrome ou as contas do trabalho; nunca digitar senha. Só me escale: login, dinheiro, mudança de guardrail, risco à conta, mudança de arquitetura.
4. Os guardrails e a identidade do canal (Bíblia: mascote, voz, estrutura de roteiro, proibições) são piso: nenhuma economia pode afrouxá-los nem mudá-los sem o meu OK.
5. Sessões de diagnóstico curtas: nenhuma passa de uns 50% da janela de 5 h; ao chegar em 40%, grave o estado em arquivo (handover curto, como no método) e pare. Registre quanto a própria Fase A custou. Antes de rodar qualquer teste, me diga o custo estimado em % da janela. Se o ambiente permitir escolher o modelo por subagente, use o mais barato que dê conta para leitura e inventário e reserve o melhor para o desenho do plano.

## Princípios de custo e de qualidade (regras do jogo)
- Código antes de modelo: tudo que for determinístico (validar, contar, formatar, nomear, agendar, checar tema repetido) é script.
- Memória em arquivo, briefs curtos, subagentes devolvem caminho de arquivo, não texto longo.
- Dividir por contexto, não por tipo de trabalho: segundo a pesquisa do pacote (ainda não reverificada), times por papel gastam mais coordenando do que produzindo e cada passagem perde fidelidade. Só divida onde houver paralelismo real ou isolamento necessário (como o verificador independente).
- Trilhas por risco: formato recorrente e seguro passa por menos etapas que tema novo ou sensível; sobe sozinha, nunca desce no meio.
- Guarda vira código com teste. Se o ambiente não tiver ganchos (hooks), a guarda vive dentro do script, com falha fechada (por exemplo, o script de agendamento recusa rodar sem guardrails.py = 0 e sem o relatório do Gemini).
- Contexto e uso são monitorados: aposentar com handover antes de estourar; pausar o lote (usando fila e reserva, que já existem) em vez de entregar pior quando a janela passar de um limiar.
- O próprio sistema tem orçamento: constituição de até ~200 linhas, skills de até ~300 (prefira bem menos), agentes de até ~120 e descrições curtas; meça com um linter simples.
- Eu só aprovo o que importa; o resto segue o que o Diretor já faz ("constância vale mais que perfeição").

## FASE A: diagnóstico e plano (não construa nada ainda)

A1. Inventário real
- Descubra onde e como cada modo roda (app desktop, terminal ou nuvem), os horários exatos das tarefas agendadas, quais ferramentas existem nesse ambiente (ganchos, leitura de uso, subagentes, Chrome, conector do Drive) e qual modelo cada papel usa hoje (explícito ou padrão).
- Fluxo atual por vídeo e por dia: quantos contextos (sessões e agentes) abrem, o que cada um lê e devolve, quantas rodadas de correção em média e a taxa de reprovação por etapa (use historico.csv, handovers, relatórios de QA e PLACAR). Quais passos já são script e quais dependem do modelo.
- Custo fixo de "posse": quantos arquivos e linhas cada sessão lê só para começar e quantas sessões por dia repetem isso.
- Divergências entre skills e git, duplicações, o que está obsoleto.
- Delegue a leitura pesada a subagentes baratos que gravem resumos de uma página em orion-video/inventario/; você lê só os resumos.

A2. Medição de custo e de limite
A documentação oficial não dá um número fixo de tokens por janela: o consumo varia com o modelo, o tamanho da conversa e dos arquivos. Portanto NÃO estime de memória: calibre medindo.
1. Fontes de medida: (a) o indicador de uso das janelas de 5 h e semanal (anote horário e % antes e depois; ele pode atrasar, então espere e confirme; se a granularidade for grossa, repita o passo várias vezes seguidas dentro da mesma janela e divida); (b) os transcripts de sessão, se existirem localmente, que trazem o uso de cada resposta (entrada, saída, cache criado e cache lido): some por etapa e por subagente com um script simples; (c) se nenhum dos dois estiver ao seu alcance, diga e me peça o print de Configurações > Uso nos momentos exatos (antes e depois de qual passo).
2. Microbancada por etapa e por modelo: rode a mesma tarefa fixa em cada modelo candidato, no mínimo 3 vezes, e registre tokens, número de turnos e variação em % da janela. Calcule a razão entre modelos para a mesma etapa; não assuma pesos.
3. Modelo de custo do dia: soma, sobre modos × vídeos × etapas, de (custo medido × fator de retrabalho medido) + custo fixo de posse por sessão. Mostre em % da janela de 5 h (pico por modo) e em % do teto semanal, diga quais janelas de 5 h cada modo abre (elas começam na primeira mensagem) e descubra qual dos dois limites realmente prende. Calcule também quantos vídeos por dia cabem com a folga definida abaixo.
4. Reserva: deixe folga para o meu uso manual (o limite é compartilhado) e para dias ruins. Proponha uma meta (por exemplo, o canal usar no máximo X% do semanal) e uma regra automática que pausa o lote, em vez de entregar pior, quando a janela passar de um limiar.
5. Registre em orion-video/custo/ (medicoes.csv e modelo_de_custo.md) como refazer a medição.

A3. Mapa Órion × Pipo
Para cada peça do pacote, diga MANTER, ADAPTAR ou DESCARTAR, com o porquê e o ganho esperado. Ponto de partida, que você deve contestar:
- Orquestrador que renasce, lê um estado compacto e delega → Diretor → manter; encurtar a posse (H2).
- Dono do contexto por frente + especialistas efêmeros com brief por arquivo → gerente por vídeo + O1 a O4 → testar fundir (H1); manter o brief curto por arquivo.
- Verificador independente, novo a cada rodada → QA-Claude novo + QA-Gemini + qa_check.py → MANTER os três; acionar o QA-Claude por trilha ou gatilho (H7).
- Trilhas por risco (T0 a T3) → hoje "hierarquia sem exceção" → ADAPTAR: trilhas de vídeo, do formato recorrente seguro ao tema sensível ou formato novo.
- Guardas determinísticas com teste → guardrails.py + portão do Gemini → ADAPTAR: ampliar; sem ganchos, pré-condição dentro dos scripts de agendamento e publicação.
- Controle de contexto e de uso das janelas → não existe → ADOTAR (A2).
- Aposentadoria e handover → APOSENTADORIA.md → MANTER; gatilho por % de contexto quando o ambiente permitir medir.
- Base de lições com "reincidiu" e "garantida por guarda" → caderno de ~40 linhas por papel → ADAPTAR.
- Diário de observações de processo (gargalo, token, tempo, erro) + retro → semanal e MELHORA_CONTINUA → ADAPTAR, ligado às métricas de custo.
- Júri e moderador → não há → só para decisão cara de reverter; Gemini como juiz de outra família, porque o júri do Órion é todo Claude e tem erro correlacionado (H9).
- Leitor de fontes em lote que grava em arquivo → G1 no Gemini → MANTER.
- Linter de orçamento de contexto → não há → ADOTAR.
- Painel ao vivo → não há → só se custar quase nada.

A4. Matriz de modelos por etapa
Etapas: G1 pesquisa, G2 roteiro, G3 produção, G4 portão, G5 publicação, G6 métricas, comentários, semanal, mensal. Colunas: modelo atual → candidatos (script, Gemini, Haiku, Sonnet, Opus; outros só se estiverem no plano sem custo extra) → tokens e % da janela medidos → risco de qualidade → validador determinístico existente? → teste de rebaixamento → decisão.
- Regra: o mais barato que passe no limiar na bancada; sobe um degrau só se falhar; volta ao degrau anterior se o QA reprovar duas vezes seguidas. Quanto mais um validador determinístico (schema de JSON, qa_check.py, guardrails.py) pega o erro, mais barato pode ser o modelo; quanto mais o julgamento é de gosto (gancho, humor seco, texto que soa IA), mais vale o caro.
- Bancada de qualidade: 6 a 10 pautas já publicadas (com métricas) mais 3 de risco; cada etapa candidata roda 3 vezes (a maioria vale, como no Órion); julgamento por checklist objetivo e pelo Gemini às cegas (sem saber qual modelo gerou), nunca pelo mesmo modelo avaliado; no máximo 3 pares para eu conferir em poucos minutos.
- Defina "qualidade" de forma mensurável: guardrails.py = 0; qa_check aprovado; nota da plateia do Gemini acima de um limiar; checklist da Bíblia (gancho de 0 a 2,5 s, mudança visual a cada 1,5 a 3 s, um tipo de final, nada na faixa da legenda); retrabalho (rodadas até aprovar); e, como indicador atrasado, retenção em 24 h, 72 h e 7 dias.

A5. Alternativas de caminho (no mínimo 3)
Cada uma com: contextos por vídeo, % do semanal por dia, risco de qualidade, esforço para implementar e o que muda para mim. Por exemplo: (1) o atual com cortes baratos; (2) enxuta, com um produtor por vídeo + scripts + portões do Gemini + QA-Claude por gatilho; (3) em lote, com um produtor por lote e trilhas por risco. Proponha outras se enxergar melhor. Recomende uma e diga o que faria você mudar de ideia.

A6. Plano de implementação em etapas pequenas
Cada etapa com: o que entrega, teste de aceitação objetivo, custo estimado, como reverter e quando entra em produção. Migração gradual: o fluxo novo roda primeiro em 1 dos 3 vídeos por dia (o de menor risco), por alguns dias, e só vira padrão se a nota e o custo ficarem melhores que os do atual.

A7. Entrega da Fase A
orion-video/PLANO.md (até 2 páginas) com decisões numeradas em duas partes. Parte A: decisões gerais (tabela técnica D1…Dn). Parte B, "Precisa de você": só o que depende de mim, cada uma concisa (o que acontece hoje, opções, recomendação e porquê); nenhuma sigla ou id inventado sem explicar no mesmo bloco. Recomendação primeiro, PT-BR, curto. Depois ESPERE o meu OK.

## Hipóteses iniciais (para confirmar ou derrubar com medição, não para aceitar)
H1. Dividir por tipo de trabalho (gerente por vídeo + O1 a O4) gasta mais contexto coordenando do que produzindo, e O2, O3 e O4 são quase só scripts (tts, render2d, compose, qa_check) com o modelo escrevendo JSONs (roteiro, cenas, meta). Teste: um produtor por vídeo (e uma variante por lote) contra o atual, nas mesmas pautas.
H2. A "posse" (cerca de 12 documentos lidos a cada sessão, em 4 ou mais sessões por dia) é um custo fixo grande. Teste: um ESTADO.md compacto gerado por script (poucos milhares de tokens) + documentos sob demanda.
H3. Uma vigia sem nada a fazer ainda gasta a posse inteira. Teste: portão de entrada em script ("há algo a fazer?") que encerra cedo.
H4. Onde existe validador determinístico, um modelo mais barato basta; onde o julgamento é de gosto, o caro compensa.
H5. O Gemini (fora do meu limite do Claude) pode absorver mais volume (rascunhos, checagem de fatos em 2 fontes, classificação e rascunho de respostas a comentários, plateia), ficando para o Claude a escolha, a reescrita final e a decisão. Antes, verifique cota e custo do Gemini.
H6. Publicar e responder comentários pelo Chrome é o passo mais caro por ação (capturas de tela e DOM): priorize buffer.py/API; no Chrome, um lote por dia e regra de valor para responder (por exemplo, só pergunta, palpite ou correção).
H7. O QA-Claude independente não precisa rodar em todo vídeo: por trilha ou gatilho (formato novo, tema sensível, avisos do qa_check, nota baixa do Gemini).
H8. A pesquisa semanal em muitos agentes (se ainda existir assim) pode migrar em boa parte para o Gemini com busca, com o Claude só consolidando e decidindo.
H9. Um júri de 5 jurados, todos Claude, é caro (veja a ordem de grandeza em 05-custo-e-uso) e tem erro correlacionado: usar raramente e com o Gemini como juiz de outra família.
H10. Os horários dos modos podem abrir janelas de 5 h em horas ruins, e o teto semanal pode ser o que realmente prende, não a janela.

## FASE B: construção (só depois do meu OK)
Etapas pequenas, uma por vez. Cada script ou guarda nasce com teste; cada erro vira lição em arquivo (marque "reincidiu" quando repetir); atualize as specs do git e aposente as skills obsoletas; meça de novo depois de cada etapa e compare com o modelo de custo; ao final, rode o linter de orçamento e registre o resultado no handover.