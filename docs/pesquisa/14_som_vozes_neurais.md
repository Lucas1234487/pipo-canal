# 14. Som e vozes neurais (som_vozes_neurais)

Relatório do Agente 14 do ShoShortz. Data: 21/11/2026.
Base: pesquisa web do estado atual e testes práticos feitos aqui (edge-tts 7.3.1, Piper, Whisper para checar a inteligibilidade, librosa para medir pitch e ffmpeg para mixar e medir loudness).

---

## Resumo em uma tela

| Papel | Voz | Parâmetros edge-tts | Reserva |
|---|---|---|---|
| PT masculina séria | `en-US-AndrewMultilingualNeural` (falando português) | rate `+8%`, pitch `-2Hz` | `en-US-BrianMultilingualNeural` (+8%, -2Hz); último recurso `pt-BR-AntonioNeural` (+8%, -4Hz) |
| PT feminina leve | `pt-BR-ThalitaMultilingualNeural` | rate `+10%`, pitch `+2Hz` | `pt-BR-FranciscaNeural` (+10%, +3Hz) |
| EN masculina séria | `en-US-AndrewMultilingualNeural` | rate `+5%`, pitch `-2Hz` | `en-GB-RyanNeural` (+8%, -2Hz), a mais expressiva medida |
| EN feminina leve | `en-US-EmmaMultilingualNeural` | rate `+10%`, pitch `+3Hz` | `en-GB-SoniaNeural` (+10%, +3Hz) |

Por que essa combinação:
- A voz masculina é a mesma nas duas línguas (Andrew Multilingual fala português e inglês). Fica o mesmo "narrador do canal" no PT e no EN, e isso já é metade da assinatura sonora.
- A Thalita é a voz pt-BR nativa mais nova da Microsoft e aparece bem menos que a Francisca e o Antonio nos vídeos de TikTok BR.
- A Emma foi a voz feminina mais expressiva medida em inglês (maior variação de entonação) e é bem menos batida que a Jenny e a Aria, que foram o padrão de TTS por anos.
- Antes de travar a escolha, o Lucas precisa ouvir os arquivos. Eu medi inteligibilidade e expressividade, mas não consigo julgar sotaque de ouvido. O ponto mais sensível é o Andrew falando português (ver seção 1).

Efeitos e trilha: gerados por código (script pronto em `vozes/sfx_procedural.py`, roda em menos de 1 segundo), mais um acervo CC0 baixado uma vez (Kenney e Freesound filtrado por CC0). Nada de música em alta.

Volume final: -14 LUFS integrado, pico real abaixo de -1 dBTP, trilha uns 15 a 18 dB abaixo da voz enquanto alguém fala (ducking automático). A cadeia ffmpeg testada está em `vozes/mix_demo.sh` e deu -13,7 LUFS com pico de -3,5 dBFS.

Ponto jurídico importante: o edge-tts usa o serviço de leitura em voz alta do Edge, que não tem licença comercial clara. As mesmas vozes existem no Azure AI Speech, que tem nível gratuito (F0) e licença comercial. O volume do canal cabe no nível gratuito. Recomendo prototipar no edge-tts e publicar com Azure F0 (seção 1.3).

---

## Arquivos gerados nos testes

Pasta: `/home/claude/canal/pesquisa/vozes/`

- 69 amostras `PT_*` e `EN_*`: mesma frase em cada voz candidata, com 3 variações de rate e pitch.
  - Frase séria PT: "Você sabia que o seu cérebro apaga memórias toda noite? Parece estranho, mas é isso que te mantém são."
  - Frase leve PT: "Gente, o polvo tem três corações. Três! E mesmo assim ele não consegue lidar com uma segunda-feira."
  - As mesmas duas frases em inglês.
  - Sufixos: `_base` (sem ajuste), `_r8_pm4` (+8%, -4Hz), `_r12_p0` (+12%), `_r10_p3` (+10%, +3Hz), `_r15_p5` (+15%, +5Hz).
- `X_*`: vozes multilíngues usadas na outra língua (Thalita falando inglês, William, Andrew e Emma Multilingual em inglês), para testar uma voz única nas duas versões.
- `Z_offline_Piper_faber_PT_M.wav`: voz open source offline (Piper, pt_BR faber), para comparar.
- `sfx/`: pop, whoosh, ding, boing, riser, thump, click, squish, vinheta do canal, trilha leve (96 bpm) e trilha séria (84 bpm), todos gerados por código.
- `sfx_procedural.py`: gerador desses sons (numpy puro). Com `python3 sfx_procedural.py <pasta> <seed>` cada seed dá uma melodia diferente.
- `mix_demo.sh` e `mix_demo_PT_leve.m4a`: demo de mixagem (vinheta + whoosh + voz + trilha com ducking + pop), normalizada em 2 passadas.

Ordem de escuta sugerida para o Lucas (10 minutos):
1. `PT_M_AntonioNeural_base` (referência do que queremos evitar), depois `PT_M_AndrewMultilingualNeural_r8_pm4`, `PT_M_BrianMultilingualNeural_r8_pm4` e `PT_M_WilliamMultilingualNeural_r8_pm4`. A pergunta é: o Andrew ou o Brian soam brasileiros o bastante?
2. `PT_F_ThalitaMultilingualNeural_r10_p3` contra `PT_F_FranciscaNeural_r10_p3` e `PT_F_EmmaMultilingualNeural_r10_p3`.
3. `EN_M_US_AndrewNeural_r8_pm4`, `EN_M_GB_RyanNeural_r8_pm4` e `EN_M_US_ChristopherNeural_base`.
4. `EN_F_US_EmmaNeural_r10_p3`, `EN_F_US_AvaNeural_r10_p3` e `EN_F_GB_SoniaNeural_r10_p3`.
5. `mix_demo_PT_leve.m4a` no alto-falante do celular, para conferir o volume.

---

## 1. Vozes neurais gratuitas ou baratas além do Antonio

### 1.1 O que existe no edge-tts hoje (lista real, consultada hoje)

Português do Brasil nativo: só 3 vozes.
- `pt-BR-AntonioNeural` (M): a mais usada em TikTok e Shorts BR, soa "voz de TikTok".
- `pt-BR-FranciscaNeural` (F): também muito usada, fica com cara de "voz do Google Tradutor melhorada".
- `pt-BR-ThalitaMultilingualNeural` (F): nativa, mais nova, menos vista. É a melhor opção feminina.

Não existe voz masculina pt-BR nativa além do Antonio no edge-tts. A saída são as vozes Multilingual, que leem qualquer idioma e detectam a língua pelo texto:
- `en-US-AndrewMultilingualNeural` (M, "Warm, Confident, Authentic"), a mais "narrador de documentário".
- `en-US-BrianMultilingualNeural` (M, "Approachable, Casual, Sincere"), mais leve e conversada.
- `en-AU-WilliamMultilingualNeural` (M), grave e mais monótona.
- `en-US-AvaMultilingualNeural` e `en-US-EmmaMultilingualNeural` (F).

Inglês (en-US e en-GB) tem muitas opções. As mais naturais são a geração "Copilot/Conversation" (Andrew, Brian, Ava e Emma). Christopher, Eric, Guy, Roger e Steffan são da geração "News/Novel", mais locutor. Ana é infantil/cartoon (pode servir para personagem, não para narração). Jenny e Aria são as que mais soam "TTS clássico" e foram as mais usadas até 2024. No en-GB: Ryan, Thomas, Sonia, Libby e Maisie (Maisie é jovem e aguda). Também há en-AU e en-IE (Connor, Emily, Natasha).

### 1.2 Medições dos testes

Inteligibilidade: transcrevi cada amostra com Whisper small e conferi se o idioma detectado era o certo.

| Voz falando PT | Transcrição | Idioma detectado | Pitch médio | Variação de entonação* |
|---|---|---|---|---|
| Antonio | perfeita | pt 1.00 | 134 Hz | 4,8 (a mais expressiva) |
| Brian Multilingual | perfeita | pt 1.00 | 131 Hz | 4,35 |
| Andrew Multilingual | quase perfeita (pausa estranha antes de "são") | pt 0.99 | 115 Hz (mais grave) | 3,5 a 3,9 |
| William Multilingual | perfeita | pt 1.00 | 108 Hz | 2,9 (mais monótona) |
| Thalita | perfeita | pt 1.00 | 204 Hz | 2,9 a 3,1 |
| Francisca | perfeita | pt 0.99 | 251 Hz (mais aguda) | 3,2 |
| Emma Multilingual | perfeita | pt 0.99 | 219 Hz | 4,5 |
| Ava Multilingual | perfeita | pt 0.99 | 225 Hz | 2,9 |
| Piper faber (offline) | perfeita | - | 154 Hz | 3,0 |

*Desvio padrão do pitch em semitons. Quanto maior, menos monótona. Na faixa das vozes testadas, acima de 4 já soa viva.

Inglês, frase séria (masculinas): Ryan GB teve a maior variação (6,4), seguido de Andrew (4,4), Thomas (3,6), Christopher (3,6), Eric (3,6), Guy (3,6) e Brian (3,1). O Andrew é a voz mais rápida e direta (6,1 s na frase, contra 7,3 s do Christopher), o que combina com Shorts.

Inglês, frase leve (femininas): Emma (4,3 a 4,6), Sonia (4,1), Libby (4,0), Aria (3,8), Ava (3,4), Jenny (3,1), Maisie (2,3) e Ana (1,7, infantil e chapada).

Observações práticas:
- Todas transcreveram "polvo" como "povo". É limitação do Whisper, não da voz. Mesmo assim, palavras curtas e parecidas merecem atenção no roteiro.
- Mesmo com transcrição perfeita, as Multilingual em português podem ter um leve sotaque estrangeiro nas vogais nasais e no "r". Isso só se decide de ouvido. Se o Lucas achar o Andrew "gringo", vale o Brian Multilingual. Se os dois soarem gringos, fica o Antonio com pitch -4Hz e rate +8%, que já soa bem diferente do Antonio padrão do TikTok.
- O edge-tts falhou uma vez sem motivo (NoAudioReceived) e funcionou na segunda tentativa. O pipeline precisa repetir até 4 vezes com espera de 2 s.

### 1.3 Licença e uso comercial (importante)

- A biblioteca edge-tts é GPL-3 e pode ser usada à vontade. O problema é o serviço: ela usa o endpoint gratuito do "Ler em voz alta" do Edge, que não é uma API comercial documentada. Nas respostas oficiais do fórum, a Microsoft diz que uso comercial do serviço sem assinatura Azure válida "pode violar os termos". Não há proibição explícita de YouTube, mas também não há permissão.
- O caminho seguro e gratuito é o Azure AI Speech, nível F0. São as mesmas vozes (Andrew, Thalita, Emma, Brian...), com uso comercial permitido, SSML completo (pausas exatas, ênfase, estilos de emoção em algumas vozes) e cota mensal gratuita de caracteres de voz neural, historicamente 0,5 milhão por mês. Confirme o valor atual ao criar a conta.
- Conta do consumo: 2 vídeos por dia × 2 idiomas × uns 1.200 caracteres (90 s de fala) dá uns 150 mil caracteres por mês. Cabe com folga no F0.
- Recomendação: usar edge-tts para prototipar e testar vozes (grátis, sem conta). Quando o canal entrar no Programa de Parcerias ou antes de monetizar, trocar o módulo de voz para o SDK do Azure F0, sem mudar as vozes. O código do pipeline deve ter uma função `sintetizar(texto, voz, rate, pitch)` com dois backends, para trocar com uma linha.

### 1.4 Outras opções grátis ou baratas (fora da Microsoft)

- Google Cloud TTS e Amazon Polly: têm níveis gratuitos mensais e vozes pt-BR (Chirp/Neural). São boas, mas exigem cartão e conta cloud. Não ganham da Microsoft em pt-BR para esse uso.
- ElevenLabs e similares: são as mais humanas, mas o plano gratuito não permite uso comercial e exige atribuição. Os planos pagos baratos (5 a 11 dólares por mês) dão uns 30 a 100 mil caracteres. É a evolução natural se o canal monetizar e a voz virar o gargalo de retenção.
- Open source local: seção 2.

---

## 2. Modelos open source de TTS em CPU com bom pt-BR

| Modelo | Licença | pt-BR | CPU | Clonagem | Veredito para nós |
|---|---|---|---|---|---|
| Piper | MIT (código). Cada voz tem a licença do seu dataset no MODEL_CARD | Vozes faber, cadu, jeff e edresson (low/medium) | Muito rápido. Testado: frase de 6 s gerada em 1,6 s, já contando o carregamento | Não | Backup offline. Inteligível, porém mais monótono (variação 3,0) e com cara de assistente |
| Kokoro-82M | Apache 2.0 (comercial OK) | 3 vozes: pf_dora (F), pm_alex (M) e pm_santa (M) | 3 a 5x mais rápido que o tempo real em CPU | Não | Ótimo em inglês, mediano em português (prosódia mais plana). Vale testar a pm_alex como segunda voz masculina PT se o Andrew não servir |
| Chatterbox Multilingual (Resemble) | MIT, com marca d'água inaudível (PerTh) | Sim (pt-br e pt-pt) | Roda, mas é lento (bem mais lento que o tempo real em CPU; pensado para GPU) | Sim, zero-shot com mais de 10 s de áudio de referência, controle de emoção | O único caminho sério para uma voz própria clonada (ver seção 4). Aceitável porque o render 3D já leva 1 h por vídeo |
| F5-TTS pt-br | Pesos CC-BY-NC (dataset Emilia) | Sim, bom | Lento | Sim | Não serve: licença não comercial |
| XTTS-v2 (Coqui) | Coqui Public Model License, não comercial (a empresa fechou) | Sim | Lento | Sim | Não serve |
| Fish Speech, Voxtral, CosyVoice | Licenças de pesquisa ou com restrições | Parcial | GPU | Sim | Não serve agora |

Conclusão: em qualidade de pt-BR, nenhum open source em CPU supera hoje as vozes neurais da Microsoft. Use open source como backup (Piper ou Kokoro) e como caminho para clonagem própria (Chatterbox).

---

## 3. Como a narração não soar como IA genérica

### 3.1 Limites do edge-tts atual
Desde a versão 5, o edge-tts não aceita SSML personalizado. Por chamada, só existem `rate`, `pitch` e `volume`, e mais nada (sem `<break>`, sem `<emphasis>`, sem estilos). No Azure F0 o SSML completo funciona. Com edge-tts dá para contornar assim:

### 3.2 Técnicas que funcionam (aplicáveis já)
1. Velocidade: o padrão do edge-tts é lento para Shorts (uns 2,4 palavras por segundo em PT). Use +8% a +12% na voz séria e +10% a +15% na leve. Acima de +18% começa a engolir sílabas.
2. Pitch: só ajuste fino, entre -4Hz e +5Hz. Mais que isso gera timbre artificial (efeito "esquilo" ou "robô grave"). O ganho real está na velocidade e nas pausas, não no pitch.
3. Pausas controladas: gere a narração frase por frase (ou bloco por bloco) e junte com silêncios escolhidos pelo roteiro. Regra prática:
   - 0,15 a 0,25 s entre frases normais;
   - 0,4 a 0,6 s antes de uma revelação ("E sabe o que acontece?" [pausa] "Ele explode.");
   - nenhuma pausa no gancho dos primeiros 2 segundos.
4. Ênfase sem SSML: a palavra-chave vai num segmento próprio com rate um pouco menor (-5%) e pitch +2Hz. Ou repita a palavra como frase curta ("Três!"). No teste, "Três!" sozinho já gerou uma entonação de ênfase natural.
5. Pontuação como controle: vírgula gera micro-pausa, reticências geram hesitação, a interrogação sobe o fim da frase e a exclamação dá energia. O agente de roteiro deve escrever pensando no TTS: frases curtas, números por extenso quando a leitura for ambígua ("1,5" vira "um e meio"), siglas soletradas com hífen ("D-N-A") e palavras em inglês no texto PT escritas como se fala, se a voz errar ("xórts" em vez de "Shorts").
6. Variar a energia ao longo do vídeo: gancho com +12%, explicação com +8%, desfecho e CTA com +5%. Mudar a velocidade entre blocos quebra a cara de "texto lido de uma vez".
7. Pós-processamento leve na voz (dá cara de "gravado", não de API): passa-alta em 80 Hz, compressor 3:1, +2 dB de presença em 3 kHz e, opcionalmente, um reverb de sala bem curto e baixo. Está na cadeia do `mix_demo.sh`.
8. Legenda palavra por palavra: testado. O edge-tts devolve o tempo de cada palavra com `boundary="WordBoundary"` (por exemplo, "polvo" em 0,95 s com duração de 0,34 s). É a base para as legendas animadas, sem precisar rodar Whisper.
9. Evitar "produção em massa": não mudar a voz a cada vídeo (isso destrói a identidade), mas mudar ritmo, pausas e trilha conforme o tema e a série. Também dá para usar uma terceira voz para personagens (por exemplo, `en-US-AnaNeural` infantil ou o Brian como "segundo personagem").

### 3.3 Esqueleto de código (edge-tts com pausas, retry e legenda)
```python
import certifi; certifi.where = lambda: "/root/.ccr/ca-bundle.crt"  # só neste ambiente
import asyncio, edge_tts, subprocess

async def seg(texto, voz, rate, pitch, arq, tent=4):
    for i in range(tent):
        try:
            c = edge_tts.Communicate(texto, voz, rate=rate, pitch=pitch, boundary="WordBoundary")
            palavras = []
            with open(arq, "wb") as f:
                async for ch in c.stream():
                    if ch["type"] == "audio": f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        palavras.append((ch["offset"]/1e7, ch["duration"]/1e7, ch["text"]))
            return palavras
        except Exception:
            await asyncio.sleep(2)
    raise RuntimeError("TTS falhou")
# roteiro = [("Você sabia...", "+12%", "-2Hz", 0.2), ("Ele explode.", "+5%", "-2Hz", 0.5), ...]
# gera cada bloco, soma os offsets + pausas para montar a legenda e concatena com
# ffmpeg (anullsrc para os silêncios, filtro concat).
```

---

## 4. Dá para criar uma voz própria do canal sem custo e sem violar licença?

Sim, em dois níveis:

1. "Voz da marca" por parâmetros (já, custo zero, sem risco): é o que está na tabela do topo. Sempre a mesma voz, mesma velocidade, mesmo pitch, mesma cadeia de EQ e compressão e mesmo reverb curto. O público reconhece o conjunto, não a voz crua. Com a mesma voz Multilingual no PT e no EN, o narrador é literalmente o mesmo nas duas versões. É legal porque são vozes de catálogo, que podem ser usadas comercialmente via Azure.

2. Voz clonada própria (fase 2, custo zero, mais lenta):
   - Use o Chatterbox Multilingual (MIT) com 10 a 30 s de áudio limpo da voz do próprio Lucas, ou de alguém que autorize por escrito (por exemplo, um amigo, com uma autorização simples guardada).
   - O modelo leva o mesmo timbre para PT e EN, então dá uma voz realmente exclusiva nas duas línguas.
   - Custo: o tempo de CPU. Ainda assim, é menor que o render 3D e pode rodar em paralelo.
   - Proibido: clonar voz de famoso, dublador, streamer, personagem ou qualquer pessoa sem consentimento. Isso viola as políticas do YouTube e da Meta e, no Brasil, direitos de personalidade.
   - Rótulo de conteúdo sintético: voz clonada realista de pessoa real pede o rótulo de IA do YouTube. O agente de políticas cuida disso. Com voz de catálogo e animação 3D estilizada, normalmente não é obrigatório, mas confira com ele.
   - "Misturar" vozes (interpolar embeddings, como o Kokoro permite entre as suas vozes) é tecnicamente possível e a licença Apache permite, mas em pt-BR o resultado fica abaixo das vozes Microsoft. Só para experimento.

Recomendação: começar com o nível 1. Quando o canal tiver umas 30 publicações, fazer um teste A/B com a voz clonada do Lucas em PT (Chatterbox) contra o Andrew e olhar a retenção nos primeiros 3 segundos.

---

## 5. Trilhas e efeitos livres para uso comercial

### 5.1 Geração procedural (prioridade 1: 100% nossa, zero risco de Content ID)
Já está pronto: `vozes/sfx_procedural.py` (numpy, roda em menos de 1 s). Gera:
- pop (massinha e bolha, para objeto aparecendo), squish (amassar), boing (comédia), click (texto surgindo), whoosh com pan estéreo (transição), riser (tensão antes da revelação), thump (impacto ou corte seco), ding (curiosidade, "você sabia") e a vinheta do canal (pop + arpejo de marimba + sino, 1,2 s);
- trilhas em loop com bateria, baixo, pad e melodia pentatônica aleatória: "leve" (maior, 96 bpm) e "séria" (menor, 84 bpm). Tonalidade, bpm e seed mudam a cada vídeo, então nenhuma trilha se repete igual.

Como evoluir sem perder a originalidade:
- variar a seed por vídeo e o bpm por série (humor de 100 a 115 bpm, curiosidade de 85 a 95, mistério e sério de 70 a 85);
- criar 3 ou 4 "kits" de timbre (marimba, synth pluck, piano elétrico, chiptune) e sortear um por série;
- usar o Blender como fonte de sincronia: o script 3D exporta os tempos dos eventos (objeto aparece, colide, explode) num JSON, e o mixador coloca o pop, o thump ou o whoosh exatamente nesses quadros. Isso dá uma sensação de produção cara;
- para sons mais ricos sem baixar nada: o ffmpeg tem gerador de ruído e de seno (`anoisesrc`, `sine`, `aevalsrc`) e dá para usar o FluidSynth com um SoundFont livre (por exemplo, GeneralUser GS ou FluidR3, confira a licença) para tocar MIDI gerado em Python (biblioteca `mido`). Assim a trilha soa como instrumento real.

### 5.2 Bancos prontos (prioridade 2: baixar uma vez e guardar num acervo local com manifesto)
- Kenney (pacotes de áudio): CC0, sem atribuição, ótimos para UI, impactos, pops e cliques.
- Freesound: só o filtro "Creative Commons 0". Evite CC-BY-NC (proíbe comercial) e Sampling+. CC-BY é permitido, mas exige crédito na descrição, o que complica a automação. Cuidado: há uploads de material de terceiros, então prefira autores com muitos envios próprios.
- Sonniss GDC Bundle (inclusive o de 2026): grátis, uso comercial em obras finalizadas, sem atribuição. Não é CC0: não pode redistribuir os sons soltos e é proibido usar para treinar IA. Para efeitos dentro do vídeo, é perfeito e tem qualidade de cinema.
- YouTube Audio Library: grátis e sem Content ID, mas parte das faixas exige crédito, e a licença é pensada para o YouTube. Para a versão Reels, prefira o procedural.
- Pixabay Music: uso livre sem atribuição, mas faixas do Pixabay às vezes recebem reivindicação de Content ID mesmo licenciadas. Use pouco.
- Mixkit, Uppbeat, Incompetech, Jamendo e Free Music Archive: licença por faixa, crédito obrigatório ou restrições. Evitar no pipeline automático.
- BBC Sound Effects: não permite uso comercial no plano gratuito. Evitar.

Regra para o pipeline: todo arquivo de terceiros entra no acervo com um `manifesto.csv` (arquivo, origem, autor, licença, data do download). O agente de edição só pode puxar sons do acervo e do gerador procedural, nunca da internet na hora.

### 5.3 Música por IA
- ACE-Step 1.5: código MIT (confira a licença dos pesos no Hugging Face). Gera músicas completas e instrumentais com qualidade alta, mas foi feito para GPU. Em CPU, uma faixa de 30 s deve levar dezenas de minutos ou mais. Opção: gerar um banco de 30 a 50 trilhas uma vez (num fim de semana, ou numa GPU gratuita tipo Colab, se os termos permitirem) e reutilizar trocando trechos.
- Stable Audio Open: licença comunitária da Stability. Na versão que eu conheço, uso comercial grátis até 1 milhão de dólares de receita anual. Confira os termos atuais. É bom para texturas e efeitos.
- MusicGen (Meta): pesos não comerciais. Não usar.
- Suno e Udio: só plano pago permite uso comercial, e há disputas judiciais com gravadoras. Não recomendo para canal automatizado.

---

## 6. Volume ideal (LUFS) para Shorts e Reels no celular

Alvos:
- Volume integrado: -14 LUFS (aceitável de -15 a -13). Nenhuma plataforma publica número oficial: -14 é o observado no YouTube e o padrão de mercado para Reels e TikTok. Acima de -14 o YouTube só abaixa, então "mixar alto" não ganha nada.
- Pico real (true peak): no máximo -1 dBTP, para evitar distorção quando a plataforma recodifica em AAC/Opus.
- Faixa dinâmica: baixa (LRA de 2 a 6 LU), porque o celular toca em ambiente barulhento e com alto-falante pequeno.

Equilíbrio dentro da mixagem (referência é a voz):
- Voz: elemento principal, normalizada sozinha por volta de -16 a -15 LUFS antes da mixagem.
- Trilha com voz por cima: 15 a 18 dB abaixo da voz (ducking por sidechain). Sem voz (intro, transições, final): sobe para uns 6 a 8 dB abaixo do nível da voz.
- Efeitos: picos de 3 a 6 dB abaixo da voz. Efeitos de impacto podem chegar perto do nível da voz se não houver fala ao mesmo tempo.
- Grave: corte abaixo de 80 Hz na voz e abaixo de 40 Hz no geral. O alto-falante do celular não reproduz sub-grave, então o "peso" do impacto precisa estar entre 100 e 200 Hz (o thump procedural já tem harmônicos nessa faixa).
- Presença: +2 dB por volta de 3 kHz na voz, para inteligibilidade no alto-falante do celular.
- Compatibilidade mono: o pan do whoosh é bonito no fone, mas nada importante pode depender do estéreo.

Cadeia testada (`mix_demo.sh`):
1. Voz: highpass 80 Hz, compressor 3:1, EQ +2 dB em 3 kHz.
2. Trilha a -6 dB, com sidechaincompress acionado pela voz (threshold 0.03, ratio 8, attack 20 ms, release 300 ms).
3. amix, depois um limitador.
4. loudnorm em 2 passadas no modo linear. Em clipe curto, a passada única ficou em -16,3 LUFS, longe do alvo. Com 2 passadas deu -13,7 LUFS e pico de -3,5 dBFS. O pipeline deve sempre usar 2 passadas.
5. Saída AAC 192 kbps, 48 kHz.

Checagem automática no fim de cada vídeo: `ffmpeg -i video.mp4 -af ebur128=peak=true -f null -`. Rejeite e refaça se o volume integrado ficar fora de -15 a -13 ou o pico passar de -1.

---

## 7. Músicas em alta: dá para usar? Ajudam no alcance?

Instagram:
- Conta comercial (Business): acesso só à Meta Sound Collection, uns 14 mil faixas liberadas para uso comercial. As músicas em alta de verdade não ficam disponíveis.
- Conta de criador (Creator): acesso amplo à biblioteca, inclusive músicas em alta, mas para uso não comercial. Publi, venda de produto ou parceria pede música licenciada à parte.
- A licença da biblioteca da Meta vale só no Facebook e no Instagram. Ela não vai junto para o YouTube.
- Problema prático do nosso caso: a postagem via Metricool usa a API do Instagram, que não permite escolher música da biblioteca. Só dá para publicar com o áudio que já está no arquivo, que vira "áudio original", e, no máximo, dar um nome a ele. Ou seja, música em alta exigiria postagem manual, o que quebra a automação.

YouTube Shorts:
- Música adicionada pelo editor do próprio app ("Adicionar som") é coberta pelos acordos das gravadoras, para Shorts de até 60 s (em alguns casos 90 s). Isso também exige edição manual no app.
- A mesma música colocada fora do app, no nosso pipeline ffmpeg, gera reivindicação de Content ID. Em Shorts de mais de 1 minuto, uma reivindicação ativa pode bloquear o vídeo no mundo inteiro.
- Receita: Shorts com música licenciada dividem o bolo com os detentores. Com uma faixa, metade da parte atribuída vai para a música antes da divisão com o criador. Áudio original fica fora dessa divisão.

Alcance: não existe evidência sólida e atual de que música em alta aumente a distribuição de Shorts ou Reels de forma consistente. O que se vê é a música ajudando quando o formato do vídeo é a própria trend (dança, dublagem, meme sonoro), e não é o nosso caso. Para conteúdo narrado, a voz e o gancho pesam muito mais.

Decisão: 100% áudio original (voz + trilha procedural + efeitos CC0 ou próprios). No Instagram, o áudio fica como "áudio original ShoShortz", que outras pessoas podem reutilizar, e isso vira divulgação grátis. Se algum dia valer muito a pena surfar uma trend sonora, faça um vídeo manual pontual, fora do pipeline.

---

## 8. Mesma assinatura sonora no PT e no EN

1. Separar a trilha do idioma: o pipeline monta primeiro um "stem M&E" (música + efeitos) único por vídeo, sincronizado com os eventos do 3D (JSON exportado do Blender). Depois só a voz muda entre PT e EN. Efeitos e trilha ficam idênticos nas duas versões.
2. Vinheta sem palavras: a vinheta do canal (pop + arpejo + sino, 1,2 s) não tem fala, então funciona igual nas duas línguas. Use a mesma vinheta sempre, no mesmo lugar: nos primeiros 0,3 s junto com o gancho, ou como "selo" no último segundo (que ajuda no loop). Não coloque vinheta longa no começo, porque mata a retenção.
3. Dicionário fixo de efeitos por função: aparecer = pop; transição = whoosh; revelação = riser + thump; curiosidade = ding; piada = boing; texto na tela = click. Com o mesmo som para o mesmo tipo de evento, o público passa a reconhecer o canal pelo ouvido.
4. Mesmo narrador nas duas línguas: Andrew Multilingual nos vídeos sérios, em PT e EN. Nos leves, Thalita (PT) e Emma (EN) têm timbre parecido (médio, simpático) e passam com a mesma cadeia de EQ e reverb para soarem "da mesma família". Se o Lucas aprovar a Thalita falando inglês (`X_EN_F_Thalita_falando_ingles.mp3`) ou a Emma falando português (`PT_F_EmmaMultilingualNeural_*`), dá para usar uma única voz feminina nas duas línguas também.
5. Duração diferente entre línguas: o texto em PT costuma ser 15% a 25% mais longo que o EN. Nos testes, a frase leve deu 7,2 s com a Thalita em PT e 6,2 s com a Emma em EN. Monte o vídeo pela versão PT, que é o público principal. Na EN, ajuste a velocidade para caber (calcule o rate pela razão das durações, limitado a +15%) ou aumente as pausas entre blocos, para que cada frase caia no mesmo evento visual. As legendas vêm do WordBoundary de cada idioma.
6. Mesma loudness e mesma cadeia: as duas versões passam pelo mesmo `mix_demo.sh` (ou a função equivalente), com o mesmo alvo de -14 LUFS.

---

## Próximos passos concretos
1. Lucas ouve as amostras na ordem da seção "Arquivos gerados" e confirma ou troca as 4 vozes (decisão de 10 minutos). O ponto crítico é o Andrew em PT.
2. Criar a conta Azure AI Speech F0 e implementar o backend Azure na função de síntese, com as mesmas vozes. Usar `<break>` e `<prosody>` do SSML no lugar do truque de segmentos.
3. Integrar `sfx_procedural.py` e a cadeia do `mix_demo.sh` no agente de edição, com loudnorm em 2 passadas e checagem automática de LUFS.
4. Baixar uma vez o Kenney Audio e o Sonniss GDC 2026 e montar o acervo com `manifesto.csv`.
5. Fazer o Blender exportar o JSON de eventos para sincronizar os efeitos.
6. Fase 2 (depois de umas 30 publicações): teste A/B da voz clonada do Lucas com Chatterbox em CPU.
