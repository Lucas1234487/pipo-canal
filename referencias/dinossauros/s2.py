import sys; sys.path.insert(0, "/home/claude/v")
from lib import *
import lib
lib.HUD_DEPTH = 0.45

F = lambda t: int(30 * (0.3 + t)) + 1
N = 410
s = reset(N)
bloom(s)
world_stars(s)
LAT, LON = 21.4, -89.5
root, e, _, _ = earth(3.0, texdir=f"{DIR}/tex4k")
D.materials["earthm"].node_tree.nodes["cloudamt"].inputs[1].default_value = 0.0
ca = D.materials["earthm"].node_tree.nodes["cloudamt"].inputs[1]
ksock(ca, 1, 0.8)
ksock(ca, F(1.5), 0.1)
rz = math.radians(-90 - LON)
root.rotation_euler = (math.radians(LAT - 10), 0, rz - math.radians(75))
root.keyframe_insert("rotation_euler", frame=1)
root.rotation_euler = (math.radians(LAT), 0, rz)
root.keyframe_insert("rotation_euler", frame=F(1.6))
root.rotation_euler = (math.radians(LAT), 0, rz + math.radians(1.5))
root.keyframe_insert("rotation_euler", frame=N)
sun(direction=(0.55, 0.75, -0.45), strength=4.5)

cam = camera((0, -12, 0), lens=35)
key_cam(cam, 1, (0, -11.0, 0.6), (0, 0, 0.6))
key_cam(cam, F(1.4), (0, -9.5, 0.2), (0, 0, 0.2))
key_cam(cam, F(4.4), (0, -5.0, 0.15), (0, 0, 0.12))
key_cam(cam, F(5.4), (0, -5.0, 0.12), (0, 0, 0.1))
key_cam(cam, F(8.2), (0.03, -4.5, 0.02), (0, -3, 0.0))
key_cam(cam, N, (0.03, -4.4, 0.02), (0, -3, 0.0))

# marker objects on the globe
pos = latlon(LAT, LON, 3.0)
nrm = pos.normalized()
q = nrm.to_track_quat('Z', 'Y')
anchor = link(D.objects.new("anchor", None))
anchor.parent = root
anchor.location = pos
anchor.rotation_euler = q.to_euler()

red = mat("pinred", (0.9, 0.05, 0.05), 0.3, emit=(1, 0.05, 0.02), estr=1.5)
pin = link(D.objects.new("pin", None))
pin.parent = anchor
bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=0.05, radius2=0.0, depth=0.22, location=(0, 0, 0.11), rotation=(math.pi, 0, 0))
c = bpy.context.object; smooth(c); setmat(c, red); c.parent = pin
h = sphere("pinhead", 0.075, loc=(0, 0, 0.25), m=red); h.parent = pin
for x in (c, h): x.visible_shadow = False
pin.scale = (0.001,) * 3
pin.keyframe_insert("scale", frame=F(1.1))
pin.scale = (1.3,) * 3
pin.keyframe_insert("scale", frame=F(1.5))
pin.scale = (1.0,) * 3
pin.keyframe_insert("scale", frame=F(1.8))
pin.keyframe_insert("scale", frame=F(4.4))
pin.scale = (0.28,) * 3
pin.keyframe_insert("scale", frame=F(5.6))
pin.keyframe_insert("scale", frame=F(6.0))
pin.scale = (0.001,) * 3
pin.keyframe_insert("scale", frame=F(6.6))

# pulse rings
for k in range(3):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.008, location=(0, 0, 0.005))
    r = bpy.context.object
    m, mx, em = emis_fade(f"pulse{k}", (1, 0.1, 0.05), 6)
    setmat(r, m)
    r.parent = anchor
    r.visible_shadow = False
    f0 = F(1.3) + k * 25
    r.scale = (0.2,) * 3; r.keyframe_insert("scale", frame=f0)
    r.scale = (2.2,) * 3; r.keyframe_insert("scale", frame=f0 + 40)
    r.scale = (0.001,) * 3; r.keyframe_insert("scale", frame=f0 + 41)
    ksock(mx.inputs[0], f0 - 1, 0.0)
    ksock(mx.inputs[0], f0, 1.0)
    ksock(mx.inputs[0], f0 + 40, 0.0)

# crater ring (~180 km => radius 0.042 units on r=3 earth)
bpy.ops.mesh.primitive_torus_add(major_radius=0.043, minor_radius=0.005, major_segments=64, minor_segments=8, location=(0, 0, 0.002))
cr = bpy.context.object
cm, cmx, cem = emis_fade("crater", (1.0, 0.25, 0.05), 5)
setmat(cr, cm)
cr.parent = anchor
cr.visible_shadow = False
ksock(cmx.inputs[0], 1, 0.0)
ksock(cmx.inputs[0], F(5.5), 0.0)
ksock(cmx.inputs[0], F(6.0), 1.0)
ksock(cmx.inputs[0], F(9.6), 1.0)
ksock(cmx.inputs[0], F(10.4), 0.35)
cr.scale = (0.3,) * 3; cr.keyframe_insert("scale", frame=F(5.5))
cr.scale = (1.0,) * 3; cr.keyframe_insert("scale", frame=F(6.3))
# crater diameter line
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.0012, depth=0.086, location=(0, 0, 0.003), rotation=(0, math.pi / 2, 0))
ln = bpy.context.object
lm, lmx, lem = emis_fade("dline", (1, 1, 1), 3)
setmat(ln, lm)
ln.parent = anchor
ln.visible_shadow = False
ksock(lmx.inputs[0], 1, 0.0)
ksock(lmx.inputs[0], F(7.4), 0.0)
ksock(lmx.inputs[0], F(7.8), 1.0)
ksock(lmx.inputs[0], F(9.6), 1.0)
ksock(lmx.inputs[0], F(10.0), 0.0)

mw, mo = txt_mats()
t1 = hud_text(cam, "PENÍNSULA DE IUCATÃ", 2.35, 0.27, mw)
t2 = hud_text(cam, "MÉXICO", 1.9, 0.45, mo)
pop(t1, F(1.8), F(4.6))
pop(t2, F(3.2), F(4.6))
t3 = hud_text(cam, "CRATERA", 2.45, 0.3, mw)
t4 = hud_text(cam, "CHICXULUB", 1.95, 0.5, mo)
pop(t3, F(4.7), F(9.5))
pop(t4, F(5.8), F(9.5))
t5 = hud_text(cam, "~180 km", -2.2, 0.45, mw)
pop(t5, F(7.6), F(9.5))
t6 = hud_text(cam, "HOJE: ESCONDIDA", 2.35, 0.32, mw)
t7 = hud_text(cam, "SOB TERRA E MAR", 1.85, 0.32, mo)
pop(t6, F(9.8))
pop(t7, F(10.6))

run("s2", [F(3.5), F(7.9), F(11.0)])
