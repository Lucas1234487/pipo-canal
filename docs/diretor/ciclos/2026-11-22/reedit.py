"""Reedição sem render: corta faixas de quadros do ep003 e remapeia narração e eventos."""
import json, os, shutil, copy
SRC, DST = "/home/claude/ep003", "/home/claude/ep003b"
FPS = 30
CUTS = [(545, 565), (899, 1438)]             # quadros removidos (inclusive)
DROP_LINES = {7, 8, 9, 10}
N0 = json.load(open(f"{SRC}/events.json"))["N"]
keep = [f for f in range(1, N0 + 1) if not any(a <= f <= b for a, b in CUTS)]
cuts_t = [((a - 1) / FPS, b / FPS) for a, b in CUTS]
def nt(t):
    sh = 0
    for t0, t1 in cuts_t:
        if t >= t1: sh += t1 - t0
        elif t > t0: return None
    return t - sh
def nf(f):
    if any(a <= f <= b for a, b in CUTS): return None
    return f - sum(b - a + 1 for a, b in CUTS if b < f)
# quadros
os.makedirs(f"{DST}/frames", exist_ok=True)
for i, f in enumerate(keep, 1):
    d = f"{DST}/frames/f{i:04d}.png"
    if os.path.exists(d): os.remove(d)
    os.link(f"{SRC}/frames/f{f:04d}.png", d)
# narração
for suf, ad in (("", "aud"), ("_en", "aud_en")):
    T = json.load(open(f"{SRC}/timing{suf}.json"))
    os.makedirs(f"{DST}/{ad}", exist_ok=True)
    out = []
    for l in T["lines"]:
        if l["i"] in DROP_LINES: continue
        s = nt(l["start"]); assert s is not None, l["i"]
        sh = l["start"] - s
        l = copy.deepcopy(l); l["start"] = s
        l["words"] = [[w, a - sh, d] for w, a, d in l["words"]]
        out.append(l); shutil.copy(f"{T['aud']}/l{l['i']}.wav", f"{DST}/{ad}/l{l['i']}.wav")
    json.dump(dict(lines=out, total=len(keep) / FPS, aud=f"{DST}/{ad}"), open(f"{DST}/timing{suf}.json", "w"), ensure_ascii=False, indent=1)
# eventos
E = json.load(open(f"{SRC}/events.json")); E["N"] = len(keep)
for k in ("shots", "cortes"):
    E[k] = sorted({x for x in (nf(f) for f in E[k]) if x})
E["f_pop"] = nf(E["f_pop"]) or E["f_pop"]
E["sfx"] = [[p if p.startswith("../") is False else p, nt(t), v] for p, t, v in E["sfx"] if nt(t) is not None]
for k in ("pills", "pills_en"):
    E[k] = [[nt(a), nt(b)] + r for a, b, *r in E[k] if nt(a) is not None and nt(b) is not None]
E["music_gaps"] = [[nt(a), nt(b) if nt(b) is not None else nt(a) + 0.5] for a, b in E["music_gaps"] if nt(a) is not None]
E["music_gaps"][-1][1] = len(keep) / FPS + 2
E["music_gap"] = E["music_gaps"][0]
E["silencios"] = [dict(s, t0=nt(s["t0"]), t1=nt(s["t1"])) for s in E["silencios"] if nt(s["t0"]) is not None]
json.dump(E, open(f"{DST}/events.json", "w"), ensure_ascii=False, indent=1)
print("quadros", len(keep), "s", len(keep) / FPS)
