"""Fundos abstratos animados do PipoPop 2D (cenário `chapado` e tela do cenário `celular`) e transições de corte.

Cada padrão desenha a tela inteira (com folga para câmera/tremida) e termina com uma "calmaria" radial no centro,
para não brigar com texto e personagem. Opções lidas da cena: `energia` (0..1, padrão 0,6), `calma` (0..1),
`velocidade` (espiral), `ceu` (dia, tarde, noite). A textura de papel é aplicada depois pelo render.
"""
import math, random, zlib
import cairo
from estilo import W, H, INK, BRANCO, VERMELHO, VERDE, hexc, mix, escurece, clareia, jitter, traco, clamp, ease_in_out

M = 90                       # folga fora da tela (câmera, tremida, zoom < 1)
X0, Y0, X1, Y1 = -M, -M, W + M, H + M
CX, CY = W / 2, H * 0.40     # "centro de atenção" (onde ficam Pipo e texto)
_CACHE = {}


# ======================= utilidades =======================
def _grad_v(ctx, stops, y0=Y0, y1=Y1):
    g = cairo.LinearGradient(0, y0, 0, y1)
    for p, c in stops:
        g.add_color_stop_rgb(p, *c)
    ctx.set_source(g); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()


# Camadas suaves (gradientes grandes, brilhos, desfoque) são desenhadas em 1/4 da resolução e ampliadas com
# filtro bilinear: gradiente radial de tela cheia custa ~30 ms em resolução cheia e ~2 ms assim.
LS = 4
LO_W, LO_H = int((X1 - X0) / LS) + 2, int((Y1 - Y0) / LS) + 2


def _lo(opaco=True, chave="lo"):
    """Contexto de baixa resolução em coordenadas de tela (mesmo X/Y do ctx principal)."""
    if chave not in _CACHE:
        _CACHE[chave] = cairo.ImageSurface(cairo.FORMAT_ARGB32, LO_W, LO_H)
    s = _CACHE[chave]; c = cairo.Context(s)
    if not opaco:
        c.set_operator(cairo.OPERATOR_CLEAR); c.paint(); c.set_operator(cairo.OPERATOR_OVER)
    c.scale(1 / LS, 1 / LS); c.translate(-X0, -Y0)
    return s, c


def _cola(ctx, s, alpha=1.0):
    s.flush()
    ctx.save(); ctx.translate(X0, Y0); ctx.scale(LS, LS)
    pat = cairo.SurfacePattern(s); pat.set_filter(cairo.FILTER_BILINEAR); pat.set_extend(cairo.EXTEND_PAD)
    ctx.set_source(pat); ctx.rectangle(0, 0, LO_W, LO_H)
    if alpha < 1:
        ctx.clip(); ctx.paint_with_alpha(alpha)
    else:
        ctx.fill()
    ctx.restore()


def _calma_grad(c, cor, k, raio=780):
    g = cairo.RadialGradient(CX, CY, 0, CX, CY, raio)
    g.add_color_stop_rgba(0, *cor, k); g.add_color_stop_rgba(0.55, *cor, k * 0.65); g.add_color_stop_rgba(1, *cor, 0)
    c.set_source(g); c.rectangle(CX - raio, CY - raio, 2 * raio, 2 * raio); c.fill()


def _calma(ctx, cor, k, raio=780):
    """Baixa o contraste no centro de atenção (radial na cor de base do padrão), em camada cacheada."""
    if k <= 0:
        return
    ch = ("calma", tuple(round(v, 3) for v in cor), round(k, 3), raio)
    if ch not in _CACHE:
        s, c = _lo(False, chave=ch); _calma_grad(c, cor, k, raio); s.flush()
    _cola(ctx, _CACHE[ch])


def _poli(ctx, pts, cor, lw=5, alpha=1.0, seed=1, amp=1.4, sombra=True):
    """Polígono de quinas vivas com traço tremido (line boil) e sombra chapada."""
    p = jitter(pts, amp, seed)
    if sombra:
        ctx.move_to(p[0][0] + 7, p[0][1] + 9)
        for x, y in p[1:]:
            ctx.line_to(x + 7, y + 9)
        ctx.close_path(); ctx.set_source_rgba(*INK, 0.28 * alpha); ctx.fill()
    ctx.move_to(*p[0])
    for q in p[1:]:
        ctx.line_to(*q)
    ctx.close_path(); ctx.set_source_rgba(*cor, alpha); ctx.fill_preserve()
    ctx.set_line_width(lw); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.set_source_rgba(*INK, alpha); ctx.stroke()


def _rng(*k):
    return random.Random(zlib.crc32(repr(k).encode()))   # determinístico entre processos (hash() de str não é)


# ======================= 1. gradiente vivo =======================
def gradiente_vivo(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    c0, c1, c2 = escurece(bg, 0.22), mix(bg, a2, 0.55), mix(bg, a1, 0.50)
    lo, ctx_ = _lo(True); dst = ctx; ctx = ctx_
    ang = t * (0.10 + 0.22 * en) + seed
    dx, dy = math.cos(ang) * 1150, math.sin(ang) * 1150
    g = cairo.LinearGradient(CX - dx, H / 2 - dy, CX + dx, H / 2 + dy)
    b = 0.5 + 0.12 * math.sin(t * 0.9)                      # respira
    g.add_color_stop_rgb(0, *c1); g.add_color_stop_rgb(b - 0.18, *bg); g.add_color_stop_rgb(b + 0.18, *c0); g.add_color_stop_rgb(1, *c2)
    ctx.set_source(g); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()
    for k, cor in enumerate((a3, a1, a2)):                   # brilhos suaves em Lissajous
        px = CX + math.sin(t * (0.31 + 0.07 * k) + k * 2.1) * 430
        py = H * 0.5 + math.cos(t * (0.23 + 0.05 * k) + k * 1.3) * 760
        r = 620 + 120 * math.sin(t * 0.7 + k)
        gr = cairo.RadialGradient(px, py, 0, px, py, r)
        a = (0.22 if k == 0 else 0.30) * (0.6 + 0.6 * en)
        gr.add_color_stop_rgba(0, *cor, a); gr.add_color_stop_rgba(1, *cor, 0)
        ctx.set_source(gr); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()
    _calma_grad(ctx, bg, o.get("calma", 0.10))
    _cola(dst, lo)
    return None


# ======================= 2. bokeh =======================
def bokeh(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    lo, ctx_ = _lo(True); dst = ctx; ctx = ctx_          # desfoque de graça: tudo em 1/4 da resolução
    _grad_v(ctx, [(0, escurece(bg, 0.32)), (0.5, bg), (1, mix(bg, bg2, 0.6))])
    cores = (a1, a2, a3, clareia(bg, 0.45))
    camadas = ((int(30 * (0.5 + en)), 14, 34, 0.30, 22, 0.80),    # (quantos, rmin, rmax, alfa, vel, nitidez)
               (int(16 * (0.5 + en)), 50, 95, 0.26, 55, 0.70),
               (int(7 * (0.5 + en)), 120, 190, 0.18, 110, 0.45))
    for li, (n, rmin, rmax, alfa, vel, nit) in enumerate(camadas):
        for i in range(n):
            r_ = _rng("bk", seed, li, i)
            r = r_.uniform(rmin, rmax); cor = cores[r_.randrange(4)]
            span = H + 2 * r + 2 * M
            y = (r_.uniform(0, span) - t * vel * (0.4 + 0.9 * en)) % span - r - M
            x = r_.uniform(X0, X1) + math.sin(t * r_.uniform(0.3, 0.8) + i) * 40 * (li + 1)
            a = alfa * (0.75 + 0.25 * math.sin(t * 1.7 + i * 1.3))
            g = cairo.RadialGradient(x, y, 0, x, y, r)
            g.add_color_stop_rgba(0, *cor, a * 0.75); g.add_color_stop_rgba(nit, *cor, a)
            g.add_color_stop_rgba(min(0.97, nit + 0.12), *cor, a * 0.9); g.add_color_stop_rgba(1, *cor, 0)
            ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
    _calma_grad(ctx, bg, o.get("calma", 0.22))
    _cola(dst, lo)
    return None


# ======================= 3. formas (confete) =======================
def _estrela(x, y, r, rot, n=5):
    return [(x + (r if k % 2 == 0 else r * 0.45) * math.cos(rot + math.pi * k / n), y + (r if k % 2 == 0 else r * 0.45) * math.sin(rot + math.pi * k / n)) for k in range(2 * n)]


def formas(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    _grad_v(ctx, [(0, bg), (1, mix(bg, bg2, 0.9))])
    cores = (a1, a2, a3, clareia(bg, 0.35))
    n = int(20 + 22 * en)
    for i in range(n):
        r_ = _rng("fm", seed, i)
        tipo = r_.randrange(5); s = r_.uniform(38, 74); cor = cores[r_.randrange(4)]
        vel = r_.uniform(70, 150) * (0.5 + 0.8 * en)
        span = Y1 - Y0 + 160
        y = (r_.uniform(0, span) + t * vel) % span + Y0 - 80
        x = r_.uniform(X0, X1) + math.sin(t * r_.uniform(0.6, 1.3) + i) * 50
        rot = r_.uniform(0, 6.3) + t * r_.uniform(-1.6, 1.6) * (0.5 + en)
        d = math.hypot(x - CX, (y - CY) * 0.6)
        al = 0.55 + 0.45 * clamp((d - 260) / 360)            # mais discreto no centro
        if tipo == 0:   # triângulo
            pts = [(x + s * math.cos(rot + k * 2.094), y + s * math.sin(rot + k * 2.094)) for k in range(3)]
            _poli(ctx, pts, cor, alpha=al, seed=seed + i)
        elif tipo == 1:  # círculo / anel
            ctx.arc(x + 6, y + 8, s * 0.7, 0, 2 * math.pi); ctx.set_source_rgba(*INK, 0.28 * al); ctx.fill()
            ctx.arc(x, y, s * 0.7, 0, 2 * math.pi); ctx.set_source_rgba(*cor, al); ctx.fill_preserve()
            ctx.set_line_width(5); ctx.set_source_rgba(*INK, al); ctx.stroke()
        elif tipo == 2:  # zigue-zague
            c, sn = math.cos(rot), math.sin(rot)
            pts = [(x + (k - 2.5) * s * 0.42 * c - (12 if k % 2 else -12) * sn, y + (k - 2.5) * s * 0.42 * sn + (12 if k % 2 else -12) * c) for k in range(6)]
            ctx.save(); ctx.translate(6, 8); traco(ctx, pts, lw=17, cor=INK, alpha=0.28 * al, seed=seed + i); ctx.restore()
            traco(ctx, pts, lw=19, cor=INK, alpha=al, seed=seed + i, amp=0.8)
            traco(ctx, pts, lw=9, cor=cor, alpha=1.0, seed=seed + i, amp=0.8)
        elif tipo == 3:  # estrelinha
            _poli(ctx, _estrela(x, y, s * 0.85, rot), cor, alpha=al, seed=seed + i)
        else:            # retângulo de confete
            c, sn = math.cos(rot), math.sin(rot); w2, h2 = s * 0.55, s * 0.25
            pts = [(x + a * c - b * sn, y + a * sn + b * c) for a, b in ((-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2))]
            _poli(ctx, pts, cor, alpha=al, seed=seed + i)
    return bg, 0.0      # formas já ficam mais discretas no centro


# ======================= 4. espiral =======================
def espiral(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    ctx.set_source_rgb(*bg); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()
    vel = o.get("velocidade", 1.0)
    braços, torcao, R = 8, 0.0052, 2300
    giro = -t * (0.6 + 1.6 * en) * vel
    c_b = mix(bg, a3, 0.22 + 0.25 * en)
    ctx.save(); ctx.translate(CX, CY)
    for k in range(braços):
        base = giro + 2 * math.pi * k / braços
        ida = [(r * math.cos(base + r * torcao), r * math.sin(base + r * torcao)) for r in range(0, R, 40)]
        volta = [(r * math.cos(base + math.pi / braços + r * torcao), r * math.sin(base + math.pi / braços + r * torcao)) for r in range(R, -1, -40)]
        ctx.move_to(0, 0)
        for p in ida + volta:
            ctx.line_to(*p)
        ctx.close_path()
    ctx.set_source_rgb(*c_b); ctx.fill()
    ctx.restore()
    pul = 0.5 + 0.5 * math.sin(t * 5 * vel)                  # pulso de brilho no miolo
    lo, ctx_ = _lo(False); dst = ctx; ctx = ctx_
    g = cairo.RadialGradient(CX, CY, 0, CX, CY, 520 + 80 * pul)
    g.add_color_stop_rgba(0, *a3, 0.55); g.add_color_stop_rgba(0.4, *a3, 0.18); g.add_color_stop_rgba(1, *a3, 0)
    ctx.set_source(g); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()
    g = cairo.RadialGradient(CX, CY, 700, CX, CY, 1500)    # vinheta escura nas bordas
    g.add_color_stop_rgba(0, *INK, 0); g.add_color_stop_rgba(1, *INK, 0.35)
    ctx.set_source(g); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()
    _cola(dst, lo)
    return bg, 0.0


# ======================= 5. halftone =======================
def halftone(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    _grad_v(ctx, [(0, clareia(bg, 0.06)), (1, escurece(bg, 0.10))])
    esp = 44
    ox, oy = X0 - 200, Y1 + 200                              # a onda nasce no canto de baixo
    vel = 1.6 + 2.6 * en
    for camada, (cor, fase, dy0) in enumerate(((escurece(bg, 0.32), 0.0, 0), (mix(bg, a1, 0.55), 2.2, esp / 2))):
        ctx.new_path()
        for j, y in enumerate(range(int(Y0) + int(dy0), int(Y1) + esp, esp)):
            for x in range(int(X0) + (esp // 2 if j % 2 else 0) + camada * (esp // 4), int(X1) + esp, esp):
                d = math.hypot(x - ox, y - oy)
                w = 0.5 + 0.5 * math.sin(d / 120 - t * vel + fase)
                dc = math.hypot(x - CX, (y - CY) * 0.65)
                m = 0.35 + 0.65 * clamp((dc - 220) / 520)
                r = esp * 0.46 * (0.12 + 0.88 * w) * m * (0.75 if camada else 1)
                if r > 1.4:
                    ctx.new_sub_path(); ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*cor, 1.0 if camada == 0 else 0.55); ctx.fill()
    return bg, 0.0      # os pontos já encolhem no centro


# ======================= 6. ondas =======================
def ondas(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    cores = [mix(bg, a3, 0.10), bg, mix(bg, a1, 0.35), bg2, mix(bg, a2, 0.38), mix(bg, a3, 0.22), mix(bg, a1, 0.50), escurece(bg, 0.18)]
    ctx.set_source_rgb(*cores[0]); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()
    v = 0.5 + 1.1 * en
    n = len(cores) - 1
    for k in range(1, n + 1):
        y_base = Y0 + (Y1 - Y0) * k / (n + 0.6)
        ph = seed + k * 1.7
        pts = []
        for i in range(0, 49):
            x = X0 + (X1 - X0) * i / 48
            y = (y_base + 38 * math.sin(x / 190 + t * v * (1 if k % 2 else -1) + ph)
                 + 22 * math.sin(x / 83 - t * v * 1.6 + ph * 2) + 16 * math.sin(t * 0.9 + k))
            pts.append((x, y))
        def caminho(dy=0):
            ctx.move_to(*pts[0])
            for x, y in pts[1:]:
                ctx.line_to(x, y + dy)
            ctx.line_to(X1, Y1 + 10); ctx.line_to(X0, Y1 + 10); ctx.close_path()
        caminho(14); ctx.set_source_rgba(*INK, 0.22); ctx.fill()                 # sombra chapada
        caminho(); ctx.set_source_rgb(*cores[k]); ctx.fill()
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke()
        ctx.move_to(pts[0][0], pts[0][1] + 16)                                     # brilho tipo lava
        for x, y in pts[1:]:
            ctx.line_to(x, y + 16)
        ctx.set_line_width(7); ctx.set_source_rgba(*a3, 0.22); ctx.stroke()
    return bg, 0.20


# ======================= 7. raios de HQ =======================
def raios_hq(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    lo, c = _lo(True)
    g = cairo.RadialGradient(CX, CY, 0, CX, CY, 1400)
    g.add_color_stop_rgb(0, *mix(bg, a3, 0.55)); g.add_color_stop_rgb(0.35, *bg); g.add_color_stop_rgb(1, *escurece(bg, 0.25))
    c.set_source(g); c.paint(); _cola(ctx, lo)
    pulso = 0.5 + 0.5 * math.sin(t * 2 * math.pi * (0.8 + 1.2 * en))
    q = int(t * 12)                                           # as linhas "fervem" a 12 desenhos/s
    n = int(70 + 60 * en)
    escuro, claro = escurece(bg, 0.55), mix(bg, a3, 0.7)
    for cor, alfa, sel in ((escuro, 0.75, 0), (claro, 0.55, 1)):
        ctx.new_path()
        for i in range(n):
            r_ = _rng("hq", seed, i)
            if (i % 3 == 0) != bool(sel):
                continue
            r2 = _rng("hq", seed, i, q // 2)
            a = r_.uniform(0, 2 * math.pi) + r2.uniform(-0.015, 0.015)
            w = r_.uniform(0.004, 0.02)
            r0 = 430 + r_.uniform(0, 260) - 150 * pulso * en + r2.uniform(-30, 30)
            ctx.move_to(CX + r0 * math.cos(a), CY + r0 * math.sin(a))
            ctx.line_to(CX + 2400 * math.cos(a - w), CY + 2400 * math.sin(a - w))
            ctx.line_to(CX + 2400 * math.cos(a + w), CY + 2400 * math.sin(a + w)); ctx.close_path()
        ctx.set_source_rgba(*cor, alfa); ctx.fill()
    return mix(bg, a3, 0.3), 0.0     # o miolo já fica sem linhas


# ======================= 8. grade retrô =======================
def grade_retro(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    hz = H * 0.585
    lo, c = _lo(True); dst = ctx; ctx = c
    _grad_v(ctx, [(0, mix(bg, INK, 0.62)), (0.32, mix(bg, INK, 0.25)), (hz / H, mix(a2, a1, 0.45))])
    sr, sx, sy = 300, CX, hz - 150
    gl = cairo.RadialGradient(sx, sy, sr * 0.8, sx, sy, sr * 1.9)
    gl.add_color_stop_rgba(0, *a1, 0.35); gl.add_color_stop_rgba(1, *a1, 0)
    ctx.set_source(gl); ctx.rectangle(sx - sr * 1.9, sy - sr * 1.9, sr * 3.8, sr * 1.9 + (hz - sy)); ctx.fill()
    _cola(dst, lo); ctx = dst
    for i in range(40):                                        # estrelinhas no alto
        r_ = _rng("gr", seed, i); x, y = r_.uniform(0, W), r_.uniform(0, hz * 0.55)
        a = 0.4 + 0.4 * math.sin(t * r_.uniform(1, 3) + i)
        ctx.arc(x, y, r_.uniform(1.5, 3.5), 0, 2 * math.pi); ctx.set_source_rgba(*a3, a); ctx.fill()
    # sol listrado
    ctx.save(); ctx.rectangle(X0, Y0, X1 - X0, hz - Y0); ctx.clip()
    ctx.arc(sx, sy, sr, 0, 2 * math.pi); ctx.clip()
    gs = cairo.LinearGradient(0, sy - sr, 0, sy + sr)
    gs.add_color_stop_rgb(0, *clareia(a1, 0.25)); gs.add_color_stop_rgb(1, *mix(a1, VERMELHO, 0.8))
    ctx.set_source(gs); ctx.paint()
    desl = (t * 40 * (0.5 + en)) % 56                           # faixas que descem
    for k in range(9):
        yy = sy + 10 + k * 56 + desl - 56
        if yy > sy:
            ctx.rectangle(sx - sr, yy, 2 * sr, 6 + (yy - sy) / sr * 18)
    ctx.set_source_rgb(*mix(bg, INK, 0.25)); ctx.fill()
    ctx.restore()
    # montanhas
    r_ = _rng("mt", seed)
    pts = [(X0, hz)] + [(X0 + (X1 - X0) * i / 14, hz - abs(math.sin(i * 1.7 + seed)) * r_.uniform(40, 170)) for i in range(15)] + [(X1, hz)]
    _poli(ctx, pts, mix(bg, INK, 0.55), lw=5, seed=seed + 3, sombra=False)
    # chão com grade
    ctx.rectangle(X0, hz, X1 - X0, Y1 - hz); ctx.set_source_rgb(*mix(bg, INK, 0.70)); ctx.fill()
    gc = cairo.LinearGradient(0, hz, 0, hz + 160)
    gc.add_color_stop_rgba(0, *a1, 0.35); gc.add_color_stop_rgba(1, *a1, 0)
    ctx.set_source(gc); ctx.rectangle(X0, hz, X1 - X0, 160); ctx.fill()
    linha = mix(a2, a3, 0.25)
    ctx.save(); ctx.rectangle(X0, hz, X1 - X0, Y1 - hz); ctx.clip(); ctx.new_path()
    for k in range(-16, 17):
        ctx.move_to(CX, hz); ctx.line_to(CX + k * 330, Y1 + 400)
    fase = (t * (0.6 + 1.4 * en)) % 1.0
    D = (Y1 + 50 - hz) * 1.0
    for j in range(0, 26):
        z = j + 1 - fase
        y = hz + D / z
        if y < Y1 + 20:
            ctx.move_to(X0, y); ctx.line_to(X1, y)
    ctx.set_line_width(16); ctx.set_source_rgba(*linha, 0.22); ctx.stroke_preserve()
    ctx.set_line_width(5); ctx.set_source_rgba(*linha, 0.95); ctx.stroke()
    ctx.restore()
    ctx.move_to(X0, hz); ctx.line_to(X1, hz); ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke()
    return None


# ======================= 9. céu =======================
CEUS = {"dia": ("#3D9BF0", "#8CCBFF", "#D8F1FF", "#FFFFFF", "#CFE4F7"),
        "tarde": ("#4B2A86", "#E8558C", "#FFB04D", "#FFE3D0", "#F4A3A8"),
        "noite": ("#0B0A26", "#1E1B4E", "#3B3478", "#4A4790", "#34326E")}


def _nuvem(modo, li, i, esc):
    """Sprite de nuvem (cacheado): bolotas unidas, contorno grosso, sombreado embaixo."""
    k = ("nuvem", modo, li, i)
    if k in _CACHE:
        return _CACHE[k]
    r_ = _rng("nv", li, i)
    bolas = [(0, 0, 70)] + [(r_.uniform(-150, 150), r_.uniform(-50, 10), r_.uniform(45, 80)) for _ in range(5)] + [(-120, 20, 50), (120, 20, 50)]
    w, h = int(520 * esc), int(260 * esc)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s)
    c.translate(w / 2, h * 0.58); c.scale(esc, esc)
    cor, sombra = hexc(CEUS[modo][3]), hexc(CEUS[modo][4])
    def bolotas(dy=0):
        for x, y, r in bolas:
            c.new_sub_path(); c.arc(x, y + dy, r, 0, 2 * math.pi)
    bolotas(14); c.set_source_rgba(*INK, 0.22); c.fill()
    bolotas(); c.set_line_width(12); c.set_source_rgb(*INK); c.stroke()
    bolotas(); c.set_source_rgb(*sombra); c.fill()
    c.save(); bolotas(); c.clip(); c.translate(-6, -18); bolotas(); c.set_source_rgb(*cor); c.fill(); c.restore()
    s.flush(); _CACHE[k] = (s, w, h)
    return _CACHE[k]


def ceu(ctx, pal, t, o, en, seed):
    bg = pal[0]
    modo = o.get("ceu", "dia") if o.get("ceu", "dia") in CEUS else "dia"
    c = [mix(hexc(x), bg, 0.12) for x in CEUS[modo][:3]]
    lo, sky = _lo(True)
    _grad_v(sky, [(0, c[0]), (0.55, c[1]), (1, c[2])])
    if modo == "noite":
        mx, my = W * 0.80, H * 0.105
        g = cairo.RadialGradient(mx, my, 60, mx, my, 300)
        g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.35); g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
        sky.set_source(g); sky.arc(mx, my, 300, 0, 2 * math.pi); sky.fill()
    else:
        sx, sy, sr = (W * 0.80, H * 0.10, 105) if modo == "dia" else (W * 0.5, H * 0.52, 220)
        cor = hexc("#FFD21F") if modo == "dia" else hexc("#FFB347")
        g = cairo.RadialGradient(sx, sy, sr * 0.6, sx, sy, sr * 3.2)
        g.add_color_stop_rgba(0, *clareia(cor, 0.4), 0.55); g.add_color_stop_rgba(1, *cor, 0)
        sky.set_source(g); sky.arc(sx, sy, sr * 3.2, 0, 2 * math.pi); sky.fill()
    _calma_grad(sky, c[1], o.get("calma", 0.12))
    _cola(ctx, lo)
    if modo == "noite":
        for i in range(110):
            r_ = _rng("st", seed, i); x, y = r_.uniform(X0, X1), r_.uniform(Y0, H * 0.75)
            a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * r_.uniform(1.5, 4.5) * (0.6 + en) + i))
            rr = r_.uniform(1.6, 4.2)
            ctx.arc(x, y, rr, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 0.92, a); ctx.fill()
            if rr > 3.6 and a > 0.75:      # cintilada em cruz
                ctx.set_line_width(2.5); ctx.set_source_rgba(1, 1, 0.92, a * 0.8)
                ctx.move_to(x - 16, y); ctx.line_to(x + 16, y); ctx.move_to(x, y - 16); ctx.line_to(x, y + 16); ctx.stroke()
        mx, my = W * 0.80, H * 0.105                            # lua crescente
        ctx.push_group()
        ctx.arc(mx, my, 95, 0, 2 * math.pi); ctx.set_source_rgb(*hexc("#FFF1B8")); ctx.fill_preserve()
        ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke()
        ctx.set_operator(cairo.OPERATOR_CLEAR); ctx.arc(mx + 52, my - 30, 86, 0, 2 * math.pi); ctx.fill()
        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.arc(mx + 52, my - 30, 86, 0, 2 * math.pi); ctx.save(); ctx.arc(mx, my, 98, 0, 2 * math.pi); ctx.clip()
        ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke(); ctx.restore(); ctx.new_path()
        ctx.pop_group_to_source(); ctx.paint()
    else:
        sx, sy, sr = (W * 0.80, H * 0.10, 105) if modo == "dia" else (W * 0.5, H * 0.52, 220)
        ctx.save(); ctx.translate(sx, sy); ctx.rotate(t * (0.15 + 0.3 * en))
        for k in range(12):                                      # raios do sol
            a = 2 * math.pi * k / 12; L = sr * (1.45 + 0.12 * math.sin(t * 4 + k))
            ctx.move_to(sr * 1.15 * math.cos(a - 0.09), sr * 1.15 * math.sin(a - 0.09))
            ctx.line_to(L * math.cos(a), L * math.sin(a)); ctx.line_to(sr * 1.15 * math.cos(a + 0.09), sr * 1.15 * math.sin(a + 0.09)); ctx.close_path()
        ctx.set_source_rgba(*cor, 0.85); ctx.fill_preserve(); ctx.set_line_width(4); ctx.set_source_rgba(*INK, 0.7); ctx.stroke()
        ctx.restore()
        ctx.arc(sx + 8, sy + 10, sr, 0, 2 * math.pi); ctx.set_source_rgba(*INK, 0.25); ctx.fill()
        ctx.arc(sx, sy, sr, 0, 2 * math.pi); ctx.set_source_rgb(*cor); ctx.fill_preserve()
        ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke()
        ctx.arc(sx - sr * 0.3, sy - sr * 0.3, sr * 0.28, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.45); ctx.fill()
    for li, (n, esc, vel, alfa, y0, y1) in enumerate(() if o.get("nuvens") is False else ((4, 0.55, 14, 0.75, 0.05, 0.42), (3, 0.85, 32, 0.92, 0.10, 0.80), (2, 1.30, 60, 1.0, 0.74, 0.98))):
        for i in range(n):
            s, w, h = _nuvem(modo, li, i, esc)
            r_ = _rng("nvp", seed, li, i)
            span = X1 - X0 + w
            x = (r_.uniform(0, span) + t * vel * (0.5 + en)) % span + X0 - w
            y = H * r_.uniform(y0, y1) - h * 0.58 + 6 * math.sin(t * 0.8 + i)
            ctx.set_source_surface(s, x, y); ctx.paint_with_alpha(alfa)
    return None


# ======================= 10. espaço =======================
def espaco(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    lo, c = _lo(True); dst = ctx; ctx = c
    _grad_v(ctx, [(0, mix(bg, INK, 0.82)), (1, mix(bg, INK, 0.55))])
    for k, cor in enumerate((a2, bg2, a1)):                    # nebulosas
        px = W * (0.2 + 0.6 * k / 2) + math.sin(t * 0.2 + k) * 80; py = H * (0.25 + 0.25 * k) + math.cos(t * 0.15 + k) * 60
        g = cairo.RadialGradient(px, py, 0, px, py, 700)
        g.add_color_stop_rgba(0, *cor, 0.20); g.add_color_stop_rgba(1, *cor, 0)
        ctx.set_source(g); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()
    _calma_grad(ctx, mix(bg, INK, 0.65), o.get("calma", 0.10))
    _cola(dst, lo); ctx = dst
    v = 0.5 + en
    for li, (n, rmin, rmax, vel) in enumerate(((140, 1.2, 2.4, 8), (60, 2.4, 3.6, 22), (18, 3.8, 5.2, 48))):
        for i in range(n):
            r_ = _rng("es", seed, li, i)
            x = (r_.uniform(0, X1 - X0) - t * vel * v * 0.5) % (X1 - X0) + X0
            y = (r_.uniform(0, Y1 - Y0) + t * vel * v) % (Y1 - Y0) + Y0
            a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * r_.uniform(1, 4) + i))
            r = r_.uniform(rmin, rmax)
            ctx.arc(x, y, r, 0, 2 * math.pi); ctx.set_source_rgba(*mix(a3, (1, 1, 1), 0.5), a); ctx.fill()
            if li == 2:
                ctx.set_line_width(2.5); ctx.set_source_rgba(1, 1, 1, a * 0.7)
                ctx.move_to(x - r * 4, y); ctx.line_to(x + r * 4, y); ctx.move_to(x, y - r * 4); ctx.line_to(x, y + r * 4); ctx.stroke()
    # planeta com anel (canto de baixo, longe da legenda)
    px, py, pr = W * 0.80, H * 0.86, 210
    ctx.save(); ctx.translate(px, py); ctx.rotate(-0.35)
    def anel(frente):
        ctx.save(); ctx.scale(1, 0.26)
        ctx.arc(0, 0, pr * 1.75, 0 if frente else math.pi, math.pi if frente else 2 * math.pi)
        ctx.arc_negative(0, 0, pr * 1.35, math.pi if frente else 2 * math.pi, 0 if frente else math.pi); ctx.close_path()
        ctx.restore()
        ctx.set_source_rgb(*mix(a3, a1, 0.3)); ctx.fill_preserve(); ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.stroke()
    anel(False)
    ctx.arc(0, 0, pr, 0, 2 * math.pi); ctx.set_source_rgb(*a1); ctx.fill_preserve()
    ctx.save(); ctx.clip()
    off = (t * 25) % 120
    for k in range(-3, 5):
        ctx.rectangle(-pr, -pr + k * 120 + off * 0 + 40 + 12 * math.sin(t + k), 2 * pr, 34)
    ctx.set_source_rgba(*escurece(a1, 0.25), 0.8); ctx.fill()
    ctx.arc(-pr * 0.45, -pr * 0.45, pr * 1.25, 0, 2 * math.pi); ctx.rectangle(-2 * pr, -2 * pr, 4 * pr, 4 * pr)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); ctx.set_source_rgba(*INK, 0.35); ctx.fill(); ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    ctx.restore()
    ctx.arc(0, 0, pr, 0, 2 * math.pi); ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke()
    anel(True)
    ctx.restore()
    # luazinha no alto à esquerda
    ctx.arc(W * 0.14, H * 0.09, 52, 0, 2 * math.pi); ctx.set_source_rgb(*mix(a2, a3, 0.3)); ctx.fill_preserve()
    ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.stroke()
    # estrela cadente ocasional
    per = 2.8 - 1.2 * en
    ciclo = int(t / per); u = (t - ciclo * per) / 0.55
    if 0 <= u <= 1:
        r_ = _rng("cad", seed, ciclo)
        sx, sy = r_.uniform(W * 0.3, W * 1.05), r_.uniform(0, H * 0.3)
        ang = r_.uniform(2.35, 2.7); L = 900
        hx, hy = sx + math.cos(ang) * L * u, sy + math.sin(ang) * L * u
        tx, ty = hx - math.cos(ang) * 320, hy - math.sin(ang) * 320
        g = cairo.LinearGradient(tx, ty, hx, hy)
        a = math.sin(math.pi * u)
        g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(1, 1, 1, 0.9, a)
        ctx.move_to(tx, ty); ctx.line_to(hx, hy); ctx.set_line_width(7); ctx.set_source(g); ctx.stroke()
        ctx.arc(hx, hy, 8, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 0.9, a); ctx.fill()
    return None


# ======================= 11. papel rasgado =======================
def _rasgo(seed, k):
    """Borda rasgada periódica (período W): lista de (x, dy)."""
    ch = ("rasgo", seed, k)
    if ch not in _CACHE:
        r_ = _rng(*ch); n = 54
        f1, f2 = r_.randint(1, 3), r_.randint(3, 6); p1, p2 = r_.uniform(0, 6), r_.uniform(0, 6)
        _CACHE[ch] = [(W * i / n, 26 * math.sin(2 * math.pi * f1 * i / n + p1) + 12 * math.sin(2 * math.pi * f2 * i / n + p2) + r_.uniform(-13, 13)) for i in range(n)]
    return _CACHE[ch]


def papel_rasgado(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    ctx.set_source_rgb(*bg); ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0); ctx.fill()
    tiras = ((0.10, mix(bg, a3, 0.30)), (0.30, bg2), (0.50, mix(bg, a1, 0.30)), (0.68, mix(bg, a2, 0.40)), (0.86, escurece(bg, 0.18)))
    for k, (yf, cor) in enumerate(tiras):
        borda = _rasgo(seed, k); fibra = _rasgo(seed + 99, k)
        v = (22 + 30 * en) * (1 if k % 2 else -1) * (0.7 + 0.15 * k)
        off = (t * v) % W
        y0 = H * yf + 10 * math.sin(t * 0.9 + k * 1.4)
        def tira(dx, dy, fib):
            pts = [(x + off - W + dx + W * rep, y0 + d + dy - (fibra[i][1] * 0.25 + 12 if fib else 0))
                   for rep in range(3) for i, (x, d) in enumerate(borda)]
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            ctx.line_to(pts[-1][0], Y1 + 20); ctx.line_to(pts[0][0], Y1 + 20); ctx.close_path()
        ctx.save(); ctx.translate(CX, y0); ctx.rotate(0.03 * math.sin(k * 2.3 + 0.4 * t)); ctx.translate(-CX, -y0)
        tira(0, 14, True); ctx.set_source_rgba(*INK, 0.25); ctx.fill()         # sombra
        tira(0, 0, True); ctx.set_source_rgb(*BRANCO); ctx.fill()              # miolo branco do papel rasgado
        tira(0, 0, True); ctx.set_line_width(3); ctx.set_source_rgba(*INK, 0.55); ctx.stroke()
        tira(0, 0, False); ctx.set_source_rgb(*cor); ctx.fill()
        ctx.restore()
    return bg, 0.15


# ======================= 12. luzes (pisca-pisca) =======================
def luzes(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    base = escurece(bg, 0.50)
    lo, glow = _lo(True)
    _grad_v(glow, [(0, escurece(bg, 0.62)), (0.5, base), (1, escurece(bg, 0.40))])
    cores = (a1, VERMELHO, VERDE, a2, hexc("#38D1C6"))
    for i in range(14):                                          # luzinhas desfocadas lá no fundo
        r_ = _rng("lzf", seed, i); x, y = r_.uniform(X0, X1), r_.uniform(H * 0.2, H * 0.85); r = r_.uniform(40, 90)
        cor = cores[i % 5]; a = 0.14 * (0.6 + 0.4 * math.sin(t * 1.5 + i))
        g = cairo.RadialGradient(x, y, 0, x, y, r); g.add_color_stop_rgba(0, *cor, a); g.add_color_stop_rgba(0.7, *cor, a * 0.8); g.add_color_stop_rgba(1, *cor, 0)
        glow.set_source(g); glow.arc(x, y, r, 0, 2 * math.pi); glow.fill()
    passo = int(t * (2.5 + 5 * en))
    fios = ((-60, 40, W + 60, 120, 150), (-60, 250, W + 60, 170, 120), (-60, 1440, W + 60, 1520, 130), (-60, 1700, W + 60, 1640, 120))
    fios_pts = []
    for f, (xa, ya, xb, yb, sag) in enumerate(fios):
        sag = sag + 12 * math.sin(t * 1.3 + f)
        fios_pts.append([(xa + (xb - xa) * i / 40, ya + (yb - ya) * i / 40 + sag * 4 * (i / 40) * (1 - i / 40)) for i in range(41)])
    idx = 0
    for pts in fios_pts:                                         # brilho das lâmpadas acesas (baixa resolução)
        for i in range(2, 40, 3):
            if (idx + passo) % 3 != 0:
                x, y = pts[i]; cor = cores[idx % 5]
                g = cairo.RadialGradient(x, y + 40, 0, x, y + 40, 110); g.add_color_stop_rgba(0, *cor, 0.6); g.add_color_stop_rgba(1, *cor, 0)
                glow.set_source(g); glow.arc(x, y + 40, 110, 0, 2 * math.pi); glow.fill()
            idx += 1
    _calma_grad(glow, base, o.get("calma", 0.10))
    _cola(ctx, lo)
    idx = 0
    for f, (xa, ya, xb, yb, sag) in enumerate(fios):
        pts = fios_pts[f]
        traco(ctx, pts, lw=5, cor=INK, seed=seed + f, amp=0.6)
        for i in range(2, 40, 3):
            x, y = pts[i]
            dx = pts[i + 1][0] - pts[i - 1][0]; dy = pts[i + 1][1] - pts[i - 1][1]
            ang = math.atan2(dy, dx) + math.pi / 2 + 0.15 * math.sin(t * 2 + i)
            cor = cores[idx % 5]
            aceso = (idx + passo) % 3 != 0
            ctx.save(); ctx.translate(x, y); ctx.rotate(ang - math.pi / 2)
            ctx.rectangle(-9, 0, 18, 20); ctx.set_source_rgb(*hexc("#3A3550")); ctx.fill_preserve()
            ctx.set_line_width(3); ctx.set_source_rgb(*INK); ctx.stroke()
            ctx.save(); ctx.translate(0, 44); ctx.scale(1, 1.35)
            ctx.arc(0, 0, 17, 0, 2 * math.pi); ctx.restore()
            ctx.set_source_rgb(*(clareia(cor, 0.25) if aceso else escurece(cor, 0.5))); ctx.fill_preserve()
            ctx.set_line_width(4); ctx.set_source_rgb(*INK); ctx.stroke()
            if aceso:
                ctx.arc(-5, 36, 5, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.fill()
            ctx.restore()
            idx += 1
    return None


PADROES = {"gradiente_vivo": gradiente_vivo, "bokeh": bokeh, "formas": formas, "espiral": espiral, "halftone": halftone,
           "ondas": ondas, "raios_hq": raios_hq, "grade_retro": grade_retro, "ceu": ceu, "espaco": espaco,
           "papel_rasgado": papel_rasgado, "luzes": luzes}


def desenha(ctx, nome, pal, t, opts, seed=1):
    """Desenha o fundo `nome` cobrindo a tela toda (coordenadas da cena, já com a câmera aplicada)."""
    en = clamp(float(opts.get("energia", 0.6)))
    ctx.save(); ctx.new_path(); ctx.set_tolerance(0.5)
    r = PADROES[nome](ctx, pal, t, opts, en, seed)
    ctx.new_path()
    if r:
        _calma(ctx, r[0], opts.get("calma", r[1]))
    ctx.restore()


# ======================= transições de corte =======================
TRANSICOES = ("wipe_diagonal", "zoom_blur", "papel", "flash_cor")


def transicao(ctx, nome, prev, u, pal, seed=1):
    """Mistura o último quadro da cena anterior (surface `prev`) sobre a cena nova já desenhada. u: 0..1 do corte."""
    bg, bg2, a1, a2, a3 = pal
    ctx.save(); ctx.identity_matrix()
    if nome == "wipe_diagonal":
        e = ease_in_out(u); bw = 110; k = 0.55
        L = -20 + e * (W + k * H + bw + 60)
        ctx.move_to(L, 0); ctx.line_to(W + 400, 0); ctx.line_to(W + 400, H); ctx.line_to(L - k * H, H); ctx.close_path()
        ctx.save(); ctx.clip(); ctx.set_source_surface(prev, 0, 0); ctx.paint(); ctx.restore()
        for (d0, d1, cor) in ((0, bw * 0.62, a1), (bw * 0.62, bw, a2)):
            ctx.move_to(L - d0, 0); ctx.line_to(L - d0 - k * H, H); ctx.line_to(L - d1 - k * H, H); ctx.line_to(L - d1, 0); ctx.close_path()
            ctx.set_source_rgb(*cor); ctx.fill_preserve(); ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke()
    elif nome == "flash_cor":
        ctx.set_source_surface(prev, 0, 0); ctx.paint_with_alpha(clamp(1 - u * 2.2))
        g = cairo.RadialGradient(W / 2, H * 0.4, 0, W / 2, H * 0.4, 1300)
        a = 0.95 * (1 - u) ** 1.6
        g.add_color_stop_rgba(0, *clareia(a1, 0.5), a); g.add_color_stop_rgba(1, *a1, a)
        ctx.set_source(g); ctx.paint()
    elif nome == "zoom_blur":
        e = ease_in_out(u)
        for i in range(4):
            s = 1 + e * 0.9 * (1 + i * 0.12)
            ctx.save(); ctx.translate(W / 2, H * 0.42); ctx.scale(s, s); ctx.translate(-W / 2, -H * 0.42)
            ctx.set_source_surface(prev, 0, 0); ctx.paint_with_alpha((1 - e) * (0.55 if i else 1.0) / (1 + i * 0.6))
            ctx.restore()
    elif nome == "papel":
        e = u * u
        borda = _rasgo(seed + 7, 0)
        pts = [(W / 2 + d, H * i / (len(borda) - 1)) for i, (_, d) in enumerate(borda)]
        for lado in (-1, 1):
            ctx.save()
            ctx.translate(W / 2 + lado * e * W * 0.75, H * 0.5 + e * 260); ctx.rotate(lado * e * 0.35); ctx.translate(-W / 2, -H * 0.5)
            def metade(dx=0):
                ctx.move_to(-200 if lado < 0 else W + 200, -50)
                for x, y in pts:
                    ctx.line_to(x + dx, y)
                ctx.line_to(-200 if lado < 0 else W + 200, H + 50); ctx.close_path()
            ctx.save(); ctx.translate(lado * 10, 16); metade(-lado * 16); ctx.set_source_rgba(*INK, 0.35); ctx.fill(); ctx.restore()
            metade(-lado * 16); ctx.set_source_rgb(*BRANCO); ctx.fill_preserve(); ctx.set_line_width(3); ctx.set_source_rgba(*INK, 0.6); ctx.stroke()
            metade(); ctx.save(); ctx.clip(); ctx.set_source_surface(prev, 0, 0); ctx.paint(); ctx.restore()
            ctx.restore()
    ctx.restore()


# ======================= 13. cidade à noite =======================
def _predios(seed, camada):
    ch = ("predios", seed, camada)
    if ch not in _CACHE:
        r_ = _rng(*ch); out = []; x = 0.0
        while x < 2 * W:                                       # período 2W: desliza sem emenda
            w = r_.uniform(110, 210) if camada else r_.uniform(80, 150)
            h = r_.uniform(380, 760) if camada else r_.uniform(520, 900)
            out.append((x, w, h, r_.random(), r_.randrange(3)))
            x += w + (r_.uniform(-10, 18) if camada else r_.uniform(-25, 0))
        _CACHE[ch] = (out, x)
    return _CACHE[ch]


def cidade(ctx, pal, t, o, en, seed):
    bg, bg2, a1, a2, a3 = pal
    ceu(ctx, pal, t, dict(o, ceu="noite", nuvens=False), en, seed)
    janela_on = mix(a1, (1, 0.9, 0.55), 0.5)
    for camada, (vel, cor, lw) in enumerate(((10, mix(bg, INK, 0.55), 0), (26, mix(bg, INK, 0.78), 5))):
        lista, per = _predios(seed, camada)
        off = (t * vel * (0.5 + en)) % per
        ctx.new_path()
        for rep in (0, 1):
            for x, w, h, r, tipo in lista:
                px = x - off + rep * per - 40
                if px > X1 or px + w < X0:
                    continue
                y = Y1 - h - 60
                ctx.rectangle(px, y, w, h + 200)
                if tipo == 1:   # antena
                    ctx.rectangle(px + w / 2 - 4, y - 70, 8, 70)
                elif tipo == 2:  # telhado em degrau
                    ctx.rectangle(px + w * 0.2, y - 40, w * 0.6, 40)
        ctx.set_source_rgb(*cor); ctx.fill_preserve()
        if lw:
            ctx.set_line_width(lw); ctx.set_source_rgb(*INK); ctx.stroke()
        else:
            ctx.new_path()
        q = int(t * (0.6 + 1.5 * en))                          # algumas janelas acendem/apagam
        for rep in (0, 1):
            for bi, (x, w, h, r, tipo) in enumerate(lista):
                px = x - off + rep * per - 40
                if px > X1 or px + w < X0:
                    continue
                y = Y1 - h - 60
                jw, jh = (18, 26) if camada else (10, 14)
                nx = max(1, int((w - 24) // (jw + 14))); ny = int((h - 40) // (jh + 18))
                for j in range(ny):
                    for i in range(nx):
                        k = (bi * 131 + j * 17 + i * 7) % 97
                        if (k + (q if k % 9 == 0 else 0)) % 5 < 2:
                            ctx.rectangle(px + 14 + i * (jw + 14) + ((w - 28) - nx * (jw + 14) + 14) / 2, y + 30 + j * (jh + 18), jw, jh)
        ctx.set_source_rgba(*janela_on, 0.55 if camada == 0 else 0.95); ctx.fill()
    return mix(bg, INK, 0.6), 0.0


PADROES["cidade"] = cidade


# ======================= FUNDO COM FOTO REAL (imersão) =======================
ESTILOS_FOTO = ("real", "duotone", "posterizada", "pintada")


def _para_surface(im):
    """PIL RGB/RGBA -> cairo ARGB32 (pré-multiplicado). Devolve (surface, buffer)."""
    import numpy as np
    a = np.asarray(im.convert("RGBA"), dtype=np.float32)
    al = a[..., 3:4] / 255.0
    bgra = np.empty(a.shape, np.uint8)
    bgra[..., 0] = (a[..., 2] * al[..., 0]); bgra[..., 1] = (a[..., 1] * al[..., 0]); bgra[..., 2] = (a[..., 0] * al[..., 0]); bgra[..., 3] = a[..., 3]
    buf = np.ascontiguousarray(bgra)
    h, w = buf.shape[:2]
    return cairo.ImageSurface.create_for_data(memoryview(buf), cairo.FORMAT_ARGB32, w, h, w * 4), buf


def _foto_camadas(arq, estilo, pal, foco):
    """Processa a foto uma vez por processo: camada de trás (desfocada) e da frente (nítida, máscara radial no foco)."""
    ch = ("foto", arq, estilo, tuple(pal[0]), tuple(foco))
    if ch in _CACHE:
        return _CACHE[ch]
    import os
    from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cam = arq if os.path.isabs(arq) else os.path.join(raiz, arq)
    if not os.path.exists(cam):
        raise SystemExit(f"fundo_foto: arquivo não encontrado: {cam}")
    im = Image.open(cam).convert("RGB")
    if max(im.size) > 1600:
        im.thumbnail((1600, 1600))
    bg, bg2, a1, a2, a3 = pal
    rgb = lambda c: tuple(int(v * 255) for v in c)
    if estilo == "duotone":   # sombras na cor da paleta, luzes no destaque: casa com o desenho
        g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
        im = ImageOps.colorize(g, black=rgb(mix(bg, INK, 0.7)), mid=rgb(bg), white=rgb(clareia(a1, 0.35)), midpoint=110)
    elif estilo == "posterizada":   # poucas cores + contorno leve de tinta
        lis = im.filter(ImageFilter.MedianFilter(5))
        lis = ImageEnhance.Color(lis).enhance(1.35)
        q = lis.quantize(colors=7, method=Image.Quantize.MEDIANCUT).convert("RGB")
        bordas = ImageOps.grayscale(q).filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 28 else 0).filter(ImageFilter.MaxFilter(3))
        tinta = Image.new("RGB", im.size, rgb(INK))
        im = Image.composite(tinta, q, bordas.point(lambda v: int(v * 0.7)))
    elif estilo == "pintada":   # pinceladas: mediana grande + suavização + cor mais viva
        im = im.filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.SMOOTH_MORE)
        im = ImageEnhance.Color(im).enhance(1.35); im = ImageEnhance.Contrast(im).enhance(1.1)
    else:
        im = ImageEnhance.Contrast(im).enhance(1.06); im = ImageEnhance.Color(im).enhance(1.1)
    tras = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(max(im.size) / 110))).enhance(0.78)
    # máscara radial suave em volta do foco (camada da frente)
    w, h = im.size
    m = Image.new("L", (w // 8, h // 8), 0); d = ImageDraw.Draw(m)
    cx, cy, r = foco[0] * w / 8, foco[1] * h / 8, min(w, h) / 8 * 0.42
    d.ellipse((cx - r, cy - r * 1.15, cx + r, cy + r * 1.15), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(r * 0.55)).resize((w, h), Image.BILINEAR)
    frente = im.convert("RGBA"); frente.putalpha(m)
    _CACHE[ch] = (_para_surface(tras), _para_surface(frente), (w, h))
    return _CACHE[ch]


def _kb(o, u):
    de = o.get("kb_de", [1.0, 0.5, 0.5]); para = o.get("kb_para", [1.18, 0.5, 0.45])
    e = ease_in_out(u)
    return [de[i] + (para[i] - de[i]) * e for i in range(3)], de


def _pinta_camada(ctx, surf, iw, ih, z, fx, fy):
    s = max((X1 - X0) / iw, (Y1 - Y0) / ih) * z
    hw, hh = (X1 - X0) / 2 / s, (Y1 - Y0) / 2 / s
    px = min(max(fx * iw, hw), iw - hw); py = min(max(fy * ih, hh), ih - hh)
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(s, s); ctx.translate(-px, -py)
    pat = cairo.SurfacePattern(surf); pat.set_filter(cairo.FILTER_GOOD if s < 1.5 else cairo.FILTER_BILINEAR)
    ctx.set_source(pat); ctx.rectangle(0, 0, iw, ih); ctx.fill(); ctx.restore()


def foto(ctx, pal, t, o, seed=1):
    """Cena com foto em tela cheia: Ken Burns (`kb_de`/`kb_para` = [zoom, x, y] do foco na foto), `estilo`,
    parallax de 2 camadas (`parallax`, padrão true) e vinheta (`vinheta`, padrão 0,45)."""
    arq = o["fundo_foto"]; estilo = o.get("estilo", "real")
    if estilo not in ESTILOS_FOTO:
        raise SystemExit(f"estilo de foto '{estilo}' não existe. Use: {', '.join(ESTILOS_FOTO)}")
    t0, t1 = o.get("_t0", 0.0), o.get("_t1", t + 4)
    u = clamp((t - t0) / max(0.5, t1 - t0))
    (z, fx, fy), de = _kb(o, u)
    para = o.get("kb_para", [1.18, 0.5, 0.45])
    foco = ((de[1] + para[1]) / 2, (de[2] + para[2]) / 2)
    (tras, _), (frente, _), (iw, ih) = _foto_camadas(arq, estilo, pal, foco)
    ctx.save(); ctx.new_path()
    if o.get("parallax", True):
        dx, dy = fx - de[1], fy - de[2]
        _pinta_camada(ctx, tras, iw, ih, z * 0.97, de[1] + dx * 0.5, de[2] + dy * 0.5)       # fundo devagar
        _pinta_camada(ctx, frente, iw, ih, z * 1.08, fx + dx * 0.5 + 0.004 * math.sin(t * 0.7), fy + dy * 0.5)   # frente mais rápida
    else:
        _pinta_camada(ctx, tras, iw, ih, z, fx, fy)
    k = o.get("vinheta", 0.45)
    if k > 0:
        ch = ("vinheta", round(k, 3))
        if ch not in _CACHE:
            s, c = _lo(False, chave=ch)
            g = cairo.RadialGradient(CX, H * 0.45, 350, CX, H * 0.45, 1250)
            g.add_color_stop_rgba(0, *INK, 0); g.add_color_stop_rgba(1, *INK, k)
            c.set_source(g); c.paint(); s.flush()
        _cola(ctx, _CACHE[ch])
    ctx.restore()


# ======================= mergulho / emergir =======================
TRANSICOES = TRANSICOES + ("mergulho", "emergir")
DUR_TRANSICAO = {"mergulho": 0.5, "emergir": 0.5}
_transicao_simples = transicao


def _copia_alvo(ctx):
    s = _CACHE.get("snap")
    if s is None:
        s = _CACHE["snap"] = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s); c.set_source_surface(ctx.get_target(), 0, 0); c.set_operator(cairo.OPERATOR_SOURCE); c.paint(); s.flush()
    return s


def _zoom_em(ctx, surf, px, py, s, alpha=1.0):
    ctx.save(); ctx.translate(px, py); ctx.scale(s, s); ctx.translate(-px, -py)
    ctx.set_source_surface(surf, 0, 0); ctx.paint_with_alpha(alpha); ctx.restore()


def _iris(ctx, px, py, r, a1, a2):
    ctx.new_path(); ctx.arc(px, py, r, 0, 2 * math.pi)
    ctx.set_line_width(34); ctx.set_source_rgb(*INK); ctx.stroke_preserve()
    ctx.set_line_width(22); ctx.set_source_rgb(*a1); ctx.stroke_preserve()
    ctx.set_line_width(7); ctx.set_source_rgb(*a2); ctx.stroke()


def transicao(ctx, nome, prev, u, pal, seed=1, opts=None):
    if nome not in ("mergulho", "emergir"):
        return _transicao_simples(ctx, nome, prev, u, pal, seed)
    opts = opts or {}
    bg, bg2, a1, a2, a3 = pal
    px, py = opts.get("mergulho_em", [0.5, 0.4]); px *= W; py *= H
    diag = math.hypot(max(px, W - px), max(py, H - py)) + 60
    ctx.save(); ctx.identity_matrix()
    novo = _copia_alvo(ctx)
    if nome == "mergulho":
        e = u ** 1.6
        ctx.set_operator(cairo.OPERATOR_SOURCE); ctx.set_source_rgb(*INK); ctx.paint(); ctx.set_operator(cairo.OPERATOR_OVER)
        for i in range(3):                       # a câmera mergulha na foto (com rastro de zoom)
            _zoom_em(ctx, prev, px, py, 1 + 7 * e * (1 + 0.1 * i), 1.0 if i == 0 else 0.35)
        r = diag * e ** 1.15
        if r > 2:
            ctx.save(); ctx.new_path(); ctx.arc(px, py, r, 0, 2 * math.pi); ctx.clip()
            _zoom_em(ctx, novo, px, py, 0.35 + 0.65 * ease_in_out(u)); ctx.restore()   # a cena 2D nasce do ponto
            _iris(ctx, px, py, r, a1, a2)
        f = clamp(1 - abs(u - 0.12) / 0.12)
    else:  # emergir: a cena anterior fecha numa íris enquanto a nova (foto) se afasta do ponto
        e = ease_in_out(u)
        ctx.set_operator(cairo.OPERATOR_SOURCE); ctx.set_source_rgb(*INK); ctx.paint(); ctx.set_operator(cairo.OPERATOR_OVER)
        _zoom_em(ctx, novo, px, py, 2.2 - 1.2 * (1 - (1 - u) ** 2.2))
        r = diag * (1 - e) ** 1.2
        if r > 2:
            ctx.save(); ctx.new_path(); ctx.arc(px, py, r, 0, 2 * math.pi); ctx.clip()
            _zoom_em(ctx, prev, px, py, 1 - 0.6 * e); ctx.restore()
            _iris(ctx, px, py, r, a1, a2)
        f = clamp(1 - abs(u - 0.85) / 0.15)
    if f > 0:
        ctx.set_source_rgba(1, 1, 0.95, 0.75 * f); ctx.paint()
    ctx.restore()
