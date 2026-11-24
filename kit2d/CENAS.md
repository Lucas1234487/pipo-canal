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

## 4. Cardápio
Paletas: tomate, mostarda, petroleo, uva, menta, cobalto, noite, rosa, laranja (troque a cada cena: dá ritmo).

Cenários: `chapado` (cor + padrão: raios, bolinhas, listras, chuva, nada) · `sala` (sofá; `cor_sofa`) · `escritorio` · `quarto` · `celular` (tela gigante; `hora`, `cor_tela`).

Elementos (`tipo`) e as propriedades que aceitam (todas podem mudar com `muda`):
| tipo | para que | propriedades |
|---|---|---|
| pipo | a Pipo (espiga cansada, sobrancelha levantada) | `segura`: "celular"; `olhar`: camera, celular, esq, dir, cima, baixo; `sobrancelha` 0 a 1,2; `palpebra` (0,42 cansada; 0 aberta); `boca`: reta, o, sorriso, sorriso_torto, triste; `forma`: "pipoca" (já estourada) |
| humano | pessoa genérica | `cabelo`: curto, longo, coque, cacheado, careca; `cabelo_cor`: preto, castanho, loiro, ruivo, grisalho, azul ou "#hex"; `pele`: clara, media, morena, escura; `roupa`, `calca` (#hex); `expressao`: neutro, feliz, bravo, surpreso, triste; `olhar`; `segura`: "celular" |
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

Ações de elemento (`"faz"`), sempre com `em`; `som` e `volume` opcionais em qualquer uma:
- `entra` (`jeito`: pop, carimba, desliza_esq, desliza_dir, sobe, desce, cai, aparece). Se o elemento tem `entra`, ele fica invisível antes.
- `sai` (pop, desliza_esq, desliza_dir, some)
- `move` (`para` [x, y]) · `escala` (`para`) · `gira` (`para` graus) · `curva`: suave, rapido, elastico, linear
- `muda` (`prop`, `para`): qualquer propriedade; número anima, texto troca na hora
- `conta` / `cresce` (`para`): anima `valor` (contador, barra)
- `squash` (`forca` 0,2) · `soco` (zoom punch no elemento) · `pula` (`altura`) · `treme` (`dur`, `forca`) · `pisca` (`ritmo`, `dur`) · `mastiga` (celular com tela boca)
- `olha`, `sobrancelha`, `boca`, `palpebra`, `expressao` (`para`) · `estoura` (Pipo vira pipoca com partículas)

Ações de câmera (em `acoes` da cena): `soco` (zoom punch, `forca` 0,12) · `treme` · `zoom` (`para`) · `pan` (`para` [x, y] do centro) · `inclina` (graus) · `flash` · `congela` (`dur`: freeze; use no fim).
Cuidado: zoom e pan empurram o que está embaixo para a faixa da legenda. Prefira `soco` no elemento.

Sons (`som`): pop, pop2, pop3, pops, estouro, whoosh, slide, impacto, impacto2, vidro, queda, metal, madeira, carimbo, tique, porta, passos, mastiga, mastiga2, arroto, ooh, fofo, coracao.
Músicas: percussao, misterio, viagem, aventura. Tudo CC0 (assets/LICENCAS.md). Não use arquivo de fora de assets/.

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
