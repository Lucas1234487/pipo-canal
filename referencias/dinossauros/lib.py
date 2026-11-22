import bpy, math, random, os, sys
from mathutils import Vector, Euler, Matrix

D = bpy.data
DIR = "/home/claude/v"
W, H, FPS = 540, 960, 30


def reset(frames, samples=4):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = samples
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.05
    s.cycles.use_denoising = True
    try:
        s.cycles.denoiser = 'OPENIMAGEDENOISE'
        s.cycles.denoising_prefilter = 'FAST'
    except Exception:
        pass
    s.cycles.max_bounces = 3
    s.cycles.diffuse_bounces = 1
    s.cycles.glossy_bounces = 1
    s.cycles.transmission_bounces = 2
    s.cycles.transparent_max_bounces = 6
    s.cycles.volume_bounces = 0
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.render.use_persistent_data = True
    s.render.resolution_x, s.render.resolution_y = W, H
    s.render.resolution_percentage = 100
    s.render.fps = FPS
    s.frame_start, s.frame_end = 1, frames
    s.view_settings.view_transform = 'AgX'
    try:
        s.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGB'
    s.world = D.worlds.new("W")
    return s


def bloom(s, threshold=1.0, size=7, mix=0.0):
    try:
        tree = D.node_groups.new("Comp", "CompositorNodeTree")
        s.compositing_node_group = tree
        tree.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = tree.nodes.new("CompositorNodeRLayers")
        g = tree.nodes.new("CompositorNodeGlare")
        out = tree.nodes.new("NodeGroupOutput")
        # 5.x: options are sockets
        for name, val in (("Type", 'Bloom'), ("Quality", 'Medium')):
            if name in g.inputs:
                try:
                    g.inputs[name].default_value = val
                except Exception:
                    pass
        for name, val in (("Threshold", threshold), ("Size", 0.6), ("Strength", 0.8)):
            if name in g.inputs:
                try:
                    g.inputs[name].default_value = val
                except Exception:
                    pass
        tree.links.new(rl.outputs["Image"], g.inputs["Image"])
        tree.links.new(g.outputs["Image"], out.inputs[0])
        return True
    except Exception as e:
        print("BLOOM FAIL", e)
        return False


# ---------------- materials ----------------
def mat(name, color=(0.8, 0.8, 0.8), rough=0.6, emit=None, estr=0.0, metal=0.0, noise_bump=0.0, noise_scale=8.0, color2=None):
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = estr
    if noise_bump > 0 or color2:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise_scale
        nz.inputs["Detail"].default_value = 6
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        if noise_bump > 0:
            b = nt.nodes.new("ShaderNodeBump")
            b.inputs["Strength"].default_value = noise_bump
            nt.links.new(nz.outputs["Fac"], b.inputs["Height"])
            nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
        if color2:
            mx = nt.nodes.new("ShaderNodeMix")
            mx.data_type = 'RGBA'
            mx.inputs[6].default_value = (*color, 1)
            mx.inputs[7].default_value = (*color2, 1)
            nt.links.new(nz.outputs["Fac"], mx.inputs[0])
            nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    return m


def emis(name, color, strength):
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def emis_fade(name, color, strength):
    """emission mixed with transparency; returns (material, mix node) so alpha can be keyed via node input 0"""
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*color, 1)
    e.inputs["Strength"].default_value = strength
    t = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    mx.inputs[0].default_value = 1.0
    nt.links.new(t.outputs[0], mx.inputs[1])
    nt.links.new(e.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], o.inputs[0])
    return m, mx, e


def key(obj, path, frame, val, idx=None):
    if idx is None:
        setattr(obj, path, val) if not hasattr(getattr(obj, path), "__len__") else setattr(obj, path, val)
        obj.keyframe_insert(path, frame=frame)
    else:
        getattr(obj, path)[idx] = val
        obj.keyframe_insert(path, index=idx, frame=frame)


def ksock(sock, frame, val):
    sock.default_value = val
    sock.keyframe_insert("default_value", frame=frame)


def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o


def setmat(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def sphere(name, r, loc=(0, 0, 0), seg=48, rings=24, m=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=r, location=loc)
    o = bpy.context.object
    o.name = name
    smooth(o)
    if m:
        setmat(o, m)
    return o


def ico(name, r, loc=(0, 0, 0), sub=3, m=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc)
    o = bpy.context.object
    o.name = name
    smooth(o)
    if m:
        setmat(o, m)
    return o


def camera(loc, target=None, lens=35):
    c = D.cameras.new("Cam")
    c.lens = lens
    c.clip_start = 0.05
    c.clip_end = 2000
    o = link(D.objects.new("Cam", c))
    o.location = loc
    bpy.context.scene.camera = o
    if target is not None:
        look(o, target)
    return o


def look(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def key_cam(o, frame, loc, target):
    o.location = loc
    look(o, target)
    o.keyframe_insert("location", frame=frame)
    o.keyframe_insert("rotation_euler", frame=frame)


def sun(rot=(0.8, 0.2, 0.6), strength=4.0, color=(1, 0.97, 0.9), angle=0.02, direction=None):
    if direction is not None:
        rot = Vector(direction).normalized().to_track_quat('-Z', 'Y').to_euler()
    l = D.lights.new("Sun", 'SUN')
    l.energy = strength
    l.color = color
    l.angle = angle
    o = link(D.objects.new("Sun", l))
    o.rotation_euler = rot
    return o


def point(loc, energy, color=(1, 1, 1), radius=0.2):
    l = D.lights.new("Pt", 'POINT')
    l.energy = energy
    l.color = color
    l.shadow_soft_size = radius
    o = link(D.objects.new("Pt", l))
    o.location = loc
    return o


def world_color(s, color, strength=1.0):
    w = s.world
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*color, 1)
    bg.inputs["Strength"].default_value = strength
    return bg


def world_gradient(s, top, bottom, strength=1.0):
    """vertical sky gradient; returns (bg node, ramp) for animation"""
    w = s.world
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45
    ramp.color_ramp.elements[0].color = (*bottom, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*top, 1)
    mp = nt.nodes.new("ShaderNodeMapRange")
    mp.inputs["From Min"].default_value = -1
    mp.inputs["From Max"].default_value = 1
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mp.inputs["Value"])
    nt.links.new(mp.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    return bg, ramp


def world_stars(s, density=0.985, strength=1.0):
    w = s.world
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 400
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (3, 3, 3, 1)
    ramp.color_ramp.elements[1].position = 0.04
    ramp.color_ramp.elements[1].color = (0, 0, 0, 1)
    nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
    nt.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    add = nt.nodes.new("ShaderNodeMix")
    add.data_type = 'RGBA'
    add.blend_type = 'ADD'
    add.inputs[0].default_value = 1
    neb = nt.nodes.new("ShaderNodeValToRGB")
    neb.color_ramp.elements[0].color = (0.0, 0.0, 0.002, 1)
    neb.color_ramp.elements[1].color = (0.006, 0.002, 0.014, 1)
    nt.links.new(tc.outputs["Generated"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], neb.inputs["Fac"])
    nt.links.new(neb.outputs["Color"], add.inputs[6])
    nt.links.new(ramp.outputs["Color"], add.inputs[7])
    nt.links.new(add.outputs[2], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    return bg


# ---------------- text ----------------
FONT = None


def font():
    global FONT
    if FONT is None:
        for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]:
            if os.path.exists(p):
                FONT = D.fonts.load(p)
                break
    return FONT


def text3d(body, size=0.5, extrude=0.06, m=None, loc=(0, 0, 0), rot=(math.radians(90), 0, 0), parent=None, align='CENTER'):
    cu = D.curves.new("T", 'FONT')
    cu.body = body
    f = font()
    if f:
        cu.font = f
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = extrude * 0.35
    cu.bevel_resolution = 2
    cu.align_x = align
    cu.align_y = 'CENTER'
    o = link(D.objects.new("T", cu))
    o.location = loc
    o.rotation_euler = rot
    if m:
        cu.materials.append(m)
    if parent:
        o.parent = parent
    return o


HUD_DEPTH = 6.0


def hud_text(cam, body, y, size, m, depth=None, extrude=0.05):
    """text fixed in front of camera; y and size given as if at depth 6"""
    d = HUD_DEPTH if depth is None else depth
    sc = d / 6.0
    k = cam.data.lens / 35.0
    o = text3d(body, size=size, extrude=extrude, m=m, loc=(0, y * sc, -6.0 * k * sc), rot=(0, 0, 0), parent=cam)
    o.scale = (sc,) * 3
    sh = text3d(body, size=size, extrude=0.0, m=shadow_mat(), loc=(0.035, -0.045, -0.06), rot=(0, 0, 0), parent=o)
    sh.data.bevel_depth = 0
    sh.data.offset = 0.025
    sh.visible_shadow = False
    o.visible_shadow = False
    return o


_SH = None


def shadow_mat():
    global _SH
    if _SH is None:
        _SH, mx, e = emis_fade("shadow", (0, 0, 0), 0.0)
        mx.inputs[0].default_value = 0.65
    return _SH


def pop(o, f0, f1=None, scale=None, dur=8, out_dur=6):
    """scale-in pop at f0, scale-out at f1"""
    if scale is None:
        scale = o.scale[0]
    o.scale = (0.001,) * 3
    o.keyframe_insert("scale", frame=f0 - 1)
    o.scale = (scale * 1.12,) * 3
    o.keyframe_insert("scale", frame=f0 + int(dur * 0.7))
    o.scale = (scale,) * 3
    o.keyframe_insert("scale", frame=f0 + dur)
    if f1:
        o.keyframe_insert("scale", frame=f1)
        o.scale = (0.001,) * 3
        o.keyframe_insert("scale", frame=f1 + out_dur)


# ---------------- models ----------------
def skin_model(name, verts, edges, radii, m, subd=2):
    me = D.meshes.new(name)
    me.from_pydata(verts, edges, [])
    o = link(D.objects.new(name, me))
    mod = o.modifiers.new("Skin", 'SKIN')
    mod.use_smooth_shade = True
    for i, r in enumerate(radii):
        if isinstance(r, (int, float)):
            r = (r, r)
        me.skin_vertices[0].data[i].radius = r
    me.skin_vertices[0].data[0].use_root = True
    sd = o.modifiers.new("Sub", 'SUBSURF')
    sd.levels = subd
    sd.render_levels = subd
    if m:
        me.materials.append(m)
    return o


def chain(pts, start_index):
    return [(start_index + i, start_index + i + 1) for i in range(len(pts) - 1)]


def eyes(parent, pos, r, spread, m_white, m_black, look_dir=(1, 0, 0)):
    out = []
    for sgn in (1, -1):
        p = Vector(pos) + Vector((0, sgn * spread, 0))
        e = sphere("eye", r, loc=p, seg=24, rings=12, m=m_white)
        pu = sphere("pupil", r * 0.55, loc=p + Vector(look_dir).normalized() * r * 0.62 + Vector((0, sgn * r * 0.25, 0)), seg=16, rings=8, m=m_black)
        hl = sphere("hl", r * 0.16, loc=p + Vector(look_dir).normalized() * r * 0.9 + Vector((0, sgn * r * 0.4, r * 0.3)), seg=8, rings=6, m=emis("hl", (1, 1, 1), 3))
        for x in (e, pu, hl):
            x.parent = parent
            x.matrix_parent_inverse = parent.matrix_world.inverted()
        out += [e, pu, hl]
    return out


def sauropod(m, mw, mb, loc=(0, 0, 0), rotz=0.0, scale=1.0):
    """body + separate neck object (for animation). returns (root_empty, neck_obj)"""
    root = link(D.objects.new("sauro", None))
    body_pts = [(-6.5, 0, 2.2), (-5.0, 0, 2.5), (-3.4, 0, 2.9), (-1.6, 0, 3.2), (0.0, 0, 3.4), (1.5, 0, 3.4), (2.3, 0, 3.7)]
    body_r = [0.08, 0.22, 0.48, 1.05, 1.35, 1.15, 0.75]
    verts = list(body_pts)
    rad = list(body_r)
    edges = chain(body_pts, 0)
    for lx, base in ((-1.6, 3), (1.5, 5)):
        for sy in (0.8, -0.8):
            i0 = len(verts)
            verts += [(lx, sy * 0.9, 2.5), (lx + 0.05, sy, 1.3), (lx + 0.1, sy, 0.15)]
            rad += [0.5, 0.36, 0.42]
            edges += [(base, i0), (i0, i0 + 1), (i0 + 1, i0 + 2)]
    body = skin_model("sauro_body", verts, edges, rad, m)
    body.parent = root
    # neck, pivot at shoulder
    piv = Vector((2.0, 0, 3.6))
    npts = [(2.0, 0, 3.6), (2.9, 0, 4.7), (3.5, 0, 6.0), (3.9, 0, 7.1), (4.4, 0, 7.5), (5.0, 0, 7.4)]
    nr = [0.85, 0.5, 0.38, 0.32, 0.42, 0.3]
    npts = [tuple(Vector(p) - piv) for p in npts]
    neck = skin_model("sauro_neck", npts, chain(npts, 0), nr, m)
    neck.location = piv
    neck.parent = root
    eyes(neck, Vector((4.55, 0, 7.72)) - piv, 0.15, 0.28, mw, mb)
    root.location = loc
    root.rotation_euler = (0, 0, rotz)
    root.scale = (scale,) * 3
    return root, neck


def trex(m, mw, mb, mteeth=None, loc=(0, 0, 0), rotz=0.0, scale=1.0):
    root = link(D.objects.new("trex", None))
    sp = [(-4.6, 0, 2.3), (-3.0, 0, 2.7), (-1.3, 0, 3.1), (0.3, 0, 3.4), (1.3, 0, 4.0), (1.9, 0, 4.5), (2.9, 0, 4.4)]
    sr = [0.07, 0.32, 0.82, 0.9, 0.55, (0.72, 0.62), (0.48, 0.42)]
    verts = list(sp)
    rad = list(sr)
    edges = chain(sp, 0)
    for sy in (0.6, -0.6):
        i0 = len(verts)
        verts += [(-1.0, sy, 2.6), (-0.5, sy * 1.1, 1.4), (-1.0, sy * 1.1, 0.35), (-0.4, sy * 1.1, 0.12)]
        rad += [0.6, 0.32, 0.2, (0.22, 0.12)]
        edges += [(2, i0), (i0, i0 + 1), (i0 + 1, i0 + 2), (i0 + 2, i0 + 3)]
        i1 = len(verts)
        verts += [(0.9, sy * 0.8, 3.3), (1.3, sy * 0.95, 2.95)]
        rad += [0.14, 0.09]
        edges += [(3, i1), (i1, i1 + 1)]
    body = skin_model("trex_body", verts, edges, rad, m)
    body.parent = root
    eyes(root, (2.15, 0, 4.92), 0.17, 0.42, mw, mb)
    root.location = loc
    root.rotation_euler = (0, 0, rotz)
    root.scale = (scale,) * 3
    return root


def raptor(m, loc=(0, 0, 0), rotz=0.0, scale=1.0, mfeather=None):
    """small feathered theropod, bird-like"""
    root = link(D.objects.new("raptor", None))
    sp = [(-2.6, 0, 1.75), (-1.6, 0, 1.6), (-0.6, 0, 1.55), (0.3, 0, 1.65), (0.8, 0, 2.2), (1.05, 0, 2.75), (1.45, 0, 2.85), (1.9, 0, 2.78)]
    sr = [0.22, 0.2, 0.42, 0.45, 0.22, 0.26, 0.2, 0.08]
    verts = list(sp)
    rad = list(sr)
    edges = chain(sp, 0)
    for sy in (0.25, -0.25):
        i0 = len(verts)
        verts += [(-0.4, sy, 1.25), (-0.1, sy, 0.75), (-0.45, sy, 0.15), (-0.1, sy, 0.05)]
        rad += [0.28, 0.12, 0.08, (0.12, 0.05)]
        edges += [(2, i0), (i0, i0 + 1), (i0 + 1, i0 + 2), (i0 + 2, i0 + 3)]
        i1 = len(verts)
        verts += [(0.4, sy * 1.6, 1.5), (0.6, sy * 2.6, 1.15), (0.3, sy * 3.2, 0.95)]
        rad += [0.1, (0.08, 0.25), (0.05, 0.22)]
        edges += [(3, i1), (i1, i1 + 1), (i1 + 1, i1 + 2)]
    body = skin_model("raptor_body", verts, edges, rad, m)
    body.parent = root
    root.location = loc
    root.rotation_euler = (0, 0, rotz)
    root.scale = (scale,) * 3
    return root, body


def asteroid(r=1.0, loc=(0, 0, 0)):
    o = ico("asteroid", r, loc=loc, sub=5)
    tx = D.textures.new("rock", 'VORONOI')
    tx.noise_scale = 0.6
    d = o.modifiers.new("disp", 'DISPLACE')
    d.texture = tx
    d.strength = -0.25 * r
    tx2 = D.textures.new("rock2", 'CLOUDS')
    tx2.noise_scale = 0.35
    d2 = o.modifiers.new("disp2", 'DISPLACE')
    d2.texture = tx2
    d2.strength = 0.35 * r
    o.scale = (1.0, 0.82, 0.9)
    setmat(o, mat("rockm", (0.16, 0.13, 0.11), 0.9, noise_bump=0.6, noise_scale=12, color2=(0.30, 0.25, 0.2)))
    return o


def trail(parent, length, radius, color=(1.0, 0.45, 0.1), strength=12):
    """glowing cone trail pointing along -X of parent (place parent moving +X)"""
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius, radius2=0.0, depth=length, location=(0, 0, 0))
    o = bpy.context.object
    o.name = "trail"
    smooth(o)
    o.rotation_euler = (0, math.radians(90), 0)
    o.location = (-length / 2, 0, 0)
    m, mx, e = emis_fade("trailm", color, strength)
    # gradient along cone length: fade to tail
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -length / 2
    mr.inputs["From Max"].default_value = length / 2
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = 'POWER'
    pw.inputs[1].default_value = 2.5
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], pw.inputs[0])
    nt.links.new(pw.outputs[0], mx.inputs[0])
    setmat(o, m)
    o.parent = parent
    o.visible_shadow = False
    return o


def earth(r=3.0, loc=(0, 0, 0), clouds=False, atmo=False, cloud_mix=True, rim=2.5, texdir=DIR):
    """earth with equirect mapping by object coords: lon=atan2(y,x), lat=asin(z/r)"""
    root = link(D.objects.new("earth_root", None))
    root.location = loc
    root.rotation_mode = 'ZYX'
    o = sphere("earth", r, seg=128, rings=64)
    o.parent = root
    m = D.materials.new("earthm")
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]

    def eq_uv():
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nrm = nt.nodes.new("ShaderNodeVectorMath")
        nrm.operation = 'NORMALIZE'
        nt.links.new(tc.outputs["Object"], nrm.inputs[0])
        nt.links.new(nrm.outputs[0], sep.inputs[0])
        at = nt.nodes.new("ShaderNodeMath"); at.operation = 'ARCTAN2'
        nt.links.new(sep.outputs["Y"], at.inputs[0]); nt.links.new(sep.outputs["X"], at.inputs[1])
        u = nt.nodes.new("ShaderNodeMath"); u.operation = 'MULTIPLY_ADD'
        u.inputs[1].default_value = 1 / (2 * math.pi); u.inputs[2].default_value = 0.5
        nt.links.new(at.outputs[0], u.inputs[0])
        asn = nt.nodes.new("ShaderNodeMath"); asn.operation = 'ARCSINE'
        nt.links.new(sep.outputs["Z"], asn.inputs[0])
        v = nt.nodes.new("ShaderNodeMath"); v.operation = 'MULTIPLY_ADD'
        v.inputs[1].default_value = 1 / math.pi; v.inputs[2].default_value = 0.5
        nt.links.new(asn.outputs[0], v.inputs[0])
        cmb = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(u.outputs[0], cmb.inputs[0]); nt.links.new(v.outputs[0], cmb.inputs[1])
        return cmb

    uv = eq_uv()
    img = nt.nodes.new("ShaderNodeTexImage")
    img.image = D.images.load(f"{texdir}/earth.png")
    img.interpolation = 'Cubic'
    img.extension = 'EXTEND'
    nt.links.new(uv.outputs[0], img.inputs["Vector"])
    land = nt.nodes.new("ShaderNodeTexImage")
    land.image = D.images.load(f"{texdir}/land.png")
    land.image.colorspace_settings.name = 'Non-Color'
    nt.links.new(uv.outputs[0], land.inputs["Vector"])
    nt.links.new(img.outputs["Color"], p.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs["To Min"].default_value = 0.5
    rr.inputs["To Max"].default_value = 0.9
    nt.links.new(land.outputs["Color"], rr.inputs["Value"])
    nt.links.new(rr.outputs["Result"], p.inputs["Roughness"])
    if cloud_mix:
        ci = nt.nodes.new("ShaderNodeTexImage")
        ci.image = D.images.load(f"{texdir}/clouds.png")
        ci.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(uv.outputs[0], ci.inputs["Vector"])
        cmul = nt.nodes.new("ShaderNodeMath"); cmul.operation = 'MULTIPLY'; cmul.inputs[1].default_value = 1.0
        cmul.name = "cloudamt"
        nt.links.new(ci.outputs["Color"], cmul.inputs[0])
        mxc = nt.nodes.new("ShaderNodeMix"); mxc.data_type = 'RGBA'
        nt.links.new(cmul.outputs[0], mxc.inputs[0])
        nt.links.new(img.outputs["Color"], mxc.inputs[6])
        mxc.inputs[7].default_value = (0.95, 0.96, 1.0, 1)
        nt.links.new(mxc.outputs[2], p.inputs["Base Color"])
        mxr = nt.nodes.new("ShaderNodeMath"); mxr.operation = 'MAXIMUM'
        nt.links.new(rr.outputs["Result"], mxr.inputs[0]); nt.links.new(cmul.outputs[0], mxr.inputs[1])
        nt.links.new(mxr.outputs[0], p.inputs["Roughness"])
    if rim > 0:
        lw = nt.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.4
        pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0
        nt.links.new(lw.outputs["Facing"], pw.inputs[0])
        p.inputs["Emission Color"].default_value = (0.3, 0.6, 1.0, 1)
        ml = nt.nodes.new("ShaderNodeMath"); ml.operation = 'MULTIPLY'; ml.inputs[1].default_value = rim
        nt.links.new(pw.outputs[0], ml.inputs[0])
        nt.links.new(ml.outputs[0], p.inputs["Emission Strength"])
    setmat(o, m)
    cl = None
    if clouds:
        cl = sphere("clouds", r * 1.012, seg=96, rings=48)
        cl.parent = root
        cm = D.materials.new("cloudm")
        cm.use_nodes = True
        cnt = cm.node_tree
        for n in list(cnt.nodes):
            cnt.nodes.remove(n)
        out = cnt.nodes.new("ShaderNodeOutputMaterial")
        dif = cnt.nodes.new("ShaderNodeBsdfDiffuse")
        dif.inputs["Color"].default_value = (1, 1, 1, 1)
        tr = cnt.nodes.new("ShaderNodeBsdfTransparent")
        mx = cnt.nodes.new("ShaderNodeMixShader")
        nt_backup = nt
        nt = cnt
        uv2 = eq_uv()
        ci = cnt.nodes.new("ShaderNodeTexImage")
        ci.image = D.images.load(f"{DIR}/clouds.png")
        ci.image.colorspace_settings.name = 'Non-Color'
        cnt.links.new(uv2.outputs[0], ci.inputs["Vector"])
        cnt.links.new(ci.outputs["Color"], mx.inputs[0])
        cnt.links.new(tr.outputs[0], mx.inputs[1])
        cnt.links.new(dif.outputs[0], mx.inputs[2])
        cnt.links.new(mx.outputs[0], out.inputs[0])
        nt = nt_backup
        setmat(cl, cm)
        cl.visible_shadow = False
    at = None
    if atmo:
        at = sphere("atmo", r * 1.04, seg=96, rings=48)
        at.parent = root
        am = D.materials.new("atmom")
        am.use_nodes = True
        ant = am.node_tree
        for n in list(ant.nodes):
            ant.nodes.remove(n)
        out = ant.nodes.new("ShaderNodeOutputMaterial")
        lw = ant.nodes.new("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.35
        pw = ant.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.0
        em = ant.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (0.25, 0.55, 1.0, 1)
        em.inputs["Strength"].default_value = 2.2
        tr = ant.nodes.new("ShaderNodeBsdfTransparent")
        mx = ant.nodes.new("ShaderNodeMixShader")
        ant.links.new(lw.outputs["Facing"], pw.inputs[0])
        ant.links.new(pw.outputs[0], mx.inputs[0])
        ant.links.new(tr.outputs[0], mx.inputs[1])
        ant.links.new(em.outputs[0], mx.inputs[2])
        ant.links.new(mx.outputs[0], out.inputs[0])
        setmat(at, am)
        at.visible_shadow = False
    return root, o, cl, at


def latlon(lat, lon, r):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))) * r


def landscape(size=120, seed=1, gcolor=(0.16, 0.36, 0.10), gcolor2=(0.32, 0.42, 0.14)):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=160, y_subdivisions=160, size=size)
    g = bpy.context.object
    g.name = "ground"
    tx = D.textures.new("hills", 'CLOUDS')
    tx.noise_scale = 1.4
    d = g.modifiers.new("disp", 'DISPLACE')
    d.texture = tx
    d.strength = 1.6
    d.texture_coords = 'GLOBAL'
    smooth(g)
    gm = mat("groundm", gcolor, 0.95, noise_bump=0.3, noise_scale=0.25, color2=gcolor2)
    setmat(g, gm)
    return g, gm


def conifer(loc, h=6, m_trunk=None, m_leaf=None, coll=None):
    objs = []
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.15 * h / 6, depth=h * 0.4, location=(loc[0], loc[1], loc[2] + h * 0.2))
    t = bpy.context.object
    setmat(t, m_trunk)
    objs.append(t)
    for i in range(3):
        z = loc[2] + h * (0.3 + 0.2 * i)
        bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=h * (0.28 - 0.06 * i), depth=h * 0.38, location=(loc[0], loc[1], z + h * 0.15))
        c = bpy.context.object
        smooth(c)
        setmat(c, m_leaf)
        objs.append(c)
    return objs


def ground_z(x, y, g):
    """raycast ground height"""
    deps = bpy.context.evaluated_depsgraph_get()
    ge = g.evaluated_get(deps)
    mw = g.matrix_world
    inv = mw.inverted()
    o = inv @ Vector((x, y, 50))
    d = (inv.to_3x3() @ Vector((0, 0, -1))).normalized()
    ok, loc, nrm, idx = ge.ray_cast(o, d)
    if ok:
        return (mw @ loc).z
    return 0.0


def render_scene(name, frames_dir=None):
    s = bpy.context.scene
    fd = frames_dir or f"/home/claude/v/frames/{name}"
    os.makedirs(fd, exist_ok=True)
    s.render.filepath = fd + "/f"
    s.render.use_overwrite = False
    s.render.use_placeholder = True
    bpy.ops.render.render(animation=True)


def preview(name, frames):
    s = bpy.context.scene
    os.makedirs("/home/claude/v/prev", exist_ok=True)
    for f in frames:
        s.frame_set(f)
        s.render.filepath = f"/home/claude/v/prev/{name}_{f:04d}.png"
        bpy.ops.render.render(write_still=True)


def run(name, preview_frames):
    mode = sys.argv[-1] if len(sys.argv) > 1 else "prev"
    if mode == "full":
        render_scene(name)
    else:
        preview(name, preview_frames)


def fcurves(obj):
    ad = obj.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    try:
        out = []
        for ly in act.layers:
            for st in ly.strips:
                for cb in st.channelbags:
                    out += list(cb.fcurves)
        if out:
            return out
    except Exception:
        pass
    try:
        return list(act.fcurves)
    except Exception:
        return []


def linear(obj, path=None):
    for fc in fcurves(obj):
        if path and fc.data_path != path:
            continue
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'


def shake(obj, f0, f1, strength=0.15, scale=2.0):
    for fc in fcurves(obj):
        if fc.data_path == "location":
            m = fc.modifiers.new('NOISE')
            m.strength = strength
            m.scale = scale
            m.use_restricted_range = True
            m.frame_start = f0
            m.frame_end = f1
            m.blend_in = 2
            m.blend_out = (f1 - f0) * 0.7


def txt_mats():
    mw = mat("txt", (1, 1, 1), 0.4, emit=(1, 1, 1), estr=0.55)
    mo = mat("txto", (1, 0.35, 0.03), 0.4, emit=(1, 0.32, 0.02), estr=0.9)
    return mw, mo
