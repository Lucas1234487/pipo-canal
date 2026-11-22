"""ep004: O T. rex tinha ossinho da sorte (dinossauros parte 2). 34,02 s de narracao + 0,9 s de respiro = 34,9 s, 30 fps, N = 1047.
Tres mundos, cada um uma cena com cortes de camera dentro; cada mundo vira UM .blend e o manifest lista os trechos:
    A_cinzas  (mundo das cinzas do ep003, luz aprovada): rugido + raio-x da furcula, card do comentario, match cut da galinha,
              ACERTOU, contraluz "aves sao dinossauros", close na furcula da galinha
    B_ceia    (mesa de ceia de Natal a noite): o V sobe do frango e vira osso; a disputa; o estalo (f_pop) com a Pipo; o final
    C_split   (tela dividida fisica: metade cinzas com o peito do T. rex, metade ceia com o ossinho)

Modos (como no kit):
    python3 ep.py qa                 QA da cena em todos os mundos (grava qa_scene.json; sai com codigo 1 se houver falha)
    python3 ep.py 1,382,501          previa de quadros em WORK/prev (p_NNNN.png) + tempo por quadro (prev/tempos.json)
    python3 ep.py full               render completo em WORK/frames (NAO rodar aqui: o Diretor decide onde)
    python3 ep.py blend              WORK/blend/{A_cinzas,B_ceia,C_split}.blend empacotados + manifest.json
Variaveis: PIPO_KIT (kit/), PIPO_WORK (pasta do episodio), PIPO_ASSETS (assets/modelos).
Nada do render depende deste script: tudo vira keyframe (camera, luzes, materiais, visibilidade), trilha NLA das acoes
dos modelos, parentesco a osso, modificador de f-curve ou instancia. O render dos .blend nao executa Python.
"""
import sys, os, json, math, random, time
KIT = os.environ.get("PIPO_KIT", "/home/claude/pipo-canal/kit")
WORK = os.environ.get("PIPO_WORK", "/home/claude/ep004")
os.environ.setdefault("PIPO_KIT", KIT); os.environ.setdefault("PIPO_WORK", WORK)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, WORK)
import bpy, bmesh
from mathutils import Vector, Euler, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view
import mundos_ep003 as M
import mundos_ep004 as X

D = bpy.data
FPS = 30
f = lambda t: int(round(t * FPS)) + 1   # mesma convencao do kit (quadro 1 = 0,0 s)
T = json.load(open(WORK + "/timing.json"))
_fim_fala = T["lines"][-1]["start"] + T["lines"][-1]["dur"]
N = int((_fim_fala + 0.9) * FPS)            # 34,02 + 0,9 = 34,92 s -> 1047 quadros (34,9 s)
M.N = N                                       # brasas, cinzas, fogo e pisca-pisca animam ate o fim
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
PLAN = [
    ("A1_rugido", "A", 0.0),                        # Esse osso brilhando fica no peito
    ("A2_peito", "A", wt("t") - 0.03),             # do T. rex.
    ("A3_close", "A", L[1] - 0.0),                  # E voce ja segurou um desses.
    ("A4_card", "A", L[2] - 0.08),                  # Na parte um, o Niko chutou quem escapou: a
    ("A5_match", "A", wt("galinha")),               # galinha. (MATCH CUT de silhueta)
    ("A6_acertou", "A", wt("acertou") - 0.03),      # Acertou.
    ("A7_aves", "A", wt("aves") - 0.12),            # Aves sao dinossauros.
    ("A8_herdaram", "A", L[4] - 0.0),               # E herdaram esse osso.
    ("B1_ceia", "B", 16.85),                        # (silencio) E o ossinho da sorte.
    ("C1_split", "C", L[6] - 0.05),                 # Duas claviculas grudadas,
    ("C2_igual", "C", wt("igual") - 0.06),          # igual as do T. rex.
    ("B2_mesa", "B", L[7] - 0.05),                  # Na ceia de Natal,
    ("B3_puxa", "B", wt("quando") - 0.06),          # quando voce puxar ele,
    ("B4_estalo", "B", wt("disputando") - 0.25),    # vai estar disputando um osso de dinossauro. (QUEBRA no "dinossauro")
    ("B5_final", "B", L[9] - 0.1),                  # Na sua casa,
    ("B6_loop", "B", wt("fica", 1) - 0.03),         # quem fica com o pedaco maior?
]
SH = {}
for i, (nm, w_, t0) in enumerate(PLAN):
    f0 = f(t0)
    f1 = (f(PLAN[i + 1][2]) - 1) if i + 1 < len(PLAN) else N
    SH[nm] = dict(name=nm, world=w_, t0=t0, f0=f0, f1=f1)
WORLDS = {"A": "A_cinzas", "B": "B_ceia", "C": "C_split"}


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


F_MATCH = SH["A5_match"]["f0"]                 # o corte do match cut cai no "galinha"
F_POP = f(wt("dinossauro"))                    # o ossinho quebra e a Pipo estoura no MESMO quadro
F_BRILHO = f(wt("brilhando"))
P_STAR = (0.5, 0.45)                           # ponto da tela (x, y de cima) onde caem as furculas (rima visual)

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


# ================================================================ MUNDO A: cinzas (planos A1-A8)
def build_A():
    cz = M.mundo_cinzas()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    sc.cycles.transparent_max_bounces = 10
    g = cz["chao"]; cam = cz["cam"]
    # o T. rex procedural do ep003 sai; entra o Quaternius do teste aprovado (escala 0.42, rotacao 0)
    for o in [cz["rex"]["root"]] + list(cz["rex"]["root"].children_recursive):
        D.objects.remove(o, do_unlink=True)
    for c in list(cam.constraints):
        cam.constraints.remove(c)
    cam.animation_data_clear(); cam.parent = None
    S = SH
    R = X.carrega_rex("qrex", (0, 0.5, 0), 0.0, 0.42)
    arm, rmesh = R["arm"], R["mesh"]
    A = R["acts"]
    # pose de referencia (TRex_Attack quadro 14, a do teste aprovado): mascara do raio-x e furcula presas ao osso do peito
    X.set_action(arm, A["TRex_Attack"]); sc.frame_set(14)
    mk = R["mask"]
    X.prende_no_osso(mk, arm, "Shoulders", Matrix.LocRotScale(Vector((0, -3.0, 3.85)), None, Vector((1.25, 1.2, 1.1))))
    fm_rex = X.furcula_mat("furcula_rex", glow=1.0)
    FR = X.furcula("furc_rex", None, (0, 0, 0), (0, 0, 0), 1.0, mat=fm_rex)
    X.prende_no_osso(FR["root"], arm, "Shoulders", Matrix.LocRotScale(Vector((0, -2.80, 3.33)),
                                                                       Euler((math.radians(22), 0, 0)).to_quaternion(), Vector((0.78,) * 3)))
    arm.animation_data.action = None
    # ---------- acoes (NLA): idle de base o tempo todo; rugido de cabeca erguida no quadro 1 e de novo no "dinossauros"
    X.nla_track(arm, [(A["TRex_Idle"], -40, (0, 60), 1.0, 20)], "base")
    f_din = f(wt("dinossauros"))
    tr = X.nla_track(arm, [(A["TRex_Attack"], -7, (5, 11), 1.0, 1),          # a boca ja abre antes do quadro 1
                           (A["TRex_Attack"], 0, (11, 13.5), 17.0, 1),       # segura o rugido de cabeca erguida (quadros 1-43)
                           (A["TRex_Attack"], 43, (13.5, 28), 1.4, 1),       # investe e fecha
                           (A["TRex_Attack"], f_din - 20, (0, 28), 1.8, 1)], "rugido")   # rugido de novo (silhueta) no "dinossauros"
    for st in tr.strips:
        st.extrapolation = 'NOTHING'
    tr.strips[2].blend_out = 8
    tr.strips[3].blend_in = 8; tr.strips[3].blend_out = 10
    halo_r, halo_s = X.halo("furc_rex_halo", FR["giro"], (0, 0.18, 0.05), 0.75, strength=0.0)
    grp = R["grp"]
    # ---------- varredura do raio-x no "brilhando": faixa desce do pescoco ate a barriga
    fb0, fb1 = F_BRILHO - 6, F_BRILHO + 20
    key_val(X.gsock(grp, "BAND"), [(1, 1.25), (fb0, 1.25), (fb1, -1.15)])
    key_val(X.gsock(grp, "ON"), [(1, 1.0)])
    key_val(X.gsock(grp, "LINE"), [(1, 0.0), (fb0 - 1, 0.0), (fb0 + 2, 1.0), (fb1 - 2, 1.0), (fb1 + 3, 0.0)])
    # A7: contraluz (silhueta) e raio-x desligado; A8: ele fica atras, silhueta
    fa7 = S["A7_aves"]["f0"]
    key_val(X.gsock(grp, "ON"), [(fa7 - 1, 1.0), (fa7, 0.0)])
    nt_interp(grp, 'LINEAR')
    for fc in M.fcurves_nt(grp):
        for k in fc.keyframe_points:
            if int(k.co.x) in (fa7 - 1,):
                k.interpolation = 'CONSTANT'
    # lamina de luz (plano fino ciano) acompanhando a linha, so durante a varredura
    sheet_m = M.halo_mat("lamina_raiox", X.CIANO_B, 1.6, power=1.4)
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1, fill_type='NGON', location=(0, 0, 0))
    sheet = bpy.context.object; sheet.name = "lamina_raiox"; M.setmat(sheet, sheet_m); sheet.parent = mk
    sheet.visible_shadow = False; sheet.visible_diffuse = False; sheet.visible_glossy = False
    for fr, z in ((fb0, 1.25), (fb1, -1.15)):
        K(sheet, "location", fr, (0, 0, z))
    keys_lin(sheet)
    key_scale_vis(sheet, [(1, False), (fb0, True), (fb1 + 3, False)], base=(1.1, 1.1, 1))
    # ---------- furcula do T. rex: acende quando a faixa passa; no close gira e pulsa (batimento no "segurou" e no "desses")
    fa3, fb3 = S["A3_close"]["f0"], S["A3_close"]["f1"]
    beats = [f(wt("segurou")), f(wt("desses"))]
    kv = [(1, 0.0), (fb0 + 4, 0.0), (F_BRILHO + 10, 9.0), (fa3, 7.0)]
    for b in beats:
        kv += [(b - 3, 7.0), (b + 1, 18.0), (b + 9, 7.0)]
    kv += [(fb3 + 30, 7.0)]
    furcula_keys(fm_rex, kv)
    key_val(halo_s, [(1, 0.0), (fb0 + 4, 0.0), (F_BRILHO + 12, 0.55), (fa3, 0.45)] + sum([[(b - 3, 0.45), (b + 1, 0.95), (b + 9, 0.45)] for b in beats], []))
    nt_interp(halo_r.data.materials[0].node_tree)
    gz = FR["giro"]
    K(gz, "rotation_euler", 1, (0, 0, 0)); K(gz, "rotation_euler", fa3, (0, 0, math.radians(-28)))
    K(gz, "rotation_euler", fb3, (0, 0, math.radians(30))); K(gz, "rotation_euler", fb3 + 40, (0, 0, 0))
    for b in beats:
        K(gz, "scale", b - 3, (1, 1, 1)); K(gz, "scale", b + 1, (1.07, 1.07, 1.07)); K(gz, "scale", b + 9, (1, 1, 1))
    # ---------- galinha Kelgar: mesmo mundo, mesma postura (de frente, 3/4), raio-x com a furcula no mesmo lugar
    GX, GY = 3.4, -9.6
    gz0 = ground_at(g, GX, GY)
    GL = X.carrega_galinha("gal", (GX, GY, gz0 - 0.004), 0.0, 0.45)
    garm = GL["arm"]
    X.set_action(garm, GL["acts"]["Idle1"]); sc.frame_set(8)
    X.prende_no_osso(GL["mask"], garm, "Backbone", Matrix.LocRotScale(Vector((GX, GY - 0.095, gz0 + 0.2)), None, Vector((0.105, 0.105, 0.095))))
    fm_gal = X.furcula_mat("furcula_gal", glow=1.0)
    rex_h = 6.25; gal_h = 0.45
    FG = X.furcula("furc_gal", None, (0, 0, 0), (0, 0, 0), 1.0, mat=fm_gal)
    X.prende_no_osso(FG["root"], garm, "Backbone", Matrix.LocRotScale(Vector((GX, GY - 0.128, gz0 + 0.152)),
                                                                     Euler((math.radians(22), 0, 0)).to_quaternion(), Vector((0.78 * gal_h / rex_h,) * 3)))
    garm.animation_data.action = None
    ida = []
    for i in range(12):        # Idle1 1-35 em ida e volta: respira e mexe a cabeca sem abaixar para ciscar
        ida.append((GL["acts"]["Idle1"], F_MATCH - 20 + i * 35, (1, 35), 1.0, 1))
    trg = X.nla_track(garm, ida, "base")
    for i, st in enumerate(trg.strips):
        st.use_reverse = bool(i % 2)
    halo_g, halo_gs = X.halo("furc_gal_halo", FG["giro"], (0, 0.18, 0.05), 0.75, strength=0.0)
    ggrp = GL["grp"]
    fa5, fa8 = S["A5_match"]["f0"], S["A8_herdaram"]["f0"]
    f_osso = f(wt("osso", 1)) if len(WT["osso"]) > 1 else f(15.67)
    key_val(X.gsock(ggrp, "ON"), [(1, 1.0), (fa7 - 1, 1.0), (fa7, 0.0), (fa8 - 1, 0.0), (fa8, 1.0)])
    key_val(X.gsock(ggrp, "BAND"), [(1, -1.3), (fa8 - 1, -1.3), (fa8, 1.25), (fa8 + 14, -1.25)])
    key_val(X.gsock(ggrp, "LINE"), [(1, 0.0), (fa8, 0.0), (fa8 + 1, 1.0), (fa8 + 12, 1.0), (fa8 + 16, 0.0)])
    nt_interp(ggrp, 'LINEAR')
    for fc in M.fcurves_nt(ggrp):
        for k in fc.keyframe_points:
            if int(k.co.x) in (fa7 - 1, fa8 - 1):
                k.interpolation = 'CONSTANT'
    furcula_keys(fm_gal, [(1, 7.0), (fa7 - 1, 7.0), (fa7, 0.0), (fa8 + 2, 0.0), (fa8 + 12, 9.0), (f_osso - 3, 8.0), (f_osso + 2, 18.0), (f_osso + 12, 9.0)])
    key_val(halo_gs, [(1, 0.45), (fa7 - 1, 0.45), (fa7, 0.0), (fa8 + 2, 0.0), (fa8 + 12, 0.55), (f_osso + 2, 1.0), (f_osso + 12, 0.55)])
    nt_interp(halo_g.data.materials[0].node_tree)
    for fr, v in ((1, 0.0), (fa7 - 1, 0.0), (fa7, 0.0)):
        pass
    K(FG["giro"], "rotation_euler", fa8, (0, 0, math.radians(-12))); K(FG["giro"], "rotation_euler", S["A8_herdaram"]["f1"], (0, 0, math.radians(14)))
    K(FG["giro"], "scale", f_osso - 3, (1, 1, 1)); K(FG["giro"], "scale", f_osso + 2, (1.08,) * 3); K(FG["giro"], "scale", f_osso + 12, (1, 1, 1))
    # cinzas e fagulhas perto da galinha (algo vivo no primeiro plano dos closes dela)
    am = D.materials.get("cinza_floco"); fm2 = D.materials.get("fagulha")
    M._flocos("cinzas_gal", 70, (GX - 1.2, GY - 1.6, gz0 - 0.1), (GX + 1.4, GY + 0.8, gz0 + 1.4), 0.006, am, 170, 7)
    fg2 = M._flocos("fagulhas_gal", 26, (GX - 1.2, GY - 1.2, gz0), (GX + 1.2, GY + 0.8, gz0 + 1.2), 0.004, fm2, 150, 8)
    for fc in M.fcurves(fg2):
        if fc.data_path == "location" and fc.array_index == 2:
            for k in fc.keyframe_points:
                k.co.y = -k.co.y
    # luz da galinha (so nos planos dela): chave quente de frente e recorte de fogo atras
    lg1 = M.light('AREA', (GX + 0.9, GY - 1.1, 0.75), (GX, GY, 0.22), 0, (1.0, 0.62, 0.32), size=0.8)
    lg2 = M.light('AREA', (GX - 0.5, GY + 0.9, 0.7), (GX, GY, 0.25), 0, (1.0, 0.35, 0.08), size=0.6)
    only_during(lg1, fa5, S["A8_herdaram"]["f1"], 40)
    only_during(lg2, fa5, S["A8_herdaram"]["f1"], 60)
    # visibilidade: rex some nos planos da galinha de perto (A5, A6); galinha so existe em A5-A8
    rex_objs = [rmesh, FR["inteira"], halo_r, sheet]
    key_hide([rmesh, sheet], [(1, False), (fa5, True), (fa7, False)])
    key_hide([FR["inteira"], halo_r], [(1, False), (fa5, True)])          # a furcula do rex nao aparece na silhueta
    # A7/A8: o rex volta de PERFIL contra o sol (silhueta classica), atras da galinha
    key_const(R["root"], "rotation_euler", [(1, (0, 0, 0)), (fa7, (0, 0, math.radians(-64)))])
    dsun = Vector((-0.35, 1.0, 0)).normalized(); perp = Vector((dsun.y, -dsun.x, 0))
    rp = Vector((GX, GY, 0)) + dsun * 8.6 + perp * 1.6
    rp.z = ground_at(g, rp.x, rp.y) - 0.05
    key_const(R["root"], "location", [(1, (0, 0.5, 0)), (fa7, tuple(rp))])
    # contraluz de verdade: fogo forte atras do rex (recorta a silhueta) so em A7-A8
    lrim = M.light('AREA', tuple(rp + dsun * 4.5 + Vector((0, 0, 4.5))), tuple(rp + Vector((0, 0, 3.0)) - dsun * 2.0), 0, (1.0, 0.42, 0.12), size=5)
    only_during(lrim, fa7, S["A8_herdaram"]["f1"], 9000)
    gal_objs = [GL["mesh"], FG["inteira"], halo_g] + ([GL["eyes"]] if GL.get("eyes") else [])
    key_hide(gal_objs, [(1, True), (fa5, False)])

    # ---------- camera
    C = Cam(cam)
    furc_c = lambda: FR["giro"].matrix_world.translation.copy()

    def a1(u, fr):        # rugido de frente, baixo, cheio no quadro 1; push-in lento
        k = ease(u)
        kt = ease(max(0.0, (fr - (F_BRILHO - 10)) / 30.0))        # na varredura a camera desce da boca para o peito
        tgt = Vector((-0.2, -4.6, 4.25)).lerp(Vector((-0.15, -3.6, 3.85)), kt)
        loc = Vector((1.25, -10.6, 3.0)).lerp(Vector((1.0, -9.5, 3.05)), k) + shake(fr, 0.03 * (1 - 0.7 * k), 1)
        return dict(loc=loc, tgt=tgt + shake(fr, 0.012 * (1 - 0.7 * k), 2), lens=26, sy=-0.03, fd=(loc - Vector((0, -4.4, 4.1))).length, fs=4.0)
    C.shot(S["A1_rugido"], a1)

    def a2(u, fr):        # 3/4 do outro lado: cabeca e peito, a furcula acesa; orbita curta
        k = ease(u)
        ang = math.radians(-128 + 14 * k)
        fc_ = furc_c()
        loc = fc_ + Vector((math.cos(ang) * 7.0, math.sin(ang) * 7.0, -0.2 + 0.3 * k))
        tgt = fc_ + Vector((-0.15, -0.55, 0.42))
        return dict(loc=loc, tgt=tgt, lens=30, sy=0.0, fd=(loc - fc_).length, fs=4.5)
    C.shot(S["A2_peito"], a2, track=True)
    shx, shy = shift_for(*P_STAR)

    def a3(u, fr):        # close no peito: a furcula gira e pulsa no ponto P*
        k = ease(u)
        fc_ = furc_c()
        d_ = 4.9 - 0.9 * k
        dirv = Vector((0.42, -1.0, 0.05)).normalized()
        loc = fc_ + dirv * d_ + shake(fr, 0.004, 3)
        return dict(loc=loc, tgt=fc_, lens=38, sx=shx, sy=shy, fd=d_, fs=4.5)
    C.shot(S["A3_close"], a3, track=True)
    fa4, fb4 = S["A4_card"]["f0"], S["A4_card"]["f1"]

    def a4(u, fr):        # plano medio na altura do peito: o card flutua ao lado; termina na pose do match
        k = ease(u)
        fc_ = furc_c()
        dirv = Vector((0.62, -1.0, 0.04)).normalized()
        d_ = 9.6 - 1.2 * k
        loc = fc_ + dirv * d_
        return dict(loc=loc, tgt=fc_, lens=30, sx=shx, sy=shy, fd=d_, fs=5.0)
    C.shot(S["A4_card"], a4, track=True)
    sc.frame_set(fb4)
    bpy.context.view_layer.update()
    rel = FR["giro"].matrix_world.inverted() @ cam.matrix_world

    def a5(u, fr):        # MATCH CUT: mesma pose relativa na furcula da galinha (escala da galinha)
        mwg = FG["giro"].matrix_world @ rel
        loc0 = mwg.translation; rot = mwg.to_3x3().normalized().to_quaternion()
        back = (mwg.to_3x3().normalized() @ Vector((0, 0, 1))).normalized()
        d0 = (loc0 - FG["giro"].matrix_world.translation).length
        loc = loc0 - back * d0 * 0.06 * ease(u)
        return dict(loc=loc, rot=rot, lens=30, sx=shx, sy=shy, fd=(loc - FG["giro"].matrix_world.translation).length, fs=5.0)
    C.shot(S["A5_match"], a5, track=True)
    gfc = lambda: FG["giro"].matrix_world.translation.copy()
    sc.frame_set(S["A5_match"]["f0"])
    d_match = (cam.matrix_world.translation - gfc()).length

    def a6(u, fr):        # ACERTOU: punch-in na galinha, o carimbo bate no card
        k = ease(min(1, u * 3))
        g_ = gfc()
        dirv = Vector((0.55, -1.0, 0.08)).normalized()
        d_ = d_match * (0.86 - 0.08 * k)
        loc = g_ + dirv * d_ + shake(fr, 0.002 * (1 - k), 5)
        return dict(loc=loc, tgt=g_, lens=30, sx=shx, sy=shy, fd=d_, fs=5.0)
    C.shot(S["A6_acertou"], a6, track=True)
    gpos = Vector((GX, GY, gz0))

    def a7(u, fr):        # "Aves sao dinossauros": a camera abre; galinha pequena na frente, a silhueta do T. rex em contraluz atras
        k = ease(u)
        loc = Vector((3.8, -10.45, 0.3)).lerp(Vector((4.05, -11.0, 0.35)), k)
        return dict(loc=loc, tgt=Vector((1.3, -2.5, 2.9)), lens=17, sy=-0.12, fd=(loc - gpos).length, fs=4.0)
    C.shot(S["A7_aves"], a7)

    def a8(u, fr):        # close na furcula da galinha acesa, no mesmo ponto da tela (P*)
        k = ease(u)
        g_ = gfc()
        dirv = Vector((0.45, -1.0, 0.32)).normalized()
        d_ = 0.62 - 0.12 * k
        loc = g_ + dirv * d_
        return dict(loc=loc, tgt=g_, lens=38, sx=shx, sy=shy, fd=d_, fs=7.0)
    C.shot(S["A8_herdaram"], a8, track=True)
    C.done()
    cam.data.clip_start = 0.01

    # ---------- card do comentario (preso a camera, no plano de foco) e carimbo ACERTOU
    CD = X.card_comentario(cam)
    ST = X.carimbo("ACERTOU!", cam)
    f_card = f(L[2] + 0.05); fa6 = S["A6_acertou"]["f0"]; f_ac = f(wt("acertou"))
    pos = []
    for nm in ("A4_card", "A5_match", "A6_acertou"):
        sc.frame_set(SH[nm]["f0"])
        fd = cam.data.dof.focus_distance
        d_ = fd * (0.5 if nm == "A4_card" else 0.8)
        p_, hw = cam_local(30, d_, 0.62, 0.275, cam.data.shift_x, cam.data.shift_y)
        pos.append((SH[nm]["f0"], p_, hw, d_))
    for fr, p_, hw, d_ in pos:
        key_const(CD["root"], "location", [(fr, tuple(p_))])
    # escala: largura do card = 56% da tela
    base = [(fr, 0.62 * 2 * hw) for fr, p_, hw, d_ in pos]
    K(CD["root"], "scale", 1, (0.0005,) * 3); K(CD["root"], "scale", f_card - 1, (0.0005,) * 3)
    K(CD["root"], "scale", f_card + 4, (base[0][1] * 1.12,) * 3); K(CD["root"], "scale", f_card + 9, (base[0][1],) * 3)
    for fr, sc_ in base[1:]:
        K(CD["root"], "scale", fr - 1, (base[0][1] if fr == base[1][0] else base[1][1],) * 3)
        K(CD["root"], "scale", fr, (sc_,) * 3)
    K(CD["root"], "scale", fa7 - 1, (base[-1][1],) * 3); K(CD["root"], "scale", fa7, (0.0005,) * 3)
    for fc in M.fcurves(CD["root"]):
        if fc.data_path == "scale":
            for k in fc.keyframe_points:
                if int(k.co.x) in [b[0] - 1 for b in base[1:]] + [fa7 - 1]:
                    k.interpolation = 'CONSTANT'
    K(CD["root"], "rotation_euler", f_card, (0, math.radians(-8), math.radians(2)))
    K(CD["root"], "rotation_euler", f_card + 10, (0, math.radians(-4), 0))
    K(CD["root"], "rotation_euler", fa7, (0, math.radians(3), math.radians(-1)))
    # avatar pisca no "Niko"
    fn = f(wt("niko"))
    av = CD["avatar"]
    K(av, "scale", fn - 3, (1, 1, 1)); K(av, "scale", fn + 2, (1.3, 1.3, 1.3)); K(av, "scale", fn + 8, (1, 1, 1))
    # carimbo: entra gigante e assenta sobre o canto do card no "Acertou"
    sc.frame_set(fa6)
    fd6 = cam.data.dof.focus_distance * 0.76
    p6, hw6 = cam_local(30, fd6, 0.70, 0.47, cam.data.shift_x, cam.data.shift_y)
    ST["root"].location = p6
    ST["root"].rotation_euler = (0, 0, math.radians(-11))
    s6 = 0.34 * 2 * hw6
    K(ST["root"], "scale", 1, (0.0005,) * 3); K(ST["root"], "scale", f_ac - 1, (0.0005,) * 3)
    K(ST["root"], "scale", f_ac, (s6 * 1.45,) * 3); K(ST["root"], "scale", f_ac + 3, (s6 * 0.88,) * 3); K(ST["root"], "scale", f_ac + 7, (s6,) * 3)
    K(ST["root"], "scale", fa7 - 1, (s6,) * 3); K(ST["root"], "scale", fa7, (0.0005,) * 3)
    for fc in M.fcurves(ST["root"]):
        for k in fc.keyframe_points:
            if int(k.co.x) in (f_ac - 1, fa7 - 1):
                k.interpolation = 'CONSTANT'
    K(ST["root"], "rotation_euler", f_ac, (0, 0, math.radians(-17))); K(ST["root"], "rotation_euler", f_ac + 6, (0, 0, math.radians(-11)))
    # o card e o carimbo nao fazem sombra nem recebem luz da cena
    for o in [CD["root"], ST["root"]] + list(CD["root"].children_recursive) + list(ST["root"].children_recursive):
        o.visible_shadow = False
    # ---------- QA
    qa_key("rex", R["root"]); qa_key("galinha", GL["root"]); qa_key("card", CD["root"]); qa_key("carimbo", ST["root"])
    qa_tela("card", "rex"); qa_tela("card", "galinha"); qa_tela("carimbo", "galinha"); qa_tela("carimbo", "rex")
    qa_touch("card", "carimbo")         # o carimbo bate no card de proposito
    qa_tela("rex", "galinha")
    for sn in ("A1_rugido", "A2_peito", "A3_close", "A4_card"):
        qa_foco(sn, FR["giro"])
    for sn in ("A5_match", "A6_acertou", "A8_herdaram"):
        qa_foco(sn, FG["giro"])
    cab = M.empty("gal_cabeca", (0, 0, 0)); sc.frame_set(F_MATCH)
    X.prende_no_osso(cab, garm, "Head", Matrix.Translation(garm.matrix_world @ garm.pose.bones["Head"].tail))
    qa_foco("A7_aves", cab)
    qa_inteiro("A7_aves", "galinha")
    return dict(cam=cam, rex=R, gal=GL, FR=FR, FG=FG)


# ================================================================ MUNDO B: ceia de Natal (B1 e B2-B6)
OSSO_H = 0.065           # altura do ossinho de verdade (m)


def face_cam_rot(cam_mw):
    """rotacao que deixa a furcula de frente para a camera (frente -Y do osso aponta para a lente, +Z para cima da tela)"""
    return (cam_mw.to_3x3().normalized() @ Matrix.Rotation(math.radians(-90), 3, 'X'))


def build_B():
    cz = X.mundo_ceia()
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    cam = cz["cam"]; S = SH
    Z = X.MESA_Z
    fa1, fb1 = S["B1_ceia"]["f0"], S["B1_ceia"]["f1"]
    fa2, fa3, fa4 = S["B2_mesa"]["f0"], S["B3_puxa"]["f0"], S["B4_estalo"]["f0"]
    fa5, fa6 = S["B5_final"]["f0"], S["B6_loop"]["f0"]
    # ---------- o ossinho (o mesmo V do rex): sobe do frango acendido e vira osso de verdade
    fm = X.furcula_mat("furcula_ceia", glow=1.0)
    FB = X.furcula("osso_ceia", None, (0, 0, 0), (0, 0, 0), OSSO_H, mat=fm)
    root, giro = FB["root"], FB["giro"]
    hb, hbs = X.halo("osso_ceia_halo", giro, (0, 0.2, 0.05), 0.8, strength=0.0)
    f_os = f(wt("ossinho")); f_sorte = f(wt("sorte"))
    f_top = f_os + 16                      # chega ao ponto P*
    shx, shy = shift_for(*P_STAR)
    C = Cam(cam)
    frango_c = Vector((0, 0.2, Z + 0.09))
    focus_end = 0.30

    def b1(u, fr):        # mesa a noite; o V sobe do frango ate o ponto P* e o foco vem com ele
        k = ease(min(1.0, (fr - fa1) / float(f_top - fa1)))
        loc = Vector((0.0, -0.98, Z + 0.31)).lerp(Vector((0.0, -0.86, Z + 0.295)), k)
        tgt = Vector((0, 0.2, Z + 0.06))
        kf = ease((fr - f_os) / 18.0)
        fd = (loc - frango_c).length * 0.8 * (1 - kf) + focus_end * kf
        return dict(loc=loc, tgt=tgt, lens=35, sx=shx * kf, sy=shy * kf, fd=fd, fs=2.2)
    C.shot(S["B1_ceia"], b1)
    # posicao final do V: na frente da camera, distancia focus_end, no ponto P* (com o shift ja aplicado)
    sc.frame_set(f_top)
    bpy.context.view_layer.update()
    cmw = cam.matrix_world.copy()
    Rf = face_cam_rot(cmw)
    p_end = cmw @ (Vector((0, 0, -focus_end)))
    def root_for(giro_world, R3):
        return giro_world - R3 @ Vector((0, 0, 0.4 * OSSO_H))
    r_end = root_for(p_end, Rf)
    r_start = root_for(frango_c, Rf)
    r_mid = r_start.lerp(r_end, 0.45) + Vector((0, 0, 0.09))
    eul = Rf.to_euler()
    for fr, p in ((1, r_start), (f_os - 1, r_start), (f_os + 7, r_mid), (f_top, r_end), (f_top + 20, r_end + Vector((0, 0, 0.003))), (fb1, r_end - Vector((0, 0, 0.002)))):
        K(root, "location", fr, tuple(p))
    K(root, "rotation_euler", 1, tuple(eul))
    K(root, "scale", 1, (0.0005,) * 3); K(root, "scale", f_os - 1, (0.0005,) * 3); K(root, "scale", f_os + 2, (OSSO_H * 0.5,) * 3)
    K(root, "scale", f_os + 9, (OSSO_H,) * 3)
    for fc in M.fcurves(root):
        if fc.data_path == "location":
            for k_ in fc.keyframe_points:
                k_.interpolation = 'BEZIER'
    # gira enquanto sobe e assenta de frente
    K(giro, "rotation_euler", f_os, (0, 0, math.radians(-300))); K(giro, "rotation_euler", f_top + 4, (0, 0, 0))
    # brilho -> marfim no "sorte"
    gl = X.fsock(fm, "GLOW")
    key_val(gl, [(1, 1.0), (f_sorte - 2, 1.0), (f_sorte + 16, 0.0)])
    furcula_keys(fm, [(1, 9.0), (f_os + 10, 14.0), (f_top + 4, 9.0), (f_sorte + 16, 2.0), (f_sorte + 24, 0.0)])
    key_val(hbs, [(1, 0.0), (f_os, 0.0), (f_os + 6, 0.7), (f_top + 6, 0.5), (f_sorte + 16, 0.0)])
    nt_interp(fm.node_tree); nt_interp(hb.data.materials[0].node_tree)
    # ---------- B2-B4: o ossinho em pe na mesa, na frente da vela baixa
    OP = Vector((0.0, -0.42, Z + 0.0095))
    rot_mesa = Euler((0, 0, math.radians(-8)))
    cut_key(root, "location", fa2, tuple(r_end - Vector((0, 0, 0.002))), tuple(OP))
    cut_key(root, "rotation_euler", fa2, tuple(eul), tuple(rot_mesa))
    key_val(gl, [(fa2, 0.0)])
    # "osso de dinossauro": o marfim volta a brilhar ciano de leve antes de quebrar
    f_osso3 = f(wt("osso", 2))
    furcula_keys(fm, [(fa2, 0.0), (f_osso3 - 4, 0.0), (f_osso3 + 4, 6.0), (F_POP, 7.0), (F_POP + 3, 0.0)])
    key_val(X.fsock(fm, "EXTRA"), [(1, 0.0), (f_osso3 - 4, 0.0), (f_osso3 + 4, 0.2), (F_POP, 0.3), (F_POP + 6, 0.0)])
    # puxoes: gancho esquerdo no "puxar", direito no "ele"; tensao cresce no "disputando"; QUEBRA no "dinossauro" (F_POP)
    HK = X.hooks_abre(FB)
    hL, hR = HK["L"], HK["R"]
    f_px, f_ele, f_disp = f(wt("puxar")), f(wt("ele")), f(wt("disputando"))
    ang = {hL: -1, hR: 1}
    plan = [(1, 0.0, 0.0), (f_px - 2, 0.0, 0.0), (f_px + 3, 7.0, 1.5), (f_px + 9, 5.0, 1.0), (f_ele - 2, 5.0, 1.0), (f_ele + 3, 6.5, 7.5),
            (f_ele + 9, 5.0, 5.5), (f_disp - 2, 5.5, 5.5), (f_disp + 6, 9.0, 9.0), (F_POP - 10, 12.5, 12.5), (F_POP - 1, 15.0, 15.0)]
    for fr, aL, aR in plan:
        K(hL, "rotation_euler", fr, (0, math.radians(-aL), 0)); K(hR, "rotation_euler", fr, (0, math.radians(aR), 0))
    # tremor que cresce (chaves a cada 2 quadros, deterministico)
    random.seed(44)
    for fr in range(f_px + 10, F_POP - 1, 2):
        j = (fr - f_px) / float(F_POP - f_px)
        amp = 0.4 + 2.2 * j * j
        base = None
        for h_, sg in ((hL, -1), (hR, 1)):
            # valor base interpolado do plano
            for i in range(len(plan) - 1):
                if plan[i][0] <= fr <= plan[i + 1][0]:
                    u_ = (fr - plan[i][0]) / max(1, plan[i + 1][0] - plan[i][0])
                    a0 = plan[i][1 if sg < 0 else 2]; a1 = plan[i + 1][1 if sg < 0 else 2]
                    base = a0 + (a1 - a0) * u_
                    break
            K(h_, "rotation_euler", fr, (0, math.radians(sg * (base + random.uniform(-amp, amp))), 0))
        K(giro, "location", fr, (random.uniform(-1, 1) * 0.004 * j, 0, 0.4 + random.uniform(-1, 1) * 0.003 * j))
    K(giro, "location", F_POP - 1, (0, 0, 0.4))
    # ---------- QUEBRA
    ins, mai, men = FB["inteira"], FB["maior"], FB["menor"]
    key_hide([ins], [(1, False), (F_POP, True)])
    key_hide([mai, men], [(1, True), (F_POP, False), (fa5, True)])
    aL0, aR0 = math.radians(-15.0), math.radians(15.0)
    for o, a0 in ((mai, aL0), (men, aR0)):
        K(o, "rotation_euler", F_POP - 1, (0, a0, 0)); K(o, "location", F_POP - 1, (0, 0, -0.4))
    # peca maior: volta como mola e balanca
    for fr, rx, ry in ((F_POP, -3, -24), (F_POP + 3, -6, 8), (F_POP + 8, -14, -4), (F_POP + 14, -9, 2), (F_POP + 22, -12, 0)):
        K(mai, "rotation_euler", fr, (math.radians(rx), math.radians(ry), 0))
    # peca menor: voa para a direita e para cima, girando, sai do quadro
    for fr, loc, rot in ((F_POP, (0.14, 0.06, -0.33), (0, 38, 0)), (F_POP + 3, (0.38, 1.2, 0.3), (40, 120, 30)), (F_POP + 8, (0.9, 3.0, 1.0), (90, 260, 60)),
                         (F_POP + 14, (1.6, 5.0, 0.6), (170, 420, 90))):
        K(men, "location", fr, loc); K(men, "rotation_euler", fr, tuple(math.radians(a) for a in rot))
    # lascas: estilhacos pequenos que voam do ponto da quebra e caem na toalha
    sc.frame_set(F_POP)
    bpy.context.view_layer.update()
    pb = giro.matrix_world @ (Vector((0, 0, -0.4)) + X._arm_path(0.2, 1))
    lasca_m = M.pbr("lasca_osso", (0.86, 0.78, 0.6), (0.7, 0.6, 0.44), rough=0.45, nscale=60)
    random.seed(9)
    lascas = []
    for i in range(12):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(0, 0, 0))
        o = bpy.context.object; o.name = "lasca"
        for v in o.data.vertices:
            v.co *= random.uniform(0.6, 1.3)
        o.scale = (random.uniform(0.6, 1.4) * 0.0009, random.uniform(0.4, 0.9) * 0.0009, random.uniform(1.0, 2.2) * 0.0009)
        M.setmat(o, lasca_m)
        v0 = Vector((random.uniform(-0.5, 1.0), random.uniform(-0.15, 0.8), random.uniform(0.3, 1.2))).normalized() * random.uniform(0.3, 0.6)
        K(o, "location", 1, tuple(pb)); K(o, "location", F_POP - 1, tuple(pb))
        landed = None
        for k_ in range(0, 22, 2):
            tt = k_ / 30.0
            p = pb + v0 * tt + Vector((0, 0, -4.9)) * tt * tt
            if p.z < Z + 0.001:
                p.z = Z + 0.001
                if landed is None:
                    landed = p.copy()
                p = landed
            K(o, "location", F_POP + k_, tuple(p))
            K(o, "rotation_euler", F_POP + k_, (k_ * random.uniform(0.3, 0.8), k_ * random.uniform(0.2, 0.6), 0))
        key_hide([o], [(1, True), (F_POP, False), (fa5, True)])
        o.visible_shadow = False
        lascas.append(o)
    # clarao do estalo (4 quadros) + pulso de luz
    fl_m = M.emis("estalo", X.CIANO_B, 10.0)
    fl = M.sph("estalo_flash", 0.0022, tuple(pb), fl_m, seg=16, rings=8)
    fl.visible_shadow = False
    K(fl, "scale", 1, (0.001,) * 3); K(fl, "scale", F_POP - 1, (0.001,) * 3); K(fl, "scale", F_POP, (1.0,) * 3); K(fl, "scale", F_POP + 2, (2.2,) * 3); K(fl, "scale", F_POP + 5, (0.001,) * 3)
    lfl = M.light('POINT', tuple(pb + Vector((0, -0.03, 0.01))), None, 0, X.CIANO_B, size=0.01)
    light_keys(lfl, [(1, 0), (F_POP - 1, 0), (F_POP, 0.07), (F_POP + 4, 0.0)])
    # luz de recorte e chave pequena no ossinho (so nos planos dele)
    lk = M.light('AREA', (0.22, -0.66, Z + 0.16), tuple(OP + Vector((0, 0, 0.03))), 0, (1.0, 0.85, 0.65), size=0.15)
    only_during(lk, fa2, fa4 + 200, 1.6)
    # ---------- a Pipo: espiga na mesa, atras e a direita, desfocada, sobrancelha levantada (SIGN); estoura no estalo
    ns = M._load_pipo()
    pipo = ns["pipo"]; FK = ns["FK"]
    PX, PY = 0.085, -0.17
    ns["pipo_place"](PX, PY, 0.085)
    pipo.location.z = Z + 0.0
    face = math.atan2(OP.x - PX, -(OP.y - PY))
    pipo.rotation_euler = (0, 0, face * 0.35)
    ns["set_face"](FK, 1, **ns["SIGN"], look=(-30, -4))
    ns["set_face"](FK, fa3, **ns["SIGN"], look=(-34, -6))
    ns["blink"](FK, f_px + 6, ns["TIRED"])
    ns["set_face"](FK, f_disp, lid=-10, brow=(14, 0.3), browL=(-16, 0.33), look=(-36, -8))      # olhos arregalam na disputa
    ns["pipo_tension"](F_POP - 22, F_POP)
    ns["pipo_pop"](F_POP, burst=True, size=0.78)
    ns["set_face"](ns["FP"], F_POP + 14, lid=-60, brow=(15, 0.33), browL=(15, 0.33), look=(-30, -5))
    # o anel e os raios do estouro do kit pareciam bug a 25 cm da lente: saem; fica so a pipoca voando (os puffs do kit)
    for o in list(pipo.children_recursive):
        if o.type == 'MESH' and o.data.materials and o.data.materials[0] and o.data.materials[0].name.startswith(("ring", "ray")):
            D.objects.remove(o, do_unlink=True)
    # pena de galinha presa na cabeca (ponta solta do ep003: escapou da galinha por pouco)
    pm = M.feather_mat("pena_pipo", [(0.55, 0.22, 0.08), (0.7, 0.32, 0.1)], tip=(0.12, 0.05, 0.02))
    pme = M.feather_mesh("pena_pipo", 1.0, 0.38, 0.1)
    pena = M.link(D.objects.new("pena_pipo", pme)); M.setmat(pena, pm)
    pena.parent = ns["kern"]; pena.location = (0.06, 0.02, 0.46); pena.rotation_euler = (math.radians(-25), math.radians(35), math.radians(20)); pena.scale = (0.32,) * 3
    pipo_foco = M.empty("foco_pipo", (0, 0, 0.6), pipo)
    vis_window([pipo], fa2, fa5 - 1)
    # ---------- B5-B6: o pedaco maior gira devagar sob a luz da arvore (heroi do loop)
    fmf = X.furcula_mat("furcula_final", glow=0.0)
    X.fsock(fmf, "EL").default_value = 2.0; X.fsock(fmf, "ER").default_value = 2.0; X.fsock(fmf, "EXTRA").default_value = 0.05
    hero = M.empty("pedaco_maior", (0, 0, 0))
    hp = M.link(D.objects.new("pedaco_maior_malha", mai.data.copy())); hp.data.materials.clear(); hp.data.materials.append(fmf)
    hp.parent = hero; hp.location = (0, 0, -0.4)
    sd = hp.modifiers.new("sub", 'SUBSURF'); sd.levels = 1; sd.render_levels = 2
    HP = Vector((1.08, 1.30, 1.18))
    hero.location = HP; hero.scale = (OSSO_H * 1.0,) * 3
    for fr, rz in ((fa5, -70), (N + 1, 200)):
        K(hero, "rotation_euler", fr, (math.radians(-6), 0, math.radians(rz)))
    keys_lin(hero)
    for fr in range(fa5, N + 1, 30):
        K(hero, "location", fr, tuple(HP + Vector((0, 0, 0.0025 * math.sin((fr - fa5) / 30 * math.pi)))))
    vis_window([hero], fa5, N)
    lh = M.light('AREA', tuple(HP + Vector((-0.25, -0.3, 0.2))), tuple(HP), 0, (1.0, 0.82, 0.6), size=0.25)
    only_during(lh, fa5, N, 0.45)
    lh2 = M.light('AREA', tuple(HP + Vector((0.2, 0.35, 0.05))), tuple(HP), 0, (0.6, 0.85, 1.0), size=0.2)
    only_during(lh2, fa5, N, 0.6)
    # ---------- cameras B2-B6
    oc = OP + Vector((0, 0, 0.6 * OSSO_H))

    def b2(u, fr):        # o ossinho em pe na toalha, a vela atras; frango, arvore e Pipo desfocados ao fundo
        k = ease(u)
        loc = oc + Vector((0.07, -0.36, 0.075)).lerp(Vector((0.055, -0.31, 0.065)), k)
        return dict(loc=loc, tgt=oc + Vector((0.01, 0, 0.012)), lens=45, sy=-0.12, fd=(loc - oc).length, fs=2.4)
    C.shot(S["B2_mesa"], b2)

    def b3(u, fr):        # mais perto: os puxoes
        k = ease(u)
        loc = oc + Vector((-0.04, -0.25, 0.045)).lerp(Vector((-0.03, -0.22, 0.04)), k)
        return dict(loc=loc, tgt=oc + Vector((0.006, 0, 0.008)), lens=45, sy=-0.13, fd=(loc - oc).length, fs=3.2)
    C.shot(S["B3_puxa"], b3)

    def b4(u, fr):        # tensao: close firme; no estalo a camera sacode
        k = ease(min(1.0, (fr - fa4) / float(F_POP - fa4)))
        loc = oc + Vector((0.03, -0.29, 0.035)).lerp(Vector((0.026, -0.25, 0.03)), k)
        return dict(loc=loc, tgt=oc + Vector((0.012, 0, 0.006)), lens=45, sy=-0.13, fd=(loc - oc).length, fs=3.5)
    C.shot(S["B4_estalo"], b4)

    def b5(u, fr):        # o pedaco maior girando sob a luz da arvore; terco de cima limpo para a pergunta
        k = ease(u)
        loc = HP + Vector((-0.075, -0.25, 0.04)).lerp(Vector((-0.068, -0.23, 0.037)), k)
        return dict(loc=loc, tgt=HP, lens=50, sy=-0.06, fd=(loc - HP).length, fs=3.0)
    C.shot(S["B5_final"], b5)

    def b6(u, fr):        # mesma luz, um pouco mais perto e de lado; estavel para o loop
        k = ease(u)
        loc = HP + Vector((-0.02, -0.215, 0.03)).lerp(Vector((-0.018, -0.205, 0.028)), k)
        return dict(loc=loc, tgt=HP, lens=50, sy=-0.06, fd=(loc - HP).length, fs=3.0)
    C.shot(S["B6_loop"], b6)
    C.done()
    # sacudida no estalo (f-curve noise, sem Python)
    for fc in M.fcurves(cam):
        if fc.data_path == "location":
            mo = fc.modifiers.new('NOISE'); mo.strength = 0.006; mo.scale = 1.2
            mo.use_restricted_range = True; mo.frame_start = F_POP; mo.frame_end = F_POP + 16; mo.blend_in = 0; mo.blend_out = 10
    cam.data.clip_start = 0.005
    # ---------- QA
    qa_key("ossinho", root); qa_key("frango", cz["frango"]["root"]); qa_key("pipo", pipo); qa_key("pedaco_final", hero)
    qa_tela("ossinho", "frango"); qa_tela("ossinho", "pipo"); qa_tela("pipo", "frango")
    qa_foco("B1_ceia", giro, fa=f_top); qa_foco("B2_mesa", giro); qa_foco("B3_puxa", giro); qa_foco("B4_estalo", giro, fb=F_POP)
    qa_foco("B2_mesa", pipo_foco); qa_foco("B4_estalo", pipo_foco)
    qa_foco("B5_final", hero); qa_foco("B6_loop", hero)
    return dict(cam=cam, FB=FB, pipo=pipo, hero=hero)


# ================================================================ MUNDO C: tela dividida (C1-C2)
def build_C():
    """Tela dividida fisica: camera em x=0 olhando +Y; tudo com x<0 cai na metade esquerda e x>0 na direita.
    Esquerda: peito do T. rex (Quaternius em escala de maquete) translucido com a furcula acesa, cinzas e brasas atras.
    Direita: o ossinho da ceia em pe na toalha, bokeh do pisca-pisca atras. As duas furculas no mesmo tamanho e altura."""
    s = M.reset(4)
    M.bloom(s, threshold=0.85, size=0.7, strength=0.75)
    s.cycles.transparent_max_bounces = 10
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, N
    nt = s.world.node_tree; nt.nodes["Background"].inputs[0].default_value = (0.004, 0.003, 0.004, 1)
    S = SH
    fa, fb = S["C1_split"]["f0"], S["C2_igual"]["f1"]
    fa2 = S["C2_igual"]["f0"]
    LENS = 35.0
    Dd = 0.32
    W_, H_ = sc.render.resolution_x, sc.render.resolution_y
    half_w = Dd * 18.0 / LENS * W_ / H_
    a = half_w * 0.5
    shx, shy = shift_for(0.5, P_STAR[1])
    Lp, Rp = Vector((-a, Dd, 0.0)), Vector((a, Dd, 0.0))
    # ---------- esquerda: o T. rex de maquete (escala para a furcula dele ficar do tamanho do ossinho)
    k = OSSO_H / 0.78
    R = X.carrega_rex("crex", (0, 0, 0), math.radians(-20), 0.42 * k)
    arm = R["arm"]
    X.set_action(arm, R["acts"]["TRex_Attack"]); sc.frame_set(14)
    bpy.context.view_layer.update()
    rmw = R["root"].matrix_world.copy()
    loc_a = lambda p: (Vector(p) - Vector((0, 0.5, 0))) / 0.42          # coordenadas locais do mundo A
    sm = lambda v: rmw.to_3x3() @ Vector(v)
    X.prende_no_osso(R["mask"], arm, "Shoulders", Matrix.LocRotScale(rmw @ loc_a((0, -3.0, 3.85)), rmw.to_quaternion(), Vector((1.25, 1.2, 1.1)) * k))
    fm_r = X.furcula_mat("furcula_split_rex", glow=1.0)
    FR = X.furcula("split_furc_rex", None, (0, 0, 0), (0, 0, 0), 1.0, mat=fm_r)
    q = rmw.to_quaternion() @ Euler((math.radians(22), 0, 0)).to_quaternion()
    X.prende_no_osso(FR["root"], arm, "Shoulders", Matrix.LocRotScale(rmw @ loc_a((0, -2.80, 3.33)), q, Vector((OSSO_H,) * 3)))
    arm.animation_data.action = None
    X.nla_track(arm, [(R["acts"]["TRex_Idle"], fa - 30, (0, 60), 1.0, 6)], "base")
    for m_ in R["mats"].values():          # o corpo do rex nao invade a metade da ceia
        X.corta_x(m_, keep_neg=True)
    hr, hrs = X.halo("split_halo_rex", FR["giro"], (0, 0.18, 0.05), 0.75, strength=0.45)
    g = R["grp"]
    X.gsock(g, "ON").default_value = 1.0; X.gsock(g, "BAND").default_value = -2.0; X.gsock(g, "LINE").default_value = 0.0
    # leva o rex para que a furcula fique em Lp no meio do plano
    sc.frame_set((fa + fb) // 2)
    bpy.context.view_layer.update()
    R["root"].location = R["root"].location + (Lp - FR["giro"].matrix_world.translation)
    bpy.context.view_layer.update()
    # fundo esquerdo: fumaca e brasa (cinzas do mundo A em miniatura)
    fum = X.halo_add_mat("split_brasa_fundo", (1.0, 0.28, 0.05), 1.0, power=1.4)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-0.35, Dd + 0.9, 0.05), rotation=(math.radians(90), 0, 0))
    bgL = bpy.context.object; bgL.name = "fundo_cinzas"; bgL.scale = (0.7, 0.9, 1)
    fmat = M._fumaca_mat("split_fumaca", (0.05, 0.012, 0.006), 0.72, 2.0, 0.4)
    M.setmat(bgL, fmat)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-0.35, Dd + 0.95, 0.0), rotation=(math.radians(90), 0, 0))
    bgL2 = bpy.context.object; bgL2.name = "fundo_ceu"; bgL2.scale = (0.7, 1.0, 1)
    M.setmat(bgL2, fum)
    for o in (bgL, bgL2):
        o.visible_shadow = False
    am = M.pbr("split_cinza", (0.55, 0.52, 0.5), (0.3, 0.28, 0.27), rough=0.9, nscale=40)
    fg = M.emis("split_fagulha", (1.0, 0.45, 0.08), 18)
    fl1 = M._flocos("split_cinzas", 60, (-0.35, Dd - 0.12, -0.25), (-0.004, Dd + 0.5, 0.3), 0.0025, am, 150, 21)
    fl2 = M._flocos("split_fagulhas", 30, (-0.35, Dd - 0.05, -0.25), (-0.004, Dd + 0.5, 0.3), 0.0014, fg, 130, 22)
    for fc in M.fcurves(fl2):
        if fc.data_path == "location" and fc.array_index == 2:
            for k_ in fc.keyframe_points:
                k_.co.y = -k_.co.y
    for fc in M.fcurves(fl1) + M.fcurves(fl2):
        for k_ in fc.keyframe_points:
            pass
    M.light('AREA', (-0.45, Dd + 0.35, 0.18), tuple(Lp), 1.2, (1.0, 0.35, 0.08), size=0.15)
    M.light('AREA', (-0.18, Dd - 0.25, 0.05), tuple(Lp), 0.25, (1.0, 0.6, 0.35), size=0.12)
    # ---------- direita: o ossinho em pe na toalha, bokeh da ceia atras
    fm_b = X.furcula_mat("furcula_split_osso", glow=0.0)
    FB = X.furcula("split_osso", None, (0, 0, 0), (0, 0, math.radians(-6)), OSSO_H, mat=fm_b)
    FB["root"].location = Rp - Vector((0, 0, 0.4 * OSSO_H))
    tz = FB["root"].location.z - 0.0095
    toalha = D.materials.get("toalha") or X._toalha_mat()
    M.box("split_toalha", (0.6, 0.32, 0.01), (0.3005, Dd + 0.04, tz - 0.005), toalha, bev=0.0)
    par = M.pbr("split_parede", (0.02, 0.07, 0.07), (0.03, 0.1, 0.1), rough=0.85, nscale=20)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0.3005, Dd + 0.22, 0.05), rotation=(math.radians(90), 0, 0))
    bgR = bpy.context.object; bgR.name = "fundo_ceia"; bgR.scale = (0.6, 0.8, 1); M.setmat(bgR, par)
    pis = X._piscas()
    random.seed(31)
    for i in range(26):
        p = (random.uniform(0.01, 0.17), Dd + random.uniform(0.13, 0.2), random.uniform(-0.03, 0.16))
        b = M.sph("split_pisca", random.uniform(0.0018, 0.003), p, pis[i % len(pis)], seg=8, rings=4); b.visible_shadow = False
    ch = M.sph("split_chama", 0.0025, (0.105, Dd + 0.14, tz + 0.045), M.emis("split_chama_m", (1.0, 0.6, 0.2), 14), seg=12, rings=6)
    ch.scale = (1, 1, 2.4); ch.visible_shadow = False
    M.light('AREA', (0.2, Dd - 0.2, 0.08), tuple(Rp), 0.5, (1.0, 0.78, 0.5), size=0.1)
    lc = M.light('POINT', (0.105, Dd + 0.12, tz + 0.05), None, 0.12, (1.0, 0.55, 0.2), size=0.005)
    random.seed(5)
    for fr in range(1, N + 1, 3):
        lc.data.energy = 0.12 * random.uniform(0.8, 1.2); lc.data.keyframe_insert("energy", frame=fr)
    # costura: linha fina e quente no meio da tela
    sm_m = M.emis("split_costura", (1.0, 0.85, 0.6), 3.0)
    M.box("split_costura", (0.00045, 0.0004, 0.5), (0, Dd - 0.02, 0.0), sm_m, bev=0.0).visible_shadow = False
    # ---------- as claviculas acendem uma de cada vez: esquerda no "duas", direita no "claviculas"; juntas no "grudadas"
    f_duas, f_clav, f_grud, f_igual, f_trex = f(wt("duas")), f(wt("clavículas")), f(wt("grudadas")), f(wt("igual")), f(wt("t", 1))
    for mat_, base, hi, extra in ((fm_r, 2.5, 15.0, None), (fm_b, 0.0, 6.0, 1.0)):
        key_val(X.fsock(mat_, "EL"), [(1, base), (f_duas - 2, base), (f_duas + 3, hi * 1.3), (f_duas + 10, hi), (f_grud - 2, hi), (f_grud + 3, hi * 1.4), (f_grud + 12, hi),
                                       (f_igual - 2, hi), (f_igual + 3, hi * 1.4), (f_igual + 12, hi), (f_trex - 2, hi), (f_trex + 3, hi * 1.5), (f_trex + 14, hi)])
        key_val(X.fsock(mat_, "ER"), [(1, base), (f_clav - 2, base), (f_clav + 3, hi * 1.3), (f_clav + 10, hi), (f_grud - 2, hi), (f_grud + 3, hi * 1.4), (f_grud + 12, hi),
                                       (f_igual - 2, hi), (f_igual + 3, hi * 1.4), (f_igual + 12, hi), (f_trex - 2, hi), (f_trex + 3, hi * 1.5), (f_trex + 14, hi)])
        if extra is not None:
            X.fsock(mat_, "EXTRA").default_value = extra
        nt_interp(mat_.node_tree)
    # ---------- camera: parada no eixo (a divisao depende disso), so a lente respira
    cam = M.camera((0, 0, 0), (0, 1, 0), LENS)
    C = Cam(cam)
    foc = Dd

    def c1(u, fr):
        return dict(loc=Vector((0, 0, 0)), rot=Euler((math.radians(90), 0, 0)), lens=LENS + 1.5 * ease(u), sx=0.0, sy=shy, fd=foc, fs=2.8)
    C.shot(S["C1_split"], c1)

    def c2(u, fr):
        return dict(loc=Vector((0, 0, 0)), rot=Euler((math.radians(90), 0, 0)), lens=LENS + 3.0 + 1.5 * ease(u), sx=0.0, sy=shy, fd=foc, fs=2.8)
    C.shot(S["C2_igual"], c2)
    C.done()
    cam.data.clip_start = 0.005
    # ---------- QA
    qa_key("rex", R["root"]); qa_key("ossinho", FB["root"])
    # tela dividida: a cauda do rex de maquete passa atras do ossinho no espaco 3D, mas o material corta tudo do rex com x>0
    # (metade da ceia), entao nao aparece; a sobreposicao de caixas e a intersecao sao so geometricas, nao de imagem
    qa_touch("rex", "ossinho")
    qa_foco("C1_split", FR["giro"], FB["giro"]); qa_foco("C2_igual", FR["giro"], FB["giro"])
    qa_inteiro("C1_split", "ossinho"); qa_inteiro("C2_igual", "ossinho")
    return dict(cam=cam, FR=FR, FB=FB, rex=R)


BUILD = {"A": build_A, "B": build_B, "C": build_C}


def build(world):
    QA["keys"].clear(); QA["touch"].clear(); QA["screen_ok"].clear(); QA["focus"].clear(); QA["inteiros"].clear()
    t = time.time()
    r = BUILD[world]()
    sc = bpy.context.scene
    sc.render.filepath = "//frames/f"
    sc.render.use_overwrite = False; sc.render.use_placeholder = True
    print("BUILD", world, round(time.time() - t, 1), "s", len(D.objects), "objetos", flush=True)
    return r


# ================================================================ eventos (formato do ep003 / kit/compose.py)
def eventos():
    """N, planos, cortes, f_pop, pills vazias e o silencio antes da revelacao. sfx e music ficam vazios: o Diretor faz o som."""
    big = ("A1_rugido", "A4_card", "A5_match", "A7_aves", "B1_ceia", "C1_split", "B2_mesa", "B4_estalo", "B5_final")
    gaps = [[16.9, 17.4]]
    ev = dict(N=N, fps=FPS, duracao_s=round(N / FPS, 3), shots=[SH[nm]["f0"] for nm in big], cortes=[SH[nm]["f0"] for nm, _, _ in PLAN],
              f_pop=F_POP, t_pop=round((F_POP - 1) / FPS, 3), music=None, sfx=[], pills=[], pills_en=[],
              music_gap=gaps[0], music_gaps=gaps,
              silencios=[dict(t0=gaps[0][0], t1=gaps[0][1], motivo="antes da revelacao da ceia (o V sobe do frango no 'ossinho')")],
              marcas=dict(brilho_raiox=F_BRILHO, match_galinha=F_MATCH, acertou=f(wt("acertou")), ossinho=f(wt("ossinho")),
                          duas=f(wt("duas")), claviculas=f(wt("clavículas")), puxar=f(wt("puxar")), estalo=F_POP),
              ponto_furcula_tela=dict(x=P_STAR[0], y=P_STAR[1]),
              planos=[dict(nome=nm, mundo=WORLDS[w_], f0=SH[nm]["f0"], f1=SH[nm]["f1"]) for nm, w_, _ in PLAN])
    json.dump(ev, open(WORK + "/events.json", "w"), ensure_ascii=False, indent=1)
    return ev


# ================================================================ modos
def main():
    mode = sys.argv[-1]
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
        out = os.environ.get("PIPO_BLEND", WORK + "/blend")
        os.makedirs(out, exist_ok=True)
        man = []
        for w_ in ("A", "B", "C"):
            build(w_)
            sc = bpy.context.scene
            seg = segments(w_)
            sc.frame_start, sc.frame_end = seg[0][0], seg[-1][1]
            sc.frame_set(seg[0][0])
            sc.render.filepath = "//frames/f"
            sc.cycles.samples = 16
            try:
                sc.cycles.device = 'GPU'          # no Kaggle: render_kaggle.py liga OPTIX/CUDA (cai para CPU se nao houver GPU)
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
        sc.cycles.samples = int(os.environ.get("PIPO_SPP", "4"))
        for fr in mine:
            sc.frame_set(fr)
            sc.render.filepath = PREV + f"/p_{fr:04d}.png"
            t0 = time.time(); bpy.ops.render.render(write_still=True); t1 = time.time() - t0
            tlog[str(fr)] = dict(plano=shot_of(fr), mundo=WORLDS[w_], quadro_s=round(t1, 2))
            print("TIME", fr, shot_of(fr), round(t1, 2), flush=True)
            json.dump(tlog, open(tlog_p, "w"), indent=1)


if __name__ == "__main__":
    main()
