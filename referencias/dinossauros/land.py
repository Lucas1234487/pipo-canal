import sys; sys.path.insert(0, "/home/claude/v")
from lib import *


def build_land():
    random.seed(7)
    g, gm = landscape(size=200, gcolor=(0.13, 0.30, 0.08), gcolor2=(0.30, 0.38, 0.10))
    tx = g.modifiers["disp"].texture
    tx.noise_scale = 14
    g.modifiers["disp"].strength = 3.0
    g.location.z = -1.5
    bpy.context.view_layer.update()

    m_trunk = mat("trunk", (0.25, 0.15, 0.08), 0.9)
    m_leaf = mat("leaf", (0.06, 0.25, 0.08), 0.8, noise_bump=0.2, noise_scale=3, color2=(0.12, 0.35, 0.1))
    trees = []
    pts = []
    for i in range(34):
        for _ in range(30):
            x = random.uniform(-45, 45)
            y = random.uniform(8, 70)
            if abs(x - 5) < 6 and y < 14:
                continue
            if all((x - a) ** 2 + (y - b) ** 2 > 16 for a, b in pts):
                break
        pts.append((x, y))
        z = ground_z(x, y, g)
        trees += conifer((x, y, z - 0.2), h=random.uniform(6, 11), m_trunk=m_trunk, m_leaf=m_leaf)
    # some near trees on the left/right edges
    for x, y in ((-9, -2), (12, 2), (-14, 6)):
        trees += conifer((x, y, ground_z(x, y, g) - 0.2), h=9, m_trunk=m_trunk, m_leaf=m_leaf)
    # bushes
    m_bush = mat("bush", (0.10, 0.32, 0.08), 0.8, noise_bump=0.4, noise_scale=4, color2=(0.2, 0.42, 0.1))
    bushes = []
    for i in range(26):
        x = random.uniform(-12, 14)
        y = random.uniform(-10, 10)
        if -6 < x < 9 and -7 < y < 9:
            continue
        b = ico("bush", random.uniform(0.6, 1.3), loc=(x, y, ground_z(x, y, g) + 0.1), sub=2, m=m_bush)
        b.scale.z = 0.6
        bushes.append(b)
    # distant volcanoes / mountains
    m_mtn = mat("mtn", (0.30, 0.24, 0.20), 0.9, noise_bump=0.5, noise_scale=0.3, color2=(0.22, 0.2, 0.18))
    for x, h, r in ((-60, 28, 30), (-20, 22, 26), (30, 34, 32), (75, 24, 28)):
        bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r, radius2=r * 0.12, depth=h, location=(x, 110, h / 2 - 2))
        c = bpy.context.object
        smooth(c)
        setmat(c, m_mtn)

    mw = mat("eyew", (1, 1, 1), 0.2)
    mb = mat("eyeb", (0.01, 0.01, 0.01), 0.1)
    m_sau = mat("sau", (0.22, 0.50, 0.36), 0.55, noise_bump=0.25, noise_scale=1.5, color2=(0.14, 0.36, 0.26))
    m_rex = mat("rex", (0.78, 0.38, 0.14), 0.5, noise_bump=0.25, noise_scale=2.0, color2=(0.55, 0.22, 0.08))
    sx, sy = 5.0, 7.0
    sroot, neck = sauropod(m_sau, mw, mb, loc=(sx, sy, ground_z(sx, sy, g) - 0.1), rotz=math.radians(200), scale=1.0)
    tx_, ty_ = -1.2, -2.0
    rex = trex(m_rex, mw, mb, loc=(tx_, ty_, ground_z(tx_, ty_, g) - 0.05), rotz=math.radians(-35), scale=0.85)
    return dict(ground=g, gm=gm, trees=trees, m_leaf=m_leaf, m_trunk=m_trunk, m_bush=m_bush, bushes=bushes,
                sau=sroot, neck=neck, rex=rex, m_sau=m_sau, m_rex=m_rex)
