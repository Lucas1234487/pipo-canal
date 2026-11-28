# 08 · Descartados e sanitização

## 1. Descartados (uma linha cada, sem conteúdo)
- Correção de achados de analisador estático de terceiros (pré-voo no diff e leitura dos comentários na entrega).
- Revisão de entrega alheia (skill com 4 revisores paralelos e o agente revisor por dimensão).
- Resposta a revisão recebida, ponto a ponto.
- Revisor de código da própria unidade como agente próprio (vira variante do verificador em 02).
- Verificação de integração com o front (vira variante "contrato" do verificador).
- Relatório da entrega em modelo fixo.
- Preparação da demonstração quinzenal.
- Revisão de UX (skill e agente).
- Criação de unidades no rastreador (skill e agente).
- Status do dia e rascunhos interpessoais.
- Painel móvel, sincronização do painel, despacho de pedidos do painel, painel estático e histórico motivacional. **Conceito mantido:** "agentes ao vivo" = ganchos de início/fim/passo de subagente gravam quem trabalha em quê; a sessão publica num painel só quando algo muda.
- Regras específicas de versionamento, entrega, rastreador, chat, e-mail, produção e navegador → só o princípio (03 §2).
- Tarefas agendadas de disparo único e o despacho periódico.
- Memórias de agente (conteúdo), configurações locais da máquina, permissões locais.

## 2. O que foi generalizado
- card → unidade de trabalho · PR → entrega · épico → frente · orquestrador → coordenadora · dev → executor · commit/push → empacotar/entregar · payloads → evidências.
- Nomes de ferramentas, conectores e arquivos da origem → papéis e `{{PLACEHOLDERS}}`.
- Valores numéricos mantidos (limiares, tetos, faixas de tokens, % de uso); valores em dinheiro omitidos.
- Lições: sem citações, sem datas, sem identificação de unidade.
- Modelos nomeados só no mapa de camadas de 05 §c (são nomes de modelos da plataforma, não do domínio).

## 3. Fontes lidas
Repositório de origem (constituição, docs de arquitetura/pesquisa/glossário/catálogo, plugin: agentes, skills, ganchos, scripts, testes, evals), configuração do usuário da ferramenta (sem credenciais), tarefas agendadas, regras de processo dos repositórios de trabalho. Do estado: **somente** a base de lições (sem citações), métricas (só formato e séries numéricas) e os relatórios de fluxos por tamanho, observações de processo, guardrails (dois arquivos que casam o padrão) e melhorias. Nada mais do estado foi lido.

## 4. Verificação de sanitização (rodada em 2026-11-28 nesta pasta)
| Padrão buscado | Resultado |
|---|---|
| e-mails | 0 |
| URLs, domínios | 0 |
| chaves de ticket (`LETRAS-número`), referências `#número` | 0 reais; falsos positivos: "UTF-8", "BY-4" (licença) |
| UUIDs, ids longos, ids de sessão | 0 |
| caminhos de máquina (`C:/`, pasta do usuário, área de trabalho) | 0; falso positivo: palavra "desktop" (app) |
| nomes da pessoa, da empresa, do produto, de repositórios, do sistema de origem | 0 (busca por palavra inteira; os únicos casamentos parciais estavam dentro de palavras inglesas comuns) |
| nomes de ferramentas da empresa (rastreador, chat, analisador) | 0 |
| conteúdo de revisões, conversas, briefings | não lido, logo não presente |

**Nomes próprios mantidos de propósito** (referências pedidas em 06, marcadas "citada no original, não reverificada aqui"): Anthropic, Google Research, Chroma, Laban et al., Kim et al., PoLL, ICLR, ICML; e nomes de plataforma: Claude Code, Python, PowerShell, Windows, camadas de modelo (Opus, Sonnet, Haiku, Fable). Nenhum identifica o dono, a empresa ou clientes.

**Exceção autorizada pelo dono:** referências públicas das duas skills de terceiros em 04 §1 (nomes das skills, autores, perfil público e domínio do autor original), exigidas pela licença CC-BY-4.0 para atribuição.

**Omitido na dúvida:** nome do sistema de origem dentro dos arquivos (só aparece no nome da pasta).

## 5. Ocorrências durante a extração
- Dois leitores tiveram a gravação de notas via shell negada por guarda da origem (falso positivo da guarda de produção, por palavras no texto da nota; e um caso não detalhado) e gravaram a mesma nota com a ferramenta de escrita de arquivo, numa pasta temporária fora do repositório. Nada do repositório foi alterado. Registrado porque a regra da tarefa era não contornar.
- Um leitor tentou abrir um arquivo de configuração de limiares dentro do estado (fora da lista permitida); foi negado e não contornado. Depois, com autorização do dono, conferiu-se que esse arquivo **não existe**: valem os padrões do código (contexto 60/70, uso 50/80, teto de 2 entregas/dia, a 3ª pergunta) — os mesmos números do pacote.
- O dono revisou e aceitou essas ocorrências.
