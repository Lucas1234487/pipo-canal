"""PIPO LIB - biblioteca base do canal (Blender/bpy 5.x).
Uso dentro de um script de episodio:
    WORK = "/home/claude/ep"            # pasta do episodio (timing.json la dentro)
    N = 870                             # total de quadros (30 fps)
    exec(open(KIT + "/pipo_lib.py").read())
Depois: crie props do episodio, anime a Pipo com as funcoes pipo_*, defina shots e chame finish(shots, events).
"""
import bpy, bmesh, math, random, sys, os, json
from mathutils import Vector

D = bpy.data
FPS = 30
W, H = 540, 960
f = lambda t: int(round(t * FPS)) + 1
T = json.load(open(WORK + "/timing.json"))
WT = {}
for l in T["lines"]:
    for w, s_, du in l["words"]:
        WT.setdefault(w.lower().strip(".,!:?…"), []).append(s_)


def wt(word, n=0):
    """tempo (s) da n-esima ocorrencia da palavra na narracao"""
    return WT[word.lower()][n]

bpy.ops.wm.read_factory_settings(use_empty=True)
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.device = 'CPU'
s.cycles.samples = 5
s.cycles.use_adaptive_sampling = True
s.cycles.adaptive_threshold = 0.08
try:
    s.cycles.denoising_prefilter = 'FAST'
    s.cycles.denoising_input_passes = 'RGB_ALBEDO'
except Exception:
    pass
s.cycles.use_denoising = True
s.cycles.max_bounces = 3
s.cycles.diffuse_bounces = 1
s.cycles.glossy_bounces = 0
s.cycles.transmission_bounces = 0
s.cycles.volume_bounces = 0
s.cycles.transparent_max_bounces = 8
s.cycles.filter_width = 1.2
s.render.use_persistent_data = True
s.render.resolution_x, s.render.resolution_y = W, H
s.render.fps = FPS
s.frame_start, s.frame_end = 1, N
s.view_settings.view_transform = 'Standard'
try:
    s.view_settings.look = 'Medium High Contrast'
except Exception:
    pass
s.render.image_settings.file_format = 'PNG'
s.render.image_settings.color_mode = 'RGB'
s.world = D.worlds.new("W")
s.world.use_nodes = True
s.world.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.35, 0.75, 1)
s.world.node_tree.nodes["Background"].inputs[1].default_value = 0.35

LDIR = Vector((-0.45, -0.65, 0.75)).normalized()


def link(o):
    s.collection.objects.link(o)
    return o


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def toon_old(name, col, shade=0.55, hi=1.12, rim=0.25, bands=(0.05, 0.55)):
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    dp = nt.nodes.new("ShaderNodeVectorMath"); dp.operation = 'DOT_PRODUCT'
    dp.inputs[1].default_value = LDIR
    nt.links.new(geo.outputs["Normal"], dp.inputs[0])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.interpolation = 'CONSTANT'
    e = r.color_ramp.elements
    sc = (col[0] * shade * 0.85, col[1] * shade * 0.8, min(1, col[2] * shade * 1.15 + 0.03))
    e[0].position = 0.0; e[0].color = (*sc, 1)
    e[1].position = bands[0] * 0.5 + 0.5; e[1].color = (*col, 1)
    e3 = e.new(bands[1] * 0.5 + 0.5); e3.color = (*[min(1, c * hi) for c in col], 1)
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -1; mr.inputs["From Max"].default_value = 1
    nt.links.new(dp.outputs["Value"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], r.inputs["Fac"])
    # rim
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.82
    nt.links.new(lw.outputs["Facing"], gt.inputs[0])
    ml = nt.nodes.new("ShaderNodeMath"); ml.operation = 'MULTIPLY'; ml.inputs[1].default_value = rim
    nt.links.new(gt.outputs[0], ml.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.blend_type = 'SCREEN'
    nt.links.new(ml.outputs[0], mix.inputs[0])
    nt.links.new(r.outputs["Color"], mix.inputs[6])
    mix.inputs[7].default_value = (0.75, 0.85, 1.0, 1)
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(mix.outputs[2], em.inputs["Color"])
    em.name = "EM"
    nt.links.new(em.outputs[0], out.inputs[0])
    m["base"] = col
    return m


def lit(name, col, rough=0.5, coat=0.0, kernels=False, popcorn=False):
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.name = "EM"
    p.inputs["Base Color"].default_value = (*col, 1)
    p.inputs["Roughness"].default_value = rough
    try:
        p.inputs["Coat Weight"].default_value = 0.0
        p.inputs["Specular IOR Level"].default_value = 0.5 + coat * 0.4
        p.inputs["Coat Roughness"].default_value = 0.15
    except Exception:
        pass
    p.inputs["Emission Color"].default_value = (1.0, 0.35, 0.05, 1)
    p.inputs["Emission Strength"].default_value = 0.0
    if kernels or popcorn:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        vor = nt.nodes.new("ShaderNodeTexVoronoi")
        if kernels:
            vor.feature = 'SMOOTH_F1' if False else 'F1'
            vor.inputs["Scale"].default_value = 22.0
            mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 0.75)
            nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], vor.inputs["Vector"])
            dist = vor.outputs["Distance"]
            rmp = nt.nodes.new("ShaderNodeMapRange"); rmp.inputs["From Min"].default_value = 0.25; rmp.inputs["From Max"].default_value = 0.55
            nt.links.new(dist, rmp.inputs["Value"])
            bmp = nt.nodes.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.6; bmp.invert = True
            nt.links.new(rmp.outputs["Result"], bmp.inputs["Height"]); nt.links.new(bmp.outputs["Normal"], p.inputs["Normal"])
            mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
            nt.links.new(rmp.outputs["Result"], mx.inputs[0])
            mx.inputs[6].default_value = (*col, 1); mx.inputs[7].default_value = (col[0] * 0.75, col[1] * 0.55, col[2] * 0.3, 1)
            nt.links.new(mx.outputs[2], p.inputs["Base Color"])
        else:
            nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 4
            nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
            bmp = nt.nodes.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.35
            nt.links.new(nz.outputs["Fac"], bmp.inputs["Height"]); nt.links.new(bmp.outputs["Normal"], p.inputs["Normal"])
            mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
            nt.links.new(nz.outputs["Fac"], mx.inputs[0])
            mx.inputs[6].default_value = (1.0, 0.97, 0.86, 1); mx.inputs[7].default_value = (0.98, 0.82, 0.5, 1)
            nt.links.new(mx.outputs[2], p.inputs["Base Color"])
        try:
            p.inputs["Subsurface Weight"].default_value = 0.0
        except Exception:
            pass
    return m


def toon(name, col, shade=0.55, hi=1.12, rim=0.25, bands=(0.05, 0.55)):
    return lit(name, col, rough=0.45, coat=0.3)


def flat(name, col, strength=1.0, alpha=None):
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*col, 1)
    em.inputs["Strength"].default_value = strength
    if alpha is None:
        nt.links.new(em.outputs[0], out.inputs[0])
    else:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader"); mx.name = "MIX"
        mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
    return m


OUTL = None


def outline_mat():
    global OUTL
    if OUTL is None:
        m = D.materials.new("outline")
        m.use_nodes = True
        nt = m.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.03, 0.01, 0.05, 1)
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(geo.outputs["Backfacing"], mx.inputs[0])
        nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
        OUTL = m
    return OUTL


def give(o, m, outline=0.02):
    outline = 0
    o.data.materials.clear()
    o.data.materials.append(m)
    if outline:
        o.data.materials.append(outline_mat())
        sd = o.modifiers.new("ol", 'SOLIDIFY')
        sd.thickness = outline
        sd.offset = 1.0
        sd.use_flip_normals = True
        sd.use_rim = False
        sd.material_offset = 1
    return o


def sphere(name, r, loc=(0, 0, 0), seg=40, rings=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=r, location=loc)
    o = bpy.context.object; o.name = name
    return smooth(o)


def empty(name, loc=(0, 0, 0), parent=None):
    o = link(D.objects.new(name, None))
    o.location = loc
    if parent:
        o.parent = parent
    return o


def par(o, p):
    o.parent = p
    return o


def K(o, path, fr, val=None):
    if val is not None:
        setattr(o, path, val)
    o.keyframe_insert(path, frame=fr)


def fcurves(obj):
    ad = obj.animation_data
    out = []
    if not ad or not ad.action:
        return out
    try:
        for ly in ad.action.layers:
            for st in ly.strips:
                for cb in st.channelbags:
                    out += list(cb.fcurves)
    except Exception:
        pass
    if not out:
        try:
            out = list(ad.action.fcurves)
        except Exception:
            pass
    return out


def interp(obj, mode, path=None):
    for fc in fcurves(obj):
        if path and fc.data_path != path:
            continue
        for k in fc.keyframe_points:
            k.interpolation = mode


def text3d(body, size, col, loc=(0, 0, 0), rot=(math.radians(90), 0, 0), parent=None, extrude=0.02, font=None):
    cu = D.curves.new("T", 'FONT')
    cu.body = body
    cu.font = D.fonts.load(font or "/home/claude/canal/Fredoka-700.ttf")
    cu.size = size
    cu.extrude = extrude
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = link(D.objects.new("T", cu))
    o.location = loc; o.rotation_euler = rot
    cu.materials.append(flat("txt" + body, col))
    if parent:
        o.parent = parent
    return o


def pop_scale(o, fr, base=1.0, dur=7):
    K(o, "scale", fr - 1, (0.001,) * 3)
    K(o, "scale", fr + int(dur * 0.6), (base * 1.18,) * 3)
    K(o, "scale", fr + dur, (base,) * 3)


def hide_scale(o, fr, base=1.0, dur=5):
    K(o, "scale", fr, (base,) * 3)
    K(o, "scale", fr + dur, (0.001,) * 3)


# ------------------------------------------------------------- environment
# floor + curved backdrop (one mesh)
bm = bmesh.new()
prof = []
for i in range(0, 25):
    a = i / 24 * (math.pi / 2)
    prof.append((math.sin(a) * 4, 4 - math.cos(a) * 4)) if False else None
# simpler: floor plane + back wall + cylinder quarter
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 10, 0))
floor = bpy.context.object
fm = D.materials.new("floor"); fm.use_nodes = True
nt = fm.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
o_ = nt.nodes.new("ShaderNodeOutputMaterial")
tc = nt.nodes.new("ShaderNodeTexCoord")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tc.outputs["Object"], sep.inputs[0])
# radial spotlight pool around products
ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'
sub = nt.nodes.new("ShaderNodeVectorMath"); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.2, -10.0, 0)
nt.links.new(tc.outputs["Object"], sub.inputs[0]); nt.links.new(sub.outputs[0], ln.inputs[0])
rr = nt.nodes.new("ShaderNodeValToRGB"); rr.color_ramp.interpolation = 'CONSTANT'
rr.color_ramp.elements[0].position = 0.0; rr.color_ramp.elements[0].color = (0.20, 0.07, 0.36, 1)
rr.color_ramp.elements[1].position = 0.5; rr.color_ramp.elements[1].color = (0.13, 0.04, 0.25, 1)
mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0; mr.inputs["From Max"].default_value = 7
nt.links.new(ln.outputs["Value"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], rr.inputs["Fac"])
em = nt.nodes.new("ShaderNodeBsdfPrincipled"); em.inputs["Roughness"].default_value = 0.6
nt.links.new(rr.outputs["Color"], em.inputs["Base Color"])
nt.links.new(em.outputs[0], o_.inputs[0])
floor.data.materials.append(fm)
rr.color_ramp.elements[0].color = (0.42, 0.12, 0.62, 1); rr.color_ramp.elements[1].color = (0.26, 0.06, 0.42, 1)
# lights
def _light(kind, loc, tgt, energy, col=(1, 1, 1), size=1.0, angle=None):
    l = D.lights.new(kind, kind); l.energy = energy; l.color = col
    if kind == 'AREA': l.size = size
    if kind == 'SUN': l.angle = math.radians(angle or 6)
    if kind == 'SPOT': l.spot_size = math.radians(50); l.spot_blend = 0.5; l.shadow_soft_size = size
    o = link(D.objects.new(kind, l)); o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o
_light('SUN', (-3, -5, 6), (0, 0, 0.5), 2.6, (1.0, 0.95, 0.88), angle=8)
_light('AREA', (4, -4, 2.5), (0, 0, 1), 350, (0.75, 0.85, 1.0), size=3)
_light('SPOT', (0.5, 4, 4.5), (-0.3, -0.5, 1.2), 900, (1.0, 0.7, 0.9), size=0.6)

# back wall with halftone dots
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 7, 8), rotation=(math.radians(90), 0, 0))
wall = bpy.context.object
wm = D.materials.new("wall"); wm.use_nodes = True
nt = wm.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
o_ = nt.nodes.new("ShaderNodeOutputMaterial")
tc = nt.nodes.new("ShaderNodeTexCoord")
vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = 'F1'; vor.inputs["Scale"].default_value = 3.0
try:
    vor.inputs["Randomness"].default_value = 0.0
except Exception:
    pass
nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
sepw = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sepw.inputs[0])
# dot size grows toward bottom (halftone gradient)
mrw = nt.nodes.new("ShaderNodeMapRange"); mrw.inputs["From Min"].default_value = -8; mrw.inputs["From Max"].default_value = 6
mrw.inputs["To Min"].default_value = 0.42; mrw.inputs["To Max"].default_value = 0.05
nt.links.new(sepw.outputs["Y"], mrw.inputs["Value"])
lt = nt.nodes.new("ShaderNodeMath"); lt.operation = 'LESS_THAN'
nt.links.new(vor.outputs["Distance"], lt.inputs[0]); nt.links.new(mrw.outputs["Result"], lt.inputs[1])
mxw = nt.nodes.new("ShaderNodeMix"); mxw.data_type = 'RGBA'
nt.links.new(lt.outputs[0], mxw.inputs[0])
mxw.inputs[6].default_value = (0.36, 0.06, 0.42, 1)
mxw.inputs[7].default_value = (0.50, 0.10, 0.52, 1)
emw = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mxw.outputs[2], emw.inputs["Color"])
nt.links.new(emw.outputs[0], o_.inputs[0])
wall.data.materials.append(wm)


# fake shadow blobs (desligados no modo 3D)
shm = flat("blob", (0.05, 0.01, 0.10), 1.0, alpha=0.75)


def blob(loc, sx, sy):
    bpy.ops.mesh.primitive_circle_add(vertices=40, radius=1, fill_type='NGON', location=loc)
    b = bpy.context.object; b.scale = (sx, sy, 1)
    b.data.materials.append(shm)
    b.hide_render = True
    return b

# ------------------------------------------------------------- PIPO
PIPX = -0.85
kern_m = lit("cob", (1.0, 0.70, 0.12), rough=0.35, coat=0.6, kernels=True)
husk_m = lit("husk", (0.42, 0.72, 0.22), rough=0.55, coat=0.0)
white_m = lit("eyew", (0.98, 0.98, 1.0), rough=0.15, coat=0.8)
blk_m = lit("pupil", (0.02, 0.01, 0.03), rough=0.1, coat=1.0)
cream_m = lit("cream", (1.0, 0.92, 0.74), rough=0.4, coat=0.5, popcorn=True)
blush_m = lit("blush", (1.0, 0.45, 0.5), rough=0.6, coat=0.0)
tie_m = lit("tie", (0.95, 0.15, 0.3), rough=0.3, coat=0.6)

pipo = empty("pipo", (PIPX, -0.95, 0))
pipo.scale = (1.45,) * 3
body = empty("body", (0, 0, 0), pipo)

# --- espiguinha (corn cob) ---
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=0.3)
kern = bpy.context.object; kern.name = "cob"
for v in kern.data.vertices:
    z = v.co.z
    v.co.z *= 1.75
    k = 1.0 - 0.18 * max(0, z / 0.3)   # slightly narrower top
    v.co.x *= k; v.co.y *= k
smooth(kern)
give(kern, kern_m, 0)
kern.parent = body; kern.location = (0, 0, 0.6)
# husk leaves wrapping the bottom
def leaf(angle, h=0.62, w=0.28, lean=0.25):
    bm = bmesh.new()
    rows, cols = 8, 5
    vs = []
    for i in range(rows + 1):
        t = i / rows
        width = w * math.sin(math.pi * min(1, t * 1.15 + 0.05)) * (1 - t * 0.55)
        z = -0.5 + t * h
        out = 0.31 + lean * t * t
        row = []
        for j in range(cols + 1):
            u = (j / cols - 0.5) * 2
            a = angle + u * width / 0.33
            r = out * (1 - 0.05 * u * u)
            row.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z)))
        vs.append(row)
    for i in range(rows):
        for j in range(cols):
            bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    me = D.meshes.new("leaf"); bm.to_mesh(me); bm.free()
    o = link(D.objects.new("leaf", me))
    sd = o.modifiers.new("s", 'SOLIDIFY'); sd.thickness = 0.025
    sb = o.modifiers.new("sub", 'SUBSURF'); sb.levels = 1; sb.render_levels = 2
    smooth(o); o.data.materials.append(husk_m)
    o.parent = kern
    return o
for a in (math.radians(-90 + 60), math.radians(-90 - 60), math.radians(90), math.radians(30), math.radians(150)):
    leaf(a, h=0.55 if abs(math.sin(a) + 1) < 0.3 else 0.7)
# little silk tuft on top
for i in range(5):
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.025, radius2=0.004, depth=0.22, location=(0, 0, 0))
    c = bpy.context.object; smooth(c); c.data.materials.append(lit("silk", (0.85, 0.6, 0.3), 0.6, 0))
    c.parent = kern; c.location = ((i - 2) * 0.025, 0.02, 0.55); c.rotation_euler = (0.2, (i - 2) * 0.25, 0)

FACE = {}


def make_face(parent, center, scale, name, lashes=False):
    root = empty(name + "_face", center, parent)
    root.scale = (scale,) * 3
    d = dict(root=root, lids=[], pupils=[], brows=[])
    for sx in (-1, 1):
        e = sphere(name + "eye", 0.15, (sx * 0.17, 0, 0), 32, 16); give(e, white_m, 0); e.parent = root
        pe = empty(name + "pupil_e", (sx * 0.17, 0, 0), root)
        p = sphere(name + "pupil", 0.08, (0, -0.1, 0), 24, 12); p.data.materials.append(blk_m); p.parent = pe
        hl = sphere(name + "hl", 0.024, (0.03, -0.175, 0.035), 12, 6); hl.data.materials.append(flat("hlw", (1, 1, 1), 2.0)); hl.parent = pe
        d["pupils"].append(pe)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.162)
        lid = bpy.context.object
        bml = bmesh.new(); bml.from_mesh(lid.data)
        bmesh.ops.delete(bml, geom=[v for v in bml.verts if v.co.z < -0.005], context='VERTS')
        bml.to_mesh(lid.data); bml.free()
        smooth(lid)
        give(lid, parent_m[name], 0)
        le = empty(name + "lid_e", (sx * 0.17, 0, 0), root)
        lid.parent = le
        if lashes:
            for k in range(3):
                bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.014, radius2=0.002, depth=0.08)
                ls = bpy.context.object; ls.data.materials.append(blk_m); ls.parent = lid
                a = math.radians(-35 + k * 35) * sx
                ls.location = (math.sin(a) * 0.15 + sx * 0.04, -0.13, 0.03 + math.cos(a) * 0.02)
                ls.rotation_euler = (math.radians(-60), 0, 0)
                ls.rotation_euler.y = -sx * (0.5 + k * 0.25)
        d["lids"].append(le)
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.026, depth=0.19, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
        br = bpy.context.object; smooth(br)
        bvb = br.modifiers.new("bv", 'BEVEL'); bvb.width = 0.024; bvb.segments = 3
        br.data.materials.append(lit("brow", (0.35, 0.16, 0.06), 0.5, 0))
        be = empty(name + "brow_e", (sx * 0.17, -0.06, 0.24), root)
        br.parent = be
        d["brows"].append(be)
    return d


parent_m = {"k": kern_m, "p": cream_m}
FK = make_face(kern, (0, -0.27, 0.16), 0.82, "k")


# --- menininha de pipoca (premium mushroom popcorn with pigtails) ---
def metaball_mesh(name, elems, res=0.07):
    mb = D.metaballs.new(name)
    mb.resolution = res; mb.render_resolution = res
    for c, r in elems:
        e = mb.elements.new(); e.co = c; e.radius = r
    o = link(D.objects.new(name, mb))
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    o = bpy.context.object
    o.name = name
    return smooth(o)


pop_root = empty("pop_root", (0, 0, 0.75), body)
random.seed(4)
# head: round premium popcorn with gentle lumps
head_el = [((0, 0, 0.3), 0.78)] + [((math.cos(a) * 0.46, math.sin(a) * 0.36, 0.3 + math.sin(a * 3) * 0.14), 0.32) for a in [i * 2 * math.pi / 9 for i in range(9)]]
head_el += [((0.16, -0.08, 0.78), 0.3), ((-0.18, -0.02, 0.8), 0.28), ((0.0, 0.12, 0.86), 0.26)]
head = metaball_mesh("pophead", head_el)
give(head, cream_m, 0); head.parent = pop_root
# pigtails (maria-chiquinha): butterfly popcorn flaps on each side
popo = head
for sx in (-1, 1):
    el = [((sx * 0.68, 0.05, 0.55), 0.3), ((sx * 0.86, 0.0, 0.38), 0.3), ((sx * 0.95, 0.05, 0.16), 0.28), ((sx * 0.97, 0.0, -0.06), 0.24),
          ((sx * 0.82, 0.12, 0.25), 0.22), ((sx * 1.05, -0.05, 0.3), 0.2)]
    pt = metaball_mesh("pigtail", el)
    give(pt, cream_m, 0); pt.parent = pop_root
    bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.04, location=(0, 0, 0))
    tie = bpy.context.object; smooth(tie); tie.data.materials.append(tie_m); tie.parent = pop_root
    tie.location = (sx * 0.6, 0.0, 0.62); tie.rotation_euler = (0, math.radians(90 - sx * 30), 0)
# body (small puff dress) + golden hull skirt
bod = metaball_mesh("popbody", [((0, 0, -0.38), 0.5), ((0.2, 0, -0.5), 0.3), ((-0.2, 0, -0.5), 0.3), ((0, -0.05, -0.22), 0.36)])
give(bod, cream_m, 0); bod.parent = pop_root
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.32)
hull = bpy.context.object
for v in hull.data.vertices:
    if v.co.z > 0.0:
        v.co.z *= 0.25
    v.co.x *= 1.1; v.co.y *= 1.1
smooth(hull); give(hull, kern_m, 0); hull.parent = pop_root; hull.location = (0, 0.02, -0.62)
for sx in (-1, 1):
    ch = sphere("blush", 0.08, (sx * 0.4, -0.6, 0.12), 16, 8); ch.scale = (1, 0.4, 0.6); ch.data.materials.append(blush_m); ch.parent = pop_root
FP = make_face(pop_root, (0, -0.62, 0.32), 1.05, "p", lashes=True)


def set_face(F, fr, lid=None, brow=None, look=None, browL=None):
    if lid is not None:
        for le in F["lids"]:
            K(le, "rotation_euler", fr, (math.radians(lid), 0, 0))
    if brow is not None:
        for i, be in enumerate(F["brows"]):
            sgn = 1 if i == 0 else -1
            b = brow if (browL is None or i == 1) else browL
            K(be, "rotation_euler", fr, (0, math.radians(-sgn * b[0]), 0))
            K(be, "location", fr, (be.location.x, be.location.y, b[1]))
    if look is not None:
        for pe in F["pupils"]:
            K(pe, "rotation_euler", fr, (math.radians(look[1]), 0, math.radians(-look[0])))


def blink(F, fr, base):
    set_face(F, fr - 1, lid=base)
    set_face(F, fr + 2, lid=40)
    set_face(F, fr + 5, lid=base)


# kernel: deadpan/tired default, one brow raised = signature
TIRED = -22
set_face(FK, 1, lid=TIRED, brow=(8, 0.24), browL=(-12, 0.29), look=(-18, 0))      # looks at the tag
blink(FK, 40, TIRED)

TIRED = -22   # palpebra padrao: cara de tedio (assinatura)
SIGN = dict(lid=TIRED, brow=(8, 0.24), browL=(-12, 0.29))   # sobrancelha levantada (marca registrada)


def pipo_place(x=-0.85, y=-0.95, scale=1.45):
    pipo.location = (x, y, 0); pipo.scale = (scale,) * 3


def pipo_idle(F, f0, f1, period=24):
    for i, fr in enumerate(range(f0, f1, period)):
        K(body, "scale", fr, (1.0, 1.0, 1.0) if i % 2 == 0 else (1.03, 1.03, 0.96))


def pipo_hop(fr, h=0.3):
    K(body, "location", fr, (0, 0, 0)); K(body, "location", fr + 5, (0, 0, h)); K(body, "location", fr + 10, (0, 0, 0))
    K(body, "scale", fr + 10, (1.12, 1.12, 0.85)); K(body, "scale", fr + 15, (1, 1, 1))


def pipo_tension(f0, f1):
    """espiguinha treme e esquenta antes de estourar"""
    for fr in range(f0, f1 - 2, 3):
        j = (fr - f0) / max(1, (f1 - f0))
        K(body, "location", fr, (random.uniform(-1, 1) * 0.02 * j, 0, 0))
        K(body, "scale", fr, (1 + 0.08 * j, 1 + 0.08 * j, 1 - 0.06 * j))
    K(body, "location", f1 - 2, (0, 0, 0))
    emk = kern_m.node_tree.nodes["EM"].inputs["Emission Strength"]
    emk.default_value = 0.0; emk.keyframe_insert("default_value", frame=f0)
    emk.default_value = 1.2; emk.keyframe_insert("default_value", frame=f1 - 1)
    emk.default_value = 0.0; emk.keyframe_insert("default_value", frame=f1 + 1)


def pipo_start_kernel():
    K(kern, "scale", 1, (1, 1, 1)); K(pop_root, "scale", 1, (0.001,) * 3)


def pipo_start_popped():
    K(kern, "scale", 1, (0.001,) * 3); K(pop_root, "scale", 1, (1,) * 3)


def pipo_pop(fp, burst=True, size=1.0):
    """O ESTOURO: espiguinha some, menininha de pipoca aparece (com particulas, anel e raios)"""
    K(kern, "scale", fp - 1, (1, 1, 1)); K(kern, "scale", fp, (0.001,) * 3)
    K(pop_root, "scale", fp - 1, (0.001,) * 3)
    K(pop_root, "scale", fp + 3, (1.35 * size,) * 3); K(pop_root, "scale", fp + 8, (0.92 * size,) * 3); K(pop_root, "scale", fp + 12, (size,) * 3)
    set_face(FP, fp, lid=-85, brow=(15, 0.33), browL=(15, 0.33), look=(0, -6))
    if not burst:
        return
    random.seed(fp)
    for i in range(26):
        pz = sphere("puff", random.uniform(0.06, 0.12), (0, 0, 0), 12, 6)
        give(pz, cream_m, 0.0)
        pz.parent = pipo
        v = Vector((random.uniform(-1, 1), random.uniform(-0.6, 0.2), random.uniform(0.2, 1.2))).normalized() * random.uniform(1.0, 2.0)
        p0 = Vector((0, 0, 0.7))
        K(pz, "scale", 1, (0.001,) * 3); K(pz, "scale", fp - 1, (0.001,) * 3); K(pz, "scale", fp, (1,) * 3)
        for k in range(0, 22, 3):
            tt = k / 30
            K(pz, "location", fp + k, p0 + v * tt + Vector((0, 0, -1.5)) * tt * tt)
        K(pz, "scale", fp + 14, (1,) * 3); K(pz, "scale", fp + 22, (0.001,) * 3)
    bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.04, major_segments=64, minor_segments=8, location=(0, -0.2, 0.75), rotation=(math.radians(90), 0, 0))
    ring = bpy.context.object; ring.parent = pipo
    ring.data.materials.append(flat("ring", (1.0, 0.95, 0.6), 2.0))
    K(ring, "scale", 1, (0.001,) * 3); K(ring, "scale", fp - 1, (0.001,) * 3)
    K(ring, "scale", fp, (0.3,) * 3); K(ring, "scale", fp + 7, (1.6, 1.6, 0.4)); K(ring, "scale", fp + 8, (0.001,) * 3)
    for i in range(10):
        a = i / 10 * 2 * math.pi
        bpy.ops.mesh.primitive_cube_add(size=1)
        ray = bpy.context.object; ray.parent = pipo
        ray.data.materials.append(flat("ray", (1.0, 0.85, 0.2), 1.5))
        ray.location = (math.cos(a) * 0.9, -0.3, 0.75 + math.sin(a) * 0.9)
        ray.rotation_euler = (0, -a, 0)
        K(ray, "scale", 1, (0.001,) * 3); K(ray, "scale", fp, (0.001,) * 3)
        K(ray, "scale", fp + 2, (0.45, 0.03, 0.06)); K(ray, "scale", fp + 9, (0.001,) * 3)
        K(ray, "location", fp + 9, (math.cos(a) * 1.4, -0.3, 0.75 + math.sin(a) * 1.4))


def pipo_unpop(fr, size=1.0):
    """volta a ser espiguinha (para o loop final)"""
    K(pop_root, "scale", fr, (size,) * 3); K(pop_root, "scale", fr + 4, (1.1 * size,) * 3); K(pop_root, "scale", fr + 9, (0.001,) * 3)
    K(kern, "scale", fr + 8, (0.001,) * 3); K(kern, "scale", fr + 13, (1.08,) * 3); K(kern, "scale", fr + 17, (1.0,) * 3)


def confetti(f0, center=(0.3, 0, 0), n=70):
    cols = [(0.15, 0.85, 0.85), (1.0, 0.82, 0.12), (0.95, 0.12, 0.2), (1, 1, 1), (0.5, 0.9, 0.3)]
    cms = [flat("cf%d" % i, c) for i, c in enumerate(cols)]
    for i in range(n):
        bpy.ops.mesh.primitive_plane_add(size=0.09)
        cf = bpy.context.object
        cf.data.materials.append(random.choice(cms))
        x = center[0] + random.uniform(-2.3, 2.3); y = random.uniform(-1.5, 1.0)
        z0 = random.uniform(3.6, 5.5)
        st = f0 + random.randint(0, 25)
        K(cf, "location", st, (x, y, z0))
        K(cf, "location", st + 90, (x + random.uniform(-0.6, 0.6), y, z0 - random.uniform(3.6, 5.0)))
        K(cf, "rotation_euler", st, (random.uniform(0, 6), random.uniform(0, 6), 0))
        K(cf, "rotation_euler", st + 90, (random.uniform(6, 16), random.uniform(6, 16), 3))
        K(cf, "scale", 1, (0.001,) * 3); K(cf, "scale", st - 1, (0.001,) * 3); K(cf, "scale", st, (1,) * 3)
        K(cf, "scale", st + 88, (1,) * 3); K(cf, "scale", st + 90, (0.001,) * 3)
        interp(cf, 'LINEAR', "location")


def aim(loc, tgt):
    return (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()


def finish(shots, events, shake_at=None, dof=None):
    """shots: lista de (t_inicio_s, loc_inicio, loc_fim, alvo, lente). Corte seco entre shots, drift linear dentro.
    events: dict salvo em WORK/events.json para o compose (precisa de N, shots, f_pop, sfx, pills)."""
    cd = D.cameras.new("Cam"); cd.lens = 32; cd.clip_start = 0.05
    cam = link(D.objects.new("Cam", cd)); s.camera = cam
    if dof:
        foco = empty("foco", (0, 0, 0.55), dof[0])      # mira no rosto, nao no chao
        cd.dof.use_dof = True; cd.dof.focus_object = foco; cd.dof.aperture_fstop = dof[1]
    for i, (t0, a, b, tgt, lens) in enumerate(shots):
        t1 = shots[i + 1][0] if i + 1 < len(shots) else N / 30
        f0, f1 = f(t0), max(f(t0) + 1, f(t1) - 1)
        cam.location = a; cam.rotation_euler = aim(a, tgt); cd.lens = lens
        cam.keyframe_insert("location", frame=f0); cam.keyframe_insert("rotation_euler", frame=f0); cd.keyframe_insert("lens", frame=f0)
        cam.location = b; cam.rotation_euler = aim(b, tgt)
        cam.keyframe_insert("location", frame=f1); cam.keyframe_insert("rotation_euler", frame=f1); cd.keyframe_insert("lens", frame=f1)
    for fc in fcurves(cam):
        for j, k in enumerate(fc.keyframe_points):
            k.interpolation = 'LINEAR' if j % 2 == 0 else 'CONSTANT'
    for fc in fcurves(cd):
        for k in fc.keyframe_points:
            k.interpolation = 'CONSTANT'
    if shake_at:
        for fc in fcurves(cam):
            if fc.data_path == "location":
                m = fc.modifiers.new('NOISE'); m.strength = 0.06; m.scale = 1.2
                m.use_restricted_range = True; m.frame_start = shake_at; m.frame_end = shake_at + 14; m.blend_out = 10
    events = dict(events); events["N"] = N; events["shots"] = [f(x[0]) for x in shots]
    json.dump(events, open(WORK + "/events.json", "w"), ensure_ascii=False, indent=1)
    mode = sys.argv[-1]
    if mode == "qa":
        run_qa()
        return
    os.makedirs(WORK + "/frames", exist_ok=True); os.makedirs(WORK + "/prev", exist_ok=True)
    if mode == "full":
        rg = os.environ.get("PIPO_RANGE")          # "a-b": usado pelo render_par.py para dividir o trabalho
        if rg:
            a, b = [int(x) for x in rg.split("-")]
            s.frame_start, s.frame_end = a, b
        th = int(os.environ.get("PIPO_THREADS", "0"))
        if th:
            s.render.threads_mode = 'FIXED'; s.render.threads = th
        s.render.filepath = WORK + "/frames/f"
        s.render.use_overwrite = False
        s.render.use_placeholder = True
        bpy.ops.render.render(animation=True)
    else:
        import time
        for fr in [int(x) for x in mode.split(",")]:
            s.frame_set(fr)
            s.render.filepath = WORK + f"/prev/p_{fr:04d}.png"
            t = time.time()
            bpy.ops.render.render(write_still=True)
            print("TIME", fr, round(time.time() - t, 2))


# ------------------------------------------------------------- QA (revisao automatica de sobreposicao)
QA_KEYS = {}
QA_TOUCH = set()


def qa_touch(a, b):
    """declara que dois grupos encostam/sobrepoem DE PROPOSITO (ex.: etiqueta pendurada no fone)"""
    QA_TOUCH.add(tuple(sorted((a, b))))


def qa_key(name, *objs):
    """marca objetos importantes do episodio para a revisao (ex.: qa_key("etiqueta", tag_piv))"""
    QA_KEYS[name] = objs


def _meshes_under(o):
    out = [o] if o.type in ('MESH', 'FONT', 'META') else []
    for c in o.children_recursive:
        if c.type in ('MESH', 'FONT') and not c.hide_render:
            out.append(c)
    return out


def _bbox2d(objs, cam):
    from bpy_extras.object_utils import world_to_camera_view
    xs, ys = [], []
    for o in objs:
        if o.hide_render:
            continue
        mw = o.matrix_world
        if mw.to_scale().length < 0.01:
            continue
        for c in o.bound_box:
            p = world_to_camera_view(s, cam, mw @ Vector(c))
            if p.z > 0:
                xs.append(p.x); ys.append(1 - p.y)   # y de cima para baixo
    if not xs:
        return None
    return [min(xs), min(ys), max(xs), max(ys)]


def run_qa(step=3, bvh_step=15):
    """modo qa: nao renderiza; mede sobreposicao entre grupos-chave, corte na borda,
    texto 3D na faixa da legenda/pilula e objetos atravessando (BVH). Grava WORK/qa_scene.json"""
    from mathutils.bvhtree import BVHTree
    cam = s.camera
    groups = dict(QA_KEYS)
    groups.setdefault("pipo_espiga", (kern,))
    groups.setdefault("pipo_pipoca", (pop_root,))
    gm = {k: sum((_meshes_under(o) for o in v), []) for k, v in groups.items()}
    texts = [o for o in bpy.data.objects if o.type == 'FONT' and not o.hide_render]
    issues, boxes = [], {}
    deps = bpy.context.evaluated_depsgraph_get()
    for fr in range(1, N + 1, step):
        s.frame_set(fr)
        bx = {k: _bbox2d(v, cam) for k, v in gm.items()}
        bx = {k: b for k, b in bx.items() if b and (b[2] - b[0]) * (b[3] - b[1]) > 0.0004}
        boxes[fr] = bx
        ks = list(bx)
        for i in range(len(ks)):
            a = bx[ks[i]]
            w = a[2] - a[0]
            if a[0] < -0.35 * w or a[2] > 1 + 0.35 * w:
                issues.append(dict(frame=fr, tipo="cortado_na_borda", alvo=ks[i]))
            for j in range(i + 1, len(ks)):
                b = bx[ks[j]]
                if tuple(sorted((ks[i], ks[j]))) in QA_TOUCH:
                    continue
                ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
                amin = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
                if amin > 0 and ix * iy / amin > 0.15:
                    issues.append(dict(frame=fr, tipo="imagens_sobrepostas", alvo=f"{ks[i]} x {ks[j]}", fracao=round(ix * iy / amin, 2)))
        for t in texts:
            b = _bbox2d([t], cam)
            if not b or (b[2] - b[0]) < 0.03:
                continue
            for band, (y0, y1) in (("legenda", (0.58, 0.70)), ("pilula", (0.11, 0.20))):
                if b[1] < y1 and b[3] > y0 and b[2] > 0.1 and b[0] < 0.9:
                    issues.append(dict(frame=fr, tipo=f"texto3d_na_faixa_da_{band}", alvo=t.data.body))
        if fr % bvh_step == 1:
            trees = {}
            for k, objs in gm.items():
                if k not in bx:
                    continue
                for o in objs:
                    if o.type != 'MESH' or o.matrix_world.to_scale().length < 0.05:
                        continue
                    try:
                        oe = o.evaluated_get(deps)
                        me = oe.to_mesh()
                        vs = [oe.matrix_world @ v.co for v in me.vertices]
                        ps = [tuple(p.vertices) for p in me.polygons]
                        trees.setdefault(k, []).append(BVHTree.FromPolygons(vs, ps))
                        oe.to_mesh_clear()
                    except Exception:
                        pass
            kk = list(trees)
            for i in range(len(kk)):
                for j in range(i + 1, len(kk)):
                    if tuple(sorted((kk[i], kk[j]))) in QA_TOUCH:
                        continue
                    hit = any(ta.overlap(tb) for ta in trees[kk[i]] for tb in trees[kk[j]])
                    if hit:
                        issues.append(dict(frame=fr, tipo="objetos_atravessando", alvo=f"{kk[i]} x {kk[j]}"))
    json.dump(dict(issues=issues, boxes={str(k): v for k, v in boxes.items()}), open(WORK + "/qa_scene.json", "w"), ensure_ascii=False)
    print("QA_SCENE", len(issues), "ocorrencias")
