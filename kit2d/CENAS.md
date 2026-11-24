# cenas.json: como escrever um vídeo 2D do PipoPop

Você escreve só este arquivo. O motor desenha tudo, amarra cada ação a uma palavra da narração e grava o som.

```
python3 kit/tts.py WORK                   # narração + WORK/timing.json (já pronto? pule)
python3 kit2d/render2d.py WORK --previa   # folha WORK/previa.jpg, 1 quadro a cada 1,5 s (2 s de espera). Itere aqui.
python3 kit2d/render2d.py WORK --quadros 1,90,300   # quadros soltos em WORK/prev/
python3 kit2d/render2d.py WORK            # todos os quadros + events.json + qa_scene.json (~35 s para 22 s de vídeo)
python3 kit/compose.py WORK               # legenda, som, -14 LUFS -> WORK/final_pt.mp4
python3 kit/qa_check.py WORK pt           # revisão; olhe WORK/qa_sheet_pt.jpg com os seus olhos
```

## 1. Regras de ouro
- A tela é 1080x1920. Posição `x`, `y` vai de 0 a 1 (0,5 = centro). É o CENTRO do elemento.
- A legenda fica entre `y` 0,60 e 0,72. Nada com texto ou rosto ali. Deixe o importante entre `y` 0,10 e 0,58.
- Margens: `x` entre 0,08 e 0,92 para textos. O render avisa (QA) se algo invadir a legenda ou sair da zona segura.
- Algo muda a cada 1,5 a 3 s. Quadro 1 já mostra o conflito, sem depender do som.
- Ordem dos elementos = ordem de desenho (o último fica na frente).

## 2. Tempo: `"em"` é uma palavra da narração
- `"em": "sessenta"`: no início da palavra (acentos e maiúsculas não importam).
- A busca começa no início da cena: a mesma palavra mais adiante é achada sozinha.
- `"sessenta#2"`: a 2ª vez que a palavra aparece no vídeo inteiro.
- `"linha3"`: início da linha 3 do roteiro (começa em 0).
- Número: segundos (`"em": 1.5`). `"depois": 0.2` atrasa a ação.
- Duração: `"dur": 0.5` (segundos) ou `"ate": "horas"` (até o FIM dessa palavra).
- Palavra que não existe na narração dá erro com a lista de palavras válidas.

## 3. Estrutura
```json
{
 "paleta": "tomate",
 "musica": "percussao",
 "cenas": [
  {"em": 0, "cenario": "chapado", "paleta": "uva", "padrao": "raios",
   "elementos": [ {"id": "cal", "tipo": "calendario", "x": 0.5, "y": 0.25, "acoes": [ ... ]} ],
   "acoes": [ {"em": "dias", "faz": "soco"} ]}
 ]
}
```
Topo: `paleta` (padrão), `musica` (apelido ou caminho em assets/musica), `musica_inicio` (s), `whoosh_nos_cortes` (true/false/apelido),
`volume_whoosh` (0,22), `silencios` ([[a, b]] em segundos: tira a música), `sfx` (extras: [["assets/sfx/...", t, volume]]), `cauda` (0,6 s).

Cena: `em` (corte; a 1ª é sempre 0), `cenario`, `paleta`, `padrao` (no chapado/celular), `zoom` (1,0), `deriva` (aproximação lenta automática, 0,025; 0 desliga),
`elementos`, `acoes` (de câmera). Cada cena nova começa do zero: elementos não passam de uma cena para outra.
Opcionais da cena: `transicao` (seção 4.2), `energia`/`calma` (fundos animados), `fundo_foto` (seção 4.3).

## 4. Cardápio
Paletas: tomate, mostarda, petroleo, uva, menta, cobalto, noite, rosa, laranja (troque a cada cena: dá ritmo).

Cenários simples: `chapado` (cor + padrão: raios, bolinhas, listras, chuva, nada) · `celular` (tela gigante; `hora`, `cor_tela`).

### Cenários em camadas (kit2d/cenarios2.py)
Fundo condizente com a história e com vida própria (algo sempre se mexe, sem roubar a cena). Três camadas: fundo, meio e FRENTE.
A frente (mesa, balcão, painel, encosto do banco, cerca...) é desenhada DEPOIS dos personagens: esconde as pernas de quem está atrás.
`pipo`, `humano` e `porta` ficam atrás da frente; textos, cartões, setas etc. ficam por cima dela. Mude com `"camada": "meio"` ou `"topo"`.

Opções da cena: `luz` (dia, tarde, noite: noite = abajur/lâmpadas com halo quente e janela escura com lua; tarde = laranja com raio de sol; os personagens pegam só um pouco da cor e não perdem contraste) ·
`ceu` (só o céu das janelas) · `vida`: false (congela as animações) · `chuva`: true (gotas escorrendo na janela; chuva na rua) · `frente`: false (sem camada da frente).

| cenário | o que tem (vida) | âncoras |
|---|---|---|
| sala | janela com cortina balançando, nuvens, pássaro, carrinho ao longe, ventilador de teto, relógio, porta, luminária; `cor_sofa` | sofa_assento, sofa_esq, sofa_dir, porta, janela, quadro, relogio, chao |
| escritorio | persiana, mural de post-its, monitor com texto rolando, café com vapor, luminária, relógio (mesa na frente) | cadeira, em_pe, mesa, monitor, janela, quadro, relogio |
| quarto | janela (noite por padrão), cama, criado-mudo com abajur, ventilador, pôster | cama, em_pe, janela, abajur, poster |
| cozinha | geladeira com ímãs, janela com cortininha, panela com vapor, utensílios balançando (balcão na frente) | balcao, geladeira, fogao, pia, janela, relogio |
| rua | prédios, loja com toldo, semáforo trocando (`sinal` fixa: verde, amarelo, vermelho), poste, carro passando na frente | calcada, calcada_esq, calcada_dir, loja, semaforo, poste, ceu |
| onibus | paisagem passando nas janelas, alças balançando, botão PARE (encosto da frente) | banco, banco_dir, em_pe, janela, pare |
| escola | lousa (`lousa`: "texto\nde giz"), relógio, carteiras (carteira na frente) | carteira, professor, lousa, relogio |
| carro | de frente para quem está dentro: rua passando no vidro de trás, cheirinho balançando, rádio, volante na frente do motorista. `vista`: "motorista" = rua vindo no para-brisa | motorista, carona, para_brisa, retrovisor, radio |
| casa_natal_fora | fachada à noite (padrão), pisca-pisca correndo, árvore acesa na janela, vizinho com MUITO mais luz, estrelas, cerca com luzinhas na frente | quintal, quintal_esq, quintal_dir, porta, janela, vizinho, ceu |
| sala_natal | árvore piscando, presentes, festão, ventilador de teto e de pé (calor), mesa da ceia com peru soltando vapor na frente | mesa, arvore, presentes, ceia, centro, janela |
| loja | vitrine com gente passando, araras, placas piscando (`placa` "-50%", `placa2` "PROMO"), balcão com caixa na frente | caixa, centro, vitrine, placa, placa2 |
| supermercado | corredor em perspectiva, placa de preço balançando (`preco`), alguém cruzando no fundo, carrinho na frente | carrinho, corredor, placa, fundo |
| praia | ondas, espuma indo e voltando, sol girando, barquinho, gaivota, guarda-sol; cadeira de praia na frente se alguém senta | areia, areia_dir, cadeira, guarda_sol, mar, ceu |
| festa | bandeirinhas, balões, globo e feixes de luz coloridos girando, velas, confete caindo na frente (noite por padrão) | centro, esq, bolo, globo |
| cidade_noite_alto | cidade vista do alto: janelas acendendo e apagando, faróis andando nas ruas | ceu, cidade, lua |
| espaco_terra | Terra à noite girando com luzes das cidades piscando, atmosfera, satélite passando | espaco, terra, satelite, flutuando |
| hospital | monitor cardíaco com traçado correndo e bipe, soro pingando, persiana, leito | leito, medico, monitor, janela |
| academia | espelho, halteres, esteira com a lona andando e km subindo, ventilador, cartaz (`cartaz`) | esteira, halteres, espelho, cartaz |
| restaurante | luminárias balançando, cardápio (`cardapio`), garçom passando ao fundo, pratos com vapor e toalha xadrez na frente | mesa, mesa_dir, garcom, cardapio |

Âncoras: em qualquer elemento, `"ancora": "sofa_assento"` no lugar de `x`, `y` (com `dx`, `dy` opcionais, em fração da tela).
Assento: o quadril do personagem vai no assento e a frente cobre as pernas. Chão: os pés no chão. As outras são pontos (o centro do elemento vai ali).
Personagem sem `escala` ganha a escala certa da âncora. `move` também aceita âncora: `{"faz": "move", "para": "porta"}`.
Âncora errada dá erro com a lista das âncoras do cenário.

Porta que abre: `{"id": "pt", "tipo": "porta", "ancora": "porta", "acoes": [{"em": "toc", "faz": "muda", "prop": "abre", "para": 1, "dur": 0.5, "som": "porta"}]}`
e, DEPOIS dela na lista, o humano com `"ancora": "porta"` e `{"faz": "entra", "jeito": "aparece"}`: ele aparece no vão e o batente fica na frente dele.
A porta também funciona no chapado (`largura`, `altura`, `cor`, `dentro` = cor da luz do outro lado).
Cenários: `chapado` (cor + padrão: os animados da seção 4.2 ou os antigos raios, bolinhas, listras, chuva, nada) · `sala` (sofá; `cor_sofa`) · `escritorio` · `quarto` · `celular` (tela gigante; `hora`, `cor_tela`).

Elementos (`tipo`) e as propriedades que aceitam (todas podem mudar com `muda`):
| tipo | para que | propriedades |
|---|---|---|
| pipo | a Pipo (espiga cansada, sobrancelha levantada) | `segura`: "celular"; `olhar`: camera, celular, esq, dir, cima, baixo; `sobrancelha` 0 a 1,2; `palpebra` (0,42 cansada; 0 aberta); `boca`: reta, o, sorriso, sorriso_torto, triste; `forma`: "pipoca" (já estourada) |
| humano | pessoa (cartoon editorial, kit2d/humano2.py; detalhes na seção 4.1) | `preset` (elenco fixo, seção 4.2), `idade`, `corpo`, `cabelo`, `cabelo_cor`, `barba`, `pele`, `roupa`, `calca`, `sapato`, `manga`, `expressao`, `olhar`, `pose`, `aponta_para`, `segura`: "celular", `assento`, traços (4.2) e acessórios `oculos`, `bone`, `mochila`, `avental`, `gravata`, `fone` |
| celular | celular na mão | `tela`: feed (rolando), boca (come coisas), texto; `linhas` (tela texto); `cor_tela`; `dedao`: true (polegar rolando) |
| calendario | folhinha do mês | `titulo`, `comidos` (quantos dias viraram buraco), `cor` |
| fluxo | folhinhas voando de A para B | `de`, `para`: id de elemento ou [x, y]; `ritmo` (por s), `vida` (s), `adianta` (s já em voo no 1º quadro), `cor` |
| relogio | despertador | `horas` (fatia colorida 0 a 12), `giro` (voltas/s dos ponteiros), `cor` |
| contador | número grande | `valor`, `prefixo`, `sufixo`, `casas`, `tam`, `cor`, `fundo` (true) |
| barra | barra que cresce para cima; `y` = BASE | `valor`, `max`, `altura` (px), `largura`, `pilha` [{valor, cor, rotulo}], `total` (texto no topo), `nome` (embaixo), `lado_rotulo` |
| texto | título com contorno | `texto` (aceita \n), `tam`, `cor`, `fundo` (#hex vira pílula) |
| comentario | card de comentário SEM curtidas | `nome`, `texto`, `cor_avatar`, `largura` |
| seta | seta desenhada | `vetor` [dx, dy] em px, `curva`, `progresso` 0 a 1, `cor` |
| carimbo | carimbo torto | `texto`, `cor`, `inclina`, `tam` |
| rachadura | tela trincada | `progresso` 0 a 1 |
| bloco | cartão/painel (split, antes e depois) | `largura`, `altura`, `cor`, `texto`, `tam` |
| foto | foto real CC0/domínio público numa polaroide (kit/imagens.py) | `arquivo` (caminho), `largura` (px), `altura`, `legenda`, `credito`, `zoom_lento` |
| meme | formato de meme redesenhado no nosso estilo (seção 4.1) | `formato`, `revela`, `largura`, `altura` (900), `pers`, `pers_a`/`pers_b`, textos do formato |

Todo elemento: `id`, `x`, `y`, `escala`, `rot` (graus), `alpha`, `espelha`, `pode_sobrepor` (true = não acusar texto sobreposto).

### 4.1 Memes (`"tipo": "meme"`, kit2d/memes.py)
Regra do canal: o meme é a ESTRUTURA redesenhada (painéis, rótulos, nossos personagens). Nunca a foto original de meme famoso, nunca pessoa real.
Use `x` 0,5 e `y` 0,335 com `escala` 1: a caixa (900 x 900) fica entre y 0,10 e 0,57, fora da legenda. Textos nunca ficam abaixo de 48 px (quebram linha).
- `revela`: quantos painéis/níveis já apareceram (padrão: todos). Comece em 1 e anime: `{"em": "palavra", "faz": "muda", "prop": "revela", "para": 2}`; cada painel entra com pop.
- `pers`: identidade do personagem (padrão Pipo; ex. `{"tipo": "humano", "cabelo": "coque", "pele": "escura"}`). O formato põe a expressão; `pers_a`/`pers_b` sobrepõem por painel.
- `tam` ajusta o texto principal; `cor_a`, `cor_b`, `cor_cena` trocam as cores dos painéis.

| formato | painéis | textos e opções |
|---|---|---|
| aprova_reprova | 2: recusa com a mão / aponta aprovando | `nao`, `sim` |
| expectativa_realidade | 2: EXPECTATIVA / REALIDADE | `foto_a`/`foto_b` (CC0 de kit/imagens.py, polaroide) ou `texto_a`/`texto_b`; sem nada: Pipo feliz / Pipo acabada com nuvem de chuva; `rotulo_a`/`rotulo_b` |
| ninguem_eu | 2: "Ninguém:" vazio / "Eu:" + cena | `texto` (o que vem depois de Eu:), `ninguem`, `eu` |
| pov | 2: faixa POV / cena | `texto`, `expr` (choque, feliz, acabado, maroto, nada, nervoso) |
| plot_twist | 2: cena / carimbo PLOT TWIST com estrelinhas (personagem leva susto) | `texto` (faixa em cima), `carimbo`, `cor_carimbo` |
| eu_explicando | 2: eu no quadro rabiscado / "eles:" com cara de nada | `texto` (vira "eu explicando X"), `eles`, `eles_pers` (lista de pessoas) |
| cerebro_niveis | 3 ou 4 níveis, cérebro cada vez mais brilhante | `niveis`: lista de textos |
| botoes_dificil | 2: dois botões vermelhos com dedo indeciso / personagem suando | `botao_a`, `botao_b` |
| grafico_mentiroso | 2: gráfico subindo / despenca e fura o chão (ou explode para fora) | `texto` (título), `direcao`: despenca ou explode, `valor` (ex. "-99%") |
| legenda_choque | 1 ou 2: texto gigante tremendo com linhas de impacto / personagem chocado (só com `pers`) | `texto` (vira maiúsculo), `cor_explosao` |

Formatos das trends de out/nov 2026 (pesquisa, fontes e um exemplo de cada em docs/pesquisa/2026-11-24_memes_em_alta.md):
| formato | trend | painéis / animação | textos e opções |
|---|---|---|---|
| carregando | Recharged / "carregando 1% a 100%" | 1; anime `nivel` (0 a 100) com `muda` + `dur`: a bateria enche e a Pipo levanta; no 100 vira pipoca | `texto` (faixa), `nivel`, `vira_pipoca` (false mantém espiga), `cor_cena` |
| estagios | "5 estágios de ser..." | 1 por estágio (3 a 6), a cara da Pipo piora a cada linha | `texto` (vira "N estágios de X") ou `titulo`, `estagios` (lista), `exprs` (lista) |
| retrospectiva | "sinto que não fiz nada esse ano" | 1 por mês (12), o último fica dourado | `texto` (faixa), `meses` (lista curta, 1 ou 2 palavras), `rotulos` (troca JAN..DEZ), `colunas`, `destaque` |
| carta_noel | "Querido Papai Noel, eu visto tamanho..." | 2: carta / resposta à mão circulada, Pipo espiando com lápis | `inicio`, `tamanho`, `cor_cena` |
| soft_launch | soft launch (My Moon My Man, sem o áudio) | 2: cortina com sombra e "?" / cortina sobe: coração com o "amor" + carimbo | `texto` (faixa), `amor`, `carimbo` (OFICIAL) |
| remoendo | "paid me no mind" (ler a mesma mensagem de novo e de novo) | 1 + leituras: balão da mensagem / 4 caras, cada uma com uma ênfase | `de`, `mensagem`, `leituras` (lista), `exprs`, `cor_avatar` |
| vai_vai_vai | "go go go" | 2; anime `revela` de 1 a 2 com `dur`: os VAI brotam um a um e a Pipo treme | `texto` (faixa), `progresso` (0,99), `rotulo` (texto do visor), `grito` (VAI) |
| nao_nao_sim | "não, não, não... SIM!" | 1 por item: carimbo NÃO + cara de recusa; o último é o SIM com festa | `itens` (lista, o último é o SIM), `nao`, `sim`, `cor_sim` |
| nao_julgamos | "a gente escuta e não julga" | 3: roda de conversa / balão da confissão / a plateia reage (um sorri, outro sua) | `titulo`, `confissao`, `reacao` (balãozinho opcional), `ouvintes` (lista de humanos), `reacoes` (expressões) |
| distraida | "getting robbed" (vidrada no celular) | 2; anime `revela` de 1 a 2 com `dur`: a mão entra, agarra o saco e arrasta | `texto` (faixa), `roubado` (etiqueta do saco), `hora` (relógio de parede), `cor_luva` |

```json
{"id": "m", "tipo": "meme", "formato": "aprova_reprova", "x": 0.5, "y": 0.335, "revela": 1,
 "nao": "estudar com antecedência", "sim": "estudar na noite da prova",
 "acoes": [{"em": "linha1", "faz": "entra", "jeito": "pop", "som": "pop"},
           {"em": "noite", "faz": "muda", "prop": "revela", "para": 2, "som": "pop2"}]}
```

### 4.2 Fundos animados e transições (kit2d/fundos.py)
Prefira estes aos antigos (cor chapada e listras). Valem no `chapado` e viram o papel de parede da tela no `celular`.
Todos usam as cores da paleta, se mexem sozinhos e baixam o contraste no centro (onde ficam Pipo e texto).
Na cena: `energia` 0 a 1 (padrão 0,6: velocidade e quantidade) e `calma` 0 a 1 (quanto o centro fica mais liso).

| padrao | o que é | quando usar | extras |
|---|---|---|---|
| gradiente_vivo | 3 cores da paleta girando e respirando, brilhos suaves | neutro, explicação | |
| bokeh | círculos desfocados subindo em 3 profundidades | clima, nostalgia, sonho | |
| formas | confete: triângulos, círculos, zigue-zague, estrelinhas caindo e girando | festa, lista, curiosidade | |
| espiral | espiral hipnótica girando | choque, virada, "o quê?" | `velocidade` (1) |
| halftone | retícula de HQ pulsando em onda | humor, quadrinho | |
| ondas | faixas onduladas com contorno (lava) | transição de assunto, calma | |
| raios_hq | speed lines de HQ pulsando, miolo limpo | impacto, revelação | |
| grade_retro | chão synthwave com grade andando, sol listrado, montanhas | anos 80, tecnologia, "antigamente" | |
| ceu | céu com sol/lua e nuvens em parallax | ao ar livre, tempo, clima | `ceu`: dia, tarde, noite (estrelas cintilando) |
| espaco | estrelas em parallax, nebulosa, planeta com anel, estrela cadente | ciência, "imagine", tamanho das coisas | |
| papel_rasgado | tiras de papel colorido rasgado deslizando | colagem, lista, antes e depois | |
| luzes | pisca-pisca em fios, piscando em sequência | Natal, Ano Novo, festa | |
| cidade | céu noturno + prédios com janelas acesas em parallax | cidade, noite, trabalho | |

`transicao` (na cena que ENTRA): o 1º quadro da cena nova se mistura com o último da anterior.
`wipe_diagonal` (faixa colorida varre na diagonal), `zoom_blur` (a cena velha explode em zoom), `papel` (a cena velha rasga ao meio),
`flash_cor` (flash na cor de destaque), `mergulho` e `emergir` (seção 4.3). `transicao_dur` em s (0,25; mergulho/emergir 0,5).
Use no máximo uma a cada 2 ou 3 cortes: o resto é corte seco (o whoosh já entra sozinho).
```json
{"em": "virou", "cenario": "chapado", "padrao": "espiral", "paleta": "cobalto", "energia": 0.9, "velocidade": 1.4, "transicao": "zoom_blur", "elementos": [...]}
```

### 4.3 Foto real em tela cheia e mergulho no desenho
`fundo_foto` na cena: foto CC0/domínio público (kit/imagens.py) cobrindo a tela, com Ken Burns e parallax de 2 camadas
(atrás desfocada e lenta; na frente nítida, maior, com máscara radial no foco). Vinheta e textura de papel por cima; elementos 2D por cima normalmente.
- `estilo`: real, duotone (2 cores da paleta: casa com o desenho), posterizada (poucas cores + contorno de tinta), pintada (suavizada, cor viva).
- `kb_de` / `kb_para`: [zoom, x, y], x e y = ponto da FOTO (0 a 1) que fica no centro; vai de um ao outro ao longo da cena (padrão [1, 0,5, 0,5] -> [1,18, 0,5, 0,45]).
- `parallax` (true), `vinheta` (0,45). Ponha `"deriva": 0` (o Ken Burns já move a câmera).
- `"transicao": "mergulho"` na cena 2D seguinte: a câmera mergulha num ponto da foto (`mergulho_em` [x, y] da TELA) e a cena nova nasce dali numa íris que abre, com flash.
  `"emergir"` é o inverso (a cena 2D fecha numa íris e a foto se afasta do ponto). Bom para abrir o vídeo: foto real -> mergulho -> nosso mundo.
```json
{"em": 0, "fundo_foto": "WORK/img/foto1.jpg", "estilo": "real", "kb_de": [1.0, 0.45, 0.5], "kb_para": [1.6, 0.47, 0.47], "deriva": 0, "elementos": [...]},
{"em": "cidade", "cenario": "chapado", "padrao": "cidade", "paleta": "noite", "transicao": "mergulho", "mergulho_em": [0.5, 0.45], "elementos": [...]}
```
Custo: os fundos animados somam ~10 a 30 ms por quadro (camadas suaves em 1/4 da resolução, sprites em cache); o render fica até ~1,2x o tempo dos fundos antigos.

Ações de elemento (`"faz"`), sempre com `em`; `som` e `volume` opcionais em qualquer uma:
- `entra` (`jeito`: pop, carimba, desliza_esq, desliza_dir, sobe, desce, cai, aparece). Se o elemento tem `entra`, ele fica invisível antes.
- `sai` (pop, desliza_esq, desliza_dir, some)
- `move` (`para` [x, y]) · `escala` (`para`) · `gira` (`para` graus) · `curva`: suave, rapido, elastico, linear
- `muda` (`prop`, `para`): qualquer propriedade; número anima, texto troca na hora
- `conta` / `cresce` (`para`): anima `valor` (contador, barra)
- `squash` (`forca` 0,2) · `soco` (zoom punch no elemento) · `pula` (`altura`) · `treme` (`dur`, `forca`) · `pisca` (`ritmo`, `dur`) · `mastiga` (celular com tela boca)
- `olha`, `sobrancelha`, `boca`, `palpebra`, `expressao`, `pose` (`para`) · `estoura` (Pipo vira pipoca com partículas)

Ações de câmera (em `acoes` da cena): `soco` (zoom punch, `forca` 0,12) · `treme` · `zoom` (`para`) · `pan` (`para` [x, y] do centro) · `inclina` (graus) · `flash` · `congela` (`dur`: freeze; use no fim).
Cuidado: zoom e pan empurram o que está embaixo para a faixa da legenda. Prefira `soco` no elemento.

Sons (`som`): pop, pop2, pop3, pops, estouro, whoosh, slide, impacto, impacto2, vidro, queda, metal, madeira, carimbo, tique, porta, passos, mastiga, mastiga2, arroto, ooh, fofo, coracao.
Sons de meme (assets/sfx/memes/, mesmo volume entre si): boom ("vine boom"), disco (arranhão de disco), violino_triste, badumtss, palhaco (buzina),
riser (suspense 1,6 s), dundun ("dun dun dunnn"), ohh (plateia), risada (plateia), grilo, certo (ding), errado (buzzer), dinheiro (ching),
glitch, gongo, apito_sobe, apito_desce, boing, fa e fa2 (o "FAAH" com eco, nosso; fa = voz grave, fa2 = voz aguda). Use `volume` 0,6 a 0,9.
Músicas: percussao, misterio, viagem, aventura. Tudo CC0 (assets/LICENCAS.md). Não use arquivo de fora de assets/.

### 4.1 Humano em detalhe
- `idade`: adulto (padrão), crianca (cabeça bem maior, corpo curto), idoso (leve corcunda, rugas, cabelo grisalho e óculos por padrão; `"oculos": false` tira).
- `corpo`: magro, medio (padrão), forte.
- `cabelo`: curto, longo (franja e mechas com pontas), coque, cacheado, black_power, careca, rabo_de_cavalo, trancas. `barba`: true (cheia), "bigode", "cavanhaque".
- `cabelo_cor`: preto, castanho, loiro, ruivo, grisalho, branco, azul, rosa ou "#hex". `pele`: clara, media, morena, escura. `roupa`, `calca`, `sapato`: "#hex". `manga`: curta (padrão) ou longa.
- `expressao`: neutro, feliz, gargalhada, bravo, surpreso, triste, chorando (lágrimas), nervoso (gota de suor), envergonhado (bochecha corada), apaixonado (olhos de coração), cansado. Pisca sozinho. As sobrancelhas mudam suave na troca.
- `pose`: em_pe (padrão), sentado (com banquinho; `"assento": false` para sentar no sofá do cenário), bracos_cruzados, maos_na_cabeca, acenando, apontando (`aponta_para`: [dx, dy], direção na tela), comemorando.
  Troque com `{"em": "palavra", "faz": "pose", "para": "comemorando"}` (ou `muda` com `prop` "pose"): os braços e as pernas giram até a pose nova em 0,38 s.
- `segura`: "celular" (com pose em_pe ou sentado) põe as duas mãos no celular; `"olhar": "celular"` acende a tela no rosto.
- Acessórios: `oculos`, `bone`, `mochila`, `avental`, `gravata`, `fone`. Use true ou uma cor ("#hex").
- Medidas (escala 1): pés em y +338 px do centro para todas as idades; rosto do adulto entre -334 e -138; criança e idoso têm o rosto mais baixo; sentado desce o corpo 66 px.
  Com `escala` 0,8 e `y` 0,36 o rosto do adulto fica entre 0,22 e 0,30. Rosto nunca entre `y` 0,60 e 0,72: o QA acusa `rosto_na_faixa_legenda`.
- Exemplo: `{"id": "vo", "tipo": "humano", "x": 0.7, "y": 0.36, "escala": 0.85, "idade": "idoso", "cabelo": "coque", "expressao": "feliz", "pose": "acenando", "avental": true}`


### 4.2 Humano: assinatura, traços peculiares e elenco fixo
Assinatura do canal (todo humano tem, não precisa pedir):
- Bochecha-grão: em cada bochecha, um grãozinho de milho rosado com brilho branco (o mesmo grão do corpo da Pipo).
- Olho com a pálpebra da Pipo: olhos grandes, meio cobertos por uma pálpebra da cor da pele.
- Cabeça de borracha: quando a `expressao` troca, a cabeça estica (surpreso, bravo, nervoso, apaixonado) ou amassa (as outras) e balança por 0,5 s.

Traços (combine à vontade; a piada é o traço, nunca o grupo: nada de raça, etnia, religião, deficiência ou corpo como humilhação):
- `cabeca`: oval (padrão), feijao, pera, quadrada, lua (cara de lua cheia). `queixo`: normal, quadrado, furinho. `pescoco`: curto, normal, longo ou px.
- `nariz`: normal, bolinha, batata, pontudo, adunco, arrebitado. `orelhas`: normal, abano.
- `dentes`: normal, separados, dentuco (aparece até de boca fechada), aparelho, banguela (os outros aparecem com a boca aberta: feliz, gargalhada, bravo).
- `sobrancelha`: "fina", "grossa", "monocelha". `cilios`: true. `sardas`, `olheiras`: true. `pinta`: true, "esq" ou "dir".
- `cabelo` extras: topete, moicano, calvicie (coroa careca com a "ponte" de fios), franja_reta, arrepiado. `barba`: também "bigodao".
- `brilho`: true (aura de galã: estrelinhas e dente que brilha) ou "sutil".
- Roupa: `estampa` (natal, havaiana, listras, xadrez), `manga` "regata", `pochete`, `faixa` (testeira). `oculos_tipo`: redondo, ponta, fundo_de_garrafa (aumenta os olhos), escuro; `oculos_cor`.

Elenco fixo (`"preset": "nome"`; qualquer propriedade no elemento vale por cima; lista em kit2d/elenco.py):
vizinho_exagerado, tia_do_zap, gala, crush, chefe, estagiario, vovo_turbo, crianca_terrivel, tiozao_do_churrasco, nerd, esportista, influencer, seu_ze_da_banca.
Ex.: `{"id": "chefe", "tipo": "humano", "preset": "chefe", "x": 0.7, "y": 0.36, "escala": 0.85, "acoes": [{"em": "prazo", "faz": "expressao", "para": "surpreso"}]}`
Use os mesmos nomes de preset nos vídeos para virarem personagens recorrentes.
### 4.2 Reações de meme (ação de câmera `"faz": "reacao"`)
O efeito cômico dos memes virais (o "aughhh", o vine boom, o arranhão de disco) refeito com som livre e a nossa câmera. Nunca áudio ou vídeo original de desenho, filme ou streamer.
```json
"acoes": [{"em": "prova", "faz": "reacao", "estilo": "boom", "alvo": "pipo"}]
```
- `estilo` (abaixo), `alvo` (id de elemento ou [x, y]; padrão: o 1º personagem da cena; em personagem a câmera mira o rosto), `dur` (0,4 a 1,2 s),
  `forca` (1,0; multiplica o zoom/tremor), `som` (troca o som; `false` = mudo), `som_dur` (corta o som em N s), `volume` (0,8).
- Cada reação traz o seu som (já cortado para não atropelar a narração). Não ponha `som` de novo na mesma ação.
- Durante a reação a câmera fica presa dentro do cenário, e o QA não acusa legenda/zona segura (o zoom passa por cima de propósito).

| estilo | o que acontece | som | quando usar |
|---|---|---|---|
| boom | zoom rápido no alvo, tremor leve, vermelho e contraste, vinheta, congela 0,4 s (0,9 s) | boom | revelação, fala absurda, "olha isso" |
| disco | congela o quadro, tira a cor, tarja "*para tudo*" no topo (`texto`, `texto_y` 0,1; `"texto": ""` tira) (1,0 s) | disco | virada: "e aí deu tudo errado", interromper a história |
| triste | tira a cor + azul, vinheta, zoom lento (1,2 s) | violino_triste (2,6 s) | derrota, fracasso fofo, "e o salário acabou" |
| dramatico | 3 cortes secos de zoom no rosto, no tempo do dun dun dunnn (1,2 s) | dundun (2,2 s) | suspense falso, revelação exagerada |
| ohh | linhas de impacto brancas de mangá + soco leve (0,9 s) | ohh (2,0 s) | indireta, "ele não sabia...", golpe baixo |
| grilo | tudo congela, o alvo pisca duas vezes, cor some um pouco (1,2 s) | grilo | piada sem graça, silêncio constrangedor |
| fa | zoom seco + tremor forte + flash branco (0,7 s) | fa | grito de susto/indignação, "FAAH" |

Regra de dose: no máximo 2 reações por vídeo, nunca duas seguidas da mesma; pausa na narração ajuda (a reação dura até 1,2 s e o som passa disso).

## 5. Exemplos
### A) Celular comendo o calendário (quadro 1 com conflito)
```json
{"musica": "percussao", "cenas": [
 {"em": 0, "cenario": "chapado", "paleta": "uva", "padrao": "raios", "elementos": [
   {"id": "cal", "tipo": "calendario", "x": 0.5, "y": 0.25, "comidos": 9,
    "acoes": [{"em": "sessenta", "faz": "muda", "prop": "comidos", "para": 24, "ate": "ano"}]},
   {"id": "voo", "tipo": "fluxo", "de": "cal", "para": "cel", "adianta": 0.8},
   {"id": "cel", "tipo": "celular", "x": 0.52, "y": 0.48, "escala": 0.9, "rot": 9, "tela": "boca", "dedao": true,
    "acoes": [{"em": 0, "faz": "mastiga", "dur": 3}, {"em": "dias", "faz": "soco", "som": "mastiga"}]}]}]}
```
### B) Número que explode (contador + relógio que esmaga a tela)
```json
{"em": "mas", "cenario": "chapado", "paleta": "tomate", "elementos": [
  {"id": "rel", "tipo": "relogio", "x": 0.5, "y": 0.47, "escala": 0.28, "horas": 4,
   "acoes": [{"em": "vira", "faz": "muda", "prop": "giro", "para": 5},
             {"em": "vira", "faz": "escala", "para": 1.35, "ate": "sessenta"},
             {"em": "horas#2", "faz": "escala", "para": 2.6, "dur": 0.18, "curva": "rapido"}]},
  {"id": "rach", "tipo": "rachadura", "x": 0.55, "y": 0.43, "acoes": [{"em": "horas#2", "faz": "entra", "jeito": "aparece", "som": "vidro"}]},
  {"id": "n", "tipo": "contador", "x": 0.5, "y": 0.17, "valor": 4, "sufixo": " h",
   "acoes": [{"em": "vira", "faz": "conta", "para": 1460, "ate": "sessenta", "som": "tique"}]}],
 "acoes": [{"em": "horas#2", "faz": "treme", "forca": 26}, {"em": "horas#2", "faz": "soco", "som": "impacto"}]}
```
### C) Pessoa + comentário + carimbo + estouro da Pipo
```json
{"em": "linha2", "cenario": "escritorio", "paleta": "menta", "elementos": [
  {"id": "ana", "tipo": "humano", "x": 0.68, "y": 0.42, "escala": 0.8, "cabelo": "coque", "cabelo_cor": "ruivo", "roupa": "#E8452C",
   "acoes": [{"em": "audio", "faz": "expressao", "para": "bravo"}]},
  {"id": "c1", "tipo": "comentario", "x": 0.5, "y": 0.12, "nome": "@grupo_da_firma", "texto": "áudio de 4 minutos",
   "acoes": [{"em": "audio", "faz": "entra", "jeito": "desliza_dir", "som": "slide"}]},
  {"id": "pipo", "tipo": "pipo", "x": 0.25, "y": 0.40, "escala": 0.8,
   "acoes": [{"em": "minutos", "faz": "estoura", "som": "estouro"}]},
  {"id": "st", "tipo": "carimbo", "x": 0.3, "y": 0.52, "texto": "VISTO", "cor": "#2A3FD1", "acoes": [{"em": "ok", "faz": "entra", "jeito": "carimba", "som": "carimbo"}]}]}
```

## 6. Antes de entregar
1. `--previa` e olhe: algo parado mais de 3 s? texto pequeno? personagem pequeno demais (Pipo: `escala` 0,75 a 1)?
2. Render completo: as linhas `QA:` no fim apontam texto na legenda ou fora da zona segura. Corrija posição, não ignore.
3. compose + qa_check e olhe a qa_sheet com os seus olhos.
