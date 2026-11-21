# 15. Viabilidade técnica 3D em CPU e pipeline

Agente 15, ShoShortz, 21/11/2026.

Tudo o que está aqui foi medido nesta máquina (2 núcleos, 7 GB de RAM, sem GPU, Blender 5.3 via bpy, FFmpeg). A cena de teste tem um personagem feito por skin modifier (corpo, braços, pés, olhos, boca), chão, 6 árvores, 3 caixas com bevel, texto 3D e câmera em movimento. É mais leve que as cenas do vídeo dos dinossauros (que tinham Terra com textura, bloom no compositor e muito mais objetos), então nas cenas reais conte com algo entre 1,5x e 2x os tempos abaixo.

Arquivos gerados:
- /home/claude/canal/pesquisa/render_tests/comparativo.png e comparativo2.png: o mesmo quadro em cada configuração, lado a lado.
- /home/claude/canal/pesquisa/render_tests/<config>/: quadros de exemplo de cada teste.
- /home/claude/canal/pesquisa/render_tests/teste_lipsync_PT.mp4 e teste_lipsync_EN.mp4: personagem falando com boca pela amplitude do áudio, legenda palavra por palavra, versão EN feita só re-renderizando a região da boca.
- /home/claude/canal/pesquisa/render_tests/lipsync_pt_en.png: quadro das duas versões lado a lado.
- /home/claude/canal/pesquisa/render_tests/interp_15para30_exemplo.png: artefato de interpolação de quadros.
- /home/claude/canal/pesquisa/render_tests/scripts/: scene.py (cena + todas as configs), lip.py (TTS + curva da boca + tempos das palavras), subs.py (legenda ASS estilo karaokê), run.sh.

Observação importante sobre a máquina: a mesma configuração rodou 2x mais lenta na primeira bateria (ex.: Cycles 4 amostras 540x960 deu 2,1 s/quadro e depois 1,0 s/quadro em três repetições estáveis). É VM compartilhada, então o planejamento diário precisa de folga de 2x.

## 1. Tabela custo x qualidade (medida)

Tempo por quadro em segundos, média dos quadros 2 a 4 (o primeiro quadro inclui carregar cena e BVH e é sempre mais lento). Resolução nativa do render; o upscale para 1080x1920 é feito no FFmpeg.

| Config | Motor e ajustes | Resolução | s/quadro | 60 s a 30 fps (1800 q) | Visual |
|---|---|---|---|---|---|
| Clay atual | Cycles 4 amostras + OIDN, 3 bounces, AgX | 540x960 | 1,0 (2,1 na bateria lenta) | 30 min (cena simples) | Massinha bonita, mas cor lavada com AgX padrão |
| Clay 720 | Cycles 4 amostras + OIDN | 720x1280 | 1,9 | 57 min | Igual ao anterior, mais nítido |
| Clay 2 amostras | Cycles 2 amostras + OIDN | 720x1280 | 1,1 | 33 min | Praticamente igual ao de 4 amostras nesta cena (o OIDN segura) |
| Clay 1 amostra | Cycles 1 amostra + OIDN | 720x1280 | 1,2 | 36 min | Começa a borrar sombras; não ganha tempo sobre 2 amostras |
| Clay "punchy" | Cycles 4 amostras, AgX Punchy, sol mais forte | 720x1280 | 2,1 | 63 min | Ainda acinzentado; o problema é o AgX, não as amostras |
| Flat iluminado | Cycles 4 amostras + OIDN, só Diffuse BSDF, 0 bounces, view Standard | 720x1280 | 1,45 | 44 min | Cores vivas, sombra real projetada, volume suave. Melhor custo-benefício "3D de verdade" |
| Flat iluminado | idem | 540x960 | 0,78 | 23 min | idem, menos nítido |
| Toon (cel shading) | Cycles 4 amostras SEM denoise, material só emissão com rampa de 3 tons calculada pela normal x direção da luz, sombra falsa em disco sob o personagem | 720x1280 | 0,6 | 18 min | Estilo desenho animado limpo, cores fortes, sem ruído nenhum |
| Toon | idem | 540x960 | 0,33 | 10 min | idem |
| Toon | idem | 1080x1920 | 1,3 | 39 min | Nativo em Full HD, sem upscale |
| Workbench | Studio light, cavity, sombra, contorno, AA 5 | 720x1280 | 0,75 | 23 min | Parece viewport de Blender, escuro e "técnico". Não recomendo |
| Workbench | idem, AA 8 | 1080x1920 | 4,0 | 2 h | Caro e feio para o propósito |
| EEVEE | 8 amostras TAA, roda via OpenGL por software (Mesa llvmpipe) | 720x1280 | 10 a 20 | 5 a 10 h | Bom, mas inviável sem GPU |
| EEVEE toon | Shader to RGB + rampa | 720x1280 | 11 | 5,5 h | Inviável sem GPU |

Conclusões dos testes:
- EEVEE funciona nesta máquina (Blender cai para renderização OpenGL em software), mas é 10 a 20 vezes mais lento que Cycles. O primeiro quadro leva quase 1 minuto só compilando shaders. Esqueça EEVEE enquanto não houver GPU.
- Workbench também passa pelo OpenGL em software, então não é o atalho que parece. Só é rápido em 720 com AA baixo e o visual não serve para o canal.
- Em Cycles, o que mais pesa não é o número de amostras, é o tipo de material e os bounces. Trocar Principled + 3 bounces por Diffuse + 0 bounces corta uns 25% e deixa as cores mais vivas. Trocar por emissão pura (toon) corta 70%.
- 2 amostras com OIDN é o ponto ideal para clay: abaixo disso não acelera (o denoiser passa a dominar o tempo) e piora a imagem.
- A cor "lavada" dos testes clay vem do AgX. Para cores fortes de Shorts, usar view transform Standard (ou AgX com saturação compensada nos materiais). No toon e no flat, Standard deixou as cores saturadas sem esforço.

## 2. Estilo recomendado

Recomendação: toon/cel shading feito com emissão em Cycles (o "cyctoon" dos testes), com a opção de "flat iluminado" para vídeos que pedem mais profundidade.

Por quê:
- É 3 vezes mais barato que o clay atual na mesma resolução, e por isso permite render nativo em 720x1280 (ou até 1080x1920) em vez de 540x960 esticado.
- Não tem ruído, então não depende de denoise (que às vezes "ferve" entre quadros em animação) e a compressão do YouTube/Instagram estraga menos: áreas de cor chapada comprimem muito bem.
- Parece "desenho animado 3D" intencional, que é uma estética que o público aceita como estilo, e não como "3D barato". O clay com AgX, por outro lado, sai cinza e parece render inacabado se não for muito bem iluminado.
- É 100% procedural e determinístico: o mesmo personagem sai idêntico todo dia, o que ajuda na consistência de mascote.

Como fazer o toon (já implementado em scripts/scene.py, função material com TOON):
- Material = Geometria.Normal · direção_da_luz → ColorRamp em modo Constant com 3 tons (sombra puxada para o azul/roxo, cor base, luz clara) → Emission. Nenhuma luz real é calculada.
- Cycles com max_bounces 0, 4 amostras, denoise desligado, filter_size 1,2 (anti-aliasing suficiente).
- View transform Standard.
- Sombra no chão: disco escuro achatado embaixo do personagem (custo zero). Se quiser sombra projetada real em algum plano, use o "flat iluminado" só naquela cena.
- Contorno opcional: casca invertida (solidify com normais invertidas e material preto emissivo, backface culling). Freestyle não testei porque é caro em CPU.

Comparação rápida dos estilos que o gerente listou:
- Toon/cel: o melhor custo x beleza (0,6 s/quadro em 720).
- Low poly flat: é o mesmo toon com rampa de 2 tons e shade flat. Mesmo custo, ótimo para cenários e objetos; para personagem fica menos fofo.
- Flat 3D / isométrico: câmera ortográfica + toon. Mesmo custo, e com câmera fixa dá para reaproveitar fundo (ver seção 4). Excelente para vídeos explicativos (mapas, processos, "como funciona").
- Clay/massinha: o mais caro (1 a 2 s/quadro na cena simples, 2,5 a 4 s nas cenas reais). Fica bonito com 2 amostras + OIDN + Standard + luz de área grande. Reservar para vídeos especiais.
- Papel (paper cut): planos com bevel leve e textura de ruído; em toon com sombra de disco fica barato. Viável.
- Voxel: cubos instanciados por geometry nodes, toon, custo baixo; o risco é a cena ter dezenas de milhares de cubos e o BVH pesar. Viável para cenas pequenas.

## 3. Resolução, upscale e penalização

- As duas plataformas recomendam 1080x1920. O mínimo aceitável em ambas é 720x1280; abaixo disso a recompressão deixa tudo mole. Nenhuma das duas "penaliza alcance" por resolução, mas vídeo borrado derruba retenção, que é o que importa.
- Decisão prática: renderizar em 720x1280 e fazer upscale Lanczos para 1080x1920 no FFmpeg na hora do encode. Para toon de cor chapada, o upscale Lanczos fica quase indistinguível do nativo (bordas limpas, sem textura fina para perder). 540x960 esticado é o limite inferior e se nota em texto e olhos.
- Upscale com IA (Real-ESRGAN e similares): em CPU de 2 núcleos custa segundos por quadro, ou seja, mais caro do que renderizar direto em 1080. Não compensa. Para toon, se precisar de 1080 nativo, é mais barato renderizar 1080 direto (1,3 s/quadro).
- Enviar sempre 1080x1920, H.264, CRF 18 a 20, 30 fps, AAC 160 a 192 kbps, faststart. Mandar 1080 em vez de 720 faz a plataforma reservar mais bitrate, mesmo que o conteúdo veio de 720.

## 4. Como cortar o tempo de render

Testado:
- 24 fps em vez de 30: corta 20% dos quadros sem mudar nada no visual de animação estilizada. O FFmpeg converte para 30 no encode duplicando quadros. Recomendado para cenas de personagem.
- Interpolação de quadros (renderizar 15 fps e gerar 30 com minterpolate): custa pouco (6,7 s para 6 s de vídeo em 720), mas borrou e deformou a boca e os olhos no teste (ver interp_15para30_exemplo.png). Só use em planos de câmera lenta sem personagem falando (paisagem, b-roll). A alternativa "framerate" (mistura de quadros) é rápida mas gera fantasma. Para personagem, prefira 24 fps nativo ou animação "em dois" (o personagem muda pose a cada 2 quadros, que é um visual de animação clássica e não precisa de interpolação).
- Render por região (border render): re-renderizar só a caixa da boca custou 0,04 s/quadro contra 0,57 do quadro inteiro (14 vezes menos). É assim que a versão EN fica quase de graça (seção 6).

Não testado, mas direto de aplicar:
- Fundos estáticos: em planos com câmera parada, renderizar o fundo uma vez (1 quadro) e renderizar o personagem com film_transparent + holdout nos objetos de fundo, depois compor no FFmpeg. Em plano fixo de 5 s isso transforma 150 quadros de cena inteira em 1 quadro de fundo + 150 quadros só do personagem (geralmente 30 a 50% da área).
- Câmera parada é amiga: zoom e pan suaves podem ser feitos em 2D no FFmpeg (crop/zoompan) em cima do render, desde que renderize com margem. Um plano de 4 s com "zoom lento" vira 1 render de quadro maior + zoom 2D. Para toon isso funciona muito bem porque não tem paralaxe perceptível em movimentos pequenos.
- Repetição de ciclos: idle do personagem (respiração, piscar, balanço) em loop de 24 a 48 quadros. Se a câmera estiver parada, renderiza o ciclo uma vez e repete.
- Cenas curtas: cortes a cada 2 a 4 s já são o ritmo ideal de Shorts e permitem misturar planos caros (personagem, câmera em movimento) com planos baratos (fundo fixo + texto, close estático com zoom 2D).
- persistent_data ligado (já está) evita recarregar a cena entre quadros. Agrupar todos os quadros de um plano numa única chamada de render.
- Evitar no CPU: volumes, vidro/transmissão, SSS, desfoque de movimento real, profundidade de campo com poucas amostras (gera ruído), bloom no compositor em cada quadro (fazer brilho com materiais emissivos e, se precisar, glow 2D no FFmpeg).
- Subdivisão: skin modifier com subsurf 2 é suficiente; 3 multiplica a geometria por 4 sem ganho visível em 720.

## 5. Personagens e cenários só por script

Funciona bem (já testado aqui e no vídeo dos dinossauros):
- Mascote "gota/feijão": skin modifier com 5 a 7 vértices (quadril, peito, cabeça, braços, pés) + subsurf 2. Olhos grandes (esfera branca + pupila + ponto de brilho emissivo) são 80% do carisma. Boca separada como objeto, para poder animar e re-renderizar por idioma.
- Expressões baratas: escala e rotação das pálpebras (meia esfera da cor do corpo por cima do olho), sobrancelha como cilindro curvo, pupilas que se movem, squash and stretch no corpo (já está no teste, quique com achatamento).
- Família de personagens: mesma base de skin modifier com parâmetros (altura, largura, cor, acessório: chapéu cone, óculos toro, antena). Gerar a partir de um dicionário JSON por personagem garante consistência entre vídeos.
- Animais estilizados: o T-rex, saurópode e raptor de lib.py mostram que skin modifier aguenta bichos inteiros. Bichos "fofos" com corpo de esfera + patas cilíndricas também funcionam.
- Cenários: chão plano com displacement leve, árvores cone + cilindro, pedras ico com displace, nuvens de esferas, prédios de cubos com bevel, água como plano emissivo com rampa. Texto 3D com extrusão e bevel.
- Geometry nodes para espalhar árvores/pedras/estrelas com semente fixa (reprodutível).
- Partículas simples: confete, poeira, faíscas como instâncias de esferas ou planos emissivos.

O que evitar: cabelo/pelo (curves ficaram até 15x mais pesadas no Blender 5), mãos com dedos, roupas com dobra, rostos realistas. Tudo isso quebra no estilo procedural e aumenta render.

Biblioteca de modelos livres para complementar (todos CC0, uso comercial sem atribuição):
- Kenney: milhares de modelos low poly de jogos (cidades, natureza, comida, veículos, interiores). Combina direto com toon.
- Quaternius: personagens e animais low poly, muitos já com rig e animações (andar, correr, acenar). É o atalho para ter bichos e pessoas estilizadas animadas sem modelar.
- Poly Haven: modelos, texturas PBR e HDRIs. Mais realistas; texturas úteis no clay, HDRIs dão para usar só como cor de fundo.
- ambientCG: texturas e materiais CC0.
- Poly Pizza: mistura CC0 e CC-BY, checar modelo por modelo (CC-BY exige crédito).
- Sketchfab: licença varia por modelo; só usar os marcados CC0, e nunca os "editorial" ou NC.

Regra para o agente 3D: baixar uma vez, guardar numa pasta assets/ com o arquivo de licença ao lado, e reaplicar os materiais toon por script (trocar todos os materiais por emissão com rampa usando a cor base original), para tudo ficar com o mesmo visual. Não baixar nada em tempo de execução diária.

## 6. Lip-sync e sincronização com a narração

Testado e funcionando (teste_lipsync_PT.mp4 e teste_lipsync_EN.mp4):
1. Gerar a narração com edge-tts pedindo boundary="WordBoundary". Isso devolve o tempo de início e duração de cada palavra (18 palavras no teste, em PT e EN). Sem esse parâmetro, a versão atual só devolve frases.
2. Converter o MP3 para WAV mono 48 kHz, calcular o RMS em janelas de 1/fps (1600 amostras a 30 fps).
3. Normalizar pelo percentil 95, aplicar ataque rápido e soltura lenta (valor = max(atual, anterior x 0,6)) e quantizar em 4 níveis (0, 1/3, 2/3, 1). A quantização faz a boca "pular" entre poses como desenho animado, e esconde a imprecisão.
4. Keyframe da escala da boca por quadro: altura 0,15 → 1,0 e largura 1,3 → 1,05 conforme o nível.
5. As palavras com tempo viram legenda ASS em grupos de 3, com a palavra falada destacada em amarelo (subs.py), queimada no FFmpeg com a fonte Poppins Bold.

Resultado: convincente para personagem cartoon. A boca abre nas sílabas fortes e fecha nas pausas. Custo de cálculo desprezível (menos de 1 s).

Melhorias possíveis, em ordem de custo:
- Trocar escala por 3 a 5 formas de boca (fechada, aberta, "O", "E", sorriso) como objetos ou shape keys, escolhendo pela intensidade e pela vogal da palavra atual (as palavras com tempo vêm do TTS, então dá para pegar a vogal tônica por regra simples de texto em PT e EN).
- Rhubarb Lip Sync (motor livre, MIT, com addon que funciona até Blender 5.2) gera as formas de boca clássicas de desenho animado a partir do áudio. O reconhecedor dele é treinado para inglês; em português funciona razoavelmente no modo fonético, mas é mais um binário para manter. Só vale se a boca por amplitude ficar pobre.
- Piscar automático: piscar a cada 2 a 5 s aleatório + piscar sempre no início de frase.
- Gestos ligados ao roteiro: o roteiro marca palavras-chave (ex.: [aponta], [surpreso]) e o script de cena põe keyframes de pose no tempo daquela palavra, que vem do WordBoundary.

Como fazer duas línguas sem renderizar duas vezes (testado):
- O vídeo é renderizado uma vez com a boca na versão PT (ou com a boca fechada, se preferir que as duas sejam overlays).
- Para EN, a cena é recarregada com a curva de boca EN e renderizada só na caixa da boca (border render + crop). No teste: 150x236 pixels, 0,04 s/quadro, 7,5 s para o clipe todo.
- O FFmpeg sobrepõe o recorte na posição fixa (overlay=x:y). No quadro comparativo não aparece emenda nenhuma, porque é a mesma cena, mesma luz e mesmo quadro.
- Isso só funciona se o rosto não se mover demais no plano. O script calcula a caixa que cobre a boca em todos os quadros do plano. Em plano com o personagem andando pela tela, renderize o plano inteiro de novo para EN (ou faça a fala em close).

Ponto crítico: PT e EN têm durações diferentes. No teste, a mesma frase deu 6,4 s em PT e 5,9 s em EN (8% a menos). Regra para o pipeline:
- Gerar os dois áudios ANTES da cena.
- Para cada frase, a duração do plano = maior das duas + 0,25 s.
- Na língua mais curta, completar com pausa no fim da frase ou ajustar o parâmetro rate do edge-tts (até -8%) para aproximar. Nunca usar atempo acima de 6%, porque a voz fica artificial.
- Os cortes de cena caem no início das frases, então o visual serve às duas versões.

## 7. Texto na tela

Não colocar texto em 3D renderizado dentro da cena (como o "DINOSSAUROS" do vídeo atual), porque aí o texto teria que ser renderizado duas vezes. Todo texto que muda por idioma vai como overlay 2D no FFmpeg (ASS com animação de entrada, ou PNG gerado com Pillow). Texto 3D só para coisas neutras: números, logotipo, símbolos, nomes próprios.

Zona segura: legenda no terço central-inferior, deixando livre os 14% de cima e os 35% de baixo (Reels) e a coluna direita de botões. No teste usei margem inferior de 620 px em 1920, que fica acima da interface das duas plataformas.

## 8. Tempo de CPU por dia (2 vídeos x 2 idiomas)

Premissas: um vídeo de humor de 30 s e um de conhecimento de 75 s por dia (105 s de vídeo). Cenas reais 1,5 a 2x mais pesadas que a cena de teste. Valores em tempo de relógio nesta máquina de 2 núcleos.

| Etapa | Uma vez por vídeo | Por idioma | Total do dia |
|---|---|---|---|
| Roteiro PT + adaptação EN (Claude) | sim | | minutos de LLM, não CPU local |
| TTS edge-tts (por frase) | | ~1 s por frase, 10 a 20 frases | ~1 min |
| Curva de boca, tempos de palavras, legenda ASS | | < 5 s | desprezível |
| Montagem da cena por script (bpy) | sim | | ~10 s por plano, ~2 a 4 min |
| Render toon 720 a 24 fps (2520 quadros) | sim | | 25 a 50 min |
| Render toon 720 a 30 fps (3150 quadros) | sim | | 32 a 63 min |
| Render flat iluminado 720 a 24 fps | sim | | 60 a 120 min |
| Render clay atual 540 a 30 fps (referência) | sim | | 2,2 a 3,5 h |
| Re-render da boca para EN (border) | | só EN, ~0,05 s/quadro em planos de fala | 2 a 3 min |
| Trilha e efeitos gerados (numpy) | sim | | < 1 min |
| Mix de áudio por idioma | | ~5 s | < 1 min |
| Encode 1080x1920 com upscale, legenda e overlay | | ~3 s por 6 s de vídeo | ~2 min por idioma, ~4 min no total |
| Verificação automática (ffprobe, quadros de amostra) | | segundos | ~1 min |

Total diário recomendado (toon 720, 24 fps nos planos de personagem): cerca de 40 min a 1h15 de CPU, e no pior caso com a VM lenta (2x) cerca de 2h30. Com o clay atual seriam 2,5 a 7 h, o que não cabe com folga se algo der errado e precisar renderizar de novo.

O que é renderizado uma vez só: toda a imagem 3D, a trilha e os efeitos sonoros.
O que muda por idioma: narração, curva de boca (recorte pequeno), legenda, textos 2D, título/descrição, mix final e encode.

## 9. Pipeline completo, em ordem

1. Tendência e pauta (agente diário): sai um JSON com tema, formato (humor 30 s ou conhecimento 60 a 90 s), tom (sério = voz masculina, leve = voz feminina) e personagem.
2. Roteiro PT (Claude) já dividido em frases, cada frase com: texto, plano/cenário, ação do personagem, palavra-chave para gesto, texto 2D de destaque. Formato JSON fixo validado por esquema.
3. Adaptação EN (Claude): localizar, não traduzir ao pé da letra, mantendo o mesmo número de frases e a mesma ordem, e com comprimento parecido (pedir para ficar entre 90% e 110% das sílabas do PT).
4. TTS PT e EN por frase com edge-tts e WordBoundary. Medir a duração de cada frase com ffprobe. Calcular a duração de cada plano como a maior das duas + respiro. Se uma frase passar de 120% da outra, voltar ao passo 3 e encurtar.
5. Linha do tempo: um JSON com início e fim de cada plano em quadros, posições dos gestos (do WordBoundary) e curvas de boca de cada idioma.
6. Geração de cena (bpy): um script por plano, usando a biblioteca de funções (personagem parametrizado, cenários, materiais toon, câmera). Plano curto = um processo Blender, para que um erro num plano não derrube o vídeo todo.
7. Prévia rápida: renderizar 3 quadros por plano em 540 (segundos) e checar automaticamente se a imagem não está preta, branca, vazia ou com o personagem fora do quadro (fração de pixels da cor do personagem na região central). Opcional: Claude olha a folha de contato antes do render final.
8. Render final em 720x1280, toon, 24 fps nos planos de personagem, com use_overwrite desligado e placeholder ligado (como já está em lib.py), para que uma interrupção retome do quadro onde parou.
9. Render da boca EN por região, nos planos com fala de personagem.
10. Áudio: narração + trilha gerada + efeitos, uma mix por idioma, normalizada (loudnorm, alvo perto de -14 LUFS integrado, pico -1 dBTP; detalhes no relatório de áudio).
11. Legendas ASS por idioma geradas dos WordBoundary, com quebra em grupos de 2 a 3 palavras e destaque da palavra falada.
12. Montagem FFmpeg por idioma: concatena planos, overlay da boca (EN), textos 2D, legenda, upscale Lanczos para 1080x1920, H.264 CRF 18 a 20, AAC, faststart. Saem dois MP4: <id>_PT.mp4 e <id>_EN.mp4.
13. Controle de qualidade automático: duração esperada (diferença menor que 0,2 s), áudio presente e não mudo, resolução 1080x1920, sem quadro preto (blackdetect), loudness dentro da faixa. Extrair 6 quadros e montar uma folha para revisão.
14. Agendamento no Metricool com título, descrição e hashtags de cada idioma.
15. Registro: salvar roteiro, JSONs, logs e o .blend de cada vídeo por 7 dias para refazer qualquer coisa sem regenerar tudo.

## 10. Pontos de falha e como blindar

- edge-tts parar de funcionar: já aconteceu (erro 403 na conexão com o serviço da Microsoft), e a correção foi atualizar o pacote. A versão instalada aqui é a 7.3.1. Blindagem: rodar pip install --upgrade edge-tts antes do TTS se falhar, tentar de novo com espera, e ter uma voz alternativa local (Piper ou similar) como plano B para não perder o dia.
- Durações PT/EN diferentes: descrito na seção 6. Sem o passo de equalizar, a versão mais longa fica com a fala cortada ou o vídeo termina antes.
- Render mais lento que o previsto (VM compartilhada oscila 2x): começar o render cedo, com pelo menos 2x de folga antes do horário de postagem. Ter sempre 1 ou 2 vídeos "de reserva" prontos (temas atemporais) para cobrir um dia que falhar.
- Processo Blender travado ou morto no meio: render por plano com placeholders, script de retomada que só renderiza quadros que faltam e timeout por plano.
- Cena com erro visual (câmera dentro de objeto, personagem fora de quadro, objeto preto por normal invertida, texto cortado): prévia rápida + checagem automática do passo 7.
- Skin modifier falha com raios ou vértices em configurações estranhas (gera malha quebrada ou some): usar só topologias testadas do catálogo de personagens, nunca deixar o LLM inventar vértices livres.
- Fontes e acentos: legenda com fonte que não tem ç, ã, õ. Usar Poppins ou Montserrat (testado com "CORAÇÕES" e funcionou).
- Texto 3D com idioma: evitar, pelos motivos da seção 7.
- Sobreposição da boca desalinhada se a câmera ou o personagem se moverem demais: o script calcula a caixa em todos os quadros e, se a caixa passar de ~30% da tela, re-renderiza o plano inteiro para EN.
- Disco cheio: 1 vídeo de 75 s em PNG 720 dá ~1 GB de quadros. Apagar os PNG depois do encode e checagem.
- Política do YouTube contra conteúdo "inautêntico": em julho de 2026 o YouTube reforçou que conteúdo genérico, repetitivo, feito em massa por template de IA não é monetizável. Isso afeta direto um canal automatizado. Blindagem técnica: variar cenários, planos, enquadramentos e personagens entre vídeos (o gerador de cena precisa ter muitas variações, não um template único), ter roteiro com ponto de vista próprio, e nunca usar personagem de IA posando de especialista em saúde, dinheiro ou direito.
- Upscale de IA ou interpolação deformando o personagem: não usar (seções 3 e 4).
- Mudanças do Blender entre versões (o compositor e alguns nomes de propriedade mudaram no 5.x, como já tratado em lib.py com try/except): fixar a versão do bpy no ambiente e só atualizar depois de rodar a cena de teste (scripts/scene.py) e comparar os quadros.

## 11. Resumo das decisões

- Motor: Cycles em CPU. EEVEE e Workbench descartados sem GPU.
- Estilo: toon/cel shading por emissão (0,6 s/quadro em 720 na cena de teste), com flat iluminado (1,45 s) para cenas que pedem sombra real, e clay só em vídeos especiais.
- Resolução: render 720x1280, encode 1080x1920 com Lanczos. Sem upscale de IA.
- Fps: 24 nos planos de personagem (convertido para 30 no encode), sem interpolação em personagem.
- Lip-sync: amplitude do TTS quantizada em 4 níveis, tempos de palavra do próprio edge-tts para legenda e gestos.
- Dois idiomas: render uma vez, boca EN por região (0,04 s/quadro), texto e legenda em 2D.
- CPU diária: cerca de 40 min a 1h15 para 2 vídeos x 2 idiomas (até 2h30 com a VM lenta), contra 2,5 a 7 h no clay atual.
