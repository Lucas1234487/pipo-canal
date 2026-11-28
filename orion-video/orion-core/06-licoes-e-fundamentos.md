# 06 · Lições e fundamentos

`[CC]` = conferido em 2026-11-28/2.1.288. Referências externas: **citada no original, não reverificada aqui**.

## 1. Lições generalizadas (problema → regra → como virou garantia)
Base de origem: 37 lições — 21 ativas, 15 garantidas, 1 pendente. Garantias: guarda 13 · sem garantia 9 · só injeção no início de sessão 5 · skill 4 · constituição 3 · script 2 · revisão 1. As que mais voltaram: roteamento de aprovação entre sessões e aposentadoria.

| Tema | Problema | Regra | Garantia |
|---|---|---|---|
| aprovação | pergunta de permissão presa na janela de sessão filha | sobe à coordenadora, que pergunta e devolve | guarda G-ASK (garantida) |
| aprovação | na troca de coordenadora a pergunta ficou presa | pedido gravado; a nova leva ao assumir | guarda G-ASK (ativa) |
| aprovação | pedido sem dizer o que o comando faz | 1 linha: o que faz e por quê | injeção |
| sucessão | sucessor conversava com o antecessor aposentado | ninguém fala com aposentado; dúvida vai ao dono | guarda G-MSG |
| sucessão | sucessor registrou e parou; aviso negado ficou "reenvio depois" | ao assumir, conferir que cada aviso chegou | texto |
| sessões | sessão nova nascia filiada e acordava o criador | desanexar logo e mover ao grupo certo | skill |
| registro | escolha do dono só no quadro | também no arquivo da unidade e no destino | script (garantida) |
| registro | regra nova só na conversa/memória | vira guarda com teste + lição; memória não basta | injeção |
| comunicação | status inútil entre sessões | só decisão, bloqueio, entrega | guarda (garantida) |
| comunicação | explicou em vez de corrigir quando ouviu "já combinamos" | conferir, corrigir, testar, registrar | injeção |
| comunicação | gerente falava direto ao dono | só pela coordenadora ativa; sem ela, parar | skill |
| contexto | coordenadora passou do limite | aposentar > 60% terminando o que está no fim | guarda G-APOS (garantida) |
| publicação | anúncio antes da verificação | só depois do pré-voo | guarda G-PUBL (garantida) |
| escopo | risco de mexer em item alheio | só itens do dono ou do sistema | guarda (garantida) |
| ritmo | volume de entregas | 2–3/dia; defeito de QA humano fura o teto | guarda (garantida) |
| ritmo | guarda contou defeito sem unidade e perguntou à toa | classificar defeito fora da contagem | guarda (garantida) |
| processo | defeito pontual e doc no processo pesado | trilhas aprovadas no passo 1 | skill |
| júri | correção contestada seguiu sem júri | contestação → moderador + júri antes do dono | skill |
| verificação | itens "corrigidos" voltaram | "corrigido" só com teste verde | injeção |
| estado | "falta entrega" afirmado quando já existia | conferir fonte; quadro recusa sem flag | script P-REGRESS (garantida) |
| tokens | verificação repetida em mudança só de doc | não repetir sem mudança de código | guarda G-IDEMP (garantida) |
| tokens | listar metadados do rastreador a cada ação | ids fixos, campos curtos | guarda (garantida) |
| tokens | 2º gerente na mesma frente | um ativo por vez | texto (→ G-GER1) |
| uso | semana podia esgotar antes do fim | ~20% do semanal por dia útil, sem teto seco | texto |
| uso | dia com 2 unidades gastou ~29 pontos semanais | executor novo por rodada; regressão = 1 QA intermediário; bancada numa passada | texto |
| agendamento | retomada por suposição de horário falhou | usar o horário de reset informado | texto |
| leitura remota | rotina parava pedindo aprovação para consulta de leitura | leitura não pergunta; só mutação | guarda (garantida) |
| QA | processo de QA | após gate verde; opinião por achado; 1ª rodada explora | guia do repositório (garantida) |
| qualidade estática | achados chamados de "falso positivo" | zero achados; impossível vai ao dono com motivo | skill |
| textos | texto ao usuário final se contradizia | separar o que o assistente consulta do que a tela mostra | revisão |
| escopo | "em paralelo" lido como abrir unidade nova | confirmar quantas entregas saem no dia | texto |
| arquitetura | vários orquestradores? | um orquestrador na frente, demais em 2º plano; estado em arquivo local com limpeza | constituição (garantida) |
| entrega | envio normal de ramo do sistema repassado ao dono | envio normal após aprovação é do sistema; só o forçado vai ao dono | texto |
| painel | indicador de concluídos parado | tem que andar; conferir na próxima rotina | pendente |

**Ciclo da base:** reclamação/correção/"não devia ter que avisar" → `adicionar` **na hora** → erro repetido → `reincidiu` → quando há guarda com teste nomeado → `garantir` (sai do contexto) → `verificar` diário (teste sumiu/falhou → volta a ativa) → `limpar` aposentadas > 30 dias. Retro: lição ativa > 14 dias vira guarda ou é aposentada se já está em texto sempre carregado.

## 2. Diário de observações de processo (formato)
Arquivo markdown incremental por frente, escrito pelo gerente durante o trabalho; lido pela retro de melhorias, que só aplica com OK.
```
N. **[gargalo|token|tempo|erro|número] observação curta**
   Evidência: fatos com números (contagens, tokens, minutos)
   Proposta: ação (esforço: baixo|médio|alto)
   [Aplicado em <data>: o que mudou · versão do plugin · resultado dos testes]
```
Seções por data: Gargalos · Gasto de token · Tempo · Erros frequentes · Números do dia.
Achados genéricos recorrentes:
- **gargalo:** decisão miúda vira volta inteira; troca de gerente perde opinião dada só no chat (gravar antes de sair); guarda lendo heredoc/aspas como argumento.
- **token:** respostas sem filtro de campos; executor reaproveitado; relatórios longos lidos inteiros; moderador caro.
- **tempo:** empacotar mudanças por trecho de arquivo (~13 min para 8 pacotes) → plano de pacotes já na proposta; ambiente de exemplos remontado por unidade → ambiente fixo.
- **erro:** unidade promete o que o código não tem → revisor cético confere cada critério e cada "já existe" com busca; pinos de teste esquecidos → planejador busca cada texto/padrão alterado; correção quebra vizinho → brief exige o contraste mais próximo; dublê esconde o real → exemplos ponta a ponta **antes** do QA R1; padrão de texto amplo dispara em pergunta neutra → 3 neutros por padrão novo.

## 3. Fundamentos da pesquisa → o que muda no desenho

**Plataforma** (documentação da ferramenta, todos `[CC]`)
1. Subagente cria subagente até 3 níveis → orquestrador→gerente→especialista é nativo.
2. Subagente termina com a tarefa; sessão persiste → gerente = sessão, especialista = subagente.
3. Sessão acordada por mensagem não abre sessões → só a coordenadora, em conversa, abre gerentes.
4. Agente declara modelo, ferramentas, memória, isolamento em árvore própria e skills → cada papel é um pacote com memória própria.
5. Dá para restringir quais agentes um agente cria → especialista não cria fora do papel.
6. Ganchos pré-ferramenta com permitir/perguntar/negar → regra crítica vira código.
7. Instrução de chat some na compactação → estado e regras em arquivo.
8. A linha de status expõe % de contexto → aposentadoria mensurável.
9. Tarefas agendadas só rodam com o app aberto e travam em permissão → rotina agendada só lê e grava o próprio estado.
10. Existem validação estrita de plugin e diagnóstico → "doctor" de cada peça.
11. Eval de plugin usa juiz pequeno e publica relatório por padrão → rodar com juiz intermediário e sem publicar.
12. Times de agentes experimentais, sem aninhamento → não usar; o gerente faz o repasse.

**Literatura** (citadas no original, não reverificadas aqui)
13. Dividir por tipo de trabalho costuma piorar; cada passagem perde fidelidade → dividir por contexto (Anthropic, *Building multi-agent systems: when and how to use them*).
14. Multiagente custa 3–15× tokens; ajuda no paralelizável e piora no sequencial (quedas de 39–70%); orquestrador central contém a amplificação de erros (~4× contra ~17× sem) → paralelo só entre etapas independentes (Anthropic, *How we built our multi-agent research system*; Google Research, *Towards a science of scaling agent systems*).
15. Agente elogia o próprio trabalho; verificador novo e cético funciona, mas sofre "vitória precoce" → verificador sempre novo, critérios explícitos, suíte completa (Anthropic, *Harness design for long-running apps*).
16. Contexto longo degrada mesmo sem compactar → aposentar cedo, sucessão em arquivo (Laban et al., ICLR 2026, conversas multi-turno; Chroma 2025, "context rot").
17. Brief de subagente precisa de objetivo, formato de saída, fontes e limites; resultado em arquivo → modelo de brief (Anthropic, *multi-agent research system*).
18. Humanos rejeitam muito mais planos que ações → aprovação humana no plano; o resto em lote (Anthropic, *Measuring agent autonomy*).
19. Júri heterogêneo supera homogêneo, mas o ganho vem do voto cego e de seletor com critérios; debate pode trocar resposta certa por errada; mesmo provedor erra junto → júri com voto cego e calibração (PoLL 2024; *When Agents Disagree* 2026; Kim et al., ICML 2025).
20. Assistente de rotina precisa da lista do que já foi tratado; modelos superestimam urgência de e-mail → quadro guarda o tratado; filtro "ganha/participa/pedido a mim" (relatos genéricos de "secretária de IA").

**Dores medidas nas sessões de origem**
21. Contexto perdido em várias compactações → estado em arquivo; gerente aposenta na 1ª compactação.
22. Pedidos repetidos (mesmo modelo colado várias vezes; "onde paramos?" ~9×) → skills fixas + quadro.
23. Coordenação manual entre sessões; dois agentes na mesma pasta → dono do contexto; um escritor por árvore.
24. Rodadas de QA com retorno decrescente → só a 1ª explora.
25. Automação anterior que enviava mensagens sem supervisão foi bloqueada pela política da ferramenta → o sistema nunca envia sozinho.
26. Skill de terceiros importada apontava para pastas inexistentes → adaptar ao layout real antes de adotar.
