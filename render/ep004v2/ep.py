"""ep004 v2: O T. rex tinha ossinho da sorte. 23,0 s (690 quadros, 30 fps), narracao ja gravada (timing.json).
Abre na CEIA (duas maos puxando o ossinho no quadro 1). Quatro mundos, cada um vira UM .blend; o manifest lista os trechos:
    B_ceia     maos puxando o ossinho (P1), tensao (B2-B3), ESTALO + pop da Pipo no quadro 575, vitoria e loop (B4-B5)
    A_cinzas   T. rex nas cinzas (luz aprovada do ep003): rugido, raio-x acende o V no ALTO do peito, close no V (duas/claviculas/grudadas)
    Q_quintal  quintal ao sol do ep003: galinha Kelgar ciscando, card do @Niko_com_k, carimbo ACERTOU!
    C_primos   tela dividida bem iluminada: raio-x do rex | raio-x da galinha; no "herdaram" os dois V voam ao centro e encaixam
Modos:
    python3 ep.py qa                 QA da cena em todos os mundos (qa_scene.json; sai com 1 se houver falha)
    python3 ep.py 10,80,200          previa de quadros em WORK/prev (p_NNNN.png, PIPO_RES=50 -> 540x960) + prev/tempos.json
    python3 ep.py blend              WORK/blend/*.blend empacotados + manifest.json
    python3 ep.py tempo              mede s/quadro em 1080x1920 (OIDN) num quadro de cada mundo -> tempo_cpu.txt
Nada do render depende deste script: tudo vira keyframe, NLA, parentesco ou modificador.
"""
import sys, os, json, math, random, time
KIT = os.environ.get("PIPO_KIT", "/home/claude/pipo-canal/kit")
WORK = os.environ.get("PIPO_WORK", "/home/claude/ep004v2")
os.environ.setdefault("PIPO_KIT", KIT); os.environ.setdefault("PIPO_WORK", WORK)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORK)
import bpy, bmesh
from mathutils import Vector, Euler, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view
import mundos_ep003 as M
import mundos_ep004 as X
import maos as MAOS

D = bpy.data
FPS = 30
f = lambda t: int(round(t * FPS)) + 1
T = json.load(open(WORK + "/timing.json"))
N = 690
M.N = N
WT = {}
for l in T["lines"]:
    for w_, s_, du in l["words"]:
        WT.setdefault(w_.lower().strip(".,!:?…"), []).append(s_)


def wt(word, n=0):
    return WT[word.lower()][n]


FONT = KIT + "/Fredoka-700.ttf"
F_POP = 575                                   # estalo do osso + pop da Pipo (19,13 s)
PLAN = [
    ("P1_ceia", "B", 0.0),                    # Esse ossinho que voce disputa na ceia
    ("A1_rugido", "A", 2.52),                 # e de dinossauro (corte no "dinossauro")
    ("A2_peito", "A", 4.28),                  # O T. rex tinha igual, no alto do peito (raio-x acende o V)
    ("A3_close", "A", 6.27),                  # Duas claviculas grudadas em V
    ("Q1_quintal", "Q", 8.47),                # O Niko acertou: aves sao dinossauros
    ("C1_primos", "C", 11.08),                # A galinha e prima do T. rex
    ("C2_herdaram", "C", 13.40),              # Os dois herdaram esse osso
    ("B2_mesa", "B", 15.40),                  # Entao quando voce puxar ele
    ("B3_tensao", "B", 17.30),                # vai disputar um osso de dinossauro -> ESTALO
    ("B4_vitoria", "B", (F_POP - 1) / FPS),   # o pedaco maior sobe contra o bokeh da arvore
    ("B5_loop", "B", 20.75),                  # quem ficou com o maior? (rima com o quadro 1)
]
SH = {}
for i, (nm, w_, t0) in enumerate(PLAN):
    f0 = f(t0) if nm != "B4_vitoria" else F_POP
    SH[nm] = dict(name=nm, world=w_, t0=t0, f0=f0)
for i, (nm, w_, t0) in enumerate(PLAN):
    SH[nm]["f1"] = (SH[PLAN[i + 1][0]]["f0"] - 1) if i + 1 < len(PLAN) else N
WORLDS = {"B": "B_ceia", "A": "A_cinzas", "Q": "Q_quintal", "C": "C_primos"}
ORDER = ("B", "A", "Q", "C")


def segments(world):
    out = []
    for nm, w_, _ in PLAN:
        if w_ != world:
            continue
        a, b = SH[nm]["f0"], SH[nm]["f1"]
        if out and out[-1][1] + 1 == a:
            out[-1][1] = b
        else:
            out.append([a, b])
    return out


def world_of(fr):
    for nm, w_, _ in PLAN:
        if SH[nm]["f0"] <= fr <= SH[nm]["f1"]:
            return w_
    return PLAN[-1][1]


def shot_of(fr):
    for nm, w_, _ in PLAN:
        if SH[nm]["f0"] <= fr <= SH[nm]["f1"]:
            return nm
    return PLAN[-1][0]


P_STAR = (0.5, 0.42)          # ponto da tela onde cai o V (rima entre os mundos), acima da faixa de legenda

K = M.K
look = M.look


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return Vector(a).lerp(Vector(b), u)


def under(o, root):
    while o is not None:
        if o == root:
            return True
        o = o.parent
    return False


def desc_meshes(root):
    out = [root] if root.type in ('MESH', 'FONT', 'CURVE') else []
    out += [c for c in root.children_recursive if c.type in ('MESH', 'FONT', 'CURVE')]
    return out


def keys_lin(obj):
    for fc in M.fcurves(obj):
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'


def key_hide(objs, frames_vals):
    """visibilidade animada: [(quadro, escondido)] (constante entre chaves)"""
    for o in objs:
        for fr, hid in frames_vals:
            o.hide_render = hid
            o.keyframe_insert("hide_render", frame=fr)
        for fc in M.fcurves(o):
            if fc.data_path == "hide_render":
                for k in fc.keyframe_points:
                    k.interpolation = 'CONSTANT'


def vis_window(roots, a, b):
    """objetos (e descendentes) so existem no render entre a e b: fora disso nem entram no BVH (custo zero)"""
    objs = []
    for r in roots:
        for o in [r] + list(r.children_recursive):
            if o.type != 'LIGHT' and o not in objs:
                objs.append(o)
    key_hide(objs, [(1, True), (a, False), (b + 1, True)])


def key_scale_vis(o, frames_vals, base=None):
    """mostra/esconde por escala (para hierarquias)"""
    base = base or tuple(o.scale)
    for fr, vis in frames_vals:
        K(o, "scale", fr, base if vis else (0.0005,) * 3)
    for fc in M.fcurves(o):
        if fc.data_path == "scale":
            for k in fc.keyframe_points:
                k.interpolation = 'CONSTANT'


def key_val(sock, fr_vals, interp='LINEAR'):
    for fr, v in fr_vals:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=fr)


def nt_interp(nt, mode='LINEAR'):
    for fc in M.fcurves_nt(nt):
        for k in fc.keyframe_points:
            k.interpolation = mode


def light_keys(lo, fr_vals):
    for fr, e in fr_vals:
        lo.data.energy = e
        lo.data.keyframe_insert("energy", frame=fr)
    ad = lo.data.animation_data
    for fc in M.fcurves(lo.data):
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'


def only_during(lo, fa, fb, e, ramp=0):
    """luz ligada so dentro dos planos dela (o resto do mundo nao muda)"""
    light_keys(lo, [(1, 0.0), (fa - 1, 0.0), (fa + ramp, e), (fb, e), (fb + 1, 0.0)])


def hide_from_camera(objs):
    for o in objs:
        o.visible_camera = False
        o.visible_glossy = False
        o.visible_transmission = False


def ground_at(g, x, y):
    return M.ground_z(g, x, y)


def wpos(o):
    return o.matrix_world.translation.copy()


# ---------------------------------------------------------------- camera: tudo assado em chaves a cada 2 quadros
class Cam:
    def __init__(self, cam):
        self.cam = cam; self.cd = cam.data; self.prev = None
        self.cd.dof.use_dof = True
        self.cd.dof.focus_object = None
        self.cd.sensor_fit = 'AUTO'

    def shot(self, sh, fn, step=2, track=False):
        sc = bpy.context.scene
        f0, f1 = sh["f0"], sh["f1"]
        frs = list(range(f0, f1 + 1, step))
        if frs[-1] != f1:
            frs.append(f1)
        for fr in frs:
            if track:
                sc.frame_set(fr)
            u = (fr - f0) / max(1, f1 - f0)
            d = fn(u, fr)
            loc = Vector(d["loc"])
            if "rot" in d:
                q = d["rot"].to_quaternion() if hasattr(d["rot"], "to_quaternion") else d["rot"]
            else:
                q = (Vector(d["tgt"]) - loc).to_track_quat('-Z', 'Y')
                if d.get("roll"):
                    q = q @ Quaternion((0, 0, 1), d["roll"])
            e = q.to_euler('XYZ', self.prev) if self.prev is not None else q.to_euler('XYZ')
            self.prev = e.copy()
            self.cam.location = loc; self.cam.rotation_euler = e
            self.cam.keyframe_insert("location", frame=fr); self.cam.keyframe_insert("rotation_euler", frame=fr)
            self.cd.lens = d.get("lens", 30); self.cd.keyframe_insert("lens", frame=fr)
            self.cd.shift_x = d.get("sx", 0.0); self.cd.keyframe_insert("shift_x", frame=fr)
            self.cd.shift_y = d.get("sy", 0.0); self.cd.keyframe_insert("shift_y", frame=fr)
            fd = d.get("fd")
            if fd is None:
                fd = (Vector(d.get("focus", d.get("tgt", loc + Vector((0, 1, 0))))) - loc).length
            self.cd.dof.focus_distance = max(0.02, fd); self.cd.keyframe_insert("dof.focus_distance", frame=fr)
            self.cd.dof.aperture_fstop = d.get("fs", 8.0); self.cd.keyframe_insert("dof.aperture_fstop", frame=fr)

    def done(self):
        for o in (self.cam, self.cd):
            for fc in M.fcurves(o):
                for k in fc.keyframe_points:
                    k.interpolation = 'LINEAR'


def shake(fr, amp, seed=0, freq=0.35):
    random.seed(seed)
    return Vector((math.sin(fr * freq * 1.7 + seed) * amp, math.sin(fr * freq * 1.3 + 2 + seed) * amp * 0.6, math.sin(fr * freq * 2.1 + 4 + seed) * amp))


def cam_from_local(ref_obj, loc_local, tgt_local):
    mw = ref_obj.matrix_world
    return mw @ Vector(loc_local), mw @ Vector(tgt_local)


# ---------------------------------------------------------------- QA (modelo da run_qa do kit, por mundo)
QA = dict(keys={}, touch=set(), screen_ok=set(), focus={}, inteiros={})


def qa_key(name, *objs):
    QA["keys"][name] = list(objs)


def qa_touch(a, b):
    """dois grupos encostam/atravessam DE PROPOSITO (BVH e sobreposicao na tela liberados)"""
    QA["touch"].add(tuple(sorted((a, b))))


def qa_tela(a, b):
    """sobreposicao so NA TELA (um na frente do outro, longe em profundidade): o BVH continua checando"""
    QA["screen_ok"].add(tuple(sorted((a, b))))


def qa_foco(shot, *objs, fa=None, fb=None):
    """pontos de foco do plano (olho, cabeca, furcula...): fora de 60-72% de y e dentro da zona segura.
    fa/fb: janela de quadros em que o ponto e o foco (ex.: a Pipo ate sair de quadro; depois o foco e a galinha)"""
    QA["focus"].setdefault(shot, []).extend((o, fa, fb) for o in objs)


def qa_inteiro(shot, *groups):
    """grupos que precisam aparecer inteiros no plano (nao cortados na borda)"""
    QA["inteiros"].setdefault(shot, []).extend(groups)


SAFE = (0.05, 0.10, 0.95, 0.80)      # mesma zona segura do qa_check.py
BAND_LEG = (0.60, 0.72)              # pontos de foco (pedido do Diretor)
BAND_TXT = {"legenda": (0.58, 0.70), "pilula": (0.11, 0.20)}


def _meshes_q(objs):
    out = []
    for o in objs:
        for m in desc_meshes(o):
            if m not in out:
                out.append(m)
    return out


def _vis(o):
    if o.hide_render:
        return False
    p = o
    while p is not None:
        if p.hide_render:
            return False
        p = p.parent
    return o.matrix_world.to_scale().length > 0.003


def _bbox2d(objs, cam, sc):
    xs, ys = [], []
    for o in objs:
        if not _vis(o):
            continue
        mw = o.matrix_world
        for c in o.bound_box:
            p = world_to_camera_view(sc, cam, mw @ Vector(c))
            if p.z > 0:
                xs.append(p.x); ys.append(1 - p.y)
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def run_qa(world, step=3, bvh_step=15):
    from mathutils.bvhtree import BVHTree
    sc = bpy.context.scene; cam = sc.camera
    gm = {k: _meshes_q(v) for k, v in QA["keys"].items()}
    texts = [o for o in D.objects if o.type == 'FONT']
    issues = []
    focus_log = {}
    deps = bpy.context.evaluated_depsgraph_get()
    frames = []
    for a, b in segments(world):
        frames += list(range(a, b + 1, step))
        if frames[-1] != b:
            frames.append(b)
    for n_, fr in enumerate(frames):
        sc.frame_set(fr)
        shn = shot_of(fr)
        bx = {k: _bbox2d(v, cam, sc) for k, v in gm.items()}
        bx = {k: b for k, b in bx.items() if b and (b[2] - b[0]) * (b[3] - b[1]) > 0.0004 and b[2] > 0 and b[0] < 1 and b[3] > 0 and b[1] < 1}
        ks = list(bx)
        for i in range(len(ks)):
            a = bx[ks[i]]
            w_ = a[2] - a[0]; h_ = a[3] - a[1]
            if ks[i] in QA["inteiros"].get(shn, []) and (a[0] < -0.02 or a[2] > 1.02 or a[1] < -0.02 or a[3] > 1.02):
                issues.append(dict(frame=fr, plano=shn, tipo="cortado_na_borda", alvo=ks[i], bbox=[round(x, 3) for x in a]))
            for j in range(i + 1, len(ks)):
                pair = tuple(sorted((ks[i], ks[j])))
                if pair in QA["touch"] or pair in QA["screen_ok"]:
                    continue
                b = bx[ks[j]]
                ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
                amin = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
                if amin > 0 and ix * iy / amin > 0.15:
                    issues.append(dict(frame=fr, plano=shn, tipo="imagens_sobrepostas", alvo=f"{ks[i]} x {ks[j]}", fracao=round(ix * iy / amin, 2)))
        for t in texts:
            if not _vis(t):
                continue
            b = _bbox2d([t], cam, sc)
            if not b or (b[2] - b[0]) < 0.03 or b[3] < 0 or b[1] > 1:
                continue
            for band, (y0, y1) in BAND_TXT.items():
                if b[1] < y1 and b[3] > y0 and b[2] > 0.1 and b[0] < 0.9:
                    issues.append(dict(frame=fr, plano=shn, tipo=f"texto3d_na_faixa_da_{band}", alvo=t.data.body))
            if b[0] < SAFE[0] or b[2] > SAFE[2] or b[1] < SAFE[1] or b[3] > SAFE[3]:
                issues.append(dict(frame=fr, plano=shn, tipo="texto3d_fora_da_zona_segura", alvo=t.data.body, bbox=[round(x, 3) for x in b]))
        for o, fa_, fb_ in QA["focus"].get(shn, []):
            if (fa_ and fr < fa_) or (fb_ and fr > fb_):
                continue
            if not _vis(o) and o.type != 'EMPTY':
                continue
            p = world_to_camera_view(sc, cam, o.matrix_world.translation)
            x, y = p.x, 1 - p.y
            focus_log.setdefault(shn, []).append((fr, o.name, round(x, 3), round(y, 3)))
            if p.z <= 0:
                continue
            if BAND_LEG[0] <= y <= BAND_LEG[1]:
                issues.append(dict(frame=fr, plano=shn, tipo="foco_na_faixa_da_legenda", alvo=o.name, y=round(y, 3)))
            if not (SAFE[0] <= x <= SAFE[2] and SAFE[1] <= y <= SAFE[3]):
                issues.append(dict(frame=fr, plano=shn, tipo="foco_fora_da_zona_segura", alvo=o.name, xy=[round(x, 3), round(y, 3)]))
        if n_ % max(1, bvh_step // step) == 0:
            trees = {}
            for k, objs in gm.items():
                if k not in bx:
                    continue
                for o in objs:
                    if o.type not in ('MESH', 'CURVE', 'FONT') or not _vis(o):
                        continue
                    try:
                        oe = o.evaluated_get(deps)
                        me = oe.to_mesh()
                        vs = [oe.matrix_world @ v.co for v in me.vertices]
                        ps = [tuple(p.vertices) for p in me.polygons]
                        if ps:
                            trees.setdefault(k, []).append(BVHTree.FromPolygons(vs, ps))
                        oe.to_mesh_clear()
                    except Exception:
                        pass
            kk = list(trees)
            for i in range(len(kk)):
                for j in range(i + 1, len(kk)):
                    if tuple(sorted((kk[i], kk[j]))) in QA["touch"]:
                        continue
                    if any(ta.overlap(tb) for ta in trees[kk[i]] for tb in trees[kk[j]]):
                        issues.append(dict(frame=fr, plano=shn, tipo="objetos_atravessando", alvo=f"{kk[i]} x {kk[j]}"))
    return issues, focus_log


# ================================================================ materiais extras
def mat_mix_xray(name, rim_col=(1.0, 0.45, 0.2), rim=4.0, xcol=(0.35, 0.8, 1.0), xs=1.0):
    """silhueta com contraluz (a do mundo de comparacao) <-> raio-x (borda ciano, miolo transparente).
    devolve (material, socket do fator) para animar em keyframes"""
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; M._clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.25
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(pw.outputs[0], mx.inputs[0]); mx.inputs[6].default_value = (0.012, 0.006, 0.025, 1); mx.inputs[7].default_value = (*rim_col, 1)
    e = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mx.outputs[2], e.inputs["Color"])
    ml = nt.nodes.new("ShaderNodeMath"); ml.operation = 'MULTIPLY_ADD'; ml.inputs[1].default_value = rim; ml.inputs[2].default_value = 1.0
    nt.links.new(pw.outputs[0], ml.inputs[0]); nt.links.new(ml.outputs[0], e.inputs["Strength"])
    # raio-x
    lw2 = nt.nodes.new("ShaderNodeLayerWeight"); lw2.inputs["Blend"].default_value = 0.45
    p2 = nt.nodes.new("ShaderNodeMath"); p2.operation = 'POWER'; p2.inputs[1].default_value = 1.6
    nt.links.new(lw2.outputs["Facing"], p2.inputs[0])
    e2 = nt.nodes.new("ShaderNodeEmission"); e2.inputs["Color"].default_value = (*xcol, 1)
    s2 = nt.nodes.new("ShaderNodeMath"); s2.operation = 'MULTIPLY_ADD'; s2.inputs[1].default_value = 3.5 * xs; s2.inputs[2].default_value = 0.08 * xs
    nt.links.new(p2.outputs[0], s2.inputs[0]); nt.links.new(s2.outputs[0], e2.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = 'MULTIPLY_ADD'; a2.inputs[1].default_value = 0.75; a2.inputs[2].default_value = 0.12
    nt.links.new(p2.outputs[0], a2.inputs[0])
    mx2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a2.outputs[0], mx2.inputs[0]); nt.links.new(tr.outputs[0], mx2.inputs[1]); nt.links.new(e2.outputs[0], mx2.inputs[2])
    fin = nt.nodes.new("ShaderNodeMixShader"); fin.name = "XRAY"
    nt.links.new(e.outputs[0], fin.inputs[1]); nt.links.new(mx2.outputs[0], fin.inputs[2]); nt.links.new(fin.outputs[0], out.inputs[0])
    fin.inputs[0].default_value = 0.0
    return m, fin.inputs[0]


def mat_simple(name, col, rough=0.5, emit=0.0, spec=0.5):
    m = D.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Roughness"].default_value = rough
    try:
        p.inputs["Specular IOR Level"].default_value = spec
    except Exception:
        pass
    if emit:
        p.inputs["Emission Color"].default_value = (*col, 1); p.inputs["Emission Strength"].default_value = emit
    return m


def text_obj(body, size, mat, loc, parent=None, align='LEFT', extrude=0.0):
    cu = D.curves.new("txt", 'FONT')
    cu.body = body
    cu.font = D.fonts.load(FONT, check_existing=True)
    cu.size = size; cu.extrude = extrude
    cu.align_x = align; cu.align_y = 'CENTER'
    o = M.link(D.objects.new("txt_" + body[:12], cu))
    cu.materials.append(mat)
    o.location = loc
    if parent:
        o.parent = parent
    return o


def join_baked(objs, ref_inv, name):
    """junta as malhas avaliadas (com modificadores) num objeto so, no espaco de ref (para instanciar barato)"""
    deps = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    mats = []
    for o in objs:
        if o.type not in ('MESH', 'CURVE'):
            continue
        oe = o.evaluated_get(deps)
        me = oe.to_mesh()
        if me is None or not len(me.polygons):
            oe.to_mesh_clear(); continue
        me = me.copy()
        me.transform(ref_inv @ o.matrix_world)
        remap = []
        for m in (me.materials or [None]):
            if m not in mats:
                mats.append(m)
            remap.append(mats.index(m))
        for p in me.polygons:
            p.material_index = remap[min(p.material_index, len(remap) - 1)]
        bm.from_mesh(me)
        D.meshes.remove(me)
        oe.to_mesh_clear()
    out = D.meshes.new(name); bm.to_mesh(out); bm.free()
    for m in mats:
        out.materials.append(m)
    for p in out.polygons:
        p.use_smooth = True
    return out



def add_noise_range(obj, path, fa, fb, strength=0.05, scale=1.5):
    for fc in M.fcurves(obj):
        if fc.data_path == path:
            mo = fc.modifiers.new('NOISE'); mo.strength = strength; mo.scale = scale
            mo.use_restricted_range = True; mo.frame_start = fa; mo.frame_end = fb; mo.blend_in = 2; mo.blend_out = 5


# ================================================================ tela: posicao de um ponto e enquadramento
def shift_for(sx, sy):
    """shift da camera que leva o ponto mirado (centro) para (sx, sy) da tela (y de cima). Retrato: unidade = altura."""
    W_, H_ = bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y
    return -(sx - 0.5) * W_ / H_, (sy - 0.5)


def cam_local(lens, d, sx, sy, shx=0.0, shy=0.0):
    """ponto no espaco da camera (distancia d) que cai em (sx, sy) da tela, com lente e shift dados"""
    W_, H_ = bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y
    hh = d * 18.0 / lens
    hw = hh * W_ / H_
    return Vector(((sx - 0.5) * 2 * hw + shx * 2 * hh, (0.5 - sy) * 2 * hh + shy * 2 * hh, -d)), hw


def screen_xy(o_or_p, fr=None):
    sc = bpy.context.scene
    if fr is not None:
        sc.frame_set(fr)
    p = o_or_p if isinstance(o_or_p, Vector) else o_or_p.matrix_world.translation
    v = world_to_camera_view(sc, sc.camera, p)
    return round(v.x, 3), round(1 - v.y, 3)


def key_const(o, path, fr_vals):
    for fr, v in fr_vals:
        K(o, path, fr, v)
    for fc in M.fcurves(o):
        if fc.data_path == path:
            for k in fc.keyframe_points:
                k.interpolation = 'CONSTANT'


def cut_key(o, path, fr, old, new):
    """troca seca no corte (chave no quadro anterior com o valor antigo)"""
    K(o, path, fr - 1, old); K(o, path, fr, new)


def ui_pop(o, fr, base, over=1.15, dur=8, fr_out=None, fr_in_from=0.0005):
    """entra com escala exagerada e assenta; some (escala 0) em fr_out"""
    K(o, "scale", 1, (fr_in_from,) * 3); K(o, "scale", fr - 1, (fr_in_from,) * 3)
    K(o, "scale", fr + int(dur * 0.55), (base * over,) * 3); K(o, "scale", fr + dur, (base,) * 3)
    if fr_out:
        K(o, "scale", fr_out - 1, (base,) * 3); K(o, "scale", fr_out, (0.0005,) * 3)


def furcula_keys(mat, fr_vals, side=None):
    """forca do brilho das claviculas (EL esquerda, ER direita): [(quadro, valor)]"""
    for nm in (("EL", "ER") if side is None else (side,)):
        key_val(X.fsock(mat, nm), fr_vals)
    nt_interp(mat.node_tree)



def shake_keys(o, path, fa, fb, amp_fn, base, seed, step=2, axes=(0, 1, 2)):
    """tremor deterministico em chaves (a cada 'step' quadros) somado a um valor base(fr)"""
    random.seed(seed)
    for fr in range(fa, fb + 1, step):
        a = amp_fn(fr)
        b = Vector(base(fr))
        for i in axes:
            b[i] += random.uniform(-1, 1) * a
        K(o, path, fr, tuple(b))


def pose_hand(h_obj, hook, tip_world, fwd_mesh, fwd_want, scale, roll=0.0):
    """posiciona a mao (malha com origem na pinca) com a pinca na ponta do osso e o antebraco saindo para o lado;
    depois parenta ao gancho do braco do V (a mao acompanha a ponta: puxao, curvatura, tremor, quebra)"""
    q = Vector(fwd_mesh).normalized().rotation_difference(Vector(fwd_want).normalized())
    if roll:
        q = Quaternion(Vector(fwd_want).normalized(), roll) @ q
    mw = Matrix.LocRotScale(Vector(tip_world), q, Vector((scale,) * 3))
    bpy.context.view_layer.update()
    h_obj.parent = hook
    h_obj.matrix_parent_inverse = Matrix.Identity(4)
    bpy.context.view_layer.update()
    h_obj.matrix_world = mw
    bpy.context.view_layer.update()


# ================================================================ MUNDO B: ceia (P1, B2-B5)
OSSO = 0.11            # ossinho de peru grande (m): le bem entre duas maos


def build_B():
    cz = X.mundo_ceia()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    cam = cz["cam"]; S = SH
    Z = X.MESA_Z
    fb1 = S["P1_ceia"]["f1"]
    fa2, fa3, fa4, fa5 = S["B2_mesa"]["f0"], S["B3_tensao"]["f0"], S["B4_vitoria"]["f0"], S["B5_loop"]["f0"]
    # ---------- ossinho no ar, entre as maos, na frente do frango
    BP = Vector((0.0, -0.40, Z + 0.10))                       # raiz (juncao) do V
    fm = X.furcula_mat("furcula_ceia", glow=0.0)
    for k_ in ("EL", "ER"):
        X.fsock(fm, k_).default_value = 0.0
    FB = X.furcula("osso_ceia", None, tuple(BP), (math.radians(-12), 0, 0), OSSO, mat=fm)
    root, giro = FB["root"], FB["giro"]
    HK = X.hooks_abre(FB)
    hL, hR = HK["L"], HK["R"]
    ins, mai, men = FB["inteira"], FB["maior"], FB["menor"]
    # as pecas da quebra vivem nos ganchos: cada mao fica com a sua
    for o, h in ((mai, hL), (men, hR)):
        o.parent = h; o.location = (0, 0, 0)
    bpy.context.view_layer.update()
    # ---------- maos (CC0, assadas em pinca)
    H = MAOS.bake_maos()
    mE, mD = H["R"]["obj"], H["L"]["obj"]                 # mE: mao da esquerda da tela (malha do lado R do rig)
    mE.name = "mao_esquerda"; mD.name = "mao_direita"
    # tons de pele diferentes: duas pessoas
    pele2 = MAOS.mat_pele("pele_mao_2", (0.52, 0.31, 0.2))
    mD.data = mD.data.copy(); mD.data.materials[0] = pele2
    rmw = root.matrix_world
    tipL = rmw @ (X._arm_path(1.0, -1) + Vector((0, 0, -0.04)))
    tipR = rmw @ (X._arm_path(1.0, 1) + Vector((0, 0, -0.04)))
    pose_hand(mE, hL, tipL, H["R"]["fwd"], (1.0, 0.15, -0.55), 0.78, roll=math.radians(-20))
    pose_hand(mD, hR, tipR, H["L"]["fwd"], (-1.0, 0.15, -0.55), 0.78, roll=math.radians(20))
    for o in (mE, mD):
        o.visible_shadow = True
    # ---------- puxoes (rotacao dos ganchos: o V abre e curva), tremor ja no quadro 1, cresce ate o estalo
    f_px, f_ele, f_disp, f_os3, f_din = f(wt("puxar")), f(wt("ele")), f(wt("disputar")), f(wt("osso", 1)), f(wt("dinossauro", 1))
    plan = [(1, 6.0), (fb1, 9.0), (fa2, 6.0), (f_px - 2, 7.0), (f_px + 4, 11.0), (f_ele + 4, 12.5), (f_disp + 4, 15.0), (f_din, 18.0), (F_POP - 1, 21.0)]

    def base_ang(fr):
        for i in range(len(plan) - 1):
            if plan[i][0] <= fr <= plan[i + 1][0]:
                u_ = (fr - plan[i][0]) / max(1, plan[i + 1][0] - plan[i][0])
                return plan[i][1] + (plan[i + 1][1] - plan[i][1]) * u_
        return plan[-1][1]

    def amp(fr):
        if fr < fa2:
            return 1.4
        j = (fr - fa2) / float(F_POP - fa2)
        return 0.8 + 3.4 * j * j
    random.seed(44)
    for fr in list(range(1, F_POP - 1, 2)) + [F_POP - 1]:
        a = amp(fr)
        K(hL, "rotation_euler", fr, (0, math.radians(-(base_ang(fr) + random.uniform(-a, a))), 0))
        K(hR, "rotation_euler", fr, (0, math.radians(base_ang(fr) + random.uniform(-a, a)), 0))
        K(giro, "location", fr, (random.uniform(-1, 1) * 0.02 * a, random.uniform(-1, 1) * 0.01 * a, 0.4 + random.uniform(-1, 1) * 0.012 * a))
    keys_lin(hL); keys_lin(hR); keys_lin(giro)
    # ---------- ESTALO (F_POP): inteira some, as duas pecas aparecem, as maos recuam com o tranco
    key_hide([ins], [(1, False), (F_POP, True)])
    key_hide([mai, men], [(1, True), (F_POP, False)])
    aF = base_ang(F_POP - 1)
    K(hL, "location", F_POP - 1, (0, 0, -0.4)); K(hR, "location", F_POP - 1, (0, 0, -0.4))
    K(hL, "rotation_euler", F_POP, (0, math.radians(-aF - 10), math.radians(4)))
    K(hR, "rotation_euler", F_POP, (0, math.radians(aF + 14), math.radians(-6)))
    K(hL, "location", F_POP + 3, (-0.3, -0.06, -0.36)); K(hR, "location", F_POP + 3, (0.38, -0.04, -0.45))
    K(hL, "location", F_POP + 7, (-0.26, -0.08, -0.34))
    # vitoria: a mao da esquerda (pedaco MAIOR, com a juncao) sobe e mostra o pedaco contra a arvore; a outra sai por baixo
    sc.frame_set(F_POP); bpy.context.view_layer.update()
    gmw_inv = giro.matrix_world.inverted()
    PP = BP + Vector((0.06, 0.02, 0.13))                    # onde o pedaco maior para (mundo)
    PP_l = gmw_inv @ PP
    K(hL, "location", F_POP + 12, tuple(Vector((-0.26, -0.08, -0.34)).lerp(PP_l, 0.35)))
    K(hL, "location", fa5, tuple(PP_l))
    K(hL, "location", N, tuple(PP_l + Vector((0.0, -0.05, 0.08))))
    K(hL, "rotation_euler", F_POP + 12, (math.radians(8), math.radians(-24), math.radians(10)))
    K(hL, "rotation_euler", fa5, (math.radians(4), math.radians(-6), math.radians(-6)))
    K(hL, "rotation_euler", N, (math.radians(2), math.radians(4), math.radians(-14)))
    K(hR, "location", F_POP + 16, (1.4, -0.2, -1.6)); K(hR, "location", F_POP + 34, (2.6, -0.4, -4.0))
    K(hR, "rotation_euler", F_POP + 34, (0, math.radians(aF + 30), math.radians(-20)))
    for h in (hL, hR):
        for fc in M.fcurves(h):
            for k in fc.keyframe_points:
                if k.co.x >= F_POP:
                    k.interpolation = 'BEZIER'
    K(giro, "location", F_POP, (0, 0, 0.4))
    vis_window([mD], 1, F_POP + 34)
    # "osso de dinossauro": brilho ciano de leve sobre o marfim antes de quebrar; o pedaco maior brilha de leve no final
    furcula_keys(fm, [(1, 0.0), (f_os3 - 4, 0.0), (f_os3 + 4, 6.0), (F_POP, 7.0), (F_POP + 4, 0.0), (fa5 - 6, 0.0), (fa5 + 4, 2.5), (N, 2.0)])
    key_val(X.fsock(fm, "EXTRA"), [(1, 0.0), (f_os3 - 4, 0.0), (f_os3 + 4, 0.25), (F_POP, 0.3), (F_POP + 6, 0.0), (fa5 - 6, 0.0), (fa5 + 4, 0.06)])
    nt_interp(fm.node_tree)
    # lascas
    sc.frame_set(F_POP); bpy.context.view_layer.update()
    pb = giro.matrix_world @ (Vector((0, 0, -0.4)) + X._arm_path(0.2, 1))
    lasca_m = M.pbr("lasca_osso", (0.86, 0.78, 0.6), (0.7, 0.6, 0.44), rough=0.45, nscale=60)
    random.seed(9)
    for i in range(14):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(0, 0, 0))
        o = bpy.context.object; o.name = "lasca"
        for v in o.data.vertices:
            v.co *= random.uniform(0.6, 1.3)
        o.scale = (random.uniform(0.6, 1.4) * 0.0014, random.uniform(0.4, 0.9) * 0.0014, random.uniform(1.0, 2.2) * 0.0014)
        M.setmat(o, lasca_m)
        v0 = Vector((random.uniform(-1, 1), random.uniform(-0.8, 0.3), random.uniform(0.3, 1.2))).normalized() * random.uniform(0.4, 0.8)
        K(o, "location", F_POP - 1, tuple(pb))
        landed = None
        for k_ in range(0, 26, 2):
            tt = k_ / 30.0
            p = pb + v0 * tt + Vector((0, 0, -4.9)) * tt * tt
            if p.z < Z + 0.001:
                p.z = Z + 0.001
                landed = landed or p.copy(); p = landed
            K(o, "location", F_POP + k_, tuple(p))
            K(o, "rotation_euler", F_POP + k_, (k_ * random.uniform(0.3, 0.8), k_ * random.uniform(0.2, 0.6), 0))
        key_hide([o], [(1, True), (F_POP, False), (F_POP + 40, True)])
        o.visible_shadow = False
    fl_m = M.emis("estalo", (1.0, 0.92, 0.75), 8.0)
    fl = M.sph("estalo_flash", 0.003, tuple(pb), fl_m, seg=16, rings=8); fl.visible_shadow = False
    K(fl, "scale", 1, (0.001,) * 3); K(fl, "scale", F_POP - 1, (0.001,) * 3); K(fl, "scale", F_POP, (1.0,) * 3); K(fl, "scale", F_POP + 2, (2.0,) * 3); K(fl, "scale", F_POP + 5, (0.001,) * 3)
    # ---------- luz: chave quente nas maos e no osso (da vela/lustre), recorte frio da janela
    lk = M.light('AREA', tuple(BP + Vector((0.28, -0.42, 0.32))), tuple(BP + Vector((0, 0, 0.05))), 7.0, (1.0, 0.8, 0.6), size=0.35)
    lr = M.light('AREA', tuple(BP + Vector((-0.35, 0.35, 0.25))), tuple(BP + Vector((0, 0, 0.05))), 4.0, (0.6, 0.75, 1.0), size=0.3)
    lf = M.light('AREA', tuple(BP + Vector((-0.2, -0.5, 0.0))), tuple(BP + Vector((0, 0, 0.05))), 1.6, (1.0, 0.7, 0.5), size=0.4)
    # ---------- a Pipo (espiga com a pena), desfocada ao fundo na mesa a direita; estoura no MESMO quadro do estalo
    ns = M._load_pipo()
    pipo = ns["pipo"]; FK = ns["FK"]
    PX, PY = 0.10, -0.06
    ns["pipo_place"](PX, PY, 0.085)
    pipo.location.z = Z
    pipo.rotation_euler = (0, 0, math.radians(-25))
    ns["set_face"](FK, 1, **ns["SIGN"], look=(-30, -4))
    ns["set_face"](FK, f_px, lid=-10, brow=(14, 0.3), browL=(-16, 0.33), look=(-36, -8))
    ns["blink"](FK, fa2 + 20, ns["TIRED"])
    ns["pipo_tension"](F_POP - 22, F_POP)
    ns["pipo_pop"](F_POP, burst=True, size=0.78)
    for o in list(pipo.children_recursive):
        if o.type == 'MESH' and o.data.materials and o.data.materials[0] and o.data.materials[0].name.startswith(("ring", "ray")):
            D.objects.remove(o, do_unlink=True)
    pm = M.feather_mat("pena_pipo", [(0.55, 0.22, 0.08), (0.7, 0.32, 0.1)], tip=(0.12, 0.05, 0.02))
    pme = M.feather_mesh("pena_pipo", 1.0, 0.38, 0.1)
    pena = M.link(D.objects.new("pena_pipo", pme)); M.setmat(pena, pm)
    pena.parent = ns["kern"]; pena.location = (0.06, 0.02, 0.46); pena.rotation_euler = (math.radians(-25), math.radians(35), math.radians(20)); pena.scale = (0.32,) * 3
    pipo_foco = M.empty("foco_pipo", (0, 0, 0.6), pipo)
    vis_window([pipo], fa2, N)
    # ---------- cameras
    C = Cam(cam)
    oc = BP + Vector((0, 0, 0.055))
    shx, shy = shift_for(*P_STAR)

    def p1(u, fr):        # close das duas maos puxando; push-in
        k = ease(u)
        loc = oc + Vector((0.03, -0.50, 0.05)).lerp(Vector((0.02, -0.42, 0.04)), k)
        return dict(loc=loc, tgt=oc, lens=35, sx=shx, sy=shy, fd=(loc - oc).length, fs=2.8)
    C.shot(S["P1_ceia"], p1)

    def b2(u, fr):        # de volta a ceia, outro angulo (esquerda), a Pipo ao fundo
        k = ease(u)
        loc = oc + Vector((-0.10, -0.46, 0.08)).lerp(Vector((-0.08, -0.40, 0.065)), k)
        return dict(loc=loc, tgt=oc + Vector((0.01, 0, 0)), lens=38, sx=shx, sy=shy, fd=(loc - oc).length, fs=2.6)
    C.shot(S["B2_mesa"], b2)

    def b3(u, fr):        # tensao: close que aperta ate o estalo
        k = ease(u)
        loc = oc + Vector((0.04, -0.40, 0.03)).lerp(Vector((0.03, -0.31, 0.025)), k)
        return dict(loc=loc, tgt=oc, lens=40, sx=shx, sy=shy, fd=(loc - oc).length, fs=3.2)
    C.shot(S["B3_tensao"], b3)
    sc.frame_set(F_POP); bpy.context.view_layer.update()

    def piece_c():
        return hL.matrix_world.translation.copy() + Vector((0, 0, 0.055))

    def b4(u, fr):        # o pedaco maior sobe contra a arvore e as luzes (camera baixa, olhando para cima e para a direita)
        k = ease(u)
        pc = piece_c()
        loc = oc + Vector((0.0, -0.58, 0.05)).lerp(Vector((-0.13, -0.38, 0.0)), ease(min(1, u * 1.3)))
        tgt = oc.lerp(pc, ease(min(1, u * 1.6)))
        return dict(loc=loc, tgt=tgt, lens=40, sx=shx, sy=shy, fd=(loc - pc).length, fs=2.4)
    C.shot(S["B4_vitoria"], b4, track=True)

    def b5(u, fr):        # loop: a mao vencedora no ponto do V do quadro 1, push-in leve ate o fim
        k = ease(u)
        pc = piece_c()
        loc = pc + Vector((-0.18, -0.44, -0.10)).lerp(Vector((-0.16, -0.38, -0.085)), k)
        return dict(loc=loc, tgt=pc + Vector((0, 0, 0.045)), lens=40, sx=shx, sy=shy, fd=(loc - pc).length, fs=2.4)
    C.shot(S["B5_loop"], b5, track=True)
    C.done()
    for fc in M.fcurves(cam):
        if fc.data_path == "location":
            mo = fc.modifiers.new('NOISE'); mo.strength = 0.005; mo.scale = 1.2
            mo.use_restricted_range = True; mo.frame_start = F_POP; mo.frame_end = F_POP + 14; mo.blend_in = 0; mo.blend_out = 10
    cam.data.clip_start = 0.005
    # ---------- QA
    qa_key("ossinho", root); qa_key("mao_esq", mE); qa_key("mao_dir", mD); qa_key("frango", cz["frango"]["root"]); qa_key("pipo", pipo)
    qa_touch("ossinho", "mao_esq"); qa_touch("ossinho", "mao_dir")
    for a_ in ("ossinho", "mao_esq", "mao_dir"):
        qa_tela(a_, "frango"); qa_tela(a_, "pipo")
    qa_tela("mao_esq", "mao_dir"); qa_tela("pipo", "frango")
    qa_foco("P1_ceia", giro); qa_foco("B2_mesa", giro); qa_foco("B3_tensao", giro, fb=F_POP - 1)
    qa_foco("B2_mesa", pipo_foco); qa_foco("B3_tensao", pipo_foco)
    pfoc = M.empty("foco_pedaco", tuple(X._arm_path(1.0, -1) * 0.55), hL)
    qa_foco("B5_loop", pfoc)
    return dict(cam=cam, FB=FB, pipo=pipo, maos=(mE, mD))


# ================================================================ MUNDO A: cinzas (A1-A3)
def furcula_no_alto_do_peito(arm, sc_world, size, pose_fr=14):
    """matriz de mundo da raiz do V: pontas na base do pescoco, entre os ombros (osso Shoulders -> Neck), na frente do peito"""
    bpy.context.view_layer.update()
    pb = arm.pose.bones["Shoulders"]
    head = arm.matrix_world @ pb.head; tail = arm.matrix_world @ pb.tail
    fwd = (tail - head); fwd.z = 0; fwd.normalize()
    return head, tail, fwd


def build_A():
    cz = M.mundo_cinzas()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    sc.cycles.transparent_max_bounces = 10
    cam = cz["cam"]
    for o in [cz["rex"]["root"]] + list(cz["rex"]["root"].children_recursive):
        D.objects.remove(o, do_unlink=True)
    for c in list(cam.constraints):
        cam.constraints.remove(c)
    cam.animation_data_clear(); cam.parent = None
    S = SH
    fa1, fa2, fa3, fb3 = S["A1_rugido"]["f0"], S["A2_peito"]["f0"], S["A3_close"]["f0"], S["A3_close"]["f1"]
    R = X.carrega_rex("qrex", (0, 0.5, 0), 0.0, 0.42)
    arm, rmesh = R["arm"], R["mesh"]
    A = R["acts"]
    X.set_action(arm, A["TRex_Attack"]); sc.frame_set(14)
    head, tail, fwd = furcula_no_alto_do_peito(arm, sc, 0.78)
    # o V: juncao (raiz) logo abaixo da base do pescoco, na frente do peito; pontas sobem ate os ombros
    VS = 0.62
    vroot = tail.lerp(head, 0.18) + fwd * 0.55 + Vector((0, 0, -1.05))
    mk = R["mask"]
    X.prende_no_osso(mk, arm, "Shoulders", Matrix.LocRotScale(vroot + Vector((0, 0, 0.35)), None, Vector((1.05, 1.0, 0.95))))
    fm_rex = X.furcula_mat("furcula_rex", glow=1.0)
    FR = X.furcula("furc_rex", None, (0, 0, 0), (0, 0, 0), 1.0, mat=fm_rex)
    yaw = math.atan2(-fwd.x, fwd.y) if fwd.length else 0.0
    X.prende_no_osso(FR["root"], arm, "Shoulders", Matrix.LocRotScale(vroot, Euler((math.radians(-14), 0, yaw + math.pi)).to_quaternion(), Vector((VS,) * 3)))
    arm.animation_data.action = None
    X.nla_track(arm, [(A["TRex_Idle"], -40, (0, 60), 1.0, 20)], "base")
    tr = X.nla_track(arm, [(A["TRex_Attack"], fa1 - 8, (5, 11), 1.0, 1),
                           (A["TRex_Attack"], fa1 - 2, (11, 13.5), 14.0, 1),
                           (A["TRex_Attack"], fa1 + 33, (13.5, 28), 1.4, 1)], "rugido")
    for st in tr.strips:
        st.extrapolation = 'NOTHING'
    tr.strips[0].blend_in = 4
    tr.strips[2].blend_out = 8
    halo_r, halo_s = X.halo("furc_rex_halo", FR["giro"], (0, 0.18, 0.05), 0.75, strength=0.0)
    grp = R["grp"]
    # varredura do raio-x (do pescoco para baixo) no "tinha igual"; o V acende no "alto" e pulsa no "peito"
    fb0, fbx = f(wt("igual")) + 2, f(wt("peito")) + 6
    key_val(X.gsock(grp, "BAND"), [(1, 1.25), (fb0, 1.25), (fbx, -1.15)])
    key_val(X.gsock(grp, "ON"), [(1, 0.0), (fb0 - 1, 0.0), (fb0, 1.0)])
    key_val(X.gsock(grp, "LINE"), [(1, 0.0), (fb0 - 1, 0.0), (fb0 + 2, 1.0), (fbx - 2, 1.0), (fbx + 3, 0.0)])
    nt_interp(grp, 'LINEAR')
    for fc in M.fcurves_nt(grp):
        for k in fc.keyframe_points:
            if int(k.co.x) == fb0 - 1:
                k.interpolation = 'CONSTANT'
    sheet_m = M.halo_mat("lamina_raiox", X.CIANO_B, 1.6, power=1.4)
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1, fill_type='NGON', location=(0, 0, 0))
    sheet = bpy.context.object; sheet.name = "lamina_raiox"; M.setmat(sheet, sheet_m); sheet.parent = mk
    sheet.visible_shadow = False; sheet.visible_diffuse = False; sheet.visible_glossy = False
    for fr, z in ((fb0, 1.25), (fbx, -1.15)):
        K(sheet, "location", fr, (0, 0, z))
    keys_lin(sheet)
    key_scale_vis(sheet, [(1, False), (fb0, True), (fbx + 3, False)], base=(1.1, 1.1, 1))
    f_alto, f_peito = f(wt("alto")), f(wt("peito"))
    f_duas, f_clav, f_grud, f_v = f(wt("duas")), f(wt("clavículas")), f(wt("grudadas")), f(wt("v"))
    # A2: V inteiro aceso; A3 (corte): apaga e acende por metades (duas / claviculas), pulso na juncao (grudadas, V)
    kv_l = [(1, 0.0), (f_alto - 4, 0.0), (f_alto + 2, 14.0), (f_peito - 2, 9.0), (f_peito + 2, 18.0), (f_peito + 10, 9.0), (fa3 - 1, 9.0), (fa3, 1.2),
            (f_duas - 1, 1.2), (f_duas + 3, 16.0), (f_duas + 10, 10.0)]
    kv_r = [(1, 0.0), (f_alto - 4, 0.0), (f_alto + 2, 14.0), (f_peito - 2, 9.0), (f_peito + 2, 18.0), (f_peito + 10, 9.0), (fa3 - 1, 9.0), (fa3, 1.2),
            (f_clav - 1, 1.2), (f_clav + 3, 16.0), (f_clav + 10, 10.0)]
    for b in (f_grud, f_v):
        kv_l += [(b - 2, 10.0), (b + 2, 20.0), (b + 10, 10.0)]
        kv_r += [(b - 2, 10.0), (b + 2, 20.0), (b + 10, 10.0)]
    furcula_keys(fm_rex, kv_l, "EL"); furcula_keys(fm_rex, kv_r, "ER")
    for fc in M.fcurves_nt(fm_rex.node_tree):
        for k in fc.keyframe_points:
            if int(k.co.x) == fa3 - 1:
                k.interpolation = 'CONSTANT'
    key_val(halo_s, [(1, 0.0), (f_alto - 4, 0.0), (f_alto + 4, 0.55), (f_peito + 2, 0.9), (f_peito + 10, 0.5), (f_grud - 2, 0.5), (f_grud + 2, 1.0), (f_grud + 10, 0.55),
                     (f_v - 2, 0.55), (f_v + 2, 1.0), (f_v + 10, 0.55)])
    nt_interp(halo_r.data.materials[0].node_tree)
    # pulso na juncao: esfera de luz no ponto de encontro das duas claviculas ("grudadas")
    jm = X.halo_add_mat("juncao_pulso", X.CIANO_B, 1.0, power=1.6)
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1, fill_type='NGON', location=(0, 0, 0))
    jun = bpy.context.object; jun.name = "juncao_pulso"; M.setmat(jun, jm); jun.parent = FR["giro"]; jun.location = (0, -0.08, -0.36)
    jun.rotation_euler = (math.radians(90), 0, 0); jun.visible_shadow = False
    for b in (f_grud, f_v):
        K(jun, "scale", b - 2, (0.001,) * 3); K(jun, "scale", b + 2, (0.22,) * 3); K(jun, "scale", b + 12, (0.001,) * 3)
    K(jun, "scale", 1, (0.001,) * 3)
    K(FR["giro"], "rotation_euler", fa3, (0, 0, math.radians(-16))); K(FR["giro"], "rotation_euler", fb3, (0, 0, math.radians(16)))
    for b in (f_grud, f_v):
        K(FR["giro"], "scale", b - 3, (1, 1, 1)); K(FR["giro"], "scale", b + 2, (1.08,) * 3); K(FR["giro"], "scale", b + 10, (1, 1, 1))
    # luz do rex (legivel em 0,5 s): chave quente de frente-lado e recorte de fogo; a cena das cinzas continua igual
    sc.frame_set(fa2); bpy.context.view_layer.update()
    fc0 = FR["giro"].matrix_world.translation.copy()
    M.light('AREA', tuple(fc0 + Vector((4.5, -6.5, 2.5))), tuple(fc0 + Vector((0, 0, 0.6))), 2600, (1.0, 0.72, 0.48), size=4.0)
    M.light('AREA', tuple(fc0 + Vector((-5.0, 3.0, 4.0))), tuple(fc0), 4000, (1.0, 0.4, 0.12), size=4.0)
    M.light('AREA', tuple(fc0 + Vector((-3.0, -7.0, -1.0))), tuple(fc0), 700, (0.55, 0.7, 1.0), size=5.0)
    # ---------- camera
    C = Cam(cam)
    furc_c = lambda: FR["giro"].matrix_world.translation.copy()

    def a1(u, fr):        # rugido aberto: o rex inteiro de frente/3-4, push-in
        k = ease(u)
        loc = Vector((3.4, -13.2, 2.4)).lerp(Vector((2.9, -12.0, 2.5)), k) + shake(fr, 0.03 * (1 - 0.6 * k), 1)
        return dict(loc=loc, tgt=Vector((0.0, -3.4, 3.6)), lens=24, sy=-0.04, fd=(loc - Vector((0, -3.6, 4.2))).length, fs=5.0)
    C.shot(S["A1_rugido"], a1)

    def a2(u, fr):        # cabeca e peito, 3/4; a faixa desce e o V acende no alto do peito
        k = ease(u)
        fc_ = furc_c()
        ang = math.radians(-62 + 10 * k)
        loc = fc_ + Vector((math.cos(ang) * 6.2, math.sin(ang) * 6.2, 0.9 - 0.3 * k))
        tgt = fc_ + Vector((0, 0, 0.75))
        return dict(loc=loc, tgt=tgt, lens=28, sy=-0.02, fd=(loc - fc_).length, fs=5.0)
    C.shot(S["A2_peito"], a2, track=True)
    shx, shy = shift_for(*P_STAR)

    def a3(u, fr):        # close no V
        k = ease(u)
        fc_ = furc_c()
        d_ = 3.4 - 0.6 * k
        dirv = Vector((0.35, -1.0, 0.12)).normalized()
        loc = fc_ + dirv * d_ + shake(fr, 0.004, 3)
        return dict(loc=loc, tgt=fc_, lens=38, sx=shx, sy=shy, fd=d_, fs=4.5)
    C.shot(S["A3_close"], a3, track=True)
    C.done()
    cam.data.clip_start = 0.01
    qa_key("rex", R["root"])
    for sn in ("A2_peito", "A3_close"):
        qa_foco(sn, FR["giro"])
    cabeca = M.empty("rex_cabeca", (0, 0, 0)); sc.frame_set(fa1 + 10)
    X.prende_no_osso(cabeca, arm, "Head", Matrix.Translation(arm.matrix_world @ arm.pose.bones["Head"].tail))
    qa_foco("A1_rugido", cabeca)
    return dict(cam=cam, rex=R, FR=FR)


# ================================================================ MUNDO Q: quintal ao sol (Q1)
def build_Q():
    qt = M.mundo_quintal()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    cam = qt["cam"]; g = qt["chao"]; S = SH
    fa, fb = S["Q1_quintal"]["f0"], S["Q1_quintal"]["f1"]
    # a galinha procedural sai; entra a Kelgar (a mesma do raio-x dos primos), ciscando no milho
    gr = qt["galinha"]["root"]
    for o in [gr] + list(gr.children_recursive):
        D.objects.remove(o, do_unlink=True)
    for c in list(cam.constraints):
        cam.constraints.remove(c)
    cam.animation_data_clear(); cam.parent = None
    GX, GY = 0.35, 0.05
    gz0 = M.ground_z(g, GX, GY)
    GL = X.carrega_galinha("gal", (GX, GY, gz0 - 0.004), math.radians(-18), 0.45, xray=False)
    garm = GL["arm"]; acts = GL["acts"]
    garm.animation_data_clear()
    st = []
    t0 = fa - 30
    seq = [("Idle1", (1, 35)), ("Pecking1", None), ("Idle2", None), ("Pecking2", None), ("Idle1", (1, 35))]
    for nm, rg in seq:
        a = acts.get(nm)
        if not a:
            continue
        r_ = rg or tuple(a.frame_range)
        st.append((a, t0, r_, 1.0, 1)); t0 += int(r_[1] - r_[0]) + 1
    trk = X.nla_track(garm, st, "cisca")
    for s_ in trk.strips:
        s_.blend_in = 3; s_.blend_out = 3; s_.extrapolation = 'HOLD_FORWARD'
    cab = M.empty("gal_cabeca", (0, 0, 0)); sc.frame_set(fa)
    X.prende_no_osso(cab, garm, "Head", Matrix.Translation(garm.matrix_world @ garm.pose.bones["Head"].tail))
    # luz de preenchimento quente na galinha (o sol do ep003 vem de tras)
    gp = Vector((GX, GY, gz0 + 0.25))
    M.light('AREA', tuple(gp + Vector((0.7, -1.1, 0.6))), tuple(gp), 18, (1.0, 0.82, 0.62), size=0.8)
    # camera: baixa, de frente, galinha no meio-baixo da tela; terco de cima livre para o card
    C = Cam(cam)

    def q1(u, fr):
        k = ease(u)
        loc = Vector((GX + 0.31, GY - 1.44, 0.36)).lerp(Vector((GX + 0.20, GY - 1.24, 0.33)), k)
        tgt = gp + Vector((0, 0, 0.06))
        return dict(loc=loc, tgt=tgt, lens=32, sy=0.08, fd=(loc - gp).length, fs=3.5)
    C.shot(S["Q1_quintal"], q1)
    C.done()
    cam.data.clip_start = 0.01
    # card do comentario: so o @ e o texto (sem data, sem curtidas); terco de cima
    CD = X.card_comentario(cam)
    for t_ in list(CD["textos"]):
        if t_.data.body.startswith("há"):
            D.objects.remove(t_, do_unlink=True)
    ST = X.carimbo("ACERTOU!", cam)
    sc.frame_set(fa)
    d_ = 0.5
    p_, hw = cam_local(32, d_, 0.5, 0.275, cam.data.shift_x, cam.data.shift_y)
    CD["root"].location = p_
    base = 0.74 * 2 * hw
    f_card = fa + 1; f_ac = f(wt("acertou")); fn = f(wt("niko"))
    K(CD["root"], "scale", 1, (0.0005,) * 3); K(CD["root"], "scale", f_card - 1, (0.0005,) * 3)
    K(CD["root"], "scale", f_card + 4, (base * 1.1,) * 3); K(CD["root"], "scale", f_card + 9, (base,) * 3); K(CD["root"], "scale", fb, (base * 1.03,) * 3)
    K(CD["root"], "rotation_euler", f_card, (0, math.radians(-8), math.radians(2))); K(CD["root"], "rotation_euler", f_card + 10, (0, math.radians(-3), 0))
    av = CD["avatar"]
    K(av, "scale", fn - 3, (1, 1, 1)); K(av, "scale", fn + 2, (1.3, 1.3, 1.3)); K(av, "scale", fn + 8, (1, 1, 1))
    p6, hw6 = cam_local(32, d_ * 0.96, 0.67, 0.345, cam.data.shift_x, cam.data.shift_y)
    ST["root"].location = p6
    s6 = 0.36 * 2 * hw6
    K(ST["root"], "scale", 1, (0.0005,) * 3); K(ST["root"], "scale", f_ac - 1, (0.0005,) * 3)
    K(ST["root"], "scale", f_ac, (s6 * 1.5,) * 3); K(ST["root"], "scale", f_ac + 3, (s6 * 0.88,) * 3); K(ST["root"], "scale", f_ac + 7, (s6,) * 3)
    for fc in M.fcurves(ST["root"]) + M.fcurves(CD["root"]):
        for k in fc.keyframe_points:
            if int(k.co.x) in (f_ac - 1, f_card - 1):
                k.interpolation = 'CONSTANT'
    K(ST["root"], "rotation_euler", f_ac, (0, 0, math.radians(-17))); K(ST["root"], "rotation_euler", f_ac + 6, (0, 0, math.radians(-9)))
    for o in [CD["root"], ST["root"]] + list(CD["root"].children_recursive) + list(ST["root"].children_recursive):
        o.visible_shadow = False
    qa_key("galinha", GL["root"]); qa_key("card", CD["root"]); qa_key("carimbo", ST["root"])
    qa_touch("card", "carimbo")
    qa_foco("Q1_quintal", cab)
    qa_inteiro("Q1_quintal", "galinha", "card")
    return dict(cam=cam, gal=GL, card=CD)


# ================================================================ MUNDO C: primos (C1-C2), tela dividida iluminada
def build_C():
    s = M.reset(4)
    M.bloom(s, threshold=0.9, size=0.7, strength=0.6)
    s.cycles.transparent_max_bounces = 10
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    nt = s.world.node_tree; nt.nodes["Background"].inputs[0].default_value = (0.02, 0.02, 0.025, 1)
    S = SH
    fa, fb = S["C1_primos"]["f0"], S["C2_herdaram"]["f1"]
    fa2 = S["C2_herdaram"]["f0"]
    LENS = 35.0; Dd = 0.42
    W_, H_ = sc.render.resolution_x, sc.render.resolution_y
    half_w = Dd * 18.0 / LENS * W_ / H_
    a = half_w * 0.5
    zV = (0.5 - P_STAR[1]) * 2 * Dd * 18.0 / LENS * 0.0          # o V no centro vertical do quadro (shift faz o resto)
    shx, shy = shift_for(0.5, P_STAR[1])
    Lp, Rp = Vector((-a, Dd, 0.0)), Vector((a, Dd, 0.0))
    VS = 0.055                                                       # tamanho dos dois V na tela (iguais)
    # ---------- esquerda: o T. rex em escala de maquete, raio-x, V no alto do peito
    k = VS / 0.62
    R = X.carrega_rex("crex", (0, 0, 0), math.radians(-28), 0.42 * k)
    arm = R["arm"]
    X.set_action(arm, R["acts"]["TRex_Attack"]); sc.frame_set(14)
    head, tail, fwd = furcula_no_alto_do_peito(arm, sc, 0.0)
    sk = 0.42 * k
    vroot = tail.lerp(head, 0.18) + fwd * 0.55 * k + Vector((0, 0, -1.05 * k))
    X.prende_no_osso(R["mask"], arm, "Shoulders", Matrix.LocRotScale(vroot + Vector((0, 0, 0.35 * k)), None, Vector((1.05, 1.0, 0.95)) * k))
    fm_r = X.furcula_mat("furcula_primo_rex", glow=1.0)
    FR = X.furcula("primo_furc_rex", None, (0, 0, 0), (0, 0, 0), 1.0, mat=fm_r)
    yaw = math.atan2(-fwd.x, fwd.y)
    X.prende_no_osso(FR["root"], arm, "Shoulders", Matrix.LocRotScale(vroot, Euler((math.radians(-14), 0, yaw + math.pi)).to_quaternion(), Vector((VS,) * 3)))
    arm.animation_data.action = None
    X.nla_track(arm, [(R["acts"]["TRex_Idle"], fa - 30, (0, 60), 1.0, 6)], "base")
    for m_ in R["mats"].values():
        X.corta_x(m_, keep_neg=True)
    g = R["grp"]
    X.gsock(g, "ON").default_value = 1.0; X.gsock(g, "BAND").default_value = -2.0; X.gsock(g, "LINE").default_value = 0.0
    sc.frame_set((fa + fa2) // 2); bpy.context.view_layer.update()
    R["root"].location = R["root"].location + (Lp - FR["giro"].matrix_world.translation)
    # ---------- direita: a galinha Kelgar, raio-x, V no alto do peito (base do pescoco)
    GH = 0.42
    GL = X.carrega_galinha("cgal", (0, 0, 0), math.radians(24), GH)
    garm = GL["arm"]
    X.set_action(garm, GL["acts"]["Idle1"]); sc.frame_set(8); bpy.context.view_layer.update()
    pbk = garm.pose.bones["Backbone"]
    bh = garm.matrix_world @ pbk.head; bt = garm.matrix_world @ pbk.tail
    gfwd = bt - bh; gfwd.z = 0; gfwd.normalize()
    u = GH / 12.65
    groot = bt + gfwd * 0.55 * u + Vector((0, 0, -1.9 * u))
    X.prende_no_osso(GL["mask"], garm, "Backbone", Matrix.LocRotScale(groot + Vector((0, 0, 0.6 * u)), None, Vector((2.6 * u, 2.6 * u, 2.4 * u))))
    fm_g = X.furcula_mat("furcula_primo_gal", glow=1.0)
    gyaw = math.atan2(-gfwd.x, gfwd.y)
    FG = X.furcula("primo_furc_gal", None, (0, 0, 0), (0, 0, 0), 1.0, mat=fm_g)
    gvs = 2.2 * u
    X.prende_no_osso(FG["root"], garm, "Backbone", Matrix.LocRotScale(groot, Euler((math.radians(-10), 0, gyaw + math.pi)).to_quaternion(), Vector((gvs,) * 3)))
    garm.animation_data.action = None
    ida = []
    for i in range(6):
        ida.append((GL["acts"]["Idle1"], fa - 20 + i * 35, (1, 35), 1.0, 1))
    trg = X.nla_track(garm, ida, "base")
    for i, st in enumerate(trg.strips):
        st.use_reverse = bool(i % 2)
    gg = GL["grp"]
    X.gsock(gg, "ON").default_value = 1.0; X.gsock(gg, "BAND").default_value = -2.0; X.gsock(gg, "LINE").default_value = 0.0
    X.corta_x(GL["mat"], keep_neg=False)
    sc.frame_set((fa + fa2) // 2); bpy.context.view_layer.update()
    GL["root"].location = GL["root"].location + (Rp - FG["giro"].matrix_world.translation)
    bpy.context.view_layer.update()
    # ---------- fundos e luz (os dois lados claros)
    fum = X.halo_add_mat("primo_brasa_fundo", (1.0, 0.32, 0.06), 1.4, power=1.2)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-0.3, Dd + 0.6, 0.0), rotation=(math.radians(90), 0, 0))
    bgL = bpy.context.object; bgL.name = "fundo_cinzas"; bgL.scale = (0.62, 1.2, 1); M.setmat(bgL, fum); bgL.visible_shadow = False
    ceu = M.pbr("primo_ceu", (0.35, 0.6, 0.95), (0.55, 0.75, 1.0), rough=1.0, nscale=1.5)
    em_ = M.emis("primo_ceu_e", (0.45, 0.68, 1.0), 1.3)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0.3, Dd + 0.6, 0.0), rotation=(math.radians(90), 0, 0))
    bgR = bpy.context.object; bgR.name = "fundo_ceu"; bgR.scale = (0.62, 1.2, 1); M.setmat(bgR, em_); bgR.visible_shadow = False
    terra = M.pbr("primo_terra", (0.36, 0.2, 0.1), (0.5, 0.3, 0.15), rough=0.92, nscale=40)
    am = M.pbr("primo_cinza_chao", (0.18, 0.12, 0.1), (0.3, 0.2, 0.15), rough=0.9, nscale=40)
    sc.frame_set(fa); bpy.context.view_layer.update()
    gz = min((GL["root"].matrix_world @ Vector(c)).z for c in GL["mesh"].bound_box) if False else None
    M.light('AREA', (-0.25, Dd - 0.35, 0.15), tuple(Lp), 4.0, (1.0, 0.72, 0.5), size=0.3)
    M.light('AREA', (-0.45, Dd + 0.3, 0.2), tuple(Lp), 3.0, (1.0, 0.4, 0.12), size=0.25)
    M.light('AREA', (0.3, Dd - 0.35, 0.2), tuple(Rp), 3.5, (1.0, 0.9, 0.78), size=0.3)
    M.light('AREA', (0.45, Dd + 0.25, 0.15), tuple(Rp), 2.0, (0.7, 0.85, 1.0), size=0.25)
    sm_m = M.emis("primo_costura", (1.0, 0.92, 0.75), 2.5)
    cost = M.box("primo_costura", (0.0005, 0.0004, 0.6), (0, Dd - 0.05, 0.0), sm_m, bev=0.0); cost.visible_shadow = False
    # ---------- os V: galinha acende no "galinha"/"prima", rex no "T. rex"; no "herdaram" voam ao centro e encaixam
    f_gal, f_prima, f_trex, f_her, f_osso = f(wt("galinha")), f(wt("prima")), f(wt("t", 1)), f(wt("herdaram")), f(wt("osso"))
    furcula_keys(fm_g, [(1, 3.0), (fa, 3.0), (f_prima - 2, 3.0), (f_prima + 3, 15.0), (f_prima + 12, 10.0)])
    furcula_keys(fm_r, [(1, 3.0), (fa, 3.0), (f_trex - 2, 3.0), (f_trex + 3, 15.0), (f_trex + 12, 10.0)])
    hr, hrs = X.halo("primo_halo_rex", FR["giro"], (0, 0.18, 0.05), 0.75, strength=0.4)
    hg, hgs = X.halo("primo_halo_gal", FG["giro"], (0, 0.18, 0.05), 0.75, strength=0.4)
    # copias livres dos V (as presas ao osso somem no "herdaram")
    fv = f_her - 2
    sc.frame_set(fv); bpy.context.view_layer.update()
    PC = Vector((0, Dd - 0.06, 0.0))
    frees = []
    for src, mat_, nm, side in ((FR, fm_r, "voa_rex", -1), (FG, fm_g, "voa_gal", 1)):
        mw = src["root"].matrix_world.copy()
        F2 = X.furcula(nm, None, (0, 0, 0), (0, 0, 0), 1.0, mat=X.furcula_mat(nm + "_m", glow=1.0))
        for k_ in ("EL", "ER"):
            X.fsock(F2["mat"], k_).default_value = 10.0
        r_ = F2["root"]
        r_.matrix_world = mw
        bpy.context.view_layer.update()
        l0, q0, s0 = mw.decompose()
        e0 = q0.to_euler()
        lt = PC - Vector((0, 0, 0.4 * VS))
        K(r_, "location", fv, tuple(l0)); K(r_, "rotation_euler", fv, tuple(e0)); K(r_, "scale", fv, tuple(s0))
        K(r_, "location", fv + 12, tuple(lt + Vector((side * 0.004, 0, 0.0)))); K(r_, "rotation_euler", fv + 12, (math.radians(90 - 8), 0, 0)); K(r_, "scale", fv + 12, (VS,) * 3)
        K(r_, "location", fv + 16, tuple(lt)); K(r_, "rotation_euler", fv + 16, (math.radians(90 - 8), 0, 0))
        K(r_, "location", fb, tuple(lt)); K(r_, "rotation_euler", fb, (math.radians(90 - 8), 0, math.radians(8)))
        key_hide([F2["inteira"]], [(1, True), (fv, False)])
        key_hide([src["inteira"]], [(1, False), (fv, True)])
        key_val(X.fsock(F2["mat"], "EL"), [(fv + 14, 10.0), (fv + 18, 26.0), (fv + 30, 12.0), (f_osso - 2, 12.0), (f_osso + 3, 22.0), (f_osso + 14, 12.0)])
        key_val(X.fsock(F2["mat"], "ER"), [(fv + 14, 10.0), (fv + 18, 26.0), (fv + 30, 12.0), (f_osso - 2, 12.0), (f_osso + 3, 22.0), (f_osso + 14, 12.0)])
        nt_interp(F2["mat"].node_tree)
        frees.append(F2)
    key_val(hrs, [(fv - 1, 0.4), (fv, 0.0)]); key_val(hgs, [(fv - 1, 0.4), (fv, 0.0)])
    hc, hcs = X.halo("primo_halo_centro", frees[0]["giro"], (0, 0.18, 0.05), 0.85, strength=0.0)
    key_val(hcs, [(1, 0.0), (fv + 13, 0.0), (fv + 18, 1.2), (fv + 32, 0.6)])
    # corpos esmaecem quando os V saem (o foco vira o encaixe)
    for grp_ in (g, gg):
        key_val(X.gsock(grp_, "ON"), [(fv, 1.0)])
    # ---------- camera parada no eixo (a divisao depende disso); a lente fecha no encaixe
    cam = M.camera((0, 0, 0), (0, 1, 0), LENS)
    C = Cam(cam)

    def c1(u, fr):
        return dict(loc=Vector((0, 0, 0)), rot=Euler((math.radians(90), 0, 0)), lens=LENS + 2.0 * ease(u), sx=0.0, sy=shy, fd=Dd, fs=3.5)
    C.shot(S["C1_primos"], c1)

    def c2(u, fr):
        k = ease(min(1.0, (fr - fa2) / float(max(1, fv + 14 - fa2))))
        return dict(loc=Vector((0, 0, 0)), rot=Euler((math.radians(90), 0, 0)), lens=LENS + 2.0 + 14.0 * k, sx=0.0, sy=shy, fd=Dd - 0.06 * k, fs=3.5)
    C.shot(S["C2_herdaram"], c2)
    C.done()
    cam.data.clip_start = 0.005
    qa_key("rex", R["root"]); qa_key("galinha", GL["root"])
    qa_touch("rex", "galinha")      # os dois corpos sao cortados pelo material em x=0: nao ha sobreposicao de imagem
    qa_foco("C1_primos", FR["giro"], FG["giro"])
    qa_foco("C2_herdaram", frees[0]["giro"], fa=fv + 12)
    return dict(cam=cam, FR=FR, FG=FG)


BUILD = {"A": build_A, "B": build_B, "Q": build_Q, "C": build_C}


def build(world):
    QA["keys"].clear(); QA["touch"].clear(); QA["screen_ok"].clear(); QA["focus"].clear(); QA["inteiros"].clear()
    t = time.time()
    r = BUILD[world]()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.filepath = "//frames/f"
    sc.render.use_overwrite = False; sc.render.use_placeholder = True
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    sc.cycles.samples = SPP[world]
    print("BUILD", world, round(time.time() - t, 1), "s", len(D.objects), "objetos", flush=True)
    return r


SPP = {"B": 12, "A": 12, "Q": 10, "C": 12}     # amostras do render final (OIDN ligado); medidas em tempo_cpu.txt


def eventos():
    cortes = [SH[nm]["f0"] for nm, _, _ in PLAN]
    ev = dict(N=N, fps=FPS, duracao_s=round(N / FPS, 3), shots=cortes, cortes=cortes,
              f_pop=F_POP, t_pop=round((F_POP - 1) / FPS, 3), music=None, sfx=[], pills=[], pills_en=[],
              marcas=dict(estalo=F_POP, pop_pipo=F_POP, rugido=SH["A1_rugido"]["f0"], v_acende_alto_do_peito=f(wt("alto")), peito=f(wt("peito")),
                          metade_esquerda_duas=f(wt("duas")), metade_direita_claviculas=f(wt("clavículas")), juncao_grudadas=f(wt("grudadas")),
                          card_niko=SH["Q1_quintal"]["f0"] + 1, carimbo_acertou=f(wt("acertou")), encaixe_herdaram=f(wt("herdaram")) - 2 + 16,
                          puxar=f(wt("puxar")), fim_da_fala=f(21.9)),
              ponto_furcula_tela=dict(x=P_STAR[0], y=P_STAR[1]),
              planos=[dict(nome=nm, mundo=WORLDS[w_], f0=SH[nm]["f0"], f1=SH[nm]["f1"], s=round((SH[nm]["f1"] - SH[nm]["f0"] + 1) / FPS, 2)) for nm, w_, _ in PLAN])
    json.dump(ev, open(WORK + "/events.json", "w"), ensure_ascii=False, indent=1)
    return ev


def main():
    mode = sys.argv[-1]
    eventos()
    only = os.environ.get("PIPO_WORLDS", "".join(ORDER))
    if mode == "qa":
        allissues = {}; focus = {}
        for w_ in [w for w in ORDER if w in only]:
            build(w_)
            iss, fl = run_qa(w_)
            allissues[WORLDS[w_]] = iss; focus.update(fl)
            print("QA", WORLDS[w_], len(iss), "ocorrencias", flush=True)
            agg = {}
            for i in iss:
                agg.setdefault((i["plano"], i["tipo"], i["alvo"]), []).append(i["frame"])
            for k, v in sorted(agg.items()):
                print("   ", k, "quadros", v[0], "..", v[-1], "(%d)" % len(v))
        fsum = {}
        for shn, lst in focus.items():
            ys = [y for _, _, _, y in lst]; xs = [x for _, _, x, _ in lst]
            fsum[shn] = dict(y_min=min(ys), y_max=max(ys), x_min=min(xs), x_max=max(xs))
        tot = sum(len(v) for v in allissues.values())
        json.dump(dict(total=tot, issues=allissues, foco=fsum), open(WORK + "/qa_scene.json", "w"), ensure_ascii=False, indent=1)
        print("QA_SCENE", tot, "ocorrencias")
        for k, v in fsum.items():
            print("  foco", k, v)
        sys.exit(1 if tot else 0)
    if mode == "blend":
        out = os.environ.get("PIPO_BLEND", WORK + "/blend")
        os.makedirs(out, exist_ok=True)
        man = []
        for w_ in ORDER:
            build(w_)
            sc = bpy.context.scene
            seg = segments(w_)
            sc.frame_start, sc.frame_end = seg[0][0], seg[-1][1]
            sc.frame_set(seg[0][0])
            sc.render.filepath = "//frames/f"
            sc.render.resolution_percentage = 100
            try:
                sc.cycles.device = 'GPU'
            except Exception:
                pass
            bpy.ops.file.pack_all()
            fn = f"{WORLDS[w_]}.blend"
            bpy.ops.wm.save_as_mainfile(filepath=f"{out}/{fn}", compress=True, relative_remap=True)
            for a, b in seg:
                man.append(dict(blend=fn, frame_start=a, frame_end=b, out_prefix="frames/f",
                                cmd=f"blender -b {fn} -o //frames/f -s {a} -e {b} -a -- --cycles-device OPTIX"))
            print("SALVO", fn, seg, flush=True)
        man.sort(key=lambda m_: m_["frame_start"])
        json.dump(man, open(out + "/manifest.json", "w"), ensure_ascii=False, indent=1)
        print("MANIFEST", len(man), "trechos", sum(m_["frame_end"] - m_["frame_start"] + 1 for m_ in man), "quadros")
        return
    if mode == "tempo":
        frs = {"B": 540, "A": 200, "Q": 290, "C": 440}
        res = {}
        for w_ in [w for w in ORDER if w in only]:
            build(w_)
            sc = bpy.context.scene
            sc.render.resolution_percentage = 100
            sc.frame_set(frs[w_])
            sc.render.filepath = f"/tmp/tempo_{w_}.png"
            t0 = time.time(); bpy.ops.render.render(write_still=True); t1 = time.time() - t0
            res[w_] = round(t1, 1)
            print("TEMPO", w_, frs[w_], SPP[w_], "spp", t1, flush=True)
            json.dump(res, open(WORK + f"/prev/tempo_{w_}.json", "w"))
        return
    frs = [max(1, int(x)) for x in mode.split(",")]
    PREV = os.environ.get("PIPO_PREV", WORK + "/prev")
    os.makedirs(PREV, exist_ok=True)
    tlog_p = PREV + "/tempos.json"
    tlog = json.load(open(tlog_p)) if os.path.exists(tlog_p) else {}
    for w_ in ORDER:
        mine = [x for x in frs if world_of(x) == w_]
        if not mine:
            continue
        build(w_)
        sc = bpy.context.scene
        sc.render.resolution_percentage = int(os.environ.get("PIPO_RES", "50"))
        sc.cycles.samples = int(os.environ.get("PIPO_SPP", "8"))
        for fr in mine:
            sc.frame_set(fr)
            sc.render.filepath = PREV + f"/p_{fr:04d}.png"
            t0 = time.time(); bpy.ops.render.render(write_still=True); t1 = time.time() - t0
            tlog[str(fr)] = dict(plano=shot_of(fr), mundo=WORLDS[w_], quadro_s=round(t1, 2))
            print("TIME", fr, shot_of(fr), round(t1, 2), flush=True)
            json.dump(tlog, open(tlog_p, "w"), indent=1)


if __name__ == "__main__":
    main()
