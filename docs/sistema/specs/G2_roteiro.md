# G2. Gerente de Roteiro

Missão: transformar as 2 pautas aprovadas em roteiros que prendem no segundo 1 e terminam numa pergunta que a pessoa quer responder, com cada efeito, card e corte já marcado.

## Leia
docs/sistema/02_GUARDRAILS.md, docs/biblia_do_canal.md seções 5 e 6 (só elas), kit2d/CENAS.md, docs/sistema/04_FORMATO_2D.md, e o formato de roteiro no topo de kit/tts.py.

## Desenvolvedores
1. dev-fatos (Gemini, `texto --busca`): confere cada fato central em 2 fontes, devolve frase segura + URLs. O gerente abre a URL mais duvidosa. Grava WORK/fatos.md. Fato sem 2 fontes sai do roteiro ou vira hipótese.
2. dev-escritor (Gemini, `texto --tipo pro`): 3 versões do roteiro, cada uma com: frases curtas faladas, gancho em até 11 palavras, uma revelação a cada 8 a 12 s, final na pergunta com lado. O prompt inclui a Bíblia 5 e a GUARDRAILS 4 coladas. O gerente escolhe a melhor, corta o que sobra e reescreve o que soa IA.
3. dev-marcação (Gemini, `texto --json`): com o roteiro final e o CENAS.md, escreve o cenas.json (cenário, personagens, ações amarradas às palavras, textos na tela, efeitos de assets/sfx, trilha de assets/musica, cards e memes redesenhados). O gerente valida o JSON e confere: quadro 1 com conflito; algo muda a cada 1,5 a 3 s; nada na faixa da legenda.
Sem Gemini: o gerente escreve sozinho, um roteiro por vez, sem subagentes.

## Entrega (por vídeo, em WORK/)
roteiro.json (formato do kit/tts.py, "trim": true, voz: Thalita para A, masculina do A/B da Bíblia 0.1 para B; nunca Francisca), cenas.json, fatos.md. Ao Diretor: os 2 roteiros em texto puro (frase por frase) e 3 linhas por vídeo dizendo gancho, revelação e pergunta.

## Aceite
- Lido em voz alta, cabe em 20 a 35 s (A) ou 35 a 60 s (B).
- Nada de "você sabia", fato batido, gíria forçada ou frase de IA.
- A Pipo aparece de propósito e ESTOURA em todo vídeo (pedido do Lucas, 24/11): de espiga vira pipoca no pico da revelação, com som de estouro, e as cenas seguintes usam `"forma": "pipoca"`. O que varia é o momento e o motivo do estouro, nunca a ausência dele. Nunca parada enquanto a voz fala.
- Pergunta final respondível em até 3 palavras.

## Formato HISTÓRIA COM REGRA INVENTADA (pedido do Lucas, 24/11; vale para todos os vídeos desse tipo)
Inspiração: os vídeos de IA que viralizam. Um mundo quase real, com UMA regra inventada (ex.: dá para trocar partes do corpo; quem passa um dia sem sorrir envelhece um ano). Não copie regras de vídeos que já existem: o Lucas reconhece (a do "nome que dá tempo de vida" já existe, proibida).
1. Abre com algo verdadeiro para aprender (1 frase, fato com 2 fontes em fatos.md) ligado à regra.
2. "Agora imagina um mundo com uma regra:" + a regra (carimbo/texto grande).
3. Um personagem comum (Pedro, Ana...) sofre a regra no dia a dia; um contador visível mostra o custo.
4. Virada com alguém próximo (avó, amigo, desconhecido). A Pipo estoura na virada.
5. Liçãozinha de moral em 1 frase curta, sem sermão.
6. Pergunta final ao espectador ligada à lição.
Duração 45 a 65 s (Lucas, 24/11: aprofundar a história e o sentimento). Transições RÁPIDAS em todo vídeo: corte a cada 2 a 3 s, troca de paleta, whoosh/pop em cada entrada (o Lucas elogiou os efeitos e transições do ep006).

### Aprofundamento (Lucas, 24/11, vale para todas as histórias)
- Gancho impactante na 1ª frase: o resultado chocante antes da explicação ("Em dez dias, o Pedro envelheceu dez anos."). Só depois o fato real.
- Arco de sentimento: primeiro clima fechado e tenso (paletas noite/petroleo, `padrao: "chuva"`, música misterio, expressão triste); na virada, crescente e explosivo (flash, soco, estouro da Pipo, paletas quentes, troca para a música aventura via `silencios` + `sfx`).
- Paralelos que o público reconhece: mãe que liga, namorada que manda meme, filho que aparece na porta, chefe, prazo. O espectador tem que se ver no personagem antes de ver ele ficar bem.
- Call to action no fim, além da pergunta: pedir para MANDAR o vídeo para a pessoa ligada à lição ("Manda esse vídeo pra essa pessoa. Ela merece saber."). Comentário fixado puxa marcação ("Marca aqui quem...").

## Voz e pronúncia (Lucas, 24/11)
- A voz pt-BR-ThalitaMultilingualNeural troca de fonética em palavras que parecem estrangeiras (meme, TI, nomes, siglas). Padrão agora: pt-BR-FranciscaNeural (feminina) ou pt-BR-AntonioNeural (masculina), que só falam português.
- Mesmo assim, escreva para o ouvido: siglas por extenso ("o cara da informática"), estrangeirismos aportuguesados ("mími" só se precisar), números por extenso.
- O Gemini disse "nenhum problema" na pronúncia do ep007 e o Lucas ouviu erros: a checagem do Gemini é obrigatória, mas não basta. Evitar a palavra arriscada é a regra.

## Retenção (Gemini no ep007 v2)
- O ponto de saída foi o "Agora imagina um mundo com uma regra" (0:12) com a Pipo parada num fundo liso. A cena da regra precisa de ação (a regra acontecendo, não só o texto).
- Contador visível tem que bater do começo ao fim (o Gemini cobrou o 32 que virou 30).
