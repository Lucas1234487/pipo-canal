import sys; sys.path.insert(0, "/home/claude/v")
from lib import *
import lib
lib.HUD_DEPTH = 0.35

F = lambda t: int(30 * (0.3 + t)) + 1
N = 360
HIT = 24
s = reset(N)
bloom(s)
world_stars(s)
LAT, LON = 21.4, -89.5
root, e, _, _ = earth(3.0, texdir=f"{DIR}/tex4k")
D.materials["earthm"].node_tree.nodes["cloudamt"].inputs[1].default_value = 0.15
root.rotation_euler = (math.radians(LAT), 0, math.radians(-90 - LON))
sun(direction=(0.55, 0.75, -0.45), strength=4.5)
bpy.context.view_layer.update()

pos = latlon(LAT, LON, 3.0)
anchor = link(D.objects.new("anchor", None))
anchor.parent = root
anchor.location = pos
anchor.rotation_euler = pos.normalized().to_track_quat('Z', 'Y').to_euler()
bpy.context.view_layer.update()


def child(o):
    o.parent = anchor
    o.visible_shadow = False
    return o


# camera in anchor space (Z = up from the surface)
cam = camera((0, 0, 0), lens=30)
cam.parent = anchor
key_cam(cam, 1, (0.25, -1.55, 0.75), (0, 0.15, 0.05))
key_cam(cam, HIT, (0.2, -1.5, 0.72), (0, 0.1, 0.06))
key_cam(cam, F(5.0), (0.1, -1.75, 0.95), (0, 0.15, 0.1))
key_cam(cam, F(7.4), (0.0, -2.1, 1.35), (0, 0.25, 0.0))
key_cam(cam, N, (0.0, -2.3, 1.55), (0, 0.3, 0.0))
shake(cam, HIT, HIT + 45, strength=0.04, scale=1.5)

# asteroid incoming
ar = link(D.objects.new("ast", None))
child(ar)
a = asteroid(0.035)
a.parent = ar
a.visible_shadow = False
tr = trail(ar, 0.9, 0.034, strength=14)
p0, p1 = Vector((-0.9, 0.9, 1.6)), Vector((0, 0, 0.0))
ar.rotation_euler = (p1 - p0).normalized().to_track_quat('X', 'Z').to_euler()
ar.location = p0
ar.keyframe_insert("location", frame=1)
ar.location = p1
ar.keyframe_insert("location", frame=HIT)
ar.scale = (1,) * 3
ar.keyframe_insert("scale", frame=HIT)
ar.scale = (0.001,) * 3
ar.keyframe_insert("scale", frame=HIT + 1)
linear(ar)

# flash
fl = child(sphere("flash", 0.1, seg=32, rings=16))
fm, fmx, fem = emis_fade("flashm", (1, 0.85, 0.6), 60)
setmat(fl, fm)
fl.scale = (0.001,) * 3; fl.keyframe_insert("scale", frame=HIT)
fl.scale = (1.0,) * 3; fl.keyframe_insert("scale", frame=HIT + 4)
fl.scale = (2.2,) * 3; fl.keyframe_insert("scale", frame=HIT + 20)
ksock(fmx.inputs[0], HIT, 1.0)
ksock(fmx.inputs[0], HIT + 6, 1.0)
ksock(fmx.inputs[0], HIT + 24, 0.0)
pl = point((0, 0, 0.05), 0, color=(1, 0.6, 0.3), radius=0.05)
child(pl)
pl.data.energy = 0; pl.data.keyframe_insert("energy", frame=HIT - 1)
pl.data.energy = 400; pl.data.keyframe_insert("energy", frame=HIT + 2)
pl.data.energy = 60; pl.data.keyframe_insert("energy", frame=HIT + 40)
pl.data.energy = 15; pl.data.keyframe_insert("energy", frame=N)

# fireball / plume
fb = child(ico("fireball", 0.1, sub=4))
_tx = D.textures.new("fbn", 'CLOUDS'); _tx.noise_scale = 0.035
_d = fb.modifiers.new("d", 'DISPLACE'); _d.texture = _tx; _d.strength = 0.045
fbm = mat("fbm", (0.15, 0.06, 0.03), 0.9, emit=(1, 0.16, 0.01), estr=0, noise_bump=1.0, noise_scale=40, color2=(0.05, 0.04, 0.04))
pr = fbm.node_tree.nodes["Principled BSDF"]
ksock(pr.inputs["Emission Strength"], HIT, 9)
ksock(pr.inputs["Emission Strength"], HIT + 60, 2.5)
ksock(pr.inputs["Emission Strength"], N, 0.6)
setmat(fb, fbm)
fb.scale = (0.001,) * 3; fb.keyframe_insert("scale", frame=HIT)
fb.scale = (0.9, 0.9, 1.2); fb.location = (0, 0, 0.03); fb.keyframe_insert("scale", frame=HIT + 15); fb.keyframe_insert("location", frame=HIT + 15)
fb.scale = (1.4, 1.4, 2.6); fb.location = (0, 0, 0.12); fb.keyframe_insert("scale", frame=N); fb.keyframe_insert("location", frame=N)
# dark dust cap
cap = child(ico("cap", 0.12, sub=4, m=mat("dust", (0.12, 0.1, 0.09), 1.0, noise_bump=1.5, noise_scale=20, color2=(0.25, 0.2, 0.17))))
_d2 = cap.modifiers.new("d", 'DISPLACE'); _d2.texture = _tx; _d2.strength = 0.06
cap.scale = (0.001,) * 3; cap.keyframe_insert("scale", frame=HIT + 20)
cap.location = (0, 0, 0.25); cap.keyframe_insert("location", frame=HIT + 20)
cap.scale = (1.6, 1.6, 0.8); cap.location = (0, 0, 0.42); cap.keyframe_insert("scale", frame=N); cap.keyframe_insert("location", frame=N)

# scorch disc
bpy.ops.mesh.primitive_circle_add(vertices=48, radius=0.1, fill_type='NGON', location=(0, 0, 0.002))
sc = child(bpy.context.object)
scm, scmx, sce = emis_fade("scorch", (0.0, 0.0, 0.0), 0)
setmat(sc, scm)
ksock(scmx.inputs[0], HIT, 0.0)
ksock(scmx.inputs[0], HIT + 30, 0.0)
sc.scale = (0.001,) * 3; sc.keyframe_insert("scale", frame=HIT)
sc.scale = (1.3,) * 3; sc.keyframe_insert("scale", frame=HIT + 40)
# make scorch an actual dark surface (no emission): swap emission->diffuse black
nt = scm.node_tree
dif = nt.nodes.new("ShaderNodeBsdfDiffuse"); dif.inputs["Color"].default_value = (0.02, 0.01, 0.005, 1)
nt.links.new(dif.outputs[0], scmx.inputs[2])
ksock(scmx.inputs[0], HIT + 30, 0.9)

# debris
random.seed(3)
dm = emis("debris", (1, 0.45, 0.1), 18)
g = Vector((0, 0, -1.1))
for i in range(70):
    th = random.uniform(0, 2 * math.pi)
    sp = random.uniform(0.35, 0.9)
    up = random.uniform(0.5, 1.4)
    v = Vector((math.cos(th) * sp, math.sin(th) * sp, up))
    d = child(ico("deb", random.uniform(0.012, 0.026), sub=1, m=dm))
    t0 = HIT + random.randint(0, 6)
    life = random.randint(40, 75)
    d.scale = (0.001,) * 3; d.keyframe_insert("scale", frame=t0 - 1)
    d.scale = (1,) * 3; d.keyframe_insert("scale", frame=t0)
    for k in range(0, life + 1, 5):
        tt = k / 30.0
        p = v * tt + 0.5 * g * tt * tt
        if p.z < 0:
            p.z = 0
        d.location = p
        d.keyframe_insert("location", frame=t0 + k)
    d.keyframe_insert("scale", frame=t0 + life - 8)
    d.scale = (0.001,) * 3; d.keyframe_insert("scale", frame=t0 + life)


def ring(name, color, strength, r0, r1, f0, f1, minor=0.006, fade_from=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=minor, major_segments=96, minor_segments=8, location=(0, 0, 0.004))
    o = child(bpy.context.object)
    m, mx, em = emis_fade(name, color, strength)
    setmat(o, m)
    o.scale = (r0, r0, 1); o.keyframe_insert("scale", frame=f0)
    o.scale = (r1, r1, 1); o.keyframe_insert("scale", frame=f1)
    ksock(mx.inputs[0], f0 - 1, 0.0)
    ksock(mx.inputs[0], f0, 1.0)
    ksock(mx.inputs[0], fade_from or int(f0 + (f1 - f0) * 0.6), 1.0)
    ksock(mx.inputs[0], f1, 0.0)
    return o


# shockwaves: one right away, a big one when narrated
ring("sw1", (1, 0.8, 0.6), 12, 0.02, 0.5, HIT + 1, HIT + 35, minor=0.004)
ring("sw2", (1, 0.9, 0.75), 10, 0.05, 1.1, F(5.6), F(7.4), minor=0.006)
ring("sw3", (1, 0.7, 0.4), 8, 0.05, 0.9, F(6.0), F(7.6), minor=0.004)
# tsunamis
for k in range(4):
    f0 = F(7.6) + k * 14
    ring(f"ts{k}", (0.3, 0.8, 1.0), 9, 0.08, 0.85, f0, min(N, f0 + 75), minor=0.008, fade_from=f0 + 50)

mw, mo = txt_mats()
t0 = hud_text(cam, "IMPACTO!", 2.3, 0.6, mo)
pop(t0, HIT + 2, F(2.6))
t1 = hud_text(cam, "BILHÕES DE", 2.45, 0.32, mw)
t2 = hud_text(cam, "BOMBAS ATÔMICAS", 1.95, 0.4, mo)
pop(t1, F(2.9), F(5.3)); pop(t2, F(3.4), F(5.3))
t3 = hud_text(cam, "ONDA DE CHOQUE", 2.3, 0.4, mw)
pop(t3, F(5.7), F(7.5))
t4 = hud_text(cam, "TSUNAMIS", 2.35, 0.55, mo)
t5 = hud_text(cam, "NO GOLFO DO MÉXICO", 1.85, 0.28, mw)
pop(t4, F(7.7)); pop(t5, F(9.3))

run("s3", [HIT + 4, F(4.0), F(6.6), F(9.8)])
