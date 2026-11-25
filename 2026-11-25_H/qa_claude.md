# QA-Claude ep010 (H, 25/11/2026 21h17)
VEREDITO: CORRIGE (1 ponto de continuidade). Nenhum outro achado.

1. Piso §3: qa_check aprovado (-14,6 LUFS, sem alertas); fatos.md com 2 fontes; quadro 1 com conflito sem som ("SÓ A DELA APAGOU", contador 1→0); 2 gatilhos de interação naturais e específicos (L17 e L18); nada da §1 violado.
2. Fatos: Smithsonian e History.com conferidos na web hoje. Os dois dizem 1882, Nova York, 80 lâmpadas. "De que se tem notícia" não exagera (a LoC diz "may have been the first"). Sem nome de pessoa na fala.
3. Ficção declarada em 13 s ("Agora imagina um mundo com uma regra:") e também na descrição.
4. Contador certo do começo ao fim: 1 (0 s), 0 (2,5 s), 31 (19,5 s), 30 (26 s), 29 (30,5 s), 28...1 (31-34 s), 1 (35-42 s), 0 (42,5 s), 31 (50,5 s). As luzes da casa batem com ele (1 lâmpada vermelha no canto em 35 s e 42 s; escuro em 43-49 s). A contagem 0→31 dentro do flash (50,4-50,7 s) é rápida e vale como "de uma vez".
5. ERRO DE CONTINUIDADE, 52,0-53,4 s: a casa da Ana aparece de parede e telhado rosa. No resto do vídeo ela é lilás com telhado azul (20 s, 25 s, 30 s, 35 s, 50,5 s). Correção: redesenhar a casa dessa cena com parede lilás/branca e telhado azul. Pode manter a luz quente e as 31 lâmpadas acesas.
6. Estouro da Pipo: o milho estoura em 50,3 s, no "acenderam" (que começa em 50,2 s), com flash e a pipoca entrando em 50,5 s. OK.
7. Ritmo: freezedetect não achou nenhum trecho parado de 2 s ou mais. As cenas mais longas têm cerca de 2,5 s. O vídeo termina na chamada "Ou liga agora" (62 s).
8. Religião, política e futebol: nada. O Natal aparece como data cultural (ceia, presentes, pisca-pisca), sem presépio, anjo, igreja ou reza. As estrelas no topo das árvores (8-12 s, 32-34 s, 52-55 s) são genéricas e eu aceito. Vermelho, branco e azul só nas luzes de 1882, conforme a fonte, sem bandeira.
9. Detalhe sem bloqueio: o texto na tela em 58,5-60,5 s diz "você deve uma ligação" e a fala diz "você tá devendo uma ligação". Não precisa mexer.
10. Fotos: o vídeo não usa nenhuma, então não há proveniência a conferir.

## Rodada de correção (Diretor, 25/11)
Casa da Ana na C26 (52 a 53,4 s) corrigida pelo O2 (parede #A6B5EC, telhado #2439A0, igual às outras cenas). Re-render pelo O4: qa_check APROVADO, -14,5 LUFS, 62,0 s, upload 3,61 MB. Conferido pelo Diretor em quadros de 20,5 e 52,5 s. Gemini 7,4, sem erro grave; a legenda "truncada" aos 6 s é falso positivo ("de que se" sai num bloco próprio). Liberado para a fila.
