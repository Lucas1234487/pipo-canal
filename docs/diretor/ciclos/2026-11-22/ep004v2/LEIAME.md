# ep004 v2 (roteiro e voz prontos; cena 3D não feita)

- roteiro.json: 9 frases, Antonio +12%, "trim": true. Abre na ceia ("Esse ossinho que você disputa na ceia... é de dinossauro."), Niko em 1 frase, fato corrigido (galinha é prima do T. rex; fúrcula no alto do peito), termina na pergunta.
- timing.json + aud/*.mp3: narração gravada, 22,3 s. Para regenerar os .wav: `python3 kit/tts.py <WORK>` (o tts.py agora corta o silêncio do fim de cada frase com "trim").
- O agente da cena 3D foi parado a pedido do Lucas (23/11), antes de entregar. A cena v1 está no branch render/ep004.
- Plano de planos (com tempos por palavra) no briefing: frase "shot" de cada linha do roteiro.json.
- Comparativo Claude x Gemini pedido pelo Lucas: https://claude.ai/artifact/HAFoUh55EYpedP8JM9diKA
