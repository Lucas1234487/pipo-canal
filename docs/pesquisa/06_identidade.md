# 06. Identidade e marcas registradas do canal

Agente 6. Data: 21/11/2026. Relatório sem fontes, como pedido. Nenhum estilo foi assumido de antemão (inclusive o clay atual).

## 1. O que a pesquisa mostrou: por que alguns canais curtos são reconhecidos em 1 segundo

Olhei canais de vídeo curto com identidade forte em 3D, animação, curiosidades e humor, e os fenômenos de personagem que se espalharam em 2025 e 2026. O padrão que se repete:

1. **Uma pergunta por vídeo, dita no primeiro segundo.** O maior canal de curiosidades animadas em 3D do mundo (perto de 28 milhões de inscritos) faz sempre a mesma coisa: a pergunta aparece logo de cara, o vídeo responde uma coisa só e termina assim que a curiosidade acaba. Vídeos de 30 s que o público assiste mais de uma vez em média. Título curto, sempre com exatamente um emoji, descrição vazia. A marca dele é o FORMATO, não um logo.
2. **Contraste como assinatura.** O canal de divulgação científica mais reconhecível do YouTube usa cores neon e formas redondas e fofas para falar de temas sombrios (morte, universo, doenças), com trilha alegre por baixo. O choque entre o visual e o assunto é o que fica na cabeça. Tem também bichinhos simples (pássaros) que aparecem em todos os vídeos e uma estrutura fixa em cinco tempos (gancho, chão, crise, virada, alívio).
3. **Visual que ninguém mais tem.** O criador de Shorts 3D que mais cresceu na história da plataforma tinha um 3D escuro, quase realista, e mini-histórias bizarras com menos de 20 s que terminam antes do esperado. A lição dele: "vídeo curto é 99% conteúdo". Ele também diz que vídeo de Short demora até um mês para chegar a 1 milhão e continua rendendo por um ano.
4. **Personagem com design legível + nome sonoro + som próprio.** Os personagens "brainrot" que dominaram 2025 e seguem gerando derivados em 2026 tinham sempre: uma mistura absurda e clara à primeira vista (bicho + objeto), nome com aliteração fácil de repetir, um som ou bordão repetitivo, e um papel fixo (o bobo, o calmo, o vilão). O que mais se espalhou foi o que dava para remixar.
5. **Feito à mão vence "cara de IA".** Animadores independentes que crescem hoje em dia se destacam justamente por parecer feitos por gente. O clay viralizou em 2026 como "anti-slop" porque tem marcas de dedo, imperfeição e movimento levemente travado. O mesmo vale para qualquer material: textura e imperfeição são sinal de cuidado.
6. **O que está perdendo força:** narração genérica de IA em cima de slideshow (está sendo rebaixada em favor de canais com ponto de vista claro), áudios reutilizados por dezenas de milhares de vídeos, e variações derivadas do mesmo meme.
7. **Faceless com personagem consistente** está entre os formatos que se mantêm, junto com explicadores de 45 a 60 s e histórias narradas.
8. **Empresas sem estrela crescem por formato repetível.** Estúdios digitais que não dependem de um apresentador montam formatos que podem render "100 vídeos de 1 milhão cada", e não um viral isolado. O público reconhece o formato antes de reconhecer qualquer pessoa. É exatamente o nosso caso: canal automatizado, sem rosto.
9. **No Brasil, a animação independente está em alta** (séries brasileiras de comédia sombria ganharam versão em inglês e chegaram a grandes plataformas), e o público jovem consome memes de animação e animatics toda semana. Ferramentas de dublagem ampliam o alcance para fora. Ou seja: identidade brasileira não atrapalha o EN, desde que a piada seja visual.
10. **Intro mata Short.** Abertura lenta, fade, vinheta ou "olá pessoal" faz a pessoa passar antes do vídeo começar. A distribuição depende muito da retenção inicial. Logo: a marca tem que estar DENTRO do gancho, nunca antes dele.
11. **Assinatura sonora boa é curtíssima e simples:** 3 a 5 notas, sting de 1 s (as melhores marcas sonoras do mundo têm versão de 1 s), fácil de adaptar a estilos diferentes. Para nós: menos de 0,5 s e tocada por baixo da primeira palavra.

**Conclusão da pesquisa:** marca registrada em vídeo curto = (a) formato fixo reconhecível + (b) um momento visual/sonoro que se repete em todo vídeo + (c) um elemento que o público procura (personagem ou easter egg). Logo e vinheta quase não importam.

## 2. Restrições que filtram as ideias

- Render em CPU: 2,5 a 4 s por quadro a 540x960. Tudo procedural por script (primitivas, skin modifier, displacement, texto 3D, partículas simples).
- Sem lip sync: lip sync por idioma dobra o trabalho e o render. Qualquer personagem deve NÃO falar (narrador fora de cena), ou ter boca tão simples que abre e fecha pela amplitude do áudio num passe de composição.
- Versões PT e EN usando o MESMO render: só trocam áudio e camada de legenda. Então nada de texto em português "queimado" dentro da cena 3D. Números, símbolos e ícones podem.
- Duas vozes (masculina para tema sério, feminina para leve): a identidade não pode depender de uma voz única. Por isso a marca deve estar no visual e no som, não na voz.
- Nada de personagem/marca com copyright, nada de música com direitos: trilha e sons gerados por código ou CC0.

## 3. Três direções de identidade

### Direção A: "Ilha" (diorama em miniatura, sem mascote)

**Ideia central:** todo vídeo acontece em cima de uma pequena ilha circular flutuando no vazio, como um brinquedo de mesa. O assunto muda (um vulcão, um coração humano estilizado, uma cidade, um átomo), mas é sempre construído sobre o mesmo disco. No final, a câmera se afasta e revela onde a ilha está (dentro de um globo de neve, na palma de uma mão de brinquedo, numa vitrine, num prato), o que vira a piada/assinatura de fechamento.

**Estilo visual 3D**
- Paleta: fundo em degradê de azul petróleo (#0F3B4C) para azul acinzentado (#3E6E7E); ilha em tons de areia (#E8D5B0) com detalhes em coral (#FF6B57), amarelo manteiga (#FFD25A) e verde menta (#7ED6B2). Cor de destaque única para "o fato": coral.
- Materiais: plástico de brinquedo acetinado (roughness 0,35 a 0,5), leve bevel em tudo para pegar brilho nas arestas, sem texturas fotográficas. Variação de cor por objeto com ruído suave para não parecer genérico.
- Iluminação: 1 luz de área quente principal a 45°, 1 rim fria por trás, ambiente do mundo em degradê. Sombra de contato macia embaixo da ilha.
- Câmera: lente média (50 a 70 mm), olhando de cima a uns 30°, órbita lenta e constante (assinatura de movimento). Desfoque de profundidade estilo tilt-shift feito na composição com o passe de profundidade (mais barato que DOF no render).

**Personagem:** nenhum. O "personagem" é a ilha. Vantagem: zero problema de consistência de personagem e de lip sync.

**Roteiro assinatura (60 a 90 s, conhecimento; 30 s para humor)**
1. 0 a 1 s: pergunta falada + objeto central já em cena na ilha.
2. 1 a 10 s: "o que todo mundo acha" (o mito ou a resposta óbvia), mostrado na ilha.
3. 10 a 50 s: a verdade em 3 camadas, cada uma é a ilha se transformando (o chão abre, a peça vira corte transversal, a escala muda).
4. Virada: o dado mais absurdo, com a "explosão de escala" (a ilha fica pequena e algo gigante aparece).
5. Fechamento: câmera se afasta e revela onde a ilha está; frase que reconecta à pergunta inicial para o loop.

**Bordões**
- Abertura: sem bordão falado (a pergunta é a abertura). Visual fixo: a ilha "pousa" no quadro com um quique de 6 quadros.
- Fechamento PT: "E isso tudo cabe aqui." / EN: "And all of it fits right here." (dito no recuo final da câmera).

**Assinatura sonora:** um "tóc" de madeira oca + sininho curto quando a ilha pousa (0,4 s), e uma caixinha de música de 3 notas no recuo final. Tudo sintetizado por código.

**Tipografia e legendas:** fonte arredondada e pesada (Fredoka ou Baloo 2, ambas de licença livre OFL). Legenda branca com contorno azul petróleo, 1 a 3 palavras por vez, palavra-chave em coral. Posição a cerca de 60% da altura da tela (acima da zona de interface).

**Easter egg:** uma lesminha minúscula amarela escondida em algum canto de toda ilha. Nunca no mesmo lugar. Gera comentário espontâneo ("achei a lesma em 0:14").

**PT e EN:** perfeito. Nada na cena tem texto, a ilha é universal, o bordão funciona traduzido.

**Viabilidade em CPU:** boa. Fundo é só degradê (render rápido), a cena é pequena e fechada, o tilt-shift é composição. Plástico acetinado em Cycles com poucas amostras + denoiser fica limpo. Ponto de atenção: transformar a ilha em cada vídeo exige uma biblioteca de "módulos" procedurais (montanha, água, prédio, órgão, planeta). Nota de viabilidade: 8/10.

**Riscos:** sem personagem, a ligação emocional é menor; o vídeo de humor bobo fica mais difícil (humor sem personagem depende de objeto, o que é mais fraco). Diorama em miniatura também é um visual que já existe bastante em canais de "mundo pequeno".

---

### Direção B: "Pipo" (mascote que estoura, feltro e massinha)

**Ideia central:** um mascote fixo, o Pipo, um grão de milho de pipoca vivo, redondo, amarelo, com dois olhinhos e pés de palito. Ele vive os temas do vídeo (é picado pelo mosquito, cai no buraco negro, vira astronauta, tenta dormir 8 horas). A regra de ouro: **quando chega o fato mais absurdo do vídeo, o Pipo ESTOURA e vira pipoca.** Na cena seguinte ele volta como grão, como se nada tivesse acontecido. Isso é a marca: o público espera o estouro, e a frase "o Pipo estourou" vira código da comunidade.

Por que funciona (ligando com a pesquisa): é um design misto e legível à primeira vista (grão + criatura), tem nome com repetição sonora, tem um som próprio (o pop), tem um papel fixo (o curioso que se dá mal) e é remixável (o público pode pedir "o que faria o Pipo estourar?"). Também é a tradução visual de "isso explodiu minha cabeça", então serve para conhecimento e para humor.

**Estilo visual 3D**
- Paleta: fundo creme quente (#FFF1DC) ou cenário colorido simples; Pipo amarelo milho (#F7B500) com bochechas laranja (#FF7A2F); pipoca estourada branco creme (#FFF8EC); cores de apoio azul céu (#4FB3FF), vermelho tomate (#E8423F) e verde folha (#55B86A). Sempre a mesma combinação, para o feed do perfil ficar reconhecível de longe.
- Materiais: mistura de feltro e massinha. Feltro (cenários e objetos): base difusa + ruído fino no bump + leve "fuzz" com camada de sheen, sem partículas de pelo. Massinha (Pipo): difuso com displacement de ruído grande e suave (marcas de dedo) e leve brilho. Imperfeição proposital: nada perfeitamente liso.
- Iluminação: luz de janela grande e macia, quente, vinda de um lado; preenchimento suave; sem rim forte. Visual "aconchego de quarto", contrastando com assuntos estranhos ou assustadores (o contraste do canal de ciência mais reconhecido do mundo).
- Câmera: altura do olho do Pipo (câmera baixa, objetos ficam gigantes ao redor dele), cortes secos entre planos em vez de câmera passeando. Animação em "dois" (12 fps reais duplicados para 24), o que dá o charme de stop motion E corta o render pela metade.

**Personagem:** Pipo não fala. Ele reage: arregala os olhos, treme, "aham" com a cabeça, sua. O narrador fala com ele e sobre ele, fora de cena. Isso resolve PT/EN e resolve a troca de voz masculina/feminina (o narrador muda, o Pipo é o mesmo). Pode ter um elenco de apoio mínimo, criado aos poucos e só quando um vídeo pedir (ex.: uma gota d'água ranzinza, um tijolo calmo), todos objetos-criatura simples.

Modelagem por script: esfera achatada + displacement (corpo), duas esferas pretas com brilho (olhos), dois cilindros finos (pernas) com skin modifier, sem braços (ou braços de palito opcionais). Estouro: troca de malha por uma "nuvem" de esferas deformadas com metaballs ou displacement forte + partículas de pedacinhos + sacudida de câmera de 4 quadros. É tudo primitiva, o personagem fica idêntico em todo vídeo porque vem do mesmo arquivo-base.

**Roteiro assinatura**
- Conhecimento (60 a 90 s): "Pergunta no frame 1 com o Pipo já em perigo" > "contexto rápido" > "3 degraus, cada um piora a situação do Pipo" > "fato final: ESTOURO" > "Pipo volta grão, olha para a câmera, frase que reconecta à pergunta (loop)".
- Humor (30 s): "situação comum do dia a dia" > "o Pipo tenta resolver" > "escala absurda" > "ESTOURO" > "volta como grão em outra situação igual (loop)".
- A estrutura fixa "3 degraus + estouro" é a assinatura de roteiro. O público aprende que o estouro vem perto do final, o que segura retenção até lá.

**Bordões**
- Abertura: nada de saudação. A primeira frase é sempre a pergunta, mas pode começar com o nome dele quando cabe: PT "O Pipo vai descobrir o que acontece se..." / EN "Pipo is about to find out what happens if...". Fica natural, curto e vira marca.
- Fechamento: no estouro, o narrador diz PT "Estourou." / EN "Popped." (uma palavra, mesmo peso nos dois idiomas). Opcional no fim: Pipo volta e a última fala reconecta ao começo.

**Assinatura sonora**
- O "pop" do Pipo: estalo seco + leve chiado + nota subindo, menos de 0,5 s. É O som do canal, igual em PT e EN porque não tem palavra.
- Sting de abertura: 3 notas de marimba ou kalimba (algo como dó, mi, sol subindo) por baixo da primeira palavra, 0,4 s.
- Passinhos do Pipo: "tic tic" de madeira toda vez que ele anda.
- Trilha de fundo: loop simples gerado por código ou CC0, sempre do mesmo "timbre" (instrumentos de brinquedo: marimba, toy piano, ukulele), mudando o andamento conforme o tema.

**Tipografia e legendas:** Baloo 2 ExtraBold ou Lilita One (licença livre OFL), branco com contorno marrom escuro grosso e sombra dura deslocada. Palavra-chave em amarelo milho. Cada palavra entra com um "quique" de 3 quadros. Fugir de Montserrat e Bebas Neue, que estão em todo vídeo de template.

**Easter egg:** um grãozinho de pipoca já estourado escondido em toda cena (no chão, numa prateleira, preso no teto). E um contador: no canto da última cena, um pequeno cartaz com o número do estouro ("#47"), em número, que serve para os dois idiomas. O público começa a contar, o que reforça série e coleção.

**PT e EN:** excelente. Personagem mudo, som sem palavra, número no easter egg, bordão de uma palavra. Só a narração e a legenda mudam. O nome "Pipo" se pronuncia igual nos dois idiomas.

**Viabilidade em CPU:** boa a muito boa. Fundo creme ou cenário simples, poucos objetos, animação em dois (metade dos quadros), sem pelos de verdade, sem SSS caro (a cara de massinha vem do displacement e de um leve brilho, não de subsurface). O estouro é um efeito curto e reaproveitável (mesma simulação para todo vídeo, só muda cor do fundo). Nota de viabilidade: 9/10.

**Riscos:** mascote fofo pode puxar o canal para público infantil (o que no YouTube mexe com "conteúdo para crianças" e reduz monetização). Antídoto: temas e humor de adolescente/adulto jovem (sono, celular, corpo humano, dinheiro, universo, situações de escola e trabalho), contraste "fofo com assunto pesado", nada de cantigas. Outro risco: cansar o "estouro" se ele vier sempre do mesmo jeito; variar a forma (estoura pequeno, estoura em câmera lenta, demora a estourar, estoura no lugar errado, NÃO estoura uma vez e isso vira o fato).

---

### Direção C: "Interrogação" (toon gráfico, sem mascote, objeto-símbolo)

**Ideia central:** visual de desenho animado gráfico em 3D (cel shading, cores chapadas, contorno preto), como uma história em quadrinhos que se mexe. Todo vídeo começa com um ponto de interrogação 3D grande caindo no quadro e termina com ele virando ponto de exclamação. O símbolo é o "mascote".

**Estilo visual 3D**
- Paleta: dois tons por vídeo sobre fundo chapado (uma cor por tema: azul elétrico #2D5BFF para ciência, laranja #FF7A00 para corpo humano, roxo #7B3FE4 para espaço, verde ácido #A6E22E para bichos, rosa #FF4FA0 para humor), sempre com preto puro para contorno e branco para luz. O grid do perfil vira um mosaico de cores sólidas, fácil de reconhecer.
- Materiais: toon de 2 ou 3 faixas de sombra, sem textura, com uma meia-tinta de pontinhos (retícula de gibi) nas sombras como detalhe assinatura.
- Iluminação: uma luz principal dura, sombras recortadas, sem luz ambiente realista.
- Câmera: enquadramentos de quadrinho (close extremo, plano holandês, contra-plongée), cortes secos e "smash zooms" de 3 quadros. Linhas de velocidade em 2D sobrepostas.

**Personagem:** nenhum fixo. Figuras humanas, se aparecerem, são bonecos de silhueta lisa (manequim sem rosto), o que evita qualquer "pessoa real".

**Roteiro assinatura:** "Pergunta + ? caindo (1 s)" > "Resposta curta que parece óbvia (5 s)" > "MAS... (corte seco, cor do fundo inverte)" > "explicação em 3 quadros numerados 1, 2, 3 na tela" > "? gira e vira ! no fato final" > "frase de loop". O "MAS" com inversão de cor é o momento marca.

**Bordões**
- Abertura: a pergunta, com o "?" caindo. Sem saudação.
- Virada: PT "Só que não." / EN "Except... no." (meme bem conhecido nos dois idiomas, curto).
- Fechamento: o "!" se fecha com um clique; sem frase fixa obrigatória.

**Assinatura sonora:** "whoosh + toc" do ? caindo; "vinil arranhando" curto (sintetizado) no "Só que não"; "clique metálico" no ! final. Trilha de batida eletrônica seca, lo-fi.

**Tipografia e legendas:** Bricolage Grotesque ExtraBold ou Archivo Black (OFL), caixa alta, preto em balão branco tipo gibi, palavra-chave na cor do tema. Números grandes 1, 2, 3 como elementos gráficos (servem aos dois idiomas).

**Easter egg:** uma pequena mosca desenhada em 2D que pousa em algum lugar da tela em todo vídeo, por meio segundo.

**PT e EN:** muito bom. Símbolos (? !), números e cores são universais. O "Só que não / Except no" depende de tradução boa, mas é curto.

**Viabilidade em CPU:** a melhor das três. Cel shading com cor chapada esconde ruído, então dá para usar pouquíssimas amostras; fundo é cor sólida; contorno sai do solidify invertido ou de linhas na composição. Nota de viabilidade: 10/10.

**Riscos:** é o visual mais "frio"; sem personagem, o apego é baixo e o canal pode virar só mais um de curiosidade. Cel shading em 3D também é mais comum em templates. Humor bobo funciona menos.

## 4. Comparativo rápido

| Critério | A: Ilha | B: Pipo | C: Interrogação |
|---|---|---|---|
| Reconhecível em 1 s no feed | Médio-alto | Alto | Médio |
| Apego/comunidade | Médio (lesma) | Alto (estouro, contador) | Baixo |
| Serve para humor de 30 s | Fraco | Forte | Médio |
| Serve para conhecimento de 60 a 90 s | Forte | Forte | Forte |
| PT/EN com o mesmo render | Ótimo | Ótimo | Ótimo |
| Parece "feito à mão", anti-IA | Médio | Alto | Médio |
| Render em CPU | 8/10 | 9/10 | 10/10 |
| Complexidade de automação | Alta (módulos de ilha) | Média (Pipo + cenários) | Baixa |
| Risco principal | Visual já visto | Ser lido como infantil | Ser genérico |

## 5. O nome "ShoShortz"

**Avaliação:**
- **Memorável:** médio. Tem ritmo (Sho-Shor), mas não remete a nada concreto (nem ao estilo, nem ao tema).
- **Pronúncia e escrita:** ruim para o brasileiro. Falado em voz alta, a pessoa não sabe se é "Show Shorts", "Xô Shorts" ou "Sho Shorts", e não sabe como escreve (sh? z no final? junto?). Nome que precisa ser soletrado perde a busca boca a boca.
- **Buscável:** ruim. "Shorts" é a palavra mais genérica possível na plataforma; ao digitar algo parecido, o YouTube completa para milhões de outros resultados. A busca encontrou nomes parecidos já existentes (variações como "ShortShortz" e muitos "Shorty"), o que aumenta a confusão.
- **Bilíngue:** razoável no EN (soa como "show shorts"), sem sentido no PT.
- **Amarra o canal ao formato:** "Shorts" é termo do YouTube. No Instagram (Reels) soa estranho, e se o canal crescer para vídeos longos, compilações ou outros produtos, o nome vira limitação.
- **O "z" no lugar do "s":** passa uma estética de internet de 2010, um pouco o "tiozão querendo pagar de jovem" que o contexto quer evitar.

**Veredito:** trocar agora, enquanto o canal ainda não tem público. Trocar depois de 50 mil inscritos é muito mais caro.

**Alternativas** (todas precisam de verificação manual antes: handle livre no YouTube e no Instagram, busca exata no YouTube e no Google, e busca simples no INPI para não esbarrar em marca registrada):

| Nome | Combina com | Prós | Contras |
|---|---|---|---|
| **Pipo** / handle @pipopop ou @opipo | Direção B | Curto, igual em PT e EN, é o nome do mascote (canal = personagem) | "Pipo" sozinho deve ter homônimos, por isso o handle composto |
| **PipoPop** | Direção B | Aliteração (lição dos personagens virais), onomatopeia do estouro, fácil de soletrar, provavelmente único | Pode soar infantil se o conteúdo também for |
| **Estourou** / EN "Popped" | Direção B | Bordão = nome | Dois nomes diferentes por idioma, ruim para marca única |
| **Ilhota** / "Tiny Isle" | Direção A | Descreve o visual | PT e EN diferentes; "ilhota" é palavra comum |
| **Mundinho** | Direção A | Simpático, brasileiro | Só PT, difícil para EN |
| **Interroga** | Direção C | Curto, legível em PT, EN entende por causa de "interrogate" | Frio, parece canal de notícia |
| **Kurioh** / **Quirk** | Qualquer | Curiosidade nos dois idiomas | "Quirk" é palavra comum (busca ruim); grafias inventadas trazem de volta o problema de soletrar |

Minha sugestão: **PipoPop** como nome do canal e @pipopop como handle (ou "Pipo" como nome de exibição e @pipopop como handle, se o handle estiver livre e o nome curto ficar melhor no perfil). Se o dono quiser manter ShoShortz por apego, o mínimo é tirar a ambiguidade (definir a pronúncia "Show Shorts" e usar isso no bordão) e aceitar que a busca pelo nome vai ser fraca.

## 6. Recomendação

**Recomendo a Direção B (Pipo), pegando duas coisas das outras:** a estrutura "pergunta + 3 degraus + virada" da C (com números 1, 2, 3 que servem aos dois idiomas) e o cuidado de não deixar texto dentro da cena, como na A.

Justificativa:
1. **É a única com personagem, e personagem é o que cria apego e volta.** A pesquisa mostrou que faceless com personagem consistente se mantém, enquanto narração genérica de IA está sendo rebaixada. Um canal 100% automatizado precisa de algo que pareça ter "alma" e ponto de vista: o Pipo é esse ponto de vista.
2. **O estouro resolve três problemas de uma vez:** dá um momento-recompensa fixo perto do fim (segura retenção), dá uma assinatura sonora sem palavras (igual em PT e EN) e dá algo para a comunidade comentar e contar.
3. **Serve aos dois tipos de vídeo** (humor de 30 s e conhecimento de 60 a 90 s), coisa que A e C fazem mal no humor.
4. **Passa longe da cara de IA:** feltro e massinha com imperfeição, animação em dois tipo stop motion, luz quente. É o oposto do slideshow genérico.
5. **Viável em CPU:** animar em 12 fps duplicados já corta o render pela metade, o personagem é feito de primitivas e o estouro é um efeito reaproveitável.
6. **Escala como marca:** mascote vira série, figurinha, avatar do perfil, produto no futuro. Uma ilha ou um "?" não viram isso.

Cuidados obrigatórios para a B dar certo:
- Marcar todo vídeo como "não é conteúdo para crianças" e escrever para 15 a 30 anos (temas de celular, sono, escola, trabalho, corpo, dinheiro, universo, situações absurdas do dia a dia). Fofo no visual, adulto no assunto.
- O Pipo nunca fala. Narrador fora de cena, masculino ou feminino conforme o tema, sem mudar o personagem.
- Variar o estouro (no mínimo 6 variações no banco de animações) e, de vez em quando, um vídeo em que ele NÃO estoura, para quebrar a expectativa.
- Testar a direção com 10 a 14 vídeos antes de travar: se o estouro não gerar comentário nem replay, considerar migrar para A ou C mantendo as marcas registradas abaixo.

## 7. Marcas registradas que devem existir em qualquer cenário

Valem para A, B ou C, e para qualquer nome escolhido:

1. **Abertura sem abertura.** O frame 1 já é o vídeo: a pergunta falada desde a primeira palavra e o objeto ou personagem principal já em cena. A "vinheta" é só um sting sonoro de até 0,4 s (3 notas) tocando por baixo da primeira palavra. Nunca logo, nunca saudação, nunca fade.
2. **Um momento de virada visual e sonoro idêntico em todo vídeo.** Estouro (B), recuo da ilha (A) ou ? virando ! (C). Mesmo som, mesma duração, sempre no último quarto do vídeo. É o que o público aprende a esperar e o que torna o canal reconhecível de olhos fechados.
3. **Paleta fixa e legenda própria.** No máximo 5 cores fixas e um fundo característico, mais um estilo de legenda único (fonte de licença livre que não seja Montserrat nem Bebas, palavra-chave sempre na mesma cor de destaque, 1 a 3 palavras por vez, a cerca de 60% da altura da tela). O grid do perfil tem que ser reconhecível de longe.
4. **Easter egg escondido em todo vídeo.** Um objeto pequeno e sempre o mesmo (pipoca estourada, lesma, mosca), em lugar diferente a cada vídeo, de preferência com um número de contagem. Gera comentário espontâneo sem pergunta-isca.
5. **Final em loop.** A última frase e o último quadro reconectam com o primeiro, para a pessoa assistir de novo sem perceber. Sem CTA longo de "segue aí".

## 8. Checklist técnico para os agentes de construção

- Um arquivo-base de personagem e cenário, versionado, de onde todo vídeo parte (consistência).
- Render único por vídeo; PT e EN só mudam faixa de áudio e camada de legenda na montagem (FFmpeg).
- Nada de texto em idioma dentro da cena 3D; só números e símbolos.
- Sons de marca (sting, estouro, passos) gerados uma vez por código, salvos como arquivos fixos e reaproveitados em todo vídeo, com o mesmo volume.
- Banco de animações reaproveitáveis: entrada do personagem, 6 reações, 6 variações do momento de virada.
- Animação em 12 fps duplicados para 24 (ou o equivalente), fundo simples, desfoque e efeitos na composição.
- Fontes: Baloo 2, Lilita One, Fredoka, Bricolage Grotesque, Archivo Black (todas de licença livre OFL, uso comercial permitido).
