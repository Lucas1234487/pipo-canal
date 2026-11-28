# Correção de duração (Diretor, antes do QA) — ep015
80,9 s é longo demais para H (45-65 s). O Diretor já editou WORK/roteiro.json: saíram 4 falas ("Os dois olhos miram...", "Comendo de cabeça baixa...", "Deixa o like...", "Com essa regra, comedor de planta..."), a linha 2 e a do bico-de-pato real mudaram de texto (a do bico-de-pato agora junta o leque largo), rate +10%.
Faça: tts.py de novo -> ajuste o cenas.json/gen_cenas.py ao timing novo (as cenas das falas cortadas saem: cones cruzando no alvo do T. rex, like, contador; o leque largo do bico-de-pato real fica na cena da fala que sobrou) -> render -> compose -> qa_check APROVADO -> upload.mp4 -> meta.json (duracao, interacao do roteiro.json; tire "contador" se citado).
Aproveite: silêncio antes do "Rugido" em 0,35-0,45 s; o quadro quase vazio no corte da penúltima fala (botões entram junto do corte); grilo pode ter 0,7 s se couber.
Meta: 58-66 s. Se passar de 66 s, diga quanto. Apague frames. Retorno em até 6 linhas.
