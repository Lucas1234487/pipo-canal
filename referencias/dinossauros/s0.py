import sys; sys.path.insert(0, "/home/claude/v")
from lib import *

F = lambda t: int(30 * (0.3 + t)) + 1
N = 300
s = reset(N, samples=8)
bloom(s)
world_stars(s, strength=1.0)

root, e, cl, at = earth(3.0)
root.rotation_euler = (math.radians(20), 0, math.radians(-150))
root.keyframe_insert("rotation_euler", frame=1)
root.rotation_euler = (math.radians(20), 0, math.radians(-128))
root.keyframe_insert("rotation_euler", frame=N)
sun(direction=(-1, 0.55, -0.35), strength=5.0)

cam = camera((0, -13.5, 3.2), (0, 0, 1.2), lens=35)
key_cam(cam, 1, (0, -13.5, 3.2), (0, 0, 1.4))
key_cam(cam, N, (0.8, -11.2, 2.6), (0.4, 0, 1.6))

# asteroid
ar = link(D.objects.new("ast_root", None))
a = asteroid(0.32)
a.parent = ar
tr = trail(ar, 6.0, 0.3)
p0, p1 = Vector((9.0, 6.0, 12.0)), Vector((1.7, -3.6, 4.1))
dirv = (p1 - p0).normalized()
ar.rotation_euler = dirv.to_track_quat('X', 'Z').to_euler()
ar.location = p0
ar.keyframe_insert("location", frame=1)
ar.location = p1
ar.keyframe_insert("location", frame=N)
linear(ar)
a.rotation_euler = (0, 0, 0)
a.keyframe_insert("rotation_euler", frame=1)
a.rotation_euler = (2.0, 1.2, 3.0)
a.keyframe_insert("rotation_euler", frame=N)
point((0, 0, 0), 0)  # dummy
glow = point((0, 0, 0), 300, color=(1, 0.5, 0.15), radius=0.3)
glow.parent = ar

# HUD text
mw = mat("txt", (1, 1, 1), 0.4, emit=(1, 1, 1), estr=0.7)
mo = mat("txto", (1, 0.55, 0.15), 0.4, emit=(1, 0.5, 0.1), estr=1.2)
t1 = hud_text(cam, "66 MILHÕES", 2.35, 0.52, mo)
t2 = hud_text(cam, "DE ANOS ATRÁS", 1.75, 0.34, mw)
pop(t1, F(0.1), F(3.0))
pop(t2, F(0.9), F(3.0))
t3 = hud_text(cam, "~10 km", 2.3, 0.5, mo)
t3b = hud_text(cam, "DE LARGURA", 1.8, 0.3, mw)
pop(t3, F(3.4), F(6.0)); pop(t3b, F(3.6), F(6.0))
t4 = hud_text(cam, "72.000 km/h", 2.3, 0.45, mo)
pop(t4, F(6.6))

run("s0", [100, 290])
