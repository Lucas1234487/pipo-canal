# 02. Guardrails do PipoPop (regras duras para Diretor, gerentes, organizadores, QA e Gemini)

Atualizado em 24/11/2026 com as decisões do Lucas. Este arquivo vale acima de qualquer spec. Mudar uma regra daqui só com o Lucas.

## 0. As 3 regras principais (o que o canal é)
1. **Três pilares por dia, todo santo dia.** Um vídeo de cada: M assunto do momento, H história com regra inventada, C conhecimento. Produção diária mesmo sem o Lucas aparecer.
2. **Estrutura completa, sem exceção.** Diretor -> Gerente de Produção -> organizadores O1 Roteiro e Fala, O2 Cenário, O3 Sonoplastia, O4 Montagem -> QA final (QA-Claude novo + QA-Gemini) -> agendamento. Nenhum vídeo pula o QA final.
3. **Publica sozinho, o Lucas só veta.** O que passa no piso (seção 3) é agendado sem esperar o OK do Lucas. Ele pode segurar qualquer vídeo a qualquer hora (seção 5).

## 0.1 Atualização constante (Lucas, 24/11 15h46)
- FIXO: a Pipo e o elenco principal (presets do humano), a assinatura visual e estas regras.
- VIVO, sempre atualizado com o ambiente: roteiros, regras inventadas, pautas, cenários, memes, reações e sons. O G1 semanal renova a lista de memes/trends em alta (docs/pesquisa/memes_em_alta_*.md) e aposenta o que tem mais de 30 dias sem estar em alta; o G1 diário confere se o assunto do momento ainda está quente.
- Nenhum meme, regra inventada, fundo temático ou gancho se repete no mesmo pilar em menos de 14 dias (o Diretor confere no historico.csv).
- Todo mês o motor ganha pelo menos 2 cenários ou recursos novos, escolhidos pelo que o público respondeu (EXPERIMENTOS.md) e pelo que os organizadores pediram nos bilhetes.
- Padrão de qualidade: "dá pra ver que é IA, mas uma IA que deu trabalho". Imersão (foto real em tela cheia que mergulha no desenho, fundo que é o lugar da história com vida, camadas) vale mais que cena simples.

## 1. Nunca, em hipótese nenhuma
1. Política, religião ou futebol: nem direto, nem indireto, nem na piada, na referência ou na trilha. ÚNICA exceção (decisão do Lucas, 24/11 20h39): o personagem caricato "Neymaro" (preset neymaro), sem nome real, sem escudo, logo, número ou patrocínio, sem ofensa; nenhum outro jogador, time ou partida.
2. Fato falso ou exagerado apresentado como verdade. Todo fato central tem 2 fontes em WORK/fatos.md. Hipótese vai como hipótese. Ficção vai declarada ("imagina um mundo onde...").
3. Conteúdo protegido de terceiros: personagem, logo, música, trecho de vídeo, still de filme/série/jogo/esporte, obra de arte.
4. **Memes:** o formato do meme entra como ESTRUTURA redesenhada no nosso traço (elemento `meme` do kit2d). A foto original de meme famoso NÃO entra: quase toda é foto de stock, frame de filme ou pessoa real, e isso dá reivindicação de direitos e risco à monetização. Texto e piada do meme são livres; a imagem é sempre nossa.
5. **Imagens da internet:** só CC0 ou domínio público, pelo kit/imagens.py (Openverse, NASA), com a proveniência em WORK/img/proveniencia.tsv e crédito na descrição. Nunca pessoa real identificável, marca, obra de arte, foto jornalística.
6. Número inventado em interface que imita a real (curtidas, views, prints). Nada de "parte 2" falsa.
7. Pessoa real (rosto, nome ou voz) sem autorização. Nada que exponha pessoa privada.
8. Senha, código ou chave digitada pelo Claude em site. Chave de API nunca no git (repositório público).
9. Gasto de dinheiro, conta paga ou assinatura sem o Lucas.
10. O Chrome do PC do trabalho (EMS) ou a conta principal do Lucas no Instagram.
11. Copiar a regra inventada de vídeo que já existe (o Lucas reconhece; a do "nome que dá vida" já existe).

## 2. Sempre
- VARIEDADE (política de "conteúdo inautêntico" do YouTube desde 15/07/2025 mira "roteiros em template" e produção em massa): dois vídeos seguidos do mesmo pilar nunca repetem a mesma estrutura de cenas, o mesmo gancho, a mesma paleta de abertura ou a mesma música. O Diretor confere isso no lote do dia contra os 3 anteriores do mesmo pilar.
- A Pipo aparece em todo vídeo e ESTOURA em todo vídeo (o gatilho muda). Ela é feminina (cílios, bochechas, lacinho rosa). Nos 3 pilares ela faz ponta; protagonista só no 4º vídeo, quando ele for liberado.
- Voz que só fala português: pt-BR-FranciscaNeural ou pt-BR-AntonioNeural. Sem sigla nem palavra estrangeira na fala.
- Transições rápidas: corte a cada 2 a 3 s, nada parado mais de 3 s, som em toda entrada.
- Legenda queimada. "Não é conteúdo para crianças". Declaração de IA só nos critérios do YouTube (2D assumido = "Não").
- Histórico, placar, cadernos e handover atualizados; commit e push ao fim de cada ciclo.

## 3. Piso mínimo para agendar (constância > perfeição)
1. kit/qa_check.py aprovado (legenda, zona segura, áudio -14 LUFS, sem quadro preto).
2. fatos.md com 2 fontes por fato central.
3. Nenhum item da seção 1 violado.
4. Quadro 1 com conflito ou pergunta visível sem som.
5. Pelo menos 1 gatilho de interação (curtir, comentar ou compartilhar) escrito de um jeito natural e específico do vídeo (ver specs/G2, "Interação"). Pedido genérico e solto ("deixa o like aí", "se inscreve", "comenta aí") não conta.
6. QA-Claude sem REPROVA e QA-Gemini sem erro grave (fato errado, ofensa, trecho incompreensível, erro de continuidade visível).
Reprovou: uma rodada de correção pelo organizador certo. Reprovou de novo: entra a reserva e o caso vai para o handover.

## 4. Anti-cringe
Nunca "você sabia", nunca fato batido (polvo de três corações, mel que não estraga, 10% do cérebro, galinha é dinossauro), nunca gíria forçada (aura, sigma, rizz, 6-7, brainrot), nunca pedido de interação genérico e solto (ele tem que nascer da história: "comenta se já aconteceu com você", "manda pra quem acende o pisca-pisca em outubro"), nunca chantagem do tipo "só conto o final se der like" (o vídeo sempre entrega), nunca personagem parado enquanto a voz fala, nunca o mesmo susto ou frase em todo vídeo, nunca frases de IA ("fascinante", "mergulhar", "é importante notar"). Lição de moral só no pilar história: uma frase curta, sem sermão.

## 5. Veto do Lucas
- Se o Lucas disser "segura", "não posta" ou reprovar um vídeo em qualquer conversa, a sessão grava fila/<pasta>/segurar.json (motivo, data) e, se já estiver agendado, muda o vídeo para privado no Studio. Nada com segurar.json é agendado.
- A nota e o comentário do Lucas valem mais que qualquer QA e entram no caderno do papel responsável.

## 6. Escalar para o Lucas (só isto)
Login, criação de conta, dinheiro, um guardrail que precise mudar, risco à conta (strike, aviso de política). Todo o resto o Diretor decide e registra.
