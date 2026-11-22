"""EPISODIO DE REFERENCIA: Black Friday "metade do dobro" (humor util, 29 s).
Copie este arquivo como modelo para novos episodios: troque props, eventos e shots.
Rodar: python3 ep.py 1,300,520     (previa de quadros)   |   python3 ep.py full   (render completo)
"""
import os
KIT = os.environ.get("PIPO_KIT", "/home/claude/kit")
WORK = os.environ.get("PIPO_WORK", "/home/claude/ep")
N = 860
exec(open(KIT + "/pipo_lib.py").read())
exec(open(KIT + "/cenarios.py").read())
AMB = cenario_sala(noite=True, natal=True)


t_l = [l["start"] for l in T["lines"]]          # inicio de cada frase
t_aguenta = wt("aguenta"); t_cheirar = wt("cheirar"); t_chacoalhar = wt("chacoalhar")
t_cantinho = wt("cantinho"); t_trinta2 = wt("trinta", 1)
PIPX = -1.05
pipo_place(PIPX, -0.95, 1.45)
BX = 1.0

# ------------------------------------------------------------- props: presente
RED = (0.86, 0.10, 0.18); GOLD = (1.0, 0.75, 0.15); GREEN = (0.10, 0.62, 0.35)
gift = empty("gift", (BX, 0.15, 0))
def boxmesh(name, sx, sy, sz, col, loc, parent, bev=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object; o.name = name; o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    b = o.modifiers.new("bv", 'BEVEL'); b.width = bev; b.segments = 3
    smooth(o); o.data.materials.append(lit(name + "m", col, 0.35, 0.4)); o.parent = parent; o.location = loc
    return o
gbody = boxmesh("gbody", 0.95, 0.95, 0.72, RED, (0, 0, 0.36), gift)
boxmesh("rib1", 0.16, 0.97, 0.73, GOLD, (0, 0, 0.36), gift, 0.02)
boxmesh("rib2", 0.97, 0.16, 0.73, GOLD, (0, 0, 0.36), gift, 0.02)
hinge = empty("hinge", (0, 0.5, 0.72), gift)                       # dobradica na borda de tras
lid = empty("lid", (0, 0, 0), hinge)
boxmesh("glid", 1.03, 1.03, 0.2, RED, (0, -0.5, 0.1), lid)
boxmesh("lrib1", 0.17, 1.05, 0.21, GOLD, (0, -0.5, 0.1), lid, 0.02)
boxmesh("lrib2", 1.05, 0.17, 0.21, GOLD, (0, -0.5, 0.1), lid, 0.02)
for sx in (-1, 1):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.05, location=(0, 0, 0))
    bow = bpy.context.object; smooth(bow); bow.data.materials.append(lit("bow", GOLD, 0.3, 0.5)); bow.parent = lid
    bow.location = (sx * 0.15, -0.5, 0.3); bow.rotation_euler = (math.radians(90), math.radians(sx * 35), 0); bow.scale = (1, 1, 0.7)
# presente de dentro (menor, verde) escondido dentro da caixa
inner = empty("inner", (0, 0, 0.05), gift)
boxmesh("ibody", 0.5, 0.5, 0.42, GREEN, (0, 0, 0.21), inner)
boxmesh("irib1", 0.1, 0.52, 0.43, GOLD, (0, 0, 0.21), inner, 0.015)
boxmesh("irib2", 0.52, 0.1, 0.43, GOLD, (0, 0, 0.21), inner, 0.015)
for sx in (-1, 1):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.09, minor_radius=0.03, location=(0, 0, 0))
    b2 = bpy.context.object; smooth(b2); b2.data.materials.append(lit("bow2", GOLD, 0.3, 0.5)); b2.parent = inner
    b2.location = (sx * 0.08, 0, 0.47); b2.rotation_euler = (math.radians(90), math.radians(sx * 35), 0); b2.scale = (1, 1, 0.7)
rug = AMB['rug']

F_ = f
f_cheirar = F_(t_cheirar); f_chac = F_(t_chacoalhar); f_cant = F_(t_cantinho)
f_open = F_(t_l[5] + T["lines"][5]["dur"] + 0.1)   # tampa abre no silencio
f_pop = f_open + 27                                 # estouro sem narracao, so o POP
t_caixa = (f_pop - 1) / 30
f_loop = N - 30

# ------------------------------------------------------------- animacao
pipo_start_kernel()
set_face(FK, 1, lid=TIRED, brow=(8, 0.24), browL=(-12, 0.29), look=(-20, 0))
blink(FK, F_(t_aguenta) + 4, TIRED)
set_face(FK, F_(t_aguenta) + 12, lid=TIRED)
pipo_idle(FK, 1, f_pop - 30)
# dia dois: inclina e cheira
K(body, "location", f_cheirar - 4, (0, 0, 0)); K(body, "rotation_euler", f_cheirar - 4, (0, 0, 0))
K(body, "location", f_cheirar + 8, (0.22, 0, 0)); K(body, "rotation_euler", f_cheirar + 8, (0, math.radians(14), 0))
K(body, "location", f_cheirar + 40, (0.22, 0, 0)); K(body, "rotation_euler", f_cheirar + 40, (0, math.radians(14), 0))
K(body, "location", f_cheirar + 52, (0, 0, 0)); K(body, "rotation_euler", f_cheirar + 52, (0, 0, 0))
set_face(FK, f_cheirar + 6, lid=10, look=(-25, 5))
set_face(FK, f_cheirar + 45, lid=TIRED, look=(-20, 0))
# dia tres: chacoalha a caixa
for k in range(6):
    K(gift, "rotation_euler", 1 + k * 5, (0, math.radians(3 if k % 2 else -3), 0))
K(gift, "rotation_euler", 32, (0, 0, 0))
K(gift, "rotation_euler", f_chac - 1, (0, 0, 0))
for k in range(8):
    K(gift, "rotation_euler", f_chac + 3 + k * 4, (0, math.radians(7 if k % 2 else -7), math.radians(4 if k % 2 else -4)))
K(gift, "rotation_euler", f_chac + 36, (0, 0, 0))
pipo_hop(f_chac + 2, 0.22)
pipo_hop(f_chac + 18, 0.18)
# dia quatro: olha pros lados, tampa sobe um pouco, silencio, abre
set_face(FK, f_cant - 12, look=(25, 0)); set_face(FK, f_cant - 2, look=(-30, 0)); set_face(FK, f_cant + 8, look=(28, 0))
set_face(FK, f_cant + 18, lid=-40, look=(-22, 3), brow=(10, 0.3), browL=(10, 0.3))
K(hinge, "rotation_euler", 1, (0, 0, 0)); K(hinge, "rotation_euler", f_cant + 10, (0, 0, 0))
K(hinge, "rotation_euler", f_cant + 18, (math.radians(-14), 0, 0))
K(hinge, "rotation_euler", f_open, (math.radians(-14), 0, 0))
K(hinge, "rotation_euler", f_open + 8, (math.radians(-115), 0, 0))
K(inner, "location", 1, (0, 0, 0.05)); K(inner, "location", f_open + 4, (0, 0, 0.05))
K(inner, "location", f_open + 14, (0, 0, 0.85)); K(inner, "location", f_open + 18, (0, 0, 0.78))
pipo_tension(f_open + 4, f_pop)
pipo_pop(f_pop, size=0.78)
set_face(FP, f_pop + 14, lid=-30, brow=(-18, 0.2), browL=(-18, 0.2), look=(-22, 0))   # brava olhando a caixa nova
blink(FP, F_(t_trinta2) + 10, -30)
set_face(FP, F_(t_trinta2) + 20, lid=-25, brow=(8, 0.24), browL=(-12, 0.3), look=(0, -6))  # encara a camera (assinatura)
pipo_idle(FP, f_pop + 12, f_loop)
# loop: volta tudo ao inicio
pipo_unpop(f_loop, size=0.78)
K(inner, "location", f_loop + 2, (0, 0, 0.78)); K(inner, "location", f_loop + 10, (0, 0, 0.05))
K(hinge, "rotation_euler", f_loop + 6, (math.radians(-115), 0, 0)); K(hinge, "rotation_euler", f_loop + 14, (0, 0, 0))
set_face(FK, f_loop, lid=TIRED, brow=(8, 0.24), browL=(-12, 0.29), look=(-20, 0))
K(body, "scale", f_loop, (1, 1, 1))

# ------------------------------------------------------------- camera + events
shots = [
    (0.0, (0.0, -6.0, 1.5), (0.0, -5.5, 1.45), (0.0, 0, 0.75), 30),
    (t_l[1] - 0.05, (-0.75, -3.4, 1.3), (-0.75, -3.2, 1.28), (PIPX + 0.1, -0.95, 0.95), 36),
    (t_l[2] - 0.05, (0.2, -6.2, 1.2), (0.15, -5.4, 1.15), (0.0, 0, 0.7), 30),
    (t_l[3] - 0.05, (1.6, -5.2, 1.1), (1.5, -4.9, 1.1), (-0.45, -0.3, 0.75), 32),
    (t_l[4] - 0.05, (0.9, -3.8, 0.45), (0.85, -3.6, 0.5), (BX - 0.2, 0.1, 0.85), 30),
    (t_l[5] - 0.05, (-0.4, -5.6, 1.6), (-0.35, -5.2, 1.55), (-0.3, -0.2, 0.75), 30),
    (t_caixa - 0.02, (-0.1, -6.8, 1.7), (-0.15, -7.2, 1.75), (-0.1, -0.3, 0.95), 30),
    (t_l[7] - 0.05, (-0.55, -6.6, 1.6), (-0.55, -6.3, 1.55), (-0.45, -0.5, 0.95), 32),
    ((f_loop + 14) / 30, (0.0, -6.0, 1.5), (0.0, -6.0, 1.5), (0.0, 0, 0.75), 30),
]
DK = [26, 8, 36]; WH = [255, 255, 255]
events = dict(
    f_pop=f_pop, f_loop=f_loop, music="trilha_leve_96bpm.wav",
    sfx=[("squish.wav", (f_cheirar + 6) / 30, 0.5), ("thump.wav", (f_chac + 3) / 30, 0.4), ("thump.wav", (f_chac + 11) / 30, 0.35),
         ("thump.wav", (f_chac + 19) / 30, 0.35), ("click.wav", (f_cant + 16) / 30, 0.6), ("click.wav", (f_open + 8) / 30, 0.5),
         ("riser.wav", (f_pop - 1) / 30 - 1.6, 0.35), ("pop.wav", (f_pop - 1) / 30, 1.0), ("thump.wav", (f_pop - 1) / 30, 0.6),
         ("squish.wav", (f_loop - 1) / 30 + 0.05, 0.6)],
    pills=[(0.0, t_l[2] - 0.05, "33 DIAS PRO NATAL", WH, DK), (t_l[2], t_l[3] - 0.05, "DIA 1 · FALTAM 33", WH, DK),
           (t_l[3], t_l[4] - 0.05, "DIA 2 · FALTAM 32", WH, DK), (t_l[4], t_l[5] - 0.05, "DIA 3 · FALTAM 31", WH, DK),
           (t_l[5], t_caixa - 0.05, "DIA 4 · FALTAM 30", [240, 30, 50], WH), (t_caixa + 0.1, (f_loop - 1) / 30, "AINDA FALTAM 30", [255, 214, 30], DK)],
    pills_en=[(0.0, t_l[2] - 0.05, "33 DAYS TO CHRISTMAS", WH, DK), (t_l[2], t_l[3] - 0.05, "DAY 1 · 33 TO GO", WH, DK),
              (t_l[3], t_l[4] - 0.05, "DAY 2 · 32 TO GO", WH, DK), (t_l[4], t_l[5] - 0.05, "DAY 3 · 31 TO GO", WH, DK),
              (t_l[5], t_caixa - 0.05, "DAY 4 · 30 TO GO", [240, 30, 50], WH), (t_caixa + 0.1, (f_loop - 1) / 30, "STILL 30 TO GO", [255, 214, 30], DK)],
    music_gap=[(f_pop - 1) / 30 - 0.7, (f_pop - 1) / 30],
)
qa_key("presente", gift); qa_key("tapete", rug)
qa_touch("presente", "tapete"); qa_touch("tapete", "pipo_espiga"); qa_touch("tapete", "pipo_pipoca")
finish(shots, events, shake_at=f_pop, dof=(pipo, 1.1))
