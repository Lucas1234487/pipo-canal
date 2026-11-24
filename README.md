# PipoPop

**Comece aqui:** este canal é comandado pelo Diretor. Leia `docs/diretor/BRIEFING_DIRETOR.md` e siga a ordem de leitura de `docs/diretor/APOSENTADORIA.md`. Depois leia `docs/diretor/RESGATE_PESQUISA.md` (o que a pesquisa inicial mandou e o canal esqueceu).
Memória: `docs/BASE_CONHECIMENTO.md` (longo prazo), `docs/diretor/handovers/` (diário de cada mandato, em ordem), `docs/diretor/PLACAR.md` (números).
Referência do que funcionou: `referencias/dinossauros/`.

---

# Pipo - kit de produção do canal

Canal de vídeos curtos 3D (YouTube Shorts + Instagram Reels), PT e EN, foco Brasil.
Mascote: Pipo, espiguinha de milho que estoura e vira uma menininha de pipoca premium com maria-chiquinha.

## Pastas
- `kit/` código de produção (Blender via `bpy`, edge-tts, ffmpeg)
- `docs/biblia_do_canal.md` regras do canal (roteiro, proibições, vozes, horários, SEO)
- `docs/pauta_14_dias.md`, `docs/decisoes_pendentes.md`
- `docs/pesquisa/` os 15 relatórios + revisões das personas

## Fluxo de um episódio
```bash
bash kit/setup.sh                                   # 1x por sessão
WORK=/home/claude/ep1; mkdir -p $WORK
# 1) escrever $WORK/roteiro.json (e roteiro_en.json) -> ver docstring de kit/tts.py
python3 kit/tts.py $WORK ; python3 kit/tts.py $WORK en
# 2) copiar kit/ep_exemplo_blackfriday.py para $WORK/ep.py e reescrever a parte do episódio
PIPO_KIT=$PWD/kit PIPO_WORK=$WORK python3 $WORK/ep.py 1,300,600   # prévia (olhar $WORK/prev/*.png)
PIPO_KIT=$PWD/kit PIPO_WORK=$WORK python3 $WORK/ep.py full        # render (~3-4 s/quadro em 540x960)
# 2b) revisão da cena antes do render (segundos): ver $WORK/qa_scene.json
PIPO_KIT=$PWD/kit PIPO_WORK=$WORK python3 $WORK/ep.py qa
# 3) montar
python3 kit/compose.py $WORK        # -> $WORK/final_pt.mp4
python3 kit/compose.py $WORK en     # -> $WORK/final_en.mp4 (usa timing_en.json e pills_en)
# 4) revisão final (legenda sobreposta, objetos sobrepostos, zona segura, áudio) + folha de contato
python3 kit/qa_check.py $WORK pt ; python3 kit/qa_check.py $WORK en
```

## Funções principais (pipo_lib.py)
`wt(palavra, n)` tempo de uma palavra da narração · `pipo_place` · `pipo_start_kernel` · `pipo_idle` · `pipo_hop` ·
`pipo_tension` · `pipo_pop` (o estouro, com partículas) · `pipo_unpop` (loop) · `set_face(F, quadro, lid, brow, browL, look)` ·
`blink` · `SIGN` (cara de tédio + sobrancelha levantada) · `FK` rosto da espiga · `FP` rosto da menininha ·
`qa_key` / `qa_touch` (revisão) · `lit()` material 3D · `flat()` emissivo · `text3d` · `confetti` · `finish(shots, events, shake_at)`.
