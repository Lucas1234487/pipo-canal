"""Teste de GPU no Kaggle. Uso: python3 gpu_test.py  (roda depois de kaggle_setup.sh)"""
import sys, os, time, json
sys.path.insert(0, "/home/claude/ep003")
import bpy
import mundos as M

def use_gpu():
    pr = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA"):
        try:
            pr.compute_device_type = kind
            pr.get_devices()
            devs = [d for d in pr.devices if d.type == kind]
            if devs:
                for d in pr.devices: d.use = (d.type == kind)
                bpy.context.scene.cycles.device = "GPU"
                return kind, [d.name for d in devs]
        except Exception as e:
            print("falhou", kind, e)
    return "CPU", []

cz = M.mundo_cinzas()
s = bpy.context.scene
print("DEVICE", use_gpu(), flush=True)
res = {}
for nome, (w, h, spp) in {"540_3spp": (540, 960, 3), "1080_16spp": (1080, 1920, 16)}.items():
    s.render.resolution_x, s.render.resolution_y = w, h
    s.render.resolution_percentage = 100
    s.cycles.samples = spp
    ts = []
    for f in (24, 25, 26):
        s.frame_set(f); s.render.filepath = f"/kaggle/working/test_{nome}_{f}.png"
        t = time.time(); bpy.ops.render.render(write_still=True); ts.append(round(time.time() - t, 2))
    res[nome] = ts
    print("TIME", nome, ts, flush=True)
json.dump(res, open("/kaggle/working/gpu_tempos.json", "w"))
print("RESULTADO", res)
