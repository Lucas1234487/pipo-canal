"""Prepara um video pronto para a Plateia 'assistir' como uma pessoa no feed.
Uso: python3 plateia_kit.py WORK [pt|en] [fps]
Gera em WORK/plateia_<lang>/:
  folha_NN.jpg   grade 4x3 de quadros a cada 1/fps s (padrao 2 por segundo), com o tempo em cada quadro
  roteiro_tempo.txt  o que se ouve, frase por frase, com tempo de inicio e fim
  energia.txt    volume do audio por segundo (barra) e marcas de silencio
  resumo.txt     duracao, numero de folhas e instrucao de leitura
A Plateia deve ler as folhas na ordem, junto com roteiro_tempo.txt, e decidir segundo a segundo se continua ou desliza."""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WORK = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 else "pt"
fps = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
MP4 = f"{WORK}/final_{lang}.mp4"
OUT = f"{WORK}/plateia_{lang}"
os.makedirs(OUT, exist_ok=True)
KIT = os.path.dirname(os.path.abspath(__file__))

dur = float(subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", MP4],
                           capture_output=True, text=True).stdout.strip())

# quadros
tmp = f"{OUT}/_q"
os.makedirs(tmp, exist_ok=True)
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", MP4, "-vf", f"fps={fps},scale=270:480", f"{tmp}/q%04d.jpg"], check=True)
qs = sorted(os.listdir(tmp))
try:
    font = ImageFont.truetype(f"{KIT}/Fredoka-700.ttf", 26)
except Exception:
    font = ImageFont.load_default()
COLS, ROWS = 4, 3
per = COLS * ROWS
nfol = 0
for s in range(0, len(qs), per):
    sheet = Image.new("RGB", (COLS * 270, ROWS * 480), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    for k, q in enumerate(qs[s:s + per]):
        im = Image.open(f"{tmp}/{q}")
        x, y = (k % COLS) * 270, (k // COLS) * 480
        sheet.paste(im, (x, y))
        t = (s + k) / fps
        d.rectangle([x, y, x + 92, y + 34], fill=(0, 0, 0))
        d.text((x + 6, y + 3), f"{t:5.1f}s", fill=(255, 230, 0), font=font)
    nfol += 1
    sheet.save(f"{OUT}/folha_{nfol:02d}.jpg", quality=85)

# fala com tempo
tj = f"{WORK}/timing{'_en' if lang == 'en' else ''}.json"
linhas = []
if os.path.exists(tj):
    T = json.load(open(tj))
    for L in T["lines"]:
        linhas.append(f"[{L['start']:5.1f}s - {L['start'] + L['dur']:5.1f}s] {L['text']}")
ev = f"{WORK}/events.json"
if os.path.exists(ev):
    E = json.load(open(ev))
    for sf in E.get("sfx", []):
        try:
            linhas.append(f"[{float(sf[1]) / 30 if float(sf[1]) > 200 else float(sf[1]):5.1f}s] (efeito: {sf[0]})")
        except Exception:
            pass
open(f"{OUT}/roteiro_tempo.txt", "w").write("\n".join(sorted(linhas)) + "\n")

# energia do audio
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", MP4, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                     capture_output=True).stdout
a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
out = []
for sec in range(int(np.ceil(dur))):
    seg = a[sec * 8000:(sec + 1) * 8000]
    rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0
    db = 20 * np.log10(rms + 1e-9)
    bar = "#" * max(0, int((db + 50) / 2))
    out.append(f"{sec:3d}s {db:6.1f} dB {bar}{'  <- quase silencio' if db < -40 else ''}")
open(f"{OUT}/energia.txt", "w").write("\n".join(out) + "\n")

open(f"{OUT}/resumo.txt", "w").write(
    f"Video: {MP4}\nDuracao: {dur:.1f} s\nFolhas: {nfol} (cada uma = {per / fps:.0f} s, {fps:g} quadros por segundo, tempo no canto)\n"
    "Leia folha_01.jpg, folha_02.jpg ... em ordem, junto com roteiro_tempo.txt (o que se ouve) e energia.txt (volume).\n")
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
os.rmdir(tmp)
print(f"ok: {OUT} ({nfol} folhas, {dur:.1f} s)")
