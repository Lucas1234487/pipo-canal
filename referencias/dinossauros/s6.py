import sys; sys.path.insert(0, "/home/claude/v")
from lib import *
import lib
lib.HUD_DEPTH = 3.0

F = lambda t: int(30 * (0.3 + t)) + 1
N = 480
s = reset(N)
bloom(s)
bg, ramp = world_gradient(s, top=(0.0, 0.0, 0.0), bottom=(0.02, 0.03, 0.06), strength=1.0)
ksock(bg.inputs["Strength"], F(11.4), 1.0)
ksock(bg.inputs["Strength"], F(13.6), 0.0)

bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
setmat(bpy.context.object, mat("gr", (0.03, 0.03, 0.035), 0.6, noise_bump=0.3, noise_scale=2))
# a few rocks
rm = mat("rk", (0.06, 0.06, 0.065), 0.8, noise_bump=0.8, noise_scale=6)
for x, y, r in ((-2.6, 2, 0.7), (2.4, 3, 1.0), (-1.2, 5, 0.5), (3.5, -0.5, 0.4)):
    o = ico("rock", r, loc=(x, y, r * 0.3), sub=3, m=rm)
    o.scale.z = 0.6

mw = mat("eyew", (1, 1, 1), 0.2)
mb = mat("eyeb", (0.01, 0.01, 0.01), 0.1)
m4 = mat("f4", (0.05, 0.3, 0.85), 0.45, color2=(0.02, 0.15, 0.55), noise_scale=3)
rr, body = raptor(m4)
bpy.context.view_layer.update()
eyes(rr, (1.55, 0, 2.98), 0.1, 0.17, mw, mb)
# feather crest + tail fan
fm = mat("feather", (0.9, 0.6, 0.1), 0.5)
for i, (x, z, rot) in enumerate(((1.15, 3.1, -0.5), (0.95, 3.0, -0.8), (0.78, 2.85, -1.0))):
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.08, depth=0.45, location=(x, 0, z), rotation=(0, rot, 0))
    c = bpy.context.object; smooth(c); setmat(c, fm); c.parent = rr
rr.location = (0, 0, 0)
rr.rotation_euler = (0, 0, math.radians(200))
rr.scale = (0.9,) * 3
# idle bob + head turn to camera at "Quem sao eles?"
for f, rz in ((1, 200), (F(9.4), 200), (F(10.0), 245), (N, 247)):
    rr.rotation_euler = (0, 0, math.radians(rz))
    rr.keyframe_insert("rotation_euler", frame=f)
for f in range(1, N, 20):
    rr.location.z = 0.04 if (f // 20) % 2 else 0.0
    rr.keyframe_insert("location", frame=f)

# lights: rim from behind (appears when "sobreviveram"), dim key
rim = D.lights.new("rim", 'AREA'); rim.size = 3; rim.color = (0.5, 0.65, 1.0)
ro = link(D.objects.new("rim", rim)); ro.location = (-1, 5, 4); look(ro, (0, 0, 1.6))
key = D.lights.new("key", 'SPOT'); key.spot_size = math.radians(40); key.spot_blend = 0.6; key.color = (1, 0.85, 0.7)
ko = link(D.objects.new("key", key)); ko.location = (2.5, -5, 5); look(ko, (0, 0, 1.6))
for f, er, ek in ((1, 60, 0), (F(5.0), 60, 0), (F(5.9), 1600, 250), (F(9.4), 1600, 250), (F(10.0), 2200, 650),
                  (F(11.4), 2200, 650), (F(13.4), 0, 0), (N, 0, 0)):
    rim.energy = er; rim.keyframe_insert("energy", frame=f)
    key.energy = ek; key.keyframe_insert("energy", frame=f)

cam = camera((0, 0, 0), lens=40)
key_cam(cam, 1, (0.6, -9.5, 2.3), (0, 0, 2.2))
key_cam(cam, F(9.4), (0.3, -6.8, 2.0), (0, 0, 2.0))
key_cam(cam, F(13.4), (0.15, -5.4, 2.0), (0, 0, 2.1))
key_cam(cam, N, (0.1, -5.2, 2.0), (0, 0, 2.1))

mwt, mo = txt_mats()
lib_depth = 3.0
t1 = hud_text(cam, "NEM TODOS OS DINOSSAUROS", 2.45, 0.27, mwt)
t2 = hud_text(cam, "MORRERAM", 1.95, 0.5, mo)
pop(t1, F(2.6), F(6.6)); pop(t2, F(3.9), F(6.6))
t3 = hud_text(cam, "VOCÊ PROVAVELMENTE", 2.45, 0.3, mwt)
t4 = hud_text(cam, "VIU UM HOJE", 1.95, 0.45, mo)
pop(t3, F(6.8), F(9.4)); pop(t4, F(7.7), F(9.4))
q = hud_text(cam, "?", 2.0, 1.5, mo)
pop(q, F(9.6), F(13.2), dur=10)
t5 = hud_text(cam, "PRÓXIMO VÍDEO...", -2.4, 0.38, mwt)
pop(t5, F(11.6), F(13.6))

run("s6", [F(4.0), F(8.0), F(10.6), F(12.5)])
