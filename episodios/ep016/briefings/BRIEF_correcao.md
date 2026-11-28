# Correção pós-QA (rodada ÚNICA) — ep016. Achados em WORK/qa_claude.md (o Diretor já corrigiu meta.json e fatos.md: não mexa neles)
1. Quadro 1 (0-3,2 s): POEIRA VISÍVEL: camada cinza de pó (pontinhos/manchas) sobre o móvel e o piso, crescendo com o relógio girando; tire o retângulo marrom liso e a barra solta perto da porta. Texto do topo fica.
2. Estouro em "fora" (11,75 s): o pop/boom tem que aparecer sobre a voz no celular: antecipe o pop ~0,12 s (no silêncio antes da palavra) e/ou abaixe a voz 3 dB naquele trecho; confira com passa-alta 300 Hz (mix > voz sozinha).
3. 33,3-33,8 s: suba a Pipo ~120 px para a legenda "FICA NA PORTA?" não cobrir a base dela (nada da Pipo entre y 0,60 e 0,72).
4. 6,2-6,7 s: carimbo "MITO" deslocado para não borrar "PELE MORTA" (ambos legíveis); suba a Pipo espiga ~60 px para ela não ficar atrás do cartão.
5. 18,2-21,2 s: etiquetas FIAPO e TAPETE em branco com contorno escuro.
Não mude falas nem timing. Render -> compose -> qa_check APROVADO -> upload.mp4. Extraia de novo q_0.5, q_6.5, q_11.75 e q_33.5 em WORK/qa_quadros/ e olhe. Apague frames no fim. Retorno em até 5 linhas.
