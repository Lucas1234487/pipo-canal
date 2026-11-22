"""ep004 (O T. rex tinha ossinho da sorte, parte 2 dos dinossauros): pecas e mundos novos.
Usa mundos_ep003 (M) para o mundo das cinzas aprovado (luz e clima intocados) e para os utilitarios.
    import mundos_ep003 as M, mundos_ep004 as X
    X.furcula("furc", parent, escala)         # ossinho da sorte (2 pecas: a maior com a juncao e a quilha)
    X.carrega_rex(...) / X.carrega_galinha()   # modelos CC0 (Quaternius 2018, Kelgar) com raio-x por mascara
    X.mundo_ceia() / X.mundo_split()           # mesa de Natal a noite / tela dividida
Tudo animado vira keyframe, driver nenhum, modificador de f-curve ou parentesco a osso: o .blend renderiza sem Python.
"""
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix, Euler, Quaternion
import mundos_ep003 as M

D = bpy.data
ASSETS = os.environ.get("PIPO_ASSETS", "/home/claude/pipo-canal/assets/modelos")
TREX = ASSETS + "/quaternius_dinos_2018/Trex.blend"
GALINHA = ASSETS + "/galinha_kelgar/chickenV2.blend"
CIANO = (0.35, 0.85, 1.0)
CIANO_B = (0.75, 0.97, 1.0)


# =============================================================== utilidades
def key_val(sock, fr_vals, interp='LINEAR'):
    for fr, v in fr_vals:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=fr)


def nt_interp(nt, mode='LINEAR'):
    for fc in M.fcurves_nt(nt):
        for k in fc.keyframe_points:
            k.interpolation = mode


def obj_interp(o, mode='LINEAR', path=None):
    for fc in M.fcurves(o):
        if path is None or fc.data_path == path:
            for k in fc.keyframe_points:
                k.interpolation = mode


def set_action(arm, act):
    arm.animation_data_create()
    arm.animation_data.action = act
    try:
        arm.animation_data.action_slot = act.slots[0]
    except Exception:
        pass


def nla_track(arm, strips, name="acao"):
    """strips: [(acao, quadro_inicio, (a0, a1) do trecho da acao, escala, repeticoes)] numa trilha NLA (sem Python no render)"""
    arm.animation_data_create()
    arm.animation_data.action = None
    tr = arm.animation_data.nla_tracks.new(); tr.name = name
    for act, f0, rng, sc, rep in strips:
        st = tr.strips.new(act.name + "_%d" % f0, int(f0), act)
        try:
            st.action_slot = act.slots[0]
        except Exception:
            pass
        st.action_frame_start, st.action_frame_end = rng
        st.scale = sc; st.repeat = rep
        st.extrapolation = 'HOLD_FORWARD'
        st.blend_in = st.blend_out = 0
        st.use_auto_blend = False
    return tr


def append_objs(path, skip=()):
    with D.libraries.load(path) as (a, b):
        b.objects = [n for n in a.objects if n not in skip]
        b.actions = list(a.actions)
    out = {}
    for o in b.objects:
        if o is None or o.type not in ("ARMATURE", "MESH"):
            continue
        M.link(o)
        out[o.name.split(".")[0]] = o
    return out


# =============================================================== FURCULA (ossinho da sorte)
def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    return p0 * u ** 3 + p1 * 3 * u * u * t + p2 * 3 * u * t * t + p3 * t ** 3


def _arm_path(t, side):
    """braco direito (side=+1) ou esquerdo (-1): t=0 na juncao, t=1 na ponta. Unidade: altura 1."""
    p = _bez(Vector((0, 0, 0)), Vector((0.13, 0, 0.0)), Vector((0.29, 0, 0.36)), Vector((0.35, 0, 1.0)), t)
    p.x = (p.x + 0.05 * t ** 4) * side                              # pontas abrem um pouco para fora
    p.y = -0.09 * math.sin(math.pi * t) - 0.05 * t ** 3          # arco para a frente (-Y), pontas viradas para a frente
    return p


def _radii(t):
    """(raio no plano do V, raio em profundidade): mais grosso na juncao, fino no meio, ponta achatada em paleta"""
    a = 0.052 - 0.028 * min(1, t / 0.5) ** 0.7 + 0.007 * max(0.0, 1 - t / 0.14)
    b = 0.046 - 0.019 * min(1, t / 0.5) + 0.006 * max(0.0, 1 - t / 0.14)
    if t > 0.8:
        k = (t - 0.8) / 0.2
        a += 0.020 * math.sin(k * math.pi * 0.5)
        b -= 0.009 * k
    return a, b


def _sweep(bm, pts, radii, nseg=14, cap0=True, cap1=True, jag0=0.0, jag1=0.0, seed=0, plane_n=Vector((0, 1, 0))):
    """tubo de secao eliptica ao longo de pts (raios (a,b) por ponto), com tampas arredondadas ou lascadas"""
    random.seed(seed)
    n = len(pts)
    rings = []

    def frame(i):
        t = (pts[min(n - 1, i + 1)] - pts[max(0, i - 1)]).normalized()
        nb = plane_n - t * plane_n.dot(t)
        nb = nb.normalized() if nb.length > 1e-6 else Vector((0, 0, 1))
        na = t.cross(nb).normalized()
        return t, na, nb

    def ring(c, t, na, nb, a, b, jag=0.0):
        vs = []
        for k in range(nseg):
            ang = 2 * math.pi * k / nseg
            off = na * math.cos(ang) * a + nb * math.sin(ang) * b
            if jag:
                off = off + t * random.uniform(-jag, jag)
            vs.append(bm.verts.new(c + off))
        return vs
    # tampa inicial
    t0, na0, nb0 = frame(0)
    a0, b0 = radii[0]
    if cap0:
        for k, u in enumerate((0.92, 0.7, 0.4)):
            s_ = math.sqrt(max(0.0, 1 - u * u))
            rings.append(ring(pts[0] - t0 * a0 * u * 0.9, t0, na0, nb0, a0 * s_, b0 * s_))
    for i in range(n):
        t, na, nb = frame(i)
        a, b = radii[i]
        jag = jag0 if (i == 0 and not cap0) else (jag1 if (i == n - 1 and not cap1) else 0.0)
        rings.append(ring(pts[i], t, na, nb, a, b, jag))
    t1, na1, nb1 = frame(n - 1)
    a1, b1 = radii[-1]
    if cap1:
        for u in (0.4, 0.7, 0.92):
            s_ = math.sqrt(max(0.0, 1 - u * u))
            rings.append(ring(pts[-1] + t1 * a1 * u * 0.9, t1, na1, nb1, a1 * s_, b1 * s_))
    for r0, r1 in zip(rings[:-1], rings[1:]):
        for k in range(nseg):
            bm.faces.new((r0[k], r0[(k + 1) % nseg], r1[(k + 1) % nseg], r1[k]))
    # fecha as pontas com um leque (ponto central)
    for rr, end, sign in ((rings[0], pts[0] - t0 * a0 * (0.98 if cap0 else 0.0), -1), (rings[-1], pts[-1] + t1 * a1 * (0.98 if cap1 else 0.0), 1)):
        c = bm.verts.new(end)
        for k in range(nseg):
            if sign < 0:
                bm.faces.new((rr[(k + 1) % nseg], rr[k], c))
            else:
                bm.faces.new((rr[k], rr[(k + 1) % nseg], c))
    return bm


def furcula_meshes(name, s_cut=0.2, nseg=14):
    """duas malhas no mesmo espaco (origem na juncao, V no plano XZ, frente -Y):
    maior = braco esquerdo + juncao + quilha (hipocleideo) + toco do direito; menor = resto do braco direito.
    Juntas, formam o ossinho inteiro (a costura fica escondida na sobreposicao)."""
    st = 48
    # maior: s de -1 (ponta esquerda) ate +s_cut
    pts, rad = [], []
    for i in range(st + 1):
        t = 1 - i / st
        pts.append(_arm_path(t, -1)); rad.append(_radii(t))
    nr = max(3, int(st * s_cut * 2.5))
    for i in range(1, nr + 1):
        t = s_cut * i / nr
        a, b = _radii(t)
        k = 1.0 - 0.07 * max(0.0, (t - (s_cut - 0.02)) / 0.02)        # termina afinando por dentro da peca menor
        pts.append(_arm_path(t, 1)); rad.append((a * k, b * k))
    bm = bmesh.new()
    _sweep(bm, pts, rad, nseg, cap0=True, cap1=False, jag1=0.006, seed=3)
    # quilha (hipocleideo): lamina fina para baixo e para tras
    kp = [Vector((0, -0.004, 0.045)), Vector((0, 0.004, -0.01)), Vector((0, 0.018, -0.065)), Vector((0, 0.036, -0.11)), Vector((0, 0.058, -0.145))]
    kr = [(0.040, 0.030), (0.040, 0.019), (0.033, 0.013), (0.022, 0.010), (0.011, 0.006)]
    _sweep(bm, kp, kr, 12, cap0=False, cap1=True, plane_n=Vector((0, 1, 0)))
    me_a = D.meshes.new(name + "_maior"); bm.to_mesh(me_a); bm.free()
    # menor: de s_cut - 0.02 (sobrepoe) ate a ponta direita
    pts, rad = [], []
    t0 = max(0.0, s_cut - 0.025)
    for i in range(st + 1):
        t = t0 + (1 - t0) * (i / st) ** 1.35
        a, b = _radii(t)
        k = 0.93 + 0.07 * min(1.0, max(0.0, (t - (s_cut - 0.012)) / 0.024))
        pts.append(_arm_path(t, 1)); rad.append((a * k, b * k))
    bm = bmesh.new()
    _sweep(bm, pts, rad, nseg, cap0=False, cap1=True, jag0=0.006, seed=5)
    me_b = D.meshes.new(name + "_menor"); bm.to_mesh(me_b); bm.free()
    # inteira (sem costura): ponta esquerda -> juncao -> ponta direita + quilha
    pts, rad = [], []
    for i in range(st + 1):
        t = 1 - i / st
        pts.append(_arm_path(t, -1)); rad.append(_radii(t))
    for i in range(1, st + 1):
        t = i / st
        pts.append(_arm_path(t, 1)); rad.append(_radii(t))
    bm = bmesh.new()
    _sweep(bm, pts, rad, nseg, cap0=True, cap1=True)
    _sweep(bm, kp, kr, 12, cap0=False, cap1=True, plane_n=Vector((0, 1, 0)))
    me_c = D.meshes.new(name + "_inteira"); bm.to_mesh(me_c); bm.free()
    for me in (me_a, me_b, me_c):
        for p in me.polygons:
            p.use_smooth = True
    return me_a, me_b, me_c


def furcula_mat(name, glow=1.0, ivory=0.0):
    """um material para as duas pecas: brilho de raio-x (ciano-branco, borda ciano) <-> osso marfim de verdade.
    Sockets animaveis: GLOW (0..1 mistura), EL / ER (forca do brilho de cada clavicula: lado -X / +X do objeto)"""
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; M._clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    # osso marfim: cor com veios suaves, poros finos, leve subsuperficie e brilho umido
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9; nz.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].position = 0.3; rp.color_ramp.elements[0].color = (0.78, 0.66, 0.46, 1)
    rp.color_ramp.elements[1].position = 0.75; rp.color_ramp.elements[1].color = (0.93, 0.86, 0.70, 1)
    nt.links.new(nz.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.38
    try:
        p.inputs["Subsurface Weight"].default_value = 0.25
        p.inputs["Subsurface Radius"].default_value = (0.02, 0.012, 0.008)
        p.inputs["Subsurface Scale"].default_value = 0.05
        p.inputs["Specular IOR Level"].default_value = 0.6
        p.inputs["Coat Weight"].default_value = 0.15
    except Exception:
        pass
    pn = nt.nodes.new("ShaderNodeTexNoise"); pn.inputs["Scale"].default_value = 120; pn.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], pn.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12; bp.inputs["Distance"].default_value = 0.01
    nt.links.new(pn.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    # brilho: miolo branco-ciano, borda ciano forte (layer weight)
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
    mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = 'RGBA'
    nt.links.new(lw.outputs["Facing"], mc.inputs[0]); mc.inputs[6].default_value = (*CIANO_B, 1); mc.inputs[7].default_value = (*CIANO, 1)
    em = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mc.outputs[2], em.inputs["Color"])
    # forca por lado (clavicula esquerda/direita) no espaco do objeto
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    sd = nt.nodes.new("ShaderNodeMapRange"); sd.inputs["From Min"].default_value = -0.03; sd.inputs["From Max"].default_value = 0.03
    nt.links.new(sp.outputs["X"], sd.inputs["Value"])
    el = nt.nodes.new("ShaderNodeValue"); el.name = "EL"; el.outputs[0].default_value = 8.0
    er = nt.nodes.new("ShaderNodeValue"); er.name = "ER"; er.outputs[0].default_value = 8.0
    ms = nt.nodes.new("ShaderNodeMix"); ms.data_type = 'FLOAT'
    nt.links.new(sd.outputs["Result"], ms.inputs[0]); nt.links.new(el.outputs[0], ms.inputs[2]); nt.links.new(er.outputs[0], ms.inputs[3])
    # borda mais forte que o miolo
    rim = nt.nodes.new("ShaderNodeMath"); rim.operation = 'MULTIPLY_ADD'; rim.inputs[1].default_value = 1.2; rim.inputs[2].default_value = 0.6
    nt.links.new(lw.outputs["Facing"], rim.inputs[0])
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'
    nt.links.new(ms.outputs[0], mu.inputs[0]); nt.links.new(rim.outputs[0], mu.inputs[1])
    nt.links.new(mu.outputs[0], em.inputs["Strength"])
    # brilho por cima do osso (o osso aparece por baixo quando GLOW cai)
    gv = nt.nodes.new("ShaderNodeValue"); gv.name = "GLOW"; gv.outputs[0].default_value = glow
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.name = "MIX"
    nt.links.new(gv.outputs[0], mix.inputs[0]); nt.links.new(p.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    # EXTRA: a mesma emissao somada por cima do osso (claviculas acendendo sobre o marfim)
    ex = nt.nodes.new("ShaderNodeValue"); ex.name = "EXTRA"; ex.outputs[0].default_value = 0.0
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = 'MULTIPLY'
    nt.links.new(mu.outputs[0], m2.inputs[0]); nt.links.new(ex.outputs[0], m2.inputs[1])
    em2 = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mc.outputs[2], em2.inputs["Color"]); nt.links.new(m2.outputs[0], em2.inputs["Strength"])
    ad = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(mix.outputs[0], ad.inputs[0]); nt.links.new(em2.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs[0])
    return m


def fsock(m, name):
    return m.node_tree.nodes[name].outputs[0]


def furcula(name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), size=1.0, mat=None, sub=2):
    """ossinho completo: raiz (empty na juncao) + peca maior + peca menor. size = altura total (m)"""
    root = M.empty(name, loc, parent, rot)
    root.scale = (size,) * 3
    piv = M.empty(name + "_giro", (0, 0, 0.4), root)            # giro em volta do meio do osso
    ma, mb, mc = furcula_meshes(name)
    mat = mat or furcula_mat(name + "_mat")
    pcs = []
    for me, nm in ((ma, "_maior"), (mb, "_menor"), (mc, "_inteira")):
        o = M.link(D.objects.new(name + nm, me))
        o.parent = piv; o.location = (0, 0, -0.4)
        me.materials.append(mat)
        sd = o.modifiers.new("sub", 'SUBSURF'); sd.levels = 1; sd.render_levels = sub
        o.visible_shadow = False
        pcs.append(o)
    for o in pcs[:2]:          # as pecas so aparecem quando o osso quebra (ver quebra())
        o.hide_render = True
    return dict(root=root, giro=piv, maior=pcs[0], menor=pcs[1], inteira=pcs[2], mat=mat, objs=pcs)


# =============================================================== halo (brilho barato atras do osso)
def halo_add_mat(name, col, strength, power=2.2):
    """disco de brilho aditivo: transparente + emissao com queda radial (forca 0 = some de verdade)"""
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; M._clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'; nt.links.new(tc.outputs["Object"], ln.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Max"].default_value = 1.0; mr.inputs["To Min"].default_value = 1; mr.inputs["To Max"].default_value = 0
    nt.links.new(ln.outputs["Value"], mr.inputs["Value"])
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = power
    nt.links.new(mr.outputs["Result"], pw.inputs[0])
    sv = nt.nodes.new("ShaderNodeValue"); sv.name = "FORCA"; sv.outputs[0].default_value = strength
    mu = nt.nodes.new("ShaderNodeMath"); mu.operation = 'MULTIPLY'; nt.links.new(pw.outputs[0], mu.inputs[0]); nt.links.new(sv.outputs[0], mu.inputs[1])
    e = nt.nodes.new("ShaderNodeEmission"); e.name = "Emission"; e.inputs["Color"].default_value = (*col, 1)
    nt.links.new(mu.outputs[0], e.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    ad = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(tr.outputs[0], ad.inputs[0]); nt.links.new(e.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs[0])
    return m


def halo(name, parent, loc, r, col=CIANO, strength=0.6, power=2.2):
    hm = halo_add_mat(name + "_m", col, strength, power=power)
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1, fill_type='NGON', location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    h = bpy.context.object; h.name = name; M.setmat(h, hm); h.parent = parent; h.location = loc; h.scale = (r, r, 1)
    h.rotation_euler = (math.radians(90), 0, 0)
    h.visible_shadow = False; h.visible_diffuse = False; h.visible_glossy = False
    return h, hm.node_tree.nodes["FORCA"].outputs[0]


# =============================================================== RAIO-X por mascara (sem Python no render)
def xray_group(name, mask_obj, line_col=CIANO_B):
    """grupo de nos: mascara elipsoidal no espaco do empty mask_obj (escala = raios) + faixa que varre de +Z para -Z.
    Valores animaveis dentro do grupo: BAND (posicao da faixa em z local), ON (0..1), LINE (forca da linha), SIL (contraluz)"""
    g = D.node_groups.new(name, "ShaderNodeTree")
    g.interface.new_socket("Fac", in_out='OUTPUT', socket_type='NodeSocketFloat')
    g.interface.new_socket("Line", in_out='OUTPUT', socket_type='NodeSocketFloat')
    g.interface.new_socket("Sil", in_out='OUTPUT', socket_type='NodeSocketFloat')
    nt = g
    go = nt.nodes.new("NodeGroupOutput")
    tc = nt.nodes.new("ShaderNodeTexCoord"); tc.object = mask_obj
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'; nt.links.new(tc.outputs["Object"], ln.inputs[0])
    ins = nt.nodes.new("ShaderNodeMapRange"); ins.inputs["From Min"].default_value = 0.6; ins.inputs["From Max"].default_value = 1.0
    ins.inputs["To Min"].default_value = 1.0; ins.inputs["To Max"].default_value = 0.0
    nt.links.new(ln.outputs["Value"], ins.inputs["Value"])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    vals = {}
    for nm, v in (("BAND", 1.5), ("ON", 0.0), ("LINE", 0.0), ("SIL", 0.0)):
        n = nt.nodes.new("ShaderNodeValue"); n.name = nm; n.label = nm; n.outputs[0].default_value = v; vals[nm] = n
    dz = nt.nodes.new("ShaderNodeMath"); dz.operation = 'SUBTRACT'
    nt.links.new(sp.outputs["Z"], dz.inputs[0]); nt.links.new(vals["BAND"].outputs[0], dz.inputs[1])
    ps = nt.nodes.new("ShaderNodeMath"); ps.operation = 'MULTIPLY_ADD'; ps.use_clamp = True; ps.inputs[1].default_value = 14.0; ps.inputs[2].default_value = 0.5
    nt.links.new(dz.outputs[0], ps.inputs[0])
    m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = 'MULTIPLY'; nt.links.new(ins.outputs["Result"], m1.inputs[0]); nt.links.new(ps.outputs[0], m1.inputs[1])
    m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = 'MULTIPLY'; nt.links.new(m1.outputs[0], m2.inputs[0]); nt.links.new(vals["ON"].outputs[0], m2.inputs[1])
    nt.links.new(m2.outputs[0], go.inputs["Fac"])
    # linha de varredura: gaussiana em z, um pouco alem da mascara
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'; nt.links.new(dz.outputs[0], ab.inputs[0])
    lr = nt.nodes.new("ShaderNodeMapRange"); lr.inputs["From Min"].default_value = 0.0; lr.inputs["From Max"].default_value = 0.07
    lr.inputs["To Min"].default_value = 1.0; lr.inputs["To Max"].default_value = 0.0
    nt.links.new(ab.outputs[0], lr.inputs["Value"])
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.0; nt.links.new(lr.outputs["Result"], pw.inputs[0])
    ie = nt.nodes.new("ShaderNodeMapRange"); ie.inputs["From Min"].default_value = 1.0; ie.inputs["From Max"].default_value = 1.25
    ie.inputs["To Min"].default_value = 1.0; ie.inputs["To Max"].default_value = 0.0
    nt.links.new(ln.outputs["Value"], ie.inputs["Value"])
    l1 = nt.nodes.new("ShaderNodeMath"); l1.operation = 'MULTIPLY'; nt.links.new(pw.outputs[0], l1.inputs[0]); nt.links.new(ie.outputs["Result"], l1.inputs[1])
    l2 = nt.nodes.new("ShaderNodeMath"); l2.operation = 'MULTIPLY'; nt.links.new(l1.outputs[0], l2.inputs[0]); nt.links.new(vals["LINE"].outputs[0], l2.inputs[1])
    nt.links.new(l2.outputs[0], go.inputs["Line"])
    nt.links.new(vals["SIL"].outputs[0], go.inputs["Sil"])
    return g


def gsock(g, name):
    return g.nodes[name].outputs[0]


def xray_wrap(m, grp, xs=1.0, rim_col=(1.0, 0.45, 0.2), rim=4.0, line_col=CIANO_B):
    """envolve a saida do material: (original | raio-x translucido) pela mascara + linha de varredura + contraluz"""
    nt = m.node_tree
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output] or [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL']
    out = out[0]
    for n in nt.nodes:
        if n.type == 'OUTPUT_MATERIAL' and n != out:
            nt.nodes.remove(n)
    src = out.inputs["Surface"].links[0].from_socket
    gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = grp
    # raio-x: borda ciano emissiva, miolo transparente
    lw2 = nt.nodes.new("ShaderNodeLayerWeight"); lw2.inputs["Blend"].default_value = 0.45
    p2 = nt.nodes.new("ShaderNodeMath"); p2.operation = 'POWER'; p2.inputs[1].default_value = 1.6
    nt.links.new(lw2.outputs["Facing"], p2.inputs[0])
    e2 = nt.nodes.new("ShaderNodeEmission"); e2.inputs["Color"].default_value = (*CIANO, 1)
    s2 = nt.nodes.new("ShaderNodeMath"); s2.operation = 'MULTIPLY_ADD'; s2.inputs[1].default_value = 3.0 * xs; s2.inputs[2].default_value = 0.06 * xs
    nt.links.new(p2.outputs[0], s2.inputs[0]); nt.links.new(s2.outputs[0], e2.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    a2 = nt.nodes.new("ShaderNodeMath"); a2.operation = 'MULTIPLY_ADD'; a2.inputs[1].default_value = 0.7; a2.inputs[2].default_value = 0.1
    nt.links.new(p2.outputs[0], a2.inputs[0])
    mx2 = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(a2.outputs[0], mx2.inputs[0]); nt.links.new(tr.outputs[0], mx2.inputs[1]); nt.links.new(e2.outputs[0], mx2.inputs[2])
    mx = nt.nodes.new("ShaderNodeMixShader")
    # so os raios de camera veem o raio-x; sombra e luz indireta veem o corpo opaco (render bem mais barato, mesma imagem)
    lp = nt.nodes.new("ShaderNodeLightPath")
    fc = nt.nodes.new("ShaderNodeMath"); fc.operation = 'MULTIPLY'
    nt.links.new(gn.outputs["Fac"], fc.inputs[0]); nt.links.new(lp.outputs["Is Camera Ray"], fc.inputs[1])
    nt.links.new(fc.outputs[0], mx.inputs[0]); nt.links.new(src, mx.inputs[1]); nt.links.new(mx2.outputs[0], mx.inputs[2])
    # linha
    le = nt.nodes.new("ShaderNodeEmission"); le.inputs["Color"].default_value = (*line_col, 1)
    lm = nt.nodes.new("ShaderNodeMath"); lm.operation = 'MULTIPLY'; lm.inputs[1].default_value = 25.0
    nt.links.new(gn.outputs["Line"], lm.inputs[0]); nt.links.new(lm.outputs[0], le.inputs["Strength"])
    ad = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(mx.outputs[0], ad.inputs[0]); nt.links.new(le.outputs[0], ad.inputs[1])
    # contraluz (silhueta escura com borda laranja)
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.25
    pw = nt.nodes.new("ShaderNodeMath"); pw.operation = 'POWER'; pw.inputs[1].default_value = 3.0
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = 'RGBA'
    nt.links.new(pw.outputs[0], mc.inputs[0]); mc.inputs[6].default_value = (0.010, 0.005, 0.012, 1); mc.inputs[7].default_value = (*rim_col, 1)
    es = nt.nodes.new("ShaderNodeEmission"); nt.links.new(mc.outputs[2], es.inputs["Color"])
    ml = nt.nodes.new("ShaderNodeMath"); ml.operation = 'MULTIPLY_ADD'; ml.inputs[1].default_value = rim; ml.inputs[2].default_value = 1.0
    nt.links.new(pw.outputs[0], ml.inputs[0]); nt.links.new(ml.outputs[0], es.inputs["Strength"])
    fin = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(gn.outputs["Sil"], fin.inputs[0]); nt.links.new(ad.outputs[0], fin.inputs[1]); nt.links.new(es.outputs[0], fin.inputs[2])
    nt.links.new(fin.outputs[0], out.inputs["Surface"])
    return m


# =============================================================== T. REX (Quaternius 2018, CC0)
def rex_mats():
    """os PBR do ep003 (mesmos parametros do M.trex); cria se o mundo ainda nao tiver"""
    g = D.materials.get
    pele = g("rex_pele") or M.pbr("rex_pele", (0.035, 0.03, 0.022), (0.16, 0.07, 0.03), (0.3, 0.13, 0.04), rough=0.5, nscale=3.5,
                                   vor_bump=0.9, vor_scale=26, nbump=0.6, nbscale=7, spec=0.6)
    boca = g("rex_boca") or M.pbr("rex_boca", (0.32, 0.04, 0.04), (0.18, 0.02, 0.025), rough=0.25, nscale=8, nbump=0.3, nbscale=20, spec=0.8)
    dentes = g("rex_dentes") or M.pbr("rex_dentes", (0.78, 0.68, 0.48), (0.55, 0.42, 0.25), rough=0.35, nscale=12, nbump=0.15, nbscale=40, spec=0.7)
    garra = g("rex_garra") or M.pbr("rex_garra", (0.08, 0.07, 0.06), rough=0.3)
    barriga = g("rex_barriga") or M.pbr("rex_barriga", (0.16, 0.12, 0.08), (0.3, 0.22, 0.14), rough=0.6, nscale=5, vor_bump=0.6, vor_scale=30, nbump=0.4, nbscale=9)
    return {"Green": pele, "LightGreen": barriga, "Black": garra, "Red": boca, "LightYellow": dentes}


def carrega_rex(name="qrex", loc=(0, 0.5, 0), rotz=0.0, scale=0.42, xray=True, mask_bone="Shoulders"):
    """T. rex Quaternius (o do teste aprovado): escala 0.42, materiais PBR do ep003, shade smooth + Subsurf 1.
    Raio-x: cada material ganha a mascara do grupo XM_<name> (empty 'mask' preso ao osso do peito)."""
    R = append_objs(TREX)
    arm, mesh = R["Armature"], R["Trex"]
    arm.name = name + "_arm"; mesh.name = name + "_malha"
    root = M.empty(name, loc, rot=(0, 0, rotz)); root.scale = (scale,) * 3
    arm.parent = root
    mp = rex_mats()
    mats = {}
    for i, m in enumerate(mesh.data.materials):
        key = m.name.split(".")[0] if m else None
        if key in mp:
            if key not in mats:
                mats[key] = mp[key].copy(); mats[key].name = name + "_" + mp[key].name
            mesh.data.materials[i] = mats[key]
    for p in mesh.data.polygons:
        p.use_smooth = True
    sm = mesh.modifiers.new("sub", "SUBSURF"); sm.levels = sm.render_levels = 1
    d = dict(root=root, arm=arm, mesh=mesh, mats=mats, acts={a.name: a for a in D.actions if a.name.startswith("TRex_")})
    if xray:
        mk = M.empty(name + "_mask", (0, 0, 0))
        mk.parent = arm; mk.parent_type = 'BONE'; mk.parent_bone = mask_bone
        grp = xray_group("XM_" + name, mk)
        for k, m in mats.items():
            xray_wrap(m, grp, xs=1.0)
        d.update(mask=mk, grp=grp)
    return d


def bone_world(arm, bone):
    pb = arm.pose.bones[bone]
    return arm.matrix_world @ pb.head, arm.matrix_world @ pb.tail, arm.matrix_world @ pb.matrix


def prende_no_osso(o, arm, bone, world_matrix):
    """parenta o a um osso mantendo a matriz de mundo do quadro atual"""
    bpy.context.view_layer.update()
    o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = bone
    o.matrix_parent_inverse = Matrix.Identity(4)
    bpy.context.view_layer.update()
    o.matrix_world = world_matrix
    bpy.context.view_layer.update()


# =============================================================== GALINHA (Kelgar, CC0)
def galinha_mat(name, img, nimg):
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img
    hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = 1.15; hs.inputs["Value"].default_value = 1.1
    nt.links.new(t.outputs[0], hs.inputs["Color"]); nt.links.new(hs.outputs[0], p.inputs["Base Color"])
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = nimg; nimg.colorspace_settings.name = 'Non-Color'
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8
    nt.links.new(tn.outputs[0], nm.inputs["Color"]); nt.links.new(nm.outputs[0], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.75
    try:
        p.inputs["Sheen Weight"].default_value = 0.35; p.inputs["Sheen Roughness"].default_value = 0.4
    except Exception:
        pass
    return m


def carrega_galinha(name="gal", loc=(0, 0, 0), rotz=0.0, height=0.45, xray=True, mask_bone="Backbone"):
    """galinha Kelgar (altura ~45 cm), textura de foto + normal map. O 'Cylinder' do arquivo (malha de escultura escondida) fica de fora."""
    G = append_objs(GALINHA, skip=("Cylinder", "Camera", "Hemi", "Lamp"))
    arm = G["Armature"]; body = G["Chicken"]; eyes = G.get("Eyes")
    arm.name = name + "_arm"; body.name = name + "_malha"
    sc = height / 12.65
    root = M.empty(name, loc, rot=(0, 0, rotz)); root.scale = (sc,) * 3
    arm.parent = root
    tdir = os.path.dirname(GALINHA) + "/textures/"
    img = D.images.load(tdir + "UV-Texture.png", check_existing=True)
    nimg = D.images.load(tdir + "ChickenNorm.png", check_existing=True)
    m = galinha_mat(name + "_pele", img, nimg)
    for i in range(len(body.data.materials)):
        body.data.materials[i] = m
    for p in body.data.polygons:
        p.use_smooth = True
    d = dict(root=root, arm=arm, mesh=body, eyes=eyes, mat=m, scale=sc,
             acts={a.name: a for a in D.actions if a.name in ("Idle", "Idle1", "Idle2", "Pecking1", "Pecking2", "Walk", "Stand", "Eating", "BeginPecking")})
    if xray:
        mk = M.empty(name + "_mask", (0, 0, 0))
        mk.parent = arm; mk.parent_type = 'BONE'; mk.parent_bone = mask_bone
        grp = xray_group("XM_" + name, mk)
        xray_wrap(m, grp, xs=0.6)
        if eyes:
            for i, em in enumerate(eyes.data.materials):
                if em:
                    em2 = em.copy(); eyes.data.materials[i] = em2
                    if em2.node_tree and any(n.type == 'OUTPUT_MATERIAL' and n.inputs["Surface"].links for n in em2.node_tree.nodes):
                        xray_wrap(em2, grp, xs=0.6)
        d.update(mask=mk, grp=grp)
    return d


# =============================================================== CARD do comentario e CARIMBO
FONT = os.environ.get("PIPO_KIT", "/home/claude/pipo-canal/kit") + "/Fredoka-700.ttf"


def flat_mat(name, col, strength=1.0):
    """cor de interface (nao depende da luz da cena)"""
    m = D.materials.new(name); m.use_nodes = True
    nt = m.node_tree; M._clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (*col, 1); e.inputs["Strength"].default_value = strength
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


def txt(body, size, mat, loc, parent, align='LEFT', extrude=0.0, bevel=0.0):
    cu = D.curves.new("txt", 'FONT')
    cu.body = body; cu.font = D.fonts.load(FONT, check_existing=True)
    cu.size = size; cu.extrude = extrude; cu.bevel_depth = bevel; cu.bevel_resolution = 2
    cu.align_x = align; cu.align_y = 'CENTER'
    o = M.link(D.objects.new("txt_" + body[:12], cu))
    cu.materials.append(mat)
    o.parent = parent; o.location = loc
    return o


def round_rect(name, w, h, r, mat, parent, loc=(0, 0, 0), depth=0.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    o = bpy.context.object; o.name = name; o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new("bv", 'BEVEL'); bv.affect = 'VERTICES'; bv.width = r; bv.segments = 8
    if depth:
        so = o.modifiers.new("so", 'SOLIDIFY'); so.thickness = depth
    M.setmat(o, mat); o.parent = parent; o.location = loc
    return o


def card_comentario(parent=None):
    """card 3D de comentario no estilo do YouTube (modo escuro). Unidade: largura 1.0. Frente para +Z (camera)."""
    root = M.empty("card", (0, 0, 0), parent)
    bg = flat_mat("card_fundo", (0.075, 0.075, 0.085), 1.0)
    borda = flat_mat("card_borda", (0.22, 0.22, 0.25), 1.0)
    round_rect("card_borda", 1.012, 0.392, 0.062, borda, root, (0, 0, -0.004))
    round_rect("card_fundo", 1.0, 0.38, 0.056, bg, root, (0, 0, 0))
    # avatar: circulo laranja com N
    av = flat_mat("card_avatar", (0.95, 0.42, 0.08), 1.0)
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=0.072, fill_type='NGON', location=(0, 0, 0))
    a = bpy.context.object; a.name = "card_avatar"; M.setmat(a, av); a.parent = root; a.location = (-0.39, 0.065, 0.003)
    branco = flat_mat("card_branco", (0.95, 0.95, 0.95), 1.0)
    cinza = flat_mat("card_cinza", (0.62, 0.62, 0.65), 1.0)
    letra = txt("N", 0.09, branco, (-0.39, 0.062, 0.006), root, align='CENTER')
    nome = txt("@Niko_com_k", 0.072, branco, (-0.295, 0.088, 0.004), root)
    quando = txt("há 1 dia", 0.055, cinza, (0.215, 0.086, 0.004), root)
    texto = txt("A galinha eu acho", 0.105, branco, (-0.295, -0.055, 0.004), root)
    # curtir (polegar estilizado) + contagem
    return dict(root=root, avatar=a, textos=[letra, nome, quando, texto])


def carimbo(texto="ACERTOU!", parent=None):
    """carimbo verde: texto 3D com chanfro + moldura arredondada (tudo verde, com brilho proprio)"""
    root = M.empty("carimbo", (0, 0, 0), parent)
    vm = D.materials.new("carimbo_verde"); vm.use_nodes = True
    p = vm.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.1, 0.85, 0.25, 1); p.inputs["Roughness"].default_value = 0.35
    p.inputs["Emission Color"].default_value = (0.15, 1.0, 0.3, 1); p.inputs["Emission Strength"].default_value = 2.2
    t = txt(texto, 0.2, vm, (0, -0.005, 0.01), root, align='CENTER', extrude=0.025, bevel=0.006)
    # moldura: retangulo arredondado vazado (anel)
    fm = vm
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.object; o.name = "carimbo_moldura"; o.scale = (1.08, 0.32, 1)
    bpy.ops.object.transform_apply(scale=True)
    bv = o.modifiers.new("bv", 'BEVEL'); bv.affect = 'VERTICES'; bv.width = 0.07; bv.segments = 8
    wf = o.modifiers.new("wf", 'WIREFRAME'); wf.thickness = 0.03; wf.use_even_offset = True
    M.setmat(o, fm); o.parent = root
    return dict(root=root, texto=t, moldura=o)


# =============================================================== CEIA DE NATAL (mesa a noite)
MESA_Z = 0.76


def _toalha_mat():
    """toalha vermelha de natal com adamascado discreto (ruido + ondas) e trama fina"""
    m = D.materials.new("toalha"); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wv = nt.nodes.new("ShaderNodeTexNoise"); wv.inputs["Scale"].default_value = 14; wv.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].position = 0.3; rp.color_ramp.elements[0].color = (0.075, 0.003, 0.006, 1)
    rp.color_ramp.elements[1].position = 0.7; rp.color_ramp.elements[1].color = (0.12, 0.008, 0.012, 1)
    nt.links.new(wv.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.8
    br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 260; br.inputs["Mortar Size"].default_value = 0.2
    nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15
    nt.links.new(br.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    return m


def _metal_mat(name, col, rough=0.25):
    m = D.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*col, 1); p.inputs["Metallic"].default_value = 1.0; p.inputs["Roughness"].default_value = rough
    return m


def _porcelana_mat():
    m = D.materials.new("porcelana"); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (0.92, 0.9, 0.86, 1); p.inputs["Roughness"].default_value = 0.12
    try:
        p.inputs["Coat Weight"].default_value = 0.6
    except Exception:
        pass
    return m


def _vidro_mat():
    """vidro barato: transparente + reflexo (sem refracao, sem custo de transmissao)"""
    m = D.materials.new("vidro"); m.use_nodes = True
    nt = m.node_tree; M._clear(nt)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = (0.95, 0.97, 1.0, 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.05
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.2
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Fresnel"], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return m


def lathe(name, prof, m, segs=48, loc=(0, 0, 0), parent=None, smooth_=True):
    """solido de revolucao: prof = [(raio, z)] de baixo para cima"""
    bm = bmesh.new()
    rings = []
    for r, z in prof:
        ring = [bm.verts.new((r * math.cos(2 * math.pi * k / segs), r * math.sin(2 * math.pi * k / segs), z)) for k in range(segs)]
        rings.append(ring)
    for a, b in zip(rings[:-1], rings[1:]):
        for k in range(segs):
            bm.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
    me = D.meshes.new(name); bm.to_mesh(me); bm.free()
    o = M.link(D.objects.new(name, me))
    o.location = loc
    if parent:
        o.parent = parent
    if smooth_:
        for p in me.polygons:
            p.use_smooth = True
    me.materials.append(m)
    return o


def prato(name, loc, r=0.13, m=None, borda=None, parent=None):
    m = m or D.materials.get("porcelana") or _porcelana_mat()
    prof = [(0.0, 0.0), (r * 0.55, 0.0), (r * 0.62, 0.004), (r * 0.66, 0.012), (r * 0.9, 0.02), (r, 0.024), (r * 1.005, 0.021), (r * 0.93, 0.014), (r * 0.66, 0.006), (r * 0.6, 0.009), (0.0, 0.009)]
    o = lathe(name, prof, m, 64, loc, parent)
    if borda:
        rim = lathe(name + "_ouro", [(r * 0.94, 0.0215), (r * 0.975, 0.0235), (r * 0.99, 0.0245)], borda, 64, (0, 0, 0), o)
        rim.location = (0, 0, 0.0005)
    return o


def taca(name, loc, m, parent=None):
    prof = [(0.0, 0.0), (0.035, 0.0), (0.036, 0.003), (0.006, 0.008), (0.004, 0.09), (0.008, 0.1), (0.03, 0.12), (0.042, 0.16), (0.04, 0.2), (0.038, 0.21),
            (0.036, 0.208), (0.037, 0.16), (0.027, 0.122), (0.0, 0.112)]
    return lathe(name, prof, m, 32, loc, parent)


def vela(name, loc, h=0.24, r=0.016, col=(0.65, 0.02, 0.03), suporte=None, seed=0):
    """vela com chama (gota emissiva que treme) e luz que oscila com ela"""
    root = M.empty(name, loc)
    cm = M.pbr(name + "_cera", col, tuple(c * 0.8 for c in col), rough=0.45, nscale=30, spec=0.5)
    try:
        p = cm.node_tree.nodes["Principled BSDF"]
        p.inputs["Subsurface Weight"].default_value = 0.4; p.inputs["Subsurface Radius"].default_value = (0.02, 0.005, 0.004)
        p.inputs["Subsurface Scale"].default_value = 0.02
    except Exception:
        pass
    c = M.cyl(name + "_corpo", r, h, (0, 0, h / 2 + 0.03), cm, verts=24, parent=root)
    if suporte:
        lathe(name + "_cast", [(0.0, 0.0), (0.04, 0.0), (0.042, 0.006), (0.015, 0.012), (0.01, 0.022), (0.022, 0.028), (0.024, 0.034), (0.0, 0.034)], suporte, 32, (0, 0, 0), root)
    pv = M.cyl(name + "_pavio", 0.0015, 0.012, (0, 0, h + 0.036), M.emis(name + "_pv", (0.02, 0.01, 0.0), 1.0), verts=6, parent=root)
    fm = M.emis(name + "_chama", (1.0, 0.62, 0.2), 14.0)
    fl = M.sph(name + "_chama", 0.006, (0, 0, h + 0.05), fm, seg=16, rings=10, parent=root)
    for v in fl.data.vertices:
        z = v.co.z / 0.006
        v.co.z *= 2.6 if z > 0 else 1.0
        k = 1.0 - 0.55 * max(0.0, z)
        v.co.x *= k; v.co.y *= k
    fl.visible_shadow = False
    nucleo = M.sph(name + "_nucleo", 0.0025, (0, 0, h + 0.047), M.emis(name + "_nc", (0.4, 0.6, 1.0), 6.0), seg=10, rings=6, parent=root)
    nucleo.visible_shadow = False
    lo = M.light('POINT', (0, 0, 0), None, 1.2, (1.0, 0.58, 0.22), size=0.012)
    lo.parent = root; lo.location = (0, 0, h + 0.06)
    random.seed(seed)
    for fr in range(1, M.N + 1, 3):
        a = random.uniform(0.85, 1.15)
        M.K(fl, "scale", fr, (1.0 + random.uniform(-0.08, 0.08), 1.0, a))
        M.K(fl, "rotation_euler", fr, (random.uniform(-0.12, 0.12), random.uniform(-0.12, 0.12), 0))
        lo.data.energy = 1.2 * a; lo.data.keyframe_insert("energy", frame=fr)
    return dict(root=root, chama=fl, luz=lo, topo=Vector(loc) + Vector((0, 0, h + 0.05)))


def frango_assado(name="frango", loc=(0, 0, 0), rotz=0.0, s=1.0):
    """frango assado (metaballs): peito alto e redondo, coxas com a ponta do osso, asas dobradas; pele dourada e brilhante"""
    root = M.empty(name, loc, rot=(0, 0, rotz)); root.scale = (s,) * 3
    pele = D.materials.new("pele_assada"); pele.use_nodes = True
    nt = pele.node_tree; p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 18; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.65
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    rp = nt.nodes.new("ShaderNodeValToRGB")
    rp.color_ramp.elements[0].position = 0.32; rp.color_ramp.elements[0].color = (0.15, 0.04, 0.008, 1)
    rp.color_ramp.elements[1].position = 0.6; rp.color_ramp.elements[1].color = (0.45, 0.17, 0.035, 1)
    e = rp.color_ramp.elements.new(0.8); e.color = (0.68, 0.36, 0.09, 1)
    nt.links.new(nz.outputs["Fac"], rp.inputs["Fac"]); nt.links.new(rp.outputs["Color"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.28
    try:
        p.inputs["Coat Weight"].default_value = 0.55; p.inputs["Coat Roughness"].default_value = 0.15
        p.inputs["Subsurface Weight"].default_value = 0.15; p.inputs["Subsurface Radius"].default_value = (0.02, 0.008, 0.004); p.inputs["Subsurface Scale"].default_value = 0.02
    except Exception:
        pass
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 90
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35; bp.inputs["Distance"].default_value = 0.002
    nt.links.new(vo.outputs["Distance"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], p.inputs["Normal"])
    el = [((0, 0.0, 0.05), 0.15, (1.0, 1.3, 0.72)),                                   # corpo
          ((0.038, -0.015, 0.075), 0.1, (0.85, 1.15, 0.72)), ((-0.038, -0.015, 0.075), 0.1, (0.85, 1.15, 0.72))]   # peito
    for sx in (1, -1):
        el += [((sx * 0.078, -0.055, 0.045), 0.085, (0.8, 1.0, 0.8)),                     # sobrecoxa
               ((sx * 0.085, -0.105, 0.06), 0.06, (0.85, 1.1, 0.85)), ((sx * 0.075, -0.15, 0.08), 0.042, (1, 1, 1)),   # coxa
               ((sx * 0.095, 0.06, 0.04), 0.07, (0.6, 1.2, 0.55))]                         # asa dobrada
    body = M.metaball_mesh(name + "_corpo", [(Vector(c), r, sz) for c, r, sz in el], res=0.006, thr=0.6)
    M.setmat(body, pele); body.parent = root
    osso_m = D.materials.get("osso_marfim_frango") or M.pbr("osso_marfim_frango", (0.85, 0.78, 0.62), (0.7, 0.6, 0.45), rough=0.4, nscale=40)
    for sx in (1, -1):
        M.cone(name + "_osso", 0.0065, 0.005, 0.04, (sx * 0.072, -0.178, 0.092), (math.radians(-62), sx * math.radians(-8), 0), osso_m, parent=root)
        M.sph(name + "_ponta", 0.0085, (sx * 0.071, -0.196, 0.101), osso_m, seg=12, rings=6, parent=root)
    return dict(root=root, corpo=body, pele=pele)


def _piscas(n_mats=4, period=24, seed=11):
    """materiais de pisca-pisca que piscam em fase diferente (emissao animada)"""
    cols = [(1.0, 0.72, 0.3), (1.0, 0.25, 0.2), (0.35, 0.75, 1.0), (0.45, 1.0, 0.45)]
    out = []
    random.seed(seed)
    for i in range(n_mats):
        m = M.emis("pisca_%d" % i, cols[i % len(cols)], 8.0)
        sk = m.node_tree.nodes["Emission"].inputs["Strength"]
        ph = i * period // n_mats
        for fr in range(1 - ph, M.N + period, period):
            for df, v in ((0, 9.0), (period // 2 - 2, 9.0), (period // 2, 1.5), (period - 2, 1.5)):
                sk.default_value = v * random.uniform(0.85, 1.1); sk.keyframe_insert("default_value", frame=fr + df)
        out.append(m)
    return out


def arvore_natal(loc, h=1.9, piscas=None, seed=3):
    """pinheiro de natal: camadas de galhos (cones deformados e recortados), bolas e pisca-pisca piscando"""
    root = M.empty("arvore_natal", loc)
    verde = M.pbr("pinheiro", (0.01, 0.07, 0.03), (0.03, 0.16, 0.06), rough=0.75, nscale=30, nbump=0.6, nbscale=60)
    random.seed(seed)
    M.cyl("tronco_arv", 0.04, 0.25, (0, 0, 0.12), M.pbr("tronco_n", (0.15, 0.08, 0.03), rough=0.8), parent=root)
    for i in range(7):
        t = i / 6
        r = 0.62 * (1 - t) + 0.08
        z = 0.22 + t * (h - 0.45)
        bpy.ops.mesh.primitive_cone_add(vertices=28, radius1=r, depth=0.42 * (1 - 0.4 * t), location=(0, 0, z + 0.12))
        c = bpy.context.object; c.name = "galhos"; M.smooth(c); M.setmat(c, verde); c.parent = root
        c.rotation_euler = (0, 0, random.uniform(0, 6.3))
        dsp = c.modifiers.new("d", 'DISPLACE'); tx = D.textures.new("pinh", 'DISTORTED_NOISE'); tx.noise_scale = 0.08; dsp.texture = tx; dsp.strength = 0.06
        sd = c.modifiers.new("s", 'SUBSURF'); sd.levels = sd.render_levels = 1
    orn = [M.pbr("bola_v", (0.7, 0.02, 0.04), rough=0.12, spec=1.0), M.pbr("bola_o", (0.9, 0.6, 0.15), rough=0.15, metal=1.0), M.pbr("bola_a", (0.05, 0.2, 0.6), rough=0.12, spec=1.0)]
    piscas = piscas or _piscas()
    for i in range(110):
        z = random.uniform(0.3, h - 0.2)
        t = (z - 0.22) / (h - 0.45)
        rr = (0.62 * (1 - t) + 0.08) * random.uniform(0.82, 0.98)
        a = random.uniform(0, 2 * math.pi)
        p = (math.cos(a) * rr, math.sin(a) * rr, z)
        if i % 3 == 0:
            M.sph("bola", random.uniform(0.028, 0.04), p, random.choice(orn), seg=14, rings=8, parent=root)
        else:
            b = M.sph("pisca", 0.011, p, piscas[i % len(piscas)], seg=8, rings=4, parent=root); b.visible_shadow = False
    st = M.sph("estrela", 0.05, (0, 0, h + 0.02), M.emis("estrela_n", (1.0, 0.85, 0.45), 12.0), seg=12, rings=6, parent=root)
    return root


def mundo_ceia():
    """Ceia de Natal a noite. Primeiro plano: borda da mesa, taca, pratos. Meio: frango dourado na travessa, velas acesas.
    Fundo: parede verde-petroleo com varal de luzes, arvore com pisca-pisca, janela com a cidade a noite (tudo desfocado)."""
    s = M.reset(4)
    M.bloom(s, threshold=0.85, size=0.75, strength=0.75)
    s.cycles.transparent_max_bounces = 8
    nt = s.world.node_tree; bg = nt.nodes["Background"]
    bg.inputs[0].default_value = (0.012, 0.014, 0.03, 1); bg.inputs[1].default_value = 1.0
    Z = MESA_Z
    # piso e mesa
    madeira = M.pbr("piso_madeira", (0.12, 0.05, 0.02), (0.2, 0.09, 0.035), rough=0.45, nscale=2.5, nbump=0.2, nbscale=40)
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 2, 0)); M.setmat(bpy.context.object, madeira)
    toalha = _toalha_mat()
    mesa = M.box("mesa_toalha", (2.6, 1.7, 0.04), (0, -0.05, Z - 0.02), toalha, bev=0.015)
    saia = M.box("toalha_caida", (2.62, 1.72, 0.3), (0, -0.05, Z - 0.17), toalha, bev=0.01)
    ouro = _metal_mat("ouro", (1.0, 0.72, 0.32), 0.22)
    prata = _metal_mat("prata", (0.85, 0.85, 0.88), 0.18)
    porc = _porcelana_mat(); vidro = _vidro_mat()
    # caminho de mesa dourado
    cm = M.pbr("caminho_mesa", (0.55, 0.36, 0.08), (0.75, 0.52, 0.15), rough=0.35, nscale=60, metal=0.6, nbump=0.3, nbscale=200)
    M.box("caminho", (2.4, 0.34, 0.002), (0, 0.15, Z + 0.001), cm, bev=0)
    # travessa oval + frango
    trav = lathe("travessa", [(0.0, 0.0), (0.12, 0.0), (0.15, 0.012), (0.19, 0.028), (0.2, 0.03), (0.185, 0.026), (0.14, 0.012), (0.0, 0.01)], porc, 64, (0, 0.22, Z + 0.002))
    trav.scale = (1.45, 1.0, 1.0)
    lathe("travessa_ouro", [(0.188, 0.0285), (0.196, 0.0305), (0.2, 0.031)], ouro, 64, (0, 0, 0.0004), trav)
    fr = frango_assado("frango", (0, 0.22, Z + 0.012), 0.0, 1.1)
    # guarnicao: batatinhas, tomatinhos, alecrim
    random.seed(8)
    bat = M.pbr("batata", (0.55, 0.32, 0.08), (0.8, 0.55, 0.18), rough=0.3, nscale=25, nbump=0.3, nbscale=80, coat=0.4)
    tom = M.pbr("tomatinho", (0.7, 0.03, 0.02), (0.9, 0.1, 0.04), rough=0.15, nscale=20, coat=0.8)
    ale = M.pbr("alecrim", (0.04, 0.16, 0.05), (0.08, 0.25, 0.08), rough=0.6, nscale=40)
    for i in range(16):
        a = random.uniform(0, 2 * math.pi); rr = random.uniform(0.17, 0.25)
        x, y = math.cos(a) * rr * 1.1, 0.22 + math.sin(a) * rr * 0.6
        if i % 3 == 0:
            M.sph("tomatinho", 0.014, (x, y, Z + 0.03), tom, seg=14, rings=8)
        else:
            o = M.sph("batatinha", 0.02, (x, y, Z + 0.032), bat, seg=14, rings=8); o.scale = (1.2, 1.0, 0.85)
    for i in range(7):
        a = random.uniform(0, 2 * math.pi); rr = random.uniform(0.13, 0.2)
        x, y = math.cos(a) * rr * 1.2, 0.22 + math.sin(a) * rr * 0.7
        M.tube("alecrim", [(x, y, Z + 0.035), (x + 0.02, y + 0.03, Z + 0.04), (x + 0.03, y + 0.06, Z + 0.038)], 0.0025, ale, res=1)
    # lugares: pratos com borda dourada, tacas, talheres
    lugares = [(-0.75, -0.25), (0.75, -0.25), (-0.75, 0.6), (0.75, 0.6), (-0.3, 0.7), (0.35, 0.72)]
    for i, (x, y) in enumerate(lugares):
        prato("prato", (x, y, Z + 0.002), 0.13, porc, ouro)
        taca("taca", (x + 0.17 * (1 if x < 0 else -1) * -1, y + 0.12, Z + 0.002), vidro)
        M.box("garfo", (0.012, 0.17, 0.003), (x - 0.16, y, Z + 0.004), prata, bev=0.001)
        M.box("faca", (0.014, 0.19, 0.003), (x + 0.16, y, Z + 0.004), prata, bev=0.001)
    # velas (luz com motivo): duas altas no meio, uma baixa perto da camera
    velas = [vela("vela_a", (-0.34, 0.32, Z + 0.002), 0.26, suporte=ouro, seed=1),
             vela("vela_b", (0.36, 0.36, Z + 0.002), 0.21, suporte=ouro, seed=2),
             vela("vela_c", (-0.22, -0.22, Z + 0.002), 0.12, 0.02, col=(0.9, 0.85, 0.7), suporte=ouro, seed=3)]
    # enfeite: guirlanda de pinha e bolinhas no meio
    for i in range(10):
        x = -0.55 + i * 0.12
        M.sph("enfeite", 0.018, (x, 0.5 + 0.03 * math.sin(i), Z + 0.02), D.materials["bola_v"] if D.materials.get("bola_v") else ouro, seg=12, rings=6)
    # fundo: parede, rodape, janela com cidade, varal de luzes, arvore
    par = M.pbr("parede_verde", (0.02, 0.07, 0.07), (0.03, 0.1, 0.1), rough=0.85, nscale=2, nbump=0.2, nbscale=30)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 2.6, 2.0), rotation=(math.radians(90), 0, 0))
    wall = bpy.context.object; wall.scale = (9, 5, 1); M.setmat(wall, par)
    cid = M.emis("cidade_noite", (0.04, 0.06, 0.18), 1.0)
    nt2 = cid.node_tree; em = nt2.nodes["Emission"]
    tc = nt2.nodes.new("ShaderNodeTexCoord"); vo = nt2.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 30
    nt2.links.new(tc.outputs["Generated"], vo.inputs["Vector"])
    lt = nt2.nodes.new("ShaderNodeMath"); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.1
    nt2.links.new(vo.outputs["Distance"], lt.inputs[0])
    mx = nt2.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'
    nt2.links.new(lt.outputs[0], mx.inputs[0]); mx.inputs[6].default_value = (0.03, 0.05, 0.16, 1); mx.inputs[7].default_value = (1.0, 0.7, 0.3, 1)
    nt2.links.new(mx.outputs[2], em.inputs["Color"]); em.inputs["Strength"].default_value = 2.0
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-1.3, 2.58, 1.55), rotation=(math.radians(90), 0, 0))
    jan = bpy.context.object; jan.scale = (1.1, 1.3, 1); M.setmat(jan, cid)
    branco = M.pbr("moldura_janela", (0.85, 0.83, 0.8), rough=0.4)
    for (sx, sz, x, z) in ((1.25, 0.06, -1.3, 2.2), (1.25, 0.06, -1.3, 0.9), (0.06, 1.36, -1.92, 1.55), (0.06, 1.36, -0.68, 1.55), (0.04, 1.3, -1.3, 1.55)):
        M.box("moldura", (sx, 0.06, sz), (x, 2.55, z), branco, bev=0.01)
    piscas = _piscas()
    for i in range(34):            # varal de luzes na parede (vira bokeh)
        x = -2.2 + i * 0.13; z = 2.15 - 0.22 * math.sin(math.pi * (i % 17) / 16)
        b = M.sph("varal", 0.018, (x, 2.52, z), piscas[i % 4], seg=8, rings=4); b.visible_shadow = False
    arv = arvore_natal((1.25, 2.0, 0.0), 2.0, piscas)
    # luzes com motivo: lustre quente em cima, contraluz frio da janela, brilho da arvore
    M.light('AREA', (0.3, -0.5, 1.9), (0, 0.15, Z), 45, (1.0, 0.72, 0.42), size=1.0)
    M.light('AREA', (-1.4, 2.2, 1.6), (0, 0.2, Z + 0.1), 25, (0.5, 0.65, 1.0), size=1.0)
    M.light('POINT', (1.2, 1.7, 1.2), None, 7, (1.0, 0.6, 0.3), size=0.5)
    cam = M.camera((0, -0.9, Z + 0.35), (0, 0.2, Z + 0.08), 35)
    return dict(scene=s, cam=cam, frango=fr, travessa=trav, velas=velas, arvore=arv, piscas=piscas, mesa=mesa, ouro=ouro, prata=prata, porcelana=porc)



def hooks_abre(fu):
    """dois ganchos (empties) na peca inteira: girar o gancho abre o braco do V em volta da juncao, com curvatura suave
    (peso cresce da juncao para a ponta). Esquerdo abre com rotacao Y negativa, direito com positiva."""
    o = fu["inteira"]
    me = o.data
    out = {}
    for side, nm in ((-1, "L"), (1, "R")):
        vg = o.vertex_groups.new(name=nm)
        for v in me.vertices:
            x, z = v.co.x, v.co.z
            if x * side <= 0.002:
                continue
            w = max(0.0, min(1.0, (z - 0.06) / 0.8))
            w = w * w * (3 - 2 * w)
            if w > 0:
                vg.add([v.index], w, 'REPLACE')
        h = M.empty(fu["root"].name + "_gancho" + nm, (0, 0, -0.4), fu["giro"])
        bpy.context.view_layer.update()
        md = o.modifiers.new("gancho" + nm, 'HOOK'); md.object = h; md.vertex_group = nm; md.falloff_type = 'NONE'
        md.matrix_inverse = Matrix.Identity(4)          # gancho e objeto tem a mesma matriz em repouso: transformacao identidade
        while o.modifiers[0] != md:
            o.modifiers.move(o.modifiers.find(md.name), 0)
        out[nm] = h
    return out


def corta_x(m, keep_neg=True):
    """plano de corte no material: tudo do lado errado de x=0 (mundo) vira transparente (tela dividida sem Python)"""
    nt = m.node_tree
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    src = out.inputs["Surface"].links[0].from_socket
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sp.inputs[0])
    gt = nt.nodes.new("ShaderNodeMath"); gt.operation = 'GREATER_THAN' if keep_neg else 'LESS_THAN'; gt.inputs[1].default_value = 0.0
    nt.links.new(sp.outputs["X"], gt.inputs[0])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(gt.outputs[0], mx.inputs[0]); nt.links.new(src, mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m
