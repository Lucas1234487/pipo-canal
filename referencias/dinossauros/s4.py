import sys; sys.path.insert(0, "/home/claude/v")
from land import *

F = lambda t: int(30 * (0.3 + t)) + 1
N = 656
s = reset(N)
bloom(s)
L = build_land()
bg, ramp = world_gradient(s, top=(0.08, 0.28, 0.85), bottom=(1.0, 0.62, 0.35), strength=1.0)
sn = sun(direction=(-0.6, 0.8, -0.45), strength=4.0, color=(1.0, 0.88, 0.72), angle=0.05)

top, bot = ramp.color_ramp.elements[1], ramp.color_ramp.elements[0]


def kcol(el, f, c):
    el.color = (*c, 1)
    el.keyframe_insert("color", frame=f)


# sky: normal -> red/orange -> dark brown/grey
for f, tc, bc in ((1, (0.08, 0.28, 0.85), (1.0, 0.62, 0.35)),
                  (F(2.2), (0.35, 0.08, 0.04), (1.0, 0.35, 0.08)),
                  (F(8.8), (0.30, 0.07, 0.03), (0.9, 0.30, 0.06)),
                  (F(11.5), (0.03, 0.025, 0.022), (0.12, 0.09, 0.07)),
                  (N, (0.02, 0.018, 0.016), (0.08, 0.06, 0.05))):
    kcol(top, f, tc)
    kcol(bot, f, bc)
for f, e, c in ((1, 4.0, (1, 0.88, 0.72)), (F(2.2), 3.0, (1, 0.5, 0.3)), (F(8.8), 2.6, (1, 0.45, 0.25)),
                (F(11.5), 0.35, (0.7, 0.6, 0.55)), (N, 0.25, (0.7, 0.6, 0.55))):
    sn.data.energy = e
    sn.data.color = c
    sn.data.keyframe_insert("energy", frame=f)
    sn.data.keyframe_insert("color", frame=f)

cam = camera((0, 0, 0), lens=26)
key_cam(cam, 1, (1.5, -14.5, 2.6), (2.2, 4, 5.8))
key_cam(cam, F(9.0), (0.5, -13.0, 2.6), (1.8, 4, 4.5))
key_cam(cam, F(16.0), (0.0, -12.0, 2.4), (1.5, 4, 3.5))
key_cam(cam, N, (0.3, -10.5, 2.2), (1.5, 4, 3.2))

# dinos react
neck = L["neck"]
for f, a in ((1, -0.34), (F(2.0), -0.30), (F(15.5), -0.05), (F(17.5), 0.55), (N, 0.6)):
    neck.rotation_euler = (0, a, 0)
    neck.keyframe_insert("rotation_euler", frame=f)
rex = L["rex"]
rz0 = rex.rotation_euler.z + 0.36
for f, a, ry in ((1, 0, 0), (F(18.0), 0.0, 0.0), (F(19.5), -0.2, 0.18), (N, -0.22, 0.2)):
    rex.rotation_euler = (0, ry, rz0 + a)
    rex.keyframe_insert("rotation_euler", frame=f)

# fire rain
random.seed(11)
hm = emis("fhead", (1, 0.6, 0.25), 25)
fire_m = mat("fire", (0.3, 0.05, 0.0), 0.8, emit=(1, 0.1, 0.0), estr=1.4, noise_bump=1, noise_scale=3)
_ftx = D.textures.new("fn", "CLOUDS"); _ftx.noise_scale = 0.5
g = L["ground"]
for i in range(64):
    land_x = random.uniform(-14, 18)
    land_y = random.uniform(-4, 35) if i % 3 else random.uniform(35, 70)
    f_land = random.randint(F(2.6), F(9.5))
    fall = random.randint(18, 30)
    dirv = Vector((random.uniform(-0.6, -0.2), random.uniform(-0.2, 0.2), -1)).normalized()
    end = Vector((land_x, land_y, ground_z(land_x, land_y, g)))
    start = end - dirv * random.uniform(45, 70)
    ar = link(D.objects.new("fm", None))
    hd = sphere("fh", 0.28, seg=12, rings=6, m=hm)
    hd.parent = ar
    hd.visible_shadow = False
    trail(ar, 6, 0.26, strength=9)
    ar.rotation_euler = dirv.to_track_quat('X', 'Z').to_euler()
    ar.location = start
    ar.keyframe_insert("location", frame=f_land - fall)
    ar.location = end
    ar.keyframe_insert("location", frame=f_land)
    ar.scale = (0.001,) * 3
    ar.keyframe_insert("scale", frame=f_land - fall - 1)
    ar.scale = (1,) * 3
    ar.keyframe_insert("scale", frame=f_land - fall)
    ar.keyframe_insert("scale", frame=f_land)
    ar.scale = (0.001,) * 3
    ar.keyframe_insert("scale", frame=f_land + 1)
    linear(ar)
    # ground fire at landing
    if i % 2 == 0:
        fo = ico("gf", random.uniform(0.6, 1.2), loc=end, sub=3, m=fire_m)
        _fd = fo.modifiers.new("d", 'DISPLACE'); _fd.texture = _ftx; _fd.strength = 0.6
        fo.visible_shadow = False
        fo.scale = (0.001,) * 3
        fo.keyframe_insert("scale", frame=f_land)
        fo.scale = (1, 1, 1.6)
        fo.keyframe_insert("scale", frame=f_land + 10)
        fo.scale = (1.2, 1.2, 2.0)
        fo.keyframe_insert("scale", frame=F(11.0))
        fo.scale = (0.001,) * 3
        fo.keyframe_insert("scale", frame=F(12.5))

# fire light flicker
fl = point((-3, 6, 3), 0, color=(1, 0.4, 0.1), radius=3)
for f in range(1, N + 1, 6):
    t = (f - 1) / 30.0
    on = 1.0 if F(3.0) <= f <= F(11.5) else 0.0
    fl.data.energy = on * random.uniform(1500, 3500)
    fl.data.keyframe_insert("energy", frame=f)

# trees: burn -> dead
ml = L["m_leaf"]
p = ml.node_tree.nodes["Principled BSDF"]
mixn = [n for n in ml.node_tree.nodes if n.bl_idname == "ShaderNodeMix"][0]
p.inputs["Emission Color"].default_value = (1, 0.08, 0.0, 1)
ksock(p.inputs["Emission Strength"], F(6.8), 0.0)
ksock(p.inputs["Emission Strength"], F(8.0), 0.55)
ksock(p.inputs["Emission Strength"], F(10.5), 0.45)
ksock(p.inputs["Emission Strength"], F(12.5), 0.0)
ksock(mixn.inputs[6], F(10.5), (0.06, 0.25, 0.08, 1))
ksock(mixn.inputs[7], F(10.5), (0.12, 0.35, 0.1, 1))
ksock(mixn.inputs[6], F(14.6), (0.07, 0.05, 0.035, 1))
ksock(mixn.inputs[7], F(14.6), (0.13, 0.09, 0.05, 1))
mb_ = L["m_bush"]
mixb = [n for n in mb_.node_tree.nodes if n.bl_idname == "ShaderNodeMix"][0]
ksock(mixb.inputs[6], F(12.5), (0.10, 0.32, 0.08, 1))
ksock(mixb.inputs[7], F(12.5), (0.2, 0.42, 0.1, 1))
ksock(mixb.inputs[6], F(15.0), (0.08, 0.06, 0.04, 1))
ksock(mixb.inputs[7], F(15.0), (0.14, 0.10, 0.06, 1))
for b in L["bushes"]:
    b.keyframe_insert("scale", frame=F(13.5))
    b.scale = (b.scale.x, b.scale.y, 0.3)
    b.keyframe_insert("scale", frame=F(15.5))
# ground to ash
gmix = [n for n in L["gm"].node_tree.nodes if n.bl_idname == "ShaderNodeMix"][0]
ksock(gmix.inputs[6], F(9.0), (0.13, 0.30, 0.08, 1))
ksock(gmix.inputs[7], F(9.0), (0.30, 0.38, 0.10, 1))
ksock(gmix.inputs[6], F(13.0), (0.10, 0.09, 0.08, 1))
ksock(gmix.inputs[7], F(13.0), (0.18, 0.16, 0.14, 1))

# falling ash (dark flakes) during darkness
am = mat("ash", (0.35, 0.33, 0.3), 1.0)
for i in range(70):
    x, y = random.uniform(-6, 8), random.uniform(-9, 4)
    z0 = random.uniform(6, 12)
    a = ico("ash", random.uniform(0.03, 0.06), loc=(x, y, z0), sub=1, m=am)
    a.visible_shadow = False
    f0 = F(10.0)
    a.location = (x, y, z0 + 8)
    a.keyframe_insert("location", frame=f0)
    a.location = (x + random.uniform(-2, 2), y, z0 - 12)
    a.keyframe_insert("location", frame=N)
    linear(a)

mw, mo = txt_mats()
T = [("O PIOR VEIO DEPOIS", 2.3, 0.3, mw, 0.0, 2.3),
     ("CHUVA DE FOGO", 2.35, 0.45, mo, 5.9, 8.9),
     ("INCÊNDIOS", 1.85, 0.32, mw, 7.5, 8.9),
     ("POEIRA E FULIGEM", 2.35, 0.36, mw, 9.8, 12.9),
     ("CÉU ESCURO POR MESES", 1.85, 0.3, mo, 11.2, 12.9),
     ("SEM LUZ DO SOL", 2.35, 0.38, mw, 13.1, 16.1),
     ("AS PLANTAS MORRERAM", 1.85, 0.3, mo, 14.4, 16.1),
     ("HERBÍVOROS: SEM COMIDA", 2.35, 0.28, mw, 16.3, None),
     ("CARNÍVOROS: SEM PRESAS", 1.85, 0.28, mo, 18.5, None)]
for body, y, sz, m, t0, t1 in T:
    o = hud_text(cam, body, y, sz, m)
    pop(o, F(t0) if t0 > 0 else 2, F(t1) if t1 else None)

run("s4", [F(8.5)])
