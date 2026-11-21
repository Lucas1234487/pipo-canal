# Decisões pendentes (só o Lucas decide)

21/11/2026. Seis itens. Até você responder, o pipeline usa a opção marcada como padrão.

## 1. Um canal/perfil ou separado por idioma

- A) Um canal no YouTube com faixa de áudio EN e um perfil PT no Instagram.
  - Pró: soma todas as views num canal só, o que ajuda a bater o YPP mais rápido.
  - Contra: a legenda queimada em PT aparece para quem ouve em inglês, e a faixa EN só sobe à mão pelo Studio.
- B) Dois canais no YouTube (PT e EN, cada um com legenda queimada própria) e um perfil PT no Instagram.
  - Pró: cada versão fica nativa, com legenda queimada e horário próprios, e o EN mira o RPM dos EUA.
  - Contra: divide as views e o canal EN começa do zero.
- C) Dois canais e dois perfis.
  - Pró: o EN fica completo nas duas redes.
  - Contra: dobra o trabalho, e um perfil EN no Instagram quase não dá receita.

Recomendação: B (é o padrão). A legenda queimada é inegociável para o público, e isso inviabiliza a A. O perfil EN no Instagram fica para reavaliar em 60 dias.

## 2. Licença da voz (Azure)

Verifiquei na web: os termos da Microsoft só dão direito de uso comercial do áudio das vozes neurais a quem usa o nível pago. Moderadores da Microsoft confirmaram que o F0 (grátis) é para teste e não dá esse direito. O edge-tts também não tem licença comercial.

- A) Azure pago (S0 ou pague pelo uso).
  - Pró: licença comercial, as mesmas vozes (Antonio incluída), SSML completo e estabilidade.
  - Contra: precisa de cartão. O custo fica em poucos dólares por mês para uns 150 a 250 mil caracteres (confirmar a tabela ao criar a conta).
- B) Continuar no edge-tts grátis.
  - Pró: custo zero.
  - Contra: risco contratual, e o endpoint pode cair sem aviso.
- C) Voz open source com licença comercial (Piper ou Kokoro).
  - Pró: grátis e legal.
  - Contra: qualidade em PT-BR abaixo da Microsoft e soa mais monótona.

Recomendação: A antes do primeiro vídeo público. Até lá, o edge-tts serve só para os testes.

## 3. Plano do Metricool

São cerca de 120 posts por mês só no PT (2 vídeos × 2 redes × 30 dias), mais uns 60 no canal EN. Na opção 1B são 2 marcas.

- A) Plano grátis.
  - Pró: custo zero.
  - Contra: 1 marca e um limite de posts por mês muito abaixo do volume (o relatório 11 fala em 20).
- B) Starter.
  - Pró: várias marcas e posts suficientes.
  - Contra: pela pesquisa, o acesso à API completa fica no Advanced.
- C) Advanced.
  - Pró: API e relatórios avançados, bom para o agente de engajamento.
  - Contra: mais caro. Uma comparação de terceiros cita cerca de US$ 53 por mês no plano anual.

Recomendação: B. Antes de assinar, confira na página do Metricool se a conexão que já usamos (via MCP) e a análise de métricas funcionam no Starter. Se não funcionarem, vá de C. Não consegui confirmar os preços atuais na página oficial.

## 4. Duração dos vídeos de conhecimento

- A) Alvo de 55 s, como recomenda o relatório 03.
  - Pró: mais alcance, mais conclusão e menos render.
  - Contra: alguns temas ficam rasos.
- B) 60 a 90 s livre, como você decidiu.
  - Pró: dá espaço para história e mais salvamentos.
  - Contra: as views caem bastante acima de 60 s.
- C) Alvo de 60 a 70 s, com 75 a 90 s só quando o tema tem uma virada real no meio, e revisão depois de 30 vídeos.
  - Pró: equilíbrio.
  - Contra: exige disciplina do roteirista.

Recomendação: C (é o padrão).

## 5. Pipo mudo ou falante

- A) Mudo: um narrador fora de cena fala com ele e sobre ele.
  - Pró: mais adulto, sem re-render da boca por idioma, e as duas personas preferiram assim.
  - Contra: menos "personagem que conversa".
- B) Fala, com uma boca simples de linha fina.
  - Pró: mais conexão, como defende o relatório 02.
  - Contra: risco de parecer fantoche infantil e mais trabalho na versão EN.
- C) Mudo no conhecimento e falante só no humor.
  - Pró: testa as duas formas.
  - Contra: o personagem fica inconsistente.

Recomendação: A (é o padrão). Os olhos e o corpo carregam a expressão, e a espiguinha e a menininha reagem.

## 6. Voz masculina PT e regra de gênero

Amostras em /home/claude/canal/pesquisa/vozes/:
- PT_M_AntonioNeural_r8_pm4.mp3
- PT_M_BrianMultilingualNeural_r8_pm4.mp3
- PT_M_AndrewMultilingualNeural_r8_pm4.mp3
- PT_F_ThalitaMultilingualNeural_r10_p3.mp3
- EN_M_US_AndrewNeural_r8_pm4.mp3
- EN_F_US_EmmaNeural_r10_p3.mp3
- mix_demo_PT_leve.m4a (para ouvir o volume no celular)

Opções para a voz masculina PT:
- A) Antonio com tratamento (+8%, -4 Hz, EQ e pausas).
  - Pró: é a sua preferida e é nativa.
  - Contra: os relatórios 02 e 09 a associam a "vídeo de fábrica" do TikTok BR.
- B) Brian ou Andrew Multilingual.
  - Pró: soam menos batidos, e o Andrew pode ser o mesmo narrador em PT e EN.
  - Contra: podem ter sotaque gringo. Um brasileiro precisa ouvir antes.
- C) A/B de 2 semanas, Antonio tratado contra Brian, medindo a retenção nos 3 primeiros segundos.
  - Pró: decide pelo dado.
  - Contra: atrasa a marca sonora em 2 semanas.

Regra de gênero ("sério = masculina, leve = feminina"): a persona adulta percebeu e achou antiquada. A alternativa é escolher a voz pelo tipo de narrador (seco, calmo, irônico), por exemplo uma narradora séria nos vídeos de dinheiro.

Recomendação: C (é o padrão), com a Thalita como feminina e a Francisca fora. Sobre a regra de gênero, mantenho a sua decisão, mas sugiro liberar uma narradora séria nos vídeos de dinheiro como teste.
