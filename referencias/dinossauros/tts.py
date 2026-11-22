import certifi; certifi.where=lambda: "/root/.ccr/ca-bundle.crt"
import asyncio,edge_tts,json,subprocess
L=[
"Sessenta e seis milhões de anos atrás, uma rocha de uns dez quilômetros de largura vinha em direção à Terra, a mais de setenta mil quilômetros por hora.",
"Lá embaixo, os dinossauros dominavam o planeta havia mais de cento e cinquenta milhões de anos. Nenhum deles fazia ideia do que estava por vir.",
"O impacto aconteceu aqui: na península de Iucatã, no México. A cratera, chamada Chicxulub, tem cerca de cento e oitenta quilômetros de diâmetro, e hoje está escondida debaixo da terra e do mar.",
"Em segundos, a explosão liberou mais energia do que bilhões de bombas atômicas. Uma onda de choque varreu a região, e tsunamis gigantes atravessaram o Golfo do México.",
"Mas o pior veio depois. Rochas derretidas foram lançadas para o alto e caíram de volta como uma chuva de fogo, espalhando incêndios. Então, poeira e fuligem cobriram o céu por meses. Sem luz do sol, as plantas morreram. Os herbívoros ficaram sem comida, e os carnívoros, sem presas.",
"No fim, cerca de três quartos de todas as espécies do planeta desapareceram. Inclusive os grandes dinossauros.",
"Mas tem um detalhe que pouca gente sabe: nem todos os dinossauros morreram. Alguns sobreviveram... e você provavelmente viu um deles hoje. Quem são eles? Isso fica pro próximo vídeo.",
]
async def go():
  for i,t in enumerate(L):
    await edge_tts.Communicate(t,"pt-BR-AntonioNeural",rate="+4%").save(f"aud/n{i}.mp3")
asyncio.run(go())
for i in range(len(L)):
  d=subprocess.run(["ffprobe","-v","0","-show_entries","format=duration","-of","csv=p=0",f"aud/n{i}.mp3"],capture_output=True,text=True).stdout.strip()
  print(i,d)
