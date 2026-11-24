"""Revisao automatica de um episodio. Uso: python3 qa_check.py WORK [pt|en]
Le WORK/qa_scene.json (3D: PIPO_WORK=WORK python3 WORK/ep.py qa; 2D: gravado pelo kit2d/render2d.py junto com os quadros), WORK/layout_<lang>.json (gerado pelo compose)
e o MP4 final. Gera WORK/qa_report_<lang>.md e WORK/qa_sheet_<lang>.jpg (folha de contato para revisao visual).
Sai com codigo 1 se houver reprovacao."""
import json, sys, os, subprocess
from PIL import Image, ImageDraw

WORK = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 else "pt"
MP4 = f"{WORK}/final_{lang}.mp4"
FAIL, WARN = [], []


def inter(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return ix * iy


def runs(items):
    """agrupa ocorrencias por (tipo, alvo) em faixas de quadros"""
    g = {}
    if isinstance(items, dict):  # QA por mundo (ep com varias cenas): {"A": [...], "B": [...]}
        items = [it for v in items.values() for it in v]
    for it in items:
        g.setdefault((it["tipo"], it["alvo"]), []).append(it["frame"])
    out = []
    for (tp, al), frs in g.items():
        frs.sort()
        out.append((tp, al, frs[0], frs[-1], len(frs)))
    return out


# 1) cena 3D
scene = json.load(open(f"{WORK}/qa_scene.json")) if os.path.exists(f"{WORK}/qa_scene.json") else None
if scene is None:
    FAIL.append("qa_scene.json ausente: rode `ep.py qa` (3D) ou `kit2d/render2d.py WORK` (2D) antes")
else:
    for tp, al, a, b, n in runs(scene["issues"]):
        msg = f"{tp}: {al} (quadros {a}-{b}, {n} amostras)"
        if tp in ("objetos_atravessando",) or (tp == "imagens_sobrepostas" and n >= 3) or tp.startswith("texto3d_na_faixa") and n >= 2 \
                or (tp == "texto_na_faixa_legenda" and n >= 2) or (tp == "fora_zona_segura" and n >= 3):   # 2D (kit2d)
            FAIL.append(msg)
        else:
            WARN.append(msg)

# 2) camada 2D (legendas e pilulas)
lay = json.load(open(f"{WORK}/layout_{lang}.json")) if os.path.exists(f"{WORK}/layout_{lang}.json") else {}
if not lay:
    FAIL.append(f"layout_{lang}.json ausente: rode o compose antes")
bad_overlap, bad_safe, bad_multi, bad_3d = [], [], [], []
boxes3d = scene.get("boxes", {}) if scene else {}  # ep multi-cena: o foco fora da faixa de legenda vem em scene["foco"]
for fr, L in lay.items():
    cap = L.get("legenda"); pills = L.get("pilulas", [])
    if len(pills) > 1:
        bad_multi.append(int(fr))
    for p in pills:
        if cap and inter(cap, p) > 0:
            bad_overlap.append(int(fr))
    for bx in [cap] + pills:
        if bx and (bx[0] < 0.05 or bx[2] > 0.95 or bx[1] < 0.10 or bx[3] > 0.80):
            bad_safe.append(int(fr))
    # legenda em cima do rosto da Pipo (pega o quadro QA mais proximo)
    if cap and boxes3d:
        k = min(boxes3d, key=lambda q: abs(int(q) - int(fr)))
        for name, b in boxes3d[k].items():
            if name.startswith("pipo") and b:
                face = [b[0], b[1], b[2], b[1] + (b[3] - b[1]) * 0.55]   # metade de cima = rosto
                fa = (face[2] - face[0]) * (face[3] - face[1])
                if fa > 0 and inter(cap, face) / fa > 0.3:
                    bad_3d.append(int(fr))
for lst, msg, hard in ((bad_overlap, "legenda sobreposta a pilula de texto", True), (bad_multi, "duas pilulas ao mesmo tempo", True),
                       (bad_safe, "texto fora da zona segura", True), (bad_3d, "legenda cobrindo o rosto da Pipo", False)):
    if lst:
        lst.sort()
        (FAIL if hard and len(lst) > 2 else WARN).append(f"{msg}: {len(lst)} quadros (ex.: {lst[:6]})")

# 3) arquivo final
if os.path.exists(MP4):
    pr = subprocess.run(["ffprobe", "-v", "0", "-show_entries", "stream=codec_type,width,height", "-show_entries", "format=duration", "-of", "json", MP4], capture_output=True, text=True)
    info = json.loads(pr.stdout)
    vs = [s for s in info["streams"] if s["codec_type"] == "video"]
    if not vs or (vs[0]["width"], vs[0]["height"]) != (1080, 1920):
        FAIL.append("resolucao diferente de 1080x1920")
    if not any(s["codec_type"] == "audio" for s in info["streams"]):
        FAIL.append("sem audio")
    dur = float(info["format"]["duration"])
    lu = subprocess.run(["ffmpeg", "-i", MP4, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = [l for l in lu.splitlines() if l.strip().startswith("I:")]
    if I:
        v = float(I[-1].split()[1])
        if not -16.5 <= v <= -12.5:
            WARN.append(f"loudness {v} LUFS (alvo -14)")
    bl = subprocess.run(["ffmpeg", "-i", MP4, "-vf", "blackdetect=d=0.3:pix_th=0.08", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    if "black_start" in bl:
        FAIL.append("trecho preto detectado")
    # folha de contato: 1 quadro a cada 1,5 s
    n = max(1, int(dur / 1.5))
    thumbs = []
    for i in range(n):
        t = 0.2 + i * 1.5
        out = f"/tmp/qa_{i}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", MP4, "-frames:v", "1", "-vf", "scale=216:384", out])
        if os.path.exists(out):
            im = Image.open(out); ImageDraw.Draw(im).text((6, 6), f"{t:.1f}s", fill=(255, 255, 0)); thumbs.append(im)
    cols = 8
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 216, rows * 384), (0, 0, 0))
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * 216, (i // cols) * 384))
    sheet.save(f"{WORK}/qa_sheet_{lang}.jpg", quality=85)
else:
    FAIL.append(f"{MP4} nao existe")

rep = [f"# Revisao automatica ({lang})", "", "RESULTADO: " + ("REPROVADO" if FAIL else "APROVADO na parte automatica"), ""]
rep += ["## Reprovacoes"] + [f"- {x}" for x in FAIL] + ["", "## Alertas"] + [f"- {x}" for x in WARN]
rep += ["", f"Folha de contato para a revisao visual: {WORK}/qa_sheet_{lang}.jpg"]
open(f"{WORK}/qa_report_{lang}.md", "w").write("\n".join(rep))
print("\n".join(rep))
sys.exit(1 if FAIL else 0)
