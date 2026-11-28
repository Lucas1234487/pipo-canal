# Brief do PRODUTOR — ep015 (H, série "olhos pra frente" PARTE 2: dinossauros) — vai ao ar SÁB 28/11/2026 19h06

Você é o produtor único deste vídeo (faz O2 cenário + O3 som + O4 montagem). Trabalhe sozinho, sem subagentes. Rode tudo de /home/claude/pipo-canal.
WORK = /home/claude/2026-11-28_H (já tem roteiro.json APROVADO pelo Diretor e fatos.md; não mude o texto das falas).
PRAZO DURO: upload.mp4 + meta.json + qa_check APROVADO até 18h15 (hora de Brasília; confira com `TZ=America/Sao_Paulo date`). Se às 17h45 o motor de dinossauro não estiver pronto, simplifique o desenho (constância > perfeição) mas entregue.

## Leia (só isto)
docs/sistema/specs/O2_cenario.md, O3_sonoplastia.md, O4_montagem.md; docs/diretor/cadernos/O2.md, O3.md, O4.md (lições); kit2d/CENAS.md; kit2d/bicho.py (topo). Referência de série: episodios/ep013/cenas.json (parte 1: pombo, gato, regra dos olhos) — reaproveite o pombo e o gato do bicho.py.

## Passos
1. `python3 kit/tts.py WORK` (voz Antonio, já no roteiro) -> timing.json. Duração esperada ~60-65 s; se passar de 66 s, avise no retorno (não corte fala).
2. MOTOR (novo recurso, exigido pelo canal): acrescente ao kit2d/bicho.py duas espécies no traço da casa, com o mesmo esquema `olhos: "lado" | "frente"`:
   - "tiranossauro": bípede, cabeção, bracinhos curtos, cauda; olhos SEMPRE "frente" (como o gato). Ação de dar de ombros (bracinhos) se couber; boca abrindo no rugido.
   - "bicodepato" (hadrossauro): quadrúpede/semi, bico largo de pato, crista opcional; aceita "lado" (real) e "frente" (regra).
   Sem copiar dinossauro de filme/desenho famoso (nada de Jurassic, Rex de Toy Story, Littlefoot): design nosso, fofo-assustador. Rode os testes existentes em kit2d/testes se houver.
3. cenas.json seguindo as "shot" de cada linha do roteiro.json. Pontos obrigatórios:
   - QUADRO 1 legível sem som: bico-de-pato com os 2 olhos na frente comendo samambaia, sombra/silhueta do tiranossauro atrás, texto no topo (y >= 0,145): "OLHO NA FRENTE = ALMOÇO" e selo pequeno "PARTE 2".
   - Linha2: pombo da parte 1 -> sombra vira dinossauro -> `transicao: "mergulho"` para floresta do Cretáceo (samambaias, vulcão fumegando ao fundo, folhas mexendo). Fundo com vida em toda cena.
   - Cones de visão (como o ep013): T. rex com 2 cones cruzando num alvo; bico-de-pato real com leque largo; bico-de-pato da regra com cone estreito e costas escuras.
   - "picanha" (linha10): corte rápido para humano (elenco: tio) na churrasqueira vidrado no espeto; sem marca.
   - Tensão (linhas 11-13): paleta noite/petroleo, pegadas/chão tremendo.
   - ESTOURO DA PIPO em "Rugido" (de espiga vira pipoca com o susto, flash, tremor); depois "forma": "pipoca". A Pipo aparece antes (espiga pequena, nunca parada enquanto a voz fala).
   - Linha15: bico-de-pato vira devagar, cara a cara com o T. rex, sorriso amarelo; reação de meme "grilo" e corte seco. SEM violência/mordida/sangue.
   - Linha16: contador "DIAS SEM VER O PERIGO" (número tem que bater com o que a cena mostra).
   - Linha17: SPLIT CAÇADOR x PRESA em paleta quente, música vira aventura.
   - Fim (linha22): texto "CAÇADOR ou PRESA?" + Pipo pipoca apontando; acaba logo depois da fala.
   - VARIEDADE vs ep013: não abra com foto real (o ep013 abriu); paleta de abertura diferente da do ep013; música de abertura diferente da do ep013 (ele usou percussao -> misterio -> percussao: aqui use outra faixa na abertura, mistério só na tensão, aventura na virada).
   - Corte a cada 2-3 s, troca de paleta, nada parado > 3 s, nada na faixa da legenda (y 0,60-0,72). Textos na tela curtos e em PT, sem palavra estrangeira.
4. Som (O3): música por clima com `silencios` + `sfx`; som em toda entrada; rugido audível no celular (`python3 kit/checa_sons.py` em som novo); silêncio 0,3-0,5 s antes do rugido; estouro da Pipo sempre audível. Só CC0 de assets/ (registre proveniência se baixar som novo).
5. `python3 kit2d/render2d.py WORK` -> `python3 kit/compose.py WORK` -> `python3 kit/qa_check.py WORK pt` até APROVADO. Olhe a qa_sheet com os seus olhos (texto cortado, sobreposição, bicho fora de quadro).
6. WORK/upload.mp4 (720p, até 3,8 MB) e WORK/meta.json completo (copie o formato de fila/2026-11-26_H/meta.json). Valores:
   - titulo (<= 50 caracteres): "E se o dinossauro tivesse olho na frente? 🦖 Parte 2"  (se passar de 50, encurte: "Dinossauro com olho na frente? 🦖 Parte 2")
   - descricao: 2-4 frases: ficção declarada + fatos reais com as fontes (Stevens/Univ. de Oregon 2006 sobre a visão do tiranossauro; Museu Hooper sobre o olho lateral do bico-de-pato; Museu de História Natural de Londres: aves são dinossauros) + "Parte 2 de 3 da série Olhos pra frente." + hashtags.
   - hashtags: do roteiro.json. comentario_fixado: do roteiro.json. horario_sugerido: "2026-11-28 19:06".
   - interacao, humor ("referencia"), aposta "evolucao", serie "olhos_pra_frente", parte 2, tema "olhos pra frente parte 2: dinossauros", emocao "susto e riso -> tensão -> 'faz sentido'", reconhecivel "dinossauro, tio da picanha no churrasco, pombo da praça", estilo_animacao, versao_pipo, musica, meme, erro_proposital ("nenhum"), foto_real, voz, duracao, titulo_en, descricao_en, relacionado: "ep013 (parte 1)".
7. Apague WORK/frames depois do upload.mp4 pronto. Bilhete curto em WORK/bilhetes/produtor.md (o que fez, o que faltou no motor, 1 lição) e 1 lição datada (até 3 linhas) no fim de docs/diretor/cadernos/O2.md e O4.md. NÃO faça commit nem push (o Diretor faz).

## Retorno ao Diretor (até 10 linhas)
Caminho do upload.mp4, duração, tamanho, resultado do qa_check, segundo do estouro, o que ficou simplificado, e qualquer risco.
