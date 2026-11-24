# Licenças dos assets de terceiros (conferidas em 22/11/2026, Diretor 2)

Regra: só entra aqui asset com licença CC0 (domínio público) conferida NA PÁGINA DE ORIGEM e, quando o pacote traz, no arquivo de licença dentro dele. CC0 permite uso comercial, modificação e redistribuição, sem crédito obrigatório. Nada CC-BY, CC-BY-SA ou "só uso pessoal" entra sem decisão do Diretor registrada aqui.

## Modelos 3D (assets/modelos/)

| Pasta | O que é | Autor | Origem | Licença |
|---|---|---|---|---|
| quaternius_dinos_2018/ | T. rex, Velociraptor, Triceratops, Stegosaurus, Parasaurolophus, Apatosaurus, low poly, com armature e animações (Idle, Walk, Run, Attack, Jump, Death) | Quaternius | https://quaternius.itch.io/animated-lowpoly-dinosaurs ("Dinosaur Animated Pack - Dec 2018.zip") | CC0 1.0: na página do itch ("CC0 license") e no License.txt do pacote |
| galinha_kelgar/ | Galinha com armature e 13 animações (ciscar, andar, comer...) | Čestmír Dammer (cdmir), projeto Kelgar | https://opengameart.org/content/chicken-animated | CC0 1.0: na página e no license.txt do pacote |
| maos_arms_lowpoly/ | Braços e mãos low poly com rig Rigify (dedos com FK), FBX + .blend + textura; usados com subdivisão e pose de pinça no ep004 v2 | DevMops | https://opengameart.org/content/low-poly-arms-rigged ("arms_low_poly_rigged.zip") | CC0 1.0: na página (conferida em 23/11/2026); cópia em maos_arms_lowpoly/LICENCA.txt |

ATENÇÃO: o site quaternius.com passou a usar a "Quaternius Asset License (QAL) v1.0" em 28/08/2026 para os downloads atuais, que proíbe redistribuir os assets. NÃO baixe Quaternius pelo site nem pelo Drive dele para pôr neste repositório (é público). O pacote de 2018 acima veio do itch.io, publicado como CC0 (licença irrevogável), com o License.txt original guardado na pasta.

Ferramentas de download: /home/claude/tools não fica no repo; o caminho que funcionou foi o itch.io (POST /file/<upload_id>?source=view_game&as_props=1 com o csrf_token da página). O Drive da Quaternius dá "Quota exceeded".

## Efeitos sonoros (assets/sfx/) e trilhas (assets/musica/)

Todos de https://opengameart.org, baixados só quando a página dizia CC0 1.0 (o script recusou automaticamente as páginas CC-BY e CC-BY-SA). A lista com a URL de cada arquivo e o autor está em sfx/proveniencia.tsv e musica/proveniencia.tsv.

| Pasta | Conteúdo | Autor (usuário no OGA) |
|---|---|---|
| sfx/t-rex-calls | chamados de T. rex | caveboytup |
| sfx/cc0-deep-monster-roar | rugido grave | trazzz123 |
| sfx/80-cc0-creature-sfx | 80 sons de criaturas | rubberduck |
| sfx/75-cc0-breaking-falling-hit-sfx | quebras, quedas, impactos | rubberduck |
| sfx/100-cc0-sfx-2 | 100 sons variados (ar, portas, passos, vidro, impactos, ambientes) | rubberduck |
| sfx/deep-bone-crackbreak-sfx | estalo e quebra de osso | zane-little-music |
| sfx/air-whoosh | whoosh | pyranostudios |
| sfx/fire-crackling | fogo crepitando | antumdeluge |
| sfx/rain-long-thunder | chuva com trovão | wuxiascrub |
| sfx/heartbeat-sounds | batimento lento e rápido | bart |
| sfx/3-pop-sounds, sfx/pop-sounds, sfx/pop-effect-sounds, sfx/a-slide-pop-sound | estouros (pop) para a Pipo | wubitog, cogitollc, trezegames, ezduzziteh |
| musica/adventure-intro-title-cinematic-epic | abertura épica | nene |
| musica/cinematic-percussion-loop | percussão cinematográfica em loop | marwan-antonios |
| musica/cc0-mystery | mistério / exploração | polygondan |
| musica/a-mystery-travel | mistério leve | cybersoft |

## Sons de meme (assets/sfx/memes/), 24/11/2026

Pedido do dono: o efeito dos memes sonoros virais sem usar o original (Bob Esponja = Paramount/Nickelodeon, Content ID). Buscados na API do Openverse (filtro `license=cc0,pdm`), todos vindos do Freesound; a licença foi conferida de novo NA PÁGINA do Freesound de cada som (CC0 1.0). Baixado o preview HQ (mp3) que o Openverse indica; cortado, com fade e volume igualado (cerca de -14 LUFS momentâneo, pico -3 dBFS), mono 48 kHz ogg. Apelido, autor, página, arquivo baixado e recorte de cada um em sfx/memes/proveniencia.tsv.

| Apelido | Som de origem (Freesound) | Autor |
|---|---|---|
| boom | "Boom 1" + sub-grave de "Sine Bass Drop" | greenvwbeetle + josheb_policarpio |
| disco | "Record Scratch #2" | musicvision31 |
| violino_triste | "Hearts and Flowers.wav" | andyssoundbox |
| badumtss | "Sting, rimshot, drum roll (smooth)" | tlwmdbt |
| palhaco | "Clown Horn (Single Honk).wav" | Gimp_Revival |
| riser | "Riser" | Rizzard |
| dundun | "Dun Dun Duuun v.01.mp3" | divenorth |
| ohh | "Crowd Oooh.wav" | deleted_user_2104797 |
| risada | "Crowd laugh.wav" | deleted_user_2104797 |
| grilo | "Cricket - Grillo" | Lunevix |
| certo | "Quiz Gameshow Correct Ding 01.mp3" | craigscottuk |
| errado | "Wrong Answer" | -Andreas |
| dinheiro | "cash register chching" | disman |
| glitch | "Glitch Corruption" | dotY21 |
| gongo | "Gong" | qubodup |
| apito_sobe, apito_desce | "SLIDE WHISTLE - 1" (subida e descida recortadas) | SamuelGremaud |
| boing | "Funny Boing" | se2001 |
| fa, fa2 | GERADO POR NÓS: edge-tts (pt-BR-AntonioNeural / pt-BR-FranciscaNeural) dizendo "FÁÁÁÁÁÁ!" + saturação, queda de tom, eco, reverb e corte seco (kit/gera_fa.py). Não usa o áudio do streamer. | PipoPop |

Recusados na conferência da página (o Openverse dizia CC0, a página não): "Boing Spring Mouth harp downward 1" (pan14, está CC-BY 4.0) e "Cash register" (MaoDin204, página sem licença CC0 legível). Sempre confira a página: o índice do Openverse pode estar velho.

Páginas recusadas por não serem CC0 (não usar sem crédito): bubble-pop, cork, cracking-sounds, long-deep-impact, big-low-frequency-explosion-boom, robot-scanning-area, breeze, 6-monstrous-growls, cinematic-ending-music, cinematic-intro-soundtrack, cinematic-strings-trailer, cinematic-trailer-music, mystery, high-tension, distant-horizon.
