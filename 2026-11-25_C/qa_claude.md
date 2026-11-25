# QA-Claude, piloto_C (pilar C, "Dá pra ver o Natal do espaço"), 24/11/2026
VEREDITO: APROVA

1. Piso §3: qa_check APROVADO (-14,6 LUFS, nenhum quadro preto). fatos.md tem 2+ fontes por fato. Nada da §1 violado. Quadro 1 já mostra a pergunta "DÁ PRA VER O NATAL DAQUI?". Interação específica nas linhas 11 e 12 (você ou o vizinho, manda pro vizinho da árvore).
2. Fatos: abri as 4 fontes (NASA Goddard, Earth Observatory, phys.org, SVS). Batem 70 cidades, 20 a 50%, centro 20 a 30%, subúrbios 30 a 50%, início na Black Friday e "yard space". A fala não exagera ("até trinta", "até cinquenta", "de vinte a cinquenta").
3. Continuidade: 70 / +20% a +50% / +30% / +50% iguais na fala, na tela e na descrição. Depois do estouro (23,4 s) a Pipo segue pipoca até o fim, sem voltar a ser milho.
4. Técnica: legenda legível; o maior plano tem 4,2 s (7,8 a 11,9 s), mas o contador 54→70 e o satélite se mexem, então nada fica parado. Termina na chamada.
   Áudio com passa-alta de 300 Hz: boom em 33,9 s fica +5 dB acima da voz sozinha. Estouro em 23,44 s: +6 dB no whoosh (23,39 s), só +1 dB no ataque (fica embaixo de "bairros") e +3 a +11 dB na cauda (23,54 a 23,74 s). Aparece no celular, mas sem passar da voz.
5. Transição de papel em 36,1 a 36,3 s: rasgo de uns 5 quadros, não um corte seco de 1 quadro. "EXAGERADO" estava na tela desde 33,9 s e é rasgado junto com a cena, o que é o efeito esperado. Não é defeito.
6. Título honesto: a manchete da NASA é "Satellite Sees Holiday Lights Brighten Cities". A fala já diz "Nos Estados Unidos" aos 8 s e a descrição também. Só o título não diz que é nos EUA, o que está ok para um título.
7. Fotos: foto1 = iss070e062746, NASA, domínio público, registrada em proveniencia.tsv; crédito na tela e na descrição.
8. Conteúdo: o gancho prende (foto real com pergunta); a virada centro x bairros e o vizinho exagerado dão vontade de compartilhar.
Sugestões que não travam: (a) O3 sobe pop2/hit_03 em 23,44 s de +3 a +4 dB para o estouro passar da voz; (b) o último 0,8 s (42,1 a 42,9 s) fica em silêncio.
Pendente fora do QA-Claude: avaliacao_gemini.md está vazio, então o QA-Gemini ainda precisa rodar antes de agendar.
