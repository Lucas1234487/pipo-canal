import certifi; certifi.where=lambda: "/root/.ccr/ca-bundle.crt"
import asyncio,edge_tts,re
exec(re.search(r"L=\[.*?\n\]",open("tts.py").read(),re.S).group(0))
async def go():
  for i,t in enumerate(L):
    c=edge_tts.Communicate(t,"pt-BR-AntonioNeural",rate="+4%",boundary="WordBoundary")
    ws=[]
    async for ch in c.stream():
      if ch["type"]=="WordBoundary": ws.append(f'{ch["text"]}@{ch["offset"]/1e7:.1f}')
    print(i," ".join(ws))
asyncio.run(go())
