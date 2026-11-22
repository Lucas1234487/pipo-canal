import sys; sys.path.insert(0, "/home/claude/v")
from land import *

F = lambda t: int(30 * (0.3 + t)) + 1
N = 305
s = reset(N)
bloom(s)
L = build_land()
bg, ramp = world_gradient(s, top=(0.08, 0.28, 0.85), bottom=(1.0, 0.62, 0.35), strength=1.0)
sun(direction=(-0.6, 0.8, -0.45), strength=4.0, color=(1.0, 0.88, 0.72), angle=0.05)

cam = camera((0, 0, 0), lens=26)
key_cam(cam, 1, (-1.0, -17.0, 2.2), (2.5, 4, 5.2))
key_cam(cam, N, (1.5, -14.5, 2.6), (2.2, 4, 5.8))

# sauropod neck idle + look up at the sky at the end
neck = L["neck"]
for f, a in ((1, 0.0), (60, 0.06), (120, -0.03), (180, 0.05), (F(6.0), 0.0), (F(6.9), -0.32), (N, -0.34)):
    neck.rotation_euler = (0, a, 0)
    neck.keyframe_insert("rotation_euler", frame=f)
rex = L["rex"]
rz0 = rex.rotation_euler.z
for f, a in ((1, 0), (90, 0.08), (F(6.0), 0.0), (F(6.9), 0.35), (N, 0.36)):
    rex.rotation_euler = (0, 0, rz0 + a)
    rex.keyframe_insert("rotation_euler", frame=f)

# asteroid streak in the sky
ar = link(D.objects.new("ast_root", None))
head = sphere("head", 0.9, seg=16, rings=8, m=emis("headm", (1, 0.7, 0.4), 30))
head.parent = ar
trail(ar, 22, 0.8, strength=10)
p0, p1 = Vector((-40, 140, 95)), Vector((-12, 140, 60))
ar.rotation_euler = (p1 - p0).normalized().to_track_quat('X', 'Z').to_euler()
ar.location = p0 + (p0 - p1)
ar.keyframe_insert("location", frame=F(5.4))
ar.location = p0
ar.keyframe_insert("location", frame=F(6.0))
ar.location = p1
ar.keyframe_insert("location", frame=N)
linear(ar)

mw, mo = txt_mats()
t1 = hud_text(cam, "DINOSSAUROS", 2.35, 0.42, mo)
t2 = hud_text(cam, "+150 MILHÕES DE ANOS", 1.85, 0.24, mw)
t2b = hud_text(cam, "NO TOPO DO PLANETA", 1.5, 0.24, mw)
pop(t1, F(1.1), F(5.6))
pop(t2, F(3.4), F(5.6))
pop(t2b, F(3.7), F(5.6))

run("s1", [F(3.8), N - 5])
