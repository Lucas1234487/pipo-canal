# G7. Redes sociais: Instagram, Facebook e perfis (pedido do Lucas, 26/11)

O Diretor é dono de TUDO que aparece nas redes, não só dos vídeos: perfis, bios, fotos, descrições, posts, stories e interação. Decide sozinho, dentro dos GUARDRAILS, e registra o que mudou no handover. O Lucas só veta.

## Contas (todas no Metricool, brand 8272438)
- YouTube @pipopo.88 (UCTpmIKPlwy4i6nOcaybJ5Yg).
- Instagram @pipo.pop88 (perfil de Criador, categoria Criador de conteúdo digital).
- Página do Facebook "PipoPop" (1491381724050961), ligada ao @pipo.pop88. Admin é o Facebook pessoal do Lucas, mas isso não aparece em público. Nunca postar, curtir ou comentar como o perfil pessoal dele.

## 1. Vídeos (todo dia, G5)
Cada vídeo vai para YouTube + Reel no Instagram + Reel no Facebook, mesmo horário. Regra completa em G5.

## 2. Sincronia e arquivo (decisão do Lucas, 26/11)
As 3 redes andam no mesmo passo: Instagram e Facebook usam SÓ os horários do YouTube (tabela do 03_CICLO). Pode sair mais de um Reel no mesmo horário no Instagram/Facebook. Vídeo que já saiu no YouTube e ainda falta no Instagram/Facebook entra no próximo horário da tabela, junto com o vídeo novo, até zerar a diferença. Nunca repostar vídeo datado que perdeu o sentido. Controle em docs/diretor/redes/arquivo.md.

## 2b. Todo vídeo publicado fica salvo no git (Lucas, 26/11)
- Nenhum vídeo publicado pode existir só no YouTube. O upload.mp4 de todo vídeo que vai ao ar fica na branch `fila` (pasta do dia ou fila/arquivo/<data>_<slug>/) e NUNCA é apagado, nem na limpeza de disco.
- Se aparecer no Studio um vídeo sem arquivo no git (ex.: subido à mão pelo Lucas), baixar pelo Studio (Opções > Baixar, no Chrome dele), pedir que ele ponha no Drive "Pipo - Canal" e subir para fila/arquivo/.

## 3. Posts de imagem e carrossel (memes)
- 2 a 4 por semana no Instagram e no Facebook (type POST). Fontes: memes da Pipo de kit2d/memes.py, quadro mais forte de um vídeo com frase nova, curiosidade em carrossel (3 a 5 lâminas, 1080x1350).
- Renderizar em PNG, subir na branch `fila` em social/AAAA-MM-DD_<slug>/ e usar a URL raw no Metricool. isAiGenerated true.
- Meme segue GUARDRAILS (só estrutura redesenhada, nada de imagem original de terceiro). Legenda curta com pergunta.

## 4. Stories (todo dia que tiver vídeo novo)
- 1 a 3 stories por dia no Instagram e no Facebook (type STORY): chamada do vídeo do dia (quadro de 1080x1920 com "vídeo novo" e a pergunta), bastidor (rascunho de cena, Pipo estourando), meme do dia.
- Story vai sem texto no post (o texto fica desenhado na imagem). Enquetes e caixinha de pergunta não saem pela API: se o Chrome do Lucas estiver aberto, dá para fazer pelo navegador; senão, pergunta escrita na arte e resposta nos comentários do vídeo.

## 5. Interação
- Comentário do canal em todo post (firstCommentText = comentario_fixado).
- Responder comentários (YouTube, Instagram, Facebook): o Metricool deste conector não responde comentário, então isso é feito pelo Chrome quando ele estiver aberto (sessão de publicação em lote ou qualquer sessão com o Lucas). Tom da Pipo, curto, nunca discutir, nunca responder política, religião ou futebol. Responder primeiro quem perguntou algo.
- Fixar o comentário no YouTube segue G5.

## 6. Perfis (revisão semanal, sessão semanal)
- Bio do Instagram, sobre da página do Facebook, descrição do canal do YouTube, foto de perfil e capa: uma voz só (Pipo, curiosidade + histórias, "todo dia vídeo novo"), até 150 caracteres no Instagram.
- Toda semana o Diretor relê os perfis e muda se os dados pedirem (ex.: tema que mais cresceu). Mudança só pelo Chrome; sem Chrome, anotar o texto pronto em docs/diretor/redes/perfis.md para a próxima sessão com o Lucas.
- Textos atuais: docs/diretor/redes/perfis.md.

## 7. Crescimento com base nos dados
- G6 passa a ler as 3 redes (Metricool getAnalyticsDataByMetrics). O placar compara o mesmo vídeo entre YouTube, Instagram e Facebook.
- Regras de decisão: rede onde um tipo de vídeo vai melhor ganha mais daquele tipo nos stories e posts; horário do Instagram e do Facebook pode se separar do YouTube depois de 14 dias de dados (getBestTimeToPostByNetwork).
- Cada mudança vira linha em docs/diretor/EXPERIMENTOS.md.
