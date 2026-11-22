"""ep003 (Parte 2 da extincao): os mundos 3D.
Uso:
    import sys; sys.path.insert(0, "/home/claude/ep003"); import mundos as M
    cz = M.mundo_cinzas()          # fim do Cretaceo: T. rex rugindo em close
    qt = M.mundo_quintal()         # quintal brasileiro de manha: galinha na mesma pose (match cut)
    M.pipo_foge(qt, f0=60)         # Pipo espiga vira alvo da galinha e foge pulando
    cp = M.mundo_comparacao()      # silhuetas lado a lado com as furculas acesas
Cada mundo zera a cena, monta tudo (luz, ceu, chao, props, animacao) e devolve um dict com os objetos-chave.
Match cut: M.frame_head(cam, d["head_pose"]) enquadra qualquer cabeca do mesmo jeito (mesmo offset local,
mesma lente), porque as duas cabecas foram modeladas no mesmo espaco normalizado (comprimento 1,4, focinho em -Y).
"""
import bpy, bmesh, math, random, os
from mathutils import Vector, Euler, Matrix

D = bpy.data
W, H, FPS = 540, 960, 30
N = 300
KIT = os.environ.get("PIPO_KIT", "/home/claude/pipo-canal/kit")
WORK = os.environ.get("PIPO_WORK", "/home/claude/ep003")

# pose de cabeca compartilhada (rugido / cacarejo): focinho em -Y local, levantado e virado 3/4
HEAD_EUL = (math.radians(-12), math.radians(4), math.radians(-24))
CAM_OFF = Vector((2.35, -2.75, -0.55))      # camera no espaco local da cabeca (frente, abaixo, levemente a direita)
CAM_TGT = Vector((-0.1, -0.7, -0.22))       # mira no meio da boca
CAM_LENS = 26
CAM_SHIFT_Y = -0.11                       # sobe o foco para fora da faixa de legenda (60-72%)
CU = 0.046                                 # 1 unidade da galinha = 4,6 cm (cabeca normalizada de 1,4 = 6,4 cm)


# =============================================================== base
def reset(samples=3):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = samples
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.1
    s.cycles.use_denoising = True
    try:
        s.cycles.denoiser = 'OPENIMAGEDENOISE'
        s.cycles.denoising_prefilter = 'FAST'
        s.cycles.denoising_input_passes = 'RGB'      # -0,4 s/quadro; o OIDN sem albedo segura bem a 4 amostras
    except Exception:
        pass
    s.cycles.max_bounces = 2
    s.cycles.diffuse_bounces = 1
    s.cycles.glossy_bounces = 0
    try:
        s.cycles.use_light_tree = False      # poucas luzes: a arvore de luzes so custa tempo (-1,5 s/quadro)
    except Exception:
        pass
    s.cycles.transmission_bounces = 0
    s.cycles.transparent_max_bounces = 8
    s.cycles.volume_bounces = 0
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.cycles.filter_width = 1.2
    s.render.use_persistent_data = True
    s.render.resolution_x, s.render.resolution_y = W, H
    s.render.resolution_percentage = 100
    s.render.fps = FPS
    s.frame_start, s.frame_end = 1, N
    s.view_settings.view_transform = 'Standard'      # mesmo pipeline de cor da pipo_lib (saturado)
    try:
        s.view_settings.look = 'Medium High Contrast'
    except Exception:
        pass
    s.render.image_settings.file_format = 'PNG'
    s.render.image_settings.color_mode = 'RGB'
    s.world = D.worlds.new("W")
    s.world.use_nodes = True
    return s


def bloom(s, threshold=1.0, size=0.6, strength=0.7):
    try:
        tree = D.node_groups.new("Comp", "CompositorNodeTree")
        s.compositing_node_group = tree
        tree.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
        rl = tree.nodes.new("CompositorNodeRLayers")
        g = tree.nodes.new("CompositorNodeGlare")
        out = tree.nodes.new("NodeGroupOutput")
        for name, val in (("Type", 'Bloom'), ("Quality", 'Medium'), ("Threshold", threshold), ("Size", size), ("Strength", strength)):
            if name in g.inputs:
                try:
                    g.inputs[name].default_value = val
                except Exception:
                    pass
        tree.links.new(rl.outputs["Image"], g.inputs["Image"])
        tree.links.new(g.outputs["Image"], out.inputs[0])
    except Exception as e:
        print("BLOOM FAIL", e)


def link(o):
    bpy.context.scene.collection.objects.link(o)
    return o


def smooth(o):
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def setmat(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


def empty(name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = link(D.objects.new(name, None))
    o.location = loc
    o.rotation_euler = rot
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
    if not ad or not ad.action:
        return []
    act = ad.action
    out = []
    try:
        for ly in act.layers:
            for st in ly.strips:
                for cb in st.channelbags:
                    out += list(cb.fcurves)
    except Exception:
        pass
    if not out:
        try:
            out = list(act.fcurves)
        except Exception:
            pass
    return out


def cyc(obj, linear=False):
    for fc in fcurves(obj):
        fc.modifiers.new('CYCLES')
        if linear:
            for k in fc.keyframe_points:
                k.interpolation = 'LINEAR'


def look(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()


def camera(loc, target, lens=35, shift_y=0.0):
    c = D.cameras.new("Cam")
    c.lens = lens
    c.clip_start = 0.01
    c.clip_end = 3000
    c.shift_y = shift_y
    o = link(D.objects.new("Cam", c))
    o.location = loc
    look(o, target)
    bpy.context.scene.camera = o
    return o


def frame_head(cam, head_pose, off=CAM_OFF, tgt=CAM_TGT, lens=CAM_LENS, shift=CAM_SHIFT_Y):
    """enquadra a cabeca: mesmo offset local => mesmo enquadramento em qualquer escala (match cut)"""
    bpy.context.view_layer.update()
    mw = head_pose.matrix_world
    cam.location = mw @ off
    look(cam, mw @ tgt)
    cam.data.lens = lens
    cam.data.shift_y = shift
    return cam


def dof(cam, focus_obj, fstop):
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = focus_obj
    cam.data.dof.aperture_fstop = fstop


def light(kind, loc, tgt, energy, col=(1, 1, 1), size=1.0, angle=2.0, spot=60):
    l = D.lights.new(kind, kind)
    l.energy = energy
    l.color = col
    if kind == 'AREA':
        l.size = size
    if kind == 'SUN':
        l.angle = math.radians(angle)
    if kind == 'POINT':
        l.shadow_soft_size = size
    if kind == 'SPOT':
        l.spot_size = math.radians(spot); l.spot_blend = 0.6; l.shadow_soft_size = size
    o = link(D.objects.new(kind, l))
    o.location = loc
    if tgt is not None:
        look(o, tgt)
    return o


# =============================================================== materiais
def _clear(nt):
    for n in list(nt.nodes):
        nt.nodes.remove(n)


def pbr(name, c1, c2=None, c3=None, rough=0.6, nscale=4.0, vor_bump=0.0, vor_scale=20.0, nbump=0.0, nbscale=30.0,
        metal=0.0, coord="Object", emit=None, estr=0.0, spec=0.5, ash=None, ash_amt=0.0, coat=0.0):
    """material com variacao de cor (ruido em 2-3 tons), bump de escamas/pedras (voronoi) e de rugas (ruido fino),
    e opcional camada de cinza assentada nas faces viradas para cima (ash)."""
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    try:
        p.inputs["Specular IOR Level"].default_value = spec
        p.inputs["Coat Weight"].default_value = coat
    except Exception:
        pass
    tc = nt.nodes.new("ShaderNodeTexCoord")
    co = tc.outputs[coord]
    col_out = None
    if c2 is None:
        p.inputs["Base Color"].default_value = (*c1, 1)
    else:
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = nscale; nz.inputs["Detail"].default_value = 5
        nz.inputs["Roughness"].default_value = 0.6
        nt.links.new(co, nz.inputs["Vector"])
        rp = nt.nodes.new("ShaderNodeValToRGB")
        rp.color_ramp.elements[0].position = 0.35; rp.color_ramp.elements[0].color = (*c1, 1)
        rp.color_ramp.elements[1].position = 0.65; rp.color_ramp.elements[1].color = (*c2, 1)
        if c3:
            e = rp.color_ramp.elements.new(0.8); e.color = (*c3, 1)
        nt.links.new(nz.outputs["Fac"], rp.inputs["Fac"])
        col_out = rp.outputs["Color"]
    hgt = None
    if vor_bump > 0:
        vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = vor_scale
        nt.links.new(co, vo.inputs["Vector"])
        vb = nt.nodes.new("ShaderNodeBump"); vb.inputs["Strength"].default_value = vor_bump; vb.inputs["Distance"].default_value = 0.05
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Max"].default_value = 0.6
        nt.links.new(vo.outputs["Distance"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], vb.inputs["Height"])
        hgt = vb
        if col_out is not None:   # escurece as frestas entre escamas
            dk = nt.nodes.new("ShaderNodeMix"); dk.data_type = 'RGBA'; dk.blend_type = 'MULTIPLY'
            inv = nt.nodes.new("ShaderNodeMapRange"); inv.inputs["From Min"].default_value = 0.0; inv.inputs["From Max"].default_value = 0.25
            inv.inputs["To Min"].default_value = 0.55; inv.inputs["To Max"].default_value = 0.0
            nt.links.new(vo.outputs["Distance"], inv.inputs["Value"])
            nt.links.new(inv.outputs["Result"], dk.inputs[0])
            nt.links.new(col_out, dk.inputs[6]); dk.inputs[7].default_value = (0.25, 0.2, 0.18, 1)
            col_out = dk.outputs[2]
    if nbump > 0:
        n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = nbscale; n2.inputs["Detail"].default_value = 6
        nt.links.new(co, n2.inputs["Vector"])
        nb = nt.nodes.new("ShaderNodeBump"); nb.inputs["Strength"].default_value = nbump; nb.inputs["Distance"].default_value = 0.03
        nt.links.new(n2.outputs["Fac"], nb.inputs["Height"])
        if hgt is not None:
            nt.links.new(hgt.outputs["Normal"], nb.inputs["Normal"])
        hgt = nb
    if hgt is not None:
        nt.links.new(hgt.outputs["Normal"], p.inputs["Normal"])
    if ash and col_out is not None:
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Normal"], sp.inputs[0])
        n3 = nt.nodes.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = 9
        nt.links.new(co, n3.inputs["Vector"])
        ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'MULTIPLY_ADD'; ad.inputs[1].default_value = 0.6
        nt.links.new(n3.outputs["Fac"], ad.inputs[0]); nt.links.new(sp.outputs["Z"], ad.inputs[2])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 1.0 - ash_amt + 0.3; mr.inputs["From Max"].default_value = 1.25 - ash_amt + 0.3
        nt.links.new(ad.outputs[0], mr.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        nt.links.new(mr.outputs["Result"], mx.inputs[0]); nt.links.new(col_out, mx.inputs[6]); mx.inputs[7].default_value = (*ash, 1)
        col_out = mx.outputs[2]
    if col_out is not None:
        nt.links.new(col_out, p.inputs["Base Color"])
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = estr
    return m


def emis(name, col, strength, alpha=None):
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; _clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*col, 1); e.inputs["Strength"].default_value = strength
    if alpha is None:
        nt.links.new(e.outputs[0], out.inputs[0])
    else:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def halo_mat(name, col, strength, power=2.5):
    """disco emissivo com borda que some (brilho/halo barato, sem volume)"""
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; _clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'
    nt.links.new(tc.outputs["Object"], ln.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Max"].default_value = 1.0; mr.inputs["To Min"].default_value = 1; mr.inputs["To Max"].default_value = 0
    nt.links.new(ln.outputs["Value"], mr.inputs["Value"])
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = power
    nt.links.new(mr.outputs["Result"], pw.inputs[0])
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*col, 1); e.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(pw.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def world_sky(s, stops, strength=1.0, sun_dir=None, sun_col=(1, 0.8, 0.5), sun_size=0.03, sun_str=6.0):
    """ceu em degrade vertical com varias paradas [(pos, cor)] + disco/halo do sol opcional"""
    nt = s.world.node_tree
    bg = nt.nodes["Background"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nrm = nt.nodes.new("ShaderNodeVectorMath"); nrm.operation = 'NORMALIZE'
    nt.links.new(tc.outputs["Generated"], nrm.inputs[0])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nrm.outputs[0], sp.inputs[0])
    rp = nt.nodes.new("ShaderNodeValToRGB")
    for i, (pos, c) in enumerate(stops):
        e = rp.color_ramp.elements[i] if i < 2 else rp.color_ramp.elements.new(pos)
        e.position = pos; e.color = (*c, 1)
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.2; mr.inputs["From Max"].default_value = 1.0
    nt.links.new(sp.outputs["Z"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], rp.inputs["Fac"])
    col = rp.outputs["Color"]
    if sun_dir is not None:
        dv = Vector(sun_dir).normalized()
        dp = nt.nodes.new("ShaderNodeVectorMath"); dp.operation = 'DOT_PRODUCT'; dp.inputs[1].default_value = dv
        nt.links.new(nrm.outputs[0], dp.inputs[0])
        # halo largo + disco
        h1 = nt.nodes.new("ShaderNodeMapRange"); h1.inputs["From Min"].default_value = 0.75; h1.inputs["From Max"].default_value = 1.0
        nt.links.new(dp.outputs["Value"], h1.inputs["Value"])
        pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 4
        nt.links.new(h1.outputs["Result"], pw.inputs[0])
        d1 = nt.nodes.new("ShaderNodeMapRange"); d1.inputs["From Min"].default_value = 1 - sun_size * 0.012 - 0.0004; d1.inputs["From Max"].default_value = 1 - sun_size * 0.012
        nt.links.new(dp.outputs["Value"], d1.inputs["Value"])
        ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'MULTIPLY_ADD'; ad.inputs[1].default_value = sun_str
        nt.links.new(d1.outputs["Result"], ad.inputs[0]); nt.links.new(pw.outputs[0], ad.inputs[2])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'ADD'; mx.clamp_factor = False
        nt.links.new(ad.outputs[0], mx.inputs[0]); nt.links.new(col, mx.inputs[6]); mx.inputs[7].default_value = (*sun_col, 1)
        col = mx.outputs[2]
    nt.links.new(col, bg.inputs["Color"])
    bg.inputs["Strength"].default_value = strength
    return bg


# =============================================================== geometria
def metaball_mesh(name, elems, res=0.05, thr=0.6):
    """elems: (co, r) ou (co, r, (sx,sy,sz)) -> malha organica"""
    mb = D.metaballs.new(name)
    mb.resolution = res; mb.render_resolution = res; mb.threshold = thr
    for el in elems:
        e = mb.elements.new()
        e.co = el[0]; e.radius = el[1]
        if len(el) > 2:
            e.type = 'ELLIPSOID'; e.size_x, e.size_y, e.size_z = el[2]
    o = link(D.objects.new(name, mb))
    for ob in bpy.context.selected_objects:
        ob.select_set(False)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.convert(target='MESH')
    o = bpy.context.object
    o.name = name
    return smooth(o)


def skin_model(name, verts, edges, radii, m, subd=2):
    me = D.meshes.new(name)
    me.from_pydata(verts, edges, [])
    o = link(D.objects.new(name, me))
    mod = o.modifiers.new("Skin", 'SKIN'); mod.use_smooth_shade = True
    for i, r in enumerate(radii):
        if isinstance(r, (int, float)):
            r = (r, r)
        me.skin_vertices[0].data[i].radius = r
    me.skin_vertices[0].data[0].use_root = True
    sd = o.modifiers.new("Sub", 'SUBSURF'); sd.levels = 1; sd.render_levels = subd
    if m:
        me.materials.append(m)
    return o


def chain(n, start=0):
    return [(start + i, start + i + 1) for i in range(n - 1)]


def sph(name, r, loc=(0, 0, 0), m=None, seg=24, rings=12, scale=None, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=r, location=loc)
    o = bpy.context.object; o.name = name; smooth(o)
    if scale:
        o.scale = scale
    if m:
        setmat(o, m)
    if parent:
        o.parent = parent
    return o


def cone(name, r1, r2, depth, loc, rot, m, parent=None, verts=10):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; smooth(o); setmat(o, m)
    if parent:
        o.parent = parent
    return o


def box(name, size, loc, m, bev=0.02, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bev:
        b = o.modifiers.new("bv", 'BEVEL'); b.width = bev; b.segments = 2
    setmat(o, m)
    if parent:
        o.parent = parent
    return o


def cyl(name, r, depth, loc, m, rot=(0, 0, 0), verts=16, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; smooth(o); setmat(o, m)
    if parent:
        o.parent = parent
    return o


def tube(name, pts, radius, m, res=3, taper=None):
    cu = D.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    cu.bevel_depth = radius; cu.bevel_resolution = res; cu.use_fill_caps = True
    sp = cu.splines.new('POLY' if len(pts) < 3 else 'NURBS')
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    if sp.type == 'NURBS':
        sp.use_endpoint_u = True; sp.order_u = 3
    o = link(D.objects.new(name, cu))
    cu.materials.append(m)
    return o


def ground_plane(size, m, sub=120, strength=0.4, nscale=0.8, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=sub, y_subdivisions=sub, size=size, location=loc)
    g = bpy.context.object; g.name = "chao"
    tx = D.textures.new("chaoT", 'CLOUDS'); tx.noise_scale = nscale
    d = g.modifiers.new("disp", 'DISPLACE'); d.texture = tx; d.strength = strength; d.texture_coords = 'GLOBAL'
    smooth(g); setmat(g, m)
    return g


def ground_z(g, x, y):
    deps = bpy.context.evaluated_depsgraph_get()
    ge = g.evaluated_get(deps)
    mw = g.matrix_world; inv = mw.inverted()
    ok, loc, nrm, idx = ge.ray_cast(inv @ Vector((x, y, 60)), (inv.to_3x3() @ Vector((0, 0, -1))).normalized())
    return (mw @ loc).z if ok else 0.0


# =============================================================== T. REX
def trex_head(parent, m_skin, m_mouth, m_teeth, m_eye, m_tongue):
    """cabeca no espaco normalizado: raiz na nuca, focinho em -Y (comprimento ~1,4). devolve (jaw_pivot, objetos)"""
    sk = [((0, 0.02, 0.07), 0.56, (1.18, 0.75, 0.9)),        # cranio largo atras dos olhos (T. rex tem nuca larga)
          ((0, -0.36, 0.03), 0.5, (0.95, 1.0, 0.85)),
          ((0, -0.72, -0.02), 0.42, (0.7, 1.0, 0.86)),
          ((0, -0.98, -0.06), 0.34, (0.64, 1.0, 0.86)),
          ((0, -1.12, -0.1), 0.22, (0.66, 1.0, 0.9)),
          ((0.3, -0.42, 0.22), 0.13, (0.8, 1.9, 0.6)), ((-0.3, -0.42, 0.22), 0.13, (0.8, 1.9, 0.6)),   # cristas sobre os olhos (cara de bravo)
          ((0.24, -0.2, 0.3), 0.11), ((-0.24, -0.2, 0.3), 0.11),
          ((0, -0.78, 0.2), 0.13, (1, 1.8, 1)),                          # crista nasal rugosa
          ((0.38, -0.02, -0.12), 0.27), ((-0.38, -0.02, -0.12), 0.27)]    # bochechas / musculo da mandibula
    skull = metaball_mesh("rex_cranio", sk, res=0.045)
    setmat(skull, m_skin); skull.parent = parent
    # corta o "fundo" do cranio no plano do maxilar para abrir a boca (borda reta da gengiva)
    bm = bmesh.new(); bm.from_mesh(skull.data)
    for v in bm.verts:
        lim = -0.2 - 0.04 * max(0.0, -v.co.y)
        if v.co.z < lim and v.co.y < 0.15:
            v.co.z = lim + (v.co.z - lim) * 0.15
    bm.to_mesh(skull.data); bm.free()
    pal = sph("rex_palato", 1, (0, -0.62, -0.22), m_mouth, scale=(0.27, 0.66, 0.06), parent=parent)
    thr = sph("rex_garganta", 0.3, (0, 0.05, -0.2), emis("garganta", (0.12, 0.008, 0.005), 0.6), parent=parent)
    # olhos fundos, amarelos, pupila em fenda
    out = [skull, pal, thr]
    pup = pbr("rex_pupila", (0.0, 0.0, 0.0), rough=0.1)
    for sx in (1, -1):
        e = sph("rex_olho", 0.062, (sx * 0.35, -0.44, 0.12), m_eye, parent=parent)
        p = sph("rex_fenda", 0.04, (sx * 0.39, -0.47, 0.12), pup, scale=(0.3, 0.55, 1.3), parent=parent)
        lid = sph("rex_palpebra", 0.09, (sx * 0.34, -0.43, 0.17), m_skin, scale=(1.0, 1.4, 0.45), parent=parent)
        lid.rotation_euler = (math.radians(-10), sx * math.radians(18), 0)
        n = sph("rex_narina", 0.045, (sx * 0.12, -1.14, 0.06), m_mouth, scale=(0.8, 1.4, 0.6), parent=parent)
        out += [e, p, lid, n]
    # dentes de cima (banana) ao longo da gengiva
    random.seed(7)
    for sx in (1, -1):
        for i in range(10):
            t = i / 9
            y = -0.14 - 0.96 * t
            x = sx * (0.37 - 0.17 * t)
            ln = 0.15 + 0.12 * math.sin(math.pi * min(1, t * 1.25)) + random.uniform(-0.04, 0.03)
            z = -0.21 - 0.04 * (-y)
            c = cone("rex_dente", 0.05 + 0.012 * (1 - t), 0.006, ln, (x, y, z - ln / 2 + 0.03), (math.radians(10 + random.uniform(-6, 6)), sx * math.radians(-8), 0), m_teeth, parent=parent, verts=10)
            out.append(c)
    for i in range(4):   # pre-maxilares na ponta
        a = (i - 1.5) * 0.18
        c = cone("rex_dente", 0.03, 0.004, 0.11, (math.sin(a) * 0.17, -1.17 + abs(a) * 0.1, -0.31), (math.radians(6), 0, 0), m_teeth, parent=parent, verts=8)
        out.append(c)
    # mandibula
    out.append(empty("ref_olho", (0.35, -0.44, 0.12), parent)); out.append(empty("ref_ponta", (0, -1.2, -0.12), parent))
    jaw = empty("rex_jaw", (0, 0.06, -0.2), parent)
    je = []
    for sx in (1, -1):
        for k in range(7):
            t = k / 6
            je.append(((sx * (0.34 - 0.13 * t), -1.02 * t, -0.08 - 0.06 * t), 0.18 - 0.04 * t, (0.8, 1.2, 1.05)))
    je += [((0, -1.02, -0.12), 0.16, (1.4, 1, 1.1)), ((0, -0.5, -0.15), 0.26, (1.0, 1.9, 0.45)), ((0, 0.05, -0.2), 0.3, (1.2, 0.8, 0.8))]
    jm = metaball_mesh("rex_mandibula", je, res=0.04)
    setmat(jm, m_skin); jm.parent = jaw
    tg = sph("rex_lingua", 1, (0, -0.45, -0.06), m_tongue, scale=(0.16, 0.42, 0.05), parent=jaw)
    fl = sph("rex_assoalho", 1, (0, -0.55, -0.07), m_mouth, scale=(0.26, 0.62, 0.06), parent=jaw)
    out += [jm, tg, fl]
    for sx in (1, -1):
        for i in range(10):
            t = i / 9
            y = -0.15 - 0.85 * t
            x = sx * (0.31 - 0.12 * t)
            ln = 0.12 + 0.07 * math.sin(math.pi * t) + random.uniform(-0.02, 0.02)
            c = cone("rex_dente_inf", 0.042, 0.005, ln, (x, y, 0.0 + ln / 2 - 0.01), (math.radians(-8), 0, 0), m_teeth, parent=jaw, verts=8)
            out.append(c)
    return jaw, out


def trex(root_loc=(0, 0, 0), rotz=0.0, m_skin=None, ash=None):
    """T. rex inteiro (metros). Corpo com skin modifier, cabeca detalhada. devolve dict(root, head_pose, head_anim, jaw, objs)"""
    m_skin = m_skin or pbr("rex_pele", (0.035, 0.03, 0.022), (0.16, 0.07, 0.03), (0.3, 0.13, 0.04), rough=0.5, nscale=3.5,
                           vor_bump=0.9, vor_scale=26, nbump=0.6, nbscale=7, ash=ash, ash_amt=0.12 if ash else 0, spec=0.6)
    m_mouth = pbr("rex_boca", (0.32, 0.04, 0.04), (0.18, 0.02, 0.025), rough=0.25, nscale=8, nbump=0.3, nbscale=20, spec=0.8)
    m_tongue = pbr("rex_lingua", (0.45, 0.08, 0.07), (0.3, 0.04, 0.05), rough=0.3, nscale=10, nbump=0.4, nbscale=25)
    m_teeth = pbr("rex_dentes", (0.78, 0.68, 0.48), (0.55, 0.42, 0.25), rough=0.35, nscale=12, nbump=0.15, nbscale=40, spec=0.7)
    m_eye = pbr("rex_olho", (0.9, 0.35, 0.02), (1.0, 0.6, 0.05), rough=0.08, nscale=30, emit=(1.0, 0.4, 0.02), estr=0.8, spec=1.0)
    root = empty("trex", root_loc, rot=(0, 0, rotz))
    # cabeca baixa, investindo para a frente (-Y)
    hp = empty("rex_head_pose", (0, -1.55, 2.55), root, rot=HEAD_EUL)
    ha = empty("rex_head_anim", (0, 0, 0), hp)
    jaw, hobjs = trex_head(ha, m_skin, m_mouth, m_teeth, m_eye, m_tongue)
    # corpo: pescoco grosso -> torso -> cauda (+Y), pernas, bracinhos
    sp = [(0, -1.75, 2.55), (0, -1.2, 2.45), (0, -0.55, 2.55), (0, 0.4, 2.85), (0, 1.5, 3.15), (0, 2.6, 3.25), (0, 3.8, 3.15), (0, 5.2, 2.9), (0, 6.6, 2.65), (0, 8.0, 2.45), (0, 9.4, 2.3)]
    sr = [(0.42, 0.48), (0.55, 0.62), (0.75, 0.85), (0.95, 1.15), (1.05, 1.25), (0.95, 1.05), (0.7, 0.8), (0.5, 0.55), (0.32, 0.36), (0.18, 0.2), (0.05, 0.05)]
    verts = list(sp); rad = list(sr); edges = chain(len(sp))
    for sx in (1, -1):
        i0 = len(verts)
        verts += [(sx * 0.75, 2.7, 2.55), (sx * 0.85, 2.0, 1.45), (sx * 0.8, 2.7, 0.45), (sx * 0.82, 2.3, 0.12)]
        rad += [(0.62, 0.8), (0.38, 0.45), (0.2, 0.22), (0.26, 0.12)]
        edges += [(5, i0), (i0, i0 + 1), (i0 + 1, i0 + 2), (i0 + 2, i0 + 3)]
        i1 = len(verts)
        verts += [(sx * 0.6, 0.3, 2.3), (sx * 0.7, 0.05, 1.95), (sx * 0.62, -0.2, 1.85)]
        rad += [0.13, 0.09, 0.06]
        edges += [(3, i1), (i1, i1 + 1), (i1 + 1, i1 + 2)]
    body = skin_model("rex_corpo", verts, edges, rad, m_skin)
    body.parent = root
    # garras dos pes
    claws = []
    mcl = pbr("rex_garra", (0.08, 0.07, 0.06), rough=0.3)
    for sx in (1, -1):
        for k in (-1, 0, 1):
            c = cone("rex_garra", 0.07, 0.01, 0.35, (sx * 0.82 + k * 0.17, 1.9, 0.08), (math.radians(80), 0, k * 0.25), mcl, parent=root)
            claws.append(c)
    return dict(root=root, head_pose=hp, head_anim=ha, jaw=jaw, body=body, head_objs=hobjs, skin=m_skin)


def anim_roar(rex, f0=1, peak=22, hold=48, close=70, jaw_open=40, lunge=0.35):
    """rugido: puxa a cabeca para tras, investe para a lente com a boca escancarada, treme, fecha"""
    jaw, ha = rex["jaw"], rex["head_anim"]
    for fr, a in ((f0, 6), (f0 + 8, 2), (peak, jaw_open), (peak + 6, jaw_open - 4), (hold, jaw_open - 2), (close, 10), (close + 20, 6)):
        K(jaw, "rotation_euler", fr, (math.radians(a), 0, 0))
    for fr, loc, rx in ((f0, (0, 0.25, 0.05), -6), (f0 + 8, (0, 0.38, 0.1), -12), (peak, (0, -lunge, -0.05), 4),
                        (hold, (0, -lunge * 0.85, -0.03), 3), (close, (0, 0.0, 0.0), 0), (close + 20, (0, 0.05, 0), -2)):
        K(ha, "location", fr, loc); K(ha, "rotation_euler", fr, (math.radians(rx), 0, 0))
    for fc in fcurves(ha):
        if fc.data_path == "rotation_euler":
            mo = fc.modifiers.new('NOISE'); mo.strength = 0.05; mo.scale = 1.5; mo.use_restricted_range = True
            mo.frame_start = peak; mo.frame_end = hold + 4; mo.blend_in = 3; mo.blend_out = 6


# =============================================================== GALINHA
def feather_mesh(name, length=1.0, width=0.42, curl=0.12, cup=0.08, rows=7, cols=4, point=1.0):
    bm = bmesh.new(); vs = []
    for i in range(rows + 1):
        t = i / rows
        w = width * (math.sin(math.pi * min(1.0, 0.12 + t * 0.95)) ** 0.7) * (1 - 0.35 * t) * (1 - point * 0.6 * t ** 3)
        row = []
        for j in range(cols + 1):
            u = (j / cols - 0.5) * 2
            row.append(bm.verts.new((u * w * 0.5, t * length, -curl * t * t * length + cup * (1 - u * u) * w)))
        vs.append(row)
    for i in range(rows):
        for j in range(cols):
            bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    me = D.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def feather_mat(name, cols, tip=(0.05, 0.03, 0.02), rough=0.55, spec=0.5, barb=0.25, edge=None):
    """cor por pena (Object Info > Random) + ponta mais escura + ranhuras das barbas (bump)"""
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = rough
    try:
        p.inputs["Specular IOR Level"].default_value = spec
    except Exception:
        pass
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    rp = nt.nodes.new("ShaderNodeValToRGB")
    for i, c in enumerate(cols):
        e = rp.color_ramp.elements[i] if i < 2 else rp.color_ramp.elements.new(i / (len(cols) - 1))
        e.position = i / (len(cols) - 1); e.color = (*c, 1)
    nt.links.new(oi.outputs["Random"], rp.inputs["Fac"])
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sp.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.55; mr.inputs["From Max"].default_value = 1.0
    nt.links.new(sp.outputs["Y"], mr.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(mr.outputs["Result"], mx.inputs[0]); nt.links.new(rp.outputs["Color"], mx.inputs[6]); mx.inputs[7].default_value = (*tip, 1)
    col = mx.outputs[2]
    if edge:   # borda clara (pena de pescoco dourada)
        ax = nt.nodes.new("ShaderNodeMath"); ax.operation = 'ABSOLUTE'
        sub = nt.nodes.new("ShaderNodeMath"); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = 0.5
        nt.links.new(sp.outputs["X"], sub.inputs[0]); nt.links.new(sub.outputs[0], ax.inputs[0])
        me_ = nt.nodes.new("ShaderNodeMapRange"); me_.inputs["From Min"].default_value = 0.25; me_.inputs["From Max"].default_value = 0.48
        nt.links.new(ax.outputs[0], me_.inputs["Value"])
        mx2 = nt.nodes.new("ShaderNodeMix"); mx2.data_type = 'RGBA'
        nt.links.new(me_.outputs["Result"], mx2.inputs[0]); nt.links.new(col, mx2.inputs[6]); mx2.inputs[7].default_value = (*edge, 1)
        col = mx2.outputs[2]
    nt.links.new(col, p.inputs["Base Color"])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 18; wv.inputs["Distortion"].default_value = 1.5
    wv.bands_direction = 'DIAGONAL'
    nt.links.new(tc.outputs["Generated"], wv.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = barb
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    try:
        p.inputs["Sheen Weight"].default_value = 0.1
        p.inputs["Sheen Tint"].default_value = (1, 0.9, 0.7, 1)
    except Exception:
        pass
    return m


def _place_feather(me, m, parent, base, direction, normal, scale, lift=0.25, roll=0.0):
    o = link(D.objects.new("pena", me))
    if not o.data.materials:
        o.data.materials.append(m)
    y = Vector(direction).normalized()
    z = Vector(normal).normalized()
    z = (z - y * z.dot(y)).normalized()
    # levanta a ponta um pouco (penas em telhado)
    y = (y + z * lift).normalized()
    z = (z - y * z.dot(y)).normalized()
    x = y.cross(z)
    mt = Matrix((x, y, z)).transposed().to_4x4()
    if roll:
        mt = mt @ Matrix.Rotation(roll, 4, 'Y')
    mt.translation = Vector(base)
    o.parent = parent
    o.matrix_basis = mt @ Matrix.Diagonal((scale, scale, scale, 1))
    return o


def chicken_head(parent, m_head, m_comb, m_beak, m_eye, m_mouth):
    """mesma convencao da cabeca do T. rex: raiz na nuca, bico em -Y, comprimento ~1,4"""
    out = []
    hd = metaball_mesh("gal_cabeca", [((0, -0.38, 0.06), 0.5, (0.85, 1.0, 0.95)), ((0, -0.12, 0.0), 0.42, (0.85, 0.9, 1.05)),
                                       ((0, -0.68, -0.02), 0.3, (0.75, 0.9, 0.8))], res=0.04)
    setmat(hd, m_head); hd.parent = parent; out.append(hd)
    # pele vermelha nua ao redor do olho (marca de galinha) + brinco (lobulo)
    for sx in (1, -1):
        fc = sph("gal_face", 0.17, (sx * 0.24, -0.6, 0.02), m_comb, scale=(0.5, 1.0, 0.8), parent=parent)
        lb = sph("gal_brinco", 0.1, (sx * 0.27, -0.25, -0.18), m_comb, scale=(0.5, 0.8, 1.2), parent=parent)
        e = sph("gal_olho", 0.085, (sx * 0.3, -0.58, 0.1), m_eye, parent=parent)
        pu = sph("gal_pupila", 0.045, (sx * 0.365, -0.6, 0.1), pbr("gal_pup", (0, 0, 0), rough=0.05), scale=(0.6, 1, 1), parent=parent)
        hl = sph("gal_brilho", 0.014, (sx * 0.375, -0.64, 0.135), emis("hl", (1, 1, 1), 4), parent=parent, seg=8, rings=6)
        out += [fc, lb, e, pu, hl]
    # crista serrilhada (5 pontas) grande e vermelha
    prof = [(-0.78, 0.28)]
    for i in range(5):
        t = i / 4
        y0 = -0.74 + 0.78 * t
        h = 0.36 + 0.2 * math.sin(math.pi * (0.2 + 0.65 * t))
        prof += [(y0, 0.4 + h), (y0 + 0.1, 0.5 + h * 0.45)]
    prof += [(0.18, 0.34), (0.08, 0.22), (-0.6, 0.18)]
    bm = bmesh.new()
    vs = [bm.verts.new((0, y, z)) for y, z in prof]
    bm.faces.new(vs)
    me = D.meshes.new("gal_crista"); bm.to_mesh(me); bm.free()
    cm = link(D.objects.new("gal_crista", me))
    so = cm.modifiers.new("esp", 'SOLIDIFY'); so.thickness = 0.12; so.offset = 0
    sb = cm.modifiers.new("sub", 'SUBSURF'); sb.levels = 2; sb.render_levels = 3
    smooth(cm); setmat(cm, m_comb); cm.parent = parent; out.append(cm)
    # bico superior com ponta curva
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1)
    bk = bpy.context.object; bk.name = "gal_bico"
    for v in bk.data.vertices:
        fwd = max(0.0, -v.co.y)
        v.co.x *= 0.15 * (1 - 0.75 * fwd); v.co.z *= 0.13 * (1 - 0.6 * fwd)
        v.co.y *= 0.3
        v.co.z -= 0.12 * (fwd ** 2)
        if v.co.z < 0 and fwd > 0.0:
            v.co.z *= 0.4
    smooth(bk); setmat(bk, m_beak); bk.parent = parent; bk.location = (0, -0.86, -0.03); out.append(bk)
    jaw = empty("gal_jaw", (0, -0.72, -0.1), parent)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=1)
    lb_ = bpy.context.object; lb_.name = "gal_bico_inf"
    for v in lb_.data.vertices:
        fwd = max(0.0, -v.co.y)
        v.co.x *= 0.11 * (1 - 0.7 * fwd); v.co.z *= 0.06; v.co.y *= 0.24
    smooth(lb_); setmat(lb_, m_beak); lb_.parent = jaw; lb_.location = (0, -0.16, -0.01); out.append(lb_)
    ins = sph("gal_boca", 1, (0, -0.06, 0.0), m_mouth, scale=(0.07, 0.12, 0.02), parent=jaw)
    out += [empty("ref_olho", (0.3, -0.58, 0.1), parent), empty("ref_ponta", (0, -1.14, -0.12), parent)]
    # barbelas penduradas (presas na mandibula: balancam com o cacarejo)
    wt = metaball_mesh("gal_barbela", [((sx * 0.07, -0.12, -0.12), 0.16, (0.55, 0.8, 1.0)) for sx in (1, -1)] +
                       [((sx * 0.07, -0.12, -0.27), 0.17, (0.55, 0.75, 1.1)) for sx in (1, -1)], res=0.025, thr=0.45)
    setmat(wt, m_comb); wt.parent = jaw
    out += [ins, wt]
    return jaw, out


def galinha(root_loc=(0, 0, 0), rotz=0.0, scale=CU):
    """galinha caipira (unidade: CU). Corpo coberto de penas em camadas, cauda preta-esverdeada,
    pescoco dourado, crista vermelha, pernas amarelas escamosas."""
    random.seed(11)
    root = empty("galinha", root_loc, rot=(0, 0, rotz)); root.scale = (scale,) * 3
    bodyE = empty("gal_corpo_anim", (0, 0, 0), root)
    m_body = feather_mat("gal_pena", [(0.42, 0.13, 0.04), (0.55, 0.2, 0.05), (0.62, 0.26, 0.07), (0.36, 0.1, 0.03)], tip=(0.2, 0.06, 0.02))
    m_hack = feather_mat("gal_pescoco", [(0.8, 0.32, 0.03), (0.9, 0.45, 0.05), (0.7, 0.24, 0.03)], tip=(0.45, 0.12, 0.02), edge=(1.0, 0.62, 0.12))
    m_wing = feather_mat("gal_asa", [(0.3, 0.09, 0.03), (0.45, 0.15, 0.04), (0.2, 0.06, 0.02)], tip=(0.04, 0.02, 0.01))
    m_tail = feather_mat("gal_cauda", [(0.01, 0.025, 0.02), (0.02, 0.05, 0.035), (0.03, 0.02, 0.04)], tip=(0.0, 0.0, 0.0), rough=0.22, spec=1.0, barb=0.15)
    m_under = pbr("gal_base", (0.4, 0.13, 0.04), (0.5, 0.18, 0.05), rough=0.8, nscale=6, nbump=0.3, nbscale=14)
    m_head = pbr("gal_cab_pena", (0.78, 0.32, 0.04), (0.6, 0.22, 0.03), rough=0.7, nscale=10, nbump=0.35, nbscale=40)
    m_comb = pbr("gal_crista", (0.85, 0.03, 0.03), (0.62, 0.01, 0.02), (1.0, 0.12, 0.08), rough=0.35, nscale=7, nbump=0.3, nbscale=30, vor_bump=0.1, vor_scale=35, spec=0.6)
    m_beak = pbr("gal_bico", (0.95, 0.62, 0.12), (0.8, 0.45, 0.08), rough=0.3, nscale=8, nbump=0.1, nbscale=30, spec=0.8)
    m_eye = pbr("gal_olho", (0.95, 0.45, 0.04), (1.0, 0.62, 0.1), rough=0.05, nscale=30, spec=1.0, emit=(1, 0.5, 0.05), estr=0.25)
    m_mouth = pbr("gal_bocam", (0.12, 0.03, 0.03), rough=0.4)
    m_leg = pbr("gal_perna", (0.95, 0.68, 0.12), (0.8, 0.5, 0.08), rough=0.45, nscale=6, vor_bump=0.45, vor_scale=9, spec=0.6)
    C = Vector((0, 0.6, 6.3)); R = Vector((2.5, 3.9, 2.8))
    core = sph("gal_nucleo", 1, C, m_under, scale=tuple(R * 0.86), parent=bodyE)
    fme = feather_mesh("pena_corpo", 1.0, 0.6, 0.04)
    fme_h = feather_mesh("pena_pescoco", 1.0, 0.3, 0.02, point=1.0)
    fme_w = feather_mesh("pena_asa", 1.0, 0.36, 0.05)
    fme_t = feather_mesh("pena_cauda", 1.0, 0.22, 0.35, cup=0.03, rows=10)
    # corpo: anel por anel, do peito para tras
    for ti in range(11):
        th = 0.12 * math.pi + ti * (0.78 * math.pi / 10)
        nring = int(10 + 8 * math.sin(th))
        for vi in range(nring):
            v = vi / nring * 2 * math.pi + (ti % 2) * math.pi / nring + random.uniform(-0.08, 0.08)
            st, ct = math.sin(th), math.cos(th)
            pos = C + Vector((R.x * st * math.cos(v), -R.y * ct, R.z * st * math.sin(v)))
            if pos.z < 4.0 and abs(pos.x) < 1.4:
                continue
            nrm = Vector(((pos.x - C.x) / R.x ** 2, (pos.y - C.y) / R.y ** 2, (pos.z - C.z) / R.z ** 2))
            tan = Vector((R.x * ct * math.cos(v), R.y * st, R.z * ct * math.sin(v))).normalized()
            nn = nrm.normalized()
            dirv = tan + Vector((0, 0.35, -0.45))
            dirv = (dirv - nn * dirv.dot(nn)).normalized()      # sempre tangente: nada de pena espetada para dentro
            _place_feather(fme, m_body, bodyE, pos, dirv, nrm, random.uniform(1.5, 2.0) * (1.0 + 0.25 * (ti > 6)), lift=0.3)
    # asas fechadas dos lados
    for sx in (1, -1):
        for row in range(4):
            for k in range(7):
                yy = -0.8 + k * 0.75 + row * 0.35
                zz = 6.9 - row * 0.55 - k * 0.08
                xx = sx * (R.x * 0.98 + 0.12 + row * 0.03)
                sc = 1.6 + row * 0.55 + k * 0.08
                mm = m_wing if row < 3 else m_tail
                _place_feather(fme_w, mm, bodyE, (xx, yy, zz), (0, 1, -0.28 - row * 0.05), (sx, 0, 0.25), sc, lift=0.06)
    # cauda em leque (preta esverdeada, brilho metalico)
    for i in range(16):
        a = (i / 15 - 0.5) * 1.5
        base = Vector((math.sin(a) * 0.9, 4.0, 7.2))
        d = Vector((math.sin(a) * 0.8, 0.75, 1.0 + 0.2 * math.cos(a))).normalized()
        _place_feather(fme_t, m_tail, bodyE, base, d, Vector((math.sin(a), -0.3, 0.6)), random.uniform(3.2, 4.4), lift=0.0, roll=a * 0.4)
    # pescoco (pivo no ombro) e cabeca
    neck = empty("gal_pescoco_anim", (0, -1.8, 8.0), bodyE)
    hp = empty("gal_head_pose", (0, -1.3, 2.3), neck, rot=HEAD_EUL)
    ha = empty("gal_head_anim", (0, 0, 0), hp)
    jaw, hobjs = chicken_head(ha, m_head, m_comb, m_beak, m_eye, m_mouth)
    nb = skin_model("gal_pescoco_base", [(0, 0.3, -0.6), (0, -0.5, 0.9), (0, -1.35, 2.1), (0, -1.55, 2.35)], chain(4), [1.25, 0.95, 0.62, 0.5], m_hack)
    nb.parent = neck
    # penas do pescoco (capa dourada caindo sobre os ombros)
    for ring in range(6):
        t = ring / 5
        cz = 2.2 - t * 2.4; cy = -1.45 + t * 1.3
        rr = 0.6 + t * 0.6
        n_ = 14 + ring * 2
        for k in range(n_):
            v = k / n_ * 2 * math.pi + ring * 0.3
            pos = Vector((math.cos(v) * rr, cy + math.sin(v) * rr * 0.7, cz))
            nrm = Vector((math.cos(v), math.sin(v) * 0.8, 0.25))
            _place_feather(fme_h, m_hack, neck, pos, Vector((math.cos(v) * 0.3, 0.45 + math.sin(v) * 0.2, -1.0)), nrm, 0.75 + t * 0.7, lift=0.12)
    # pernas escamosas + dedos
    legs = []
    for sx in (1, -1):
        lg = empty("gal_perna_e", (sx * 1.0, 0.6, 3.9), root)
        coxa = sph("gal_coxa", 1, (0, 0, 0.3), m_under, scale=(0.95, 1.2, 1.3), parent=lg)
        sh = skin_model("gal_canela", [(0, 0, 0), (0, 0.15, -1.6), (0, 0.05, -3.75)], [(0, 1), (1, 2)], [0.32, 0.22, 0.22], m_leg, subd=1)
        sh.parent = lg
        for a, ln in ((-0.45, 1.5), (0, 1.75), (0.45, 1.5), (math.pi, 0.9)):
            d = Vector((math.sin(a), -math.cos(a), 0)) * ln
            dd = skin_model("gal_dedo", [(0, 0.05, -3.75), (d.x * 0.6, 0.05 + d.y * 0.6, -3.82), (d.x, 0.05 + d.y, -3.86)], [(0, 1), (1, 2)], [0.16, 0.12, 0.06], m_leg, subd=1)
            dd.parent = lg
        legs.append(lg)
    return dict(root=root, body=bodyE, neck=neck, head_pose=hp, head_anim=ha, jaw=jaw, legs=legs, head_objs=hobjs, comb=m_comb)


def anim_cluck(g, f0=1, peak=22, hold=48, close=70, beak=30):
    jaw, ha = g["jaw"], g["head_anim"]
    for fr, a in ((f0, 3), (f0 + 8, 0), (peak, beak), (peak + 5, beak - 6), (peak + 10, beak), (hold, beak - 4), (close, 2)):
        K(jaw, "rotation_euler", fr, (math.radians(a), 0, 0))
    for fr, loc, rx in ((f0, (0, 0.25, 0.05), -6), (f0 + 8, (0, 0.38, 0.1), -12), (peak, (0, -0.35, -0.05), 4), (hold, (0, -0.3, -0.03), 3), (close, (0, 0, 0), 0)):
        K(ha, "location", fr, loc); K(ha, "rotation_euler", fr, (math.radians(rx), 0, 0))


def gal_corre(g, frames_locs, rotz, step=4):
    """corrida: posicoes do root + pernas alternando + corpo quicando"""
    root = g["root"]
    for fr, loc in frames_locs:
        K(root, "location", fr, loc)
    f_a, f_b = frames_locs[0][0], frames_locs[-1][0]
    K(root, "rotation_euler", f_a, (0, 0, root.rotation_euler.z)); K(root, "rotation_euler", f_a + 3, (0, 0, rotz))
    for i, fr in enumerate(range(f_a, f_b + 1, step)):
        sgn = 1 if i % 2 else -1
        K(g["legs"][0], "rotation_euler", fr, (math.radians(35 * sgn), 0, 0))
        K(g["legs"][1], "rotation_euler", fr, (math.radians(-35 * sgn), 0, 0))
        K(g["body"], "location", fr, (0, 0, 0.6 if i % 2 else 0.0))
        K(g["body"], "rotation_euler", fr, (math.radians(-12), 0, math.radians(5 * sgn)))
    K(g["body"], "rotation_euler", f_b + 2, (0, 0, 0)); K(g["body"], "location", f_b + 2, (0, 0, 0))


# =============================================================== cenario 1: CINZAS
def _arvore_queimada(loc, h, seed, m, parent=None):
    """tronco retorcido com galhos quebrados (skin modifier), nada de cone"""
    random.seed(seed)
    verts = [(0, 0, -0.3)]; rad = [h * 0.07]; edges = []
    lean = Vector((random.uniform(-0.15, 0.15), random.uniform(-0.1, 0.1), 1)).normalized()
    p = Vector((0, 0, -0.3)); last = 0
    segs = 7
    for i in range(1, segs + 1):
        p = p + (lean + Vector((random.uniform(-0.18, 0.18), random.uniform(-0.18, 0.18), 0))).normalized() * (h / segs)
        verts.append(tuple(p)); rad.append(h * 0.07 * (1 - i / (segs + 2)) + 0.03); edges.append((last, len(verts) - 1)); last = len(verts) - 1
        if i >= 3 and random.random() < 0.75:
            q = Vector(p); bi = last
            d = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(0.3, 1.0))).normalized()
            n = random.randint(2, 3)
            for k in range(n):
                q = q + (d + Vector((random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), random.uniform(-0.2, 0.3)))).normalized() * h * random.uniform(0.09, 0.15)
                verts.append(tuple(q)); rad.append(h * 0.03 * (1 - k / (n + 1)) + 0.015); edges.append((bi, len(verts) - 1)); bi = len(verts) - 1
    o = skin_model("arvore_queimada", verts, edges, rad, m, subd=1)
    o.location = loc
    if parent:
        o.parent = parent
    return o


def _carvao_mat():
    """madeira carbonizada: preto com rachaduras em brasa (voronoi), brasa mais forte embaixo"""
    m = D.materials.new("carvao"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (3, 3, 0.8)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs["Scale"].default_value = 4
    nt.links.new(mp.outputs["Vector"], vo.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    col = nt.nodes.new("ShaderNodeValToRGB")
    col.color_ramp.elements[0].color = (0.012, 0.01, 0.009, 1); col.color_ramp.elements[1].color = (0.06, 0.05, 0.045, 1)
    nt.links.new(nz.outputs["Fac"], col.inputs["Fac"]); nt.links.new(col.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.9
    cr = nt.nodes.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.0; cr.inputs["From Max"].default_value = 0.018
    cr.inputs["To Min"].default_value = 1.0; cr.inputs["To Max"].default_value = 0.0
    nt.links.new(vo.outputs["Distance"], cr.inputs["Value"])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    lo = nt.nodes.new("ShaderNodeMapRange"); lo.inputs["From Min"].default_value = 1.2; lo.inputs["From Max"].default_value = 0.0
    nt.links.new(sp.outputs["Z"], lo.inputs["Value"])
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'
    nt.links.new(cr.outputs["Result"], mu.inputs[0]); nt.links.new(lo.outputs["Result"], mu.inputs[1])
    mu2 = nt.nodes.new("ShaderNodeMath"); mu2.operation = 'MULTIPLY'; mu2.inputs[1].default_value = 3.0
    nt.links.new(mu.outputs[0], mu2.inputs[0])
    p.inputs["Emission Color"].default_value = (1.0, 0.28, 0.03, 1)
    nt.links.new(mu2.outputs[0], p.inputs["Emission Strength"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.7
    nt.links.new(vo.outputs["Distance"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def _chao_cinzas_mat():
    """cinza escura com veios de brasa que pulsam (W do ruido animado)"""
    m = D.materials.new("chao_cinzas"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].color = (0.012, 0.01, 0.009, 1); rp.color_ramp.elements[1].color = (0.09, 0.08, 0.075, 1)
    e = rp.color_ramp.elements.new(0.75); e.color = (0.035, 0.028, 0.024, 1)
    nt.links.new(nz.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.95
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs["Scale"].default_value = 0.9
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.0; cr.inputs["From Max"].default_value = 0.012
    cr.inputs["To Min"].default_value = 1.0; cr.inputs["To Max"].default_value = 0.0
    nt.links.new(vo.outputs["Distance"], cr.inputs["Value"])
    mk = nt.nodes.new("ShaderNodeTexNoise"); mk.inputs["Scale"].default_value = 0.22
    nt.links.new(tc.outputs["Object"], mk.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.56; mr.inputs["From Max"].default_value = 0.66
    nt.links.new(mk.outputs["Fac"], mr.inputs["Value"])
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'
    nt.links.new(cr.outputs["Result"], mu.inputs[0]); nt.links.new(mr.outputs["Result"], mu.inputs[1])
    mu2 = nt.nodes.new("ShaderNodeMath"); mu2.operation = 'MULTIPLY'; mu2.inputs[1].default_value = 5
    nt.links.new(mu.outputs[0], mu2.inputs[0])
    random.seed(77)
    for fr in range(1, N + 1, 9):
        mu2.inputs[1].default_value = random.uniform(3.0, 6.5); mu2.inputs[1].keyframe_insert("default_value", frame=fr)
    p.inputs["Emission Color"].default_value = (1.0, 0.22, 0.02, 1)
    nt.links.new(mu2.outputs[0], p.inputs["Emission Strength"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.5
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    for fc in (m.node_tree.animation_data.action and fcurves_nt(m.node_tree)) or []:
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'
    return m


def fcurves_nt(nt):
    class _O:
        pass
    o = _O(); o.animation_data = nt.animation_data
    return fcurves(o)


def _fumaca_mat(name, col, dens, seed, drift):
    """silhueta de fumaca: plano com mascara de ruido (sem volume), deriva com o tempo"""
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; _clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    loc = mp.inputs["Location"]
    loc.default_value = (seed, 0, 0); loc.keyframe_insert("default_value", frame=1)
    loc.default_value = (seed + drift, -drift * 0.6, 0); loc.keyframe_insert("default_value", frame=N)
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.2; nz.inputs["Detail"].default_value = 7; nz.inputs["Roughness"].default_value = 0.62
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sp.inputs[0])
    gy = nt.nodes.new("ShaderNodeMapRange"); gy.inputs["From Min"].default_value = 0.0; gy.inputs["From Max"].default_value = 1.0
    gy.inputs["To Min"].default_value = dens; gy.inputs["To Max"].default_value = dens - 0.35
    nt.links.new(sp.outputs["Y"], gy.inputs["Value"])
    ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'ADD'
    nt.links.new(nz.outputs["Fac"], ad.inputs[0]); nt.links.new(gy.outputs["Result"], ad.inputs[1])
    th = nt.nodes.new("ShaderNodeMapRange"); th.inputs["From Min"].default_value = 0.85; th.inputs["From Max"].default_value = 1.0
    nt.links.new(ad.outputs[0], th.inputs["Value"])
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*col, 1); e.inputs["Strength"].default_value = 1.0
    # borda de baixo iluminada pelo fogo
    ed = nt.nodes.new("ShaderNodeMapRange"); ed.inputs["From Min"].default_value = 0.0; ed.inputs["From Max"].default_value = 0.35
    ed.inputs["To Min"].default_value = 1.0; ed.inputs["To Max"].default_value = 0.0
    nt.links.new(sp.outputs["Y"], ed.inputs["Value"])
    cm = nt.nodes.new("ShaderNodeMix"); cm.data_type = 'RGBA'
    nt.links.new(ed.outputs["Result"], cm.inputs[0]); cm.inputs[6].default_value = (*col, 1); cm.inputs[7].default_value = (col[0] * 4 + 0.15, col[1] * 2.5 + 0.03, col[2], 1)
    nt.links.new(cm.outputs[2], e.inputs["Color"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(th.outputs["Result"], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    for fc in fcurves_nt(nt):
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'
    return m


def _flocos(name, n, box_min, box_max, size, m, period, seed, spin=True):
    """camada de flocos (um so objeto) caindo em loop sem emenda: o padrao se repete na altura"""
    random.seed(seed)
    bm = bmesh.new()
    hz = box_max[2] - box_min[2]
    for i in range(n):
        c = Vector((random.uniform(box_min[0], box_max[0]), random.uniform(box_min[1], box_max[1]), random.uniform(box_min[2], box_max[2])))
        r = Euler((random.uniform(0, 6.3), random.uniform(0, 6.3), random.uniform(0, 6.3))).to_matrix()
        sz = size * random.uniform(0.5, 1.4)
        for dz in (0, hz):
            vv = [bm.verts.new(c + Vector((0, 0, dz)) + r @ Vector(q) * sz) for q in ((-1, -0.6, 0), (1, -0.8, 0), (0.8, 0.7, 0), (-0.7, 0.9, 0))]
            bm.faces.new(vv)
    me = D.meshes.new(name); bm.to_mesh(me); bm.free()
    o = link(D.objects.new(name, me)); setmat(o, m)
    o.visible_shadow = False
    K(o, "location", 1, (0, 0, 0)); K(o, "location", 1 + period, (period * 0.004, 0, -hz))
    cyc(o, linear=True)
    return o


def mundo_cinzas():
    """Fim do Cretaceo, logo depois do impacto. Primeiro plano: brasas, galho caido e cinzas perto da lente.
    Meio: T. rex investindo e rugindo (close). Fundo: arvores carbonizadas, fogo no horizonte, fumaca em silhueta, sol vermelho."""
    s = reset()
    bloom(s, threshold=0.9, size=0.7, strength=0.8)
    sun_dir = (-0.35, 1.0, 0.32)
    world_sky(s, [(0.0, (0.2, 0.03, 0.004)), (0.17, (0.55, 0.11, 0.01)), (0.3, (0.2, 0.035, 0.008)), (0.55, (0.04, 0.01, 0.006)), (1.0, (0.008, 0.004, 0.004))],
              strength=0.7, sun_dir=sun_dir, sun_col=(0.7, 0.08, 0.015), sun_size=1.1, sun_str=1.2)
    # chao
    gm = _chao_cinzas_mat()
    g = ground_plane(160, gm, sub=160, strength=1.4, nscale=1.6, loc=(0, 30, -0.2))
    rex = trex((0, 0, 0))
    anim_roar(rex)
    # meio/fundo: arvores carbonizadas em 3 profundidades
    cm = _carvao_mat()
    trees = []
    random.seed(3)
    for i, (x, y, h) in enumerate(((-5.5, 4, 9), (6.5, 6, 11), (-9, 12, 12), (3, 16, 10), (11, 15, 13), (-14, 22, 14), (-3, 26, 12), (8, 30, 15),
                                   (16, 28, 13), (-20, 34, 16), (0, 40, 14), (-8, 45, 15), (22, 40, 16), (13, 48, 14))):
        trees.append(_arvore_queimada((x, y, ground_z(g, x, y) - 0.1), h, 40 + i, cm))
    # tronco caido e pedras em primeiro plano
    log = skin_model("tronco_caido", [(-3.2, -3.0, 0.2), (-1.6, -3.6, 0.35), (-0.4, -4.1, 0.3)], [(0, 1), (1, 2)], [0.35, 0.3, 0.24], cm, subd=1)
    rm = pbr("rocha", (0.05, 0.045, 0.04), (0.14, 0.12, 0.1), rough=0.85, nscale=3, vor_bump=0.6, vor_scale=4, ash=(0.3, 0.29, 0.28), ash_amt=0.5)
    random.seed(9)
    rocks = []
    for i in range(9):
        x, y = random.uniform(-6, 6), random.uniform(-5, 5)
        if abs(x) < 1.8 and -3 < y < 4:
            continue
        r = sph("pedra", random.uniform(0.25, 0.7), (x, y, ground_z(g, x, y)), rm, seg=16, rings=8)
        r.scale = (1, random.uniform(0.7, 1.3), random.uniform(0.4, 0.7))
        d = r.modifiers.new("d", 'DISPLACE'); tx = D.textures.new("pd", 'VORONOI'); tx.noise_scale = 0.4; d.texture = tx; d.strength = 0.2
        rocks.append(r)
    # brasas no chao (pequenas, emissivas, piscando)
    random.seed(5)
    brasas = []
    for i in range(70):
        x, y = random.uniform(-9, 9), random.uniform(-6, 18)
        em = emis("brasa%d" % (i % 6), (1.0, 0.18 + 0.06 * (i % 3), 0.02), 6 + (i % 6) * 2)
        b = sph("brasa", random.uniform(0.03, 0.09), (x, y, ground_z(g, x, y) + 0.03), em, seg=8, rings=5)
        b.scale = (1, 1, 0.6); b.visible_shadow = False
        brasas.append(b)
    for i in range(6):   # piscar das brasas
        nd = D.materials["brasa%d" % i].node_tree.nodes["Emission"].inputs["Strength"]
        for fr in range(1, N + 1, 7):
            nd.default_value = random.uniform(2, 9); nd.keyframe_insert("default_value", frame=fr + i)
    # fogo no horizonte (faixa emissiva serrilhada atras das arvores)
    fm = D.materials.new("fogo"); fm.use_nodes = True
    nt = fm.node_tree; _clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (14, 1, 1)
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.0; nz.inputs["Detail"].default_value = 4
    nz.noise_dimensions = '4D'; wv = nz.inputs["W"]; wv.default_value = 0; wv.keyframe_insert("default_value", frame=1); wv.default_value = 6; wv.keyframe_insert("default_value", frame=N)
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sp.inputs[0])
    sb = nt.nodes.new("ShaderNodeMath"); sb.operation = 'SUBTRACT'
    nt.links.new(nz.outputs["Fac"], sb.inputs[0]); nt.links.new(sp.outputs["Y"], sb.inputs[1])
    th = nt.nodes.new("ShaderNodeMapRange"); th.inputs["From Min"].default_value = 0.0; th.inputs["From Max"].default_value = 0.12
    nt.links.new(sb.outputs[0], th.inputs["Value"])
    e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (1.0, 0.35, 0.03, 1); e.inputs["Strength"].default_value = 10
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(th.outputs["Result"], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    for fc in fcurves_nt(nt):
        for k in fc.keyframe_points:
            k.interpolation = 'LINEAR'
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 62, 2.5), rotation=(math.radians(90), 0, 0))
    fogo = bpy.context.object; fogo.scale = (170, 7, 1); setmat(fogo, fm); fogo.visible_shadow = False
    # fumaca em silhueta (3 camadas: perto = mais escura)
    fum = []
    for i, (y, z, w, h, col, dens) in enumerate(((70, 18, 220, 40, (0.03, 0.012, 0.008), 0.72), (55, 14, 170, 32, (0.016, 0.006, 0.004), 0.66), (42, 10, 130, 24, (0.008, 0.003, 0.002), 0.6))):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, y, z), rotation=(math.radians(90), 0, 0))
        p = bpy.context.object; p.scale = (w, h, 1); setmat(p, _fumaca_mat("fumaca%d" % i, col, dens, i * 3.7, 0.25 + 0.1 * i)); p.visible_shadow = False
        fum.append(p)
    # cinzas caindo (3 camadas) + fagulhas subindo
    am = pbr("cinza_floco", (0.55, 0.52, 0.5), (0.3, 0.28, 0.27), rough=0.9, nscale=40)
    fm2 = emis("fagulha", (1.0, 0.45, 0.08), 18)
    ash = [_flocos("cinzas_perto", 90, (-2.5, -6.5, -0.5), (3.0, -3.2, 6.0), 0.03, am, 160, 1),
           _flocos("cinzas_meio", 160, (-7, -3, 0), (7, 6, 9), 0.05, am, 220, 2),
           _flocos("cinzas_longe", 140, (-20, 6, 0), (20, 26, 16), 0.09, am, 260, 3)]
    fag = _flocos("fagulhas", 60, (-6, -4, 0), (6, 8, 7), 0.025, fm2, 140, 4)
    for fc in fcurves(fag):   # fagulhas sobem
        if fc.data_path == "location" and fc.array_index == 2:
            for k in fc.keyframe_points:
                k.co.y = -k.co.y
    # luz com motivo: contraluz do fogo atras, brasa por baixo (cara de terror), ceu laranja fraco
    light('AREA', (-3, 5, 5.5), (0, -1.5, 2.6), 6000, (1.0, 0.3, 0.05), size=5)          # incendio atras -> recorte forte
    light('AREA', (-6, -1, 3.0), (0, -1.5, 2.6), 600, (1.0, 0.22, 0.03), size=3)         # fogo lateral esquerdo
    light('SPOT', (2.4, -4.6, 1.0), (0, -2.2, 2.4), 900, (1.0, 0.4, 0.1), size=0.5, spot=35)               # brasas na frente: luz de baixo nos dentes
    light('SUN', (0, 0, 10), (0.3, -1, -0.6), 0.25, (1.0, 0.4, 0.15), angle=8)
    cam = camera((0, -6, 2), (0, 0, 2.5), CAM_LENS)
    frame_head(cam, rex["head_pose"])
    foco = empty("foco_rex", (0, -0.75, 0.0), rex["head_anim"])
    dof(cam, foco, 2.2)
    return dict(scene=s, cam=cam, rex=rex, head_pose=rex["head_pose"], chao=g, arvores=trees, brasas=brasas, fumaca=fum, cinzas=ash, fagulhas=fag, foco=foco, foco_objs=rex["head_objs"])


# =============================================================== cenario 2: QUINTAL
def _parede_mat(name, c1, c2, suja=True, bump=0.5):
    m = pbr(name, c1, c2, rough=0.9, nscale=1.2, vor_bump=0.0, nbump=bump, nbscale=60, coord="Object")
    if suja:   # barrado sujo de terra embaixo
        nt = m.node_tree; p = nt.nodes["Principled BSDF"]
        src = p.inputs["Base Color"].links[0].from_socket
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        ad = nt.nodes.new("ShaderNodeMath"); ad.operation = 'MULTIPLY_ADD'; ad.inputs[1].default_value = 0.5
        nt.links.new(nz.outputs["Fac"], ad.inputs[0]); nt.links.new(sp.outputs["Z"], ad.inputs[2])
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.4; mr.inputs["From Max"].default_value = -0.75
        nt.links.new(ad.outputs[0], mr.inputs["Value"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
        nt.links.new(mr.outputs["Result"], mx.inputs[0]); nt.links.new(src, mx.inputs[6]); mx.inputs[7].default_value = (0.4, 0.25, 0.15, 1)
        nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    return m


def _telha_mat():
    m = D.materials.new("telha"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 3.5; wv.bands_direction = 'X'; wv.wave_profile = 'SIN'
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 1.5; br.inputs["Mortar Size"].default_value = 0.01
    br.inputs["Color1"].default_value = (0.55, 0.16, 0.06, 1); br.inputs["Color2"].default_value = (0.42, 0.11, 0.04, 1); br.inputs["Mortar"].default_value = (0.15, 0.05, 0.02, 1)
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], p.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.7
    return m


def _grama(g, n, area, avoid, seed, m):
    """tufos de grama como uma malha so (milhares de laminas finas, curvadas)"""
    random.seed(seed)
    bm = bmesh.new()
    for i in range(n):
        x, y = random.uniform(area[0], area[1]), random.uniform(area[2], area[3])
        if any(math.hypot(x - ax, (y - ay) * 1.0) < ar for ax, ay, ar in avoid):
            continue
        z = ground_z(g, x, y)
        tuft = random.randint(3, 6)
        for k in range(tuft):
            a = random.uniform(0, 6.3); h = random.uniform(0.06, 0.2); w = random.uniform(0.006, 0.012)
            bx, by = x + random.uniform(-0.03, 0.03), y + random.uniform(-0.03, 0.03)
            lean = Vector((math.cos(a), math.sin(a), 0)) * h * random.uniform(0.2, 0.6)
            px, py = -math.sin(a) * w, math.cos(a) * w
            v0 = bm.verts.new((bx - px, by - py, z)); v1 = bm.verts.new((bx + px, by + py, z))
            v2 = bm.verts.new((bx + lean.x * 0.4 + px * 0.6, by + lean.y * 0.4 + py * 0.6, z + h * 0.55)); v3 = bm.verts.new((bx + lean.x * 0.4 - px * 0.6, by + lean.y * 0.4 - py * 0.6, z + h * 0.55))
            v4 = bm.verts.new((bx + lean.x, by + lean.y, z + h))
            bm.faces.new((v0, v1, v2, v3)); bm.faces.new((v3, v2, v4))
    me = D.meshes.new("grama"); bm.to_mesh(me); bm.free()
    o = link(D.objects.new("grama", me)); setmat(o, m)
    return o


def _pano(name, w, h, loc, m, parent, seed):
    """roupa no varal: plano subdividido com dobras (displace) pendurado pela borda de cima"""
    piv = empty(name + "_piv", loc, parent)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=14, y_subdivisions=18, size=1)
    o = bpy.context.object; o.name = name
    for v in o.data.vertices:
        v.co = Vector((v.co.x * w, 0, -(v.co.y + 0.5) * h))
    tx = D.textures.new(name + "T", 'WOOD'); tx.noise_scale = 0.2; tx.wood_type = 'BANDNOISE'
    d = o.modifiers.new("dobras", 'DISPLACE'); d.texture = tx; d.strength = 0.035; d.direction = 'Y'
    smooth(o); setmat(o, m); o.parent = piv
    # balanco do vento (fase diferente por peca)
    random.seed(seed)
    ph = random.randint(0, 40); amp = random.uniform(9, 16)
    for k, fr in enumerate(range(1 - ph, N + 60, 22)):
        K(piv, "rotation_euler", fr, (math.radians(amp * (1 if k % 2 else -0.35)), 0, math.radians(random.uniform(-4, 4))))
    return piv, o


def _tecido_mat(name, c1, c2, listras=0.0, scale=12):
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    if listras:
        wv = nt.nodes.new("ShaderNodeTexWave"); wv.bands_direction = 'Z'; wv.inputs["Scale"].default_value = listras
        nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
        rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = 'CONSTANT'
        rp.color_ramp.elements[0].color = (*c1, 1); rp.color_ramp.elements[1].position = 0.5; rp.color_ramp.elements[1].color = (*c2, 1)
        nt.links.new(wv.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    else:
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
        nt.links.new(nz.outputs["Fac"], mx.inputs[0]); mx.inputs[6].default_value = (*c1, 1); mx.inputs[7].default_value = (*c2, 1)
        nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    ck = nt.nodes.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 260
    nt.links.new(tc.outputs["Object"], ck.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15
    nt.links.new(ck.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.85
    try:
        p.inputs["Sheen Weight"].default_value = 0.5
    except Exception:
        pass
    return m


def _folha(name, length, width, bend, m, parent=None, split=False):
    """folha larga (bananeira / folhagem) com nervura central e curvatura"""
    bm = bmesh.new(); rows, cols = 14, 6; vs = []
    for i in range(rows + 1):
        t = i / rows
        w = width * math.sin(math.pi * min(1, 0.05 + t)) ** 0.6
        row = []
        for j in range(cols + 1):
            u = (j / cols - 0.5) * 2
            z = -bend * (t * t) * length + 0.06 * width * abs(u) - (0.04 * math.sin(t * 30 + u * 3) * width if split else 0)
            row.append(bm.verts.new((u * w * 0.5, t * length, z)))
        vs.append(row)
    for i in range(rows):
        for j in range(cols):
            bm.faces.new((vs[i][j], vs[i][j + 1], vs[i + 1][j + 1], vs[i + 1][j]))
    me = D.meshes.new(name); bm.to_mesh(me); bm.free()
    o = link(D.objects.new(name, me)); smooth(o); setmat(o, m)
    if parent:
        o.parent = parent
    return o


def _folha_mat(name, c1, c2):
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sp.inputs[0])
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.bands_direction = 'Y'; wv.inputs["Scale"].default_value = 30; wv.inputs["Distortion"].default_value = 0.5
    nt.links.new(tc.outputs["Generated"], wv.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 4; nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(nz.outputs["Fac"], mx.inputs[0]); mx.inputs[6].default_value = (*c1, 1); mx.inputs[7].default_value = (*c2, 1)
    # nervura central clara
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'
    sb = nt.nodes.new("ShaderNodeMath"); sb.operation = 'SUBTRACT'; sb.inputs[1].default_value = 0.5
    nt.links.new(sp.outputs["X"], sb.inputs[0]); nt.links.new(sb.outputs[0], ab.inputs[0])
    nv = nt.nodes.new("ShaderNodeMapRange"); nv.inputs["From Min"].default_value = 0.03; nv.inputs["From Max"].default_value = 0.0
    nt.links.new(ab.outputs[0], nv.inputs["Value"])
    mx2 = nt.nodes.new("ShaderNodeMix"); mx2.data_type = 'RGBA'
    nt.links.new(nv.outputs["Result"], mx2.inputs[0]); nt.links.new(mx.outputs[2], mx2.inputs[6]); mx2.inputs[7].default_value = (0.6, 0.75, 0.25, 1)
    nt.links.new(mx2.outputs[2], p.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25
    nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.45
    try:
        p.inputs["Subsurface Weight"].default_value = 0.0
    except Exception:
        pass
    return m


def bemtevi(loc, rotz, scale=1.0):
    """passarinho (bem-te-vi): barriga amarela, mascara preta e branca. Anima: cabecinha olhando e pulinhos"""
    root = empty("bemtevi", loc, rot=(0, 0, rotz)); root.scale = (scale,) * 3
    amar = pbr("btv_amarelo", (1.0, 0.78, 0.02), (0.95, 0.65, 0.0), rough=0.7, nscale=20, nbump=0.2, nbscale=60)
    marr = pbr("btv_marrom", (0.25, 0.15, 0.06), (0.35, 0.22, 0.09), rough=0.7, nscale=20)
    pret = pbr("btv_preto", (0.02, 0.02, 0.02), rough=0.5)
    bran = pbr("btv_branco", (0.95, 0.95, 0.92), rough=0.6)
    body = empty("btv_corpo", (0, 0, 0), root)
    sph("btv_barriga", 1, (0, 0, 0.07), amar, scale=(0.045, 0.06, 0.05), parent=body)
    sph("btv_costas", 1, (0, 0.01, 0.085), marr, scale=(0.043, 0.065, 0.04), parent=body).rotation_euler = (math.radians(-15), 0, 0)
    cone("btv_cauda", 0.025, 0.012, 0.08, (0, 0.075, 0.06), (math.radians(-70), 0, 0), marr, parent=body)
    hd = empty("btv_cabeca", (0, -0.04, 0.12), body)
    sph("btv_cab", 0.035, (0, 0, 0), pret, parent=hd)
    for sx in (1, -1):
        sph("btv_faixa", 1, (sx * 0.012, 0.0, 0.006), bran, scale=(0.026, 0.03, 0.011), parent=hd).rotation_euler = (0, sx * 0.5, 0)
    sph("btv_coroa", 1, (0, 0.002, 0.028), amar, scale=(0.012, 0.02, 0.008), parent=hd)
    sph("btv_garganta", 1, (0, -0.02, -0.02), bran, scale=(0.022, 0.015, 0.018), parent=hd)
    cone("btv_bico", 0.009, 0.001, 0.04, (0, -0.05, -0.004), (math.radians(90), 0, 0), pret, parent=hd)
    for sx in (1, -1):
        cyl("btv_pe", 0.003, 0.04, (sx * 0.015, 0, 0.02), pret, parent=body)
    for fr in range(1, N + 30, 18):
        K(hd, "rotation_euler", fr, (0, 0, math.radians(random.choice((-50, -20, 25, 45)))))
        K(hd, "rotation_euler", fr + 3, (0, 0, hd.rotation_euler.z))
    for fr in range(30, N + 30, 75):
        K(body, "location", fr, (0, 0, 0)); K(body, "location", fr + 4, (0, 0, 0.05)); K(body, "location", fr + 8, (0, 0, 0))
    return root


def mundo_quintal():
    """Quintal brasileiro de manha. Primeiro plano: vaso de barro com folhagem, grama e milho no chao.
    Meio: galinha (match cut) e o espaco livre de terra batida (pista da fuga da Pipo).
    Fundo: varal balancando, mangueira enrolada na torneira, bananeira, muro com barrado sujo,
    casa do vizinho com telhado e caixa d'agua azul, arvore, bem-te-vi no muro, ceu de manha."""
    s = reset()
    bloom(s, threshold=1.2, size=0.5, strength=0.35)
    sun_dir = Vector((-1.0, 0.55, 0.32)).normalized()       # sol baixo vindo da esquerda/fundo: contraluz quente
    world_sky(s, [(0.0, (0.95, 0.55, 0.25)), (0.17, (0.9, 0.62, 0.38)), (0.33, (0.3, 0.55, 0.95)), (1.0, (0.05, 0.25, 0.8))], strength=0.8,
              sun_dir=sun_dir, sun_col=(1.0, 0.62, 0.3), sun_size=0.7, sun_str=2.5)
    # chao de terra batida
    tm = pbr("terra", (0.36, 0.2, 0.1), (0.5, 0.3, 0.15), (0.3, 0.16, 0.08), rough=0.92, nscale=1.5, vor_bump=0.35, vor_scale=40, nbump=0.3, nbscale=9)
    g = ground_plane(40, tm, sub=120, strength=0.12, nscale=1.2, loc=(0, 8, 0))
    gm = pbr("grama", (0.12, 0.36, 0.05), (0.35, 0.55, 0.08), (0.45, 0.45, 0.12), rough=0.6, nscale=3)
    path_y = 3.1    # caminho de fundo livre (perseguicao pequena no plano final)
    avoid = [(0.2, 0.0, 1.0), (-1.3, -0.3, 1.0), (-2.6, -0.2, 0.8)] + [(x, path_y, 0.45) for x in range(-6, 7)]
    grama = [_grama(g, 1100, (-6, 6, -1.2, 4.4), avoid + [(0, 0.8, 1.6)], 1, gm),
             _grama(g, 300, (-3.5, 3.5, -2.6, -1.6), avoid, 2, gm)]
    # muro (y = 4.6) com pilares e capa
    muro_m = _parede_mat("muro", (0.92, 0.66, 0.28), (0.82, 0.55, 0.22))
    capa_m = pbr("capa", (0.55, 0.53, 0.5), (0.42, 0.4, 0.38), rough=0.9, nscale=4, nbump=0.4, nbscale=40)
    box("muro", (14, 0.2, 2.2), (0, 4.6, 1.1), muro_m, 0.01)
    box("capa_muro", (14.2, 0.32, 0.08), (0, 4.6, 2.24), capa_m, 0.01)
    for x in (-6, -3, 0, 3, 6):
        box("pilar", (0.32, 0.32, 2.35), (x, 4.6, 1.17), muro_m, 0.02)
    # torneira + mangueira verde enrolada pendurada
    met = pbr("metal", (0.7, 0.7, 0.72), rough=0.25, metal=1.0)
    cyl("cano", 0.025, 0.25, (2.6, 4.4, 0.75), met, rot=(math.radians(90), 0, 0))
    cyl("torneira_bico", 0.02, 0.15, (2.6, 4.28, 0.68), met)
    mang_m = pbr("mangueira", (0.05, 0.45, 0.12), (0.03, 0.35, 0.08), rough=0.35, nscale=5, spec=0.7)
    pts = []
    for i in range(110):
        a = i / 110 * 2 * math.pi * 5.5
        r = 0.32 + 0.012 * (i % 7)
        pts.append((2.6 + math.cos(a) * r, 4.36 - i * 0.0014, 1.18 + math.sin(a) * r * 1.05))
    mang = tube("mangueira", pts, 0.022, mang_m, res=2)
    tube("mangueira_cai", [(2.6, 4.32, 0.62), (2.5, 4.2, 0.3), (2.2, 4.0, 0.05), (1.6, 3.9, 0.03)], 0.022, mang_m, res=2)
    # varal (postes de madeira, fio, roupas, prendedores)
    wood = pbr("madeira", (0.32, 0.2, 0.1), (0.22, 0.13, 0.06), rough=0.8, nscale=3, nbump=0.4, nbscale=12)
    vy, vz = 3.85, 1.85
    for x in (-3.4, 2.0):
        cyl("poste_varal", 0.05, 1.95, (x, vy, 0.97), wood, verts=10)
    fio_m = pbr("fio", (0.85, 0.85, 0.85), rough=0.3)
    fio = tube("fio_varal", [(-3.4, vy, vz), (-0.7, vy, vz - 0.12), (2.0, vy, vz)], 0.006, fio_m, res=1)
    varal = empty("varal", (0, 0, 0))
    roupas = []
    pecas = [("toalha", 0.75, 1.05, -2.7, _tecido_mat("toalha", (1.0, 0.72, 0.02), (0.95, 0.6, 0.0)), 1),
             ("camiseta", 0.62, 0.7, -1.75, _tecido_mat("camiseta", (0.05, 0.3, 0.85), (0.04, 0.22, 0.7)), 2),
             ("pano", 0.5, 0.55, -1.0, _tecido_mat("pano", (0.9, 0.08, 0.1), (0.98, 0.96, 0.92), listras=9), 3),
             ("lencol", 0.9, 1.2, 0.0, _tecido_mat("lencol", (0.95, 0.95, 0.98), (0.1, 0.65, 0.55), listras=4), 4),
             ("short", 0.42, 0.5, 1.2, _tecido_mat("short", (0.1, 0.65, 0.3), (0.06, 0.5, 0.22)), 5)]
    pren = [pbr("prendedor%d" % i, c, rough=0.4) for i, c in enumerate(((1, 0.2, 0.5), (0.1, 0.7, 1), (1, 0.85, 0.1)))]
    for nm, w, h, x, m, sd in pecas:
        sag = -0.12 * (1 - ((x + 0.7) / 2.7) ** 2)
        piv, o = _pano(nm, w, h, (x, vy, vz + sag - 0.01), m, varal, sd)
        roupas.append(piv)
        for dx in (-w * 0.42, w * 0.42):
            box("prendedor", (0.025, 0.03, 0.07), (x + dx, vy, vz + sag + 0.01), pren[sd % 3], 0.005)
    # bananeira (fundo esquerdo)
    banm = _folha_mat("bananeira", (0.15, 0.48, 0.08), (0.25, 0.6, 0.1))
    caule = pbr("caule_banana", (0.35, 0.42, 0.15), (0.25, 0.3, 0.1), rough=0.7, nscale=3, nbump=0.4, nbscale=6)
    ban = empty("bananeira", (-4.6, 3.9, 0))
    skin_model("pseudocaule", [(0, 0, 0), (0.05, 0, 1.4), (0.1, 0.05, 2.6)], [(0, 1), (1, 2)], [0.2, 0.15, 0.12], caule, subd=1).parent = ban
    random.seed(8)
    folhas = []
    for i in range(8):
        a = i / 8 * 2 * math.pi + random.uniform(-0.2, 0.2)
        pv = empty("folha_piv", (0.1, 0.05, 2.55), ban, rot=(math.radians(random.uniform(-55, -20)), 0, a))
        fo = _folha("folha_banana", random.uniform(1.4, 1.9), 0.55, 0.35, banm, parent=pv, split=True)
        folhas.append(pv)
        for k, fr in enumerate(range(1 + i * 5, N + 40, 40)):
            K(pv, "rotation_euler", fr, (pv.rotation_euler.x + math.radians(3 if k % 2 else -3), 0, a))
    # casa do vizinho + caixa d'agua azul + arvore grande
    casa_m = _parede_mat("casa", (0.95, 0.88, 0.8), (0.85, 0.78, 0.7), suja=False)
    box("casa", (6, 4, 3.5), (3.5, 8.5, 1.75), casa_m, 0.02)
    tel = _telha_mat()
    for sy in (1, -1):
        box("telhado", (6.6, 2.4, 0.08), (3.5, 8.5 - sy * 1.05, 3.95), tel, 0.0, rot=(math.radians(sy * 22), 0, 0))
    cx = pbr("caixa_dagua", (0.03, 0.25, 0.75), (0.05, 0.32, 0.85), rough=0.3, nscale=3, nbump=0.1, nbscale=8, spec=0.8)
    cyl("caixa_dagua", 0.65, 0.85, (5.0, 8.6, 4.7), cx, verts=32)
    cyl("tampa", 0.68, 0.1, (5.0, 8.6, 5.17), cx, verts=32)
    copa_m = pbr("copa", (0.05, 0.25, 0.04), (0.12, 0.38, 0.06), (0.2, 0.42, 0.08), rough=0.7, nscale=2, vor_bump=0.8, vor_scale=14)
    random.seed(12)
    el = [((random.uniform(-2.2, 2.2), random.uniform(-1.2, 1.2), random.uniform(-0.8, 1.6)), random.uniform(1.0, 1.6)) for i in range(16)]
    copa = metaball_mesh("copa", el, res=0.2)
    setmat(copa, copa_m); copa.location = (-2.2, 9.5, 5.2)
    d = copa.modifiers.new("d", 'DISPLACE'); tx = D.textures.new("copaT", 'CLOUDS'); tx.noise_scale = 0.5; d.texture = tx; d.strength = 0.5
    skin_model("tronco_arvore", [(-2.2, 9.5, 0), (-2.0, 9.6, 3), (-2.3, 9.4, 4.6)], [(0, 1), (1, 2)], [0.3, 0.24, 0.2], wood, subd=1)
    K(copa, "rotation_euler", 1, (0, 0, 0)); K(copa, "rotation_euler", 60, (0, math.radians(1.2), 0)); K(copa, "rotation_euler", 120, (0, 0, 0)); cyc(copa)
    # vaso de barro com folhagem (primeiro plano esquerdo)
    barro = pbr("barro", (0.62, 0.25, 0.1), (0.5, 0.18, 0.07), (0.7, 0.35, 0.18), rough=0.85, nscale=5, nbump=0.35, nbscale=30)
    vx, vy2 = -1.35, -0.55
    bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=0.17, radius2=0.25, depth=0.36, location=(vx, vy2, 0.18))
    vaso = bpy.context.object; vaso.name = "vaso"; smooth(vaso); setmat(vaso, barro)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.03, location=(vx, vy2, 0.36))
    borda = bpy.context.object; smooth(borda); setmat(borda, barro)
    cyl("terra_vaso", 0.23, 0.02, (vx, vy2, 0.34), tm)
    fvm = _folha_mat("folhagem", (0.05, 0.38, 0.1), (0.3, 0.6, 0.12))
    folhagem = []
    random.seed(21)
    for i in range(11):
        a = i / 11 * 2 * math.pi
        pv = empty("folhagem_piv", (vx, vy2, 0.34), rot=(math.radians(random.uniform(-40, -15)), 0, a))
        _folha("folha_vaso", random.uniform(0.35, 0.5), 0.16, 0.5, fvm, parent=pv)
        folhagem.append(pv)
    # graos de milho no chao (o que a galinha cisca) + pedrinhas
    milho = pbr("milho", (1.0, 0.68, 0.05), (0.95, 0.55, 0.03), rough=0.35, nscale=20, spec=0.7)
    pedra = pbr("pedrinha", (0.45, 0.4, 0.35), (0.3, 0.27, 0.24), rough=0.8, nscale=10, vor_bump=0.3, vor_scale=20)
    random.seed(31)
    for i in range(40):
        x, y = random.uniform(-0.6, 1.4), random.uniform(-1.6, 0.6)
        sph("grao", 0.009, (x, y, ground_z(g, x, y) + 0.005), milho, seg=8, rings=5, scale=(1, 0.8, 0.6))
    for i in range(30):
        x, y = random.uniform(-4, 4), random.uniform(-2.5, 3)
        sph("pedrinha", random.uniform(0.01, 0.04), (x, y, ground_z(g, x, y)), pedra, seg=8, rings=5, scale=(1, 0.8, 0.5))
    # galinha (de frente para a camera, cacarejando)
    gal = galinha((0.35, 0.15, ground_z(g, 0.35, 0.15)), rotz=math.radians(8))
    anim_cluck(gal)
    btv = bemtevi((1.3, 4.6, 2.28), math.radians(150), scale=1.0)
    # luz com motivo: sol baixo da manha (esquerda/fundo) + rebatida quente da terra + ceu azul preenchendo
    sun = light('SUN', (0, 0, 10), None, 3.4, (1.0, 0.68, 0.4), angle=1.5)
    sun.rotation_euler = (-sun_dir).to_track_quat('-Z', 'Y').to_euler()
    light('AREA', (1.5, -2.5, 1.2), (0.3, 0.1, 0.45), 30, (1.0, 0.75, 0.55), size=2.0)        # rebatida (muro/terra)
    light('AREA', (-0.3, -1.2, 2.5), (0.3, 0.1, 0.3), 25, (0.6, 0.75, 1.0), size=2.5)          # ceu
    cam = camera((0, -2, 0.5), (0, 0, 0.4), CAM_LENS)
    frame_head(cam, gal["head_pose"])
    foco = empty("foco_gal", (0, -0.75, 0.0), gal["head_anim"])
    dof(cam, foco, 4.0)
    caminho = [(x, path_y, 0.0) for x in (4.5, 3, 1.5, 0, -1.5, -3, -4.5)]
    return dict(scene=s, cam=cam, galinha=gal, head_pose=gal["head_pose"], chao=g, varal=varal, roupas=roupas, bemtevi=btv,
                vaso=vaso, mangueira=mang, bananeira=ban, foco=foco, caminho_fundo=caminho, pista_fuga=[(-0.06, -0.22), (-3.5, -0.45)],
                foco_objs=gal["head_objs"])


# =============================================================== PIPO no quintal
_PIPO = {}


def _load_pipo():
    """executa a pipo_lib no cenario atual sem zerar a cena: guarda mundo e render, apaga o estudio roxo"""
    s = bpy.context.scene
    keep = set(o.name for o in D.objects)
    world = s.world
    saved = dict(vt=s.view_settings.view_transform, look=s.view_settings.look, samples=s.cycles.samples, thr=s.cycles.adaptive_threshold,
                 gb=s.cycles.glossy_bounces, cam=s.camera, fs=s.frame_start, fe=s.frame_end)
    src = open(KIT + "/pipo_lib.py").read().replace("bpy.ops.wm.read_factory_settings(use_empty=True)", "pass")
    ns = dict(WORK=WORK, N=N, KIT=KIT, __name__="pipo_lib")
    exec(compile(src, "pipo_lib.py", "exec"), ns)
    pipo = ns["pipo"]

    def under(o):
        while o is not None:
            if o == pipo:
                return True
            o = o.parent
        return False
    for o in list(D.objects):
        if o.name not in keep and not under(o):
            D.objects.remove(o, do_unlink=True)
    s.world = world
    s.view_settings.view_transform = saved["vt"]; s.view_settings.look = saved["look"]
    s.cycles.samples = saved["samples"]; s.cycles.adaptive_threshold = saved["thr"]; s.cycles.glossy_bounces = saved["gb"]
    s.camera = saved["cam"]; s.frame_start, s.frame_end = saved["fs"], saved["fe"]
    ns["pipo_start_kernel"]()
    _PIPO.clear(); _PIPO.update(ns)
    return ns


def pipo_reacao(quintal, x=-1.12, y=-0.32, scale=0.27):
    """easter egg: Pipo espiga meio escondida atras do vaso, olho arregalado, olhando a galinha"""
    ns = _load_pipo()
    ns["pipo_place"](x, y, scale)
    g = quintal["galinha"]["root"].location
    ns["pipo"].rotation_euler = (0, 0, math.atan2(g.x - x, -(g.y - y)) * 0.6)
    ns["set_face"](ns["FK"], 1, lid=-60, brow=(15, 0.33), browL=(15, 0.33), look=(25, 5))
    quintal["pipo"] = ns["pipo"]; quintal["pipo_ns"] = ns
    return ns["pipo"]


def pipo_foge(quintal, f0=60, x=-0.06, y=-0.22, scale=0.33):
    """A Pipo (espiga = milho) vira o alvo da galinha. Linha do tempo (~3 s):
    f0: galinha vira a cabeca para a Pipo | f0..f0+18: Pipo congela com SIGN (tedio + sobrancelha levantada)
    f0+20..f0+65: Pipo sai pulando rapido para a esquerda, para fora do quadro | f0+28..f0+90: galinha corre atras.
    A pista (quintal['pista_fuga']) esta livre de props; o caminho de fundo (quintal['caminho_fundo']) serve
    para repetir a perseguicao pequena, atras, no plano final."""
    ns = _load_pipo()
    pipo, FK = ns["pipo"], ns["FK"]
    ns["pipo_place"](x, y, scale)
    gal = quintal["galinha"]; gr = gal["root"]
    dx, dy = gr.location.x - x, gr.location.y - y
    face_gal = math.atan2(dx, -dy)            # rosto da Pipo e -Y local
    K(pipo, "rotation_euler", 1, (0, 0, face_gal * 0.55))
    # galinha vira a cabeca (pescoco gira para a Pipo, cabeca abaixa um pouco: mira de comida)
    nk = gal["neck"]
    rz = gr.rotation_euler.z
    rx_, ry_ = x - gr.location.x, y - gr.location.y
    lx, ly = rx_ * math.cos(-rz) - ry_ * math.sin(-rz), rx_ * math.sin(-rz) + ry_ * math.cos(-rz)
    ang = math.atan2(lx, -ly)
    K(nk, "rotation_euler", 1, (0, 0, 0)); K(nk, "rotation_euler", f0 - 1, (0, 0, 0))
    K(nk, "rotation_euler", f0 + 4, (math.radians(10), 0, ang * 0.75)); K(nk, "rotation_euler", f0 + 20, (math.radians(12), 0, ang * 0.8))
    K(gal["jaw"], "rotation_euler", f0 + 2, (math.radians(2), 0, 0))
    # Pipo congela: SIGN, olhando a galinha
    ns["set_face"](FK, 1, **ns["SIGN"], look=(-25, 4))
    ns["set_face"](FK, f0 + 4, **ns["SIGN"], look=(-28, 6))
    ns["blink"](FK, f0 + 12, ns["TIRED"])
    # foge pulando rapido para fora do quadro (esquerda)
    xs = [x - 0.0, x - 0.55, x - 1.15, x - 1.8, x - 2.5, x - 3.3]
    fr = f0 + 20
    K(pipo, "location", fr - 1, (x, y, 0))
    K(pipo, "rotation_euler", fr - 1, (0, 0, face_gal * 0.55)); K(pipo, "rotation_euler", fr + 3, (0, 0, math.radians(-90)))
    for i in range(1, len(xs)):
        ns["pipo_hop"](fr, h=0.35)
        K(pipo, "location", fr + 9, (xs[i], y - 0.04 * i, 0))
        fr += 9
    # galinha corre atras
    p0 = gr.location.copy()
    locs = [(f0 + 28, tuple(p0))] + [(f0 + 28 + 10 * k, (p0.x - 0.75 * k, p0.y - 0.06 * k, p0.z)) for k in range(1, 7)]
    K(nk, "rotation_euler", f0 + 28, (math.radians(18), 0, 0))
    gal_corre(gal, locs, math.radians(-80))
    quintal["pipo"] = pipo; quintal["pipo_ns"] = ns
    quintal["pipo_foco"] = empty("foco_pipo", (0, 0, 0.6), pipo)
    return dict(pipo=pipo, f_congela=f0 + 6, f_sai=f0 + 20, f_fora=fr, f_galinha_corre=f0 + 28)


# =============================================================== cenario 3: COMPARACAO
def _silhueta_mat(name, rim_col=(1.0, 0.45, 0.2), rim=4.0):
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; _clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.25
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(pw.outputs[0], mx.inputs[0]); mx.inputs[6].default_value = (0.012, 0.006, 0.025, 1); mx.inputs[7].default_value = (*rim_col, 1)
    e = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mx.outputs[2], e.inputs["Color"])
    ml = nt.nodes.new("ShaderNodeMath"); ml.operation = 'MULTIPLY_ADD'; ml.inputs[1].default_value = rim; ml.inputs[2].default_value = 1.0
    nt.links.new(pw.outputs[0], ml.inputs[0]); nt.links.new(ml.outputs[0], e.inputs["Strength"])
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


def _furcula(name, parent, loc, width, depth, radius, m, halo_m, halo_r):
    """ossinho da sorte: V/U com a pontinha (hipocleideo) embaixo"""
    a, d = width / 2, depth
    pts = [(-a, 0.06 * a, 0), (-a * 0.72, 0, -d * 0.35), (-a * 0.32, 0, -d * 0.82), (0, 0, -d), (a * 0.32, 0, -d * 0.82), (a * 0.72, 0, -d * 0.35), (a, 0.06 * a, 0)]
    f = tube(name, pts, radius, m, res=3)
    f.parent = parent; f.location = loc
    hp = cyl(name + "_ponta", radius * 0.8, d * 0.2, (0, 0, -d - d * 0.08), m, parent=f, verts=8)
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1, fill_type='NGON', location=(0, -radius * 3, -d * 0.5), rotation=(math.radians(90), 0, 0))
    h = bpy.context.object; h.name = name + "_halo"; setmat(h, halo_m); h.scale = (halo_r, halo_r, 1); h.parent = f; h.visible_shadow = False
    return f


def _passaros_ceu(n, center, spread, seed):
    random.seed(seed)
    m = emis("passaro_ceu", (0.02, 0.01, 0.03), 1.0)
    out = []
    for i in range(n):
        root = empty("ave_ceu", (center[0] + random.uniform(-spread, spread), center[1] + random.uniform(-3, 3), center[2] + random.uniform(-spread * 0.4, spread * 0.4)))
        sc = random.uniform(0.8, 1.2)
        for sx in (1, -1):
            pv = empty("asa", (0, 0, 0), root)
            bpy.ops.mesh.primitive_plane_add(size=1)
            w = bpy.context.object; w.scale = (0.5 * sc, 0.16 * sc, 1); w.location = (sx * 0.25 * sc, 0, 0); setmat(w, m); w.parent = pv
            ph = random.randint(0, 8)
            for fr in range(1 - ph, N + 20, 8):
                K(pv, "rotation_euler", fr, (0, math.radians(sx * 30), 0)); K(pv, "rotation_euler", fr + 4, (0, math.radians(-sx * 25), 0))
        K(root, "location", 1); root.location.x += 6; K(root, "location", N)
        for fc in fcurves(root):
            for k in fc.keyframe_points:
                k.interpolation = 'LINEAR'
        out.append(root)
    return out


def mundo_comparacao():
    """T. rex e galinha em silhueta lado a lado, mesma pose, por do sol; furcula em V acesa no peito de cada um."""
    s = reset()
    bloom(s, threshold=1.0, size=0.6, strength=0.6)
    sun_dir = Vector((0.1, 1.0, 0.06)).normalized()
    world_sky(s, [(0.0, (1.0, 0.42, 0.05)), (0.12, (1.0, 0.25, 0.08)), (0.3, (0.75, 0.1, 0.25)), (0.55, (0.25, 0.05, 0.3)), (1.0, (0.04, 0.02, 0.12))],
              strength=1.0, sun_dir=sun_dir, sun_col=(1.0, 0.7, 0.3), sun_size=2.2, sun_str=3)
    # chao e morros em camadas (perspectiva atmosferica: longe = mais claro/roxo)
    # chao molhado espelhado (reflete o ceu e as silhuetas) + grama queimada na frente
    s.cycles.glossy_bounces = 1
    cm_ = pbr("chao_espelho", (0.02, 0.01, 0.025), (0.05, 0.02, 0.04), rough=0.12, nscale=0.6, nbump=0.35, nbscale=1.5, spec=1.0)
    chao = ground_plane(200, cm_, sub=60, strength=0.05, nscale=3, loc=(0, 40, 0))
    morros = []
    for i, (y, h, col) in enumerate(((140, 14, (0.45, 0.1, 0.3)), (100, 10, (0.22, 0.05, 0.2)), (65, 7, (0.08, 0.02, 0.1)))):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=200, y_subdivisions=2, size=1, location=(0, y, 0))
        mo = bpy.context.object; mo.scale = (420, 1, 1)
        random.seed(40 + i)
        for v in mo.data.vertices:
            if v.co.y > 0:
                v.co.z = (h + h * 0.5 * math.sin(v.co.x * 25 + i) + h * 0.3 * math.sin(v.co.x * 61 + 2 * i)) / 1.0
            v.co.y = 0
        setmat(mo, emis("morro%d" % i, col, 1.0)); morros.append(mo)
    # samambaias/cicas em silhueta no primeiro plano
    pl = emis("planta_sil", (0.005, 0.002, 0.01), 1.0)
    for (x, y, r) in ((-2.4, -5.0, 0.2), (3.0, -4.6, -0.4)):
        for k in range(7):
            a = k / 7 * math.pi - math.pi / 2
            pv = empty("fronde", (x, y, 0), rot=(math.radians(-55 + abs(a) * 25), 0, a + r))
            _folha("fronde", 2.0, 0.55, 0.5, pl, parent=pv, split=True)
    rim_m = _silhueta_mat("silhueta")
    rex = trex((-0.2, 5.5, 0), rotz=math.radians(-38))
    gal = galinha((2.0, 0.4, 0), rotz=math.radians(-38), scale=CU * 3.0)
    gq = _grama(chao, 900, (-4.5, 4.5, -6.2, -4.6), [], 5, emis("grama_queimada", (0.006, 0.003, 0.008), 1.0))
    gq.scale = (1, 1, 2.2)
    for d in (rex, gal):
        for o in D.objects:
            p = o
            while p is not None and p != d["root"]:
                p = p.parent
            if p is not None and o.type in ('MESH', 'CURVE'):
                o.data.materials.clear(); o.data.materials.append(rim_m)
    anim_roar(rex); anim_cluck(gal)
    fm = emis("furcula", (1.0, 0.78, 0.25), 22)
    hm = halo_mat("furcula_halo", (1.0, 0.55, 0.15), 3.0)
    fr_rex = _furcula("furcula_rex", rex["root"], (0, -1.62, 2.45), 1.25, 0.9, 0.075, fm, hm, 1.5)   # na frente do peito
    fr_rex.rotation_euler = (math.radians(-20), 0, 0)
    fr_gal = _furcula("furcula_gal", gal["body"], (0, -3.5, 7.2), 2.6, 3.0, 0.3, fm, hm, 4.2)
    fr_gal.rotation_euler = (math.radians(-18), 0, 0)
    aves = _passaros_ceu(7, (-4, 60, 22), 5, 3)
    light('AREA', (0, 15, 4), (0, 0, 2), 800, (1.0, 0.5, 0.2), size=10)
    cam = camera((0.6, -8.0, 0.75), (0.6, 3.0, 2.2), 30, shift_y=-0.02)
    return dict(scene=s, cam=cam, rex=rex, galinha=gal, furculas=[fr_rex, fr_gal], aves=aves, morros=morros,
                foco_objs=[fr_rex, fr_gal])


# =============================================================== MATCH CUT
def _ref(head_pose, name):
    for o in head_pose.children_recursive:
        if o.name.startswith(name):
            return o
    raise KeyError(name)


def tela_refs(cam, head_pose):
    """(olho_xy, ponta_xy) na tela, coordenadas da camera (0..1, y para cima)"""
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    s = bpy.context.scene
    e = world_to_camera_view(s, cam, _ref(head_pose, "ref_olho").matrix_world.translation)
    p = world_to_camera_view(s, cam, _ref(head_pose, "ref_ponta").matrix_world.translation)
    return (e.x, e.y), (p.x, p.y)


def match_cut(cam, head_pose, alvo_olho, alvo_ponta, iters=4):
    """ajusta distancia, giro (roll) e shift da camera para que o olho e a ponta do bico/focinho
    caiam no mesmo lugar da tela do plano anterior (o T. rex): o corte vende a troca."""
    for _ in range(iters):
        (ex, ey), (px, py) = tela_refs(cam, head_pose)
        sx, sy = W / max(W, H), H / max(W, H)
        v = Vector(((px - ex) * sx, (py - ey) * sy)); V = Vector(((alvo_ponta[0] - alvo_olho[0]) * sx, (alvo_ponta[1] - alvo_olho[1]) * sy))
        ratio = V.length / max(v.length, 1e-6)
        eye_w = _ref(head_pose, "ref_olho").matrix_world.translation
        cam.location = eye_w + (cam.location - eye_w) / ratio
        da = math.atan2(V.y, V.x) - math.atan2(v.y, v.x)
        cam.rotation_euler = (cam.rotation_euler.to_matrix() @ Matrix.Rotation(-da, 3, 'Z')).to_euler()
        bpy.context.view_layer.update()
        (ex, ey), _p = tela_refs(cam, head_pose)
        cam.data.shift_x += (ex - alvo_olho[0]) * sx
        cam.data.shift_y += (ey - alvo_olho[1]) * sy
    return tela_refs(cam, head_pose)
