"""Biblioteca de desenhos do PipoPop 2D: personagens, objetos e cenários.
Cada desenho de elemento recebe (ctx, st, t, pal) já transladado para o centro do elemento e devolve um dict de caixas
locais {"corpo": (x0,y0,x1,y1), "rosto"/"texto": ...} usado pela revisão automática."""
import math, random
import cairo
from estilo import (W, H, INK, LW, AMARELO, BRANCO, VERMELHO, VERDE, hexc, mix, escurece, clareia, forma, traco, texto, medir,
                    pts_elipse, pts_ret, path_suave, jitter, ease_out_back, ease_out, clamp)

PELES = {"clara": "#F6C9A0", "media": "#D9935F", "morena": "#A8683D", "escura": "#6E4227"}
CABELO_COR = {"preto": "#231A2B", "castanho": "#5A3420", "loiro": "#E8B84A", "ruivo": "#C8531F", "grisalho": "#BDB7C4", "azul": "#2D58D6"}


def _cor(v, padrao):
    if v is None:
        return hexc(padrao)
    return hexc(PELES.get(v, CABELO_COR.get(v, v)))


# ============================ OLHOS (comuns a todos) ============================
def piscada(t, seed, lid_base):
    """Pisca sozinho a cada 2,2 a 3,6 s (nunca fica de olho parado)."""
    r = random.Random(seed)
    tt = r.uniform(0.4, 1.8)
    while tt < t + 1:
        if tt <= t < tt + 0.13:
            return 1.0
        tt += r.uniform(2.2, 3.6)
    return lid_base


def olho(ctx, cx, cy, rx, ry, look, lid, cor_palpebra, seed):
    pts = pts_elipse(cx, cy, rx, ry, 20)
    forma(ctx, pts, (1, 1, 1), sombra=False, lw=5, seed=seed, amp=0.8)
    ctx.save(); path_suave(ctx, jitter(pts, 0.8, seed)); ctx.clip()
    px, py = cx + look[0] * rx * 0.42, cy + look[1] * ry * 0.38
    ctx.arc(px, py, rx * 0.42, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.arc(px - rx * 0.14, py - ry * 0.16, rx * 0.13, 0, 2 * math.pi); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    if lid > 0.01:
        yl = cy - ry + 2 * ry * lid
        ctx.rectangle(cx - rx - 4, cy - ry - 4, 2 * rx + 8, yl - (cy - ry) + 4); ctx.set_source_rgb(*cor_palpebra); ctx.fill()
        ctx.restore()
        if lid < 0.99:
            dx = rx * math.sqrt(max(0, 1 - ((yl - cy) / ry) ** 2))
            traco(ctx, [(cx - dx, yl), (cx, yl + 1.5), (cx + dx, yl)], lw=5, seed=seed + 1, amp=0.6)
        else:
            traco(ctx, [(cx - rx, cy), (cx, cy + 4), (cx + rx, cy)], lw=5, seed=seed + 1, amp=0.6)
    else:
        ctx.restore()
    path_suave(ctx, jitter(pts, 0.8, seed)); ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.stroke()


LOOK = {"camera": (0, 0), "frente": (0, 0), "celular": (0.15, 0.85), "baixo": (0, 0.9), "cima": (0, -0.9),
        "esq": (-0.9, 0.1), "dir": (0.9, 0.1), "esquerda": (-0.9, 0.1), "direita": (0.9, 0.1)}


def boca(ctx, tipo, x, y, esc=1.0, seed=9):
    if tipo == "o":
        forma(ctx, pts_elipse(x, y, 15 * esc, 19 * esc, 14), escurece(VERMELHO, 0.45), sombra=False, lw=5, seed=seed)
    elif tipo == "sorriso":
        traco(ctx, [(x - 26 * esc, y - 6), (x, y + 10 * esc), (x + 26 * esc, y - 6)], lw=7, seed=seed)
    elif tipo == "sorriso_torto":
        traco(ctx, [(x - 22 * esc, y + 2), (x + 6 * esc, y + 4), (x + 26 * esc, y - 10 * esc)], lw=7, seed=seed)
    elif tipo == "triste":
        traco(ctx, [(x - 22 * esc, y + 8), (x, y - 4 * esc), (x + 22 * esc, y + 8)], lw=7, seed=seed)
    else:  # reta (deadpan)
        traco(ctx, [(x - 20 * esc, y), (x + 4 * esc, y + 2), (x + 22 * esc, y - 3)], lw=7, seed=seed)


# ============================ PIPO ============================
MILHO = hexc("#FFC21A")
MILHO_GRAO = hexc("#FFD447")
MILHO_SOMBRA = hexc("#E39A00")
PALHA = hexc("#46B04A")
CABELO_MILHO = hexc("#C9792B")
PIPOCA = hexc("#FFF3D2")
PIPOCA_SOMBRA = hexc("#EBCB8B")


def _corpo_espiga():
    pts = []
    for i in range(30):
        th = 2 * math.pi * i / 30
        s = math.sin(th)
        taper = 1 - 0.25 * max(0, -s) ** 2 - 0.10 * max(0, s) ** 2
        pts.append((118 * math.cos(th) * taper, -40 + 250 * s))
    return pts


def _bracos(ctx, st, seed, cor):
    segura = st.get("segura")
    if segura == "celular":
        for sx in (-1, 1):
            traco(ctx, [(sx * 104, -10), (sx * 92, 50), (sx * 44, 74)], lw=13, seed=seed + sx)
        # celular visto por trás (a tela ilumina o rosto)
        ctx.save(); ctx.translate(0, 40); ctx.rotate(-0.08)
        forma(ctx, pts_ret(-62, -100, 124, 200, 20), hexc("#3A2E52"), sombra=True, lw=5, seed=seed + 5, sombra_off=(6, 8))
        ctx.arc(-30, -72, 10, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
        ctx.restore()
        for sx in (-1, 1):
            forma(ctx, pts_elipse(sx * 48, 74, 24, 22, 12), cor, sombra=False, lw=5, seed=seed + 7 + sx)
    else:
        bal = math.sin(st["_t"] * 2.4) * 6
        for sx in (-1, 1):
            traco(ctx, [(sx * 106, -10), (sx * 150, 50 + bal), (sx * 158, 110 + bal)], lw=13, seed=seed + sx)
            forma(ctx, pts_elipse(sx * 160, 118 + bal, 24, 22, 12), cor, sombra=False, lw=5, seed=seed + 9 + sx)


def desenha_pipo_espiga(ctx, st, t, seed):
    corpo = _corpo_espiga()
    # sombra chapada
    ctx.save(); ctx.translate(12, 14); path_suave(ctx, corpo); ctx.set_source_rgba(*INK, 0.3); ctx.fill(); ctx.restore()
    # cabelo de milho (atrás)
    for i, a in enumerate((-0.9, -0.45, 0, 0.4, 0.85)):
        p = [(a * 30, -270), (a * 70, -330 - (i % 2) * 18), (a * 120 + 10 * math.sin(t * 3 + i), -350 - (i % 3) * 10)]
        traco(ctx, p, lw=15, seed=seed + 40 + i); traco(ctx, p, lw=7, cor=CABELO_MILHO, seed=seed + 40 + i, amp=0)
    body = jitter(corpo, 1.6, seed)
    path_suave(ctx, body); ctx.set_source_rgb(*MILHO); ctx.fill_preserve()
    ctx.save(); ctx.clip()
    r = random.Random(seed)
    for row, y in enumerate(range(-300, 230, 36)):
        off = 19 if row % 2 else 0
        for x in range(-160 + off, 170, 38):
            ctx.save(); ctx.translate(x + r.uniform(-1.5, 1.5), y)
            path_suave(ctx, pts_ret(-14, -14, 28, 28, 10, 2)); ctx.set_source_rgb(*MILHO_GRAO); ctx.fill_preserve()
            ctx.set_source_rgba(*INK, 0.28); ctx.set_line_width(2.5); ctx.stroke()
            ctx.arc(-5, -6, 4, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.55); ctx.fill()
            ctx.restore()
    # meia-lua de sombra chapada (lado direito)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    path_suave(ctx, body); ctx.save(); ctx.translate(-34, -6); path_suave(ctx, body); ctx.restore()
    ctx.set_source_rgba(*escurece(MILHO_SOMBRA, 0.1), 0.55); ctx.fill()
    ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
    if st.get("segura") == "celular":   # brilho da tela no rosto
        g = cairo.RadialGradient(0, -120, 10, 0, -120, 190)
        g.add_color_stop_rgba(0, 0.6, 0.95, 1, 0.35); g.add_color_stop_rgba(1, 0.6, 0.95, 1, 0)
        ctx.set_source(g); ctx.paint()
    ctx.restore()
    path_suave(ctx, body); ctx.set_line_width(LW + 1); ctx.set_source_rgb(*INK); ctx.stroke()
    # rosto
    look = LOOK.get(st.get("olhar", "camera"), (0, 0))
    lid_base = st.get("palpebra", 0.42)
    lid = piscada(t, seed, lid_base)
    for sx, sd in ((-1, 1), (1, 2)):
        olho(ctx, sx * 50, -150, 36, 42, look, lid, MILHO_SOMBRA, seed + sd)
        traco(ctx, [(sx * 50 - 26, -96), (sx * 50, -90), (sx * 50 + 24, -97)], lw=4, alpha=0.6, seed=seed + 20 + sd)  # olheira
    sob = st.get("sobrancelha", 0.0)
    traco(ctx, [(-86, -208), (-50, -206), (-18, -200)], lw=10, seed=seed + 30)
    up = 20 + 26 * sob
    traco(ctx, [(18, -204 - up * 0.5), (50, -212 - up), (86, -204 - up * 0.6)], lw=10, seed=seed + 31)
    boca(ctx, st.get("boca", "reta"), 4, -64, 1.0, seed + 32)
    # palha (na frente)
    for sx in (-1, 1):
        leaf = [(sx * 10, 250), (sx * 90, 210), (sx * 150, 90), (sx * 158, -30), (sx * 128, 40), (sx * 70, 150), (sx * 20, 205)]
        forma(ctx, leaf, PALHA, sombra=False, sombreado=0.12 if sx > 0 else 0, lw=LW, seed=seed + 50 + sx)
        traco(ctx, [(sx * 40, 220), (sx * 105, 120), (sx * 140, 10)], lw=3, alpha=0.5, seed=seed + 55 + sx)
    for sx in (-1, 1):   # pezinhos
        forma(ctx, pts_elipse(sx * 42, 268, 34, 16, 12), hexc("#3A2E52"), sombra=False, lw=5, seed=seed + 60 + sx)
    _bracos(ctx, st, seed, MILHO)
    return {"corpo": (-170, -360, 170, 290), "rosto": (-100, -240, 100, -50)}


def _pipoca_lobos():
    return [(0, -110, 118), (-100, -50, 96), (100, -50, 96), (-80, 50, 92), (80, 50, 92), (0, 80, 100), (0, -195, 80), (-60, -170, 70), (60, -170, 70)]


def desenha_pipoca(ctx, st, t, seed):
    lob = _pipoca_lobos()
    tran = [(-170, -230, 52), (-205, -175, 42), (-205, -270, 40), (170, -230, 52), (205, -175, 42), (205, -270, 40)]
    todos = lob + tran
    ctx.push_group()
    for x, y, rr in todos:
        ctx.arc(x + 12, y + 14, rr, 0, 2 * math.pi); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(0.3)
    for x, y, rr in todos:   # contorno da união
        path_suave(ctx, jitter(pts_elipse(x, y, rr, rr, 16), 1.4, seed + int(x))); ctx.set_source_rgb(*INK); ctx.set_line_width(2 * LW + 2); ctx.stroke()
    for i, (x, y, rr) in enumerate(todos):
        path_suave(ctx, jitter(pts_elipse(x, y, rr, rr, 16), 1.4, seed + int(x))); ctx.set_source_rgb(*PIPOCA); ctx.fill()
    for i, (x, y, rr) in enumerate(todos):   # dobrinhas de pipoca
        a = 0.6 + i
        traco(ctx, [(x + rr * 0.5 * math.cos(a), y + rr * 0.5 * math.sin(a)), (x + rr * 0.75 * math.cos(a + 0.5), y + rr * 0.75 * math.sin(a + 0.5))],
              lw=5, cor=PIPOCA_SOMBRA, seed=seed + 80 + i, amp=0.5)
    for sx in (-1, 1):   # laços da maria-chiquinha
        cx, cy = sx * 128, -215
        for d in (-1, 1):
            forma(ctx, [(cx, cy), (cx + d * 34, cy - 24), (cx + d * 38, cy + 20)], VERMELHO, sombra=False, lw=5, seed=seed + 90 + d * sx, amp=0.8)
        forma(ctx, pts_elipse(cx, cy, 11, 11, 10), escurece(VERMELHO, 0.2), sombra=False, lw=5, seed=seed + 95 + sx)
    # casquinha do grão
    forma(ctx, [(-50, 168), (0, 150), (50, 168), (30, 196), (-30, 196)], hexc("#D9822B"), sombra=False, lw=5, seed=seed + 99)
    look = LOOK.get(st.get("olhar", "camera"), (0, 0))
    lid = piscada(t, seed, st.get("palpebra", 0.12))
    for sx, sd in ((-1, 1), (1, 2)):
        olho(ctx, sx * 48, -110, 38, 46, look, lid, PIPOCA_SOMBRA, seed + sd)
    sob = st.get("sobrancelha", 0.4)
    traco(ctx, [(-84, -176), (-50, -174), (-18, -168)], lw=10, seed=seed + 30)
    up = 18 + 26 * sob
    traco(ctx, [(18, -172 - up * 0.5), (50, -180 - up), (86, -172 - up * 0.6)], lw=10, seed=seed + 31)
    boca(ctx, st.get("boca", "o"), 4, -30, 1.0, seed + 32)
    _bracos(ctx, dict(st, segura=None), seed, PIPOCA)
    return {"corpo": (-250, -320, 250, 200), "rosto": (-100, -210, 100, -10)}


def particulas_estouro(ctx, dt, seed):
    """Estouro: clarão, grãos, nuvenzinhas e riscos de velocidade. dt = segundos desde o estouro."""
    if dt < 0 or dt > 0.9:
        return
    r = random.Random(seed)
    if dt < 0.12:
        k = dt / 0.12
        forma(ctx, [(math.cos(a) * (120 + 260 * k) * (1.25 if i % 2 else 0.7), math.sin(a) * (120 + 260 * k) * (1.25 if i % 2 else 0.7))
                    for i, a in enumerate([j * math.pi / 8 for j in range(16)])], (1, 1, 0.85), sombra=False, lw=6, seed=seed, amp=3)
    for i in range(14):   # riscos
        a = r.uniform(0, 2 * math.pi); r0 = 180 + dt * 700; ln = 90 * (1 - dt / 0.9)
        if ln > 4:
            traco(ctx, [(math.cos(a) * r0, math.sin(a) * r0), (math.cos(a) * (r0 + ln), math.sin(a) * (r0 + ln))], lw=8, seed=seed + i, amp=0)
    for i in range(26):   # grãos e nuvens
        a = r.uniform(0, 2 * math.pi); v = r.uniform(500, 1100)
        x = math.cos(a) * v * dt; y = math.sin(a) * v * dt + 900 * dt * dt
        sz = r.uniform(14, 30) * (1 - dt / 1.1)
        if i % 3 == 0:
            forma(ctx, pts_elipse(x, y, sz * 1.6, sz * 1.4, 10), PIPOCA, sombra=False, lw=4, seed=seed + 200 + i)
        else:
            ctx.save(); ctx.translate(x, y); ctx.rotate(a + dt * 9)
            forma(ctx, pts_ret(-sz / 2, -sz / 2, sz, sz, sz / 3, 2), MILHO_GRAO if i % 2 else hexc("#D9822B"), sombra=False, lw=4, seed=seed + 300 + i)
            ctx.restore()


def desenha_pipo(ctx, st, t, seed):
    te = st.get("_estouro")
    if te is not None and t >= te:
        dt = t - te
        k = ease_out_back(clamp(dt / 0.35), 2.6) if dt < 0.35 else 1.0
        ctx.save(); ctx.scale(max(0.05, k), max(0.05, k)); b = desenha_pipoca(ctx, st, t, seed); ctx.restore()
        particulas_estouro(ctx, dt, seed)
        return b
    if te is not None and te - 0.35 < t < te:   # antecipação: incha e treme
        k = (t - (te - 0.35)) / 0.35
        ctx.translate(math.sin(t * 90) * 7 * k, 0); ctx.scale(1 + 0.12 * k, 1 - 0.08 * k)
    return desenha_pipo_espiga(ctx, st, t, seed)


# ============================ HUMANO GENÉRICO ============================
def desenha_humano(ctx, st, t, seed):
    pele = _cor(st.get("pele"), PELES["media"])
    cab = _cor(st.get("cabelo_cor"), CABELO_COR["preto"])
    roupa = _cor(st.get("roupa"), "#2A7DE1")
    calca = _cor(st.get("calca"), "#2B2440")
    estilo = st.get("cabelo", "curto")
    # pernas e corpo
    for sx in (-1, 1):
        forma(ctx, pts_ret(sx * 50 - 34, 130, 68, 190, 20), calca, sombra=True, lw=LW, seed=seed + sx)
        forma(ctx, pts_elipse(sx * 60, 322, 56, 26, 14), INK, sombra=False, lw=4, seed=seed + 3 + sx)
    tronco = [(-120, -110), (-60, -140), (60, -140), (120, -110), (130, 150), (-130, 150)]
    forma(ctx, tronco, roupa, sombreado=0.14, seed=seed + 5)
    # pescoço e cabeça
    forma(ctx, pts_ret(-26, -175, 52, 50, 10), escurece(pele, 0.12), sombra=False, lw=5, seed=seed + 6)
    if estilo in ("longo", "cacheado"):  # cabelo de trás
        n = 22 if estilo == "cacheado" else 16
        pts = [(math.cos(a) * (120 + (14 if (estilo == "cacheado" and i % 2) else 0)), -250 + math.sin(a) * 120 + (60 if math.sin(a) > 0 else 0))
               for i, a in enumerate([2 * math.pi * k / n for k in range(n)])]
        forma(ctx, pts, cab, seed=seed + 7)
    head = pts_elipse(0, -255, 95, 102, 22)
    forma(ctx, head, pele, sombreado=0.1, seed=seed + 8)
    for sx in (-1, 1):  # orelhas
        forma(ctx, pts_elipse(sx * 96, -250, 16, 22, 10), pele, sombra=False, lw=5, seed=seed + 9 + sx)
    if estilo == "curto":
        forma(ctx, [(-98, -262), (-92, -318), (-40, -360), (30, -362), (88, -322), (98, -262), (60, -300), (-10, -310), (-60, -296)], cab, sombra=False, seed=seed + 11)
    elif estilo == "coque":
        forma(ctx, pts_elipse(0, -372, 46, 40, 14), cab, sombra=False, seed=seed + 12)
        forma(ctx, [(-98, -250), (-90, -320), (-30, -358), (40, -358), (92, -318), (98, -250), (70, -300), (0, -318), (-70, -300)], cab, sombra=False, seed=seed + 11)
    elif estilo in ("longo", "cacheado"):
        forma(ctx, [(-100, -230), (-96, -320), (-30, -364), (40, -364), (96, -320), (100, -230), (60, -300), (10, -320), (-40, -306)], cab, sombra=False, seed=seed + 11)
    # rosto
    expr = st.get("expressao", "neutro")
    look = LOOK.get(st.get("olhar", "camera"), (0, 0))
    lid = piscada(t, seed, 0)
    for sx in (-1, 1):
        ex, ey = sx * 34 + look[0] * 6, -255 + look[1] * 5
        if lid > 0.5:
            traco(ctx, [(ex - 12, ey), (ex + 12, ey)], lw=6, seed=seed + 20 + sx)
        else:
            ctx.save(); ctx.translate(ex, ey); ctx.scale(1, 1.4 if expr == "surpreso" else 1.2)
            ctx.arc(0, 0, 10, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill(); ctx.restore()
        dy = {"bravo": 6 * sx * -1, "surpreso": -14, "triste": -6 * sx}.get(expr, 0)
        inc = {"bravo": 10, "triste": -8}.get(expr, 0)
        traco(ctx, [(sx * 34 - 20, -292 + dy + (inc if sx < 0 else 0)), (sx * 34 + 20, -292 + dy + (inc if sx > 0 else 0))], lw=8, seed=seed + 24 + sx)
    traco(ctx, [(-6, -240), (4, -222), (-6, -216)], lw=4, alpha=0.6, seed=seed + 27)  # nariz
    boca(ctx, {"feliz": "sorriso", "surpreso": "o", "triste": "triste", "bravo": "triste"}.get(expr, "reta"), 0, -196, 0.9, seed + 28)
    # braços
    if st.get("segura") == "celular":
        for sx in (-1, 1):
            traco(ctx, [(sx * 116, -90), (sx * 120, 0), (sx * 40, 10)], lw=26, seed=seed + 30 + sx)
            traco(ctx, [(sx * 116, -90), (sx * 120, 0), (sx * 40, 10)], lw=14, cor=roupa, seed=seed + 30 + sx, amp=0)
        ctx.save(); ctx.translate(0, -30)
        forma(ctx, pts_ret(-50, -80, 100, 160, 16), hexc("#3A2E52"), sombra=True, lw=5, seed=seed + 33, sombra_off=(6, 8)); ctx.restore()
        for sx in (-1, 1):
            forma(ctx, pts_elipse(sx * 44, 16, 22, 20, 10), pele, sombra=False, lw=5, seed=seed + 34 + sx)
    else:
        bal = math.sin(t * 2.2) * 5
        for sx in (-1, 1):
            traco(ctx, [(sx * 116, -90), (sx * 150, 20 + bal), (sx * 150, 110)], lw=26, seed=seed + 30 + sx)
            traco(ctx, [(sx * 116, -90), (sx * 150, 20 + bal), (sx * 150, 110)], lw=14, cor=roupa, seed=seed + 30 + sx, amp=0)
            forma(ctx, pts_elipse(sx * 150, 124, 22, 20, 10), pele, sombra=False, lw=5, seed=seed + 34 + sx)
    return {"corpo": (-160, -380, 160, 350), "rosto": (-100, -360, 100, -150)}


# ============================ OBJETOS ============================
def _boca_tela(ctx, x, y, w, h, abre, t, seed):
    """Boca com dentes dentro da tela do celular (o feed comendo)."""
    oh = h * (0.18 + 0.5 * abre)
    cy = y + h * 0.5
    pts = [(x + w * 0.08, cy), (x + w * 0.3, cy - oh / 2), (x + w * 0.7, cy - oh / 2), (x + w * 0.92, cy), (x + w * 0.7, cy + oh / 2), (x + w * 0.3, cy + oh / 2)]
    forma(ctx, pts, hexc("#5A0F2A"), sombra=False, lw=6, seed=seed)
    ctx.save(); path_suave(ctx, jitter(pts, 1.6, seed)); ctx.clip()
    forma(ctx, pts_elipse(x + w * 0.5, cy + oh * 0.42, w * 0.26, oh * 0.28, 14), hexc("#FF5A7A"), sombra=False, lw=4, seed=seed + 1)
    n = 6
    for row, (yy, d) in enumerate(((cy - oh / 2, 1), (cy + oh / 2, -1))):
        for i in range(n):
            tx = x + w * (0.2 + 0.6 * (i + 0.5) / n)
            tw = w * 0.6 / n * 0.5
            forma(ctx, [(tx - tw, yy - 6 * d), (tx + tw, yy - 6 * d), (tx, yy + d * oh * 0.22)], (1, 1, 1), sombra=False, lw=4, seed=seed + 10 + i + row * 10, amp=0.6)
    ctx.restore()


def _tela(ctx, st, x, y, w, h, t, pal, seed):
    modo = st.get("tela", "feed")
    cor = hexc(st["cor_tela"]) if st.get("cor_tela") else pal[3]
    ctx.save(); path_suave(ctx, pts_ret(x, y, w, h, 22)); ctx.clip()
    ctx.set_source_rgb(*cor); ctx.paint()
    if modo == "feed":
        rol = (t * st.get("rolagem", 260)) % 220
        for i in range(-1, int(h / 220) + 2):
            yy = y + 20 + i * 220 - rol
            forma(ctx, pts_ret(x + 18, yy, w - 36, 190, 18), clareia(cor, 0.85), sombra=False, lw=4, seed=seed + i % 4)
            forma(ctx, pts_ret(x + 34, yy + 16, (w - 68), 110, 12), [pal[2], pal[0], hexc("#38D1C6"), pal[3]][i % 4], sombra=False, lw=3, seed=seed + 5 + i % 4)
            for k in range(2):
                ctx.rectangle(x + 34, yy + 140 + k * 22, (w - 68) * (0.8 - 0.3 * k), 12); ctx.set_source_rgba(*INK, 0.35); ctx.fill()
    elif modo == "boca":
        _boca_tela(ctx, x, y, w, h, st.get("boca_abre", 0.6), t, seed)
    elif modo == "texto":
        linhas = st.get("linhas", [])
        tam = st.get("tam_texto", w * 0.12)
        y0 = y + h / 2 - (len(linhas) - 1) * tam * 0.65
        for i, ln in enumerate(linhas):
            texto(ctx, str(ln), x + w / 2, y0 + i * tam * 1.3, tam * (1.9 if i == len(linhas) - 1 and st.get("ultima_grande") else 1), cor=BRANCO, max_w=w * 0.88)
    ctx.restore()


def desenha_celular(ctx, st, t, pal, seed):
    w, h = 340, 660
    forma(ctx, pts_ret(-w / 2, -h / 2, w, h, 46), hexc("#2B2238"), sombreado=0.06, seed=seed, lw=LW + 1)
    sx, sy, sw, sh = -w / 2 + 18, -h / 2 + 46, w - 36, h - 92
    _tela(ctx, st, sx, sy, sw, sh, t, pal, seed + 3)
    path_suave(ctx, pts_ret(sx, sy, sw, sh, 22)); ctx.set_line_width(4); ctx.set_source_rgb(*INK); ctx.stroke()
    forma(ctx, pts_ret(-40, -h / 2 + 18, 80, 14, 7), INK, sombra=False, lw=0, seed=seed + 4)
    # reflexo
    ctx.save(); path_suave(ctx, pts_ret(sx, sy, sw, sh, 22)); ctx.clip()
    ctx.move_to(sx + sw * 0.55, sy); ctx.line_to(sx + sw * 0.8, sy); ctx.line_to(sx + sw * 0.25, sy + sh); ctx.line_to(sx, sy + sh); ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.08); ctx.fill(); ctx.restore()
    if st.get("dedao"):
        yy = 120 - 150 * ((t * 1.6) % 1)
        ctx.save(); ctx.translate(120, yy + 220); ctx.rotate(-0.5)
        pele = _cor(st.get("pele"), PELES["media"])
        forma(ctx, pts_ret(-55, -170, 110, 330, 52), pele, sombreado=0.12, seed=seed + 8)
        forma(ctx, pts_ret(-36, -158, 72, 70, 26), clareia(pele, 0.45), sombra=False, lw=4, seed=seed + 9)
        ctx.restore()
    return {"corpo": (-w / 2, -h / 2, w / 2, h / 2), "texto": (sx, sy, sx + sw, sy + sh) if st.get("tela") == "texto" else None}


def desenha_calendario(ctx, st, t, pal, seed):
    w, h = 600, 560
    forma(ctx, pts_ret(-w / 2, -h / 2, w, h, 26), BRANCO, sombreado=0.05, seed=seed)
    forma(ctx, pts_ret(-w / 2, -h / 2, w, 130, 26), hexc(st.get("cor", "#E8352A")), sombra=False, seed=seed + 1)
    for sx in (-1, 1):   # argolas
        forma(ctx, pts_ret(sx * 150 - 12, -h / 2 - 36, 24, 70, 12), hexc("#BDB7C4"), sombra=False, lw=5, seed=seed + 2 + sx)
    texto(ctx, str(st.get("titulo", "2026")), 0, -h / 2 + 68, 78, cor=BRANCO, sombra=False)
    comidos = st.get("comidos", 0)
    cols, rows = 7, 5
    cw, ch = (w - 60) / cols, (h - 170) / rows
    r = random.Random(seed)
    for i in range(cols * rows):
        c, rr = i % cols, i // cols
        x = -w / 2 + 30 + c * cw; y = -h / 2 + 150 + rr * ch
        n = i + 1
        if n > 31:
            continue
        if i < comidos:   # buraco com mordida
            pts = [(x + 6 + r.uniform(-4, 4), y + 6), (x + cw * 0.5, y + 14 + r.uniform(-3, 6)), (x + cw - 6, y + 6), (x + cw - 10, y + ch - 6), (x + cw * 0.4, y + ch - 14), (x + 8, y + ch - 6)]
            forma(ctx, pts, escurece(pal[0], 0.55), sombra=False, lw=3, seed=seed + 100 + i, amp=1)
        else:
            path_suave(ctx, pts_ret(x + 4, y + 4, cw - 8, ch - 8, 8, 2)); ctx.set_source_rgba(*INK, 0.07); ctx.fill()
            ctx.select_font_face("Fredoka Light", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(34)
            s = str(n); tw = ctx.text_extents(s)[2]
            ctx.move_to(x + cw / 2 - tw / 2, y + ch / 2 + 12); ctx.set_source_rgb(*INK); ctx.show_text(s)
    return {"corpo": (-w / 2, -h / 2 - 36, w / 2, h / 2), "texto": (-w / 2, -h / 2, w / 2, -h / 2 + 130)}


def desenha_folhinha(ctx, n, cor, seed):
    forma(ctx, pts_ret(-38, -38, 76, 76, 10), BRANCO, sombra=False, lw=5, seed=seed, amp=1)
    ctx.rectangle(-36, -36, 72, 16); ctx.set_source_rgb(*cor); ctx.fill()
    ctx.select_font_face("Fredoka Light", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(34)
    s = str(n); tw = ctx.text_extents(s)[2]; ctx.move_to(-tw / 2, 24); ctx.set_source_rgb(*INK); ctx.show_text(s)


def desenha_relogio(ctx, st, t, pal, seed):
    R = 230
    forma(ctx, pts_elipse(0, 0, R + 26, R + 26, 30), hexc(st.get("cor", "#2A7DE1")) if st.get("cor") else pal[3], sombreado=0.08, seed=seed)
    forma(ctx, pts_elipse(0, 0, R, R, 30), BRANCO, sombra=False, seed=seed + 1)
    horas = st.get("horas", 0)
    if horas > 0:   # fatia das horas marcadas
        ctx.move_to(0, 0); ctx.arc(0, 0, R - 14, -math.pi / 2, -math.pi / 2 + 2 * math.pi * min(horas, 12) / 12); ctx.close_path()
        ctx.set_source_rgb(*pal[2]); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    for i in range(12):
        a = 2 * math.pi * i / 12
        traco(ctx, [(math.sin(a) * (R - 22), -math.cos(a) * (R - 22)), (math.sin(a) * (R - (48 if i % 3 == 0 else 34)), -math.cos(a) * (R - (48 if i % 3 == 0 else 34)))], lw=8 if i % 3 == 0 else 5, seed=seed + 10 + i, amp=0.4)
    giro = st.get("giro", 0.0)
    am = st.get("_ang_min", 0) + t * giro * 2 * math.pi
    ah = horas / 12 * 2 * math.pi + t * giro * 2 * math.pi / 12
    traco(ctx, [(0, 0), (math.sin(ah) * R * 0.5, -math.cos(ah) * R * 0.5)], lw=16, seed=seed + 30, amp=0)
    traco(ctx, [(0, 0), (math.sin(am) * R * 0.78, -math.cos(am) * R * 0.78)], lw=10, seed=seed + 31, amp=0)
    forma(ctx, pts_elipse(0, 0, 18, 18, 10), INK, sombra=False, lw=0, seed=seed + 32)
    for sx in (-1, 1):   # sininhos do despertador
        forma(ctx, pts_elipse(sx * 150, -R - 30, 60, 40, 16), hexc(st.get("cor", "#2A7DE1")) if st.get("cor") else pal[3], sombra=False, seed=seed + 40 + sx)
    return {"corpo": (-R - 26, -R - 70, R + 26, R + 26)}


def fmt_num(v, casas=0):
    if casas:
        s = f"{v:,.{casas}f}"
    else:
        s = f"{int(round(v)):,}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def desenha_contador(ctx, st, t, pal, seed):
    v = st.get("valor", 0)
    s = st.get("prefixo", "") + fmt_num(v, st.get("casas", 0)) + st.get("sufixo", "")
    tam = st.get("tam", 220)
    cor = hexc(st["cor"]) if st.get("cor") else pal[2]
    if st.get("fundo", True):
        tw = medir(ctx, s, tam)
        forma(ctx, pts_ret(-tw / 2 - 50, -tam * 0.62, tw + 100, tam * 1.24, 40), INK, sombra=True, lw=0, seed=seed, sombra_off=(12, 14))
    b = texto(ctx, s, 0, 0, tam, cor=cor)
    return {"corpo": b, "texto": b}


def desenha_barra(ctx, st, t, pal, seed):
    """Barra vertical que cresce para cima a partir da base (y do elemento = base). 'pilha' = segmentos empilhados."""
    bw = st.get("largura", 200); hmax = st.get("altura", 640); vmax = st.get("max", 100)
    v = st.get("valor", 0)
    segs = st.get("pilha") or [{"valor": vmax, "cor": st.get("cor"), "rotulo": ""}]
    y = 0; acc = 0; caixas = []; y_rot = 1e9
    # trilho
    path_suave(ctx, pts_ret(-bw / 2, -hmax, bw, hmax, 18)); ctx.set_source_rgba(*INK, 0.16); ctx.fill()
    for i, sg in enumerate(segs):
        sv = sg["valor"] if i < len(segs) - 1 or st.get("pilha") else vmax
        vis = clamp(v - acc, 0, sv)
        acc += sv
        if vis <= 0:
            continue
        hh = hmax * vis / vmax
        cor = hexc(sg["cor"]) if sg.get("cor") else [pal[2], pal[3], hexc("#38D1C6"), pal[4]][i % 4]
        forma(ctx, pts_ret(-bw / 2, y - hh, bw, hh, 12 if hh > 24 else hh / 2), cor, sombreado=0.1 if hh > 40 else 0, seed=seed + i, amp=1.2)
        rot = sg.get("rotulo", "")
        if rot and vis >= sv * 0.999:
            if hh >= 110:
                texto(ctx, rot, 0, y - hh / 2, st.get("tam_rotulo", 46), cor=BRANCO, max_w=bw - 20)
            else:
                lado = st.get("lado_rotulo", "esq")
                ly = min(y - hh / 2, y_rot - 54); y_rot = ly
                xe = (-bw / 2 - 30) if lado == "esq" else (bw / 2 + 30)
                traco(ctx, [(xe + (8 if lado == "esq" else -8), ly), ((-bw / 2) if lado == "esq" else (bw / 2), y - hh / 2)], lw=4, seed=seed + 70 + i, amp=0.3)
                bx = texto(ctx, rot, xe, ly, 44, cor=BRANCO, ancora="r" if lado == "esq" else "l")
                caixas.append(bx)
        y -= hh
    if st.get("total"):
        caixas.append(texto(ctx, st["total"], 0, y - 56, st.get("tam_total", 72), cor=hexc(st.get("cor_total", "#FFF8EC"))))
    if st.get("nome"):
        caixas.append(texto(ctx, st["nome"], 0, 50, 52, cor=BRANCO))
    xs = [c[0] for c in caixas] + [-bw / 2]; xe = [c[2] for c in caixas] + [bw / 2]
    ys = [c[1] for c in caixas] + [-hmax]; ye = [c[3] for c in caixas] + [0]
    return {"corpo": (min(xs), min(ys), max(xe), max(ye)), "texto": (min(xs), min(ys), max(xe), max(ye))}


def desenha_comentario(ctx, st, t, pal, seed):
    w = st.get("largura", 820)
    linhas = st.get("texto", "").split("\n")
    h = 150 + 62 * (len(linhas) - 1)
    forma(ctx, pts_ret(-w / 2, -h / 2, w, h, 34), BRANCO, sombreado=0.03, seed=seed)
    forma(ctx, pts_elipse(-w / 2 + 80, -h / 2 + 75, 46, 46, 16), hexc(st.get("cor_avatar", "#2A7DE1")), sombra=False, lw=5, seed=seed + 1)
    ctx.select_font_face("Fredoka Light", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(34); ctx.move_to(-w / 2 + 150, -h / 2 + 58); ctx.set_source_rgba(*INK, 0.55); ctx.show_text(st.get("nome", "@alguem"))
    ctx.set_font_size(46)
    for i, ln in enumerate(linhas):
        ctx.move_to(-w / 2 + 150, -h / 2 + 112 + i * 62); ctx.set_source_rgb(*INK); ctx.show_text(ln)
    return {"corpo": (-w / 2, -h / 2, w / 2, h / 2), "texto": (-w / 2, -h / 2, w / 2, h / 2)}


def desenha_seta(ctx, st, t, pal, seed):
    """Seta desenhada do centro do elemento até 'para' (relativo, em px: [dx, dy]). 'progresso' 0..1 desenha aos poucos."""
    dx, dy = st.get("vetor", [0, -200])
    p = clamp(st.get("progresso", 1.0))
    curva = st.get("curva", 0.25)
    mx, my = dx / 2 - dy * curva, dy / 2 + dx * curva
    pts = []
    for i in range(int(20 * p) + 1):
        u = i / 20
        pts.append(((1 - u) ** 2 * 0 + 2 * (1 - u) * u * mx + u * u * dx, 2 * (1 - u) * u * my + u * u * dy))
    if len(pts) < 2:
        return {"corpo": (0, 0, 1, 1)}
    cor = hexc(st["cor"]) if st.get("cor") else pal[2]
    traco(ctx, pts, lw=30, seed=seed); traco(ctx, pts, lw=16, cor=cor, seed=seed, amp=0)
    if p > 0.95:
        ex, ey = pts[-1]; px, py = pts[-3]
        a = math.atan2(ey - py, ex - px)
        hd = [(ex + math.cos(a) * 30, ey + math.sin(a) * 30), (ex + math.cos(a + 2.4) * 52, ey + math.sin(a + 2.4) * 52), (ex + math.cos(a - 2.4) * 52, ey + math.sin(a - 2.4) * 52)]
        forma(ctx, hd, cor, sombra=False, lw=LW, seed=seed + 1, amp=0.8)
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    return {"corpo": (min(xs) - 40, min(ys) - 40, max(xs) + 40, max(ys) + 40)}


def desenha_carimbo(ctx, st, t, pal, seed):
    s = st.get("texto", "CARIMBO").upper()
    tam = st.get("tam", 110)
    cor = hexc(st.get("cor", "#E8352A"))
    tw = medir(ctx, s, tam)
    w, h = tw + 90, tam * 1.5
    ctx.rotate(math.radians(st.get("inclina", -10)))
    ctx.push_group()   # as falhas de tinta só furam o carimbo
    for k, lw in ((0, 12), (18, 5)):
        path_suave(ctx, jitter(pts_ret(-w / 2 + k, -h / 2 + k, w - 2 * k, h - 2 * k, 18), 2.5, seed + k)); ctx.set_line_width(lw); ctx.set_source_rgb(*cor); ctx.stroke()
    ctx.select_font_face("Fredoka Light", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(tam)
    xb, yb, tw2, th, _, _ = ctx.text_extents(s)
    ctx.move_to(-tw2 / 2 - xb, tam * 0.36); ctx.set_source_rgb(*cor); ctx.show_text(s)
    r = random.Random(seed)   # falhas de tinta
    for i in range(40):
        ctx.new_sub_path(); ctx.arc(r.uniform(-w / 2, w / 2), r.uniform(-h / 2, h / 2), r.uniform(2, 7), 0, 2 * math.pi)
    ctx.set_operator(cairo.OPERATOR_DEST_OUT); ctx.set_source_rgba(0, 0, 0, 1); ctx.fill(); ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(0.92)
    return {"corpo": (-w / 2 - 20, -h / 2 - 40, w / 2 + 20, h / 2 + 40), "texto": (-w / 2 - 20, -h / 2 - 40, w / 2 + 20, h / 2 + 40)}


def desenha_texto(ctx, st, t, pal, seed):
    s = st.get("texto", "")
    tam = st.get("tam", 110)
    cor = hexc(st["cor"]) if st.get("cor") else BRANCO
    if st.get("fundo"):
        tw = medir(ctx, s, tam)
        forma(ctx, pts_ret(-tw / 2 - 40, -tam * 0.65, tw + 80, tam * 1.3, tam * 0.4), hexc(st["fundo"]), seed=seed)
    linhas = s.split("\n")
    caixas = [texto(ctx, ln, 0, (i - (len(linhas) - 1) / 2) * tam * 1.15, tam, cor=cor, max_w=st.get("max_w", 860)) for i, ln in enumerate(linhas)]
    b = (min(c[0] for c in caixas), min(c[1] for c in caixas), max(c[2] for c in caixas), max(c[3] for c in caixas))
    return {"corpo": b, "texto": b}


def desenha_rachadura(ctx, st, t, pal, seed):
    """Tela rachada (vidro) a partir do centro do elemento. 'progresso' 0..1."""
    p = clamp(st.get("progresso", 1.0))
    r = random.Random(seed)
    raios = []
    for i in range(12):
        a = 2 * math.pi * i / 12 + r.uniform(-0.15, 0.15)
        pts = [(0, 0)]; x = y = 0
        for k in range(5):
            ln = r.uniform(60, 130) * p
            a += r.uniform(-0.22, 0.22)
            x += math.cos(a) * ln; y += math.sin(a) * ln
            pts.append((x, y))
        raios.append(pts)
    for lw, cor in ((15, INK), (5, (1, 1, 1))):
        for pts in raios:
            ctx.move_to(*pts[0]); [ctx.line_to(*q) for q in pts[1:]]
        for k in (1, 2):   # anéis em zigue-zague ligando os raios
            if p > 0.4:
                ctx.move_to(*raios[0][k]); [ctx.line_to(*rr[k]) for rr in raios[1:]]; ctx.close_path()
        ctx.set_line_width(lw); ctx.set_source_rgb(*cor); ctx.set_line_join(cairo.LINE_JOIN_MITER); ctx.stroke()
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    return {"corpo": (-500, -500, 500, 500)}


def desenha_bloco(ctx, st, t, pal, seed):
    """Retângulo/cartão colorido genérico com texto opcional (split, antes/depois, placas)."""
    w, h = st.get("largura", 400), st.get("altura", 300)
    cor = hexc(st["cor"]) if st.get("cor") else pal[2]
    forma(ctx, pts_ret(-w / 2, -h / 2, w, h, st.get("raio", 28)), cor, sombreado=0.06, seed=seed)
    b = None
    if st.get("texto"):
        b = texto(ctx, st["texto"], 0, 0, st.get("tam", 70), cor=hexc(st.get("cor_texto", "#FFF8EC")), max_w=w - 40)
    return {"corpo": (-w / 2, -h / 2, w / 2, h / 2), "texto": b}


DESENHOS = {"celular": desenha_celular, "calendario": desenha_calendario, "relogio": desenha_relogio, "contador": desenha_contador,
            "barra": desenha_barra, "comentario": desenha_comentario, "seta": desenha_seta, "carimbo": desenha_carimbo,
            "texto": desenha_texto, "rachadura": desenha_rachadura, "bloco": desenha_bloco}


# ============================ CENÁRIOS ============================
def cenario(ctx, nome, pal, t, opts, seed=1):
    bg, bg2, a1, a2, a3 = pal
    ctx.set_source_rgb(*bg); ctx.paint()
    padrao = opts.get("padrao", "raios" if nome == "chapado" else None)
    if nome in ("chapado", "celular") and padrao:
        ctx.save()
        if padrao == "raios":
            ctx.translate(W / 2, H * 0.4); ctx.rotate(t * 0.08)
            for i in range(0, 24, 2):
                a0, a1_ = 2 * math.pi * i / 24, 2 * math.pi * (i + 1) / 24
                ctx.move_to(0, 0); ctx.arc(0, 0, 2400, a0, a1_); ctx.close_path()
            ctx.set_source_rgb(*bg2); ctx.fill()
        elif padrao == "bolinhas":
            for yy in range(0, H + 80, 80):
                for xx in range(0, W + 80, 80):
                    ctx.new_sub_path(); ctx.arc(xx + (40 if (yy // 80) % 2 else 0), yy + (t * 20) % 80, 12, 0, 2 * math.pi)
            ctx.set_source_rgb(*bg2); ctx.fill()
        elif padrao == "listras":
            off = (t * 30) % 160
            for k in range(-20, 30):
                x0 = k * 160 + off
                ctx.move_to(x0, 0); ctx.line_to(x0 + 80, 0); ctx.line_to(x0 + 80 - H * 0.6, H); ctx.line_to(x0 - H * 0.6, H); ctx.close_path()
            ctx.set_source_rgb(*bg2); ctx.fill()
        ctx.restore()
    if nome == "sala":
        ctx.rectangle(0, 1180, W, 740); ctx.set_source_rgb(*escurece(bg, 0.25)); ctx.fill()     # rodapé/parede baixa
        forma(ctx, [(-20, 1420), (W + 20, 1420), (W + 20, H + 20), (-20, H + 20)], hexc("#8A4B2A"), sombra=False, seed=seed)  # chão
        for k in range(6):
            traco(ctx, [(k * 220 - 40, 1440 + (k % 2) * 60), (k * 220 + 120, 1440 + (k % 2) * 60)], lw=4, alpha=0.4, seed=seed + k)
        forma(ctx, pts_ret(90, 260, 330, 400, 18), hexc("#FFF3D6"), seed=seed + 2)           # janela
        forma(ctx, pts_ret(112, 282, 286, 356, 10), hexc("#1D1B3A"), sombra=False, lw=4, seed=seed + 3)
        ctx.arc(330, 360, 34, 0, 2 * math.pi); ctx.set_source_rgb(*hexc("#FFE9A8")); ctx.fill()
        traco(ctx, [(255, 282), (255, 638)], lw=8, seed=seed + 4); traco(ctx, [(112, 460), (398, 460)], lw=8, seed=seed + 5)
        forma(ctx, pts_ret(640, 330, 260, 200, 10), a1, seed=seed + 6)                         # quadro
        forma(ctx, pts_ret(668, 358, 204, 144, 6), a2, sombra=False, lw=4, seed=seed + 7)
        traco(ctx, [(880, 560), (880, 1400)], lw=14, seed=seed + 8)                            # luminária
        forma(ctx, [(800, 560), (960, 560), (920, 440), (840, 440)], a3, seed=seed + 9)
        sofa = hexc(opts.get("cor_sofa", "#2A7DE1")) if opts.get("cor_sofa") else a2
        forma(ctx, pts_ret(70, 860, 940, 300, 70), escurece(sofa, 0.12), seed=seed + 10)     # encosto
        forma(ctx, pts_ret(40, 1080, 1000, 230, 50), sofa, sombreado=0.05, seed=seed + 11)     # assento
        for sx in (40, 900):
            forma(ctx, pts_ret(sx, 980, 140, 330, 60), escurece(sofa, 0.05), seed=seed + 12 + sx)
        for k in range(3):
            forma(ctx, pts_ret(200 + k * 230, 1300, 40, 110, 10), INK, sombra=False, lw=0, seed=seed + 20 + k) if k != 1 else None
    elif nome == "escritorio":
        ctx.rectangle(0, 1250, W, 670); ctx.set_source_rgb(*escurece(bg, 0.3)); ctx.fill()
        forma(ctx, pts_ret(120, 240, 420, 460, 14), hexc("#BFE6FF"), seed=seed + 1)
        for k in range(8):
            traco(ctx, [(140, 280 + k * 52), (520, 280 + k * 52)], lw=6, alpha=0.6, seed=seed + 2 + k)
        forma(ctx, pts_ret(-40, 1180, W + 80, 90, 18), hexc("#C98A4B"), seed=seed + 12)       # mesa
        forma(ctx, pts_ret(560, 760, 400, 290, 20), INK, sombra=True, lw=LW, seed=seed + 13)  # monitor
        forma(ctx, pts_ret(580, 780, 360, 250, 12), a2, sombra=False, lw=4, seed=seed + 14)
        forma(ctx, pts_ret(735, 1050, 50, 130, 6), INK, sombra=False, lw=0, seed=seed + 15)
        forma(ctx, pts_ret(170, 1060, 110, 130, 20), a1, seed=seed + 16)                       # caneca
        forma(ctx, pts_ret(860, 520, 110, 150, 20), hexc("#C8531F"), seed=seed + 17)          # vaso
        for k in range(5):
            forma(ctx, pts_elipse(915 + (k - 2) * 34, 470 - abs(k - 2) * 20, 30, 70, 12), VERDE, sombra=False, lw=5, seed=seed + 18 + k)
    elif nome == "quarto":
        ctx.rectangle(0, 1300, W, 620); ctx.set_source_rgb(*escurece(bg, 0.3)); ctx.fill()
        forma(ctx, pts_ret(600, 240, 360, 420, 18), hexc("#FFF3D6"), seed=seed + 1)
        forma(ctx, pts_ret(622, 262, 316, 376, 10), hexc("#141233"), sombra=False, lw=4, seed=seed + 2)
        forma(ctx, pts_elipse(840, 360, 46, 46, 16), hexc("#FFE9A8"), sombra=False, lw=4, seed=seed + 3)
        forma(ctx, pts_ret(90, 330, 300, 400, 10), a1, seed=seed + 4)                          # pôster
        forma(ctx, pts_elipse(240, 530, 90, 90, 18), a2, sombra=False, lw=5, seed=seed + 5)
        forma(ctx, pts_ret(40, 1000, 1000, 120, 40), BRANCO, seed=seed + 6)                    # cama
        forma(ctx, pts_ret(20, 1090, 1040, 260, 50), a2, sombreado=0.05, seed=seed + 7)
        forma(ctx, pts_ret(70, 930, 300, 140, 60), BRANCO, seed=seed + 8)                      # travesseiro
    elif nome == "celular":
        forma(ctx, pts_ret(40, 90, W - 80, H - 180, 90), hexc("#2B2238"), seed=seed, lw=LW + 2)
        tela = hexc(opts["cor_tela"]) if opts.get("cor_tela") else escurece(bg, 0.55)
        forma(ctx, pts_ret(76, 170, W - 152, H - 340, 60), tela, sombra=False, lw=5, seed=seed + 1)
        forma(ctx, pts_ret(W / 2 - 90, 120, 180, 30, 15), INK, sombra=False, lw=0, seed=seed + 2)
        ctx.select_font_face("Fredoka Light", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(40)
        ctx.move_to(130, 240); ctx.set_source_rgb(*BRANCO); ctx.show_text(opts.get("hora", "23:47"))
        for k in range(4):
            ctx.rectangle(860 + k * 18, 230 - k * 8, 12, 10 + k * 8)
        ctx.fill()
