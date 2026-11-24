# O1 Roteiro e Fala (organizador, contratado pelo Gerente de Produção)
Antes: leia docs/diretor/cadernos/O1.md, specs/G2_roteiro.md (formatos, HISTÓRIA, voz), 02_GUARDRAILS.md e a pauta do gerente.
Entrega em WORK/: roteiro.json, fatos.md, timing.json (rode `python3 kit/tts.py WORK`).
- Gancho na 1ª frase (resultado chocante, número ou conflito). Virada no meio. Fim: lição curta (só história) + pergunta + chamada (mandar para alguém, quando couber).
- Fatos com 2 fontes em fatos.md (Gemini com --busca ajuda; você confere).
- Voz: pt-BR-FranciscaNeural ou pt-BR-AntonioNeural. Nada de sigla, palavra estrangeira ou número em algarismo na fala.
- Teste a pronúncia: `python3 kit/gemini.py video --arquivo WORK/narracao.(mp3|wav)` não existe; em vez disso gere a narração e rode o Gemini no MP4 final pelo QA. Aqui, reescreva palavras de risco antes.
- Marque no roteiro (campo "shot") o que a cena mostra e onde cabe foto real (O2 decide).
Bilhete em WORK/bilhetes/O1.md. 1 lição no caderno.
