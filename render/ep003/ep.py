"""ep003: Dinossauros parte 2 ("Voce comeu um desses no almoco"). 62,9 s de narracao + cauda, 30 fps, N = 1912 quadros.
Tres mundos (mundos.py), cada um uma cena com cortes de camera dentro; os planos de cada mundo nao sao contiguos,
entao cada mundo vira UM .blend e o manifest lista os trechos (frame_start/frame_end) que saem dele.

Modos (como no kit):
    python3 ep.py qa                 QA da cena em todos os mundos (grava qa_scene.json; sai com codigo 1 se houver falha)
    python3 ep.py 1,382,501          previa de quadros em WORK/prev (p_NNNN.png) + tempo por quadro (prev/tempos.json)
    python3 ep.py full               render completo em WORK/frames (NAO rodar aqui: o Diretor decide onde)
    python3 ep.py blend              WORK/blend/{A_cinzas,B_quintal,C_comparacao}.blend empacotados + manifest.json
Variaveis: PIPO_KIT (kit/), PIPO_WORK (pasta do episodio).
Nada do render depende deste script: tudo vira keyframe (camera, luzes, materiais, visibilidade), modificador
CYCLES de f-curve ou instancia de vertices. O render dos .blend nao executa Python.
"""
import sys, os, json, math, random, time
KIT = os.environ.get("PIPO_KIT", "/home/claude/pipo-canal/kit")
WORK = os.environ.get("PIPO_WORK", "/home/claude/ep003")
sys.path.insert(0, WORK)
import bpy, bmesh
from mathutils import Vector, Euler, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view
import mundos as M

D = bpy.data
FPS = 30
N = 1912
M.N = N                                 # brasas, fogo, folhas e passaros dos mundos animam ate o fim do episodio
f = lambda t: int(round(t * FPS)) + 1   # mesma convencao do kit (quadro 1 = 0,0 s)
T = json.load(open(WORK + "/timing.json"))
WT = {}
for l in T["lines"]:
    for w_, s_, du in l["words"]:
        WT.setdefault(w_.lower().strip(".,!:?…"), []).append(s_)


def wt(word, n=0):
    """tempo (s) da n-esima ocorrencia da palavra na narracao"""
    return WT[word.lower()][n]


L = [l["start"] for l in T["lines"]]
FONT = KIT + "/Fredoka-700.ttf"

# ================================================================ PLANOS (tempo de inicio, mundo)
# o fim de cada plano e o inicio do seguinte; a acao cai na palavra (wt)
PLAN = [
    ("A1_rugido", "A", 0.0),                        # Voce comeu um desses no almoco.
    ("A2_recua", "A", wt("ele") - 0.19),            # Ele morreu com o asteroide
    ("A3_impacto", "A", wt("sessenta") + 0.6),      # sessenta e seis milhoes de anos atras
    ("A4_olho", "A", L[2] - 0.05),                  # Mas nem todo dinossauro morreu.
    ("A5_ruge_de_novo", "A", L[3] - 0.21),          # Um inscrito chutou: a
    ("B1_match", "B", wt("galinha")),               # galinha. (MATCH CUT)
    ("B2_comentario", "B", wt("e", 1) - 0.25),         # E acertou.   (placa do comentario)
    ("B3_quintal", "B", L[4] - 0.62),               # E galinha come
    ("B4_pipo_congela", "B", 16.55),                # milho. (contraplano na Pipo)
    ("B5_fuga", "B", 17.35),                        # pausa de 1,2 s: fuga e perseguicao
    ("C1_orbita", "C", L[5] - 0.06),                # Ave nao e parente de dinossauro.
    ("C2_lado_a_lado", "C", wt("ave", 1) - 0.09),   # Ave e dinossauro.
    ("C3_raiox", "C", L[6] - 0.07),                 # Imagine abrir o peito de um T. rex:
    ("C3b_dentro", "C", wt("lá") - 0.03),           # la dentro tem o mesmo ossinho da sorte
    ("C4_furcula_galinha", "C", wt("frango") - 0.02),   # do frango. (corte para a furcula da galinha no mesmo lugar)
    ("C5_femur_rex", "C", L[7] - 0.01),             # Ate a proteina do osso dele
    ("C6_femur_galinha", "C", wt("parece") - 0.02), # parece com a da galinha.
    ("A6_sol_some", "A", L[8] - 0.1),               # Depois do impacto, sem sol,
    ("A7_florestas", "A", wt("as") + 0.13),         # as florestas morrem.
    ("A8_cisca", "A", L[9] - 0.03),                 # Sobra quem cisca o chao
    ("A9_semente", "A", wt("e", 3) + 0.08),         # e quebra semente.
    ("A10_fossil", "A", L[10] - 0.02),              # Na Belgica, acharam uma ave
    ("C9_wonder_praia", "C", wt("antes") - 0.01),   # de pouco antes do impacto: meio galinha, (praia rasa da Belgica)
    ("C10_wonder_pato", "C", wt("meio", 1) - 0.08), # meio pato.
    ("B6_bilhoes", "B", L[11] - 0.06),              # Hoje sao vinte e sete bilhoes de galinhas.
    ("B7_fileiras", "B", wt("mais") - 0.52),        # Mais de tres por pessoa.
    ("B8_mesa", "B", L[12] - 0.08),                 # O dinossauro nao sumiu.
    ("B9_almoco", "B", wt("virou") - 0.06),         # Virou almoco.
    ("C7_penas_escamas", "C", L[13] - 0.11),        # T. rex: penas ou escamas?
    ("C8_comenta", "C", wt("comenta") - 0.3),       # Comenta.
]
SH = {}
for i, (nm, w_, t0) in enumerate(PLAN):
    f0 = f(t0)
    f1 = (f(PLAN[i + 1][2]) - 1) if i + 1 < len(PLAN) else N
    SH[nm] = dict(name=nm, world=w_, t0=t0, f0=f0, f1=f1)
WORLDS = {"A": "A_cinzas", "B": "B_quintal", "C": "C_comparacao"}


def segments(world):
    """trechos contiguos de quadros do mundo"""
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


F_MATCH = SH["B1_match"]["f0"]                # o corte do match cut cai no "galinha"
F0_FOGE = f(16.40)                            # galinha vira a cabeca (pipo_foge f0), entre "come" e "milho"
F_OSSINHO = f(wt("ossinho"))
F_FRANGO = SH["C4_furcula_galinha"]["f0"]

# ================================================================ utilidades
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


def galinha_assada(name="gal_inst"):
    """uma galinha inteira (penas incluidas) virada UMA malha, para fileiras de instancias"""
    g = M.galinha((0, 0, 0), 0.0, scale=M.CU)
    bpy.context.view_layer.update()
    objs = [o for o in g["root"].children_recursive if o.type in ('MESH', 'CURVE')]
    me = join_baked(objs, g["root"].matrix_world.inverted(), name)
    for o in [g["root"]] + list(g["root"].children_recursive):
        D.objects.remove(o, do_unlink=True)
    return me


def roar_keys(rex, fa, fopen, fhold, fclose, jaw=38, lunge=0.35, back=0.25, noise=True):
    """rugido com a boca abrindo entre fa e fopen (o do quadro 0 abre em 6 quadros)"""
    jw, ha = rex["jaw"], rex["head_anim"]
    for fr, a in ((fa, 8), (fopen, jaw), (fopen + 6, jaw + 3), (fhold, jaw - 3), (fclose, 8), (fclose + 14, 5)):
        K(jw, "rotation_euler", fr, (math.radians(a), 0, 0))
    for fr, loc, rx in ((fa, (0, back * 0.2, 0.02), -4), (fopen, (0, -lunge, -0.05), 4), (fhold, (0, -lunge * 0.85, -0.03), 3),
                        (fclose, (0, 0, 0), 0), (fclose + 14, (0, 0.03, 0), -1)):
        K(ha, "location", fr, loc); K(ha, "rotation_euler", fr, (math.radians(rx), 0, 0))


def add_noise_range(obj, path, fa, fb, strength=0.05, scale=1.5):
    for fc in M.fcurves(obj):
        if fc.data_path == path:
            mo = fc.modifiers.new('NOISE'); mo.strength = strength; mo.scale = scale
            mo.use_restricted_range = True; mo.frame_start = fa; mo.frame_end = fb; mo.blend_in = 2; mo.blend_out = 5


# ================================================================ MUNDO A: cinzas (planos A1-A5 e A6-A12)
def build_A():
    cz = M.mundo_cinzas()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    rex = cz["rex"]; g = cz["chao"]; cam = cz["cam"]
    for o in (rex["jaw"], rex["head_anim"]):
        o.animation_data_clear()
    hobjs = rex["head_objs"]
    olho, fenda, palp = hobjs[3], hobjs[4], hobjs[5]       # olho direito (o lado da camera)
    ref_olho = M._ref(rex["head_pose"], "ref_olho"); ref_ponta = M._ref(rex["head_pose"], "ref_ponta")
    S = SH
    # ---------- rex: ruge no quadro 0 (boca abre nos 6 primeiros quadros), olha o ceu, fecha o olho, ruge de novo no match
    roar_keys(rex, 1, 6, 44, 70, jaw=38, lunge=0.32)
    add_noise_range(rex["head_anim"], "rotation_euler", 6, 46, 0.045, 1.4)
    ha = rex["head_anim"]
    fa2 = S["A2_recua"]["f0"]
    K(ha, "rotation_euler", fa2 + 6, (0, 0, 0)); K(ha, "rotation_euler", fa2 + 30, (math.radians(-16), 0, math.radians(6)))   # olha o asteroide
    K(ha, "rotation_euler", S["A3_impacto"]["f0"] + 30, (math.radians(-12), 0, math.radians(4)))
    K(ha, "rotation_euler", S["A4_olho"]["f0"] - 4, (0, 0, 0))
    K(ha, "location", S["A4_olho"]["f0"] - 4, (0, 0, 0))
    # olho: pupila fecha em fenda e a palpebra desce no "morreu"
    f_morreu = f(wt("morreu", 1))
    base_lid_loc = palp.location.copy(); base_lid_sc = palp.scale.copy(); base_f = fenda.scale.copy()
    K(fenda, "scale", S["A4_olho"]["f0"], base_f); K(fenda, "scale", f(8.7), base_f)
    K(fenda, "scale", f(8.95), (base_f.x * 0.35, base_f.y, base_f.z))
    K(palp, "location", f_morreu - 1, base_lid_loc); K(palp, "scale", f_morreu - 1, base_lid_sc)
    K(palp, "location", f_morreu + 9, (base_lid_loc.x + 0.012, base_lid_loc.y - 0.01, 0.12)); K(palp, "scale", f_morreu + 9, (1.02, 1.25, 0.98))
    fa5 = S["A5_ruge_de_novo"]["f0"]
    K(palp, "location", fa5 + 2, (base_lid_loc.x + 0.012, base_lid_loc.y - 0.01, 0.12)); K(palp, "scale", fa5 + 2, (1.02, 1.25, 0.98))
    K(palp, "location", fa5 + 8, base_lid_loc); K(palp, "scale", fa5 + 8, base_lid_sc)
    K(fenda, "scale", fa5 + 2, (base_f.x * 0.35, base_f.y, base_f.z)); K(fenda, "scale", fa5 + 10, base_f)
    # segundo rugido termina EXATAMENTE na pose do pico no ultimo quadro antes do corte
    jw = rex["jaw"]
    K(jw, "rotation_euler", fa5, (math.radians(6), 0, 0)); K(jw, "rotation_euler", F_MATCH - 18, (math.radians(4), 0, 0))
    K(ha, "location", fa5, (0, 0, 0)); K(ha, "rotation_euler", fa5, (0, 0, 0))
    K(ha, "location", F_MATCH - 18, (0, 0.3, 0.06)); K(ha, "rotation_euler", F_MATCH - 18, (math.radians(-10), 0, 0))
    K(ha, "location", F_MATCH - 1, (0, -0.35, -0.05)); K(ha, "rotation_euler", F_MATCH - 1, (math.radians(4), 0, 0))
    K(jw, "rotation_euler", F_MATCH - 1, (math.radians(40), 0, 0))
    # pos-match (fora do ar): volta ao repouso para os planos A6+
    K(jw, "rotation_euler", F_MATCH + 20, (math.radians(6), 0, 0)); K(ha, "location", F_MATCH + 20, (0, 0, 0)); K(ha, "rotation_euler", F_MATCH + 20, (0, 0, 0))

    # ---------- asteroide (rastro) e clarao do impacto no horizonte
    ast_m = M.emis("asteroide", (1.0, 0.75, 0.4), 40)
    tr_m = M.halo_mat("rastro", (1.0, 0.45, 0.12), 6.0, power=1.6)
    ast = M.empty("asteroide", (0, 0, 0))
    rock = M.sph("ast_rocha", 3.2, (0, 0, 0), ast_m, seg=16, rings=8, parent=ast)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=1.25, radius2=0.0, depth=1, location=(0, 0, 0))
    tail = bpy.context.object; tail.name = "ast_rastro"; M.setmat(tail, M.emis("rastro_cone", (1.0, 0.5, 0.15), 12, alpha=0.75))
    tail.parent = ast; tail.rotation_euler = (math.radians(-90), 0, 0); tail.location = (0, 26, 0); tail.scale = (2.6, 2.6, 52)
    bpy.ops.mesh.primitive_circle_add(vertices=40, radius=1, fill_type='NGON', location=(0, 0, 0))
    hal = bpy.context.object; hal.name = "ast_halo"; M.setmat(hal, tr_m); hal.parent = ast; hal.scale = (5, 5, 1)
    hal.rotation_euler = (math.radians(90), 0, 0); hal.scale = (12, 12, 1)
    for o in (rock, tail, hal):
        o.visible_shadow = False
    p_a, p_b = Vector((-5, 130, 80)), Vector((-22, 92, 3))
    dirv = (p_b - p_a).normalized()
    ast.rotation_euler = dirv.to_track_quat('-Y', 'Z').to_euler()
    f_imp = f(wt("atrás")) + 2
    K(ast, "location", 1, p_a); K(ast, "location", S["A2_recua"]["f0"], p_a); K(ast, "location", f_imp, p_b)
    keys_lin(ast)
    key_scale_vis(ast, [(1, False), (S["A2_recua"]["f0"], True), (f_imp + 1, False)], base=(1, 1, 1))
    vis_window([ast], S["A2_recua"]["f0"], f_imp)
    # clarao: cupula emissiva que cresce e some
    fl_m = M.emis("clarao", (1.0, 0.8, 0.5), 30)
    fl_s = fl_m.node_tree.nodes["Emission"].inputs["Strength"]
    key_val(fl_s, [(f_imp, 60), (f_imp + 12, 25), (f_imp + 40, 4)])
    flash = M.sph("clarao", 1, (p_b.x, p_b.y + 6, 0), fl_m, seg=32, rings=16)
    flash.visible_shadow = False
    K(flash, "scale", 1, (0.001,) * 3); K(flash, "scale", f_imp, (0.001,) * 3); K(flash, "scale", f_imp + 6, (14, 10, 9)); K(flash, "scale", f_imp + 40, (30, 14, 16))
    K(flash, "scale", S["A4_olho"]["f0"] - 1, (30, 14, 16)); K(flash, "scale", S["A4_olho"]["f0"], (0.001,) * 3)
    lf = M.light('POINT', (p_b.x, p_b.y - 10, 8), None, 0, (1.0, 0.6, 0.3), size=6)
    light_keys(lf, [(1, 0), (f_imp - 1, 0), (f_imp + 2, 2.5e6), (f_imp + 30, 4e5), (S["A4_olho"]["f0"], 0)])

    # ---------- floresta que morre sem sol (A6, A7): longe do T. rex, de frente para o sol
    fa6, fb7 = S["A6_sol_some"]["f0"], S["A7_florestas"]["f1"]
    FX, FY = -34.0, 30.0
    trees = []
    random.seed(77)
    wood = M.pbr("tronco_vivo", (0.12, 0.07, 0.04), (0.2, 0.12, 0.06), rough=0.8, nscale=3, nbump=0.5, nbscale=10)
    copa_m = M.pbr("copa_viva", (0.03, 0.12, 0.02), (0.06, 0.2, 0.03), (0.1, 0.22, 0.04), rough=0.7, nscale=2.5, vor_bump=0.6, vor_scale=10)
    rp = [n for n in copa_m.node_tree.nodes if n.type == 'VALTORGB'][0]
    f_mor = f(wt("morrem"))
    for i, (c_live, c_dead) in enumerate((((0.03, 0.12, 0.02), (0.12, 0.06, 0.025)), ((0.06, 0.2, 0.03), (0.17, 0.1, 0.04)))):
        el = rp.color_ramp.elements[i]
        el.color = (*c_live, 1); el.keyframe_insert("color", frame=fa6 + 10)
        el.color = (*c_dead, 1); el.keyframe_insert("color", frame=f_mor + 10)
    nt_interp(copa_m.node_tree)
    pos = [(-6, 4), (-2, 10), (3, 2), (6, 9), (-9, 16), (0, 18), (8, 20), (-4, -2), (4, -5), (11, 4), (-12, 6), (2, 26), (-7, 25), (12, 14)]
    for i, (dx, dy) in enumerate(pos):
        x, y = FX + dx, FY + dy
        z = ground_at(g, x, y) - 0.2
        root = M.empty("arvore_viva", (x, y, z))
        h = random.uniform(9, 13)
        tr = M.skin_model("tronco_vivo", [(0, 0, 0), (random.uniform(-0.3, 0.3), 0, h * 0.55), (random.uniform(-0.5, 0.5), random.uniform(-0.3, 0.3), h)],
                          [(0, 1), (1, 2)], [0.85, 0.6, 0.4], wood, subd=1)
        tr.parent = root
        el = [((random.uniform(-2.4, 2.4), random.uniform(-2.4, 2.4), h + random.uniform(-0.8, 2.2)), random.uniform(2.2, 3.4)) for _ in range(9)]
        cp = M.metaball_mesh("copa_viva", el, res=0.35)
        M.setmat(cp, copa_m); cp.parent = root
        dd = cp.modifiers.new("d", 'DISPLACE'); tx = D.textures.new("copaV", 'CLOUDS'); tx.noise_scale = 0.8; dd.texture = tx; dd.strength = 0.9
        # tomba (para longe da camera), com gravidade: comeca devagar e acelera
        ft = f_mor - 18 + i * 4 + random.randint(-3, 3)
        fall = math.radians(random.uniform(72, 86)) * (1 if i % 2 else -1)
        K(root, "rotation_euler", 1, (0, 0, 0)); K(root, "rotation_euler", ft, (0, 0, 0))
        K(root, "rotation_euler", ft + 10, (math.radians(-8), fall * 0.12, 0))
        K(root, "rotation_euler", ft + 22, (math.radians(-30), fall, 0))
        K(root, "rotation_euler", ft + 26, (math.radians(-28), fall * 0.95, 0))
        for fc in M.fcurves(root):
            kp = fc.keyframe_points
            if len(kp) > 3:
                kp[2].interpolation = 'QUAD'; kp[2].easing = 'EASE_IN'
        trees.append(root)
    # o sol some atras da poeira. SEM chave no mundo (animar o mundo refaz o mapa de luz do ceu a cada quadro: +0,6 s):
    # disco do sol + halo como objetos, e um veu de poeira na frente do ceu que escurece por material
    f_sol = f(wt("sol"))
    sun_c = Vector((FX - 2, FY - 26, 2.2)) + Vector((-0.1, 1.0, 0.16)).normalized() * 230
    sd_m = M.emis("sol_disco", (1.0, 0.62, 0.28), 30)
    sd_s = sd_m.node_tree.nodes["Emission"].inputs["Strength"]
    key_val(sd_s, [(fa6, 30), (f_sol - 6, 26), (f_sol + 26, 0.6), (fb7, 0.4)])
    disco = M.sph("sol_disco", 9, tuple(sun_c), sd_m, seg=24, rings=12)
    sh_m = M.halo_mat("sol_halo", (1.0, 0.45, 0.12), 4.0, power=2.0)
    sh_s = [n for n in sh_m.node_tree.nodes if n.type == 'EMISSION'][0].inputs["Strength"]
    key_val(sh_s, [(fa6, 4.0), (f_sol - 6, 3.6), (f_sol + 26, 0.1), (fb7, 0.05)])
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1, fill_type='NGON', location=tuple(sun_c + Vector((0, 8, 0))), rotation=(math.radians(90), 0, 0))
    halo_s = bpy.context.object; halo_s.name = "sol_halo"; halo_s.scale = (60, 60, 1); M.setmat(halo_s, sh_m)
    veu_m = D.materials.new("veu_poeira"); veu_m.use_nodes = True
    vnt = veu_m.node_tree; M._clear(vnt)
    vo = vnt.nodes.new("ShaderNodeOutputMaterial"); ve = vnt.nodes.new("ShaderNodeEmission"); ve.inputs["Color"].default_value = (0.05, 0.018, 0.008, 1); ve.inputs["Strength"].default_value = 1.0
    vt = vnt.nodes.new("ShaderNodeBsdfTransparent"); vm = vnt.nodes.new("ShaderNodeMixShader")
    vnt.links.new(vt.outputs[0], vm.inputs[1]); vnt.links.new(ve.outputs[0], vm.inputs[2]); vnt.links.new(vm.outputs[0], vo.inputs[0])
    key_val(vm.inputs[0], [(fa6, 0.0), (f_sol - 6, 0.05), (f_sol + 30, 0.88), (fb7, 0.92)])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(FX, FY + 95, 30), rotation=(math.radians(90), 0, 0))
    veu = bpy.context.object; veu.name = "veu_poeira"; veu.scale = (420, 160, 1); M.setmat(veu, veu_m)
    for o in (disco, halo_s, veu):
        o.visible_shadow = False; o.visible_diffuse = False
    for nt_ in (sd_m.node_tree, sh_m.node_tree, vnt):
        nt_interp(nt_)
    vis_window([disco, halo_s, veu], fa6, fb7)
    sol = M.light('SUN', (0, 0, 10), None, 0, (1.0, 0.55, 0.25), angle=2)
    sol.rotation_euler = (-Vector((-0.35, 1.0, 0.32)).normalized()).to_track_quat('-Z', 'Y').to_euler()
    light_keys(sol, [(1, 0), (fa6 - 1, 0), (fa6, 3.0), (f_sol - 6, 2.8), (f_sol + 26, 0.15), (fb7, 0.1), (fb7 + 1, 0)])
    lfor = M.light('AREA', (FX + 4, FY - 16, 6), (FX, FY + 8, 6), 0, (1.0, 0.5, 0.25), size=12)
    only_during(lfor, fa6, fb7, 2200)
    vis_window(trees, fa6, fb7)

    # ---------- aves no chao de cinzas: ciscam e quebram semente (A8, A9)
    fa8, fb9 = S["A8_cisca"]["f0"], S["A9_semente"]["f1"]
    BX, BY = -5.2, -7.0
    bz = ground_at(g, BX, BY)
    ave = M.galinha((BX, BY, bz + 0.005), math.radians(-60), scale=M.CU * 0.75)
    ave2 = M.galinha((BX + 0.9, BY + 1.3, ground_at(g, BX + 0.9, BY + 1.3) + 0.005), math.radians(-150), scale=M.CU * 0.7)
    for a_ in (ave, ave2):
        a_["head_objs"][11].scale = (0.35, 0.35, 0.35)        # quase sem crista: ave do Cretaceo
        a_["head_objs"][17].scale = (0.4, 0.4, 0.4)
        key_scale_vis(a_["root"], [(1, False), (fa8, True), (fb9 + 1, False)])
    pecks = [f(wt("cisca")) - 2, f(wt("cisca")) + 12, f(wt("chão")) + 4, f(wt("quebra")) - 4, f(wt("semente"))]
    for a_, off in ((ave, 0), (ave2, 7)):
        nk = a_["neck"]
        K(nk, "rotation_euler", fa8, (0, 0, 0))
        for pk in pecks:
            K(nk, "rotation_euler", pk + off - 4, (math.radians(8), 0, math.radians(4 * (1 if pk % 2 else -1))))
            K(nk, "rotation_euler", pk + off, (math.radians(62), 0, 0))
            K(nk, "rotation_euler", pk + off + 4, (math.radians(10), 0, 0))
        K(a_["body"], "rotation_euler", fa8, (0, 0, 0))
        for pk in pecks:
            K(a_["body"], "rotation_euler", pk + off, (math.radians(-14), 0, 0)); K(a_["body"], "rotation_euler", pk + off + 6, (0, 0, 0))
    # semente onde o bico bate na ultima bicada
    f_sem = f(wt("semente"))
    sc.frame_set(f_sem)
    tip = M._ref(ave["head_pose"], "ref_ponta").matrix_world.translation.copy()
    sz_ = ground_at(g, tip.x, tip.y)
    sem_m = M.pbr("semente", (0.35, 0.2, 0.08), (0.5, 0.3, 0.12), rough=0.4, nscale=40, nbump=0.3, nbscale=60, spec=0.6)
    miolo_m = M.pbr("semente_miolo", (0.95, 0.85, 0.55), (0.85, 0.7, 0.4), rough=0.5, nscale=30)
    seed_root = M.empty("semente", (tip.x, tip.y, sz_ + 0.012))
    halves = []
    for sx in (1, -1):
        hv = M.empty("semente_metade", (0, 0, 0), seed_root)
        a = M.sph("semente_casca", 0.012, (sx * 0.006, 0, 0), sem_m, seg=16, rings=8, scale=(0.55, 1.0, 0.7), parent=hv)
        b = M.sph("semente_miolo", 0.01, (sx * 0.0025, 0, 0), miolo_m, seg=12, rings=6, scale=(0.3, 0.9, 0.6), parent=hv)
        halves.append(hv)
        K(hv, "location", f_sem - 1, (0, 0, 0)); K(hv, "rotation_euler", f_sem - 1, (0, 0, 0))
        K(hv, "location", f_sem + 5, (sx * 0.03, 0.01, 0.015)); K(hv, "rotation_euler", f_sem + 5, (0, sx * math.radians(70), 0))
        K(hv, "location", f_sem + 10, (sx * 0.045, 0.012, -0.004)); K(hv, "rotation_euler", f_sem + 10, (0, sx * math.radians(150), 0))
    random.seed(4)
    for i in range(22):     # outras sementes espalhadas
        x, y = BX + random.uniform(-0.8, 0.9), BY + random.uniform(-0.7, 1.4)
        M.sph("semente_chao", 0.011, (x, y, ground_at(g, x, y) + 0.006), sem_m, seg=10, rings=6, scale=(0.6, 1.0, 0.6))
    key_scale_vis(seed_root, [(1, False), (fa8, True), (fb9 + 1, False)])
    lave = M.light('AREA', (BX + 1.6, BY - 0.9, 1.4), (BX, BY, 0.2), 0, (1.0, 0.6, 0.3), size=1.5)
    only_during(lave, fa8, fb9, 260)
    vis_window([ave["root"], ave2["root"], seed_root], fa8, fb9)

    # ---------- fossil da Belgica (Wonderchicken) que ganha pele e penas girando (A10-A12)
    fa10, fb12 = S["A10_fossil"]["f0"], S["A10_fossil"]["f1"]
    FXp, FYp = 6.2, -8.0
    fz = ground_at(g, FXp, FYp)
    laje_m = M.pbr("laje", (0.16, 0.14, 0.12), (0.1, 0.09, 0.08), (0.22, 0.2, 0.17), rough=0.9, nscale=2.5, vor_bump=0.5, vor_scale=6, nbump=0.4, nbscale=30)
    laje = M.box("laje", (0.9, 0.7, 0.16), (FXp, FYp, fz + 0.04), laje_m, 0.03, rot=(0, 0, math.radians(12)))
    osso_m = M.pbr("fossil", (0.5, 0.42, 0.3), (0.32, 0.26, 0.18), (0.62, 0.54, 0.4), rough=0.75, nscale=9, vor_bump=0.25, vor_scale=30, nbump=0.5, nbscale=50)
    gir = M.empty("wonder_giro", (FXp, FYp, fz + 0.14))
    scl = 0.16
    fos = M.empty("fossil_cabeca", (0, 0, 0), gir); fos.scale = (scl,) * 3
    _, fobj = M.chicken_head(fos, osso_m, osso_m, osso_m, osso_m, osso_m)
    orb_m = M.pbr("orbita", (0.03, 0.025, 0.02), rough=0.9)
    for o in fobj:
        if o.type == 'MESH' and o.name.startswith(("gal_crista", "gal_barbela", "gal_brinco", "gal_brilho", "gal_pupila", "gal_face")):
            o.scale = (0.001,) * 3
        if o.type == 'MESH' and o.name.startswith("gal_olho"):
            M.setmat(o, orb_m); o.scale = (1.25, 1.25, 1.25)
    viva = M.empty("ave_viva", (0, 0, 0), gir)
    m_head = M.pbr("wc_cab", (0.55, 0.38, 0.22), (0.4, 0.27, 0.16), rough=0.7, nscale=10, nbump=0.35, nbscale=40)
    m_comb = M.pbr("wc_crista", (0.75, 0.1, 0.06), (0.55, 0.05, 0.04), rough=0.4, nscale=7)
    m_beak = M.pbr("wc_bico", (0.85, 0.6, 0.18), (0.7, 0.45, 0.12), rough=0.3, nscale=8, spec=0.8)
    m_eye = M.pbr("wc_olho", (0.95, 0.5, 0.05), rough=0.05, spec=1.0, emit=(1, 0.5, 0.05), estr=0.4)
    m_mouth = M.pbr("wc_boca", (0.12, 0.03, 0.03), rough=0.4)
    vjaw, vobj = M.chicken_head(viva, m_head, m_comb, m_beak, m_eye, m_mouth)
    bico, bico_inf, crista = vobj[12], vobj[13], vobj[11]
    f_ant = SH["A10_fossil"]["f1"] + 30; f_gal = f(wt("galinha", 3)); f_pato = f(wt("pato"))
    # fossil deitado e meio enterrado -> levanta girando
    K(gir, "location", fa10, (FXp, FYp, fz + 0.155)); K(gir, "rotation_euler", fa10, (0, math.radians(90), math.radians(-25)))
    K(gir, "location", f_ant - 4, (FXp, FYp, fz + 0.155)); K(gir, "rotation_euler", f_ant - 4, (0, math.radians(90), math.radians(-25)))
    K(gir, "location", f_ant + 10, (FXp, FYp, fz + 0.42)); K(gir, "rotation_euler", f_ant + 10, (0, 0, math.radians(90)))
    for k in range(1, 6):
        K(gir, "rotation_euler", f_ant + 10 + k * 12, (0, 0, math.radians(90 + 72 * k)))
    K(gir, "location", f_pato, (FXp, FYp, fz + 0.45))
    K(gir, "rotation_euler", f_pato + 4, (math.radians(-6), 0, math.radians(90 + 72 * 5 + 50)))
    K(gir, "rotation_euler", f_ant + 90, (math.radians(-4), math.radians(8), math.radians(90 + 72 * 5 + 62)))
    K(gir, "location", f_ant + 90, (FXp, FYp, fz + 0.47))
    # troca no meio do giro: fossil -> ave viva ("meio galinha")
    K(fos, "scale", 1, (scl,) * 3); K(fos, "scale", f_gal - 3, (scl,) * 3); K(fos, "scale", f_gal + 2, (0.0005,) * 3)
    K(viva, "scale", 1, (0.0005,) * 3); K(viva, "scale", f_gal - 3, (0.0005,) * 3); K(viva, "scale", f_gal + 3, (scl * 1.15,) * 3); K(viva, "scale", f_gal + 7, (scl,) * 3)
    # "meio pato": bico achata e alarga, crista encolhe
    for o, s1 in ((bico, (1.9, 1.15, 0.75)), (bico_inf, (1.9, 1.15, 0.8)), (crista, (0.45, 0.45, 0.45))):
        b0 = tuple(o.scale)
        K(o, "scale", f_pato - 2, b0); K(o, "scale", f_pato + 4, tuple(s1[i] * b0[i] * (1.08 if i == 0 else 1) for i in range(3))); K(o, "scale", f_pato + 8, tuple(s1[i] * b0[i] for i in range(3)))
    K(vjaw, "rotation_euler", f_pato + 4, (0, 0, 0)); K(vjaw, "rotation_euler", f_pato + 8, (math.radians(24), 0, 0)); K(vjaw, "rotation_euler", f_pato + 16, (math.radians(4), 0, 0))
    key_scale_vis(gir, [(1, False), (fa10, True), (fb12 + 1, False)], base=(1, 1, 1))
    key_scale_vis(laje, [(1, False), (fa10, True), (fb12 + 1, False)])
    poeira_m = M.emis("poeira_lab", (1.0, 0.75, 0.5), 3.0)
    lfo = M.light('AREA', (FXp + 0.9, FYp - 1.2, 1.4), (FXp, FYp, fz + 0.3), 0, (1.0, 0.85, 0.7), size=1.2)
    only_during(lfo, fa10, fb12, 18)
    vis_window([gir, laje], fa10, fb12)
    lfo2 = M.light('AREA', (FXp - 1.0, FYp + 0.8, 1.1), (FXp, FYp, fz + 0.3), 0, (1.0, 0.4, 0.1), size=1.0)
    only_during(lfo2, fa10, fb12, 14)

    # ---------- camera
    C = Cam(cam)
    hp = rex["head_pose"]
    bpy.context.view_layer.update()
    mw = hp.matrix_world
    c_loc = mw @ M.CAM_OFF; c_tgt = mw @ M.CAM_TGT
    sh_y = M.CAM_SHIFT_Y
    eyef = rex["head_anim"]

    def a1(u, fr):        # push-in lento + tremor leve (cinza e brasa passam na frente)
        loc = lerp(c_loc, c_tgt, 0.10 * ease(u) + 0.02 * u) + shake(fr, 0.012, 1)
        return dict(loc=loc, tgt=c_tgt + shake(fr, 0.006, 2), lens=M.CAM_LENS, sy=sh_y, fd=(c_loc - c_tgt).length * 0.95, fs=2.2)
    C.shot(S["A1_rugido"], a1)
    wide_loc, wide_tgt = Vector((3.5, -13.0, 1.3)), Vector((-0.5, 1.5, 4.8))
    end_a1 = lerp(c_loc, c_tgt, 0.12)

    def a2(u, fr):        # dolly para tras + grua: revela a planicie e o rastro do asteroide
        k = ease(min(1, u / 0.75))
        loc = lerp(end_a1, wide_loc, k) + Vector((0, 0, 1.6 * math.sin(math.pi * k)))
        tgt = lerp(c_tgt, wide_tgt, k)
        return dict(loc=loc, tgt=tgt, lens=M.CAM_LENS + (22 - M.CAM_LENS) * k, sy=sh_y * (1 - k) + 0.04 * k, fd=(loc - wpos(ref_olho)).length, fs=2.2 + 9 * k)
    C.shot(S["A2_recua"], a2, track=True)

    def a3(u, fr):        # plano geral baixo: silhueta contra o sol vermelho, o impacto no horizonte
        loc = Vector((-4.2 + 1.6 * u, -14.5 + 0.8 * u, 1.0 + 0.2 * u))
        return dict(loc=loc, tgt=Vector((-3.0, 8, 4.6 + 0.4 * u)), lens=24, sy=0.0, fd=13.0, fs=11)
    C.shot(S["A3_impacto"], a3)
    off_o = Vector((1.07, -0.74, 0.22)); off_t = Vector((0.35, -0.44, 0.12))

    def a4(u, fr):        # close extremo do olho, push-in milimetrico
        ha_mw = eyef.matrix_world
        k = 1.0 - 0.25 * ease(u)
        loc = ha_mw @ (off_t + (off_o - off_t) * k)
        tgt = ha_mw @ (off_t + Vector((0.0, 0.0, 0.0)))
        return dict(loc=loc, tgt=tgt, lens=50, sy=0.0, sx=0.0, fd=(loc - tgt).length, fs=2.0)
    C.shot(S["A4_olho"], a4, track=True)

    def a5(u, fr):        # volta ao enquadramento do plano 1 (mesma lente e altura): prepara o match cut
        loc = lerp(c_loc, c_tgt, 0.04 * u)
        return dict(loc=loc, tgt=c_tgt, lens=M.CAM_LENS, sy=sh_y, fd=(c_loc - c_tgt).length * 0.95, fs=2.2)
    C.shot(S["A5_ruge_de_novo"], a5)
    # floresta
    cfx = Vector((FX - 2, FY - 26, 2.2))

    def a6(u, fr):        # plano geral quase fixo (time-lapse de luz): sol some atras da poeira
        return dict(loc=cfx + Vector((0.8 * u, 0.6 * u, 0.1 * u)), tgt=Vector((FX + 1, FY + 10, 9.0)), lens=24, fd=25, fs=14)
    C.shot(S["A6_sol_some"], a6)

    def a7(u, fr):        # mais perto, lente longa: as copas tombam
        return dict(loc=Vector((FX + 15 - 2.0 * u, FY - 33, 2.0)), tgt=Vector((FX + 0.5 - 0.8 * u, FY + 8, 6.5 - 1.5 * u)), lens=36, fd=38, fs=14)
    C.shot(S["A7_florestas"], a7)
    bird_c = Vector((BX, BY, bz)); ave_eye = M._ref(ave["head_pose"], "ref_olho")

    def a8(u, fr):        # tilt down do ceu de poeira ate as aves no chao (de costas para o T. rex)
        k = ease(u)
        loc = bird_c + Vector((1.35 - 0.15 * k, -0.6 + 0.35 * k, 0.3))
        tgt = (wpos(ave["root"]) + wpos(ave_eye)) * 0.5 + Vector((0, 0, -0.02))
        return dict(loc=loc, tgt=tgt, lens=35, fd=(loc - bird_c).length, fs=3.2)
    C.shot(S["A8_cisca"], a8, track=True)
    sp_ = Vector((tip.x, tip.y, sz_))

    def a9(u, fr):        # macro no nivel do chao: o bico quebra a semente
        loc = sp_ + Vector((0.95 - 0.08 * u, -0.3 + 0.03 * u, 0.12))
        return dict(loc=loc, tgt=sp_ + Vector((0, 0, 0.1)), lens=45, fd=(loc - sp_).length, fs=5.0, sy=-0.07)
    C.shot(S["A9_semente"], a9)
    fpos = Vector((FXp, FYp, fz + 0.15))

    def a10(u, fr):       # o fossil na laje: push-in
        k = ease(u)
        loc = fpos + Vector((0.42 - 0.14 * k, -0.68 + 0.24 * k, 0.42 - 0.12 * k))
        return dict(loc=loc, tgt=fpos + Vector((0, 0, -0.06)), lens=40, fd=(loc - fpos).length, fs=3.5, sy=0.0)
    C.shot(S["A10_fossil"], a10)


    C.done()
    # ---------- QA
    qa_key("rex", rex["root"]); qa_key("ave", ave["root"]); qa_key("ave2", ave2["root"]); qa_key("semente", seed_root)
    qa_key("wonderchicken", gir); qa_key("laje", laje)
    qa_touch("wonderchicken", "laje"); qa_touch("ave", "semente")
    qa_tela("ave", "ave2")
    for sn in ("A1_rugido", "A5_ruge_de_novo"):
        qa_foco(sn, ref_olho, ref_ponta)
    qa_foco("A2_recua", ref_olho); qa_foco("A3_impacto", ref_olho); qa_foco("A4_olho", ref_olho)
    qa_foco("A8_cisca", M._ref(ave["head_pose"], "ref_olho")); qa_foco("A9_semente", seed_root)
    qa_foco("A10_fossil", gir)
    qa_inteiro("A8_cisca", "ave")
    # referencias do match cut: olho e ponta do focinho na tela no ultimo quadro antes do corte
    sc.frame_set(F_MATCH - 1)
    e_, p_ = M.tela_refs(cam, hp)
    json.dump(dict(frame=F_MATCH - 1, olho=e_, ponta=p_), open(WORK + "/match_refs.json", "w"))
    return dict(cam=cam)


# ================================================================ MUNDO B: quintal (B1-B5, B6-B9)
def build_B():
    qt = M.mundo_quintal()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    gal = qt["galinha"]; g = qt["chao"]; cam = qt["cam"]
    for o in (gal["jaw"], gal["head_anim"]):
        o.animation_data_clear()
    S = SH
    refs = json.load(open(WORK + "/match_refs.json"))
    # ---------- galinha: mesma pose do pico do rugido no quadro do corte, cacareja
    jw, ha = gal["jaw"], gal["head_anim"]
    K(ha, "location", F_MATCH, (0, -0.35, -0.05)); K(ha, "rotation_euler", F_MATCH, (math.radians(4), 0, 0))
    K(jw, "rotation_euler", F_MATCH, (math.radians(30), 0, 0))
    for fr, a in ((F_MATCH + 4, 22), (F_MATCH + 8, 32), (F_MATCH + 12, 20), (F_MATCH + 16, 30), (F_MATCH + 24, 4), (F_MATCH + 30, 2)):
        K(jw, "rotation_euler", fr, (math.radians(a), 0, 0))
    K(ha, "location", F_MATCH + 18, (0, -0.3, -0.03)); K(ha, "rotation_euler", F_MATCH + 18, (math.radians(3), 0, 0))
    K(ha, "location", F_MATCH + 30, (0, 0, 0)); K(ha, "rotation_euler", F_MATCH + 30, (0, 0, 0))
    add_noise_range(ha, "rotation_euler", F_MATCH, F_MATCH + 22, 0.03, 1.2)
    # "E acertou": balanca a cabeca, orgulhosa
    fb2 = S["B2_comentario"]["f0"]; f_ac = f(wt("acertou"))
    for k, fr in enumerate(range(f_ac - 4, f_ac + 22, 6)):
        K(ha, "rotation_euler", fr, (math.radians(8 if k % 2 else -6), 0, math.radians(6 if k % 2 else -4)))
    K(ha, "rotation_euler", f_ac + 26, (0, 0, 0))
    K(jw, "rotation_euler", f_ac, (math.radians(2), 0, 0)); K(jw, "rotation_euler", f_ac + 5, (math.radians(26), 0, 0)); K(jw, "rotation_euler", f_ac + 12, (math.radians(2), 0, 0))
    # ---------- Pipo foge (gag do milho)
    ev = M.pipo_foge(qt, f0=F0_FOGE)
    # a fuga se afasta do vaso (a pista original passava raspando nas folhas): y sobe 5 cm por pulo
    for fc in M.fcurves(qt["pipo"]):
        if fc.data_path == "location" and fc.array_index == 1:
            for kp in fc.keyframe_points:
                if kp.co.x > F0_FOGE + 19:
                    hop = (kp.co.x - (F0_FOGE + 19)) / 9.0
                    kp.co.y = -0.22 + 0.085 * hop; kp.handle_left.y = kp.co.y; kp.handle_right.y = kp.co.y
    # e continua fugindo ate o corte (a galinha nunca alcanca a Pipo dentro do quadro)
    fr_ = ev["f_fora"]; x_ = -0.06 - 3.3; y_ = -0.22 + 0.085 * 5
    for k in range(5):
        qt["pipo_ns"]["pipo_hop"](fr_, h=0.35)
        x_ -= 0.72; y_ += 0.02
        K(qt["pipo"], "location", fr_ + 9, (x_, y_, 0))
        fr_ += 9
    s = sc
    s.view_settings.view_transform = 'Standard'
    s.cycles.max_bounces = 2; s.cycles.diffuse_bounces = 1
    try:
        s.cycles.denoising_input_passes = 'RGB'; s.cycles.use_light_tree = False
    except Exception:
        pass
    ns = qt["pipo_ns"]; pipo = qt["pipo"]
    key_scale_vis(pipo, [(1, False), (S["B3_quintal"]["f0"], True), (S["B5_fuga"]["f1"] + 1, False)], base=(0.33,) * 3)
    ns["pipo_idle"](ns["FK"], S["B3_quintal"]["f0"], F0_FOGE - 2, period=12)
    # galinha cisca antes de ver a Pipo
    nk = gal["neck"]
    fb3 = S["B3_quintal"]["f0"]
    for fr in (fb3 + 2, fb3 + 14):
        K(nk, "rotation_euler", fr, (0, 0, 0)); K(nk, "rotation_euler", fr + 5, (math.radians(50), 0, 0)); K(nk, "rotation_euler", fr + 10, (0, 0, 0))
    # depois da fuga (fora do ar), a galinha volta ao lugar para os planos B6+
    gr = gal["root"]
    p_gal = Vector((0.35, 0.15, ground_at(g, 0.35, 0.15)))
    f_back = S["B6_bilhoes"]["f0"] - 2
    K(gr, "location", f_back, p_gal); K(gr, "rotation_euler", f_back, (0, 0, math.radians(8)))
    K(nk, "rotation_euler", f_back, (0, 0, 0)); K(gal["body"], "location", f_back, (0, 0, 0)); K(gal["body"], "rotation_euler", f_back, (0, 0, 0))
    for lg in gal["legs"]:
        K(lg, "rotation_euler", f_back, (0, 0, 0))
    for o in (gr, nk, gal["body"]) + tuple(gal["legs"]):
        for fc in M.fcurves(o):
            for kp in fc.keyframe_points:
                if int(kp.co.x) == f_back - 0 and False:
                    pass
    # bicadas no plano das fileiras (a galinha do quintal continua viva)
    fb6 = S["B6_bilhoes"]["f0"]
    for fr in range(fb6 + 4, fb6 + 70, 22):
        K(nk, "rotation_euler", fr, (0, 0, 0)); K(nk, "rotation_euler", fr + 6, (math.radians(55), 0, 0)); K(nk, "rotation_euler", fr + 12, (0, 0, 0))

    # ---------- placa 3D do comentario (presa a camera, na profundidade de foco: nitida e fora das faixas)
    card = M.empty("placa_comentario", (0, 0, 0))
    # ---------- fileiras de galinhas ate o horizonte (instancias de vertices de UMA malha)
    me_gal = galinha_assada()
    gi = M.link(D.objects.new("gal_fileira", me_gal))
    dm = gi.modifiers.new("dec", 'DECIMATE'); dm.ratio = 0.4          # longe ninguem conta penas: 1/8 dos triangulos
    gi.location = (0, 0, -500)                     # o original fica escondido longe; so as instancias aparecem
    gi.hide_render = False
    bm = bmesh.new()
    random.seed(5)
    nverts = 0
    for iy, y in enumerate([-40 + 1.45 * k for k in range(int(210 / 1.45))]):
        for x in [-90 + 1.05 * k for k in range(int(112 / 1.05))]:
            if -9 < x < 10 and -4 < y < 14:
                continue
            bm.verts.new((x + random.uniform(-0.05, 0.05), y, 0.0))
            nverts += 1
    grid_me = D.meshes.new("fileiras"); bm.to_mesh(grid_me); bm.free()
    grid = M.link(D.objects.new("fileiras", grid_me))
    grid.instance_type = 'VERTS'
    gi.parent = grid
    gi.location = (0, 0, 0); gi.scale = (M.CU,) * 3; gi.rotation_euler = (0, 0, math.radians(90))   # de perfil para a camera: forma de galinha
    grid.location = (0, 0, -0.01)
    # chao de fazenda em volta do quintal (sem fundo vazio na grua)
    faz_m = M.pbr("fazenda", (0.36, 0.26, 0.12), (0.3, 0.36, 0.1), (0.45, 0.33, 0.16), rough=0.95, nscale=0.08, nbump=0.3, nbscale=3)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 90, -0.03))
    faz = bpy.context.object; faz.location.z = -0.08; faz.name = "chao_fazenda"; faz.scale = (420, 420, 1); M.setmat(faz, faz_m)
    # as 2 outras galinhas do quintal ("um quintal com 3 galinhas")
    extra = []
    for (x, y, r) in ((-0.75, 0.75, 40), (1.25, 1.05, -120)):
        o = M.link(D.objects.new("gal_quintal", me_gal)); o.location = (x, y, ground_at(g, x, y)); o.rotation_euler = (0, 0, math.radians(r)); o.scale = (M.CU,) * 3
        extra.append(o)
        vis_window([o], fb6, S["B7_fileiras"]["f1"])
        for k, fr in enumerate(range(fb6 + 8 + (0 if x < 0 else 9), S["B6_bilhoes"]["f1"], 18)):
            K(o, "rotation_euler", fr, (math.radians(0), 0, math.radians(r))); K(o, "rotation_euler", fr + 5, (math.radians(-22), 0, math.radians(r + 6)))
            K(o, "rotation_euler", fr + 10, (0, 0, math.radians(r)))
    vis_window([grid, faz], fb6, S["B7_fileiras"]["f1"])

    # ---------- cozinha brasileira na hora do almoco (set proprio, longe do quintal) + sombra do T. rex que cresce na parede
    fa8, fb9 = S["B8_mesa"]["f0"], S["B9_almoco"]["f1"]
    KX, KY = 40.0, 0.0
    TX, TY = KX, KY + 1.15
    WY = KY + 2.0                                   # parede do fundo
    cozinha = []
    piso_m = D.materials.new("piso_cozinha"); piso_m.use_nodes = True
    pn = piso_m.node_tree; pp_ = pn.nodes["Principled BSDF"]; pp_.inputs["Roughness"].default_value = 0.35
    ck = pn.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 1.0
    ck.inputs["Color1"].default_value = (0.55, 0.12, 0.06, 1); ck.inputs["Color2"].default_value = (0.75, 0.6, 0.45, 1)
    tcn = pn.nodes.new("ShaderNodeTexCoord"); mpn = pn.nodes.new("ShaderNodeMapping"); mpn.inputs["Scale"].default_value = (3.3, 3.3, 3.3)
    pn.links.new(tcn.outputs["Object"], mpn.inputs["Vector"]); pn.links.new(mpn.outputs["Vector"], ck.inputs["Vector"]); pn.links.new(ck.outputs["Color"], pp_.inputs["Base Color"])
    azu_m = D.materials.new("azulejo"); azu_m.use_nodes = True
    an = azu_m.node_tree; ap_ = an.nodes["Principled BSDF"]; ap_.inputs["Roughness"].default_value = 0.15
    try:
        ap_.inputs["Coat Weight"].default_value = 0.5
    except Exception:
        pass
    ck2 = an.nodes.new("ShaderNodeTexChecker"); ck2.inputs["Color1"].default_value = (0.92, 0.93, 0.95, 1); ck2.inputs["Color2"].default_value = (0.12, 0.42, 0.62, 1)
    tc2 = an.nodes.new("ShaderNodeTexCoord"); mp2 = an.nodes.new("ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (6.5, 6.5, 6.5)
    an.links.new(tc2.outputs["Object"], mp2.inputs["Vector"]); an.links.new(mp2.outputs["Vector"], ck2.inputs["Vector"]); an.links.new(ck2.outputs["Color"], ap_.inputs["Base Color"])
    tinta_m = M._parede_mat("tinta_cozinha", (0.62, 0.78, 0.58), (0.52, 0.7, 0.5), suja=True, bump=0.25)
    branco_m = M.pbr("teto", (0.85, 0.83, 0.78), rough=0.9)
    cozinha.append(M.box("piso", (5.0, 4.6, 0.04), (KX, KY + 0.0, -0.02), piso_m, 0.0))
    cozinha.append(M.box("teto", (5.0, 4.6, 0.04), (KX, KY + 0.0, 2.72), branco_m, 0.0))
    cozinha.append(M.box("parede_fundo_azulejo", (5.0, 0.06, 1.25), (KX, WY + 0.03, 0.625), azu_m, 0.0))
    cozinha.append(M.box("parede_fundo_tinta", (5.0, 0.06, 1.45), (KX, WY + 0.03, 1.975), tinta_m, 0.0))
    cozinha.append(M.box("parede_dir", (0.06, 4.6, 2.7), (KX + 2.5, KY, 1.35), tinta_m, 0.0))
    # parede esquerda com janela (vao entre 4 pecas) e a luz do meio-dia entrando
    LX = KX - 2.2
    for nm, sz, lc in (("jan_baixo", (0.06, 4.6, 0.95), (LX, KY, 0.475)), ("jan_cima", (0.06, 4.6, 0.75), (LX, KY, 2.325)),
                       ("jan_fundo", (0.06, 1.0, 1.0), (LX, KY + 1.8, 1.45)), ("jan_frente", (0.06, 2.4, 1.0), (LX, KY - 1.1, 1.45))):
        cozinha.append(M.box(nm, sz, lc, tinta_m, 0.0))
    caix_m = M.pbr("caixilho", (0.12, 0.35, 0.6), rough=0.4)
    for zz in (0.95, 1.95):
        cozinha.append(M.box("caixilho", (0.08, 1.2, 0.05), (LX + 0.02, KY + 0.7, zz), caix_m, 0.005))
    for yy in (0.1, 0.7, 1.3):
        cozinha.append(M.box("caixilho", (0.08, 0.05, 1.0), (LX + 0.02, KY + yy, 1.45), caix_m, 0.005))
    ceu_j = M.emis("ceu_janela", (1.0, 0.92, 0.75), 2.5)
    cozinha.append(M.box("luz_janela", (0.02, 1.4, 1.2), (LX - 0.6, KY + 0.7, 1.45), ceu_j, 0.0))
    sol_j = M.light('AREA', (LX - 0.45, KY + 0.7, 1.75), (KX - 0.3, TY, 0.75), 0, (1.0, 0.85, 0.62), size=1.0)
    only_during(sol_j, fa8, fb9, 90)
    amb = M.light('AREA', (KX + 0.3, KY - 1.6, 2.5), (KX, TY, 0.8), 0, (1.0, 0.92, 0.85), size=2.5)
    only_during(amb, fa8, fb9, 14)
    # prateleira com panelas e potes, frigideira pendurada, filtro de barro no balcao
    wood = M.pbr("mesa_madeira", (0.35, 0.2, 0.09), (0.25, 0.14, 0.06), rough=0.6, nscale=3, nbump=0.3, nbscale=20)
    cozinha.append(M.box("prateleira", (1.6, 0.24, 0.035), (KX - 0.2, WY - 0.12, 1.62), wood, 0.004))
    alu = M.pbr("aluminio", (0.75, 0.75, 0.78), rough=0.28, metal=1.0)
    for i, (dx, r, h, mat) in enumerate(((-0.85, 0.11, 0.13, alu), (-0.55, 0.09, 0.1, alu),
                                          (-0.25, 0.045, 0.16, M.pbr("pote_verm", (0.8, 0.1, 0.08), rough=0.3)),
                                          (-0.12, 0.045, 0.14, M.pbr("pote_amar", (0.95, 0.7, 0.1), rough=0.3)),
                                          (0.02, 0.045, 0.18, M.pbr("pote_verde", (0.15, 0.55, 0.2), rough=0.3)),
                                          (0.3, 0.12, 0.09, M.pbr("panela_barro", (0.5, 0.2, 0.08), (0.4, 0.15, 0.06), rough=0.8, nscale=8)))):
        cozinha.append(M.cyl("pote", r, h, (KX + dx, WY - 0.13, 1.64 + h / 2), mat, verts=24))
    fri = M.cyl("frigideira", 0.15, 0.03, (KX + 0.95, WY - 0.03, 1.35), M.pbr("frigideira", (0.05, 0.05, 0.06), rough=0.35, metal=0.6), rot=(math.radians(90), 0, 0), verts=32)
    cozinha.append(fri); cozinha.append(M.box("cabo_frigideira", (0.03, 0.02, 0.22), (KX + 0.95, WY - 0.03, 1.6), wood, 0.005))
    barro = M.pbr("filtro_barro", (0.62, 0.27, 0.12), (0.52, 0.2, 0.09), rough=0.85, nscale=6, nbump=0.3, nbscale=30)
    cozinha.append(M.box("balcao", (0.9, 0.55, 0.9), (KX + 1.8, WY - 0.3, 0.45), wood, 0.01))
    cozinha.append(M.cyl("filtro_baixo", 0.15, 0.3, (KX + 1.8, WY - 0.3, 1.05), barro, verts=32))
    cozinha.append(M.cyl("filtro_cima", 0.14, 0.28, (KX + 1.8, WY - 0.3, 1.34), barro, verts=32))
    cozinha.append(M.sph("filtro_tampa", 0.14, (KX + 1.8, WY - 0.3, 1.48), barro, scale=(1, 1, 0.35)))
    # mesa com toalha xadrez e o prato feito: arroz, feijao e a coxa
    toalha = M._tecido_mat("toalha_mesa", (0.85, 0.08, 0.08), (0.97, 0.95, 0.9), listras=14, scale=6)
    mesa = M.box("mesa_tampo", (1.15, 0.72, 0.05), (TX, TY, 0.74), toalha, 0.01)
    pernas = [M.box("mesa_perna", (0.05, 0.05, 0.72), (TX + sx * 0.5, TY + sy * 0.3, 0.36), wood, 0.005) for sx in (1, -1) for sy in (1, -1)]
    PXc, PYc = TX - 0.05, TY - 0.12
    prato_m = M.pbr("prato", (0.95, 0.94, 0.9), rough=0.15, spec=0.8, coat=0.6)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.15, depth=0.015, location=(PXc, PYc, 0.775))
    prato = bpy.context.object; prato.name = "prato"; M.smooth(prato); M.setmat(prato, prato_m)
    bv = prato.modifiers.new("bv", 'BEVEL'); bv.width = 0.006; bv.segments = 3
    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.008, location=(PXc, PYc, 0.787))
    aba = bpy.context.object; aba.name = "prato_aba"; M.smooth(aba); M.setmat(aba, prato_m)
    arroz = M.metaball_mesh("arroz", [((PXc - 0.06 + random.uniform(-0.02, 0.02), PYc + 0.05 + random.uniform(-0.02, 0.02), 0.79), 0.035) for _ in range(5)], res=0.006)
    M.setmat(arroz, M.pbr("arroz", (0.95, 0.93, 0.86), (0.85, 0.82, 0.75), rough=0.6, nscale=120, nbump=0.6, nbscale=180))
    feijao = M.metaball_mesh("feijao", [((PXc + 0.03 + random.uniform(-0.02, 0.02), PYc + 0.07 + random.uniform(-0.015, 0.015), 0.785), 0.03) for _ in range(4)], res=0.006)
    M.setmat(feijao, M.pbr("feijao", (0.18, 0.07, 0.03), (0.28, 0.12, 0.05), rough=0.25, nscale=60, nbump=0.4, nbscale=120, spec=0.8))
    assado = M.pbr("coxa_assada", (0.55, 0.22, 0.05), (0.75, 0.38, 0.08), (0.35, 0.12, 0.03), rough=0.35, nscale=14, nbump=0.5, nbscale=40, spec=0.8, coat=0.5)
    osso = M.pbr("osso_coxa", (0.95, 0.9, 0.8), rough=0.5)
    coxa = M.empty("coxa", (PXc + 0.01, PYc - 0.04, 0.80), rot=(0, 0, math.radians(78)))
    cx_ = M.metaball_mesh("coxa_carne", [((0, -0.035, 0.012), 0.055, (1.0, 1.25, 0.85)), ((0, 0.01, 0.008), 0.045, (0.9, 1.0, 0.8)),
                                        ((0, 0.05, 0.005), 0.03, (0.75, 1.0, 0.7)), ((0, 0.08, 0.004), 0.02, (0.7, 1.0, 0.7))], res=0.005)
    M.setmat(cx_, assado); cx_.parent = coxa
    M.cyl("coxa_osso", 0.008, 0.06, (0, 0.115, 0.006), osso, rot=(math.radians(90), 0, 0), parent=coxa)
    M.sph("coxa_osso_ponta", 0.013, (0, 0.148, 0.006), osso, parent=coxa, scale=(1.4, 0.8, 0.9))
    garfo_m = M.pbr("garfo", (0.8, 0.8, 0.82), rough=0.2, metal=1.0)
    garfo = M.box("garfo", (0.018, 0.17, 0.004), (PXc + 0.2, PYc, 0.769), garfo_m, 0.002)
    copo = M.cyl("copo", 0.035, 0.11, (PXc + 0.32, PYc + 0.2, 0.822), M.pbr("copo", (0.85, 0.35, 0.05), (0.95, 0.5, 0.08), rough=0.2, spec=0.9), verts=24)
    mesa_objs = [mesa, prato, aba, coxa] + pernas
    cozinha += [mesa, prato, aba, arroz, feijao, coxa, garfo, copo] + pernas
    vis_window(cozinha, fa8, fb9)
    # T. rex que so faz sombra (nao aparece na camera): sai da parede e vem para a luz; a sombra cresce e ruge
    rx = M.trex((TX, WY - 0.4, 1.2), rotz=math.radians(-90))
    rx["root"].scale = (0.085,) * 3
    hide_from_camera(desc_meshes(rx["root"]))
    K(rx["root"], "location", fa8, (TX - 0.25, WY - 0.25, 1.25)); K(rx["root"], "location", f(wt("sumiu")) + 6, (TX - 0.22, KY + 1.0, 1.08))
    K(rx["root"], "location", fb9, (TX - 0.2, KY + 0.85, 1.05))
    keys_lin(rx["root"])
    vis_window([rx["root"]], fa8, fb9)
    f_vir = f(wt("virou"))
    rjw, rha = rx["jaw"], rx["head_anim"]
    for fr, a in ((fa8, 4), (f_vir - 2, 4), (f_vir + 4, 40), (f_vir + 26, 36), (f_vir + 36, 6)):
        K(rjw, "rotation_euler", fr, (math.radians(a), 0, 0))
    K(rha, "location", f_vir - 2, (0, 0.2, 0.05)); K(rha, "location", f_vir + 4, (0, -0.3, -0.04)); K(rha, "location", f_vir + 36, (0, 0, 0))
    spot = M.light('SPOT', (TX + 0.15, KY - 0.75, 0.95), (TX, WY, 1.55), 0, (1.0, 0.82, 0.6), size=0.03, spot=80)
    only_during(spot, fa8, fb9, 420)

    # ---------- camera
    C = Cam(cam)
    bpy.context.view_layer.update()
    sc.frame_set(F_MATCH)
    M.frame_head(cam, gal["head_pose"])
    got = M.match_cut(cam, gal["head_pose"], refs["olho"], refs["ponta"], iters=6)
    print("MATCH alvo", refs["olho"], refs["ponta"], "galinha", got)
    m_loc = cam.location.copy(); m_rot = cam.rotation_euler.copy(); m_sx, m_sy = cam.data.shift_x, cam.data.shift_y
    eye_w = M._ref(gal["head_pose"], "ref_olho").matrix_world.translation.copy()
    fwd = (m_rot.to_matrix() @ Vector((0, 0, -1)))

    def b1(u, fr):
        return dict(loc=m_loc + fwd * 0.012 * ease(u), rot=m_rot, lens=M.CAM_LENS, sx=m_sx, sy=m_sy, fd=(m_loc - eye_w).length, fs=4.0)
    C.shot(S["B1_match"], b1)
    gp = p_gal
    c2a = gp + Vector((0.3, -1.02, 0.36)); c2b = gp + Vector((0.24, -0.9, 0.36))
    t2 = gp + Vector((-0.01, 0.0, 0.36))
    LENS2 = 30

    def b2(u, fr):
        k = ease(u)
        return dict(loc=lerp(c2a, c2b, k), tgt=t2, lens=LENS2, fd=(lerp(c2a, c2b, k) - (gp + Vector((0, 0, 0.35)))).length, fs=5.6)
    C.shot(S["B2_comentario"], b2)
    pp = Vector((-0.06, -0.22, 0)); mid = (pp + Vector((gp.x, gp.y, 0))) * 0.5

    def b3(u, fr):        # o plano aprovado da previa d (plano medio do quintal), com deriva lenta
        loc = Vector((mid.x - 0.03 - 0.06 * u, mid.y - 1.22 + 0.08 * u, 0.2))
        return dict(loc=loc, tgt=Vector((mid.x - 0.03 - 0.04 * u, mid.y, 0.2)), lens=28, sy=-0.045, fd=(loc - Vector((mid.x, mid.y, 0.15))).length, fs=3.2)
    C.shot(S["B3_quintal"], b3)
    pf = qt["pipo_foco"]
    sc.frame_set(S["B4_pipo_congela"]["f0"])
    pw_ = pf.matrix_world.translation.copy()
    face = (pipo.matrix_world.to_3x3().normalized() @ Vector((0, -1, 0))).normalized()

    def b4(u, fr):        # contraplano: a Pipo vista do lado da galinha, congelada
        loc = pw_ + face * (0.6 - 0.08 * ease(u)) + Vector((0, 0, 0.17))
        return dict(loc=loc, tgt=pw_ + Vector((0, 0, -0.02)), lens=45, sy=-0.04, fd=(loc - pw_).length, fs=2.4)
    C.shot(S["B4_pipo_congela"], b4)

    gal_root = gal["root"]

    def b5(u, fr):        # plano aberto acompanhando a fuga para a esquerda; a galinha atravessa atras
        x = 0.5 * (wpos(pipo).x + wpos(gal_root).x)
        loc = Vector((x + 0.15, -1.55, 1.2))
        return dict(loc=loc, tgt=Vector((x - 0.05, 0.05, 0.02)), lens=24, sy=0.0, fd=2.0, fs=5.0)
    C.shot(S["B5_fuga"], b5, track=True)

    PX, PY = -29.6, 28.95

    def b6(u, fr):        # grua: comeca no chao, no meio das fileiras (6 galinhas nitidas), e abre rapido para o mar de galinhas
        k = ease(min(1.0, u / 0.6)); k2 = ease(u)
        loc = Vector((PX + 0.6 * k2, PY + 0.35 - 4.5 * k, 0.3 + 4.6 * k ** 1.3))
        tgt = Vector((PX + 0.3 * k2, PY + 2.4 + 17 * k, 0.2 - 0.2 * k))
        return dict(loc=loc, tgt=tgt, lens=26 - 2 * k, fd=(loc - Vector((PX, PY + 2.2, 0.25))).length if k < 0.3 else 9, fs=4.0 + 12 * k, sy=0.0)
    C.shot(S["B6_bilhoes"], b6)

    def b7(u, fr):        # voo baixo de drone sobre as fileiras ate o horizonte
        loc = Vector((-26.3 + 1.0 * u, 36 + 9 * u, 3.4 - 0.6 * u))
        return dict(loc=loc, tgt=loc + Vector((0.4, 9, -2.6)), lens=24, fd=5, fs=16, sy=0.0)
    C.shot(S["B7_fileiras"], b7)
    tcen = Vector((PXc, PYc, 0.82))

    def b8(u, fr):        # cozinha: mesa com o prato feito, janela com luz, prateleira; a sombra do T. rex cresce na parede
        loc = Vector((TX - 0.35 + 0.1 * u, KY - 0.75 + 0.15 * ease(u), 1.32))
        return dict(loc=loc, tgt=Vector((TX - 0.05, WY, 0.76)), lens=26, fd=(loc - tcen).length, fs=6.0, sy=0.0)
    C.shot(S["B8_mesa"], b8)

    def b9(u, fr):        # "virou almoco": baixo e perto do prato; a sombra ruge na parede atras
        loc = Vector((TX - 0.22 + 0.05 * u, PYc - 0.62 + 0.05 * u, 1.0))
        return dict(loc=loc, tgt=Vector((TX, WY, 0.6)), lens=24, fd=(loc - tcen).length, fs=4.0, sy=0.0)
    C.shot(S["B9_almoco"], b9)
    C.done()

    # placa: filha da camera, posicionada pela lente do plano B2
    sc.frame_set(fb2)
    d_ = 1.15
    kh = d_ * 36.0 / LENS2; kw = kh * 540 / 960
    card.parent = cam
    card.location = (0, kh * (0.5 - 0.255), -d_)
    pan_m = M.emis("placa_fundo", (0.93, 0.93, 0.95), 1.0)
    sh_m = M.emis("placa_sombra", (0.02, 0.01, 0.03), 1.0, alpha=0.55)
    av_m = M.emis("avatar", (1.0, 0.45, 0.08), 1.6)
    t1m = M.emis("placa_txt1", (0.25, 0.25, 0.32), 1.0); t2m = M.emis("placa_txt2", (0.04, 0.02, 0.06), 1.0)
    lk_m = M.emis("placa_like", (0.9, 0.1, 0.2), 1.2)
    pw, ph = 0.84 * kw, 0.118 * kh
    pan = M.box("placa_painel", (pw, ph, 0.002), (0, 0, 0), pan_m, min(ph * 0.45, 0.02), parent=card)
    shd = M.box("placa_sombra", (pw, ph, 0.001), (0.006 * kw, -0.012 * kh, -0.003), sh_m, min(ph * 0.45, 0.02), parent=card)
    bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=ph * 0.32, depth=0.002, location=(-pw / 2 + ph * 0.45, 0, 0.0015))
    av = bpy.context.object; av.name = "placa_avatar"; M.setmat(av, av_m); av.parent = card
    tn = text_obj("N", ph * 0.4, M.emis("avatar_letra", (1, 1, 1), 1.2), (-pw / 2 + ph * 0.45, -ph * 0.02, 0.0028), card, align='CENTER')
    x0 = -pw / 2 + ph * 0.9
    tx1 = text_obj("@Niko_com_k", ph * 0.24, t1m, (x0, ph * 0.2, 0.0025), card)
    tx2 = text_obj("A galinha eu acho", ph * 0.34, t2m, (x0, -ph * 0.17, 0.0025), card)
    for o in desc_meshes(card):
        o.visible_shadow = False
    f_in = fb2 + 2
    K(card, "scale", 1, (0.0005,) * 3); K(card, "scale", f_in - 1, (0.0005,) * 3); K(card, "scale", f_in + 4, (1.12,) * 3); K(card, "scale", f_in + 8, (1, 1, 1))
    K(card, "scale", S["B2_comentario"]["f1"], (1, 1, 1)); K(card, "scale", S["B2_comentario"]["f1"] + 1, (0.0005,) * 3)
    K(card, "rotation_euler", f_in, (0, 0, math.radians(-3))); K(card, "rotation_euler", f_in + 8, (0, 0, math.radians(1.5))); K(card, "rotation_euler", f_in + 40, (0, 0, math.radians(-1)))
    # ---------- QA
    qa_key("galinha", gal["root"]); qa_key("pipo_espiga", ns["kern"]); qa_key("vaso", qt["vaso"]); qa_key("placa", card)
    qa_key("mesa", *mesa_objs); qa_key("galinhas_quintal", *extra)
    qa_tela("galinha", "galinhas_quintal")
    gol = M._ref(gal["head_pose"], "ref_olho")
    qa_foco("B1_match", gol, M._ref(gal["head_pose"], "ref_ponta")); qa_foco("B2_comentario", gol, card)
    qa_foco("B3_quintal", gol, pf); qa_foco("B4_pipo_congela", pf)
    qa_foco("B5_fuga", pf, gol)
    qa_foco("B8_mesa", coxa); qa_foco("B9_almoco", coxa)
    qa_inteiro("B2_comentario", "placa", "galinha"); qa_inteiro("B3_quintal", "pipo_espiga", "galinha")
    qa_tela("pipo_espiga", "vaso")  # a Pipo passa ao lado/atras do vaso na fuga (BVH limpo: nao encosta)
    qa_tela("galinha", "vaso")      # a galinha passa ATRAS do vaso (longe em profundidade); o BVH continua valendo
    return dict(cam=cam, ev=ev)


# ================================================================ MUNDO C: comparacao (C1-C6, C7-C8)
def trex_corpo_v2(rex, m):
    """corpo novo: peito fundo, cintura marcada antes do quadril, coxa musculosa (coxa de galinha gigante),
    canela fina, metatarso longo, cauda grossa na base. Substitui o corpo-feijao."""
    old = rex["body"]
    D.objects.remove(old, do_unlink=True)
    sp = [(0, -1.75, 2.55), (0, -1.25, 2.45), (0, -0.6, 2.42), (0, 0.15, 2.55), (0, 0.95, 2.78), (0, 1.6, 3.0), (0, 2.4, 3.22),
          (0, 3.3, 3.22), (0, 4.5, 3.05), (0, 5.9, 2.85), (0, 7.3, 2.62), (0, 8.6, 2.42), (0, 9.7, 2.25)]
    sr = [(0.42, 0.5), (0.56, 0.7), (0.8, 1.02), (0.86, 1.12), (0.7, 0.88), (0.5, 0.64), (0.66, 0.8), (0.6, 0.66), (0.46, 0.5),
          (0.33, 0.36), (0.21, 0.23), (0.11, 0.12), (0.03, 0.03)]
    verts = list(sp); rad = list(sr); edges = M.chain(len(sp))
    legs = {}
    for sx in (1, -1):
        i0 = len(verts)
        verts += [(sx * 0.6, 2.5, 2.75), (sx * 0.8, 2.15, 1.95), (sx * 0.82, 1.72, 1.3), (sx * 0.8, 2.05, 0.82), (sx * 0.8, 2.38, 0.42), (sx * 0.82, 2.0, 0.13)]
        rad += [(0.6, 0.78), (0.52, 0.62), (0.27, 0.27), (0.2, 0.2), (0.15, 0.15), (0.17, 0.1)]
        edges += [(6, i0), (i0, i0 + 1), (i0 + 1, i0 + 2), (i0 + 2, i0 + 3), (i0 + 3, i0 + 4), (i0 + 4, i0 + 5)]
        legs[sx] = [verts[i0 + k] for k in range(6)]
        i1 = len(verts)
        verts += [(sx * 0.55, -0.45, 2.05), (sx * 0.66, -0.72, 1.78), (sx * 0.6, -0.92, 1.7)]
        rad += [0.12, 0.08, 0.05]
        edges += [(2, i1), (i1, i1 + 1), (i1 + 1, i1 + 2)]
    body = M.skin_model("rex_corpo_v2", verts, edges, rad, m)
    body.parent = rex["root"]
    rex["body"] = body
    return sp, legs


def build_C():
    cp = M.mundo_comparacao()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    sc.cycles.transparent_max_bounces = 12
    rex, gal, cam = cp["rex"], cp["galinha"], cp["cam"]
    S = SH
    for o in (rex["jaw"], rex["head_anim"], gal["jaw"], gal["head_anim"]):
        o.animation_data_clear()
    # materiais com raio-x animavel (um para cada bicho: o corte troca de um para o outro)
    rex_m, rex_x = mat_mix_xray("sil_rex")
    gal_m, gal_x = mat_mix_xray("sil_gal", xs=0.3)
    sp, legs = trex_corpo_v2(rex, rex_m)
    for d_, m_ in ((rex, rex_m), (gal, gal_m)):
        for o in D.objects:
            if under(o, d_["root"]) and o.type in ('MESH', 'CURVE') and not o.name.startswith("furcula"):
                o.data.materials.clear(); o.data.materials.append(m_)
    # garras no pe novo
    for o in list(rex["root"].children):
        if o.name.startswith("rex_garra"):
            o.location.y += 0.1
    f_x_on = f(wt("peito")); f_x_off = S["C7_penas_escamas"]["f0"]
    key_val(rex_x, [(1, 0.0), (f_x_on - 1, 0.0), (f_x_on + 9, 1.0), (f_x_off - 1, 1.0), (f_x_off, 0.0)])
    key_val(gal_x, [(1, 0.0), (F_FRANGO - 1, 0.0), (F_FRANGO, 1.0), (f_x_off - 1, 1.0), (f_x_off, 0.0)])
    nt_interp(rex_m.node_tree); nt_interp(gal_m.node_tree)
    for nt_ in (rex_m.node_tree, gal_m.node_tree):
        for fc in M.fcurves_nt(nt_):
            for k in fc.keyframe_points:
                if int(k.co.x) in (F_FRANGO - 1, f_x_off - 1):
                    k.interpolation = 'CONSTANT'
    # penas da galinha somem no raio-x (sobra o corpo translucido)
    feathers = [o for o in D.objects if under(o, gal["root"]) and o.type == 'MESH' and o.data.name.startswith("pena")]
    key_hide(feathers, [(1, False), (F_FRANGO, True), (f_x_off, False)])
    # ---------- esqueleto do T. rex (so aparece no raio-x)
    bone_m = M.emis("osso_xray", (0.55, 0.75, 0.95), 0.35)
    skel = M.empty("rex_esqueleto", (0, 0, 0), rex["root"])
    for i in range(len(sp) - 1):
        a, b = Vector(sp[i]), Vector(sp[i + 1])
        n = max(1, int((b - a).length / 0.32))
        for k in range(n):
            p = a.lerp(b, k / n)
            rr = 0.06 * (1 - i / len(sp)) + 0.018
            M.sph("vertebra", rr, (p.x, p.y, p.z + 0.05), bone_m, seg=10, rings=6, scale=(1, 0.7, 1), parent=skel)
    for y in [-1.1 + 0.27 * k for k in range(9)]:
        zc = 2.45 + 0.12 * (y + 1.1)
        w = 0.62 + 0.25 * math.sin(math.pi * (y + 1.1) / 2.4)
        hgt = 0.75 + 0.3 * math.sin(math.pi * (y + 1.1) / 2.4)
        for sx in (1, -1):
            pts = [(0, y, zc + 0.15), (sx * w * 0.75, y + 0.05, zc + 0.05), (sx * w, y + 0.12, zc - hgt * 0.45), (sx * w * 0.7, y + 0.15, zc - hgt * 0.95), (sx * 0.1, y + 0.1, zc - hgt * 1.05)]
            rb = M.tube("costela", pts, 0.018, bone_m, res=2); rb.parent = skel
    fibra_m = M.emis("fibra", (1.0, 0.85, 0.35), 0.0)
    fib_s = fibra_m.node_tree.nodes["Emission"].inputs["Strength"]
    femurs = {}
    for sx in (1, -1):
        a, b = Vector(legs[sx][0]) + Vector((0, 0, -0.05)), Vector(legs[sx][2])
        fm_ = M.tube("femur_rex", [tuple(a), tuple(a.lerp(b, 0.5) + Vector((0, 0.04, 0))), tuple(b)], 0.085, bone_m, res=3); fm_.parent = skel
        M.sph("femur_cabeca", 0.13, tuple(a), bone_m, parent=skel); M.sph("femur_joelho", 0.12, tuple(b), bone_m, parent=skel)
        sh_ = M.tube("tibia_rex", [tuple(b), tuple(legs[sx][3]), tuple(legs[sx][4])], 0.06, bone_m, res=2); sh_.parent = skel
        mt = M.tube("metatarso_rex", [tuple(legs[sx][4]), tuple(legs[sx][5])], 0.05, bone_m, res=2); mt.parent = skel
        femurs[sx] = (a, b)
    def fibras(parent, a, b, rad, nome):
        out = []
        ax = (b - a)
        u1 = ax.orthogonal().normalized(); u2 = ax.normalized().cross(u1)
        for j in range(6):
            pts = []
            for k in range(13):
                t = k / 12
                ang = j * math.pi / 3 + t * math.pi * 2.2
                pts.append(tuple(a.lerp(b, 0.08 + 0.84 * t) + (u1 * math.cos(ang) + u2 * math.sin(ang)) * rad))
            fb = M.tube(nome, pts, rad * 0.11, fibra_m, res=1); fb.parent = parent
            out.append(fb)
        return out
    fib_rex = fibras(skel, femurs[1][0], femurs[1][1], 0.1, "fibra_rex")
    # esqueleto da galinha (perna/femur) para o plano da proteina
    gskel = M.empty("gal_esqueleto", (0, 0, 0), gal["body"])
    ga, gb = Vector((1.0, 0.9, 5.0)), Vector((1.15, -0.3, 3.2))
    M.tube("femur_gal", [tuple(ga), tuple(ga.lerp(gb, 0.5) + Vector((0.08, 0, 0))), tuple(gb)], 0.22, bone_m, res=3).parent = gskel
    M.sph("femur_gal_c", 0.32, tuple(ga), bone_m, parent=gskel); M.sph("femur_gal_j", 0.3, tuple(gb), bone_m, parent=gskel)
    fib_gal = fibras(gskel, ga, gb, 0.26, "fibra_gal")
    key_hide([o for o in skel.children_recursive], [(1, True), (f_x_on, False), (S["C7_penas_escamas"]["f0"], True)])
    key_hide([o for o in gskel.children_recursive], [(1, True), (F_FRANGO, False), (S["C7_penas_escamas"]["f0"], True)])
    f_prot = f(wt("proteína")); f_gal2 = f(wt("galinha", 2))
    key_val(fib_s, [(1, 0), (f_prot - 6, 0), (f_prot + 4, 6), (f_prot + 14, 3), (f_gal2 - 2, 3), (f_gal2 + 3, 8), (f_gal2 + 14, 3.5)])
    nt_interp(fibra_m.node_tree)
    # furculas: dentro do peito (rex) e dentro do corpo (galinha), mesma forma; acendem no "ossinho"
    for o in cp["furculas"]:
        for c in list(o.children_recursive) + [o]:
            D.objects.remove(c, do_unlink=True)
    fm = D.materials["furcula"]; hm = D.materials["furcula_halo"]
    fem = fm.node_tree.nodes["Emission"].inputs["Strength"]
    hem = [n for n in hm.node_tree.nodes if n.type == 'EMISSION'][0].inputs["Strength"]
    key_val(fem, [(1, 0.6), (F_OSSINHO - 2, 0.6), (F_OSSINHO + 4, 14), (F_OSSINHO + 12, 7), (f_x_off - 1, 7), (f_x_off, 0.0)])
    key_val(hem, [(1, 0.0), (F_OSSINHO - 2, 0.0), (F_OSSINHO + 4, 0.35), (F_OSSINHO + 12, 0.15), (f_x_off - 1, 0.15), (f_x_off, 0.0)])
    nt_interp(fm.node_tree); nt_interp(hm.node_tree)
    fr_rex = M._furcula("furcula_rex", rex["root"], (0, -1.15, 2.55), 1.15, 1.0, 0.07, fm, hm, 0.9)
    fr_rex.rotation_euler = (math.radians(-22), 0, 0)
    fr_gal = M._furcula("furcula_gal", gal["body"], (0, -2.05, 7.05), 1.15, 1.0, 0.07, fm, hm, 0.9)
    fr_gal.rotation_euler = (math.radians(-22), 0, 0); fr_gal.scale = (1.75, 1.75, 1.75)
    # ---------- fundo escuro e limpo no raio-x (C3 a C6): esfera escura em volta dos dois
    fx_m = M.emis("fundo_xray", (0.004, 0.008, 0.02), 1.0)
    fundo = M.sph("fundo_xray", 28, tuple(rex["root"].location + Vector((0, 0, 0))), fx_m, seg=48, rings=24)
    fundo.visible_shadow = False
    vis_window([fundo], f_x_on, S["C6_femur_galinha"]["f1"])
    for lo in [o for o in D.objects if o.type == 'LIGHT' and o.data.type == 'AREA']:
        e0 = lo.data.energy
        light_keys(lo, [(1, e0), (f_x_on - 1, e0), (f_x_on, 0.0), (S["C6_femur_galinha"]["f1"], 0.0), (S["C6_femur_galinha"]["f1"] + 1, e0)])
    # ---------- anima: rugido e cacarejo juntos no "dinossauro"
    f_din = f(wt("dinossauro", 2))
    roar_keys(rex, f_din - 14, f_din, f_din + 24, f_din + 40, jaw=36, lunge=0.3)
    jw, ha = gal["jaw"], gal["head_anim"]
    for fr, a in ((f_din - 14, 2), (f_din, 30), (f_din + 5, 22), (f_din + 10, 30), (f_din + 24, 26), (f_din + 40, 2)):
        K(jw, "rotation_euler", fr, (math.radians(a), 0, 0))
    for fr, loc, rx in ((f_din - 14, (0, 0.05, 0.01), -4), (f_din, (0, -0.3, -0.05), 4), (f_din + 24, (0, -0.26, -0.03), 3), (f_din + 40, (0, 0, 0), 0)):
        K(ha, "location", fr, loc); K(ha, "rotation_euler", fr, (math.radians(rx), 0, 0))
    # a galinha grande sai do plano final (silhueta do T. rex sozinha)
    fc7 = S["C7_penas_escamas"]["f0"]
    key_scale_vis(gal["root"], [(1, True), (fc7, False)])
    # ---------- metade penas, metade escamas (so no final)
    fe_m = M.feather_mesh("pena_rex", 1.0, 0.5, 0.06)
    penas = M.empty("rex_penas", (0, 0, 0), rex["root"])
    random.seed(17)
    npen = 0
    body = rex["body"]
    deps = bpy.context.evaluated_depsgraph_get()
    be = body.evaluated_get(deps); bme = be.to_mesh()
    cand = [(v.co.copy(), v.normal.copy()) for v in bme.vertices]
    be.to_mesh_clear()
    for co, nr in cand:
        if co.y > 1.9 or co.y < -1.8 or nr.z < -0.2 or abs(co.x) > 0.95 or co.z < 1.6:
            continue
        if random.random() > 0.45:
            continue
        dirv = Vector((0, 1, -0.35)) - nr * Vector((0, 1, -0.35)).dot(nr)
        M._place_feather(fe_m, rex_m, penas, co, dirv.normalized(), nr, random.uniform(0.75, 1.05), lift=0.45)
        npen += 1
    hd = rex["head_anim"]
    for k in range(26):         # penugem no alto da cabeca e na nuca
        y = 0.25 - k * 0.04; x = random.uniform(-0.25, 0.25)
        M._place_feather(fe_m, rex_m, hd, (x, y, 0.42 - 0.12 * abs(x) * 2), Vector((0, 1, 0.25)).normalized(), Vector((x, 0, 1)), random.uniform(0.38, 0.5), lift=0.55)
    pen_objs = [o for o in D.objects if o.data is not None and getattr(o.data, "name", "").startswith("pena_rex")]
    key_hide(pen_objs, [(1, True), (fc7, False)])
    # escamas: placas osseas (escudos) na metade de tras e na cauda
    esc_m, esc_x = mat_mix_xray("sil_escama", rim_col=(1.0, 0.55, 0.25), rim=4.0)
    rim_node = [n for n in esc_m.node_tree.nodes if n.type == 'MATH' and n.operation == 'MULTIPLY_ADD' and abs(n.inputs[1].default_value - 4.0) < 1e-6][0]
    f_esc = f(wt("escamas"))
    key_val(rim_node.inputs[1], [(1, 4.0), (f_esc - 2, 4.0), (f_esc + 4, 14.0), (f_esc + 16, 5.0)])
    nt_interp(esc_m.node_tree)
    escudos = M.empty("rex_escamas", (0, 0, 0), rex["root"])
    deps = bpy.context.evaluated_depsgraph_get()
    for y in [2.0 + 0.34 * k for k in range(23)]:
        for xo in ((0.0,) if y > 6.5 else (0.0, 0.22, -0.22)):
            ok, hit, nrm_, _ = body.ray_cast(Vector((xo, y, 12)), Vector((0, 0, -1)), depsgraph=deps)
            if not ok:
                continue
            hh = 0.07 + 0.16 * max(0.0, 1 - (y - 2.0) / 8.0) * (1.0 if xo == 0 else 0.7)
            c = M.cone("escudo", hh * 0.55, 0.0, hh, (hit.x, hit.y, hit.z + hh * 0.35), (math.radians(-28), math.copysign(math.radians(18), xo) if xo else 0, 0),
                       esc_m, parent=escudos, verts=6)
    esc_objs = list(escudos.children)
    key_hide(esc_objs, [(1, True), (fc7, False)])
    for o in esc_objs:
        o.data.materials.clear(); o.data.materials.append(esc_m)
    f_pen = f(wt("penas"))
    K(penas, "scale", fc7, (1, 1, 1)); K(penas, "scale", f_pen - 1, (1, 1, 1)); K(penas, "scale", f_pen + 4, (1.035, 1.03, 1.05)); K(penas, "scale", f_pen + 12, (1, 1, 1))
    # o T. rex respira e vira a cabeca para a camera no "Comenta"
    f_com = f(wt("comenta"))
    for fr in range(fc7, N, 30):
        K(rex["body"], "scale", fr, (1, 1, 1)); K(rex["body"], "scale", fr + 15, (1.01, 1.0, 1.015))
    K(ha, "rotation_euler", fc7, (0, 0, 0))
    K(rex["head_anim"], "rotation_euler", fc7, (0, 0, 0)); K(rex["head_anim"], "rotation_euler", f_com - 10, (0, 0, 0))
    K(rex["head_anim"], "rotation_euler", f_com + 4, (math.radians(-6), 0, math.radians(-38)))
    K(rex["jaw"], "rotation_euler", f_com - 10, (math.radians(5), 0, 0)); K(rex["jaw"], "rotation_euler", f_com + 2, (math.radians(16), 0, 0)); K(rex["jaw"], "rotation_euler", f_com + 12, (math.radians(4), 0, 0))
    # ---------- perseguicao Pipo x galinha, pequena, em loop no caminho de fundo
    rroot = rex["root"]
    bpy.context.view_layer.update()
    R = rroot.matrix_world.to_3x3().normalized()
    head_dir = (R @ Vector((0, -1, 0))).normalized()
    side = (R @ Vector((1, 0, 0))).normalized()
    rex_c = rroot.matrix_world @ Vector((0, 2.0, 0))
    cam_side = 1.0                                     # a camera do final fica do lado +x do T. rex
    CH_OFF = float(os.environ.get('CH_OFF', '-3.0'))
    cam7 = rex_c + side * 20.0 + head_dir * 8.5 + Vector((0, 0, 1.3))
    tg7 = rex_c + Vector((0, 0, 2.3)) + head_dir * 0.6
    vdir = Vector(((tg7 - cam7).x, (tg7 - cam7).y, 0)).normalized()
    path_c = Vector((rex_c.x, rex_c.y, 0)) + vdir * 9.0 - Vector((-vdir.y, vdir.x, 0)) * CH_OFF   # 6 m alem do T. rex, um pouco ao lado do corpo
    caminho = [(x, 0.0) for x in (4.5, 3, 1.5, 0, -1.5, -3, -4.5)]   # mesmo caminho_fundo do quintal (x de 4,5 a -4,5)
    escala_c = 1.2
    perp = Vector((vdir.y, -vdir.x, 0))
    p_ini = path_c + perp * (caminho[0][0] * escala_c)
    p_fim = path_c + perp * (caminho[-1][0] * escala_c)
    chase = M.empty("perseguicao", (0, 0, 0))
    gch = M.galinha((0, 0, 0), 0.0, scale=M.CU * 3.6)
    gch["root"].parent = chase
    ns = M._load_pipo()
    sc.view_settings.view_transform = 'Standard'
    sc.cycles.max_bounces = 2; sc.cycles.diffuse_bounces = 1; sc.cycles.transparent_max_bounces = 12
    try:
        sc.cycles.denoising_input_passes = 'RGB'; sc.cycles.use_light_tree = False
    except Exception:
        pass
    pipo = ns["pipo"]; FK = ns["FK"]
    ns["pipo_place"](0, 0, 1.1)
    pipo.parent = chase
    run_dir = (p_fim - p_ini).normalized()
    yaw = math.atan2(-run_dir.x, run_dir.y)           # frente local -Y da galinha/Pipo apontando para onde correm
    P = 66
    f_ch0 = fc7 - 30
    for o_, lead in ((pipo, 2.2), (gch["root"], 0.0)):
        a_ = p_ini + run_dir * lead; b_ = p_fim + run_dir * lead
        K(o_, "location", f_ch0, (a_.x, a_.y, 0.0)); K(o_, "location", f_ch0 + P, (b_.x, b_.y, 0.0))
        o_.rotation_euler = (0, 0, yaw + math.pi)
        for fc in M.fcurves(o_):
            if fc.data_path == "location":
                for k in fc.keyframe_points:
                    k.interpolation = 'LINEAR'
                fc.modifiers.new('CYCLES')
    gr_ = gch["root"]; gr_.rotation_euler = (0, 0, yaw + math.pi)
    for i, fr in enumerate(range(f_ch0, f_ch0 + P + 1, 4)):
        sg = 1 if i % 2 else -1
        K(gch["legs"][0], "rotation_euler", fr, (math.radians(35 * sg), 0, 0)); K(gch["legs"][1], "rotation_euler", fr, (math.radians(-35 * sg), 0, 0))
        K(gch["body"], "location", fr, (0, 0, 0.6 if i % 2 else 0.0)); K(gch["body"], "rotation_euler", fr, (math.radians(-12), 0, math.radians(5 * sg)))
        K(gch["neck"], "rotation_euler", fr, (math.radians(18 + 6 * sg), 0, 0))
    for o_ in (gch["legs"][0], gch["legs"][1], gch["body"], gch["neck"]):
        for fc in M.fcurves(o_):
            fc.modifiers.new('CYCLES')
    bdy = ns["body"]
    for i, fr in enumerate(range(f_ch0, f_ch0 + P + 1, 9)):
        K(bdy, "location", fr, (0, 0, 0)); K(bdy, "location", fr + 4, (0, 0, 0.32)); K(bdy, "location", fr + 9, (0, 0, 0))
    for fc in M.fcurves(bdy):
        if fc.data_path == "location":
            fc.modifiers.new('CYCLES')
    ns["set_face"](FK, fc7 - 30, lid=-55, brow=(15, 0.33), browL=(15, 0.33), look=(-30, 4))
    # a pena de galinha que gruda na cabeca da Pipo (gancho do proximo video: ela aparece com a pena)
    pena_m = [o for o in gch["root"].children_recursive if o.type == 'MESH' and o.data.name.startswith("pena_corpo")][0].data.materials[0]
    bpy.context.view_layer.update()
    kern = ns["kern"]
    top_local = max((Vector(c) for c in kern.bound_box), key=lambda v: v.z)
    pena = M.link(D.objects.new("pena_na_pipo", M.feather_mesh("pena_pipo", 1.0, 0.45, 0.1)))
    pena.data.materials.append(pena_m)
    pena.parent = kern
    pena.location = (top_local.x + 0.05, top_local.y, top_local.z - 0.08)
    pena.rotation_euler = (math.radians(-20), math.radians(35), math.radians(10))
    f_pena = f(wt("escamas")) + 10            # no plano em que a perseguicao passa visivel
    K(pena, "scale", 1, (0.0005,) * 3); K(pena, "scale", f_pena - 1, (0.0005,) * 3); K(pena, "scale", f_pena + 3, (0.62,) * 3); K(pena, "scale", f_pena + 7, (0.5,) * 3)
    for k_ in range(f_pena + 7, N, 8):
        K(pena, "rotation_euler", k_, (math.radians(-20 + (8 if (k_ // 8) % 2 else -8)), math.radians(35), math.radians(10)))
    key_scale_vis(chase, [(1, False), (fc7, True)], base=(1, 1, 1))
    vis_window([chase], fc7, N)
    lchase = M.light('AREA', tuple(path_c + side * 4 + Vector((0, 0, 3))), tuple(path_c + Vector((0, 0, 0.4))), 0, (1.0, 0.75, 0.5), size=6)
    only_during(lchase, fc7, N, 900)
    # ---------- Wonderchicken (C9, C10): praia de mar raso e quente (Belgica no fim do Cretaceo), meio galinha, meio pato
    fw0, fw1 = S["C9_wonder_praia"]["f0"], S["C10_wonder_pato"]["f1"]
    WX, WYb = 26.0, -16.0
    areia = M.pbr("areia", (0.78, 0.62, 0.4), (0.7, 0.55, 0.34), (0.85, 0.72, 0.5), rough=0.9, nscale=6, nbump=0.35, nbscale=60)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=30, size=1, location=(WX, WYb - 2.0, 0.0))
    praia = bpy.context.object; praia.name = "praia"; praia.scale = (16, 7, 1)
    for v in praia.data.vertices:          # desce suave para dentro d'agua (+y)
        v.co.z = -0.06 * max(0.0, v.co.y + 0.05) * 14
    M.setmat(praia, areia)
    dd = praia.modifiers.new("d", 'DISPLACE'); txp = D.textures.new("dunas", 'CLOUDS'); txp.noise_scale = 0.6; dd.texture = txp; dd.strength = 0.05
    concha_m = M.pbr("concha", (0.95, 0.85, 0.75), (0.9, 0.6, 0.45), rough=0.4, nscale=20)
    random.seed(9)
    conchas = [M.sph("concha", random.uniform(0.02, 0.035), (WX + random.uniform(-1.6, 1.6), WYb + random.uniform(-1.2, 0.4), 0.01), concha_m, seg=10, rings=6, scale=(1, 0.7, 0.4)) for _ in range(14)]
    wc = M.galinha((WX + 0.35, WYb, 0.0), math.radians(-90), scale=M.CU * 2.0)
    wco = wc["head_objs"]
    wco[11].scale = (0.32, 0.32, 0.32)                    # crista pequena (ave antiga)
    wco[17].scale = (0.25, 0.25, 0.25)                    # quase sem barbela
    for i_, s1 in ((12, (2.0, 1.15, 0.7)), (13, (2.0, 1.15, 0.8))):    # bico largo e chato: meio pato
        b0 = tuple(wco[i_].scale); wco[i_].scale = tuple(b0[j] * s1[j] for j in range(3))
    bico_m = M.pbr("wc_bico_pato", (0.32, 0.3, 0.22), (0.22, 0.2, 0.16), rough=0.35, nscale=10, spec=0.8)
    for i_ in (12, 13):
        M.setmat(wco[i_], bico_m)
    # anda pela beira d'agua (perfil) e no "pato" vira de frente e grasna
    f_wg = f(wt("galinha", 3)); f_pt = f(wt("pato"))
    wr = wc["root"]
    K(wr, "location", fw0, (WX + 0.35, WYb, 0.0)); K(wr, "location", f_wg + 6, (WX - 0.15, WYb, 0.0)); K(wr, "location", fw1, (WX - 0.2, WYb, 0.0))
    for i_, fr in enumerate(range(fw0, f_wg + 6, 6)):
        sg = 1 if i_ % 2 else -1
        K(wc["legs"][0], "rotation_euler", fr, (math.radians(22 * sg), 0, 0)); K(wc["legs"][1], "rotation_euler", fr, (math.radians(-22 * sg), 0, 0))
        K(wc["neck"], "location", fr, (0, -1.8 + (-0.35 if i_ % 2 else 0.25), 8.0))       # cabeca vai e volta ao andar
    for lg in wc["legs"]:
        K(lg, "rotation_euler", f_wg + 8, (0, 0, 0))
    K(wc["neck"], "location", f_wg + 8, (0, -1.8, 8.0))
    K(wc["neck"], "rotation_euler", f_wg - 2, (0, 0, 0)); K(wc["neck"], "rotation_euler", f_wg + 4, (math.radians(-10), 0, math.radians(8))); K(wc["neck"], "rotation_euler", f_wg + 14, (0, 0, 0))
    K(wc["neck"], "rotation_euler", f_pt - 6, (0, 0, 0)); K(wc["neck"], "rotation_euler", f_pt + 2, (math.radians(-8), 0, math.radians(-55)))
    K(wc["neck"], "rotation_euler", fw1, (math.radians(-6), 0, math.radians(-58)))
    wj = wc["jaw"]
    for fr, a in ((f_pt - 2, 2), (f_pt + 3, 28), (f_pt + 8, 6), (f_pt + 12, 26), (f_pt + 18, 3)):
        K(wj, "rotation_euler", fr, (math.radians(a), 0, 0))
    lwc = M.light('AREA', (WX + 1.6, WYb - 2.4, 1.6), (WX, WYb, 0.4), 0, (1.0, 0.78, 0.55), size=2.0)
    only_during(lwc, fw0, fw1, 320)
    lwc2 = M.light('AREA', (WX - 2.0, WYb - 0.8, 1.0), (WX, WYb, 0.5), 0, (1.0, 0.6, 0.35), size=1.5)
    only_during(lwc2, fw0, fw1, 120)
    vis_window([praia, wc["root"]] + conchas, fw0, fw1)
    wc_eye = M._ref(wc["head_pose"], "ref_olho"); wc_tip = M._ref(wc["head_pose"], "ref_ponta")

    # ---------- camera
    C = Cam(cam)
    sc.frame_set(1)
    bpy.context.view_layer.update()
    ctr = (rroot.matrix_world.translation + gal["root"].matrix_world.translation) * 0.5 + Vector((0, 0, 1.6))
    v0 = Vector((0.6, -8.0, 0.75)) - Vector((ctr.x, ctr.y, 0.75))
    r0 = v0.length; a0 = math.atan2(v0.y, v0.x)

    def c1(u, fr):        # orbita lenta em volta dos dois (galinha na frente, T. rex atras em escala)
        a = a0 - math.radians(36) * ease(u)
        loc = Vector((ctr.x + math.cos(a) * r0 * (1 - 0.08 * u), ctr.y + math.sin(a) * r0 * (1 - 0.08 * u), 0.75 + 0.5 * u))
        return dict(loc=loc, tgt=Vector((ctr.x, ctr.y, 2.0)), lens=30, sy=-0.02, fd=r0, fs=11)
    C.shot(S["C1_orbita"], c1)

    def c2(u, fr):        # baixo e de frente: rugido e cacarejo juntos
        loc = Vector((1.8 - 0.3 * u, -6.6 + 0.9 * ease(u), 0.55))
        return dict(loc=loc, tgt=Vector((0.4, 3.0, 2.25)), lens=28, sy=-0.02, fd=7.5, fs=11)
    C.shot(S["C2_lado_a_lado"], c2)
    # raio-x: a camera atravessa o peito ate a furcula
    furl = fr_rex
    bpy.context.view_layer.update()
    fw = furl.matrix_world.translation.copy()
    fdir = (R @ Vector((0.9, -0.25, 0.08))).normalized()       # lado da camera, um pouco de frente

    def c3(u, fr):
        k = ease(u)
        loc = fw + fdir * (8.0 - 2.4 * k) + Vector((0, 0, 0.5 - 0.2 * k))
        return dict(loc=loc, tgt=fw + Vector((0, 0, 0.15)), lens=30, fd=(loc - fw).length, fs=8, sy=0.0)
    C.shot(S["C3_raiox"], c3)
    loc3 = fw + fdir * 3.9 + Vector((0, 0, 0.3))

    fdir2 = (R @ Vector((0.55, -0.83, 0.05))).normalized()     # de frente/lado: cabeca e peito juntos
    tgt3 = fw + (R @ Vector((0, -0.55, 0.25)))

    def c3b(u, fr):       # o peito em raio-x: cabeca e peito legiveis, costelas discretas, a furcula em V acende no "ossinho"
        k = ease(u)
        loc = lerp(fw + fdir2 * 5.2 + Vector((0, 0, 0.2)), fw + fdir2 * 3.6 + Vector((0, 0, 0.1)), k)
        return dict(loc=loc, tgt=tgt3, lens=30, fd=(loc - fw).length, fs=8, sy=0.0)
    C.shot(S["C3b_dentro"], c3b)
    sc.frame_set(S["C3b_dentro"]["f1"])
    bpy.context.view_layer.update()
    # a camera no fim do plano, no espaco local da furcula do T. rex -> mesma pose relativa na furcula da galinha
    lastc = cam.matrix_world.copy()
    rel = fr_rex.matrix_world.inverted() @ lastc

    def c4(u, fr):        # corte: a furcula da galinha no mesmo lugar da tela, depois recua revelando a galinha
        mwg = fr_gal.matrix_world @ rel
        loc0 = mwg.translation; rot = mwg.to_3x3().normalized().to_quaternion()
        back = (mwg.to_3x3().normalized() @ Vector((0, 0, 1))).normalized()
        loc = loc0 + back * 0.25 * ease(u)
        return dict(loc=loc, rot=rot, lens=30, fd=(loc - fr_gal.matrix_world.translation).length, fs=8, sy=0.0)
    C.shot(S["C4_furcula_galinha"], c4, track=True)
    fa_, fb_ = rroot.matrix_world @ femurs[1][0], rroot.matrix_world @ femurs[1][1]
    fmid = (fa_ + fb_) * 0.5

    def c5(u, fr):        # femur do T. rex em raio-x, a camera desliza de lado; fibras acendem
        loc = fmid + side * (4.6 - 0.3 * u) + head_dir * (1.2 - 2.0 * ease(u)) + Vector((0, 0, 0.6))
        return dict(loc=loc, tgt=fmid + Vector((0, 0, 0.1)), lens=35, fd=(loc - fmid).length, fs=5, sy=0.0)
    C.shot(S["C5_femur_rex"], c5)
    gmw = gskel.matrix_world
    gfa, gfb = gmw @ ga, gmw @ gb
    gmid = (gfa + gfb) * 0.5
    gs = (gfa - gfb).length / (fa_ - fb_).length

    def c6(u, fr):        # mesmo movimento no femur da galinha (escala da galinha)
        Rg = gal["root"].matrix_world.to_3x3().normalized()
        sideg = (Rg @ Vector((1, 0, 0))).normalized(); headg = (Rg @ Vector((0, -1, 0))).normalized()
        loc = gmid + sideg * (4.6 - 0.3 * u) * gs + headg * (1.2 - 2.0 * ease(u)) * gs + Vector((0, 0, 0.6 * gs))
        return dict(loc=loc, tgt=gmid + Vector((0, 0, 0.1 * gs)), lens=35, fd=(loc - gmid).length, fs=5, sy=0.0)
    C.shot(S["C6_femur_galinha"], c6)
    def c9(u, fr):        # perfil, cameras baixa na areia, o mar raso e o sol quente atras
        hd_ = wpos(wc_eye)
        loc = Vector((WX + 0.05 - 0.2 * u, WYb - 2.7, 0.45))
        return dict(loc=loc, tgt=Vector((hd_.x + 0.62, WYb, 0.5)), lens=33, fd=(loc - hd_).length, fs=5, sy=0.0)
    C.shot(S["C9_wonder_praia"], c9, track=True)

    def c10(u, fr):       # de frente: o bico de pato grasna
        hd_ = (wpos(wc_eye) + wpos(wc_tip)) * 0.5
        loc = hd_ + Vector((-0.95 + 0.1 * ease(u), -0.4, 0.06))
        return dict(loc=loc, tgt=hd_ + Vector((0, 0, -0.07)), lens=50, fd=(loc - hd_).length, fs=4, sy=0.0)
    C.shot(S["C10_wonder_pato"], c10, track=True)
    hpw = rex["head_pose"].matrix_world.translation.copy()
    prof = rex_c + side * cam_side * 21.0 + Vector((0, 0, 1.5))

    def c7(u, fr):        # silhueta meio pena (frente) e meio escama (cauda), 3/4 de perfil; perseguicao pequena e desfocada atras
        loc = rex_c + side * (20.0 - 1.0 * ease(u)) + head_dir * 8.5 + Vector((0, 0, 1.3))
        return dict(loc=loc, tgt=rex_c + Vector((0, 0, 2.3)) + head_dir * 0.6, lens=27, fd=(loc - rex_c).length, fs=3.2, sy=-0.06)
    C.shot(S["C7_penas_escamas"], c7)

    def c8(u, fr):        # 3/4 mais perto da cabeca e do pescoco de penas; ele vira para a camera
        tg = hpw + head_dir * 0.4
        loc = tg + side * (5.2 - 0.4 * ease(u)) + head_dir * 3.6 + Vector((0, 0, -1.3))
        return dict(loc=loc, tgt=tg + Vector((0, 0, -1.25)) - head_dir * 0.8, lens=30, fd=(loc - tg).length, fs=3.5, sy=0.0)
    C.shot(S["C8_comenta"], c8)
    C.done()
    # ---------- QA
    qa_key("rex", rex["root"]); qa_key("galinha", gal["root"]); qa_key("galinha_peq", gch["root"]); qa_key("pipo_espiga", ns["kern"])
    qa_tela("rex", "galinha"); qa_tela("rex", "galinha_peq"); qa_tela("rex", "pipo_espiga"); qa_tela("galinha_peq", "pipo_espiga")
    ro = M._ref(rex["head_pose"], "ref_olho"); go = M._ref(gal["head_pose"], "ref_olho")
    qa_foco("C1_orbita", ro, go); qa_foco("C2_lado_a_lado", ro, go); qa_foco("C3b_dentro", fr_rex); qa_foco("C4_furcula_galinha", fr_gal)
    fem_e = M.empty("foco_femur_rex", tuple(femurs[1][0].lerp(femurs[1][1], 0.5)), rex["root"])
    gfe = M.empty("foco_femur_gal", tuple(ga.lerp(gb, 0.5)), gal["body"])
    qa_foco("C5_femur_rex", fem_e); qa_foco("C6_femur_galinha", gfe)
    qa_foco("C7_penas_escamas", ro); qa_foco("C8_comenta", ro)
    qa_inteiro("C1_orbita", "galinha"); qa_inteiro("C7_penas_escamas", "rex")
    qa_key("wonderchicken", wc["root"]); qa_foco("C9_wonder_praia", wc_eye); qa_foco("C10_wonder_pato", wc_eye)
    qa_inteiro("C9_wonder_praia", "wonderchicken")
    qa_foco("C7_penas_escamas", pipo, gch["root"])
    return dict(cam=cam)


BUILD = {"A": build_A, "B": build_B, "C": build_C}


def build(world):
    QA["keys"].clear(); QA["touch"].clear(); QA["screen_ok"].clear(); QA["focus"].clear(); QA["inteiros"].clear()
    t = time.time()
    if world == "B" and not os.path.exists(WORK + "/match_refs.json"):
        build_A()
        QA["keys"].clear(); QA["touch"].clear(); QA["screen_ok"].clear(); QA["focus"].clear(); QA["inteiros"].clear()
    r = BUILD[world]()
    sc = bpy.context.scene
    sc.render.filepath = "//frames/f"
    sc.render.use_overwrite = False; sc.render.use_placeholder = True
    print("BUILD", world, round(time.time() - t, 1), "s", len(D.objects), "objetos", flush=True)
    return r


# ================================================================ eventos (formato do kit/compose.py)
def gerar_sfx():
    """efeitos que faltam no kit (rugido, vento, cacarejo, passinhos, madeira rachando), gerados por codigo"""
    import numpy as np, wave
    out = WORK + "/sfx"
    os.makedirs(out, exist_ok=True)
    SR = 48000
    rng = np.random.default_rng(3)

    def save(name, a):
        a = a / (np.abs(a).max() + 1e-9) * 0.9
        w = wave.open(f"{out}/{name}", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes()); w.close()

    def lp(x, k):
        return np.convolve(x, np.ones(k) / k, mode="same")
    t = np.arange(int(2.6 * SR)) / SR
    env = np.minimum(1, t / 0.04) * np.exp(-np.maximum(0, t - 1.2) * 2.2)
    f0 = 62 + 30 * np.exp(-t * 1.5) + 6 * np.sin(2 * np.pi * 7 * t)
    ph = 2 * np.pi * np.cumsum(f0) / SR
    growl = sum(np.sin(ph * h + h) / h for h in range(1, 14)) * (1 + 0.5 * np.sin(2 * np.pi * 23 * t))
    noise = lp(rng.standard_normal(len(t)), 30) * 3
    save("rugido.wav", np.tanh((growl * 0.8 + noise * 0.5) * env * 1.6))
    t = np.arange(int(6 * SR)) / SR
    wn = lp(rng.standard_normal(len(t)), 90) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t) ** 2)
    save("vento.wav", wn * np.minimum(1, t / 0.6) * np.minimum(1, (6 - t) / 0.8))
    t = np.arange(int(0.55 * SR)) / SR
    a = np.zeros_like(t)
    for st, du, fq in ((0.0, 0.09, 520), (0.12, 0.08, 560), (0.24, 0.25, 700)):
        m = (t >= st) & (t < st + du)
        tt = t[m] - st
        fr_ = fq * (1 + 0.35 * tt / du)
        a[m] += np.sign(np.sin(2 * np.pi * np.cumsum(fr_) / SR)) * np.sin(np.pi * tt / du) * 0.5
    save("cacarejo.wav", lp(a, 6))
    t = np.arange(int(1.2 * SR)) / SR
    a = np.zeros_like(t)
    for k in range(10):
        st = int((0.02 + k * 0.11) * SR)
        b = rng.standard_normal(int(0.03 * SR)) * np.exp(-np.arange(int(0.03 * SR)) / (0.006 * SR))
        a[st:st + len(b)] += lp(b, 8) * (0.7 + 0.3 * (k % 2))
    save("passinhos.wav", a)
    t = np.arange(int(0.9 * SR)) / SR
    cr = np.zeros_like(t)
    for k in range(14):
        st = int(rng.uniform(0, 0.35) * SR)
        b = rng.standard_normal(int(0.02 * SR)) * np.exp(-np.arange(int(0.02 * SR)) / (0.004 * SR))
        cr[st:st + len(b)] += b
    cr += lp(rng.standard_normal(len(t)), 40) * np.exp(-t * 4) * 2
    save("racha.wav", cr)


def eventos():
    rel = os.path.relpath(WORK + "/sfx", KIT + "/sfx") + "/"      # o compose junta KIT/sfx/ + nome
    SX = lambda n: rel + n
    t = lambda nm: (SH[nm]["f0"] - 1) / 30
    f_imp = f(wt("atrás")) + 2
    tm = (F_MATCH - 1) / 30
    sfx = [
        (SX("rugido.wav"), 0.0, 1.0), (SX("vento.wav"), 0.0, 0.35),
        ("thump.wav", t("A2_recua") + 0.1, 0.45), ("riser.wav", t("A2_recua") + 0.5, 0.25),
        ("thump.wav", (f_imp - 1) / 30, 0.8), (SX("vento.wav"), (f_imp - 1) / 30 + 0.2, 0.3),
        (SX("rugido.wav"), t("A5_ruge_de_novo") + 0.5, 0.55),
        ("pop.wav", tm, 0.9), (SX("cacarejo.wav"), tm + 0.04, 0.9),
        ("pop.wav", t("B2_comentario") + 0.07, 0.6), (SX("cacarejo.wav"), wt("acertou") + 0.2, 0.45),
        ("boing.wav", (F0_FOGE - 1) / 30, 0.7),
        ("whoosh.wav", (F0_FOGE + 19) / 30, 0.6), (SX("passinhos.wav"), (F0_FOGE + 20) / 30, 0.9), (SX("passinhos.wav"), (F0_FOGE + 30) / 30, 0.6),
        (SX("cacarejo.wav"), (F0_FOGE + 30) / 30, 0.55),
        (SX("rugido.wav"), wt("dinossauro", 2) - 0.1, 0.45), (SX("cacarejo.wav"), wt("dinossauro", 2), 0.45),
        ("click.wav", wt("peito") + 0.02, 0.6), ("ding.wav", wt("ossinho"), 0.8), ("ding.wav", wt("frango"), 0.45),
        ("thump.wav", wt("proteína"), 0.55), ("ding.wav", wt("galinha", 2), 0.35),
        (SX("vento.wav"), t("A6_sol_some"), 0.5), (SX("racha.wav"), wt("morrem") - 0.3, 0.7), (SX("racha.wav"), wt("morrem") + 0.4, 0.5),
        ("click.wav", wt("cisca") - 0.03, 0.35), ("click.wav", wt("cisca") + 0.43, 0.3), ("click.wav", wt("chão") + 0.1, 0.3),
        (SX("racha.wav"), wt("semente"), 0.4), ("click.wav", wt("semente"), 0.45),
        ("whoosh.wav", t("C9_wonder_praia"), 0.4), ("ding.wav", wt("galinha", 3), 0.6), ("boing.wav", wt("pato"), 0.5),
        ("riser.wav", t("B6_bilhoes"), 0.45),
        ("thump.wav", wt("sumiu"), 0.4), ("vinheta.wav", wt("virou") - 0.05, 1.0),
        (SX("passinhos.wav"), t("C7_penas_escamas") + 0.3, 0.22), (SX("passinhos.wav"), t("C7_penas_escamas") + 2.7, 0.22),
        (SX("passinhos.wav"), t("C8_comenta") + 1.0, 0.25), ("pop.wav", wt("escamas") + 0.35, 0.25),
    ]
    WH = [255, 255, 255]; DK = [26, 8, 36]; YEL = [255, 214, 30]
    pills = [(wt("bélgica") + 0.05, wt("antes") - 0.02, "WONDERCHICKEN", YEL, DK), (wt("antes"), t("B6_bilhoes") - 0.05, "66,7 MI DE ANOS", WH, DK),
             (wt("bilhões") - 0.1, wt("mais") - 0.05, "27 BILHÕES DE GALINHAS", YEL, DK), (wt("três"), t("B8_mesa") - 0.05, "+3 POR PESSOA", WH, DK)]
    pills_en = [(a, b, {"WONDERCHICKEN": "WONDERCHICKEN", "66,7 MI DE ANOS": "66.7 MILLION YEARS", "27 BILHÕES DE GALINHAS": "27 BILLION CHICKENS",
                        "+3 POR PESSOA": "+3 PER PERSON"}[tx], bg, fg) for a, b, tx, bg, fg in pills]
    gaps = [[wt("galinha") - 0.5, wt("galinha")], [(F0_FOGE + 2) / 30, (F0_FOGE + 11) / 30], [(L[13] + 0.1) - 0.5, N / 30 + 1]]
    big = ("A1_rugido", "B1_match", "B3_quintal", "C1_orbita", "C3_raiox", "C5_femur_rex", "A6_sol_some", "A8_cisca", "A10_fossil", "C9_wonder_praia", "B6_bilhoes", "B8_mesa", "C7_penas_escamas")
    ev = dict(N=N, shots=[SH[nm]["f0"] for nm in big], cortes=[SH[nm]["f0"] for nm, _, _ in PLAN], f_pop=F_MATCH, music="trilha_seria_84bpm.wav", sfx=sfx, pills=pills, pills_en=pills_en,
              music_gap=gaps[0], music_gaps=gaps,
              silencios=[dict(t0=round(gaps[0][0], 2), t1=round(gaps[0][1], 2), motivo="antes da revelacao da galinha"),
                         dict(t0=round(gaps[2][0], 2), t1=round((L[13] + 0.1), 2), motivo="antes da pergunta final (a trilha nao volta)")],
              planos=[dict(nome=nm, mundo=w_, f0=SH[nm]["f0"], f1=SH[nm]["f1"]) for nm, w_, _ in PLAN])
    json.dump(ev, open(WORK + "/events.json", "w"), ensure_ascii=False, indent=1)
    return ev


# ================================================================ modos
def main():
    mode = sys.argv[-1]
    if not os.path.exists(WORK + "/sfx/rugido.wav"):
        gerar_sfx()
    eventos()
    if mode == "qa":
        allissues = {}; focus = {}
        for w_ in ("A", "B", "C"):
            build(w_)
            iss, fl = run_qa(w_)
            allissues[w_] = iss; focus.update(fl)
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
        json.dump(dict(issues=allissues, foco=fsum), open(WORK + "/qa_scene.json", "w"), ensure_ascii=False, indent=1)
        tot = sum(len(v) for v in allissues.values())
        print("QA_SCENE", tot, "ocorrencias")
        for k, v in fsum.items():
            print("  foco", k, v)
        sys.exit(1 if tot else 0)
    if mode == "blend":
        out = WORK + "/blend"
        os.makedirs(out, exist_ok=True)
        man = []
        for w_ in ("A", "B", "C"):
            build(w_)
            sc = bpy.context.scene
            seg = segments(w_)
            sc.frame_start, sc.frame_end = seg[0][0], seg[-1][1]
            sc.frame_set(seg[0][0])
            sc.render.filepath = "//frames/f"
            try:
                sc.cycles.device = 'GPU'          # no Kaggle: blender -b X.blend ... -- --cycles-device OPTIX (cai para CPU se nao houver GPU)
            except Exception:
                pass
            bpy.ops.file.pack_all()
            fn = f"{WORLDS[w_]}.blend"
            bpy.ops.wm.save_as_mainfile(filepath=f"{out}/{fn}", compress=True, relative_remap=True)
            for a, b in seg:
                man.append(dict(blend=fn, frame_start=a, frame_end=b, out_prefix="frames/f",
                                cmd=f"blender -b {fn} -o //frames/f -s {a} -e {b} -a -- --cycles-device OPTIX"))
            print("SALVO", fn, seg, flush=True)
        json.dump(man, open(out + "/manifest.json", "w"), ensure_ascii=False, indent=1)
        print("MANIFEST", len(man), "trechos")
        return
    if mode == "full":
        os.makedirs(WORK + "/frames", exist_ok=True)
        for w_ in ("A", "B", "C"):
            build(w_)
            sc = bpy.context.scene
            sc.render.filepath = WORK + "/frames/f"
            for a, b in segments(w_):
                sc.frame_start, sc.frame_end = a, b
                bpy.ops.render.render(animation=True)
        return
    # previa por lista de quadros
    frs = [max(1, int(x)) for x in mode.split(",")]
    PREV = os.environ.get("PIPO_PREV", WORK + "/prev")
    os.makedirs(PREV, exist_ok=True)
    tlog_p = PREV + "/tempos.json"
    tlog = json.load(open(tlog_p)) if os.path.exists(tlog_p) else {}
    for w_ in ("A", "B", "C"):
        mine = [x for x in frs if world_of(x) == w_]
        if not mine:
            continue
        build(w_)
        sc = bpy.context.scene
        for fr in mine:
            sc.frame_set(fr)
            sc.render.filepath = PREV + f"/p_{fr:04d}.png"
            t0 = time.time(); bpy.ops.render.render(write_still=True); t1 = time.time() - t0
            t2 = -1
            if os.environ.get("PIPO_WARM", "1") == "1":     # tempo de um quadro seguinte, cena ja carregada (como nas previas)
                nxt = fr + 1 if world_of(fr + 1) == w_ else fr - 1
                sc.frame_set(nxt); sc.render.filepath = "/tmp/_warm.png"
                t0 = time.time(); bpy.ops.render.render(write_still=True); t2 = time.time() - t0
            tlog[str(fr)] = dict(plano=shot_of(fr), mundo=WORLDS[w_], primeiro_s=round(t1, 2), quadro_s=round(t2, 2))
            print("TIME", fr, shot_of(fr), round(t1, 2), round(t2, 2), flush=True)
            json.dump(tlog, open(tlog_p, "w"), indent=1)


if __name__ == "__main__":
    main()
