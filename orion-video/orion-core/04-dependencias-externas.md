# 04 · Dependências externas

Tudo que o sistema de origem lê, chama ou pressupõe, inclusive fora do próprio repositório. `[CC]` = conferido em 2026-11-28/2.1.288.
Classes: **PORT** portável · **ADAP** adaptável (trocar valor/nome) · **ESP** específico de código/empresa (não vai).
Placeholders: `{{HOME}}` pasta do usuário da ferramenta · `{{RAIZ}}` repositório do sistema · `{{PLUGIN}}` pasta do plugin · `{{REPOS}}` pasta dos repositórios de trabalho.

## 1. Configuração do usuário (`{{HOME}}`)
| Item | Papel | Classe |
|---|---|---|
| Modo de permissão padrão automático, sem listas globais de permitir/negar | as guardas do plugin fazem o freio | ADAP |
| Ganchos globais | não há; todos vêm do plugin `[CC]` | — |
| Linha de status apontando para script do plugin | mede contexto (05 §a) | ADAP (caminho) |
| Plugin habilitado + catálogo local do tipo "diretório" | instala o plugin a partir da pasta do repositório `[CC]` | ADAP |
| Ferramenta de fluxos de trabalho habilitada | orquestração opcional | PORT |
| Sobrescritas que desligam skills de terceiros conflitantes (fala comprimida, planejador por fases, descobridor de skills) | evita estilo concorrente com o pipeline | ADAP |
| Permissões locais extras (2 regras) | específicas da máquina | ESP |
| Agentes globais | não há; vêm do plugin | — |
| Memória de agente: uma pasta por especialista, índice + arquivos curtos (feedback, armadilhas, padrões de defeito) `[CC]` | aprendizado do papel entre unidades | estrutura PORT; conteúdo ESP (não levar) |

### Skills de terceiros de que o sistema depende — **o destino deve buscá-las e instalá-las**
| Skill | Papel | Referência | Classe |
|---|---|---|---|
| `the-jury` v1.0.0 — 3 a 5 jurados com voto cego, deliberação anônima contra ancoragem e bajulação, veredito único com confiança e dissidência; traz script de contagem e guia de deliberação | **dependência obrigatória** do júri padrão e do moderador (02/moderador-juri.md) | autor Felipe Rodrigues (perfil `felipfr` no GitHub); licença CC-BY-4.0 | PORT — manter atribuição |
| `learning-opportunities` v1.1.0 — exercícios curtos e opcionais de aprendizado depois de trabalho de arquitetura | regras de repositório mandam rodar ao fim da tarefa (04 §6, regra 11) | autor original Chris Hicks (fightforthehuman.com); adaptação de Felipe Rodrigues (`felipfr`); licença CC-BY-4.0 | PORT — manter atribuição |
Busca sugerida: perfil `felipfr` no GitHub ou pelos nomes acima num catálogo público de skills. Não copiar o texto delas para dentro do pacote; instalar na pasta de skills do usuário `[CC]`. A skill de júri cita uma irmã que só critica sem decidir (`the-fool`), não usada pelo sistema.

## 2. Tarefas agendadas `[CC]` (só rodam com o app aberto e travam em pedido de permissão)
| Tarefa | Quando | O que faz | Classe |
|---|---|---|---|
| rotina da manhã | dias úteis, início do expediente | lê constituição e skill de rotina; período desde a última; gera briefing | ADAP |
| rotina do meio-dia | dias úteis, meio do dia | acrescenta seção ao briefing | ADAP |
| rotina da tarde | dias úteis, fim do dia | fecha com "fica para amanhã"; roda verificar/limpar da base de lições | ADAP |
| despacho de pedidos do painel | era a cada 10 min; passou a rodar ao fim de cada rotina | atende pedidos feitos no painel móvel | descartar (conceito em 08) |
| sucessor pós-aposentadoria | disparo único na manhã seguinte | abre o sucessor e roda a rotina da manhã lendo o handover | padrão PORT, instância ESP |
| retomada após limite | disparo único | reabre trabalho quando o limite libera | ESP |
Todas embutiam caminho absoluto e nomes de pessoas → parametrizar. Regra: a rotina agendada só lê e grava arquivos próprios.

## 3. Conectores (só o papel)
| Papel | Uso | Classe |
|---|---|---|
| rastreador de unidades de trabalho | ler unidades do dono; escrever só com guarda (cotas, só itens próprios, transições combinadas) | ADAP |
| suíte de e-mail, agenda e chat corporativo | ler; enviar/rascunhar/apagar só com aprovação | ADAP |
| reuniões gravadas | ler decisões e ações | ADAP |
| navegador automatizado | testes de interface com confirmação, nunca produção | PORT |
| gestão de sessões do app | abrir gerentes, mensagem entre sessões, consultar uso do plano `[CC]` | ADAP |
| tarefas agendadas | criar/editar as rotinas (sob guarda) | PORT |
| banco de página publicada | painel do celular | descartar |
| hospedagem de código por CLI | listar entregas, verificações, comentários (leitura) | ADAP |
Matcher genérico por função (`mcp__.*__<função>`), nunca por id de conector.

## 4. Arquivos do plugin — o que cada um garante
| Peça | Garante | Classe |
|---|---|---|
| manifesto do plugin | nome, versão semântica, descrição, autor, palavras-chave; agentes/skills/ganchos descobertos por convenção de pastas `[CC]` | PORT |
| catálogo (marketplace) de 1 plugin com origem relativa | instalação local `[CC]` | ADAP |
| lista de ganchos | ~19 entradas, todas "interpretador + script em `${CLAUDE_PLUGIN_ROOT}` + modo" `[CC]` | PORT |
| guarda de política | modelos, saída externa, produção, banco, navegador, rastreador, versionamento | ADAP |
| guarda de disciplina | aposentadoria, publicação após verificação, mensagens, agendamentos, paralelismo, gerente único, ignorados, registro pós-ação | ADAP |
| registro de agentes ao vivo | quem trabalha em quê; injeta lições e ignorados no início de sessão | só a injeção é PORT |
| script do quadro | CRUD do estado com trava; pré-condições (03 §2) | PORT (tirar consulta fixa a uma organização) |
| consolidador de fontes | funde leituras do dia no quadro | PORT |
| base de lições | 03 §4 | PORT |
| linter de orçamento | 05 §f | PORT |
| script de linha de status | 05 §a | PORT |
| gerador de painel estático | HTML único a partir do estado | PORT (opcional) |
| painel móvel, histórico motivacional, link para chat, pré-voo de analisador estático de terceiros | — | ESP / descartar |
| 10 suítes de teste | 03 §5 | PORT (casos reais ESP) |

## 5. Caminhos, variáveis e ferramentas
- Caminhos absolutos embutidos em ~todos os scripts, ~12 agentes/skills, tarefas agendadas e servidor de preview → trocar por `{{RAIZ}}` relativo ao plugin. Lista de raízes permitidas na guarda de shell → `{{REPOS}}`.
- Variáveis: raiz do sistema; glob dos planos dos repositórios; desligar consultas à hospedagem (modo teste); depuração do registro ao vivo — PORT/ADAP. Da ferramenta `[CC]`: raiz do plugin; id local da sessão (para o gerente se registrar). Nenhum segredo lido por variável.
- Ferramentas: Python 3 (forçar UTF-8 no console Windows) · git · CLI da hospedagem · CLI da própria ferramenta (validar plugin estrito, eval) `[CC]` · PowerShell como shell secundário · comandos de build/teste dos repositórios-alvo (ESP). Servidor HTTP local só para preview do painel (ADAP).

## 6. Regras de PROCESSO que o gerente obedece nos repositórios de trabalho (genéricas)
| # | Regra | Classe |
|---|---|---|
| 1 | Reler as regras e a especificação da área no início de toda tarefa, mesmo de uma linha | PORT |
| 2 | Passo 1: parar antes de editar e perguntar base, nome do ramo, escopo dos exemplos e se haverá QA independente; nunca supor | PORT |
| 3 | Proposta antes de implementar: contratos + lista completa de testes, uma linha cada, **bordas primeiro**; esperar aprovação | PORT |
| 4 | TDD parcial: esqueletos → todos os testes → implementação; sem pular teste; dublês escritos à mão | ADAP |
| 5 | Texto ao usuário final: base e versão mais calorosa lado a lado; não reescrever textos antigos de carona | PORT |
| 6 | Comentários raros e curtos | PORT |
| 7 | Gate: build + testes com 0 erro e 0 aviso, saída real; nunca "verde" sem rodar | ADAP (comando) |
| 8 | QA independente: agente novo; relatório analisado com opinião por achado; nada muda sem aprovação; só a 1ª rodada explora | PORT |
| 9 | Versionamento nunca autônomo; uma mudança por responsabilidade; nunca stage em massa nem credenciais | PORT |
| 10 | Entrega com exemplos de uso prontos (requisição feliz, de erro, resposta esperada) | ADAP |
| 11 | Fechamento em 3 blocos (feito; regra → onde vive e qual teste a fixa; riscos, o que não tem teste, ordem de implantação) + registrar armadilha nova nos docs ou dizer "nada novo" | PORT |
| 12 | Sem testes possíveis (jobs de dados): revisão do diff é o teste — reexecução duplica? toca outro escopo? esvazia o destino se a fonte vier vazia? Idempotência obrigatória | PORT |
| 13 | Copiar o irmão correto mais novo em vez de inventar padrão | PORT |
| 14 | Não construir sobre o que não existe; dúvida de domínio se levanta, não se inventa | PORT |
| 15 | Idioma: conversa no idioma do dono; identificadores e mensagens de versão em inglês | ADAP |
| 16 | Cada repositório tem uma pasta de especificação (arquitetura, testes, convenções, preocupações, estrutura) | modelo PORT, conteúdo ESP |
| 17 | Integração em ramo de integração = implantação; convenção de ramo com chave da unidade | ESP |

Origem desta tabela: 5 arquivos de regras em repositórios de trabalho. Havia uma cópia duplicada em duas pastas: o conteúdo é idêntico, com o mesmo último commit e nenhuma versão mais nova nas referências locais (conferido pelo histórico do git, sem buscar no remoto). Havia também uma cópia antiga e fora do controle de versão de outro repositório; ela não muda nenhuma regra de processo acima.
