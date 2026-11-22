"""CENARIOS do canal Pipo: ambientes 3D completos (no lugar do estudio roxo padrao).
Uso no ep.py, logo depois do exec do pipo_lib:
    exec(open(KIT + "/cenarios.py").read())
    cenario_sala(noite=True, natal=True)        # sala de estar aconchegante
    ... e no finish: finish(shots, events, shake_at=f_pop, dof=(pipo, 2.8))
Regras (da pesquisa): cenario de adulto, paleta saturada mas quente, profundidade (primeiro plano,
meio e fundo), luzes pequenas no fundo viram bokeh com o desfoque, nada de cenario vazio.
"""


def _remove_estudio():
    for o in list(bpy.data.objects):
        if o.type == 'LIGHT' or (o.type == 'MESH' and o.data.materials and o.data.materials[0].name in ("floor", "wall")):
            bpy.data.objects.remove(o, do_unlink=True)


def _mat_madeira(name="madeira", c1=(0.40, 0.21, 0.10), c2=(0.33, 0.16, 0.07)):
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    br = nt.nodes.new("ShaderNodeTexBrick")
    br.inputs["Scale"].default_value = 0.8
    br.inputs["Mortar Size"].default_value = 0.008
    br.inputs["Brick Width"].default_value = 2.4; br.inputs["Row Height"].default_value = 0.22
    br.inputs["Color1"].default_value = (*c1, 1); br.inputs["Color2"].default_value = (*c2, 1)
    br.inputs["Mortar"].default_value = (0.08, 0.04, 0.02, 1)
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 6; wv.inputs["Distortion"].default_value = 8
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 0.15
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"]); nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    nt.links.new(br.outputs["Color"], mx.inputs[6]); nt.links.new(wv.outputs["Color"], mx.inputs[7])
    nt.links.new(mx.outputs[2], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.42
    return m


def _box(name, size, loc, mat, bev=0.04, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bev:
        b = o.modifiers.new("bv", 'BEVEL'); b.width = bev; b.segments = 3
    smooth(o); o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def _area(loc, tgt, energy, col, size):
    l = D.lights.new("A", 'AREA'); l.energy = energy; l.color = col; l.size = size
    o = link(D.objects.new("A", l)); o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


def _point(loc, energy, col, r=0.1):
    l = D.lights.new("P", 'POINT'); l.energy = energy; l.color = col; l.shadow_soft_size = r
    o = link(D.objects.new("P", l)); o.location = loc
    return o


def cenario_sala(noite=True, natal=True, parede=(0.05, 0.22, 0.24), sofa=(0.78, 0.48, 0.10)):
    """Sala de estar: piso de madeira, parede com papel listrado e rodape, janela com cidade a noite,
    sofa de veludo, luminaria de chao acesa, (natal) arvore decorada com pisca-pisca e varal de luzes."""
    _remove_estudio()
    w = s.world.node_tree.nodes["Background"]
    w.inputs[0].default_value = (0.02, 0.03, 0.07, 1) if noite else (0.5, 0.6, 0.8, 1)
    w.inputs[1].default_value = 0.6
    # piso
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 8, 0))
    fl = bpy.context.object; fl.data.materials.append(_mat_madeira())
    # parede de fundo com listras
    pm = D.materials.new("papel"); pm.use_nodes = True
    nt = pm.node_tree; p = nt.nodes["Principled BSDF"]
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
    wv.inputs["Scale"].default_value = 2.2; wv.inputs["Distortion"].default_value = 0
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = 'CONSTANT'
    rp.color_ramp.elements[0].color = (*parede, 1); rp.color_ramp.elements[1].position = 0.55
    rp.color_ramp.elements[1].color = (parede[0] * 1.35, parede[1] * 1.3, parede[2] * 1.3, 1)
    nt.links.new(wv.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.8
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 3.4, 5.0), rotation=(math.radians(90), 0, 0))
    wall = bpy.context.object; wall.scale = (16, 10, 1); wall.data.materials.append(pm)
    # lambri + rodape
    lam = lit("lambri", (0.93, 0.88, 0.78), 0.5, 0)
    _box("lambri", (16, 0.06, 1.0), (0, 3.36, 0.5), lam, 0.01)
    _box("moldura", (16, 0.1, 0.06), (0, 3.33, 1.02), lam, 0.02)
    # janela com cidade a noite
    jx, jz = -1.4, 2.35
    cid = D.materials.new("cidade"); cid.use_nodes = True
    nt = cid.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    sky = nt.nodes.new("ShaderNodeValToRGB")
    sky.color_ramp.elements[0].color = (0.05, 0.08, 0.25, 1); sky.color_ramp.elements[1].color = (0.01, 0.01, 0.06, 1)
    nt.links.new(sep.outputs["Y"], sky.inputs["Fac"])
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 28
    nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
    lt = nt.nodes.new("ShaderNodeMath"); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.12
    nt.links.new(vor.outputs["Distance"], lt.inputs[0])
    low = nt.nodes.new("ShaderNodeMath"); low.operation = 'LESS_THAN'; low.inputs[1].default_value = 0.45
    nt.links.new(sep.outputs["Y"], low.inputs[0])
    mm = nt.nodes.new("ShaderNodeMath"); mm.operation = 'MULTIPLY'
    nt.links.new(lt.outputs[0], mm.inputs[0]); nt.links.new(low.outputs[0], mm.inputs[1])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt.links.new(mm.outputs[0], mx.inputs[0]); nt.links.new(sky.outputs["Color"], mx.inputs[6])
    mx.inputs[7].default_value = (1.0, 0.75, 0.35, 1)
    nt.links.new(mx.outputs[2], em.inputs["Color"]); em.inputs["Strength"].default_value = 1.6
    nt.links.new(em.outputs[0], out.inputs[0])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(jx, 3.32, jz), rotation=(math.radians(90), 0, 0))
    vid = bpy.context.object; vid.scale = (1.5, 1.7, 1); vid.data.materials.append(cid)
    fr = lit("janela", (0.95, 0.93, 0.9), 0.4, 0)
    for (sx, sz, x, z) in ((1.7, 0.1, jx, jz + 0.88), (1.7, 0.1, jx, jz - 0.88), (0.1, 1.85, jx - 0.8, jz), (0.1, 1.85, jx + 0.8, jz), (0.06, 1.7, jx, jz), (1.5, 0.06, jx, jz + 0.1)):
        _box("jf", (sx, 0.12, sz), (x, 3.27, z), fr, 0.015)
    _box("peitoril", (1.9, 0.3, 0.07), (jx, 3.2, jz - 0.95), fr, 0.02)
    # sofa
    sm = lit("veludo", sofa, 0.7, 0)
    sf = empty("sofa", (1.9, 2.6, 0))
    _box("assento", (2.4, 0.9, 0.45), (0, 0, 0.32), sm, 0.12, sf)
    _box("encosto", (2.4, 0.3, 0.75), (0, 0.32, 0.8), sm, 0.12, sf)
    for sx in (-1, 1):
        _box("braco", (0.28, 0.95, 0.62), (sx * 1.15, 0, 0.42), sm, 0.12, sf)
    for sx, c in ((-0.55, (0.9, 0.3, 0.35)), (0.55, (0.2, 0.55, 0.6))):
        _box("almofada", (0.5, 0.18, 0.42), (sx, 0.12, 0.78), lit("alm", c, 0.8, 0), 0.12, sf).rotation_euler = (math.radians(-12), 0, sx * 0.3)
    # luminaria de chao (acesa)
    lx, ly = -2.7, 2.6
    met = lit("metal", (0.12, 0.1, 0.08), 0.3, 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.025, depth=1.9, location=(lx, ly, 0.95)); bpy.context.object.data.materials.append(met)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.22, depth=0.04, location=(lx, ly, 0.02)); bpy.context.object.data.materials.append(met)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.36, radius2=0.22, depth=0.38, location=(lx, ly, 1.95))
    sh = bpy.context.object; smooth(sh); sh.data.materials.append(flat("cupula", (1.0, 0.72, 0.4), 2.5))
    _point((lx, ly, 1.8), 140, (1.0, 0.7, 0.4), 0.2)
    # luz principal quente + recorte frio da janela + preenchimento
    _area((-3.0, -3.5, 4.0), (0, 0, 0.8), 520, (1.0, 0.86, 0.7), 3.0)
    _area((3.5, -4.0, 2.2), (0, 0, 0.9), 140, (0.65, 0.75, 1.0), 3.0)
    _area((0.5, 2.8, 3.8), (-0.3, -0.6, 1.0), 260, (0.55, 0.65, 1.0), 2.0)
    # tapete redondo estampado
    tm = D.materials.new("tapete"); tm.use_nodes = True
    nt = tm.node_tree; p = nt.nodes["Principled BSDF"]
    gr = nt.nodes.new("ShaderNodeTexGradient"); gr.gradient_type = 'SPHERICAL'
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], gr.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB"); rp.color_ramp.interpolation = 'CONSTANT'
    for i, (pos, c) in enumerate(((0.0, (0.55, 0.08, 0.1)), (0.2, (0.85, 0.7, 0.45)), (0.28, (0.55, 0.08, 0.1)), (0.6, (0.75, 0.2, 0.15)), (0.75, (0.85, 0.7, 0.45)))):
        el = rp.color_ramp.elements[i] if i < 2 else rp.color_ramp.elements.new(pos)
        el.position = pos; el.color = (*c, 1)
    nt.links.new(gr.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 1.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.0, depth=0.02, location=(0.1, 0.0, 0.01))
    rug = bpy.context.object; rug.scale = (2.0, 1.5, 1); rug.data.materials.append(tm)
    objs = dict(rug=rug, sofa=sf)
    if natal:
        # arvore decorada (fundo, desfocada)
        tx, ty = 3.0, 2.2
        tree = empty("arvore", (tx, ty, 0))
        verde = lit("pinheiro", (0.04, 0.22, 0.1), 0.7, 0)
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.08, depth=0.5, location=(0, 0, 0.25)); bpy.context.object.data.materials.append(lit("tronco", (0.3, 0.15, 0.05), 0.8, 0)); bpy.context.object.parent = tree
        for i, (r, h, z) in enumerate(((1.0, 1.1, 0.95), (0.8, 0.95, 1.55), (0.58, 0.85, 2.1), (0.36, 0.7, 2.55))):
            bpy.ops.mesh.primitive_cone_add(vertices=40, radius1=r, depth=h, location=(0, 0, z))
            c = bpy.context.object; smooth(c); c.data.materials.append(verde); c.parent = tree
            dsp = c.modifiers.new("d", 'DISPLACE'); tx_ = D.textures.new("pn", 'CLOUDS'); tx_.noise_scale = 0.15; dsp.texture = tx_; dsp.strength = 0.08
        random.seed(21)
        orn = [lit("bola_v", (0.85, 0.08, 0.1), 0.15, 0.8), lit("bola_d", (1.0, 0.7, 0.15), 0.15, 0.8), lit("bola_a", (0.15, 0.4, 0.9), 0.15, 0.8)]
        pis = [flat("pisca%d" % i, c, 6.0) for i, c in enumerate(((1, 0.75, 0.35), (1, 0.45, 0.3), (0.5, 0.8, 1.0)))]
        for i in range(70):
            z = random.uniform(0.6, 2.8)
            rr = max(0.12, 1.05 * (1 - (z - 0.5) / 2.6))
            a = random.uniform(0, 2 * math.pi)
            if i % 2:
                b = sphere("bola", 0.07, (math.cos(a) * rr, math.sin(a) * rr, z), 12, 6); b.data.materials.append(random.choice(orn))
            else:
                b = sphere("pisca", 0.025, (math.cos(a) * rr * 1.02, math.sin(a) * rr * 1.02, z), 8, 4); b.data.materials.append(random.choice(pis))
            b.parent = tree
        st = sphere("estrela", 0.12, (0, 0, 3.0), 12, 6); st.data.materials.append(flat("estrela", (1, 0.85, 0.4), 8)); st.parent = tree
        tree.location = (tx, ty, 0)
        objs["arvore"] = tree
        # varal de luzinhas na parede (vira bokeh)
        cols = [(1, 0.75, 0.35), (1, 0.4, 0.3), (0.5, 0.8, 1), (0.6, 1, 0.5)]
        for i in range(30):
            x = -4.0 + i * 0.28; z = 3.9 - 0.4 * math.sin(math.pi * (i % 15) / 14)
            b = sphere("luz", 0.04, (x, 3.3, z), 8, 4); b.data.materials.append(flat("varal%d" % (i % 4), cols[i % 4], 7))
    return objs
