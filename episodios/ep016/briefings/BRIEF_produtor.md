# Brief do PRODUTOR — ep016 (C, conhecimento: de onde vem a poeira da casa) — vai ao ar SÁB 28/11/2026 21h13

Você é o produtor único (O2 cenário + O3 som + O4 montagem). Sozinho, sem subagentes. Rode tudo de /home/claude/pipo-canal.
WORK = /home/claude/2026-11-28_C (roteiro.json APROVADO pelo Diretor + fatos.md; não mude as falas).
PRAZO DURO: upload.mp4 + meta.json + qa_check APROVADO até 18h30 (Brasília: `TZ=America/Sao_Paulo date`). Constância > perfeição. Ambiente: se faltar edge-tts ou pycairo, `pip install --break-system-packages edge-tts pycairo`.

## Leia (só isto)
docs/sistema/specs/O2_cenario.md, O3_sonoplastia.md, O4_montagem.md; docs/diretor/cadernos/O2.md, O3.md, O4.md (últimas lições); kit2d/CENAS.md. Referência de C recente (para NÃO repetir): episodios/ep014/cenas.json (panetone: abriu em mostarda, sala_natal, estouro em luzes).

## Passos
1. `python3 kit/tts.py WORK` -> timing.json (esperado 32-40 s; se passar de 42 s, avise).
2. cenas.json seguindo as "shot" do roteiro.json. Obrigatórios:
   - QUADRO 1 legível sem som: sala/casa, a mãe (elenco humano) com vassoura, móvel com camada de poeira voltando; texto no topo (y >= 0,145, entra até 0,3 s) "VARREU ONTEM. VOLTOU HOJE." O guardrails agora REPROVA se o 1º texto (3+ palavras) não entrar até 0,3 s.
   - Pipo aparece cedo (espiga), nunca parada enquanto a voz fala; ESTOURA em "fora" (linha 4) com flash e pop; depois "forma": "pipoca", sempre inteira dentro do quadro (x entre 0,15 e 0,85).
   - Carimbo "MITO" sobre "PELE MORTA" entra já grande (pop curto).
   - "Um estudo nos Estados Unidos calculou": prancheta/casa em corte com setas; sem bandeira, sem marca.
   - Sola de sapato com pegadas de terra; janela com cortina e partículas; liquidificador/mistura com a terra maior que o resto.
   - 1 reação de meme na linha 8 (vassoura que não vence), no máximo 2 no vídeo.
   - Fim: "ENTRA ou FICA NA PORTA?" com 2 botões e a Pipo pipoca; acaba logo depois da fala.
   - VARIEDADE vs ep014: paleta de abertura diferente de mostarda, estouro NÃO em luzes/raios_hq, música de abertura diferente de "a-mystery-travel".
   - Corte a cada 2-3 s, troca de paleta, fundo com vida, nada parado > 3 s, nada na faixa da legenda (y 0,60-0,72), textos curtos em PT.
3. Som (O3): som em toda entrada, estouro audível no celular, silêncio 0,3-0,4 s antes de "fora", voz 18-24 dB acima da música. Só CC0 de assets/.
4. `python3 kit2d/render2d.py WORK` -> `python3 kit/compose.py WORK` -> `python3 kit/qa_check.py WORK pt` até APROVADO. Extraia em resolução cheia os quadros 0,5 s, o do estouro e o último segundo em WORK/qa_quadros/ e olhe com os seus olhos (texto cortado, sobreposição, Pipo na borda).
5. WORK/upload.mp4 (720p, até 3,8 MB) e WORK/meta.json completo no formato de fila/2026-11-28_H/meta.json:
   - titulo (<= 50): "De onde vem a poeira que volta todo dia? 🧹"
   - descricao 2-4 frases: estudo de David Layton e Paloma Beamer (Environmental Science & Technology, 2009) estimou que mais de 60% da poeira de casa vem de fora (terra trazida e partículas sopradas); o resto é pele, fibras de roupa e tapete; dica da porta; + hashtags.
   - hashtags, comentario_fixado, interacao, humor, aposta ("seguro"): do roteiro.json. horario_sugerido "2026-11-28 21:13". tema "de onde vem a poeira de casa", emocao "identificação -> 'ahh, é isso'", reconhecivel "mãe varrendo, poeira no móvel, sapato sujo", estilo_animacao, versao_pipo, musica, meme, erro_proposital "nenhum", foto_real, voz, duracao, titulo_en, descricao_en.
6. Apague WORK/frames DEPOIS do último compose. Bilhete curto em WORK/bilhetes/produtor.md e 1 lição datada (até 3 linhas) no fim de docs/diretor/cadernos/O3.md. NÃO faça commit nem push.

## Retorno ao Diretor (até 8 linhas)
Caminho do upload.mp4, duração, tamanho, qa_check, segundo do estouro, caminhos dos quadros extraídos, riscos.
