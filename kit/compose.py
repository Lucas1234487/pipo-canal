"""Monta o MP4 final: quadros 3D (WORK/frames) + legenda karaoke + pilulas de texto + narracao + trilha + efeitos.
Uso: python3 compose.py WORK [lang] [saida.mp4]
Precisa de WORK/timing[_lang].json, WORK/events.json e quadros WORK/frames/fNNNN.png.
Som (22/11/2026): events sfx/music aceitam 'assets/sfx/...' (CC0, ver assets/LICENCAS.md) em qualquer formato,
e recortes [arquivo, inicio_s, dur_s, fade_s]. 'shot_whoosh': arquivo ou null. Os .wav de kit/sfx/ (procedurais) foram reprovados pelo Lucas.
Pilulas por idioma: events["pills"] (PT) e events["pills_en"] (EN), se existir.
"""
import json, subprocess, wave, sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont

KIT = os.path.dirname(os.path.abspath(__file__))
WORK = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] not in ("", "pt") else ""
suf = "_" + lang if lang else ""
OUT = sys.argv[3] if len(sys.argv) > 3 else f"{WORK}/final{suf or '_pt'}.mp4"
OW, OH, FPS = 1080, 1920, 30
T = json.load(open(f"{WORK}/timing{suf}.json"))
E = json.load(open(f"{WORK}/events.json"))
N = E["N"]
FONT = KIT + "/Fredoka-700.ttf"
fcap = ImageFont.truetype(FONT, 84)
DARK = (26, 8, 36)
YEL = (255, 214, 30)
f2t = lambda fr: (fr - 1) / FPS

words = []
for l in T["lines"]:
    toks = l["text"].replace("...", "…").split()
    for i, (w, s, du) in enumerate(l["words"]):
        disp = toks[i] if i < len(toks) and len(toks) == len(l["words"]) else w
        words.append(dict(w=disp, s=s, e=s + du, end_line=(i == len(l["words"]) - 1)))
chunks, cur = [], []
for w in words:
    cur.append(w)
    if len(cur) == 3 or w["w"][-1] in ".,!?:…" or w["end_line"]:
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)
for i, c in enumerate(chunks):
    nxt = chunks[i + 1][0]["s"] if i + 1 < len(chunks) else c[-1]["e"] + 0.4
    c[0]["cs"], c[0]["ce"] = c[0]["s"], min(nxt, c[-1]["e"] + 0.45)


def clean(t):
    t = t.upper()
    return t if t.endswith("…") or t.endswith("?") or t.endswith("!") else t.rstrip(".,:;")


LAYOUT = {}


def draw_caption(img, t, fr=None):
    c = next((ch for ch in chunks if ch[0]["cs"] <= t < ch[0]["ce"]), None)
    if not c:
        return
    d = ImageDraw.Draw(img)
    toks = [clean(w["w"]) for w in c]
    active = max([i for i, w in enumerate(c) if w["s"] <= t] or [0])
    sp = 22
    widths = [d.textlength(x, font=fcap) for x in toks]
    total = sum(widths) + sp * (len(toks) - 1)
    font = fcap
    if total > OW * 0.86:   # encolhe se nao couber na zona segura
        k = OW * 0.86 / total
        font = ImageFont.truetype(FONT, int(84 * k)); widths = [w * k for w in widths]; total *= k; sp *= k
    x = OW / 2 - total / 2
    y = int(OH * 0.64)
    for i, tk in enumerate(toks):
        d.text((x, y), tk, font=font, fill=YEL if i == active else (255, 255, 255), stroke_width=11, stroke_fill=DARK, anchor="lm")
        x += widths[i] + sp
    if fr is not None:
        hh = font.size * 0.75 + 11
        LAYOUT.setdefault(fr, {})["legenda"] = [(OW / 2 - total / 2 - 11) / OW, (y - hh) / OH, (OW / 2 + total / 2 + 11) / OW, (y + hh) / OH]


pills = E.get("pills_" + lang, E.get("pills", [])) if lang else E.get("pills", [])


def draw_pill(img, t, fr=None):
    for a, b, txt, bg, fg in pills:
        if a <= t < b:
            sc = min(1.0, 0.7 + (t - a) * 3)
            fnt = ImageFont.truetype(FONT, int(58 * sc))
            d = ImageDraw.Draw(img)
            w = d.textlength(txt, font=fnt)
            h = int(92 * sc)
            cx, cy = OW // 2, int(OH * 0.155)
            box = (cx - w / 2 - 36 * sc, cy - h / 2, cx + w / 2 + 36 * sc, cy + h / 2)
            d.rounded_rectangle((box[0] + 7, box[1] + 9, box[2] + 7, box[3] + 9), radius=h // 2, fill=DARK)
            d.rounded_rectangle(box, radius=h // 2, fill=tuple(bg), outline=DARK, width=6)
            d.text((cx, cy + 2), txt, font=fnt, fill=tuple(fg), anchor="mm")
            if fr is not None:
                LAYOUT.setdefault(fr, {}).setdefault("pilulas", []).append([box[0] / OW, box[1] / OH, (box[2] + 7) / OW, (box[3] + 9) / OH])


# ---------- audio
SR = 48000
TT = N / FPS
out = np.zeros(int(TT * SR) + SR)


REPO = os.path.dirname(KIT)


SFX = KIT + "/sfx/"


def resolve(name):
    """'assets/...' = relativo ao repositorio; caminho absoluto = como esta; senao = kit/sfx/ (procedural antigo)."""
    if os.path.isabs(name):
        return name
    if name.startswith("assets/"):
        return os.path.join(REPO, name)
    return SFX + name


def rd(p):
    """Le qualquer audio (wav 16/24/32 bit, ogg, mp3, flac) como mono float no SR do projeto, via ffmpeg."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError("audio ilegivel: %s %s" % (p, r.stderr[-200:]))
    return np.frombuffer(r.stdout, np.int16).astype(float) / 32768


def rd_cut(spec):
    """spec = nome | [nome, inicio_s, dur_s, fade_s]: recorta um trecho de um arquivo longo (ex.: rugido dentro de um pacote)."""
    if isinstance(spec, str):
        return rd(resolve(spec))
    name, a, d = spec[0], spec[1], spec[2]
    fd = spec[3] if len(spec) > 3 else 0.05
    x = rd(resolve(name))[int(a * SR):int((a + d) * SR)].copy()
    n = max(1, int(fd * SR))
    if len(x) > 2 * n:
        x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    return x


def add(a, t, g=1.0):
    s = max(0, int(t * SR)); e = min(len(out), s + len(a))
    out[s:e] += a[:e - s] * g


voice = np.zeros_like(out)
for l in T["lines"]:
    a = rd(f"{T['aud']}/l{l['i']}.wav")
    a = a / (np.abs(a).max() + 1e-9) * 0.8
    s = int(l["start"] * SR)
    voice[s:s + len(a)] += a[:len(voice) - s]
mus = rd_cut(E.get("music", "trilha_leve_96bpm.wav"))
if E.get("music_offset"):
    mus = mus[int(E["music_offset"] * SR):]
bed = np.tile(mus, int(np.ceil(len(out) / len(mus))))[:len(out)]
k = int(0.25 * SR)
env = np.convolve(np.abs(voice), np.ones(k) / k, mode="same")
duck = np.convolve(np.where(env > 0.01, 0.10, 0.20), np.ones(k) / k, mode="same")
tt = np.arange(len(out)) / SR
gate = np.ones_like(out)
for a, b in (E.get("music_gaps") or ([E["music_gap"]] if E.get("music_gap") else [])):   # music_gaps: varios silencios (ep003)
    gate[(tt > a) & (tt < b)] = 0.0
    r = (tt >= b) & (tt < b + 0.8); gate[r] = (tt[r] - b) / 0.8
gate = np.convolve(gate, np.ones(480) / 480, mode="same")
out += bed * duck * gate + voice
pop_t = f2t(E["f_pop"]) if E.get("f_pop") else -9
SW = E.get("shot_whoosh", "whoosh.wav")      # null = sem whoosh automatico nos cortes
if SW:
    sw = rd_cut(SW)
    for fr in E["shots"][1:]:
        if abs(f2t(fr) - pop_t) > 0.2:
            add(sw, f2t(fr) - 0.12, E.get("shot_whoosh_gain", 0.25))
for name, t, g in E.get("sfx", []):
    add(rd_cut(name), t, g)
out = out[:int(TT * SR)]
out = out / (np.abs(out).max() + 1e-9) * 0.9
mixp = f"{WORK}/mix{suf}.wav"
w = wave.open(mixp, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()

# ---------- video (blocos em paralelo + concatenacao sem reencode)
J = int(os.environ.get("PIPO_JOBS", str(max(1, os.cpu_count() or 1))))
size = (N + J - 1) // J
ranges = [(1 + i * size, min(N, (i + 1) * size)) for i in range(J) if 1 + i * size <= N]


def encode_chunk(rg):
    a, b = rg
    part = f"{WORK}/part{suf}_{a:04d}.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-threads", "1", part], stdin=subprocess.PIPE)
    lay = {}
    for fr in range(a, b + 1):
        im = Image.open(f"{WORK}/frames/f{fr:04d}.png").convert("RGB").resize((OW, OH), Image.LANCZOS)
        t = f2t(fr)
        LAYOUT.clear()
        draw_pill(im, t, fr)
        draw_caption(im, t, fr)
        lay.update(LAYOUT)
        p.stdin.write(im.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg falhou no bloco %s" % (rg,))
    return part, {str(k): v for k, v in lay.items()}


from multiprocessing import Pool
with Pool(len(ranges)) as pool:
    res = pool.map(encode_chunk, ranges)
layout = {}
lst = f"{WORK}/parts{suf}.txt"
with open(lst, "w") as fh:
    for part, lay in res:
        fh.write(f"file '{os.path.basename(part)}'\n")
        layout.update(lay)
json.dump(layout, open(f"{WORK}/layout{suf or '_pt'}.json", "w"))
vid = f"{WORK}/video{suf}.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vid], check=True)
tmp = OUT + ".tmp.mp4"
r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", mixp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", tmp])
if r.returncode == 0:
    os.replace(tmp, OUT)
    for part, _ in res:
        os.remove(part)
    print("OK", OUT)
else:
    raise SystemExit("ffmpeg falhou na mixagem final")
