"""Estilo do PipoPop 2D: paletas, traço com tremidinha (line boil), sombra chapada, texto com contorno, textura de papel.
Tudo em pycairo. Unidades em pixels de um quadro 1080x1920."""
import math, os, random, shutil, subprocess
import cairo
import numpy as np

W, H, FPS = 1080, 1920, 30
INK = (0.102, 0.059, 0.141)          # contorno escuro (mesmo tom da legenda do compose)
LW = 6.0                              # contorno principal (spec: 3 a 6 px)
FONT = "Fredoka Light"                # Fredoka-700 do kit (família registrada assim no fontconfig)


def garante_fonte():
    """Registra kit/Fredoka-700.ttf no fontconfig do usuário (uma vez)."""
    dst = os.path.expanduser("~/.local/share/fonts/Fredoka-700.ttf")
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kit", "Fredoka-700.ttf"), dst)
        subprocess.run(["fc-cache", "-f"], capture_output=True)


def hexc(h):
    if isinstance(h, (list, tuple)):
        return tuple(v / 255 if v > 1 else v for v in h[:3])
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def mix(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def escurece(c, k=0.22):
    return mix(c, INK, k)


def clareia(c, k=0.3):
    return mix(c, (1, 1, 1), k)


# Paletas saturadas (fundo, fundo2/padrão, destaque1, destaque2, destaque3). Nada de pastel.
PALETAS = {
    "tomate":   ["#E8452C", "#D23A22", "#FFD21F", "#2A7DE1", "#FFF3E0"],
    "mostarda": ["#F2B705", "#E0A500", "#E8452C", "#1F5FD1", "#FFF6DA"],
    "petroleo": ["#0E6B73", "#0B5C63", "#FFC21A", "#FF5A3C", "#E9FFF8"],
    "uva":      ["#5B2A86", "#4E2275", "#FFC21A", "#FF5A8A", "#F3E8FF"],
    "menta":    ["#16A57A", "#12906A", "#FFD21F", "#E8452C", "#EFFFF7"],
    "cobalto":  ["#2747C9", "#1F3CB0", "#FFC21A", "#FF5A3C", "#EAF0FF"],
    "noite":    ["#1D1B3A", "#252248", "#FFC21A", "#38D1C6", "#E8E6FF"],
    "rosa":     ["#E83E7C", "#D2306C", "#FFD21F", "#1F5FD1", "#FFF0F6"],
    "laranja":  ["#F57C1F", "#E06A10", "#2A3FD1", "#FFE14D", "#FFF4E6"],
}
AMARELO = hexc("#FFC21A")
BRANCO = hexc("#FFF8EC")
VERMELHO = hexc("#E8352A")
VERDE = hexc("#3DAA3A")


def paleta(nome):
    p = PALETAS.get(nome or "tomate", PALETAS["tomate"])
    return [hexc(c) for c in p]


# ---------- formas com traço vivo
_boil = {"q": 0}


def set_boil(frame):
    """O traço 'ferve' a 12 desenhos por segundo, como animação feita à mão."""
    _boil["q"] = frame // 3


def jitter(pts, amp, seed):
    if amp <= 0:
        return pts
    r = random.Random(seed * 7919 + _boil["q"] * 104729)
    return [(x + r.uniform(-amp, amp), y + r.uniform(-amp, amp)) for x, y in pts]


def path_suave(ctx, pts, fechado=True):
    """Catmull-Rom -> Bézier pelos pontos."""
    n = len(pts)
    if n < 3:
        ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]; return
    ctx.move_to(*pts[0])
    rng = range(n) if fechado else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (fechado or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (fechado or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        ctx.curve_to(*c1, *c2, *p2)
    if fechado:
        ctx.close_path()


def pts_elipse(cx, cy, rx, ry, n=26):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def pts_ret(x, y, w, h, r=14, por_canto=4):
    """Retângulo de cantos arredondados como lista de pontos (para o traço tremido)."""
    r = max(2, min(r, w / 2, h / 2))
    out = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(por_canto + 1):
            a = math.radians(a0 + 90 * k / por_canto)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    # pontos no meio das retas longas, para o tremido aparecer nelas também
    full = []
    for i, p in enumerate(out):
        full.append(p)
        q = out[(i + 1) % len(out)]
        d = math.hypot(q[0] - p[0], q[1] - p[1])
        for s in range(1, int(d // 90) + 1):
            k = s / (int(d // 90) + 1)
            full.append((p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k))
    return full


def forma(ctx, pts, cor, sombra=True, sombreado=0.0, lw=LW, seed=1, amp=1.6, sombra_off=(10, 12), cor_sombreado=None, contorno=INK):
    """Desenha a forma no estilo da casa: sombra chapada, preenchimento, meia-lua de sombreado e contorno grosso."""
    p = jitter(pts, amp, seed)
    if sombra:
        ctx.save(); ctx.translate(*sombra_off)
        path_suave(ctx, p); ctx.set_source_rgba(*INK, 0.30); ctx.fill(); ctx.restore()
    path_suave(ctx, p)
    ctx.set_source_rgb(*cor); ctx.fill_preserve()
    if sombreado:
        ctx.save(); ctx.clip()
        xs = [a for a, _ in p]; ys = [b for _, b in p]
        dx = (max(xs) - min(xs)) * sombreado; dy = (max(ys) - min(ys)) * sombreado * 0.6
        ctx.set_source_rgb(*(cor_sombreado or escurece(cor, 0.2)))
        ctx.paint()
        ctx.translate(-dx, -dy); path_suave(ctx, p); ctx.set_source_rgb(*cor); ctx.fill()
        ctx.restore()
        path_suave(ctx, p)
    if lw and contorno is not None:
        ctx.set_line_width(lw); ctx.set_source_rgb(*contorno); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
    else:
        ctx.new_path()


def traco(ctx, pts, lw=LW, cor=INK, seed=3, amp=1.2, alpha=1.0):
    p = jitter(pts, amp, seed)
    path_suave(ctx, p, fechado=False)
    ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgba(*cor, alpha); ctx.stroke()


def texto(ctx, s, x, y, tam, cor=BRANCO, contorno=INK, lw=None, ancora="c", sombra=True, max_w=None):
    """Texto com contorno grosso e sombra chapada. ancora: c (centro), l (esquerda), r (direita). Devolve a caixa."""
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(tam)
    xb, yb, tw, th, xa, _ = ctx.text_extents(s)
    if max_w and tw > max_w:
        tam = tam * max_w / tw; ctx.set_font_size(tam)
        xb, yb, tw, th, xa, _ = ctx.text_extents(s)
    lw = lw if lw is not None else max(4, tam * 0.11)
    fe = ctx.font_extents()
    cap = tam * 0.72
    ox = {"c": -tw / 2 - xb, "l": -xb, "r": -tw - xb}[ancora]
    oy = cap / 2
    if sombra:
        ctx.save(); ctx.translate(x + ox + tam * 0.05, y + oy + tam * 0.07); ctx.move_to(0, 0); ctx.text_path(s)
        ctx.set_line_width(lw * 2); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_source_rgba(*INK, 0.35)
        ctx.stroke_preserve(); ctx.fill(); ctx.restore()
    ctx.move_to(x + ox, y + oy); ctx.text_path(s)
    if contorno is not None:
        ctx.set_line_width(lw * 2); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_source_rgb(*contorno); ctx.stroke_preserve()
    ctx.set_source_rgb(*cor); ctx.fill()
    x0 = x + ox + xb - lw
    return (x0, y + oy + yb - lw, x0 + tw + 2 * lw, y + oy + yb + th + lw)


def medir(ctx, s, tam):
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(tam)
    return ctx.text_extents(s)[2]


# ---------- textura de papel e grão (pré-calculada uma vez por processo)
def textura(seed=5):
    rng = np.random.default_rng(seed)
    big = (H + 64, W + 64)
    # manchas de papel (baixa frequência) + fibras + grão fino
    low = rng.normal(0, 1, (big[0] // 48 + 2, big[1] // 48 + 2))
    low = np.kron(low, np.ones((48, 48)))[:big[0], :big[1]]
    k = np.ones(31) / 31
    low = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 1, low)
    low = np.apply_along_axis(lambda c: np.convolve(c, k, mode="same"), 0, low)
    fine = rng.normal(0, 1, big)
    v = low * 0.30 + fine * 0.55
    yy, xx = np.mgrid[0:big[0], 0:big[1]]
    vig = ((xx / big[1] - 0.5) ** 2 + (yy / big[0] - 0.5) ** 2 * 0.7)
    dark = np.clip(-v, 0, None) * 0.045 + vig * 0.22           # alfa do escuro (grão + vinheta leve)
    light = np.clip(v, 0, None) * 0.035
    a = np.clip(dark + light, 0, 0.5)
    lum = np.where(v < 0, 0.10, 1.0)                              # cor do grão: tinta ou papel
    lum = np.where(dark > light, 0.10, lum)
    argb = np.zeros(big + (4,), np.uint8)
    pm = (lum * a * 255).astype(np.uint8)
    argb[..., 0] = pm; argb[..., 1] = (pm * 0.97).astype(np.uint8); argb[..., 2] = (pm * 0.92).astype(np.uint8)
    argb[..., 3] = (a * 255).astype(np.uint8)
    argb = np.ascontiguousarray(argb)
    surf = cairo.ImageSurface.create_for_data(memoryview(argb), cairo.FORMAT_ARGB32, big[1], big[0], big[1] * 4)
    return surf, argb


def aplica_textura(ctx, tex, frame):
    r = random.Random(frame // 2)
    ctx.save(); ctx.identity_matrix()
    ctx.set_source_surface(tex, -r.randint(0, 63), -r.randint(0, 63)); ctx.paint(); ctx.restore()


# ---------- curvas de movimento
def ease_out_back(x, s=1.9):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_in_out(x):
    return x * x * (3 - 2 * x)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in_back(x, s=1.7):
    return (s + 1) * x ** 3 - s * x ** 2


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))
