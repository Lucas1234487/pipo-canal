"""Previas dos mundos do ep003. Uso: python3 /home/claude/ep003/prev_mundos.py [a,b,c,d]
Grava /home/claude/ep003/prev_mundos/{a_rex_cinzas,b_galinha_match,c_comparacao,d_pipo_foge}.png
e prev_mundos/tempos.txt (tempo do quadro com sincronizacao da cena e tempo de um quadro seguinte, cena ja carregada)."""
import sys, os, time, json
sys.path.insert(0, "/home/claude/ep003")
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
import mundos as M

OUT = "/home/claude/ep003/prev_mundos"
os.makedirs(OUT, exist_ok=True)
FR_PEAK = 24
sel = (sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].endswith(".py") else "a,b,c,d").split(",")
log = {}
if os.path.exists(OUT + "/tempos.json"):
    log = json.load(open(OUT + "/tempos.json"))


def foco_tela(objs):
    """faixa vertical (0 = topo) ocupada pelos objetos de foco na tela"""
    s = bpy.context.scene; cam = s.camera
    deps = bpy.context.evaluated_depsgraph_get()
    ys = []
    for o in objs:
        if o.type != 'MESH':
            continue
        oe = o.evaluated_get(deps)
        me = oe.to_mesh()
        mw = oe.matrix_world
        for i, v in enumerate(me.vertices):
            if i % 3:
                continue
            p = world_to_camera_view(s, cam, mw @ v.co)
            if p.z > 0 and 0 <= p.x <= 1 and 0 <= p.y <= 1:
                ys.append(1 - p.y)
        oe.to_mesh_clear()
    if not ys:
        return None
    ys.sort()
    return round(ys[int(len(ys) * 0.03)], 3), round(ys[int(len(ys) * 0.97) - 1], 3)


def shot(name, frame, foco):
    s = bpy.context.scene
    s.frame_set(frame)
    s.render.filepath = f"{OUT}/{name}.png"
    t = time.time(); bpy.ops.render.render(write_still=True); t1 = time.time() - t
    s.frame_set(frame + 1)
    s.render.filepath = f"/tmp/_{name}_warm.png"
    t = time.time(); bpy.ops.render.render(write_still=True); t2 = time.time() - t
    s.frame_set(frame)
    band = foco_tela(foco)
    log[name] = dict(frame=frame, primeiro_s=round(t1, 2), quadro_s=round(t2, 2), foco_y=band)
    print("TIME", name, log[name], flush=True)
    json.dump(log, open(OUT + "/tempos.json", "w"), indent=1)


if "a" in sel:
    cz = M.mundo_cinzas()
    bpy.context.scene.frame_set(FR_PEAK)
    log["rex_refs"] = M.tela_refs(cz["cam"], cz["head_pose"])
    shot("a_rex_cinzas", FR_PEAK, cz["foco_objs"])
if "b" in sel:
    qt = M.mundo_quintal()
    bpy.context.scene.frame_set(FR_PEAK)
    e, p = log["rex_refs"]
    log["gal_refs"] = M.match_cut(qt["cam"], qt["head_pose"], e, p)
    print("MATCH rex", log["rex_refs"], "gal", log["gal_refs"])
    shot("b_galinha_match", FR_PEAK, qt["foco_objs"])
if "c" in sel:
    cp = M.mundo_comparacao()
    shot("c_comparacao", FR_PEAK, [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(("rex_cranio", "gal_cabeca"))])
if "d" in sel:
    qt = M.mundo_quintal()
    F0 = 90
    ev = M.pipo_foge(qt, f0=F0)
    cam = qt["cam"]
    pp = Vector((-0.06, -0.22, 0)); gp = Vector(qt["galinha"]["root"].matrix_world.translation)
    mid = (pp + gp) * 0.5
    cam.location = (mid.x - 0.03, mid.y - 1.22, 0.2)
    M.look(cam, (mid.x - 0.03, mid.y, 0.2))
    cam.data.lens = 28; cam.data.shift_y = -0.045; cam.data.shift_x = 0
    cam.data.dof.focus_object = None; cam.data.dof.focus_distance = (Vector(cam.location) - mid).length; cam.data.dof.aperture_fstop = 3.2
    shot("d_pipo_foge", ev["f_congela"] + 6, [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(("cob", "gal_"))])
