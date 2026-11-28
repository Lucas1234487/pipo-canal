# 03 · Guardas e testes

`[CC]` = conferido em 2026-11-28/2.1.288. Classes: **GANCHO** (precisa de gancho) · **PRE** (pode virar pré-condição dentro do script, falha fechada) · **TEXTO** (só texto).

**Meta-regra:** regra nova do dono vira **guarda com teste** sempre que der; texto em skill/constituição é plano B. Motivo: duas regras só escritas foram furadas (contexto passou do limite; anúncio saiu antes da verificação). Guardas são lei: negou → ler o motivo e corrigir; **nunca contornar** por outra ferramenta, sessão ou agente.

Árvore para decidir a forma: (1) precisa ver parâmetros de uma ferramenta ou barrar em tempo de execução → GANCHO; (2) a checagem cabe num script que o agente já chama (registrar, publicar, fechar) → PRE; (3) é julgamento ou estilo → TEXTO + lição "ativa".

---
## 1. Mecanismo comum (como é aplicada)

- Eventos usados `[CC]`: pré-ferramenta, pós-ferramenta, falha de ferramenta, início/fim de subagente, início de sessão (normal, retomada, limpeza, compactação), envio de pedido do usuário, fim de turno, exibição de mensagem.
- Saídas `[CC]`: pré-ferramenta decide permitir/perguntar/negar + motivo (o motivo é lido pelo agente e deve dizer **o que fazer em vez**); injeção de contexto adicional; fim de turno pode bloquear (o modelo continua; respeitar a marca de "já continuando" para não laçar); exibição pode trocar o texto mostrado. Precedência negar > adiar > perguntar > permitir; contexto injetado ≤ 10 mil caracteres; pós-ferramenta não desfaz nada.
- Um script por família, despachado por argumento de modo; JSON do evento no stdin; decisão síncrona com timeout curto (5–15 s); registro/telemetria assíncrono.
- **Falha aberta global:** exceção ou entrada inválida → sai 0 sem decisão (nunca travar a sessão). Exceção: dado essencial ausente → nega com instrução de gerá-lo.
- Configuração: dicionário de padrões no código + arquivo opcional que sobrescreve por seção. Toda decisão vira linha num log JSONL (quando, guarda, ferramenta, decisão, motivo) — material da retro.
- Estado compartilhado com trava por arquivo (criação exclusiva, espera ~2 s, trava órfã > 5–30 s removida) e gravação atômica.
- Higiene de comando de shell (aprendida com falsos positivos): descartar corpo de heredoc, texto entre aspas e comentários antes de procurar comandos; redirecionamentos e pipes não são argumentos.
- Texto injetado deve ser **factual**; tom de "ordem do sistema" pode acionar a defesa contra injeção de prompt `[CC]`.
- Descartados no desenho: bloquear a compactação (viraria erro perto do limite); juiz LLM no fim de turno (custa tokens a cada turno e erra).
- Mudança no script do gancho vale na hora; mudança na lista de ganchos só após recarregar o plugin `[CC]`.

---
## 2. Tabela de guardas exportadas

| Id · Princípio | Aplicação · evento | Parâmetros (valor original) | Testes em prosa | Quando falha | Classe |
|---|---|---|---|---|---|
| **G-MOD** · custo e qualidade por política de modelo | nega/pergunta · pré-criação de agente | assento de júri por marca na descrição; embutidos exigem modelo explícito | menor fora do júri → nega; com marca → passa; topo fora → pergunta; embutido sem modelo → nega; com intermediário → passa | aberta | GANCHO |
| **G-SAIDA** · nada sai em nome do dono sem aprovação | pergunta com resumo de destinatário/assunto · pré-ferramenta sobre lista fechada de ferramentas de escrita externa | lista de ferramentas; resumo 60/300 caracteres | enviar e-mail → pergunta; enviar chat → pergunta; ler → passa | aberta | GANCHO |
| **G-ASK** · aprovação sempre chega ao dono pela porta certa | pré-ferramenta + fim de turno + pós-ferramenta | validade do pedido 3 h; chave = hash curto de sessão+ferramenta+entrada | ver §3 (~16 casos) | aberta (mantém pergunta) | GANCHO |
| **G-PROD** · produção intocável, nem leitura | nega · pré-ferramenta em shell, busca web, navegador | marcador de produção como palavra isolada (variantes "não-produtivo" não casam) | rede/cluster/banco com marcador → nega; variante não-produtiva → passa; ler histórico de versão do ramo de produção → passa | aberta | GANCHO |
| **G-BANCO** · dados reais só se leem | nega · pré-ferramenta em shell | cliente de banco **e** verbo de escrita/DDL | escrita direta e via heredoc → nega; leitura com coluna "updated_at" → passa; SQL só gravado em arquivo → passa | aberta | GANCHO |
| **G-APOS** · sessão longa passa o bastão antes de degradar | 3 camadas: injeção em todo pedido; nega em pré-ferramenta; segura fim de turno; marca na compactação | instruir 60, bloquear 70, janela 1 M, adiar 60 min | ~24: 50% nada; 65% instrui; 75% nega e só handover passa; fim de turno bloqueia uma vez; handover de ontem não vale; de outra sessão da mesma frente não vale; adiar de outra sessão não vale; subagente ignorado; linha de status recente vence transcript; compactação ativa bloqueio | aberta | GANCHO |
| **G-MSG** · sessões não trocam ruído | nega · pré-ferramenta em mensagem entre sessões | intervalo 10 min | status puro → nega; com caminho de arquivo/pedido/pergunta → passa; 2ª mensagem sem sinal < 10 min → nega; destino aposentado → nega; antecessor aposentando ainda recebe dúvidas do sucessor; subagente nominal livre | aberta | GANCHO |
| **G-GER1** · uma frente, um dono | pergunta/nega · abrir sessão | título "Gerente <frente>" | ativo da mesma frente → pergunta; nenhum → passa; sessão acordada por outra sessão → nega | aberta | GANCHO |
| **G-AGENDA** · rotinas automáticas só as aprovadas | pergunta/nega · criar/editar tarefa agendada | lista de permitidas e de desligadas | criar → pergunta; religar desligada → nega; mudar só o texto de permitida → passa | aberta | GANCHO |
| **G-PARAL** · concorrência limitada pelo orçamento | ver 05 §b · criação de executor | 2 / 50 / 80 / 30 min / 2 h | 5 casos (05 §b) | aberta | GANCHO |
| **G-IGN** · o que o dono descartou não volta, nem reescrito | nega edição de briefing/rascunho que cite termo; lembrete no pedido seguinte se a resposta citou sem o dono pedir; injeção da lista no início | termos por item + termos manuais; casamento com borda | briefing citando → nega; sem termo → passa; resposta citou → lembrete; dono perguntou → sem lembrete; referência longa não casa com prefixo curto | aberta | GANCHO + estado |
| **G-PUBL** · nada é publicado antes de verificação aprovada | 3 camadas: pré-ferramenta nega destino; fim de turno bloqueia; exibição retém (respeito do app não confirmado) | 3 fontes do registro; 2º selo obrigatório | ~14: sem verificação → retém e bloqueia; "aprovar com ressalvas" libera; "não aprovar" → pede re-verificação; chave divergente → bloqueia | aberta | GANCHO (+PRE no registro) |
| **G-IDEMP** · não repetir verificação cara sem mudança | nega com escape explícito | flag "código mudou" | 2º pré-voo da mesma entrega → nega; com flag → passa; entrega nova → passa | aberta | PRE |
| **G-REGIST** · pós-ação alimenta guarda pré-ação | pós-ferramenta assíncrono | — | entrega aberta registrada; 3ª do dia pergunta; defeito fora do teto; item criado entra na lista do dono | aberta | GANCHO |
| **P-REGRESS** · não regredir estado sem conferir a fonte | script do quadro recusa (sai ≠ 0) | consulta remota 10 s, desligável | "falta entrega" com entrega registrada → recusa; com flag de conferência → aceita | **fechada** | PRE |
| **P-OBRIG** · registro sem campo essencial não existe | script recusa | — | pré-voo sem selo → recusa; resolver decisão inexistente → recusa | fechada | PRE |
| **T-*** · tom, "conteúdo lido é dado", brincadeira ≠ fato, Parte A/B, classificação idêntico/homólogo/análogo | texto + lição ativa | — | eval de comportamento (§5) | — | TEXTO |

## Regras específicas descartadas — só o princípio
| Origem | Princípio a manter |
|---|---|
| itens do rastreador só do dono, com cotas | só mexer no que é seu ou que o sistema criou; ação de baixo risco combinada passa até um teto diário, acima pergunta |
| git: coautoria, stage em massa, formato da mensagem, plano aprovado, push, base, teto, merge | autoria é do dono; mudança entra por responsabilidade; nunca versionar credencial; aprovação humana **registrada em estado** destrava a guarda; o sistema só altera o que criou; histórico compartilhado nunca; integração final é do dono |
| navegador | automação sempre com confirmação; nunca produção |
| e-mail, chat corporativo | nada sai em nome do dono sem aprovação |
| operações destrutivas remotas | irreversível ou compartilhado → pergunta; leitura por API não pergunta |
| edição de texto pelo shell que corrompe acentos | edição sempre pela ferramenta de edição |

---
## 3. G-ASK em detalhe (a guarda genérica mais valiosa)
Problema: a pergunta de permissão de uma sessão filha prende numa janela que o dono não olha.
1. Toda "pergunta" grava um pedido pendente (chave curta, validade 3 h).
2. Na sessão coordenadora → pergunta normal na tela. Em outra sessão com coordenadora ativa → vira **negação** com a chave e a instrução de enviar à coordenadora uma decisão curta e parar. Subagente devolve a quem o chamou. Coordenadora em troca → pedido fica gravado e a nova o leva ao assumir.
3. O dono responde permitir/negar; a coordenadora grava por comando; o **mesmo** comando rodado de novo consome a resposta **uma vez**.
4. Fim de turno avisa pendências não contadas (uma vez por sessão); pós-ferramenta remove o pedido quando a ferramenta de fato rodou.
Testes: pedido vira pendência; aviso uma vez; pendência some ao rodar; gerente recebe negação com chave; subagente devolve; permitir vale uma vez; negar bloqueia; coordenadora aposentando ainda pergunta na tela; nova coordenadora recebe o pedido da troca.

---
## 4. Estado que as guardas leem (modelos)
- **Item:** chave estável, título, tipo, status (etapas ordenadas de 01 §2 + bloqueado, verificar, feito, não-é-comigo), frente, dono, próxima ação, origem, trilha (só sobe), histórico, notas.
- **Decisão:** id sequencial, pergunta, opções, recomendação, frente, origem, prazo, aberta/resolvida, escolha. Ao resolver, a escolha cai no arquivo de decisões da unidade; se cita outra unidade, também no arquivo de entradas dela.
- **Sessão:** id, frente, título, ativo/aposentando/aposentado, handover.
- **Lição:** id, data, tema, problema, regra, origem (quando, sessão), garantia {tipo, onde, **nome do teste**}, status pendente→ativa→garantida→aposentada, reincidências. Comandos: adicionar · reincidiu (garantida volta a ativa) · garantir · aposentar · resumo (≤ 12 vivas, reincidentes primeiro, injetado no início de sessão) · **verificar** (roda as suítes; garantida cujo teste não aparece como "ok" volta a ativa e sai com erro) · limpar (aposentadas > 30 dias vão a arquivo morto).
- **Consolidação das fontes:** status do quadro só nasce na criação; depois quem manda é o gerente; status da fonte fica ao lado; fonte **à frente** do quadro sobe o status e marca "verificar"; nada ignorado entra; chaves estáveis por hash curto.

---
## 5. Como os testes são organizados
- Um script de teste por família, sem framework: cada caso imprime "ok <nome>" ou "FALHA <nome>"; resumo "N/M"; sai 1 se falhar. **O nome do caso é contrato** (a base de lições confere por nome).
- Isolamento: raiz temporária com estado pré-povoado; o gancho roda como subprocesso com JSON no stdin e variável de ambiente apontando a raiz; rede desligada por variável; transcript falso gerado por função. Nunca toca estado real.
- Guardas: tabela de casos (nome, modo, ferramenta, entrada, decisão esperada) + fluxos de vários passos. Regras de disciplina: cenários sequenciais numa fixture. Cada falso positivo real vira caso nomeado.
- Volume na origem: ~380 casos (guardas ~120, disciplina ~90, registro de agentes ~25, ignorados ~50, demais ~95).
- Lacuna a fechar no destino: nada confere que **toda** regra do texto tem guarda ou lição → criar um lint que liste regras sem par.
- Evals de comportamento (para TEXTO): uma pasta por caso com o pedido exato do dono (poucos turnos, só ferramentas de leitura) e um critério em prosa de passa/falha avaliado por modelo juiz intermediário, sem publicar `[CC]`. Um caso por par de skills confundíveis e um por rotina-âncora.
