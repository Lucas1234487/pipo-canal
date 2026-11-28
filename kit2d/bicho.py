"""Bichos do PipoPop 2D ("tipo": "bicho"): pombo, gato, vaca, galinha, cavalo, coelho no traço da casa.
Contorno grosso, cor chapada com sombra simples, olhos grandes. Traço próprio (nada copiado de personagem de terceiros).

Propriedades (todas mudam com "muda"):
  especie: pombo, gato, vaca, galinha, cavalo, coelho, tiranossauro, bicodepato (dinos: ver seção DINOSSAUROS no fim do arquivo)
  olhos:   "lado" (como é de verdade: um olho de cada lado da cabeça) | "frente" (os dois juntos na cara, com sobrancelha). Gato é sempre "frente".
  vista:   "frente" (encara a câmera) | "perfil" (olhando para a direita; "espelha": true vira) | "cima" (visto do alto, cabeça para cima)
  campo:   graus do campo de visão (só em "cima"): desenha o cone translúcido saindo dos olhos. cego: true pinta a zona cega de vermelho.
  alcance: raio do cone em px (620). olhar: camera, esq, dir, cima, baixo. expressao: neutro, desconfiado, julgando, assustado, feliz.
  pose:    parado, bicando, agachado, voando (só aves). anda: true (passo no lugar; andando com "move" já anda sozinho).
  cor, cor2: troca as cores do corpo/barriga.
Escala 1: ~420 px de altura, centro no meio do bicho, pés em y +205 (local).
"""
import math
import cairo
from estilo import (INK, LW, BRANCO, hexc, mix, escurece, clareia, forma, traco, pts_elipse, path_suave, jitter, clamp)

ESPECIES = {
    "pombo":   dict(ave=True, cor="#8F99B0", cor2="#C3C9D8", asa="#7A839A", pesc="#3E9E7C", pesc2="#8B5BA6", bico="#4B4452", cere="#F1EDE6",
                    perna="#E8807C", anel="#F0782A", campo=340),
    "galinha": dict(ave=True, cor="#F8F2E4", cor2="#E8DCC2", asa="#E9DDC3", crista="#E8352A", bico="#F5B323", perna="#F5B323", campo=300),
    "gato":    dict(cor="#F29A3A", cor2="#FFE3C0", listra="#C2621B", nariz="#F07B9C", iris="#A6CE39", campo=200),
    "vaca":    dict(cor="#FBF7F0", cor2="#F5A8B8", mancha="#2B2233", chifre="#EEDFBF", casco="#3A2E3A", campo=330),
    "cavalo":  dict(cor="#9C5B33", cor2="#C9905F", crina="#3A2418", casco="#2E2530", campo=350),
    "coelho":  dict(cor="#C8BFC9", cor2="#F7F1F3", nariz="#F07B9C", interno="#F5B2C4", campo=360),
}
AVES = ("pombo", "galinha")
LID = {"neutro": 0.1, "desconfiado": 0.5, "julgando": 0.46, "assustado": 0.0, "feliz": 0.0}
BOCA = {"neutro": "reta", "desconfiado": "sorriso_torto", "julgando": "triste", "assustado": "o", "feliz": "sorriso"}
LOOK = {"camera": (0, 0), "frente": (0, 0), "baixo": (0, 0.85), "cima": (0, -0.85), "esq": (-0.9, 0.05), "dir": (0.9, 0.05),
        "esquerda": (-0.9, 0.05), "direita": (0.9, 0.05)}


# ============================ primitivas ============================
def EL(cx, cy, rx, ry, n=24, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def F(ctx, pts, cor, seed, sombra=False, sb=0.0, lw=LW, amp=1.4):
    forma(ctx, pts, cor, sombra=sombra, sombreado=sb, lw=lw, seed=seed, amp=amp)


def tubo(ctx, pts, cor, lw, seed):
    """Rabo/perna grossa: traço de contorno + traço da cor por cima (mesmo tremido)."""
    traco(ctx, pts, lw=lw + 2 * LW, cor=INK, seed=seed, amp=1.0)
    traco(ctx, pts, lw=lw, cor=cor, seed=seed, amp=1.0)


def manchas(ctx, pts, seed, blobs, cor, amp=1.4):
    """Pinta manchas recortadas dentro de uma forma já desenhada e refaz o contorno por cima."""
    p = jitter(pts, amp, seed)
    ctx.save(); path_suave(ctx, p); ctx.clip()
    for i, (x, y, rx, ry, rot) in enumerate(blobs):
        path_suave(ctx, jitter(EL(x, y, rx, ry, 12, rot), 3, seed + 31 + i)); ctx.set_source_rgb(*cor); ctx.fill()
    ctx.restore()
    path_suave(ctx, p); ctx.set_line_width(LW); ctx.set_source_rgb(*INK); ctx.stroke()


def _piscada(t, seed, base):
    import random
    r = random.Random(seed)
    tt = r.uniform(0.3, 1.6)
    while tt < t + 1:
        if tt <= t < tt + 0.13:
            return 1.0
        tt += r.uniform(2.0, 3.4)
    return base


def olho(ctx, x, y, rx, ry, look, lid, cor_pal, seed, pupila=0.46, iris=None, anel=None, rot=0.0, feliz=False):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    if anel:
        F(ctx, EL(0, 0, rx * 1.3, ry * 1.3, 18), anel, seed + 5, lw=4, amp=0.6)
    if feliz:   # olho fechado de alegria (^)
        traco(ctx, [(-rx * 0.85, ry * 0.3), (0, -ry * 0.5), (rx * 0.85, ry * 0.3)], lw=max(6, min(rx, ry) * 0.34), seed=seed)
        ctx.restore(); return
    p = jitter(EL(0, 0, rx, ry, 20), 0.7, seed)
    path_suave(ctx, p); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.save(); path_suave(ctx, p); ctx.clip()
    r = min(rx, ry)
    px, py = look[0] * (rx - r * pupila) * 0.92, look[1] * (ry - r * pupila) * 0.85
    if iris:
        ctx.arc(px, py, r * min(0.86, pupila * 1.65), 0, 2 * math.pi); ctx.set_source_rgb(*iris); ctx.fill_preserve()
        ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
    ctx.arc(px, py, r * pupila, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    ctx.arc(px - r * 0.17, py - r * 0.19, r * 0.15, 0, 2 * math.pi); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    yl = -ry + 2 * ry * lid
    if lid > 0.01:
        ctx.rectangle(-rx - 6, -ry - 6, 2 * rx + 12, yl + ry + 6); ctx.set_source_rgb(*cor_pal); ctx.fill()
    ctx.restore()
    lwo = max(3.5, min(5.0, r * 0.2))
    if 0.01 < lid < 0.99:
        dx = rx * math.sqrt(max(0, 1 - (yl / ry) ** 2))
        traco(ctx, [(-dx, yl), (0, yl + 1.5), (dx, yl)], lw=lwo, seed=seed + 1, amp=0.5)
    elif lid >= 0.99:
        traco(ctx, [(-rx, 0), (0, 3), (rx, 0)], lw=lwo, seed=seed + 1, amp=0.5)
    path_suave(ctx, p); ctx.set_line_width(lwo); ctx.set_source_rgb(*INK); ctx.stroke()
    ctx.restore()


# (sobe a ponta de dentro, sobe a de fora, sobe tudo) por expressão; desconfiado é torto (um lado diferente do outro)
SOBR = {"neutro": (-2, -2, -6), "julgando": (7, 3, 6), "assustado": (-14, 4, -18), "feliz": (-6, -6, -14)}


def sobrancelhas(ctx, olhos, expr, seed):
    for i, (x, y, rx, ry, lado) in enumerate(olhos):
        if expr == "desconfiado":
            di, do, up = (10, -4, 4) if lado < 0 else (-8, -10, -16)
        else:
            di, do, up = SOBR.get(expr, SOBR["neutro"])
        y0 = y - ry - max(10, ry * 0.42) + up
        w = rx * 0.95
        xi, xo = x - lado * w, x + lado * w
        arco = -5 if expr == "feliz" else -2
        traco(ctx, [(xo, y0 - do), (x, y0 + arco + (di - do) * 0.1 - (di + do) * 0.05), (xi, y0 + di)],
              lw=max(7, min(rx, ry) * 0.36), seed=seed + 40 + i, amp=0.6)


def boca(ctx, expr, x, y, esc, seed):
    tipo = BOCA.get(expr, "reta")
    if tipo == "o":
        F(ctx, EL(x, y + 4 * esc, 13 * esc, 17 * esc, 14), escurece(hexc("#E8352A"), 0.45), seed, lw=5)
    elif tipo == "sorriso":
        traco(ctx, [(x - 24 * esc, y - 6 * esc), (x, y + 10 * esc), (x + 24 * esc, y - 6 * esc)], lw=max(5, 6 * esc), seed=seed)
    elif tipo == "sorriso_torto":
        traco(ctx, [(x - 20 * esc, y + 3 * esc), (x + 6 * esc, y + 3 * esc), (x + 22 * esc, y - 7 * esc)], lw=max(5, 6 * esc), seed=seed)
    elif tipo == "triste":
        traco(ctx, [(x - 20 * esc, y + 5 * esc), (x, y - 1 * esc), (x + 20 * esc, y + 6 * esc)], lw=max(5, 6 * esc), seed=seed)
    else:
        traco(ctx, [(x - 18 * esc, y), (x + 2 * esc, y + 2 * esc), (x + 18 * esc, y - 1 * esc)], lw=max(5, 6 * esc), seed=seed)


# ============================ estado da animação ============================
def _anim(st, t, seed):
    esp = st.get("especie", "pombo")
    if esp not in ESPECIES:
        raise SystemExit(f"bicho: especie '{esp}' não existe. Espécies: {', '.join(ESPECIES)}")
    S = dict(ESPECIES[esp])
    for k in ("cor", "cor2"):
        if st.get(k):
            S[k] = st[k]
    S = {k: (hexc(v) if isinstance(v, str) and v.startswith("#") else v) for k, v in S.items()}
    S["nome"] = esp
    expr = st.get("expressao", "neutro"); expr = expr if expr in LID else "neutro"
    pose = st.get("pose", "parado")
    if pose == "voando" and esp not in AVES:
        pose = "parado"
    vel = st.get("_vel", 0.0)
    anda = bool(st.get("anda")) or abs(vel) > 25
    ph = seed * 0.37
    P = dict(t=t, seed=seed, expr=expr, pose=pose, anda=anda,
             olhos="frente" if esp in ("gato", "tiranossauro") else st.get("olhos", "lado"),
             look=LOOK.get(st.get("olhar", "camera"), (0, 0)), olhar=st.get("olhar", "camera"))
    base = LID[expr]
    P["lid"] = _piscada(t, seed, base) if expr != "feliz" else 0.0
    P["feliz"] = expr == "feliz" and _piscada(t, seed, 0) < 0.5
    P["pupila"] = 0.24 if expr == "assustado" else 0.46
    P["treme"] = math.sin(t * 61) * 2.2 if expr == "assustado" else 0.0
    # bicando: bicada rápida a cada ~0,9 s (aves) ou cabeça baixa pastando (mamíferos)
    if pose == "bicando":
        per = 0.9 if esp in AVES else 1.8
        u = ((t + ph) % per) / per
        P["bica"] = math.sin(math.pi * u / 0.35) if u < 0.35 else 0.0
        if esp not in AVES:
            P["bica"] = 0.75 + 0.25 * math.sin(t * 2.4 + ph)
    else:
        P["bica"] = 0.0
    P["agach"] = 1.0 if pose == "agachado" else 0.0
    P["asa"] = math.sin(t * 15 + ph) if pose == "voando" else 0.0
    P["voo_dy"] = -38 - 14 * math.sin(t * 15 + ph + 1.2) if pose == "voando" else 0.0
    # andar: passo (fase 0..2pi) e cabeçada do pombo
    P["passo"] = (t * (7.5 if esp in AVES else 6.0) + ph) if anda else None
    if anda and esp == "pombo":
        u = (t * 2.4 + ph) % 1.0
        # empurra a cabeça para frente rápido e segura enquanto o corpo alcança
        P["cabecada"] = clamp(u / 0.1) if u < 0.55 else 1 - clamp((u - 0.55) / 0.35)
    else:
        P["cabecada"] = 0.0
    if anda and esp == "galinha":
        P["cabecada"] = 0.5 + 0.5 * math.sin(t * 7.5 + ph)
    # rabo e orelhas
    if esp == "gato" and P["agach"]:
        P["rabo"] = 0.18 * math.sin(t * 9 + ph)   # ponta do rabo tremendo antes do pulo
    else:
        P["rabo"] = 0.28 * math.sin(t * (1.7 if esp == "gato" else 2.6) + ph)
    tw = (t + ph * 3) % 3.1
    P["orelha"] = 0.22 * math.exp(-tw * 9) * math.sin(tw * 40) if tw > 0 else 0.0
    P["olho_pal"] = S["cor"]
    return S, P


def _passo(P, k=0.0, amp=1.0):
    if P["passo"] is None:
        return 0.0
    return math.sin(P["passo"] + k) * amp


# ============================ VISTA DE FRENTE ============================
def _frente(ctx, S, P):
    esp = S["nome"]; sd = P["seed"]; t = P["t"]
    ag = P["agach"]
    ctx.translate(P["treme"], P["voo_dy"])
    if ag:   # agachado (gato pronto para pular): corpo baixo e largo, rebolando de leve
        ctx.translate(math.sin(t * 9 + sd) * 7, 205); ctx.scale(1.08, 0.8); ctx.translate(0, -205)
    hy_off = P["bica"] * (70 if esp in AVES else 40) + ag * 22 - (8 * P["cabecada"] if esp == "pombo" else 0)
    corpo_dy = ag * 30
    face = None
    # ---------- atrás: rabo, penas, asas abertas
    if esp == "gato":
        a = P["rabo"]
        tubo(ctx, [(70, 170 + corpo_dy), (150, 150), (175 + 30 * a, 60), (150 + 50 * a, -10)], S["cor"], 34, sd + 1)
        traco(ctx, [(165 + 40 * a, 20), (172 + 45 * a, 2)], lw=14, cor=S["listra"], seed=sd + 2)
    elif esp == "galinha":
        for i, (x, ang) in enumerate(((-88, -0.5), (88, 0.5), (-60, -0.25), (60, 0.25))):
            F(ctx, EL(x * 1.1, -20 + corpo_dy, 26, 70, 14, ang + 0.06 * math.sin(t * 2 + i)), escurece(S["cor"], 0.06), sd + 3 + i)
    if esp in AVES and P["pose"] == "voando":
        for lado in (-1, 1):
            ctx.save(); ctx.translate(lado * 80, 0 + corpo_dy); ctx.rotate(lado * (-0.15 + 0.65 * P["asa"]))
            w = EL(lado * 120, 0, 135, 46, 18)
            F(ctx, w, S["asa"], sd + 9 + lado, sb=0.2)
            for j in range(3):
                traco(ctx, [(lado * (150 + j * 30), -18), (lado * (195 + j * 22), 28)], lw=5, seed=sd + 12 + j)
            ctx.restore()
    # ---------- pernas
    if esp in AVES:
        if P["pose"] != "voando":
            for i, lado in enumerate((-1, 1)):
                lift = max(0, _passo(P, i * math.pi, 14))
                x = lado * 34; y0 = 140 + corpo_dy * 0.6; y1 = 200 - lift
                traco(ctx, [(x, y0), (x, y1)], lw=9, cor=S["perna"], seed=sd + 20 + i)
                for d in (-1, 0, 1):
                    traco(ctx, [(x, y1), (x + d * 20, y1 + 8 - abs(d) * 2)], lw=7, cor=S["perna"], seed=sd + 22 + d)
                traco(ctx, [(x, y0), (x, y1)], lw=2.5, cor=INK, seed=sd + 26 + i, alpha=0.5)
    else:
        pata = S.get("casco") or S["cor2"]
        for i, lado in enumerate((-1, 1)):
            lift = max(0, _passo(P, i * math.pi, 14))
            x = lado * (46 if esp != "coelho" else 58)
            if esp == "coelho":
                F(ctx, EL(x, 196 - lift, 48, 22, 16), S["cor2"], sd + 30 + i, sombra=True)
                continue
            y0 = 120 + corpo_dy; y1 = 192 - lift - ag * 12
            tubo(ctx, [(x, y0), (x, y1)], S["cor"], 38 if esp != "gato" else 32, sd + 30 + i)
            F(ctx, EL(x, y1 + 8, 24 if esp != "gato" else 28, 14, 14), pata, sd + 32 + i)
    # ---------- corpo
    if esp in AVES:
        bp = EL(0, 40 + corpo_dy, 112, 122, 26)
        F(ctx, bp, S["cor"], sd + 40, sombra=True, sb=0.16)
        F(ctx, EL(0, 70 + corpo_dy, 62, 72, 18), S["cor2"], sd + 41, lw=0)
        if P["pose"] != "voando":
            for lado in (-1, 1):
                F(ctx, EL(lado * 92, 58 + corpo_dy, 38, 88, 18, -lado * 0.12), S["asa"], sd + 42 + lado, sb=0.15)
                if esp == "pombo":
                    for j in range(2):
                        traco(ctx, [(lado * 76, 62 + j * 28 + corpo_dy), (lado * 108, 70 + j * 28 + corpo_dy)], lw=8, seed=sd + 44 + j)
        if esp == "pombo":   # pescoço furta-cor
            F(ctx, EL(0, -38 + corpo_dy * 0.5, 82, 42, 20), S["pesc"], sd + 46)
            manchas(ctx, EL(0, -38 + corpo_dy * 0.5, 82, 42, 20), sd + 46, [(0, -10 + corpo_dy * 0.5, 90, 22, 0)], S["pesc2"])
    else:
        larg = {"gato": (108, 120), "vaca": (138, 100), "cavalo": (122, 96), "coelho": (116, 102)}[esp]
        by = {"gato": 72, "vaca": 92, "cavalo": 100, "coelho": 104}[esp] + corpo_dy
        bp = EL(0, by, larg[0], larg[1], 26)
        F(ctx, bp, S["cor"], sd + 40, sombra=True, sb=0.16)
        if esp == "vaca":
            manchas(ctx, bp, sd + 40, [(-80, by - 20, 50, 38, 0.4), (70, by + 40, 44, 30, -0.3), (20, by - 70, 30, 22, 0)], S["mancha"])
        elif esp in ("gato", "coelho"):
            F(ctx, EL(0, by - 5, 56, 82, 18), S["cor2"], sd + 41, lw=0)
        elif esp == "cavalo":
            F(ctx, EL(0, 20 + corpo_dy * 0.5, 62, 72, 20), S["cor"], sd + 47, sb=0.12)
        if esp == "gato":   # patas da frente
            for lado in (-1, 1):
                tubo(ctx, [(lado * 40, 110 + corpo_dy), (lado * 40, 192 - ag * 14)], S["cor"], 36, sd + 48 + lado)
                F(ctx, EL(lado * 40, 198 - ag * 14, 30, 16, 14), S["cor2"], sd + 50 + lado)
    # ---------- cabeça
    ctx.save(); ctx.translate(0, hy_off)
    face = _cabeca_frente(ctx, S, P)
    ctx.restore()
    fx0, fy0, fx1, fy1 = face
    topo = {"gato": -215, "vaca": -190, "cavalo": -235, "coelho": -228, "pombo": -180, "galinha": -178}[esp]
    lx = {"gato": 200, "vaca": 160, "cavalo": 130, "coelho": 120}.get(esp, 130 if P["pose"] != "voando" else 330)
    dy = P["voo_dy"]
    return {"corpo": (-lx, topo + dy + hy_off * 0.3, lx, 215 + dy), "rosto": (fx0, fy0 + hy_off + dy, fx1, fy1 + hy_off + dy)}


def _cabeca_frente(ctx, S, P):
    esp = S["nome"]; sd = P["seed"]; t = P["t"]; expr = P["expr"]; frente = P["olhos"] == "frente"
    lk = P["look"]
    # forma, olhos lado (x, y, rx, ry), olhos frente (x, y, r), boca (x, y, esc)
    if esp == "pombo":
        hx, hy, hrx, hry = 0, -108, 72, 70
        lado_ = (68, -116, 15, 26); fre = (27, -124, 24); bc = None
    elif esp == "galinha":
        hx, hy, hrx, hry = 0, -102, 68, 68
        lado_ = (64, -110, 15, 25); fre = (26, -118, 23); bc = None
    elif esp == "gato":
        hx, hy, hrx, hry = 0, -86, 120, 98
        lado_ = (112, -98, 18, 30); fre = (44, -102, 32); bc = (0, -36, 0.9)
    elif esp == "vaca":
        hx, hy, hrx, hry = 0, -78, 102, 92
        lado_ = (98, -100, 17, 28); fre = (38, -102, 28); bc = (0, 26, 1.0)
    elif esp == "cavalo":
        hx, hy, hrx, hry = 0, -92, 70, 112
        lado_ = (66, -122, 15, 26); fre = (28, -126, 24); bc = (0, 22, 0.9)
    else:  # coelho
        hx, hy, hrx, hry = 0, -44, 94, 82
        lado_ = (90, -56, 16, 27); fre = (34, -62, 28); bc = (0, 8, 0.8)
    # orelhas/chifres atrás
    o = P["orelha"]
    if esp == "gato":
        for lado in (-1, 1):
            ctx.save(); ctx.translate(lado * 78, hy - 52); ctx.rotate(lado * 0.18 + (o if lado > 0 else 0))
            F(ctx, [(-34, 26), (lado * 6, -68), (34, 26), (0, 32)], S["cor"], sd + 60 + lado)
            F(ctx, [(-18, 18), (lado * 4, -44), (18, 18)], S["nariz"], sd + 62 + lado, lw=0)
            ctx.restore()
    elif esp == "coelho":
        for lado in (-1, 1):
            ctx.save(); ctx.translate(lado * 38, hy - 62); ctx.rotate(lado * 0.14 + (o * 2 if lado < 0 else 0))
            F(ctx, EL(0, -78, 27, 80, 20), S["cor"], sd + 60 + lado, sb=0.12)
            F(ctx, EL(0, -74, 13, 60, 16), S["interno"], sd + 62 + lado, lw=0)
            ctx.restore()
    elif esp == "vaca":
        for lado in (-1, 1):
            F(ctx, [(lado * 42, hy - 70), (lado * 62, hy - 118), (lado * 72, hy - 104), (lado * 66, hy - 62)], S["chifre"], sd + 64 + lado)
            ctx.save(); ctx.translate(lado * 100, hy - 30); ctx.rotate(lado * (0.25 + o))
            F(ctx, EL(lado * 38, 0, 44, 20, 16), S["cor"], sd + 66 + lado)
            F(ctx, EL(lado * 40, 0, 26, 10, 12), S["cor2"], sd + 68 + lado, lw=0)
            ctx.restore()
    elif esp == "cavalo":
        for lado in (-1, 1):
            ctx.save(); ctx.translate(lado * 40, hy - 100); ctx.rotate(lado * 0.2 + (o if lado > 0 else 0))
            F(ctx, [(-16, 20), (lado * 4, -42), (16, 20)], S["cor"], sd + 60 + lado)
            ctx.restore()
    # cabeça
    hp = EL(hx, hy, hrx, hry, 26)
    F(ctx, hp, S["cor"], sd + 70, sombra=True, sb=0.12)
    if esp == "vaca":
        manchas(ctx, hp, sd + 70, [(-62, hy - 40, 48, 42, 0.3)], S["mancha"])
        F(ctx, EL(0, hy + 70, 84, 46, 22), S["cor2"], sd + 72, sb=0.1)
        for lado in (-1, 1):
            F(ctx, EL(lado * 32, hy + 64, 10, 13, 10), escurece(S["cor2"], 0.5), sd + 74 + lado, lw=0)
        traco(ctx, [(-20, hy - 92), (-6, hy - 104), (8, hy - 92), (20, hy - 102)], lw=6, seed=sd + 76)
    elif esp == "cavalo":
        F(ctx, EL(0, hy - 8, 14, 52, 12), BRANCO, sd + 71, lw=0)
        F(ctx, EL(0, hy + 82, 62, 44, 22), S["cor2"], sd + 72, sb=0.1)
        for lado in (-1, 1):
            F(ctx, EL(lado * 26, hy + 84, 9, 12, 10), escurece(S["cor2"], 0.55), sd + 74 + lado, lw=0)
        for i in range(4):   # topete da crina
            F(ctx, EL(-24 + i * 16, hy - 104 + abs(i - 1.5) * 4, 14, 26, 10, -0.3 + i * 0.2 + 0.05 * math.sin(t * 3 + i)), S["crina"], sd + 77 + i, lw=4)
    elif esp == "gato":
        for i, dx in enumerate((-22, 0, 22)):
            traco(ctx, [(dx, hy - 92), (dx * 0.8, hy - 70)], lw=9, cor=S["listra"], seed=sd + 72 + i)
        for lado in (-1, 1):
            F(ctx, EL(lado * 24, hy + 46, 30, 24, 16), S["cor2"], sd + 76 + lado, lw=0)
    elif esp == "coelho":
        for lado in (-1, 1):
            F(ctx, EL(lado * 22, hy + 42, 28, 22, 16), S["cor2"], sd + 76 + lado, lw=0)
    elif esp == "galinha":
        for i, (x, r) in enumerate(((-22, 20), (0, 25), (22, 20))):
            F(ctx, EL(x, hy - 66 - r * 0.4, r * 0.8, r, 12), S["crista"], sd + 78 + i)
    # olhos
    olhos_sob = []
    if frente:
        ex, ey, er = fre
        for lado in (-1, 1):
            lid = P["lid"] + (0.1 if (expr == "desconfiado" and lado < 0) else 0)
            olho(ctx, lado * ex, ey, er, er * 1.1, lk, clamp(lid), S["cor"], sd + 80 + lado,
                 pupila=P["pupila"] if expr == "assustado" else 0.5, iris=S.get("iris"), anel=S.get("anel"), feliz=P["feliz"])
            olhos_sob.append((lado * ex, ey, er, er * 1.1, lado))
        sobrancelhas(ctx, olhos_sob, expr, sd)
    else:
        ex, ey, erx, ery = lado_
        for lado in (-1, 1):
            if P["olhar"] in ("camera", "frente"):
                look = (-lado * 0.75, 0)
            else:
                look = lk
            olho(ctx, lado * ex, ey, erx, ery, look, P["lid"], S["cor"], sd + 80 + lado, pupila=P["pupila"],
                 anel=S.get("anel"), rot=lado * 0.12, feliz=P["feliz"])
    # bico / focinho / boca
    if esp in AVES:
        yb = hy + 20
        abre = 8 if expr in ("assustado", "feliz") else 0
        if esp == "pombo":
            F(ctx, EL(0, yb - 16, 12, 7, 10), S["cere"], sd + 90, lw=3.5)
        F(ctx, [(-15, yb - 8), (15, yb - 8), (0, yb + 30 - abre)], S["bico"], sd + 91, lw=4.5)
        if abre:
            F(ctx, [(-10, yb + 2), (10, yb + 2), (0, yb + 30)], escurece(S["bico"], 0.25), sd + 92, lw=4)
        if esp == "galinha":
            for lado in (-1, 1):
                F(ctx, EL(lado * 9, yb + 40, 9, 15, 10), S["crista"], sd + 93 + lado, lw=4)
    elif esp in ("gato", "coelho"):
        ny = hy + 30
        F(ctx, [(-12, ny - 7), (12, ny - 7), (0, ny + 6)], S["nariz"], sd + 90, lw=4)
        bx, by_, be = bc
        traco(ctx, [(0, ny + 6), (0, ny + 16)], lw=4, seed=sd + 91)
        if expr == "neutro":
            traco(ctx, [(-18, ny + 18), (-8, ny + 24), (0, ny + 16), (8, ny + 24), (18, ny + 18)], lw=5, seed=sd + 92)
        else:
            boca(ctx, expr, 0, ny + 24, be, sd + 92)
        if esp == "coelho" and expr in ("feliz", "assustado", "neutro"):
            F(ctx, [(-9, ny + 26), (9, ny + 26), (9, ny + 44), (-9, ny + 44)], (1, 1, 1), sd + 95, lw=3.5)
            traco(ctx, [(0, ny + 26), (0, ny + 44)], lw=2.5, seed=sd + 96)
        for lado in (-1, 1):   # bigodes
            for j in range(3):
                traco(ctx, [(lado * 46, ny + 4 + j * 9), (lado * (110 + j * 6), ny - 12 + j * 16)], lw=3, seed=sd + 100 + j + lado * 5, alpha=0.85)
    else:
        bx, by_, be = bc
        boca(ctx, expr, bx, hy + by_ + 80, be, sd + 92)
    return (hx - hrx, hy - hry, hx + hrx, hy + hry)


# ============================ VISTA DE PERFIL (olhando para a direita) ============================
def _perfil(ctx, S, P):
    esp = S["nome"]; sd = P["seed"]; t = P["t"]; ag = P["agach"]
    ctx.translate(P["treme"], P["voo_dy"])
    ave = esp in AVES
    # ---------- geometria
    G = {
        "pombo":   dict(b=(-10, 52, 132, 88, -0.12), h=(88, -86, 58, 56), pesco=(52, -20)),
        "galinha": dict(b=(-14, 52, 140, 104, -0.08), h=(96, -92, 56, 56), pesco=(58, -24)),
        "gato":    dict(b=(-30, 52, 150, 78, 0.0), h=(132, -46, 84, 74), pesco=(90, 0), pernas=(-125, -90, 62, 98), py0=96),
        "vaca":    dict(b=(-36, 30, 176, 100, 0.0), h=(168, -70, 66, 62), pesco=(110, -10), pernas=(-150, -108, 62, 104), py0=100),
        "cavalo":  dict(b=(-34, 28, 160, 82, -0.04), h=(196, -126, 76, 42), pesco=(112, -30), pernas=(-145, -108, 70, 106), py0=80),
        "coelho":  dict(b=(-26, 92, 130, 100, -0.1), h=(98, -18, 80, 70), pesco=(60, 30)),
    }[esp]
    bx, by, brx, bry, brot = G["b"]
    by += ag * 34
    brot += -0.09 * ag if esp == "gato" else 0
    hx, hy, hrx, hry = G["h"]
    # pombo: cabeça vai para frente e volta ao andar; bicando: a cabeça gira para o chão
    hx += 22 * P["cabecada"] - (8 if esp == "pombo" and P["anda"] else 0)
    hy += ag * 30
    piv = G["pesco"]
    ang_bica = P["bica"] * (1.0 if ave else 0.75)
    cor_longe = escurece(S["cor"], 0.16)
    # ---------- atrás: pernas do outro lado, rabo
    if not ave:
        if "pernas" in G:
            pern = G["pernas"]; y0 = G["py0"] + ag * 30
            comp = 200 - y0 - ag * 10
        else:   # coelho: só a pata da frente do lado de lá
            F(ctx, EL(bx + 98 + _passo(P, 0, 10), 192, 30, 16, 12), escurece(S["cor2"], 0.12), sd + 119)
        for i in ((1, 2) if "pernas" in G else ()):   # pernas de trás e da frente do lado de lá
            x = pern[i] + 14
            sw = _passo(P, i * 1.7 + math.pi, 0.32)
            _perna_perfil(ctx, x, y0, comp, sw, cor_longe, S, sd + 120 + i, esp)
        _rabo_perfil(ctx, S, P, bx - brx, by, esp)
    else:
        _rabo_perfil(ctx, S, P, bx - brx, by, esp)
        if P["pose"] != "voando":
            for i, x in enumerate((-4, 26)):
                sw = _passo(P, i * math.pi, 0.4)
                ctx.save(); ctx.translate(x, 128 + ag * 10); ctx.rotate(sw)
                c = S["perna"] if i == 0 else escurece(S["perna"], 0.15)
                traco(ctx, [(0, 0), (0, 70 - ag * 14)], lw=9, cor=c, seed=sd + 130 + i)
                for d in (0, 1):
                    traco(ctx, [(0, 70 - ag * 14), (22 - d * 34, 76 - ag * 14)], lw=7, cor=c, seed=sd + 132 + d)
                ctx.restore()
    # ---------- corpo
    bp = EL(bx, by, brx, bry, 28, brot)
    F(ctx, bp, S["cor"], sd + 140, sombra=True, sb=0.14)
    if esp == "vaca":
        manchas(ctx, bp, sd + 140, [(-90, by - 30, 52, 40, 0.3), (40, by + 30, 46, 34, -0.4), (110, by - 60, 30, 26, 0)], S["mancha"])
    if esp in ("gato", "coelho"):
        F(ctx, EL(bx + brx * 0.45, by + bry * 0.35, brx * 0.42, bry * 0.5, 18, 0.3), S["cor2"], sd + 141, lw=0)
    if esp == "gato":
        for i in range(3):
            traco(ctx, [(bx - 60 + i * 40, by - bry + 6), (bx - 50 + i * 40, by - bry + 36)], lw=10, cor=S["listra"], seed=sd + 142 + i)
    if esp == "coelho":
        F(ctx, EL(bx - 60 + _passo(P, 1, 10), 190 + ag * 4, 76, 22, 18), S["cor2"], sd + 143)
        F(ctx, EL(bx + 112 + _passo(P, 2, 10), 194, 32, 16, 12), S["cor2"], sd + 148)
        F(ctx, EL(bx - brx + 12, by - 10, 30, 28, 14), BRANCO, sd + 144)
    if ave:
        F(ctx, EL(bx + 60, by + 20, 60, 50, 16), S["cor2"], sd + 145, lw=0)
        if P["pose"] == "voando":
            ctx.save(); ctx.translate(bx - 10, by - 40); ctx.rotate(-0.4 - 0.9 * P["asa"])
            F(ctx, EL(-70, 0, 120, 44, 18, 0.0), S["asa"], sd + 146, sb=0.2)
            for j in range(3):
                traco(ctx, [(-120 - j * 24, -14), (-160 - j * 18, 26)], lw=5, seed=sd + 147 + j)
            ctx.restore()
        else:
            F(ctx, EL(bx - 30, by - 4, 98, 52, 20, -0.12), S["asa"], sd + 146, sb=0.18)
            if esp == "pombo":
                for j in range(2):
                    traco(ctx, [(bx - 70 + j * 34, by - 14), (bx - 56 + j * 34, by + 30)], lw=8, seed=sd + 147 + j)
    # pernas do lado de cá (mamíferos)
    if not ave and "pernas" in G:
        pern = G["pernas"]; y0 = G["py0"] + ag * 30
        comp = 200 - y0 - ag * 10
        for i in (0, 3):
            sw = _passo(P, i * 1.7, 0.32)
            _perna_perfil(ctx, pern[i], y0, comp, sw, S["cor"], S, sd + 124 + i, esp)
    # ---------- pescoço + cabeça (giram juntos quando bica)
    ctx.save(); ctx.translate(*piv); ctx.rotate(ang_bica * 0.9); ctx.translate(-piv[0], -piv[1])
    if esp in ("vaca", "cavalo"):
        nk = EL((piv[0] + hx) / 2 - 6, (piv[1] + hy) / 2 + 8, 52 if esp == "vaca" else 44, math.hypot(hx - piv[0], hy - piv[1]) / 2 + 30, 20,
                math.atan2(hy - piv[1], hx - piv[0]) - math.pi / 2)
        F(ctx, nk, S["cor"], sd + 150, sb=0.1)
        if esp == "cavalo":
            for i in range(5):   # crina ao longo do pescoço
                k = i / 4
                F(ctx, EL(piv[0] - 26 + (hx - 40 - piv[0]) * k, piv[1] - 34 + (hy - 30 - piv[1]) * k, 18, 30, 10,
                          -0.6 + 0.1 * math.sin(t * 3 + i)), S["crina"], sd + 151 + i, lw=4)
    elif ave:
        F(ctx, EL((piv[0] + hx) / 2, (piv[1] + hy) / 2 + 10, 46, 62, 18, 0.5), S["pesc"] if esp == "pombo" else S["cor"], sd + 150)
        if esp == "pombo":
            manchas(ctx, EL((piv[0] + hx) / 2, (piv[1] + hy) / 2 + 10, 46, 62, 18, 0.5), sd + 150,
                    [((piv[0] + hx) / 2 - 10, (piv[1] + hy) / 2 + 40, 60, 20, 0.4)], S["pesc2"])
    face = _cabeca_perfil(ctx, S, P, hx, hy, hrx, hry)
    ctx.restore()
    fx0, fy0, fx1, fy1 = face
    if ang_bica > 0.05:   # caixa do rosto acompanha a cabeça girando
        c, s = math.cos(ang_bica * 0.9), math.sin(ang_bica * 0.9)
        pts = [(piv[0] + (x - piv[0]) * c - (y - piv[1]) * s, piv[1] + (x - piv[0]) * s + (y - piv[1]) * c) for x, y in ((fx0, fy0), (fx1, fy0), (fx0, fy1), (fx1, fy1))]
        fx0, fy0 = min(p[0] for p in pts), min(p[1] for p in pts); fx1, fy1 = max(p[0] for p in pts), max(p[1] for p in pts)
    dy = P["voo_dy"]
    return {"corpo": (-240, min(fy0, -150) + dy, 270, 215 + dy), "rosto": (fx0, fy0 + dy, fx1, fy1 + dy)}


def _perna_perfil(ctx, x, y0, comp, sw, cor, S, seed, esp):
    ctx.save(); ctx.translate(x, y0); ctx.rotate(sw)
    w = {"gato": 28, "vaca": 38, "cavalo": 30}.get(esp, 30)
    tubo(ctx, [(0, 0), (0, comp - 10)], cor, w, seed)
    pata = S.get("casco")
    if pata:
        F(ctx, [(-w / 2 - 3, comp - 16), (w / 2 + 3, comp - 16), (w / 2 + 5, comp + 4), (-w / 2 - 5, comp + 4)], pata, seed + 3, lw=4.5)
    else:
        F(ctx, EL(6, comp - 4, w * 0.75, 12, 12), cor if cor != S["cor"] else S["cor2"], seed + 3, lw=4.5)
    ctx.restore()


def _rabo_perfil(ctx, S, P, x, y, esp):
    sd = P["seed"]; a = P["rabo"]; t = P["t"]
    if esp == "gato":
        if P["agach"]:
            tubo(ctx, [(x + 10, y - 10), (x - 70, y + 10), (x - 140, y + 4 + 40 * a)], S["cor"], 26, sd + 160)
        else:
            tubo(ctx, [(x + 10, y - 10), (x - 50, y - 30), (x - 70 + 30 * a, y - 110), (x - 40 + 60 * a, y - 160)], S["cor"], 26, sd + 160)
    elif esp == "vaca":
        traco(ctx, [(x + 8, y - 40), (x - 10 + 10 * a, y + 30), (x - 6 + 20 * a, y + 110)], lw=8, seed=sd + 160)
        F(ctx, EL(x - 6 + 20 * a, y + 124, 12, 20, 10), S["mancha"], sd + 161, lw=4)
    elif esp == "cavalo":
        for i in range(3):
            F(ctx, EL(x - 26 + 8 * a, y + 40 + i * 6, 22, 70, 14, 0.25 + 0.15 * a + i * 0.12), S["crina"], sd + 160 + i, lw=4.5)
    elif esp == "pombo":
        F(ctx, [(x + 30, y - 6), (x - 80, y + 18 + 8 * a), (x - 86, y + 50 + 8 * a), (x + 30, y + 40)], escurece(S["asa"], 0.15), sd + 160)
        traco(ctx, [(x - 60, y + 22 + 8 * a), (x - 64, y + 46 + 8 * a)], lw=9, seed=sd + 161)
    elif esp == "galinha":
        for i in range(3):
            F(ctx, EL(x + 10 - i * 8, y - 70 - i * 6, 22, 66, 14, -0.5 - i * 0.22 + 0.05 * math.sin(t * 2 + i)), escurece(S["cor"], 0.05 + i * 0.03), sd + 160 + i)


def _cabeca_perfil(ctx, S, P, hx, hy, hrx, hry):
    esp = S["nome"]; sd = P["seed"]; t = P["t"]; expr = P["expr"]; frente = P["olhos"] == "frente"; lk = P["look"]
    o = P["orelha"]
    # orelhas atrás da cabeça
    if esp == "gato":
        for i, dx in enumerate((-30, 10)):
            ctx.save(); ctx.translate(hx + dx, hy - hry + 14); ctx.rotate(-0.1 + (o if i else 0))
            F(ctx, [(-26, 18), (-4, -54), (26, 18)], escurece(S["cor"], 0.1 * (1 - i)), sd + 170 + i)
            if i:
                F(ctx, [(-12, 12), (-3, -32), (12, 12)], S["nariz"], sd + 172, lw=0)
            ctx.restore()
    elif esp == "coelho":
        for i, dx in enumerate((-28, -8)):
            ctx.save(); ctx.translate(hx + dx, hy - hry + 20); ctx.rotate(-0.45 + i * 0.12 + (o * 2 if i else 0))
            F(ctx, EL(0, -76, 26, 80, 20), escurece(S["cor"], 0.1 * (1 - i)), sd + 170 + i, sb=0.1)
            if i:
                F(ctx, EL(2, -72, 12, 60, 16), S["interno"], sd + 172, lw=0)
            ctx.restore()
    elif esp == "vaca":
        F(ctx, [(hx - 10, hy - hry + 10), (hx + 2, hy - hry - 36), (hx + 16, hy - hry - 30), (hx + 14, hy - hry + 12)], S["chifre"], sd + 170)
        ctx.save(); ctx.translate(hx - 40, hy - 30); ctx.rotate(-0.3 + o)
        F(ctx, EL(-34, 0, 40, 18, 16), S["cor"], sd + 171); F(ctx, EL(-36, 0, 24, 9, 12), S["cor2"], sd + 172, lw=0)
        ctx.restore()
    elif esp == "cavalo":
        ctx.save(); ctx.translate(hx - 40, hy - hry - 4); ctx.rotate(-0.25 + o)
        F(ctx, [(-14, 16), (0, -44), (16, 16)], S["cor"], sd + 170)
        ctx.restore()
    # cabeça
    if esp == "cavalo":
        hp = EL(hx, hy, hrx, hry, 26, 0.55)
    else:
        hp = EL(hx, hy, hrx, hry, 26)
    F(ctx, hp, S["cor"], sd + 175, sombra=True, sb=0.1)
    # focinho / bico (para a direita)
    if esp == "vaca":
        mx, my = hx + hrx * 0.82, hy + hry * 0.42
        manchas(ctx, hp, sd + 175, [(hx - 30, hy - 30, 36, 30, 0.2)], S["mancha"])
        F(ctx, EL(mx, my, 46, 40, 18), S["cor2"], sd + 176, sb=0.1)
        F(ctx, EL(mx + 22, my - 6, 8, 11, 10), escurece(S["cor2"], 0.5), sd + 177, lw=0)
        bxy = (mx + 4, my + 26, 0.8)
    elif esp == "cavalo":
        mx, my = hx + 58, hy + 40
        F(ctx, EL(mx, my, 40, 34, 18, 0.5), S["cor2"], sd + 176, sb=0.1)
        F(ctx, EL(mx + 16, my - 4, 7, 10, 10), escurece(S["cor2"], 0.55), sd + 177, lw=0)
        for i in range(3):
            F(ctx, EL(hx - 34 + i * 14, hy - hry - 2 + i * 4, 12, 24, 10, -0.7 + i * 0.2), S["crina"], sd + 178 + i, lw=4)
        bxy = (mx - 2, my + 24, 0.7)
    elif esp in ("gato", "coelho"):
        mx, my = hx + hrx * 0.78, hy + hry * 0.3
        F(ctx, EL(mx - 8, my + 6, 34, 26, 16), S["cor2"], sd + 176, lw=0)
        F(ctx, EL(mx + 18, my - 8, 10, 8, 10), S["nariz"], sd + 177, lw=3.5)
        for j in range(3):
            traco(ctx, [(mx, my + 2 + j * 8), (mx + 70 + j * 4, my - 12 + j * 14)], lw=3, seed=sd + 180 + j, alpha=0.85)
        bxy = (mx, my + 20, 0.6)
        if esp == "coelho":
            F(ctx, [(mx + 4, my + 18), (mx + 16, my + 18), (mx + 16, my + 34), (mx + 4, my + 34)], (1, 1, 1), sd + 183, lw=3)
    else:   # aves
        bxx = hx + hrx * 0.86; byy = hy + 4
        abre = 7 if expr in ("assustado", "feliz") else 0
        if esp == "pombo":
            F(ctx, EL(bxx + 6, byy - 8, 11, 7, 10), S["cere"], sd + 176, lw=3.5)
        F(ctx, [(bxx - 4, byy - 10), (bxx + 40, byy + 2 - abre * 0.3), (bxx - 4, byy + 6)], S["bico"], sd + 177, lw=4.5)
        if abre:
            F(ctx, [(bxx - 2, byy + 8), (bxx + 30, byy + 12 + abre), (bxx - 2, byy + 16)], escurece(S["bico"], 0.2), sd + 178, lw=4)
        if esp == "galinha":
            for i, (dx, r) in enumerate(((-26, 16), (-6, 21), (14, 17))):
                F(ctx, EL(hx + dx, hy - hry - r * 0.3, r * 0.75, r, 12), S["crista"], sd + 179 + i)
            F(ctx, EL(bxx + 4, byy + 30, 9, 16, 10), S["crista"], sd + 182, lw=4)
        bxy = None
    # olhos
    if frente:
        # os dois olhos na cara, virados para a câmera: o de cá inteiro, o de lá passando do contorno (3/4 de cartoon)
        r = {"pombo": 20, "galinha": 20, "gato": 26, "vaca": 24, "cavalo": 21, "coelho": 24}[esp]
        if esp == "cavalo":
            e1 = (hx + 4, hy - 20); e2 = (hx + 42, hy - 6)
        elif esp in AVES:
            e1 = (hx + hrx * 0.18, hy - hry * 0.28); e2 = (hx + hrx * 0.72, hy - hry * 0.3)
        else:
            e1 = (hx + hrx * 0.1, hy - hry * 0.3); e2 = (hx + hrx * 0.62, hy - hry * 0.32)
        look = lk if P["olhar"] not in ("camera", "frente") else (-0.35, 0.05)
        pup = P["pupila"] if expr == "assustado" else 0.5
        olho(ctx, e2[0], e2[1], r * 0.82, r * 1.06, look, clamp(P["lid"] + (0.1 if expr == "desconfiado" else 0)), S["cor"], sd + 190,
             pupila=pup, iris=S.get("iris"), anel=S.get("anel"), feliz=P["feliz"])
        olho(ctx, e1[0], e1[1], r, r * 1.1, look, P["lid"], S["cor"], sd + 191, pupila=pup, iris=S.get("iris"), anel=S.get("anel"), feliz=P["feliz"])
        sobrancelhas(ctx, [(e1[0], e1[1], r, r * 1.1, -1), (e2[0], e2[1], r * 0.82, r * 1.06, 1)], expr, sd + 3)
    else:
        if esp == "cavalo":
            ex, ey = hx - 22, hy - 18
        elif esp in AVES:
            ex, ey = hx + 4, hy - 10
        else:
            ex, ey = hx - hrx * 0.05, hy - hry * 0.25
        r = {"pombo": 16, "galinha": 15, "vaca": 19, "cavalo": 17, "coelho": 20, "gato": 22}[esp]
        look = lk if P["olhar"] not in ("camera", "frente") else (0.55, 0)
        olho(ctx, ex, ey, r, r * 1.08, look, P["lid"], S["cor"], sd + 191, pupila=P["pupila"] if expr == "assustado" else 0.5,
             anel=S.get("anel"), feliz=P["feliz"])
    if bxy:
        boca(ctx, expr, bxy[0], bxy[1], bxy[2], sd + 195)
    ext = 1.25 if esp != "cavalo" else 1.0
    x1 = hx + hrx * ext + (40 if esp in AVES else 10)
    return (hx - hrx, hy - hry - (30 if frente else 0), x1, hy + hry + (24 if esp == "cavalo" else 0))


# ============================ VISTA DE CIMA (cabeça para cima) ============================
CIMA = {   # corpo (cy, rx, ry), cabeça (cy, rx, ry)
    "pombo":   ((62, 92, 132), (-112, 54, 54)),
    "galinha": ((62, 104, 132), (-110, 54, 56)),
    "gato":    ((64, 84, 138), (-122, 80, 70)),
    "vaca":    ((70, 118, 150), (-132, 64, 66)),
    "cavalo":  ((80, 98, 150), (-140, 50, 78)),
    "coelho":  ((60, 106, 118), (-94, 72, 64)),
}


_CONE = {}


def _cone_surf(campo, cego, R):
    """Cone e zona cega desenhados uma vez em 1/4 da resolução (cache por campo/cego/alcance)."""
    k = (round(campo * 2) / 2, bool(cego), int(R))
    if k in _CONE:
        return _CONE[k]
    if len(_CONE) > 400:
        _CONE.clear()
    q = 4.0; n = int(2 * R / q) + 4
    sf = cairo.ImageSurface(cairo.FORMAT_ARGB32, n, n); c = cairo.Context(sf)
    c.translate(n / 2, n / 2); c.scale(1 / q, 1 / q)
    meio = -math.pi / 2; m = math.radians(campo) / 2
    if cego and campo < 359.5:
        g = cairo.RadialGradient(0, 0, 20, 0, 0, R)
        g.add_color_stop_rgba(0, 0.95, 0.12, 0.12, 0.62); g.add_color_stop_rgba(1, 0.95, 0.12, 0.12, 0.34)
        c.move_to(0, 0); c.arc(0, 0, R, meio + m, meio - m + 2 * math.pi); c.close_path()
        c.set_source(g); c.fill_preserve()
        c.set_source_rgba(0.75, 0.05, 0.08, 0.75); c.set_line_width(4 * q / 2); c.stroke()
    if campo > 0.5:
        g = cairo.RadialGradient(0, 0, 20, 0, 0, R)
        g.add_color_stop_rgba(0, 1.0, 0.96, 0.62, 0.62); g.add_color_stop_rgba(0.7, 1.0, 0.96, 0.62, 0.3); g.add_color_stop_rgba(1, 1.0, 0.96, 0.62, 0.06)
        if campo >= 359.5:
            c.arc(0, 0, R, 0, 2 * math.pi)
        else:
            c.move_to(0, 0); c.arc(0, 0, R, meio - m, meio + m); c.close_path()
        c.set_source(g); c.fill()
    sf.flush()
    _CONE[k] = (sf, q, n)
    return _CONE[k]


def cone(ctx, ax, ay, campo, alcance, cego, t):
    """Campo de visão saindo dos olhos (para cima = para frente) e, com cego, a zona cega atrás em vermelho."""
    campo = clamp(float(campo), 0, 360)
    meio = -math.pi / 2; m = math.radians(campo) / 2
    pul = 1 + 0.025 * math.sin(t * 3)
    R = alcance * pul
    sf, q, n = _cone_surf(campo, cego, alcance)
    ctx.save(); ctx.translate(ax, ay); ctx.scale(q * pul, q * pul); ctx.translate(-n / 2, -n / 2)
    ctx.set_source_surface(sf, 0, 0); ctx.get_source().set_filter(cairo.FILTER_BILINEAR); ctx.paint(); ctx.restore()
    if 0.5 < campo < 359.5:   # bordas do cone tracejadas
        ctx.save(); ctx.set_dash([18, 14], (t * 40) % 32); ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.85)
        for a in (meio - m, meio + m):
            ctx.move_to(ax + math.cos(a) * 60, ay + math.sin(a) * 60); ctx.line_to(ax + math.cos(a) * R * 0.96, ay + math.sin(a) * R * 0.96)
        ctx.stroke(); ctx.restore()


def _cima(ctx, S, P, st):
    esp = S["nome"]; sd = P["seed"]; t = P["t"]; expr = P["expr"]; frente = P["olhos"] == "frente"; lk = P["look"]
    ave = esp in AVES
    (by, brx, bry), (hy, hrx, hry) = CIMA[esp]
    ag = P["agach"]
    brx *= 1 + 0.08 * ag
    hy += -26 * P["bica"] - 16 * P["cabecada"]
    ctx.translate(P["treme"], 0)
    o = P["orelha"]
    if "campo" in st:
        cone(ctx, 0, hy, st["campo"], st.get("alcance", 620), st.get("cego"), t)
    # sombra no chão quando voa
    if P["pose"] == "voando":
        ctx.save(); ctx.translate(26, 40); ctx.scale(1, 1)
        path_suave(ctx, EL(0, by - 40, brx * 0.9, bry * 1.1, 20)); ctx.set_source_rgba(*INK, 0.18); ctx.fill(); ctx.restore()
    # pés/patas aparecendo
    if not ave:
        for i, (sx, yy) in enumerate(((-1, by - bry * 0.55), (1, by - bry * 0.55), (-1, by + bry * 0.6), (1, by + bry * 0.6))):
            dy = _passo(P, i * 1.7 + (math.pi if i in (1, 2) else 0), 16)
            pata = S.get("casco") or S["cor2"]
            F(ctx, EL(sx * (brx + 6), yy + dy, 18, 24, 12), pata, sd + 200 + i)
    elif P["pose"] != "voando":
        for i, sx in enumerate((-1, 1)):
            dy = _passo(P, i * math.pi, 16)
            F(ctx, [(sx * 40, by + 10 + dy), (sx * 62, by - 20 + dy), (sx * 70, by + 4 + dy)], S["perna"], sd + 200 + i, lw=4)
    # rabo
    a = P["rabo"]
    if esp == "gato":
        tubo(ctx, [(0, by + bry - 10), (20 * a, by + bry + 60), (60 + 60 * a, by + bry + 110), (120 + 40 * a, by + bry + 90)], S["cor"], 26, sd + 210)
    elif esp == "vaca":
        traco(ctx, [(0, by + bry - 6), (20 * a, by + bry + 40), (30 * a, by + bry + 80)], lw=8, seed=sd + 210)
        F(ctx, EL(30 * a, by + bry + 92, 14, 18, 10), S["mancha"], sd + 211, lw=4)
    elif esp == "cavalo":
        for i in range(3):
            F(ctx, EL(-14 + i * 14 + 16 * a, by + bry + 50, 18, 68, 14, (i - 1) * 0.18 + 0.2 * a), S["crina"], sd + 210 + i, lw=4.5)
    elif esp == "coelho":
        pass
    elif ave:
        cor_r = escurece(S["asa"], 0.15)
        F(ctx, [(-34, by + bry - 30), (-54 - 6 * a, by + bry + 70), (54 - 6 * a, by + bry + 70), (34, by + bry - 30)], cor_r, sd + 210)
        if esp == "pombo":
            traco(ctx, [(-44, by + bry + 50), (44, by + bry + 50)], lw=10, seed=sd + 211)
    # asas abertas (voando) atrás do corpo
    if ave and P["pose"] == "voando":
        k = 0.35 + 0.65 * abs(P["asa"])
        for sx in (-1, 1):
            ctx.save(); ctx.translate(sx * 50, by - 30); ctx.scale(k, 1)
            F(ctx, EL(sx * 150, 0, 150, 52, 20, sx * 0.12), S["asa"], sd + 215 + sx, sb=0.2)
            for j in range(3):
                traco(ctx, [(sx * (190 + j * 34), -30), (sx * (210 + j * 30), 36)], lw=5, seed=sd + 218 + j)
            ctx.restore()
    # corpo
    bp = EL(0, by, brx, bry, 28)
    F(ctx, bp, S["cor"], sd + 220, sombra=True, sb=0.14)
    if esp == "vaca":
        manchas(ctx, bp, sd + 220, [(-60, by - 60, 50, 40, 0.3), (50, by + 40, 54, 36, -0.4), (-30, by + 100, 30, 24, 0.2)], S["mancha"])
    elif esp == "gato":
        for i in range(4):
            yy = by - 80 + i * 46
            traco(ctx, [(-brx * 0.55, yy), (0, yy + 10), (brx * 0.55, yy)], lw=11, cor=S["listra"], seed=sd + 221 + i)
    elif esp == "cavalo":
        F(ctx, EL(0, by - 10, 14, bry * 0.75, 14), S["crina"], sd + 221, lw=4)
    elif esp == "coelho":
        F(ctx, EL(0, by + bry - 8, 28, 26, 14), BRANCO, sd + 222)
    if ave and P["pose"] != "voando":
        for sx in (-1, 1):
            F(ctx, EL(sx * brx * 0.62, by + 14, brx * 0.48, bry * 0.86, 20, sx * 0.08), S["asa"], sd + 225 + sx, sb=0.18)
            if esp == "pombo":
                for j in range(2):
                    traco(ctx, [(sx * brx * 0.35, by + 10 + j * 36), (sx * brx * 0.95, by + 22 + j * 36)], lw=8, seed=sd + 227 + j)
    if esp == "pombo":
        F(ctx, EL(0, hy + hry + 6, hrx * 1.1, 32, 18), S["pesc"], sd + 229)
    # orelhas que ficam atrás da cabeça
    if esp == "coelho":
        for sx in (-1, 1):
            ctx.save(); ctx.translate(sx * 26, hy + 30); ctx.rotate(sx * 0.12 + (o * 2 if sx < 0 else 0))
            F(ctx, EL(0, 60, 24, 72, 18), S["cor"], sd + 230 + sx, sb=0.1); F(ctx, EL(0, 60, 11, 52, 14), S["interno"], sd + 232 + sx, lw=0)
            ctx.restore()
    elif esp == "vaca":
        for sx in (-1, 1):
            F(ctx, EL(sx * (hrx + 30), hy + 12, 38, 18, 14, sx * (0.2 + o)), S["cor"], sd + 230 + sx)
            F(ctx, [(sx * 26, hy - 30), (sx * 56, hy - 70), (sx * 64, hy - 56), (sx * 40, hy - 18)], S["chifre"], sd + 234 + sx)
    # cabeça
    hp = EL(0, hy, hrx, hry, 26)
    F(ctx, hp, S["cor"], sd + 240, sombra=True, sb=0.1)
    if esp == "gato":
        for sx in (-1, 1):
            ctx.save(); ctx.translate(sx * 52, hy - 44); ctx.rotate(sx * 0.35 + (o if sx > 0 else 0))
            F(ctx, [(-24, 20), (0, -40), (24, 20)], S["cor"], sd + 242 + sx); F(ctx, [(-11, 14), (0, -22), (11, 14)], S["nariz"], sd + 244 + sx, lw=0)
            ctx.restore()
        for i, dx in enumerate((-18, 0, 18)):
            traco(ctx, [(dx, hy - 10), (dx, hy + 26)], lw=8, cor=S["listra"], seed=sd + 246 + i)
    elif esp == "cavalo":
        F(ctx, EL(0, hy - hry + 20, 36, 30, 16), S["cor2"], sd + 242, sb=0.1)
        for sx in (-1, 1):
            F(ctx, [(sx * 14, hy + 40), (sx * 30, hy + 10), (sx * 40, hy + 46)], S["cor"], sd + 244 + sx)
        F(ctx, EL(0, hy + 50, 12, 26, 10), S["crina"], sd + 246, lw=4)
    elif esp == "vaca":
        F(ctx, EL(0, hy - hry + 10, 50, 30, 18), S["cor2"], sd + 242, sb=0.1)
        manchas(ctx, hp, sd + 240, [(30, hy + 20, 30, 26, 0.3)], S["mancha"])
    elif esp == "coelho":
        F(ctx, EL(0, hy - hry + 8, 12, 9, 10), S["nariz"], sd + 242, lw=3.5)
    elif ave:
        F(ctx, [(-14, hy - hry + 10), (0, hy - hry - 34), (14, hy - hry + 10)], S["bico"], sd + 242, lw=4.5)
        if esp == "galinha":
            for i in range(3):
                F(ctx, EL(0, hy - 30 + i * 22, 13, 14, 10), S["crista"], sd + 243 + i, lw=4)
        elif esp == "pombo":
            F(ctx, EL(0, hy - hry + 6, 10, 7, 10), S["cere"], sd + 243, lw=3)
    # olhos
    if frente:
        r = {"pombo": 17, "galinha": 17, "gato": 22, "vaca": 20, "cavalo": 18, "coelho": 20}[esp]
        ey = hy - hry * 0.42
        ex = hrx * 0.42 if esp != "cavalo" else hrx * 0.5
        oss = []
        for sx in (-1, 1):
            olho(ctx, sx * ex, ey, r, r * 1.05, lk, P["lid"], S["cor"], sd + 250 + sx, pupila=P["pupila"] if expr == "assustado" else 0.5,
                 iris=S.get("iris"), anel=S.get("anel"), feliz=P["feliz"])
            oss.append((sx * ex, ey, r, r * 1.05, sx))
        sobrancelhas(ctx, oss, expr, sd + 7)
    else:
        r = {"pombo": 14, "galinha": 14, "gato": 16, "vaca": 15, "cavalo": 14, "coelho": 16}[esp]
        ey = hy - hry * 0.1 if esp != "cavalo" else hy - hry * 0.25
        for sx in (-1, 1):
            look = (sx * 0.8, 0) if P["olhar"] in ("camera", "frente") else lk
            olho(ctx, sx * (hrx - r * 0.25), ey, r * 0.62, r * 1.15, look, P["lid"], S["cor"], sd + 250 + sx, pupila=P["pupila"],
                 anel=S.get("anel"), rot=0, feliz=P["feliz"])
    topo = hy - hry - (40 if ave else 30)
    return {"corpo": (-brx - 30, topo, brx + 30, by + bry + (110 if esp in ("gato", "cavalo", "vaca") else 70)),
            "rosto": (-hrx, hy - hry, hrx, hy + hry)}


# ============================ entrada ============================
def desenha_bicho(ctx, st, t, pal, seed):
    S, P = _anim(st, t, seed)
    vista = st.get("vista", "frente")
    ctx.save()
    if S["nome"] in DINOS:
        bx = _dino(ctx, S, P, st, vista)
    elif vista == "cima":
        bx = _cima(ctx, S, P, st)
    elif vista == "perfil":
        bx = _perfil(ctx, S, P)
    elif vista == "frente":
        bx = _frente(ctx, S, P)
    else:
        ctx.restore()
        raise SystemExit(f"bicho: vista '{vista}' não existe. Use frente, perfil ou cima")
    ctx.restore()
    return bx


# ============================ DINOSSAUROS (ep015) ============================
# tiranossauro: bípede, cabeção, bracinhos, cauda; olhos SEMPRE "frente". Extras: abre (0 a 1, boca), ombros (0 a 1, dá de ombros),
#   pose "rugindo" (boca aberta tremendo) e "ombros" (dá de ombros sozinho); silhueta: true (sombra escura com olhos acesos);
#   vistas: frente, perfil, cima (2 cones que cruzam num alvo: campo = abertura de cada cone, alcance = distância do alvo), cranio (com lupa), pegada.
# bicodepato (hadrossauro): quadrúpede/semi, bico largo de pato, crista (crista: false tira); aceita olhos "lado" (real) e "frente" (regra);
#   vistas: frente, perfil (pose bicando = come samambaia), cima (cone: campo, cego). suor: true (gota de nervoso).
# Design próprio (nada de filme/desenho conhecido).
DINOS = ("tiranossauro", "bicodepato")
ESPECIES["tiranossauro"] = dict(cor="#D8583E", cor2="#F7DDA8", listra="#8E2F2A", espinho="#FFC21A", garra="#FFF1D0", interior="#7A1B33",
                                lingua="#F07B9C", campo=70, dino=True)
ESPECIES["bicodepato"] = dict(cor="#8A7BE0", cor2="#E9E2FF", listra="#5B4BB0", bico="#F5B73A", bico2="#FFD36B", crista="#FF8FA8",
                              mao="#6B5CC4", campo=300, dino=True)
_SIL = "#1B1330"


def _dino_cores(S, st):
    if st.get("silhueta"):
        for k, v in list(S.items()):
            if isinstance(v, tuple) and len(v) == 3 and k not in ("espinho",):
                S[k] = hexc(_SIL)
        S["espinho"] = hexc("#2A1F45")


def _samambaia(ctx, x, y, s, t, seed, cor="#2E9E4A"):
    """Moita de samambaia (folhas em leque com folíolos) balançando; base em (x, y)."""
    c = hexc(cor); c2 = escurece(c, 0.25)
    for i, ang in enumerate((-1.0, -0.5, 0.0, 0.5, 1.0)):
        a = ang + 0.08 * math.sin(t * 2.2 + i + seed)
        L = (150 - abs(ang) * 36) * s
        pts = [(x, y)]
        for k in range(1, 6):
            u = k / 5
            pts.append((x + math.sin(a) * L * u + 0.35 * math.sin(a) * L * u * u * (1 if ang >= 0 else -1) * 0.4, y - math.cos(a) * L * u))
        traco(ctx, pts, lw=7 * s, cor=c2, seed=seed + i, amp=0.6)
        for k in range(1, 6):
            px, py = pts[k]
            for sg in (-1, 1):
                traco(ctx, [(px, py), (px + sg * 26 * s * (1 - k * 0.12) * math.cos(a), py - 8 * s)], lw=7 * s, cor=c, seed=seed + 7 + k, amp=0.5)


def _garras(ctx, x, y, n, dx, s, cor, seed):
    for i in range(n):
        xx = x + (i - (n - 1) / 2) * dx
        F(ctx, [(xx - 5 * s, y), (xx, y + 14 * s), (xx + 5 * s, y)], cor, seed + i, lw=3.5, amp=0.3)


def _dentes(ctx, x0, x1, y, n, h, sd, baixo=True, w=9):
    for i in range(n):
        xx = x0 + (x1 - x0) * (i + 0.5) / n
        F(ctx, [(xx - w / 2, y), (xx + w / 2, y), (xx, y + (h if baixo else -h))], BRANCO, sd + i, lw=3, amp=0.2)


# -------------------------- tiranossauro
def _trex_frente(ctx, S, P, st):
    sd = P["seed"]; t = P["t"]; expr = P["expr"]
    ab = P["abre"]; om = P["omb"]
    cor, cor2, lis = S["cor"], S["cor2"], S["listra"]
    bob = 3 * math.sin(t * 2.2)
    ctx.translate(P["treme"], 0)
    a = P["rabo"]
    tubo(ctx, [(60, 178), (150, 188 + 6 * a), (200, 170), (212, 138 + 10 * a)], cor, 34, sd + 1)
    for i, lado in enumerate((-1, 1)):
        lift = max(0, _passo(P, i * math.pi, 14))
        x = lado * 54
        tubo(ctx, [(x, 108), (x + lado * 6, 188 - lift)], cor, 56, sd + 30 + i)
        F(ctx, EL(x + lado * 16, 197 - lift, 46, 17, 14), cor, sd + 32 + i)
        _garras(ctx, x + lado * 16 + 4, 204 - lift, 3, 24, 1.0, S["garra"], sd + 34 + i)
    F(ctx, EL(0, 66, 116, 126, 28), cor, sd + 40, sombra=True, sb=0.16)
    F(ctx, EL(0, 94, 64, 94, 18), cor2, sd + 41, lw=0)
    for i in range(3):
        traco(ctx, [(-44, 66 + i * 36), (0, 74 + i * 36), (44, 66 + i * 36)], lw=5, cor=escurece(cor2, 0.25), seed=sd + 42 + i, alpha=0.8)
    # bracinhos (dar de ombros: sobem e abrem as mãos para os lados)
    for i, lado in enumerate((-1, 1)):
        sx, sy = lado * 84, 44
        ex, ey = lado * (110 + om * 28), 74 - om * 28
        hx, hy = lado * (96 + om * 52), 104 - om * 74
        tubo(ctx, [(sx, sy), (ex, ey), (hx, hy)], cor, 22, sd + 50 + i)
        F(ctx, EL(hx, hy, 15, 13, 10), cor, sd + 52 + i, lw=4)
        _garras(ctx, hx, hy + 6, 2, 11, 0.8, S["garra"], sd + 54 + i)
    # cabeça (cabeção)
    ctx.save()
    ctx.translate(0, bob - om * 8 + (math.sin(t * 38) * 4 if ab > 0.5 else 0)); ctx.rotate(om * 0.07 * math.sin(t * 5) + (0.02 * math.sin(t * 40) if ab > 0.5 else 0))
    for i, x in enumerate((-30, 0, 30)):
        F(ctx, [(x - 11, -176 + abs(x) * 0.35), (x, -208 + abs(x) * 0.5), (x + 11, -176 + abs(x) * 0.35)], S["espinho"], sd + 60 + i, lw=4.5, amp=0.4)
    F(ctx, EL(0, -102, 110, 94, 30), cor, sd + 61, sombra=True, sb=0.14)
    F(ctx, EL(0, -62, 82, 46, 22), cor2, sd + 62, lw=0)
    for lado in (-1, 1):   # bochecha
        F(ctx, EL(lado * 92, -78, 18, 14, 10), escurece(cor, 0.12), sd + 63 + lado, lw=0)
    # boca: fechada (sorrisinho com 2 dentes) ou aberta (rugido)
    if ab > 0.05:
        F(ctx, EL(0, -56 + 10 * ab, 70, 8 + 34 * ab, 22), S["interior"], sd + 66, lw=5)
        F(ctx, EL(0, -44 + 14 * ab, 34, 8 + 16 * ab, 14), S["lingua"], sd + 67, lw=0)
        _dentes(ctx, -60, 60, -56 - 0.0, 7, 15, sd + 68, baixo=True)
        _dentes(ctx, -52, 52, -56 + 20 * ab + 10, 5, 12, sd + 80, baixo=False)
    else:
        boca(ctx, expr, 0, -54, 2.5, sd + 66)
        for lado in (-1, 1):
            F(ctx, [(lado * 48 - 6, -60), (lado * 48 + 6, -60), (lado * 48, -45)], BRANCO, sd + 70 + lado, lw=3, amp=0.2)
    for lado in (-1, 1):   # narinas
        ctx.arc(lado * 16, -84, 4.5, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    # olhos juntos na frente + sobrancelhas
    pup = 0.26 if (ab > 0.5 or expr == "assustado") else 0.46
    oss = []
    for lado in (-1, 1):
        olho(ctx, lado * 40, -128, 26, 28, P["look"], P["lid"], cor, sd + 90 + lado, pupila=pup, feliz=P["feliz"],
             iris=hexc("#FFC21A") if st.get("silhueta") else None)
        oss.append((lado * 40, -128, 26, 28, lado))
    sobrancelhas(ctx, oss, "julgando" if expr == "neutro" and ab < 0.1 else expr, sd + 7)
    ctx.restore()
    if st.get("suor"):
        _gota(ctx, 118, -150, t, sd)
    return {"corpo": (-215, -215, 220, 215), "rosto": (-110, -200, 110, -30)}


def _gota(ctx, x, y, t, sd):
    u = (t * 1.3 + sd * 0.1) % 1.0
    yy = y + u * 36
    F(ctx, [(x, yy - 24), (x + 12, yy), (x, yy + 12), (x - 12, yy)], hexc("#7FD6FF"), sd + 301, lw=4, amp=0.2, sombra=False)


def _trex_perfil(ctx, S, P, st):
    sd = P["seed"]; t = P["t"]; expr = P["expr"]
    ab = P["abre"]; om = P["omb"]
    cor, cor2, lis = S["cor"], S["cor2"], S["listra"]
    ctx.translate(P["treme"] - 20, 0)
    bob = 3 * math.sin(t * 2.2); a = P["rabo"]
    tail = [(-90, 0), (-190, 14 + 12 * a), (-290, 70 + 34 * a), (-320, 100 + 40 * a), (-200, 96 + 14 * a), (-96, 126)]
    F(ctx, tail, cor, sd + 1, sb=0.1, sombra=True)
    for k in range(3):
        traco(ctx, [(-140 - k * 50, 40 + k * 12 + 6 * a), (-150 - k * 50, 70 + k * 12 + 6 * a)], lw=8, cor=lis, seed=sd + 2 + k, alpha=0.8)

    def perna(x, c, k, lado):
        lift = max(0, _passo(P, k, 16))
        F(ctx, EL(x + 5, 102, 56, 72, 18, 0.2), c, sd + 10 + lado, sb=0.12)
        tubo(ctx, [(x + 14, 150), (x + 4, 176 - lift), (x + 16, 194 - lift)], c, 34, sd + 12 + lado)
        F(ctx, EL(x + 42, 199 - lift, 52, 16, 14), c, sd + 14 + lado)
        _garras(ctx, x + 84, 196 - lift, 3, 12, 0.8, S["garra"], sd + 16 + lado)
    perna(-34, escurece(cor, 0.2), math.pi, 0)
    F(ctx, EL(-6, 36, 130, 98, 28, -0.16), cor, sd + 20, sombra=True, sb=0.16)
    F(ctx, EL(34, 66, 84, 52, 20, -0.16), cor2, sd + 21, lw=0)
    for i in range(3):
        traco(ctx, [(-78 + i * 48, -42 + i * 5), (-66 + i * 48, 4 + i * 5)], lw=12, cor=lis, seed=sd + 22 + i, alpha=0.75)
    perna(10, cor, 0, 1)
    # bracinho
    sx, sy = 74, 46
    tubo(ctx, [(sx, sy), (sx + 26 + om * 10, sy + 30 - om * 34), (sx + 50 + om * 14, sy + 24 - om * 56)], cor, 18, sd + 30)
    _garras(ctx, sx + 52 + om * 14, sy + 28 - om * 56, 2, 10, 0.8, S["garra"], sd + 31)
    # pescoço e cabeça
    hxx, hyy = 138, -92 + bob
    F(ctx, EL(100, -34, 52, 72, 18, 0.55), cor, sd + 40)
    ctx.save(); ctx.translate(hxx, hyy); ctx.rotate(-0.05 * ab + (0.025 * math.sin(t * 40) if ab > 0.5 else 0))
    for i in range(3):
        F(ctx, [(-40 + i * 26 - 10, -52), (-40 + i * 26, -76), (-40 + i * 26 + 10, -52)], S["espinho"], sd + 41 + i, lw=4.5, amp=0.4)
    # mandíbula de baixo (abre girando) atrás do crânio
    ctx.save(); ctx.translate(30, 34); ctx.rotate(ab * 0.5)
    if ab > 0.05:
        F(ctx, [(0, 0), (120, -2), (130, 12 - 6), (0, 6)], S["interior"], sd + 44, lw=4)
    F(ctx, EL(70, 12, 74, 17, 16), cor2, sd + 45)
    _dentes(ctx, 24, 128, 0, 6, 12, sd + 46, baixo=False, w=8)
    ctx.restore()
    F(ctx, EL(0, 0, 88, 66, 26, 0.05), cor, sd + 50, sombra=True, sb=0.14)
    F(ctx, EL(80, 8, 70, 38, 20, 0.1), cor, sd + 51)
    _dentes(ctx, 30, 140, 26, 6, 13, sd + 52, baixo=True, w=9)
    ctx.arc(142, -4, 5, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    tubo(ctx, [(10, -26), (50, -36), (84, -30)], escurece(cor, 0.25), 14, sd + 56)
    oss = []
    for ex, ey, r in ((38, -8, 21), (72, -6, 18)):
        olho(ctx, ex, ey, r, r * 1.05, P["look"] if P["olhar"] not in ("camera", "frente") else (0.7, 0.05), P["lid"], cor, sd + 60 + int(ex),
             pupila=P["pupila"], feliz=P["feliz"], iris=hexc("#FFC21A") if st.get("silhueta") else None)
        oss.append((ex, ey, r, r * 1.05, 1))
    sobrancelhas(ctx, oss, "julgando" if expr == "neutro" and ab < 0.1 else expr, sd + 8)
    ctx.restore()
    return {"corpo": (-340, -190, 280, 215), "rosto": (hxx - 70, hyy - 70, hxx + 200, hyy + 50)}


def _trex_cima(ctx, S, P, st):
    sd = P["seed"]; t = P["t"]; expr = P["expr"]
    cor, cor2, lis = S["cor"], S["cor2"], S["listra"]
    ab = P["abre"]
    ctx.translate(P["treme"], 0)
    ex, ey = 34, -160
    campo = st.get("campo", 70); D = st.get("alcance", 520)
    if campo > 0 and not st.get("sem_cone"):
        ang = math.atan(ex / D)
        for lado in (-1, 1):
            ctx.save(); ctx.translate(lado * ex, ey); ctx.rotate(-lado * ang)
            cone(ctx, 0, 0, campo, D / math.cos(ang), False, t)
            ctx.restore()
        if st.get("mira", True):   # régua tracejada + alvo onde os dois cones se cruzam
            ay = ey - D
            ctx.save(); ctx.set_dash([14, 12], (t * 30) % 26); ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.9)
            ctx.move_to(0, ey - 30); ctx.line_to(0, ay + 40); ctx.stroke(); ctx.restore()
            for k in range(1, 5):
                yy = ey - 30 - (D - 70) * k / 5
                traco(ctx, [(-12, yy), (12, yy)], lw=5, cor=BRANCO, amp=0)
            pul = 1 + 0.12 * math.sin(t * 7)
            ctx.save(); ctx.translate(0, ay); ctx.scale(pul, pul)
            ctx.arc(0, 0, 34, 0, 2 * math.pi); ctx.set_source_rgba(1, 0.2, 0.2, 0.25); ctx.fill_preserve(); ctx.set_source_rgb(*hexc("#E8352A")); ctx.set_line_width(7); ctx.stroke()
            for dx, dy in ((-52, 0), (52, 0), (0, -52), (0, 52)):
                traco(ctx, [(dx * 0.62, dy * 0.62), (dx, dy)], lw=7, cor=hexc("#E8352A"), amp=0)
            ctx.restore()
    # cauda
    a = P["rabo"]
    F(ctx, [(-44, 120), (-30 + 14 * a, 250), (10 * a, 360), (26 * a + 6, 372), (30 + 14 * a, 250), (44, 120)], cor, sd + 1, sb=0.1)
    for lado in (-1, 1):   # pés
        k = 0 if lado < 0 else math.pi
        F(ctx, EL(lado * 92, 80 + _passo(P, k, 14), 28, 46, 14), escurece(cor, 0.15), sd + 5 + lado)
    F(ctx, EL(0, 62, 78, 142, 28), cor, sd + 10, sombra=True, sb=0.14)
    for i in range(4):
        traco(ctx, [(-54, 30 + i * 44), (0, 42 + i * 44), (54, 30 + i * 44)], lw=11, cor=lis, seed=sd + 11 + i, alpha=0.7)
    for lado in (-1, 1):   # bracinhos
        tubo(ctx, [(lado * 70, -40), (lado * 98, -20), (lado * 92, 6)], cor, 16, sd + 20 + lado)
    # cabeção
    F(ctx, EL(0, -138, 66, 70, 26), cor, sd + 30, sombra=True, sb=0.12)
    F(ctx, EL(0, -204, 42, 34, 18), cor, sd + 31)
    for lado in (-1, 1):
        ctx.arc(lado * 14, -222, 4, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    pup = 0.26 if expr == "assustado" else 0.5
    oss = []
    for lado in (-1, 1):
        olho(ctx, lado * ex, ey, 17, 18, (0, -0.7), P["lid"], cor, sd + 40 + lado, pupila=pup, feliz=P["feliz"])
        oss.append((lado * ex, ey, 17, 18, lado))
    sobrancelhas(ctx, oss, "julgando" if expr == "neutro" else expr, sd + 9)
    return {"corpo": (-120, -240, 120, 380), "rosto": (-66, -240, 66, -70)}


def _trex_cranio(ctx, S, P, st):
    """Crânio estilizado (osso claro, órbita, dentes) com lupa por cima."""
    sd = P["seed"]; t = P["t"]
    osso = hexc("#F4EAD2"); osso2 = escurece(osso, 0.18)
    F(ctx, [(-190, -40), (-120, -110), (10, -130), (110, -92), (200, -50), (214, 8), (160, 30), (-20, 30), (-150, 56), (-196, 20)], osso, sd + 1, sb=0.14)
    F(ctx, [(-10, 34), (160, 34), (206, 56), (150, 78), (20, 74), (-30, 52)], osso, sd + 2)
    _dentes(ctx, 20, 190, 30, 8, 22, sd + 3, baixo=True, w=14)
    F(ctx, EL(-60, -36, 46, 52, 18), hexc("#2B2233"), sd + 4, lw=5)
    F(ctx, EL(100, -22, 18, 12, 12), hexc("#2B2233"), sd + 5, lw=4)
    F(ctx, EL(30, -58, 36, 26, 16), hexc("#2B2233"), sd + 6, lw=4)
    for i in range(3):
        traco(ctx, [(-150 + i * 60, -80 + i * 6), (-130 + i * 60, -54 + i * 6)], lw=6, cor=osso2, seed=sd + 7 + i)
    # lupa balançando sobre a órbita
    ang = 0.15 * math.sin(t * 2.4)
    ctx.save(); ctx.translate(-30 + 14 * math.sin(t * 1.8), -30); ctx.rotate(ang)
    traco(ctx, [(60, 70), (112, 138)], lw=20, cor=hexc("#8A4B2A"), seed=sd + 20, amp=0)
    ctx.arc(0, 0, 84, 0, 2 * math.pi); ctx.set_source_rgba(0.75, 0.92, 1.0, 0.28); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(16); ctx.stroke()
    ctx.arc(0, 0, 84, 0, 2 * math.pi); ctx.set_source_rgb(*hexc("#FFC21A")); ctx.set_line_width(8); ctx.stroke()
    traco(ctx, [(-44, -34), (-22, -56)], lw=9, cor=BRANCO, amp=0)
    ctx.restore()
    return {"corpo": (-215, -135, 220, 215), "rosto": None}


def _trex_pegada(ctx, S, P, st):
    sd = P["seed"]
    cor = hexc(st.get("cor", "#3A2A22"))
    F(ctx, EL(0, 40, 62, 74, 16), cor, sd + 1, sombra=False, lw=5)
    for i, (dx, dy, r) in enumerate(((-64, -34, -0.5), (0, -62, 0), (64, -34, 0.5))):
        F(ctx, EL(dx, dy, 24, 44, 12, r), cor, sd + 2 + i, sombra=False, lw=5)
        F(ctx, [(dx - 8, dy - 36), (dx + 8, dy - 36), (dx, dy - 66)], BRANCO, sd + 6 + i, lw=3.5, sombra=False, amp=0.2)
    return {"corpo": (-100, -130, 100, 120), "rosto": None}


# -------------------------- bico-de-pato
def _bico_olhos(ctx, S, P, pos_lado, pos_frente, r_lado, r_frente, sd):
    """Olhos: 'lado' = um olho alto na lateral (como é de verdade); 'frente' = dois juntos na cara, com sobrancelha."""
    expr = P["expr"]; oss = []
    if P["olhos"] == "frente":
        for i, (x, y, lado) in enumerate(pos_frente):
            olho(ctx, x, y, r_frente, r_frente * 1.05, P["look"], P["lid"], S["cor"], sd + 90 + i, pupila=P["pupila"], feliz=P["feliz"])
            oss.append((x, y, r_frente, r_frente * 1.05, lado))
        sobrancelhas(ctx, oss, expr, sd + 7)
    else:
        for i, (x, y, lado) in enumerate(pos_lado):
            olho(ctx, x, y, r_lado * 0.62, r_lado * 1.15, P["look"], P["lid"], S["cor"], sd + 90 + i, pupila=P["pupila"], feliz=P["feliz"])


def _bico_frente(ctx, S, P, st):
    sd = P["seed"]; t = P["t"]; expr = P["expr"]
    cor, cor2, lis = S["cor"], S["cor2"], S["listra"]
    hy_off = P["bica"] * 38
    ctx.translate(P["treme"], 0)
    a = P["rabo"]
    tubo(ctx, [(60, 176), (150, 188 + 6 * a), (196, 170), (208, 142 + 10 * a)], cor, 32, sd + 1)
    for i, lado in enumerate((-1, 1)):
        lift = max(0, _passo(P, i * math.pi, 14))
        x = lado * 52
        tubo(ctx, [(x, 110), (x + lado * 6, 188 - lift)], cor, 54, sd + 30 + i)
        F(ctx, EL(x + lado * 12, 197 - lift, 44, 16, 14), S["mao"], sd + 32 + i)
        for d in (-1, 0, 1):
            traco(ctx, [(x + lado * 12 + d * 22, 190 - lift), (x + lado * 12 + d * 22, 204 - lift)], lw=6, cor=INK, seed=sd + 34 + d, alpha=0.7)
    F(ctx, EL(0, 76, 120, 122, 28), cor, sd + 40, sombra=True, sb=0.16)
    F(ctx, EL(0, 100, 66, 92, 18), cor2, sd + 41, lw=0)
    for i in range(3):
        traco(ctx, [(-44, 70 + i * 36), (0, 78 + i * 36), (44, 70 + i * 36)], lw=5, cor=escurece(cor2, 0.25), seed=sd + 42 + i, alpha=0.8)
    for i, lado in enumerate((-1, 1)):   # bracinhos curtos
        tubo(ctx, [(lado * 100, 50), (lado * 128, 90), (lado * 122, 128)], cor, 22, sd + 50 + i)
        F(ctx, EL(lado * 122, 134, 15, 14, 10), S["mao"], sd + 52 + i, lw=4)
    ctx.save(); ctx.translate(0, hy_off)
    if st.get("crista", True):
        F(ctx, [(-22, -150), (-14, -214), (14, -214), (22, -150)], S["crista"], sd + 60, lw=5, amp=0.5)
        traco(ctx, [(0, -204), (0, -164)], lw=5, cor=escurece(hexc(st.get("crista_cor", "#FF8FA8")), 0.3), seed=sd + 61, alpha=0.7)
    F(ctx, EL(0, -102, 78, 70, 26), cor, sd + 62, sombra=True, sb=0.14)
    F(ctx, EL(0, -92, 50, 36, 16), cor2, sd + 63, lw=0)
    # bico largo de pato
    F(ctx, EL(0, -62, 94, 38, 24), S["bico"], sd + 64, sb=0.14)
    F(ctx, EL(0, -72, 70, 18, 16), S["bico2"], sd + 65, lw=0)
    for lado in (-1, 1):
        ctx.arc(lado * 34, -76, 4.5, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    boca(ctx, expr if expr != "neutro" else "neutro", 0, -50, 2.7, sd + 66)
    _bico_olhos(ctx, S, P, [(-70, -120, -1), (70, -120, 1)], [(-30, -128, -1), (30, -128, 1)], 26, 24, sd)
    ctx.restore()
    if st.get("suor") or expr == "assustado":
        _gota(ctx, 96, -150 + hy_off, t, sd)
    return {"corpo": (-210, -215, 220, 215), "rosto": (-100, -215 + hy_off, 100, -30 + hy_off)}


def _bico_perfil(ctx, S, P, st):
    sd = P["seed"]; t = P["t"]; expr = P["expr"]
    cor, cor2, lis = S["cor"], S["cor2"], S["listra"]
    bk = P["bica"]
    ctx.translate(P["treme"] - 30, 0)
    a = P["rabo"]
    F(ctx, [(-120, 30), (-210, 40 + 8 * a), (-300, 88 + 26 * a), (-312, 112 + 28 * a), (-210, 100 + 8 * a), (-110, 128)], cor, sd + 1, sb=0.1)

    def perna(x, c, k, lado, esp=34, topo=118):
        lift = max(0, _passo(P, k, 14))
        tubo(ctx, [(x, topo), (x + 2, 176 - lift), (x + 4, 194 - lift)], c, esp, sd + 10 + lado)
        F(ctx, EL(x + 16, 199 - lift, 40, 14, 14), S["mao"], sd + 14 + lado)
    perna(-70, escurece(cor, 0.2), math.pi, 0, 40)
    perna(60, escurece(cor, 0.2), 0, 2, 30)
    F(ctx, EL(-10, 62, 146, 90, 28, -0.05), cor, sd + 20, sombra=True, sb=0.16)
    F(ctx, EL(14, 98, 98, 44, 20, -0.05), cor2, sd + 21, lw=0)
    for i in range(3):
        traco(ctx, [(-70 + i * 52, -14 + i * 2), (-62 + i * 52, 30 + i * 2)], lw=11, cor=lis, seed=sd + 22 + i, alpha=0.75)
    perna(-40, cor, 0, 1, 44)
    perna(88, cor, math.pi, 3, 34)
    # pescoço e cabeça: bicando = cabeça desce até a samambaia
    hx = 150 + 60 * bk; hy = -86 + 238 * bk + 2 * math.sin(t * 2)
    tubo(ctx, [(70, 20), (96 + 30 * bk, -40 + 90 * bk), (hx - 14, hy + 8)], cor, 66, sd + 30)
    if bk > 0.3:
        _samambaia(ctx, hx + 112, 206, 0.9, t, sd + 5)
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(0.35 * bk)
    if st.get("crista", True):
        F(ctx, [(-34, -38), (-60, -88), (-12, -92), (4, -42)], S["crista"], sd + 40, lw=5, amp=0.5)
    F(ctx, EL(0, 0, 54, 44, 22), cor, sd + 41, sombra=True, sb=0.14)
    F(ctx, EL(88, 8, 62, 26, 18), S["bico"], sd + 42, sb=0.12)
    F(ctx, EL(92, 0, 40, 10, 12), S["bico2"], sd + 43, lw=0)
    ctx.arc(118, -2, 4, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    if P["olhos"] == "frente":
        oss = []
        for i, (ex, ey, lado) in enumerate(((10, -16, -1), (38, -14, 1))):
            olho(ctx, ex, ey, 17, 18, P["look"] if P["olhar"] not in ("camera", "frente") else (0.7, 0.1), P["lid"], cor, sd + 50 + i,
                 pupila=P["pupila"], feliz=P["feliz"])
            oss.append((ex, ey, 17, 18, 1))
        sobrancelhas(ctx, oss, expr, sd + 7)
    else:
        olho(ctx, 8, -10, 11, 20, (0.7, 0.2), P["lid"], cor, sd + 50, pupila=P["pupila"], feliz=P["feliz"])
    boca(ctx, expr, 78, 16, 0.8, sd + 60) if expr not in ("neutro",) else None
    ctx.restore()
    if st.get("suor") or expr == "assustado":
        _gota(ctx, hx + 40, hy - 70, t, sd)
    return {"corpo": (-330, -120, 300, 215), "rosto": (hx - 56, hy - 60, hx + 160, hy + 50)}


def _bico_cima(ctx, S, P, st):
    sd = P["seed"]; t = P["t"]; expr = P["expr"]
    cor, cor2, lis = S["cor"], S["cor2"], S["listra"]
    hy = -126 - 18 * P["bica"]
    ctx.translate(P["treme"], 0)
    if "campo" in st:
        cone(ctx, 0, hy - 10, st["campo"], st.get("alcance", 620), st.get("cego"), t)
    a = P["rabo"]
    F(ctx, [(-40, 130), (-26 + 12 * a, 250), (8 * a, 372), (24 * a + 4, 380), (28 + 12 * a, 250), (42, 130)], cor, sd + 1, sb=0.1)
    for i, (sx, yy) in enumerate(((-1, -20), (1, -20), (-1, 110), (1, 110))):
        F(ctx, EL(sx * 92, yy + _passo(P, i * 1.7 + (math.pi if i in (1, 2) else 0), 14), 24, 38, 12), S["mao"], sd + 5 + i)
    F(ctx, EL(0, 62, 82, 140, 28), cor, sd + 10, sombra=True, sb=0.14)
    for i in range(4):
        traco(ctx, [(-52, 20 + i * 44), (0, 32 + i * 44), (52, 20 + i * 44)], lw=11, cor=lis, seed=sd + 11 + i, alpha=0.7)
    F(ctx, EL(0, hy, 52, 58, 22), cor, sd + 30, sombra=True, sb=0.12)
    F(ctx, EL(0, hy - 70, 62, 30, 18), S["bico"], sd + 31, sb=0.12)
    if st.get("crista", True):
        F(ctx, EL(0, hy + 20, 12, 30, 12), S["crista"], sd + 32, lw=4)
    if P["olhos"] == "frente":
        oss = []
        for lado in (-1, 1):
            olho(ctx, lado * 24, hy - 24, 15, 16, (0, -0.6), P["lid"], cor, sd + 40 + lado, pupila=P["pupila"], feliz=P["feliz"])
            oss.append((lado * 24, hy - 24, 15, 16, lado))
        sobrancelhas(ctx, oss, expr, sd + 9)
    else:
        for lado in (-1, 1):
            olho(ctx, lado * 50, hy - 4, 9, 17, (lado * 0.8, 0), P["lid"], cor, sd + 40 + lado, pupila=P["pupila"], feliz=P["feliz"])
    return {"corpo": (-120, hy - 110, 120, 385), "rosto": (-62, hy - 100, 62, hy + 58)}


def _bico_planta(ctx, S, P, st):
    """Samambaia grande balançando (alvo do bico-de-pato; também folhas tremendo na borda escura)."""
    for i, dx in enumerate((-70, 0, 70)):
        _samambaia(ctx, dx, 120 - 8 * abs(dx) / 70, 1.2 - 0.2 * abs(dx) / 70, P["t"] + i, P["seed"] + i * 11, st.get("cor_folha", "#2E9E4A"))
    return {"corpo": (-170, -180, 170, 125), "rosto": None}


def _dino(ctx, S, P, st, vista):
    esp = S["nome"]
    _dino_cores(S, st)
    P["abre"] = clamp(float(st.get("abre", 0.0)))
    P["omb"] = clamp(float(st.get("ombros", 0.0)))
    if P["pose"] == "rugindo":
        P["abre"] = 1.0
        P["treme"] = math.sin(P["t"] * 55) * 3.0
    elif P["pose"] == "ombros":
        u = (P["t"] % 1.8) / 1.8
        P["omb"] = clamp(min(u / 0.12, 1.0) * (1 - clamp((u - 0.62) / 0.18))) if u < 0.8 else 0.0
    tab = {"tiranossauro": dict(frente=_trex_frente, perfil=_trex_perfil, cima=_trex_cima, cranio=_trex_cranio, pegada=_trex_pegada),
           "bicodepato": dict(frente=_bico_frente, perfil=_bico_perfil, cima=_bico_cima, planta=_bico_planta)}[esp]
    if vista not in tab:
        raise SystemExit(f"bicho: {esp} não tem vista '{vista}'. Vistas: {', '.join(tab)}")
    return tab[vista](ctx, S, P, st)
