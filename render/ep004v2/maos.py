"""Maos do ep004 v2: bracos "Low Poly Arms (Rigged)" (DevMops, CC0, assets/modelos/maos_arms_lowpoly) posados em pinca
(polegar + indicador seguram a ponta do ossinho, os outros dedos dobrados) e assados numa malha estatica suavizada.
A pose e assada no build (o .blend final nao depende do rig Rigify nem de Python): cada mao vira um objeto rigido
que o ep.py anima (puxao, tremor, tranco do estalo)."""
import os, math
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

D = bpy.data
ASSETS = os.environ.get("PIPO_ASSETS", "/home/claude/pipo-canal/assets/modelos")
ARMS = ASSETS + "/maos_arms_lowpoly/arms_low_poly.blend"

# curvatura por dedo (graus nas falanges 01, 02, 03): pinca lateral (chave) com o polegar por cima do indicador
POSE = {
    "f_index": (38, 62, 40),
    "f_middle": (62, 88, 55),
    "f_ring": (70, 92, 58),
    "f_pinky": (78, 95, 60),
}
THUMB = {"thumb.01": (0, 0, 0), "thumb.02": (22, 0, 0), "thumb.03": (28, 0, 0)}


def mat_pele(name="pele_mao", col=(0.78, 0.5, 0.36)):
    m = D.materials.get(name)
    if m:
        return m
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 180; nz.inputs["Detail"].default_value = 3
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = (col[0] * 0.86, col[1] * 0.8, col[2] * 0.8, 1)
    rp.color_ramp.elements[1].color = (min(1, col[0] * 1.06), col[1] * 1.04, col[2] * 1.02, 1)
    nt.links.new(nz.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.48
    for k, v in (("Subsurface Weight", 0.35), ("Subsurface Scale", 0.006), ("Specular IOR Level", 0.45), ("Sheen Weight", 0.15)):
        try:
            p.inputs[k].default_value = v
        except Exception:
            pass
    try:
        p.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.18)
    except Exception:
        pass
    pn = nt.nodes.new("ShaderNodeTexNoise"); pn.inputs["Scale"].default_value = 900; pn.inputs["Detail"].default_value = 2
    nt.links.new(tc.outputs["Object"], pn.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.08; bp.inputs["Distance"].default_value = 0.0005
    nt.links.new(pn.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def mat_unha(name="unha"):
    m = D.materials.get(name)
    if m:
        return m
    m = D.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.86, 0.62, 0.56, 1); p.inputs["Roughness"].default_value = 0.22
    try:
        p.inputs["Coat Weight"].default_value = 0.5; p.inputs["Subsurface Weight"].default_value = 0.2
        p.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.3); p.inputs["Subsurface Scale"].default_value = 0.002
    except Exception:
        pass
    return m


def _append():
    before = set(D.objects)
    with D.libraries.load(ARMS, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if n in ("Arm", "rig")]
    objs = [o for o in dst.objects if o]
    for o in objs:
        bpy.context.scene.collection.objects.link(o)
    return {o.name.split(".")[0]: o for o in objs}


def bake_maos(curl_extra=0.0):
    """devolve {'L': obj, 'R': obj}: malhas assadas (pinca), origem no ponto da pinca (entre a ponta do polegar e o indicador),
    eixo -Y local = direcao do antebraco para a mao (para onde a mao aponta). Unidade: metros (mao adulta ~19 cm)."""
    A = _append()
    rig, arm = A["rig"], A["Arm"]
    for side in ("L", "R"):
        pb = rig.pose.bones.get("upper_arm_parent." + side)
        if pb is not None:
            pb["IK_FK"] = 1.0
    for pb in rig.pose.bones:
        pb.rotation_mode = 'XYZ'
    for side in ("L", "R"):
        for fn, angs in POSE.items():
            for i, a in enumerate(angs):
                b = rig.pose.bones.get(f"{fn}.0{i + 1}.{side}")
                if b:
                    b.rotation_euler = (math.radians(a + curl_extra), 0, 0)
        for bn, (ax, ay, az) in THUMB.items():
            b = rig.pose.bones.get(f"{bn}.{side}")
            if b:
                b.rotation_euler = (math.radians(ax), math.radians(ay), math.radians(az))
        # punho levemente dobrado (mao firme puxando)
        h = rig.pose.bones.get("hand_fk." + side)
        if h:
            h.rotation_euler = (math.radians(-8), 0, 0)
    bpy.context.view_layer.update()
    # ponto da pinca e dorsos das unhas
    out = {}
    deps = bpy.context.evaluated_depsgraph_get()
    sd = arm.modifiers.new("sub", 'SUBSURF'); sd.levels = 2; sd.render_levels = 2
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    ae = arm.evaluated_get(deps)
    me_all = bpy.data.meshes.new_from_object(ae)
    me_all.transform(arm.matrix_world)
    pele = mat_pele(); unha = mat_unha()
    rw = rig.matrix_world
    for side in ("L", "R"):
        sg = 1 if side == "L" else -1
        bm = bmesh.new(); bm.from_mesh(me_all)
        kill = [v for v in bm.verts if v.co.x * sg < 0.0]
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
        me = bpy.data.meshes.new("mao_" + side); bm.to_mesh(me); bm.free()
        me.materials.clear(); me.materials.append(pele); me.materials.append(unha)
        for p in me.polygons:
            p.use_smooth = True; p.material_index = 0
        # unhas: lentes achatadas na ponta de cada dedo, no dorso
        th = rig.pose.bones["thumb.03." + side]; ix = rig.pose.bones["f_index.03." + side]
        pinch = (rw @ th.tail).lerp(rw @ ix.head, 0.5)
        hand = rig.pose.bones["hand_fk." + side]
        fwd = ((rw @ hand.tail) - (rw @ hand.head)).normalized()
        bm = bmesh.new(); bm.from_mesh(me)
        for fn in ("f_index", "f_middle", "f_ring", "f_pinky", "thumb"):
            b = rig.pose.bones[f"{fn}.03.{side}"]
            mw = rw @ b.matrix
            y = (mw.to_3x3() @ Vector((0, 1, 0))).normalized()
            z = (mw.to_3x3() @ Vector((0, 0, 1))).normalized()
            ln = b.length * rw.to_scale().x
            # o dorso do dedo: o lado da malha mais distante do centro do dedo na direcao +Z ou -Z do osso
            c = (rw @ b.head).lerp(rw @ b.tail, 0.62)
            best = None
            for sgn in (1, -1):
                d = z * sgn
                far = max(((v.co - c).dot(d) for v in bm.verts if (v.co - c).length < ln * 0.9), default=0)
                if best is None or far > best[0]:
                    best = (far, d)
            far, dz = best
            w = ln * (0.42 if fn != "thumb" else 0.5)
            ret = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=8, radius=1.0)
            vs = ret["verts"]
            xax = y.cross(dz).normalized()
            M_ = Matrix((xax, y, dz)).transposed()
            for v in vs:
                lc = v.co.copy()
                v.co = c + y * (ln * 0.12) + dz * (far - w * 0.08) + M_ @ Vector((lc.x * w * 0.5, lc.y * w * 0.62, lc.z * w * 0.13))
            for f_ in {f for v in vs for f in v.link_faces}:
                f_.material_index = 1; f_.smooth = True
        bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("mao_" + side, me)
        bpy.context.scene.collection.objects.link(o)
        # origem no ponto da pinca
        me.transform(Matrix.Translation(-pinch))
        o.location = (0, 0, 0)
        out[side] = dict(obj=o, fwd=fwd, pinch=pinch)
    D.meshes.remove(me_all)
    for o in (rig, arm):
        D.objects.remove(o, do_unlink=True)
    for o in list(D.objects):
        if o.name.startswith("WGT-"):
            D.objects.remove(o, do_unlink=True)
    # o material e a textura originais do pacote nao sao usados (pele propria): saem para o .blend ficar portatil
    for m in list(D.materials):
        if m.users == 0:
            D.materials.remove(m)
    for im in list(D.images):
        if im.name.startswith("Hand Texture") or im.users == 0:
            D.images.remove(im)
    return out
