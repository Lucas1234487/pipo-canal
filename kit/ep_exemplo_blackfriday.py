"""EPISODIO DE REFERENCIA: Black Friday "metade do dobro" (humor util, 29 s).
Copie este arquivo como modelo para novos episodios: troque props, eventos e shots.
Rodar: python3 ep.py 1,300,520     (previa de quadros)   |   python3 ep.py full   (render completo)
"""
import os
KIT = os.environ.get("PIPO_KIT", "/home/claude/kit")
WORK = os.environ.get("PIPO_WORK", "/home/claude/ep")
N = 870
exec(open(KIT + "/pipo_lib.py").read())

t_duz = wt("duzentos"); t_cinq = wt("cinquenta"); t_cem_pop = wt("cem", 2)
t_parab = wt("parabéns"); t_voce = wt("você"); t_metade = wt("metade")
t_hist = wt("histórico"); t_manda = wt("manda"); t_quarta = wt("quarta"); t_sexta = wt("sexta")
PIPX = -1.0

pipo_place(PIPX, -0.95, 1.45)
# ------------------------------------------------------------- props
PX = 1.4  # product x
ped_m = toon("ped", (0.95, 0.30, 0.42))
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.85, depth=1.0, location=(PX, 0.3, 0.5))
ped = give(smooth(bpy.context.object), ped_m, 0.025)
bv = ped.modifiers.new("bv", 'BEVEL'); bv.width = 0.06; bv.segments = 3
pass
for p in ped.data.polygons:
    p.use_smooth = abs(p.normal.z) < 0.5

# headphones
hp = empty("hp", (PX, 0.3, 1.0))
band_m = toon("band", (0.16, 0.16, 0.22), shade=0.5, hi=1.6)
cup_m = toon("cup", (0.15, 0.85, 0.85))
bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.075, major_segments=48, minor_segments=12, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
band = bpy.context.object
bmb = bmesh.new(); bmb.from_mesh(band.data)
bmesh.ops.delete(bmb, geom=[v for v in bmb.verts if (band.matrix_world @ v.co).z < -0.02 or False], context='VERTS') if False else None
bmb.free()
# delete lower half in object space after rotation applied
bpy.ops.object.transform_apply(rotation=True)
bmb = bmesh.new(); bmb.from_mesh(band.data)
bmesh.ops.delete(bmb, geom=[v for v in bmb.verts if v.co.z < -0.01], context='VERTS')
bmb.to_mesh(band.data); bmb.free()
smooth(band)
give(band, band_m, 0.02)
band.parent = hp; band.location = (0, 0, 0.45)
for sx in (-1, 1):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.26, depth=0.2, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    c = bpy.context.object; smooth(c)
    bvc = c.modifiers.new("bv", 'BEVEL'); bvc.width = 0.06; bvc.segments = 3
    give(c, cup_m, 0.02)
    c.parent = hp; c.location = (sx * 0.55, 0, 0.42)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.2, depth=0.08, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    pad = bpy.context.object; smooth(pad)
    give(pad, band_m, 0.0)
    pad.parent = hp; pad.location = (sx * 0.43, 0, 0.42)
# fake shadow blobs
shm = flat("blob", (0.05, 0.01, 0.10), 1.0, alpha=0.75)



# price tag hanging from the band
tag_piv = empty("tagpiv", (PX + 0.2, 0.05, 1.98))
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.012, depth=0.55, location=(0, 0, -0.27))
string = bpy.context.object; string.data.materials.append(flat("str", (0.95, 0.95, 0.9)))
string.parent = tag_piv
tag = empty("tag", (0, 0, -0.75), tag_piv)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
tb = bpy.context.object; tb.scale = (0.82, 0.07, 0.5)
bpy.ops.object.transform_apply(scale=True)
bvt = tb.modifiers.new("bv", 'BEVEL'); bvt.width = 0.06; bvt.segments = 4
give(tb, toon("tagm", (1.0, 0.82, 0.12), shade=0.62), 0.02)
tb.parent = tag
hole = sphere("hole", 0.045, (0, -0.04, 0.17)); hole.scale = (1, 0.5, 1); hole.data.materials.append(flat("h", (0.15, 0.05, 0.2))); hole.parent = tag
DARK = (0.10, 0.03, 0.14)
p100 = text3d("R$100", 0.3, DARK, loc=(0, -0.045, -0.06), parent=tag)
p200 = text3d("R$200", 0.3, DARK, loc=(0, -0.045, -0.06), parent=tag)
p100b = text3d("R$100", 0.3, DARK, loc=(0, -0.045, -0.06), parent=tag)
strike = None
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.06, -0.06))
strike = bpy.context.object; strike.scale = (0.72, 0.01, 0.045); strike.rotation_euler = (0, math.radians(-8), 0)
strike.data.materials.append(flat("strk", (0.92, 0.1, 0.15))); strike.parent = tag

f_duz = f(t_duz)
f_cinq = f(t_cinq)
f_pop = f(t_cem_pop)
f_loop = N - 30
# tag swing & number swaps
K(tag_piv, "rotation_euler", 1, (0, 0, 0))
for fr, a in ((25, 0.06), (50, -0.04), (75, 0.0)):
    K(tag_piv, "rotation_euler", fr, (a, 0, 0))
pop_scale(p100, 1, dur=1)
hide_scale(p100, f_duz - 2, dur=3)
K(p200, "scale", 1, (0.001,) * 3); pop_scale(p200, f_duz + 1)
for fr, a in ((f_duz, 0.0), (f_duz + 4, 0.35), (f_duz + 12, -0.2), (f_duz + 20, 0.08), (f_duz + 28, 0.0)):
    K(tag_piv, "rotation_euler", fr, (a, 0, 0))
K(strike, "scale", 1, (0.001, 0.01, 0.045)); K(strike, "scale", f_pop - 4, (0.001, 0.01, 0.045)); K(strike, "scale", f_pop, (0.72, 0.01, 0.045))
K(p100b, "scale", 1, (0.001,) * 3)
# at pop: 200 drops away, 100 appears
K(p200, "location", f_pop - 1, (0, -0.045, -0.06)); K(p200, "location", f_pop + 6, (0, -0.045, 0.13))
K(p200, "scale", f_pop - 1, (1, 1, 1)); K(p200, "scale", f_pop + 6, (0.7, 0.7, 0.7))
pop_scale(p100b, f_pop + 2, base=1.0)
K(p100b, "location", f_pop + 2, (0, -0.045, -0.16))
K(strike, "location", f_pop, (0, -0.06, 0.13))
# loop reset back to the original tag
hide_scale(p100b, f_loop, dur=6)
hide_scale(p200, f_loop, base=0.7, dur=6)
K(strike, "scale", f_loop, (0.72, 0.01, 0.045)); K(strike, "scale", f_loop + 6, (0.001, 0.01, 0.045))
pop_scale(p100, f_loop + 6, dur=8)
K(p100, "location", f_loop + 5, (0, -0.045, -0.06))

# -50% sticker
stk = empty("sticker", (0.38, -0.12, 0.2), tag)
bm = bmesh.new()
pts = []
for i in range(24):
    r = 0.33 if i % 2 == 0 else 0.25
    a = i / 24 * 2 * math.pi
    pts.append(bm.verts.new((math.cos(a) * r, 0, math.sin(a) * r)))
bm.faces.new(pts)
me = D.meshes.new("star"); bm.to_mesh(me); bm.free()
star = link(D.objects.new("star", me))
sol = star.modifiers.new("th", 'SOLIDIFY'); sol.thickness = 0.03
star.data.materials.append(flat("starm", (0.95, 0.12, 0.2)))
star.parent = stk
st_t = text3d("-50%", 0.2, (1, 1, 1), loc=(0, -0.04, 0), parent=stk)
stk.rotation_euler = (0, math.radians(15), 0)
K(stk, "scale", 1, (0.001,) * 3)
K(stk, "scale", f_cinq - 1, (0.001,) * 3)
K(stk, "scale", f_cinq + 3, (1.5,) * 3)
K(stk, "scale", f_cinq + 7, (0.95,) * 3)
K(stk, "scale", f_cinq + 10, (1.0,) * 3)
K(stk, "scale", f_loop, (1.0,) * 3)
K(stk, "scale", f_loop + 6, (0.001,) * 3)
for fr, a in ((f_cinq, 0.0), (f_cinq + 4, -0.25), (f_cinq + 12, 0.12), (f_cinq + 20, 0.0)):
    K(tag_piv, "rotation_euler", fr, (a, 0, 0))


# ------------------------------------------------------------- PIPO animation
f_parab = f(t_parab)
f_voce = f(t_voce)
f_meta = f(t_metade)
f_hist = f(t_hist)
f_manda = f(t_manda)
set_face(FK, f(3.0), look=(0, -5))                                                 # looks at camera
set_face(FK, f(4.4), look=(-20, 0))
# 200: squint, both brows down
set_face(FK, f_duz, lid=TIRED, brow=(8, 0.24), browL=(-12, 0.29))
set_face(FK, f_duz + 4, lid=12, brow=(-18, 0.2), browL=(-18, 0.2), look=(-22, 3))
blink(FK, f_duz + 40, 12)
set_face(FK, f_duz + 60, look=(0, -5))     # judging look to camera
# sticker: eyes wide, brows up (hope)
set_face(FK, f_cinq - 1, lid=12, brow=(-18, 0.2), browL=(-18, 0.2), look=(0, -5))
set_face(FK, f_cinq + 4, lid=-80, brow=(12, 0.31), browL=(12, 0.31), look=(-20, 0))
set_face(FK, f_parab, lid=-80, look=(-20, 0))
set_face(FK, f_parab + 6, look=(0, -4))
set_face(FK, f_voce, lid=-80, look=(0, -4))
set_face(FK, f_voce + 20, lid=-40, brow=(-5, 0.25), browL=(15, 0.31), look=(-20, 0))   # doubt
pipo_start_kernel()
pipo_idle(FK, 1, f_voce)
pipo_hop(f_duz, 0.25)
pipo_hop(f_cinq + 2, 0.35)
pipo_tension(f_voce + 10, f_pop)
pipo_pop(f_pop, size=0.78)
set_face(FP, f_pop, lid=-85, brow=(15, 0.33), browL=(15, 0.33), look=(0, -6))       # shocked
set_face(FP, f_meta - 4, lid=-85, brow=(15, 0.33), browL=(15, 0.33), look=(0, -6))
set_face(FP, f_meta + 2, lid=-20, brow=(-15, 0.22), browL=(-15, 0.22), look=(-18, 0))  # annoyed at the tag
blink(FP, f_meta + 40, -20)
set_face(FP, f_hist, lid=-20, look=(-25, 2))     # looks at the chart
set_face(FP, f_manda, lid=-25, brow=(8, 0.24), browL=(-12, 0.3), look=(0, -6))   # signature deadpan to camera
blink(FP, f_manda + 30, -25)
pipo_unpop(f_loop, size=0.78)
set_face(FK, f_loop, lid=TIRED, brow=(8, 0.24), browL=(-12, 0.29), look=(-18, 0))
pipo_idle(FP, f_pop + 12, f_loop)
K(body, "scale", f_loop, (1, 1, 1))

# burst particles + flash ring

# price history chart + confetti
confetti(f(t_sexta))
# price history chart (appears with "histórico")
chart = empty("chart", (PX - 0.2, -0.6, 3.15))
chart.rotation_euler = (0, 0, math.radians(-8))
bars = []
cm_g = toon("bg", (0.3, 0.9, 0.45)); cm_r = toon("br", (0.95, 0.15, 0.25))
bpy.ops.mesh.primitive_cube_add(size=1)
panel = bpy.context.object; panel.scale = (1.5, 0.05, 1.05); bpy.ops.object.transform_apply(scale=True)
bvp = panel.modifiers.new("bv", 'BEVEL'); bvp.width = 0.08; bvp.segments = 4
give(panel, toon("panel", (0.97, 0.95, 1.0), shade=0.8), 0.02); panel.parent = chart; panel.location = (0, 0.06, 0.1)
for i, (h, m_) in enumerate(((0.35, cm_g), (0.75, cm_r), (0.35, cm_g))):
    bpy.ops.mesh.primitive_cube_add(size=1)
    bar = bpy.context.object; bar.data.materials.append(m_.copy()); bar.parent = chart
    bar.location = (-0.42 + i * 0.42, -0.02, -0.33)
    bars.append((bar, h))
lbls = [text3d(t, 0.15, DARK, loc=(-0.42 + i * 0.42, -0.04, -0.37 + 0.0), parent=chart) for i, t in enumerate(("SEG", "QUA", "SEX"))]
for l_ in lbls:
    l_.location.z = -0.33 - 0.11
f_chart = f(t_hist) - 6
K(chart, "scale", 1, (0.001,) * 3); pop_scale(chart, f_chart, dur=8)
for i, (bar, h) in enumerate(bars):
    K(bar, "scale", 1, (0.25, 0.08, 0.001)); K(bar, "location", 1, (bar.location.x, -0.02, -0.33))
    fr0 = f_chart + 6 + i * 5
    K(bar, "scale", fr0, (0.25, 0.08, 0.001)); K(bar, "location", fr0, (bar.location.x, -0.02, -0.33))
    K(bar, "scale", fr0 + 6, (0.25, 0.08, h)); K(bar, "location", fr0 + 6, (bar.location.x, -0.02, -0.33 + h / 2))
hide_scale(chart, f_manda - 4, dur=6)


# ------------------------------------------------------------- camera + events
shots = [  # (t_inicio_s, loc_inicio, loc_fim, alvo, lente)
    (0.0, (0.15, -6.6, 1.6), (0.15, -6.0, 1.55), (0.25, 0, 0.8), 30),
    (f_duz / 30 - 0.15, (1.3, -3.5, 1.9), (1.25, -3.3, 1.85), (PX + 0.2, 0, 0.95), 34),
    (t_sexta - 0.05, (-0.4, -5.9, 0.6), (-0.2, -5.5, 0.7), (0.2, 0, 1.15), 28),
    (t_parab - 0.05, (-0.6, -4.0, 1.5), (-0.6, -3.7, 1.45), (PIPX + 0.15, -0.95, 1.0), 36),
    (t_voce - 0.05, (0.9, -3.8, 1.5), (1.1, -2.6, 1.5), (PX + 0.2, 0, 0.85), 34),
    (t_cem_pop - 0.02, (0.05, -6.3, 1.7), (0.0, -6.7, 1.75), (0.15, -0.6, 1.0), 30),
    (t_metade - 0.1, (0.2, -6.6, 1.6), (0.2, -6.3, 1.6), (0.15, 0, 0.9), 32),
    (t_hist - 0.25, (0.75, -5.0, 2.4), (0.8, -4.8, 2.4), (PX - 0.3, -0.6, 2.8), 32),
    (t_manda - 0.05, (-0.5, -5.0, 1.8), (-0.5, -4.7, 1.75), (PIPX + 0.3, -0.95, 1.3), 34),
    ((f_loop + 10) / 30, (0.15, -6.6, 1.6), (0.15, -6.6, 1.6), (0.25, 0, 0.8), 30),
]
events = dict(
    f_pop=f_pop, f_loop=f_loop,
    music="trilha_leve_96bpm.wav",
    sfx=[  # (arquivo, tempo_s, ganho)
        ("boing.wav", (f_duz - 1) / 30, 0.5), ("thump.wav", (f_cinq - 1) / 30 + 0.1, 0.7),
        ("riser.wav", (f_pop - 1) / 30 - 1.65, 0.35), ("pop.wav", (f_pop - 1) / 30, 1.0), ("thump.wav", (f_pop - 1) / 30, 0.6),
        ("ding.wav", t_hist, 0.3), ("click.wav", t_hist, 0.5), ("click.wav", t_hist + 0.17, 0.5), ("click.wav", t_hist + 0.34, 0.5),
        ("squish.wav", (f_loop - 1) / 30 + 0.05, 0.6)],
    pills=[  # (inicio_s, fim_s, texto, cor_fundo, cor_texto)  - textos curtos no topo, mudos-friendly
        (0.0, wt("segunda-feira") - 0.05, "BLACK FRIDAY: 50% OFF?", [255, 255, 255], [26, 8, 36]),
        (wt("segunda-feira"), t_quarta - 0.05, "SEGUNDA", [255, 255, 255], [26, 8, 36]),
        (t_quarta, t_sexta - 0.05, "QUARTA", [255, 255, 255], [26, 8, 36]),
        (t_sexta, t_parab - 0.05, "SEXTA: BLACK FRIDAY", [240, 30, 50], [255, 255, 255]),
        ((f_pop - 1) / 30 + 0.1, wt("antes") - 0.05, "METADE DO DOBRO", [255, 214, 30], [26, 8, 36]),
        (t_hist - 0.2, t_manda - 0.05, "OLHA O HISTÓRICO", [255, 255, 255], [26, 8, 36])],
    music_gap=[(f_pop - 1) / 30 - 0.75, (f_pop - 1) / 30],
)
# grupos que a revisao automatica vigia (sobreposicao, corte, objetos atravessando)
qa_key("etiqueta", tag_piv); qa_key("fone", hp); qa_key("pedestal", ped); qa_key("grafico", chart)
qa_touch("etiqueta", "fone"); qa_touch("fone", "pedestal"); qa_touch("etiqueta", "pedestal")
finish(shots, events, shake_at=f_pop)
