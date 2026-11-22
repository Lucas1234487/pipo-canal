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
while any(p.poll() is None for p in procs):
    time.sleep(30)
    n = len(os.listdir(OUT + "/frames"))
    print(f"{n}/{len(jobs)} quadros, {round(time.time()-t)} s", flush=True)
falta = [f for _, f in jobs if not os.path.exists(f"{OUT}/frames/f{f:04d}.png")]
print("FALTANDO", falta[:20], len(falta))
first = jobs[0][1]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-start_number", str(first), "-i", f"{OUT}/frames/f%04d.png",
                "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv444p", f"{OUT}/video/quadros.mp4"], check=True)
json.dump(dict(first=first, n=len(jobs), w=W, h=H, spp=SPP, segundos=round(time.time()-t)), open(f"{OUT}/video/info.json", "w"))
print("VIDEO", os.path.getsize(f"{OUT}/video/quadros.mp4") // 1e6, "MB")
