import json
pt=[
("Você comeu um desses no almoço.",0.3,"0s T. rex em close baixo rugindo para a lente, boca aberta, cinzas caindo, contraluz laranja de incêndio | SFX: rugido grave + vento"),
("Ele morreu com o asteroide, sessenta e seis milhões de anos atrás.",0.3,"T. rex recua, câmera abre: planície queimando, céu escuro, rastro do asteroide cruzando o céu ao fundo | SFX: estrondo distante, riser baixo"),
("Mas nem todo dinossauro morreu.",0.5,"close no olho do T. rex, a íris fecha | SFX: silêncio da trilha (pausa antes do estouro)"),
("Um inscrito chutou: a galinha. E acertou.",0.3,"MATCH-CUT: galinha no mesmo enquadramento e pose do T. rex; placa 3D com o comentário '@Niko_com_k: A galinha eu acho' | SFX: pop + cocoricó curto"),
("E galinha come milho.",1.2,"[PIPO_FOGE] ~3 s: a galinha vira a cabeça e vê a Pipo (espiga de milho) no quintal; a Pipo congela, cara de tédio com a sobrancelha levantada, e sai correndo; a galinha vai atrás | SFX: boing (virada), silêncio de 0,3 s (congela), whoosh + passinhos rápidos"),
("Ave não é parente de dinossauro. Ave é dinossauro.",0.3,"T. rex e galinha lado a lado, mesma pose, câmera gira em volta | SFX: whoosh"),
("Imagine abrir o peito de um T. rex: lá dentro tem o mesmo ossinho da sorte do frango.",0.3,"raio-x: câmera atravessa o peito do T. rex, a fúrcula em V acende; corte para a fúrcula da galinha no mesmo lugar | SFX: click + ding"),
("Até a proteína do osso dele parece com a da galinha.",0.3,"fêmur fossilizado de T. rex na mesa; fibras de proteína brilham e se alinham ao lado de um osso de galinha | SFX: thump"),
("Depois do impacto, sem sol, as florestas morrem.",0.3,"sol some atrás da poeira (céu da parte 1), floresta escurece e as copas começam a tombar | SFX: vento, trilha séria baixa"),
("Sobra quem cisca o chão e quebra semente.",0.3,"últimas copas tombam; corte para ave pequena no chão de cinzas bicando sementes | SFX: madeira rachando + bicadas"),
("Na Bélgica, acharam uma ave de pouco antes do impacto: meio galinha, meio pato.",0.3,"globo da parte 1 gira até a Bélgica; fóssil de crânio pequeno vira ave viva em giro | pill: WONDERCHICKEN, 66,7 MI DE ANOS | SFX: whoosh + ding"),
("Hoje são vinte e sete bilhões de galinhas. Mais de três por pessoa.",0.3,"câmera sobe de um quintal com galinhas e abre para fileiras infinitas até o horizonte | SFX: riser"),
("O dinossauro não sumiu. Virou almoço.",0.5,"volta ao prato: coxa de frango na mesa, sombra de T. rex projetada na parede | SFX: estouro/vinheta"),
("T. rex: penas ou escamas? Comenta.",0.3,"T. rex em silhueta, metade com penas, metade com escamas, câmera parada; frase sozinha na tela; ao fundo, pequena e fora de foco, a perseguição galinha x Pipo continua em loop vivo | SFX: trilha corta, passinhos baixos ao fundo"),
]
en=[
"You had one of these for lunch.",
"It died with the asteroid, sixty-six million years ago.",
"But not every dinosaur did.",
"One subscriber guessed: the chicken. And nailed it.",
"And chickens eat corn.",
"Birds aren't related to dinosaurs. Birds are dinosaurs.",
"Imagine opening a T. rex's chest: inside is the same wishbone as a chicken's.",
"Even the protein in its bones looks like a chicken's.",
"After the impact, with no sun, the forests die.",
"What's left pecks the ground and cracks seeds.",
"In Belgium, they found a bird from just before the impact: part chicken, part duck.",
"Today there are twenty-seven billion chickens. More than three per person.",
"The dinosaur never vanished. It became lunch.",
"T. rex: feathers or scales? Comment.",
]
json.dump(dict(voice="pt-BR-AntonioNeural",rate="+4%",pitch="+0Hz",lead=0.0,lines=[dict(text=t,pause=p,shot=s) for t,p,s in pt]),open("roteiro.json","w"),ensure_ascii=False,indent=1)
json.dump(dict(voice="en-US-BrianNeural",rate="+4%",pitch="+0Hz",lead=0.0,align_to_pt=True,lines=[dict(text=e,pause=pt[i][1],shot=pt[i][2]) for i,e in enumerate(en)]),open("roteiro_en.json","w"),ensure_ascii=False,indent=1)
