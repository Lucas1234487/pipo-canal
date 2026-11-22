"""Render de um episódio no Kaggle com as 2 GPUs em paralelo.
Uso (no notebook, depois do kaggle_setup.sh):
  python3 render_kaggle.py <pasta_blend_com_manifest> <largura> <altura> <amostras>
Cada GPU vira um processo (CUDA_VISIBLE_DEVICES) e renderiza metade dos quadros (intercalados).
Saída: /kaggle/working/out/frames/fNNNN.png e /kaggle/working/out/video/quadros.mp4 (CRF 14, para devolver via GitHub)."""
import json, os, subprocess, sys, time
B, W, H, SPP = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
OUT = "/kaggle/working/out"; os.makedirs(OUT + "/frames", exist_ok=True); os.makedirs(OUT + "/video", exist_ok=True)
man = json.load(open(B + "/manifest.json"))
jobs = []
for m in man:
    for f in range(m["frame_start"], m["frame_end"] + 1):
        jobs.append((m["blend"], f))
jobs.sort(key=lambda j: j[1])
CH = 240
EP = os.environ.get("EP", "ep003")
allf = [f for _, f in jobs]
chunks = [allf[i:i + CH] for i in range(0, len(allf), CH)]
def ja_enviado(i):
    r = subprocess.run(["git", "ls-remote", "https://github.com/Lucas1234487/pipo-canal", f"render-out/{EP}-c{i:02d}"], capture_output=True, text=True)
    return bool(r.stdout.strip())
feitos = {i for i in range(len(chunks)) if ja_enviado(i)}
print("PEDAÇOS JÁ ENVIADOS", sorted(feitos), "de", len(chunks), flush=True)
pular = {f for i in feitos for f in chunks[i]}
jobs = [j for j in jobs if j[1] not in pular]
def envia(i):
    fr = chunks[i]; d = f"{OUT}/c{i:02d}"; os.makedirs(d, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-start_number", str(fr[0]), "-i", f"{OUT}/frames/f%04d.png",
                    "-frames:v", str(len(fr)), "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv444p", f"{d}/quadros.mp4"], check=True)
    json.dump(dict(first=fr[0], last=fr[-1], n=len(fr), w=W, h=H, spp=SPP), open(f"{d}/info.json", "w"))
    r = subprocess.run(["bash", "/home/claude/pipo-canal/render/kaggle_push.sh", d, f"render-out/{EP}-c{i:02d}", f"{EP} pedaço {i}"], capture_output=True, text=True)
    print("ENVIO", i, r.stdout.strip()[-60:], r.returncode, flush=True)
    return r.returncode == 0
WORKER = r'''
import bpy, sys, json, time, os
jobs = json.loads(sys.argv[-1]); B, W, H, SPP, OUT = sys.argv[-6], int(sys.argv[-5]), int(sys.argv[-4]), int(sys.argv[-3]), sys.argv[-2]
cur = None; t0 = time.time()
def gpu():
    pr = bpy.context.preferences.addons["cycles"].preferences
    for k in ("OPTIX", "CUDA"):
        try:
            pr.compute_device_type = k; pr.get_devices()
            d = [x for x in pr.devices if x.type == k]
            if d:
                for x in pr.devices: x.use = (x.type == k)
                return k
        except Exception: pass
    return "CPU"
for i, (bl, f) in enumerate(jobs):
    if bl != cur:
        bpy.ops.wm.open_mainfile(filepath=os.path.join(B, bl)); cur = bl
        dev = gpu(); s = bpy.context.scene
        s.cycles.device = "GPU" if dev != "CPU" else "CPU"
        s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = W, H, 100
        s.cycles.samples = SPP; s.render.image_settings.file_format = "PNG"
        print("ABRIU", bl, dev, flush=True)
    s.frame_set(f); s.render.filepath = f"{OUT}/frames/f{f:04d}.png"
    bpy.ops.render.render(write_still=True)
    if i % 25 == 0: print("Q", f, round((time.time() - t0) / (i + 1), 2), "s/quadro", flush=True)
print("FIM", len(jobs), round(time.time() - t0), flush=True)
'''
open("/tmp/worker.py", "w").write(WORKER)
procs = []
t = time.time()
for g in (0, 1):
    part = jobs[g::2]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(g))
    log = open(f"{OUT}/gpu{g}.log", "w")
    procs.append(subprocess.Popen(["python3", "/tmp/worker.py", B, str(W), str(H), str(SPP), OUT, json.dumps(part)], env=env, stdout=log, stderr=subprocess.STDOUT))
def pronto(i):
    return all(os.path.exists(f"{OUT}/frames/f{f:04d}.png") for f in chunks[i])
while True:
    vivos = any(p.poll() is None for p in procs)
    for i in range(len(chunks)):
        if i not in feitos and pronto(i):
            time.sleep(3)
            if envia(i): feitos.add(i)
    n = len(os.listdir(OUT + "/frames"))
    print(f"{n}/{len(jobs)} quadros novos, pedaços {len(feitos)}/{len(chunks)}, {round(time.time()-t)} s", flush=True)
    if not vivos: break
    time.sleep(30)
faltam = [i for i in range(len(chunks)) if i not in feitos]
print("PEDAÇOS FALTANDO", faltam, flush=True)
if faltam: sys.exit(1)
print("TUDO ENVIADO", round(time.time() - t), "s")
