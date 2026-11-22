import sys; sys.path.insert(0, "/home/claude/v")
from lib import *
import lib
lib.HUD_DEPTH = 3.0

F = lambda t: int(30 * (0.3 + t)) + 1
N = 272
s = reset(N)
bloom(s)
bg, ramp = world_gradient(s, top=(0.01, 0.01, 0.02), bottom=(0.06, 0.04, 0.05), strength=1.0)

# pedestal
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=4.2, depth=3, location=(0, 0, -1.5))
ped = bpy.context.object
smooth(ped)
bv = ped.modifiers.new("b", 'BEVEL'); bv.width = 0.08; bv.segments = 3
setmat(ped, mat("ped", (0.08, 0.07, 0.07), 0.35))
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -3))
setmat(bpy.context.object, mat("floor", (0.02, 0.02, 0.025), 0.5))

# lights
kl = D.lights.new("key", 'SPOT'); kl.energy = 1100; kl.spot_size = math.radians(55); kl.spot_blend = 0.4; kl.shadow_soft_size = 1.0
ko = link(D.objects.new("key", kl)); ko.location = (3, -7, 9); look(ko, (0, 0, 0.5))
rl = D.lights.new("rim", 'AREA'); rl.energy = 900; rl.size = 4; rl.color = (0.6, 0.7, 1.0)
ro = link(D.objects.new("rim", rl)); ro.location = (-3, 6, 5); look(ro, (0, 0, 1))

mw = mat("eyew", (1, 1, 1), 0.2)
mb = mat("eyeb", (0.01, 0.01, 0.01), 0.1)
specs = []
m1 = mat("f1", (0.22, 0.50, 0.36), 0.5, color2=(0.14, 0.36, 0.26), noise_scale=1.5)
r1, n1 = sauropod(m1, mw, mb, loc=(-1.9, 0.7, 0), rotz=math.radians(-110), scale=0.12)
m2 = mat("f2", (0.78, 0.38, 0.14), 0.5, color2=(0.55, 0.22, 0.08), noise_scale=2)
r2 = trex(m2, mw, mb, loc=(-0.55, -0.3, 0), rotz=math.radians(-110), scale=0.18)
m3 = mat("f3", (0.5, 0.25, 0.6), 0.5, color2=(0.35, 0.15, 0.45), noise_scale=2)
r3 = trex(m3, mw, mb, loc=(1.95, 0.7, 0), rotz=math.radians(-70), scale=0.16)
m4 = mat("f4", (0.05, 0.3, 0.85), 0.45, color2=(0.02, 0.15, 0.55), noise_scale=3)
r4, b4 = raptor(m4, loc=(0, 0, 0), rotz=0, scale=1.0)
bpy.context.view_layer.update()
eyes(r4, (1.55, 0, 2.98), 0.1, 0.17, mw, mb)
r4.location = (0.75, -1.0, 0); r4.rotation_euler = (0, 0, math.radians(-75)); r4.scale = (0.42,) * 3

stone = (0.32, 0.31, 0.30)
for i, (root, m) in enumerate(((r1, m1), (r3, m3), (r2, m2))):
    f0 = F(3.6) + i * 9
    mix = [n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeMix"][0]
    p = m.node_tree.nodes["Principled BSDF"]
    ksock(mix.inputs[6], f0, tuple(mix.inputs[6].default_value))
    ksock(mix.inputs[7], f0, tuple(mix.inputs[7].default_value))
    ksock(mix.inputs[6], f0 + 12, (*stone, 1))
    ksock(mix.inputs[7], f0 + 12, (0.2, 0.2, 0.2, 1))
    ksock(p.inputs["Roughness"], f0 + 12, 1.0)
    z = root.location.z
    root.keyframe_insert("location", frame=F(5.4) + i * 6)
    root.location.z = z - 2.2
    root.keyframe_insert("location", frame=F(6.6) + i * 6)
    root.keyframe_insert("rotation_euler", frame=F(5.4) + i * 6)
    root.rotation_euler.y += 0.3
    root.keyframe_insert("rotation_euler", frame=F(6.6) + i * 6)
# survivor hop
for f, z in ((F(7.0), 0.0), (F(7.2), 0.35), (F(7.4), 0.0), (F(7.6), 0.25), (F(7.8), 0.0)):
    r4.location.z = z
    r4.keyframe_insert("location", frame=f)

cam = camera((0, 0, 0), lens=35)
key_cam(cam, 1, (0, -8.6, 1.9), (0, 0, 1.75))
key_cam(cam, N, (0, -7.6, 1.7), (0, 0, 1.6))

red = mat("big", (1, 0.1, 0.05), 0.4, emit=(1, 0.08, 0.03), estr=1.6)
big = text3d("75%", size=2.2, extrude=0.25, m=red, loc=(0, 1.5, 3.7))
big.visible_shadow = False
pop(big, F(1.4), dur=10)
mwt, mo = txt_mats()
t1 = hud_text(cam, "DAS ESPÉCIES", -1.9, 0.36, mwt)
t2 = hud_text(cam, "SUMIRAM", -2.45, 0.42, mo)
pop(t1, F(2.6), F(5.3)); pop(t2, F(3.8), F(5.3))
t3 = hud_text(cam, "INCLUSIVE OS", -1.9, 0.3, mwt)
t4 = hud_text(cam, "GRANDES DINOSSAUROS", -2.45, 0.3, mo)
pop(t3, F(5.5)); pop(t4, F(6.2))

run("s5", [F(3.0), N - 3])
