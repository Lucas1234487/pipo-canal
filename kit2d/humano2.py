"""Humano 2 do PipoPop 2D: cartoon editorial de cabeça grande, silhueta com ombros, cintura, cotovelos e mãos.
desenha_humano2(ctx, st, t, seed) recebe o contexto já no centro do elemento e devolve {"corpo", "rosto"} (caixas locais).
Os pés ficam sempre em y = +338 (mesmo chão para adulto, criança e idoso); a cabeça do adulto fica perto de y = -236.
Propriedades em kit2d/CENAS.md (tipo humano)."""
import math, random
import cairo
from estilo import (INK, LW, BRANCO, VERMELHO, hexc, mix, escurece, clareia, forma, traco, path_suave, jitter,
                    pts_elipse, pts_ret, ease_in_out, ease_out_back, clamp)

PELES = {"clara": "#F6C9A0", "media": "#D9935F", "morena": "#A8683D", "escura": "#6E4227"}
CABELO_COR = {"preto": "#231A2B", "castanho": "#5A3420", "loiro": "#E8B84A", "ruivo": "#C8531F", "grisalho": "#BDB7C4",
              "azul": "#2D58D6", "branco": "#EDEAF2", "rosa": "#E85A9A",
              "platinado": "#F3E7C2", "castanho_escuro": "#3A2218", "caramelo": "#C98A4B"}
BOCA_ESCURA = hexc("#6E1A2A")
LINGUA = hexc("#F0687A")
AGUA = hexc("#7FD3FF")
ROSADO = (1.0, 0.36, 0.42)
T_POSE = 0.38   # segundos da troca suave de pose


def _cor(v, padrao):
    if v is None or v is True:
        return hexc(padrao)
    return hexc(PELES.get(v, CABELO_COR.get(v, v)))


# ======================================================================== proporções
def _proporcoes(st):
    idade = st.get("idade", "adulto")
    corpo = st.get("corpo", "medio")
    lar = {"magro": (90, 60, 70, 26, 25, 22), "forte": (136, 108, 104, 38, 38, 30),
           "maromba": (172, 100, 100, 58, 40, 42)}.get(corpo, (110, 80, 86, 32, 30, 25))   # maromba: ombrão, cintura fina, braço enorme
    ow, cw, hw, aw, pw, nw = lar
    P = dict(idade=idade, chao=338.0, lean=0.0, joelho=0.0)
    if idade == "crianca":
        k = 0.70
        P.update(rx=96, ry=102, hy=228, sy=92, ua=66, fa=60, olho=(38, 23, 27), mao=22, queda=40)
        ow, cw, hw, aw, pw, nw = ow * k, cw * k * 1.05, hw * k, aw * 0.85, pw * 0.85, nw * 0.8
        P["hc"] = P["sy"] - 12 - P["ry"]
    else:
        P.update(rx=88, ry=98, hy=118, sy=-112, ua=112, fa=104, olho=(34, 18, 22), mao=27, queda=66)
        P["hc"] = P["sy"] - 26 - P["ry"]
        if idade == "idoso":
            P["hc"] += 20; P["lean"] = 0.09; P["joelho"] = 10; P["olho"] = (34, 16, 19)
    pesc = st.get("pescoco", "normal")
    pesc = {"longo": 40, "curto": -12, "normal": 0}.get(pesc, pesc if isinstance(pesc, (int, float)) else 0)
    P["hc"] -= pesc * (0.6 if idade == "crianca" else 1.0)
    P.update(ow=ow, cw=cw, hw=hw, aw=aw, pw=pw, nw=nw, cabeca=st.get("cabeca", "oval"), queixo=st.get("queixo", "normal"))
    P["muque"] = corpo == "maromba"
    if P["muque"]:
        P["mao"] = 33
    P["oleo"] = bool(st.get("bronzeado"))
    P["chuteira"] = bool(st.get("chuteira"))
    if st.get("olhos") == "grandes":   # olhos de personagem bonito: maiores e mais altos
        ex, erx, ery = P["olho"]; P["olho"] = (ex + 2, erx * 1.12, ery * 1.3)
    if st.get("oculos") and st.get("oculos_tipo") == "fundo_de_garrafa":
        ex, erx, ery = P["olho"]; P["olho"] = (ex, erx * 1.3, ery * 1.3)
    return P


def _fcab(P, a):
    """Contorno da cabeça (sem o centro) no ângulo a: oval, feijao, pera, quadrada, lua; queixo quadrado."""
    rx, ry = P["rx"], P["ry"]
    c, s = math.cos(a), math.sin(a)
    tipo = P.get("cabeca", "oval")
    jaw = 0.06 if P["idade"] == "crianca" else 0.15
    sq = lambda v, e: math.copysign(abs(v) ** e, v)
    if tipo == "quadrada":
        x, y = rx * 1.04 * sq(c, 0.4), ry * 0.96 * sq(s, 0.4)
    elif tipo == "pera":
        x, y = rx * c * (0.64 + 0.58 * ((s + 1) / 2) ** 1.4) * (1 - 0.1 * max(0, s) ** 6), ry * 1.06 * s
    elif tipo == "feijao":
        ang = math.atan2(s, c)
        x = rx * 0.92 * c * (1 - 0.24 * math.exp(-(ang - 0.1) ** 2 / 0.18)) - 0.26 * rx * s
        y = ry * 1.14 * s
    elif tipo == "lua":
        x, y = rx * 1.26 * c, ry * 0.94 * s
    else:
        x, y = rx * c * (1 - jaw * max(0, s) ** 2.2), ry * s
    if P.get("queixo") == "quadrado" and s > 0.25:
        k = clamp((s - 0.25) / 0.6) * 0.75
        x = x + (rx * 0.96 * sq(c, 0.7) - x) * k
        y = y + (ry * 1.02 * sq(s, 0.6) - y) * k
    return x, y


# ======================================================================== poses
POSES = ("em_pe", "sentado", "bracos_cruzados", "maos_na_cabeca", "acenando", "apontando", "comemorando", "muque", "correndo", "caido")


def _ik(S, T, a, b, dobra):
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = clamp(math.hypot(dx, dy), abs(a - b) + 1, (a + b) * 0.995)
    base = math.atan2(dy, dx)
    A = math.acos(clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1))
    a1 = base + dobra * A
    E = (S[0] + a * math.cos(a1), S[1] + a * math.sin(a1))
    Tc = (S[0] + d * math.cos(base), S[1] + d * math.sin(base))
    return a1, math.atan2(Tc[1] - E[1], Tc[0] - E[0])


def _bracos_pose(pose, P, st, t, sx, seed):
    """(ângulo do braço, ângulo do antebraço, tipo de mão) para o braço do lado sx (-1 esquerda da tela, +1 direita)."""
    S = (sx * P["ow"] * 0.88, P["sy"] + 24)
    a, b = P["ua"], P["fa"]
    hc, rx, ry = P["hc"], P["rx"], P["ry"]
    if st.get("segura") == "celular" and pose in ("em_pe", "sentado"):
        a1, a2 = _ik(S, (sx * 44, P["sy"] + 0.95 * a), a, b, -sx)
        return a1, a2, "segura"
    lado_acao = 1
    if pose == "apontando":
        dx, dy = (st.get("aponta_para") or [1, 0])[:2]
        if st.get("espelha"):
            dx = -dx
        lado_acao = 1 if dx >= 0 else -1
        if sx == lado_acao:
            n = math.hypot(dx, dy) or 1
            ang = math.atan2(dy / n, dx / n)
            return ang - sx * 0.12, ang, "aponta"
    elif pose == "acenando" and sx == lado_acao:
        a1, a2 = _ik(S, (sx * (P["ow"] + 0.55 * (a + b) * 0.55), hc - ry * 0.15), a, b, sx)
        return a1, a2 + 0.42 * math.sin(t * 9.5), "aberta"
    elif pose == "comemorando":
        bomb = 14 * math.sin(t * 8 + (0 if sx > 0 else 1.2))
        a1, a2 = _ik(S, (sx * (P["ow"] + 0.30 * (a + b)), hc - ry * 0.95 + bomb), a, b, -sx)
        return a1, a2, "punho"
    elif pose == "muque":   # os dois braços dobrados para cima mostrando o bíceps (pulsa)
        pulso = 6 * math.sin(t * 6 + (0 if sx > 0 else 0.5))
        a1 = math.pi / 2 - sx * (math.pi / 2 + 0.12) + sx * 0.02 * math.sin(t * 6)
        return a1, -math.pi / 2 - sx * 0.18 + sx * pulso / 200, "punho"
    elif pose == "correndo":   # cotovelo dobrado, braços balançando alternados
        sw = 0.55 * math.sin(t * 9 + (0 if sx > 0 else math.pi))
        a1 = math.pi / 2 - sx * 0.42 + sw * 0.6
        return a1, -math.pi / 2 + sx * 0.12 + sw * 0.7, "punho"
    elif pose in ("maos_na_cabeca", "caido"):
        a1, a2 = _ik(S, (sx * rx * 0.86, hc - ry * 0.40), a, b, sx)
        return a1, a2, "aberta"
    elif pose == "bracos_cruzados":
        a1, a2 = _ik(S, (-sx * P["ow"] * 0.66, P["sy"] + 1.02 * a + (12 if sx < 0 else -2)), a, b, -sx)
        return a1, a2, "punho"
    bal = math.sin(t * 2.2 + sx + seed) * 0.05
    a1, a2 = _ik(S, (sx * (P["ow"] + 6), P["sy"] + 24 + (a + b) * 0.97), a, b, -sx)
    return a1 + bal, a2 + bal * 1.6, "relaxada"


def _lerp_ang(x, y, k):
    d = (y - x + math.pi) % (2 * math.pi) - math.pi
    return x + d * k


PADRAO = {"pose": "em_pe", "expressao": "neutro", "olhar": "camera"}


def _troca(st, prop, t, dur):
    """Valor anterior e progresso (0 a 1) da última troca de uma propriedade de texto (pose, expressao, olhar)."""
    tr = st.get("_troca_" + prop)
    if not tr:
        return None, 1.0
    prev, t0 = tr
    if not isinstance(prev, str):   # a propriedade não estava no JSON: valor do preset ou o padrão
        prev = (st.get("_preset") or {}).get(prop, PADRAO.get(prop))
    k = clamp((t - t0) / dur)
    return (prev if k < 1 else None), ease_in_out(k)


# ======================================================================== traços
def _linha(ctx, pts, lw, cor, alpha=1.0):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_line_width(lw); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgba(*cor, alpha); ctx.stroke()


def _tubo(ctx, pts, w, cor, sombra=True):
    if sombra:
        ctx.save(); ctx.translate(9, 11); _linha(ctx, pts, w + 10, INK, 0.28); ctx.restore()
    _linha(ctx, pts, w + 10, INK)
    _linha(ctx, pts, w, cor)


def _coracao(ctx, x, y, r, cor, lw=4):
    ctx.move_to(x, y + r * 0.9)
    ctx.curve_to(x - r * 1.5, y - r * 0.1, x - r * 0.8, y - r * 1.2, x, y - r * 0.4)
    ctx.curve_to(x + r * 0.8, y - r * 1.2, x + r * 1.5, y - r * 0.1, x, y + r * 0.9)
    ctx.close_path(); ctx.set_source_rgb(*cor); ctx.fill_preserve()
    ctx.set_line_width(lw); ctx.set_source_rgb(*INK); ctx.stroke()


def _gota(ctx, x, y, r, cor=AGUA):
    ctx.move_to(x, y - r * 1.9)
    ctx.curve_to(x + r * 0.4, y - r * 1.0, x + r, y - r * 0.3, x + r, y + r * 0.2)
    ctx.arc(x, y + r * 0.2, r, 0, math.pi)
    ctx.curve_to(x - r, y - r * 0.3, x - r * 0.4, y - r * 1.0, x, y - r * 1.9)
    ctx.close_path(); ctx.set_source_rgb(*cor); ctx.fill_preserve()
    ctx.set_line_width(4); ctx.set_source_rgb(*INK); ctx.stroke()
    ctx.arc(x - r * 0.35, y + r * 0.05, r * 0.25, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.85); ctx.fill()


# ======================================================================== mãos
def _mao(ctx, x, y, ang, tipo, pele, r, seed):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    if tipo == "aponta":
        forma(ctx, pts_ret(r * 0.4, -r * 0.62, r * 1.9, r * 0.5, r * 0.25, 2), pele, sombra=False, lw=4.5, seed=seed, amp=0.5)
        forma(ctx, pts_elipse(r * 0.3, 0, r * 0.95, r * 0.85, 12), pele, sombra=False, lw=4.5, seed=seed + 1, amp=0.6)
        traco(ctx, [(r * 0.6, -r * 0.05), (r * 0.95, r * 0.05)], lw=3.5, alpha=0.55, seed=seed + 2, amp=0.3)
    elif tipo == "punho":
        forma(ctx, pts_elipse(r * 0.35, 0, r * 0.95, r * 0.9, 12), pele, sombra=False, lw=4.5, seed=seed + 1, amp=0.6)
        for k in (-1, 0, 1):
            traco(ctx, [(r * 0.85, k * r * 0.42), (r * 1.15, k * r * 0.42)], lw=3.5, alpha=0.6, seed=seed + 3 + k, amp=0.3)
    elif tipo == "aberta":
        for i, a in enumerate((-0.62, -0.2, 0.2, 0.6)):   # dedos abertos
            ctx.save(); ctx.rotate(a)
            forma(ctx, pts_ret(r * 0.5, -r * 0.2, r * (1.25 - abs(a) * 0.35), r * 0.4, r * 0.2, 2), pele, sombra=False, lw=4, seed=seed + 5 + i, amp=0.4)
            ctx.restore()
        ctx.save(); ctx.rotate(-1.35)
        forma(ctx, pts_ret(r * 0.3, -r * 0.2, r * 0.9, r * 0.42, r * 0.2, 2), pele, sombra=False, lw=4, seed=seed + 9, amp=0.4)
        ctx.restore()
        forma(ctx, pts_elipse(r * 0.35, 0, r * 0.8, r * 0.78, 12), pele, sombra=False, lw=4.5, seed=seed + 1, amp=0.5)
        ctx.save(); ctx.translate(r * 0.35, 0); ctx.scale(r * 0.66, r * 0.62); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
        ctx.set_source_rgb(*pele); ctx.fill()
    else:   # relaxada / segura: luva simples com polegar
        ctx.save(); ctx.rotate(-1.0)
        forma(ctx, pts_ret(r * 0.2, -r * 0.24, r * 0.95, r * 0.48, r * 0.24, 2), pele, sombra=False, lw=4, seed=seed + 9, amp=0.4)
        ctx.restore()
        forma(ctx, pts_elipse(r * 0.45, 0, r * 1.0, r * 0.82, 12), pele, sombra=False, lw=4.5, seed=seed + 1, amp=0.6)
    ctx.restore()


def _braco(ctx, S, a1, a2, mao, P, roupa, pele, manga, seed):
    a, b, w = P["ua"], P["fa"], P["aw"]
    E = (S[0] + a * math.cos(a1), S[1] + a * math.sin(a1))
    Wr = (E[0] + b * math.cos(a2), E[1] + b * math.sin(a2))
    _tubo(ctx, [S, E, Wr], w, pele)
    if P.get("muque"):   # bíceps: bola do lado de dentro da dobra do cotovelo
        dx, dy = math.cos(a1), math.sin(a1)
        nx, ny = -dy, dx
        if nx * math.cos(a2) + ny * math.sin(a2) < 0:
            nx, ny = -nx, -ny
        bx, by = S[0] + dx * a * 0.48 + nx * w * 0.42, S[1] + dy * a * 0.48 + ny * w * 0.42
        ctx.save(); ctx.translate(bx, by); ctx.rotate(a1)
        forma(ctx, pts_elipse(0, 0, a * 0.42, w * 0.6, 14), pele, sombra=False, lw=5, seed=seed + 3, amp=0.5)
        ctx.restore()
    if P.get("oleo"):   # brilho de pele besuntada
        _linha(ctx, [(S[0] + (E[0] - S[0]) * 0.2 - 6, S[1] + (E[1] - S[1]) * 0.2 - 8), (S[0] + (E[0] - S[0]) * 0.7 - 6, S[1] + (E[1] - S[1]) * 0.7 - 8)], 6, (1, 1, 1), 0.55)
    if manga == "regata":
        M = S; ang = a1
        _mao(ctx, Wr[0], Wr[1], a2, mao, pele, P["mao"], seed + 40)
        return Wr
    if manga == "longa":
        M = (E[0] + (Wr[0] - E[0]) * 0.82, E[1] + (Wr[1] - E[1]) * 0.82)
        _linha(ctx, [S, E, M], w + 3, roupa)
        ang = a2
    else:
        M = (S[0] + (E[0] - S[0]) * 0.62, S[1] + (E[1] - S[1]) * 0.62)
        _linha(ctx, [S, M], w + 6, roupa)
        ang = a1
    nx, ny = -math.sin(ang), math.cos(ang)
    hw = (w + 6) / 2 + 2
    _linha(ctx, [(M[0] + nx * hw, M[1] + ny * hw), (M[0] - nx * hw, M[1] - ny * hw)], 4.5, INK)
    _mao(ctx, Wr[0], Wr[1], a2, mao, pele, P["mao"], seed + 40)
    return Wr


# ======================================================================== cabelo
def _hp(P, u, v):
    return (u * P["rx"], P["hc"] + v * P["ry"])


def _arco(P, a0, a1, r, n=12, bump=0.0):
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        rr = r + (bump if i % 2 else 0)
        x, y = _fcab(P, a)
        out.append((rr * x, P["hc"] + rr * y))
    return out


def _grao(ctx, x, y, w, h, cor, giro=0.0, alpha=1.0, contorno=0.3):
    """Grãozinho de milho da Pipo: quadrado arredondado com brilho branco (assinatura do canal)."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(giro)
    path_suave(ctx, pts_ret(-w / 2, -h / 2, w, h, min(w, h) * 0.38, 2)); ctx.set_source_rgba(*cor, alpha); ctx.fill_preserve()
    ctx.set_source_rgba(*INK, contorno * alpha); ctx.set_line_width(2.5); ctx.stroke()
    ctx.arc(-w * 0.18, -h * 0.2, min(w, h) * 0.16, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.75 * alpha); ctx.fill()
    ctx.restore()


def _brilho(ctx, P, cor, a0=215, a1=250, r=0.9):
    traco(ctx, _arco(P, a0, a1, r, 4), lw=9, cor=clareia(cor, 0.35), seed=7, amp=0.4, alpha=0.85)


def _fio(cor):
    """Cor dos fios: mais escura no cabelo claro, mais clara no cabelo escuro (senão some)."""
    lum = 0.3 * cor[0] + 0.59 * cor[1] + 0.11 * cor[2]
    return clareia(cor, 0.3) if lum < 0.25 else escurece(cor, 0.35)


def _mechas(ctx, pts_pares, cor, seed):
    for i, (p, q, m) in enumerate(pts_pares):
        traco(ctx, [p, m, q], lw=3.5, cor=_fio(cor), seed=seed + i, amp=0.5)


def _cachos(P, r, n, raio, a0=150, a1=390):
    out = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / (n - 1))
        out.append((r * math.cos(a) * P["rx"], P["hc"] + r * math.sin(a) * P["ry"], raio * (0.9 + 0.2 * ((i * 7) % 3) / 2)))
    return out


def _bolhas(ctx, lobos, cor, seed, sombra=True):
    if sombra:
        for x, y, r in lobos:
            ctx.new_sub_path(); ctx.arc(x + 9, y + 11, r, 0, 2 * math.pi)
        ctx.set_source_rgba(*INK, 0.28); ctx.fill()
    for x, y, r in lobos:
        ctx.new_sub_path(); ctx.arc(x, y, r + LW / 2, 0, 2 * math.pi)
    ctx.set_source_rgb(*INK); ctx.fill()
    for x, y, r in lobos:
        ctx.new_sub_path(); ctx.arc(x, y, r - LW / 2, 0, 2 * math.pi)
    ctx.set_source_rgb(*cor); ctx.fill()


def _espirais(ctx, P, cor, pontos, seed):
    c = escurece(cor, 0.38)
    for i, (u, v) in enumerate(pontos):
        x, y = _hp(P, u, v)
        traco(ctx, [(x - 9, y + 4), (x - 6, y - 7), (x + 5, y - 6), (x + 6, y + 4), (x - 1, y + 3)], lw=3.5, cor=c, seed=seed + i, amp=0.4)


def _sway(t, seed, v, k=0.05):
    """Balanço do cabelo comprido: cresce para as pontas (v maior)."""
    return k * math.sin(t * 2.1 + seed * 0.37) * max(0.0, v) + 0.02 * math.sin(t * 3.3 + seed) * max(0.0, v - 0.6)


def _cabelo_tras(ctx, P, estilo, cor, t, seed, luzes=None):
    if estilo == "volumoso":   # cabelão de propaganda de xampu: volume, ondas nas pontas e balanço
        lado = [(1.1, -0.62), (1.28, -0.12), (1.42, 0.42), (1.46, 0.92), (1.4, 1.32)]
        pontas = [(1.48, 1.64), (1.24, 1.5), (1.14, 1.76), (0.92, 1.52), (0.74, 1.66), (0.58, 1.32)]
        H = lambda pts, sx: [_hp(P, sx * u + _sway(t, seed, v), v) for u, v in pts]
        pts = _arco(P, 198, 342, 1.26, 8) + H(lado, 1) + H(pontas, 1) + H(list(reversed(pontas)), -1) + H(list(reversed(lado)), -1)
        forma(ctx, pts, escurece(cor, 0.12), seed=seed, amp=1.0)
        for sx in (-1, 1):
            for j, du in enumerate((0.0, 0.16)):
                traco(ctx, H([(1.12 - du, 0.1), (1.3 - du, 0.62), (1.22 - du, 1.05), (1.32 - du, 1.45)], sx), lw=4, cor=_fio(cor), seed=seed + 3 + j + sx, amp=0.4)
            if luzes is not None:
                traco(ctx, H([(1.2, 0.2), (1.36, 0.7), (1.3, 1.1), (1.38, 1.4)], sx), lw=9, cor=luzes, seed=seed + 7 + sx, amp=0.4, alpha=0.8)
        return
    if estilo == "longo":
        lado = [(1.02, -0.6), (1.14, -0.05), (1.2, 0.55), (1.22, 1.05)]
        pontas = [(1.18, 1.55), (0.95, 1.28), (0.74, 1.6), (0.5, 1.22)]
        pts = _arco(P, 200, 340, 1.12, 8)
        pts += [_hp(P, *q) for q in lado] + [_hp(P, *q) for q in pontas]
        pts += [_hp(P, -u, v) for u, v in reversed(pontas)] + [_hp(P, -u, v) for u, v in reversed(lado)]
        forma(ctx, pts, escurece(cor, 0.12), seed=seed, amp=1.2)
        _mechas(ctx, [(_hp(P, 0.98, 0.4), _hp(P, 0.95, 1.25), _hp(P, 1.06, 0.85)),
                      (_hp(P, -0.98, 0.4), _hp(P, -0.95, 1.25), _hp(P, -1.06, 0.85))], cor, seed + 5)
    elif estilo == "franja_reta":
        pts = _arco(P, 200, 340, 1.12, 8) + [_hp(P, *q) for q in ((1.14, 0.0), (1.16, 0.78), (-1.16, 0.78), (-1.14, 0.0))]
        forma(ctx, pts, escurece(cor, 0.12), seed=seed, amp=0.8)
    elif estilo == "cacheado":
        lob = _cachos(P, 1.16, 13, 34, 140, 400)
        lob += [(u * P["rx"], P["hc"] + v * P["ry"], 34) for u, v in ((-1.12, 0.75), (1.12, 0.75), (-0.98, 1.05), (0.98, 1.05))]
        _bolhas(ctx, lob, cor, seed)
    elif estilo == "black_power":
        lob = _cachos(P, 1.38, 15, 44, 135, 405)
        lob += [(0, P["hc"] - 0.55 * P["ry"], 90), (-0.7 * P["rx"], P["hc"] - 0.2 * P["ry"], 80), (0.7 * P["rx"], P["hc"] - 0.2 * P["ry"], 80)]
        _bolhas(ctx, lob, cor, seed)
    elif estilo == "coque":
        x, y = _hp(P, 0.05, -1.22)
        forma(ctx, pts_elipse(x, y, 50, 42, 14), cor, seed=seed, amp=1)
        traco(ctx, [(x - 26, y + 4), (x - 10, y - 18), (x + 18, y - 14), (x + 22, y + 6)], lw=3.5, cor=escurece(cor, 0.35), seed=seed + 1)
    elif estilo == "rabo_de_cavalo":
        bal = math.sin(t * 3.1 + seed) * 0.06
        x0, y0 = _hp(P, 0.55, -0.82)
        ctx.save(); ctx.translate(x0, y0); ctx.rotate(bal)
        pts = [(0, -14), (60, -36), (112, 10), (128, 110), (110, 200), (128, 268), (78, 205), (66, 120), (40, 40), (-10, 20)]
        forma(ctx, pts, cor, seed=seed, amp=1.2)
        traco(ctx, [(40, -6), (96, 60), (98, 170)], lw=3.5, cor=escurece(cor, 0.35), seed=seed + 1)
        ctx.restore()


def _cabelo_frente(ctx, P, estilo, cor, idade, seed, bone, t=0.0, luzes=None):
    rx, ry = P["rx"], P["ry"]
    esc = _fio(cor)
    H = lambda pts: [_hp(P, u, v) for u, v in pts]
    if estilo == "volumoso" and not bone:
        out = _arco(P, 172, 368, 1.2, 14, bump=0.03)
        linha = [(1.08, 0.22), (1.0, -0.16), (0.84, -0.44), (0.58, -0.6), (0.3, -0.7), (0.18, -0.8),   # risca do lado direito
                 (0.02, -0.72), (-0.26, -0.68), (-0.56, -0.62), (-0.82, -0.44), (-1.0, -0.12), (-1.1, 0.18)]   # franja varrida para a esquerda
        forma(ctx, out + H(linha), cor, sombra=False, seed=seed + 11, amp=0.7)
        for i, q in enumerate(([(0.16, -1.02), (-0.3, -0.82), (-0.74, -0.42)], [(0.2, -1.0), (-0.1, -0.82), (-0.5, -0.7)], [(0.24, -1.02), (0.62, -0.84), (0.94, -0.38)])):
            traco(ctx, H(q), lw=3.5, cor=esc, seed=seed + 12 + i, amp=0.4)
        if luzes is not None:
            traco(ctx, H([(0.12, -0.98), (-0.36, -0.78), (-0.8, -0.5)]), lw=9, cor=luzes, seed=seed + 16, amp=0.3, alpha=0.85)
        traco(ctx, _arco(P, 212, 252, 0.98, 6), lw=13, cor=clareia(cor, 0.5), seed=seed + 17, amp=0.3, alpha=0.75)   # brilho de xampu
        traco(ctx, _arco(P, 222, 244, 1.03, 4), lw=5, cor=(1, 1, 1), seed=seed + 18, amp=0.2, alpha=0.7)
        sx_ = -1
        for sx in (-1, 1):   # mechas da frente caindo nos ombros, com balanço
            sw = lambda v: _sway(t, seed + 5, v)
            pts = [_hp(P, sx * u + sw(v), v) for u, v in ((0.9, -0.02), (1.14, 0.14), (1.26, 0.6), (1.18, 1.02), (1.3, 1.44), (1.06, 1.3), (0.96, 0.84), (0.88, 0.3))]
            forma(ctx, pts, cor, sombra=False, seed=seed + 20 + sx, amp=0.6)
            traco(ctx, [_hp(P, sx * u + sw(v), v) for u, v in ((1.04, 0.2), (1.12, 0.66), (1.08, 1.1))], lw=3.5, cor=esc, seed=seed + 24 + sx)
            if luzes is not None and sx == sx_:
                traco(ctx, [_hp(P, sx * u + sw(v), v) for u, v in ((1.12, 0.3), (1.2, 0.7), (1.16, 1.15))], lw=7, cor=luzes, seed=seed + 26, alpha=0.8)
        return
    if estilo == "ondulado" and not bone:   # topo ondulado com volume, risca de lado e uma mecha caindo na testa
        pts = H([(-1.06, 0.02), (-1.04, -0.45), (-0.92, -0.9), (-0.62, -1.16), (-0.3, -1.22), (-0.1, -1.34), (0.2, -1.3), (0.48, -1.32),
                 (0.78, -1.12), (1.0, -0.78), (1.08, -0.36), (1.06, 0.02), (0.98, -0.36), (0.78, -0.6), (0.46, -0.68), (0.2, -0.66),
                 (0.06, -0.56), (-0.04, -0.42), (-0.12, -0.56), (-0.36, -0.68), (-0.68, -0.64), (-0.96, -0.4)])
        forma(ctx, pts, cor, sombra=True, sombra_off=(5, 7), seed=seed + 11, amp=0.7)
        for i, q in enumerate(([(-0.78, -0.62), (-0.55, -0.98), (-0.18, -1.08)], [(-0.4, -0.62), (-0.05, -0.92), (0.4, -1.06)],
                               [(0.2, -0.62), (0.55, -0.82), (0.86, -0.8)], [(0.06, -0.74), (-0.02, -0.58), (-0.04, -0.46)])):
            traco(ctx, H(q), lw=4, cor=esc, seed=seed + 12 + i, amp=0.4)
        traco(ctx, H([(-0.62, -1.0), (-0.3, -1.12), (0.05, -1.17)]), lw=10, cor=clareia(cor, 0.45), seed=seed + 17, amp=0.3, alpha=0.85)
        return
    if estilo == "raspado" and not bone:   # máquina 1: só a sombra dos fios, entradas altas
        linha = [(1.0, -0.1), (0.9, -0.5), (0.5, -0.72), (0.0, -0.76), (-0.5, -0.72), (-0.9, -0.5), (-1.0, -0.1)]
        pts = _arco(P, 182, 358, 1.03, 12) + H(linha)
        path_suave(ctx, pts); ctx.set_source_rgba(*cor, 0.85); ctx.fill()
        rr = random.Random(seed)
        for i in range(70):
            a = rr.uniform(200, 340); r = rr.uniform(0.82, 1.0)
            x, y = _fcab(P, math.radians(a)); ctx.arc(x * r, P["hc"] + y * r, 2.2, 0, 2 * math.pi)
        ctx.set_source_rgba(*escurece(cor, 0.4), 0.8); ctx.fill()
        traco(ctx, _arco(P, 182, 358, 1.0, 12), lw=4.5, seed=seed + 3, amp=0.4)
        return
    if estilo == "careca":
        if idade == "idoso":
            for sx in (-1, 1):
                forma(ctx, [_hp(P, sx * 0.86, -0.42), _hp(P, sx * 1.07, -0.3), _hp(P, sx * 1.1, 0.05), _hp(P, sx * 0.95, 0.12), _hp(P, sx * 0.92, -0.15)],
                      cor, sombra=False, lw=5, seed=seed + sx, amp=0.8)
        if not bone:
            traco(ctx, _arco(P, 220, 252, 0.8, 4), lw=10, cor=(1, 1, 1), alpha=0.45, seed=seed + 3, amp=0.3)
        return
    if bone and estilo in ("curto", "cacheado", "black_power", "coque", "topete", "moicano", "arrepiado", "calvicie"):
        if estilo in ("curto", "topete", "arrepiado", "calvicie"):
            for sx in (-1, 1):
                forma(ctx, [_hp(P, sx * 0.84, -0.5), _hp(P, sx * 1.06, -0.4), _hp(P, sx * 1.05, -0.02), _hp(P, sx * 0.92, -0.1)], cor, sombra=False, lw=5, seed=seed + sx)
        return
    if estilo == "topete":
        out = _arco(P, 172, 368, 1.06, 12)
        forma(ctx, out + H([(1.03, 0.0), (0.95, -0.4), (0.5, -0.58), (0.0, -0.6), (-0.5, -0.58), (-0.95, -0.4), (-1.03, 0.0)]), cor, sombra=False, seed=seed + 11, amp=0.8)
        q = H([(-0.86, -0.6), (-0.72, -1.1), (-0.3, -1.38), (0.3, -1.44), (0.8, -1.3), (1.08, -0.98), (0.86, -0.92), (0.62, -0.78), (0.3, -0.64), (-0.3, -0.6)])
        forma(ctx, q, cor, sombra=True, sombra_off=(6, 8), seed=seed + 13, amp=0.8)
        for i, d in enumerate((0.0, 0.14)):
            traco(ctx, H([(-0.62 + d, -0.78), (-0.2 + d, -1.12 + d * 0.5), (0.4 + d, -1.18 + d * 0.6), (0.82, -1.0 + d * 0.3)]), lw=4, cor=esc, seed=seed + 14 + i, amp=0.4)
        traco(ctx, H([(-0.35, -1.12), (0.05, -1.3), (0.4, -1.33)]), lw=8, cor=clareia(cor, 0.4), seed=seed + 15, amp=0.3, alpha=0.9)
        return
    if estilo == "moicano":
        out = _arco(P, 176, 364, 1.02, 12)
        path_suave(ctx, out + H([(1.0, -0.05), (0.9, -0.45), (0.0, -0.62), (-0.9, -0.45), (-1.0, -0.05)])); ctx.set_source_rgba(*cor, 0.35); ctx.fill()
        crista = H([(-0.24, -0.6), (-0.32, -1.12), (-0.2, -1.08), (-0.18, -1.5), (-0.04, -1.28), (0.05, -1.66), (0.14, -1.3), (0.26, -1.52), (0.24, -1.1), (0.34, -1.12), (0.24, -0.6)])
        forma(ctx, crista, cor, sombra=True, sombra_off=(6, 8), seed=seed + 13, amp=0.6)
        return
    if estilo == "calvicie":   # tufos dos lados e a "ponte", todos seguindo o contorno da cabeça (qualquer formato)
        for sx, (a0, a1) in ((1, (14, -40)), (-1, (166, 220))):
            pts = _arco(P, a0, a1, 1.1, 6) + list(reversed(_arco(P, a0, a1, 0.94, 6)))
            forma(ctx, pts, cor, sombra=False, lw=5, seed=seed + sx, amp=0.6)
        for i, r in enumerate((0.9, 0.97)):   # fiozinhos penteados por cima
            traco(ctx, _arco(P, 214 + i * 6, 326 - i * 4, r, 6), lw=4, cor=escurece(cor, 0.15), seed=seed + 5 + i, amp=0.4)
        traco(ctx, _arco(P, 236, 262, 0.8, 4), lw=10, cor=(1, 1, 1), alpha=0.45, seed=seed + 3, amp=0.3)
        return
    if estilo == "franja_reta":
        out = _arco(P, 176, 364, 1.09, 12)
        forma(ctx, out + H([(1.1, 0.72), (0.86, 0.72), (0.88, -0.3), (0.75, -0.4), (-0.75, -0.4), (-0.88, -0.3), (-0.86, 0.72), (-1.1, 0.72)]), cor, sombra=False, seed=seed + 11, amp=0.6)
        for k in range(-3, 4):
            traco(ctx, H([(k * 0.2, -0.62), (k * 0.2 + 0.02, -0.44)]), lw=3, cor=esc, seed=seed + 20 + k, amp=0.2)
        _brilho(ctx, P, cor, 222, 250, 0.98)
        return
    if estilo == "arrepiado":
        out = _arco(P, 165, 375, 1.08, 20, bump=0.3)
        forma(ctx, out + H([(1.02, 0.0), (0.9, -0.38), (0.65, -0.5), (0.5, -0.36), (0.3, -0.55), (0.1, -0.42), (-0.1, -0.58), (-0.3, -0.4), (-0.5, -0.56), (-0.7, -0.42), (-0.92, -0.36), (-1.02, 0.0)]),
              cor, sombra=False, seed=seed + 11, amp=1.2)
        _brilho(ctx, P, cor, 225, 250, 0.95)
        return
    if estilo == "curto":
        out = _arco(P, 172, 368, 1.08, 14, bump=0.07)
        linha = [(1.04, 0.0), (0.96, -0.3), (0.72, -0.44), (0.42, -0.4), (0.22, -0.56), (-0.08, -0.47), (-0.34, -0.6), (-0.62, -0.46), (-0.9, -0.34), (-1.04, 0.0)]
        forma(ctx, out + [_hp(P, u, v) for u, v in linha], cor, sombra=False, seed=seed + 11, amp=1.0)
        _mechas(ctx, [(_hp(P, -0.2, -0.95), _hp(P, 0.1, -0.62), _hp(P, -0.05, -0.8)), (_hp(P, 0.35, -0.98), _hp(P, 0.55, -0.6), _hp(P, 0.48, -0.8))], cor, seed + 12)
        _brilho(ctx, P, cor, 222, 248, 0.95)
    elif estilo in ("longo", "rabo_de_cavalo", "coque", "trancas"):
        out = _arco(P, 176, 364, 1.09, 12)
        if estilo == "longo":   # franja cortininha com pontas, risca no lado
            linha = [(1.06, 0.22), (0.96, -0.1), (0.8, -0.34), (0.62, -0.22), (0.5, -0.46), (0.3, -0.34), (0.12, -0.56), (-0.06, -0.66),
                     (-0.2, -0.46), (-0.38, -0.36), (-0.52, -0.5), (-0.7, -0.28), (-0.86, -0.36), (-0.98, -0.08), (-1.06, 0.22)]
        elif estilo == "trancas":   # risca no meio
            linha = [(1.06, 0.1), (0.96, -0.22), (0.7, -0.5), (0.3, -0.64), (0.02, -0.74), (-0.02, -0.74), (-0.3, -0.64), (-0.7, -0.5), (-0.96, -0.22), (-1.06, 0.1)]
        else:   # puxado para trás
            linha = [(1.06, 0.06), (0.98, -0.28), (0.78, -0.52), (0.45, -0.66), (0.0, -0.7), (-0.45, -0.66), (-0.78, -0.52), (-0.98, -0.28), (-1.06, 0.06)]
        forma(ctx, out + [_hp(P, u, v) for u, v in linha], cor, sombra=False, seed=seed + 11, amp=1.0)
        if estilo == "longo":
            _mechas(ctx, [(_hp(P, -0.1, -1.02), _hp(P, 0.3, -0.38), _hp(P, 0.18, -0.75)), (_hp(P, -0.1, -1.02), _hp(P, -0.5, -0.5), _hp(P, -0.36, -0.8)),
                          (_hp(P, 0.3, -1.0), _hp(P, 0.78, -0.36), _hp(P, 0.62, -0.72))], cor, seed + 12)
            for sx in (-1, 1):   # mechas soltas na frente dos ombros, pontas desencontradas
                pts = [_hp(P, sx * u, v) for u, v in ((0.9, -0.05), (1.1, 0.1), (1.14, 0.6), (1.06, 1.08), (1.13, 1.42), (0.94, 1.16), (0.86, 0.62), (0.84, 0.2))]
                forma(ctx, pts, cor, sombra=False, seed=seed + 20 + sx, amp=0.9)
                traco(ctx, [_hp(P, sx * 0.98, 0.2), _hp(P, sx * 1.0, 0.7), _hp(P, sx * 0.98, 1.1)], lw=3.5, cor=esc, seed=seed + 24 + sx)
        elif estilo == "trancas":
            _mechas(ctx, [(_hp(P, 0, -1.06), _hp(P, 0.62, -0.5), _hp(P, 0.4, -0.84)), (_hp(P, 0, -1.06), _hp(P, -0.62, -0.5), _hp(P, -0.4, -0.84))], cor, seed + 12)
        else:
            _mechas(ctx, [(_hp(P, -0.5, -0.66), _hp(P, 0.1, -1.06), _hp(P, -0.25, -0.95)), (_hp(P, 0.5, -0.66), _hp(P, 0.2, -1.06), _hp(P, 0.42, -0.92))], cor, seed + 12)
        _brilho(ctx, P, cor, 218, 246, 0.97)
    elif estilo in ("cacheado", "black_power"):
        lob = [(_hp(P, u, v)[0], _hp(P, u, v)[1], r) for u, v, r in
               ((-0.9, -0.42, 26), (-0.62, -0.62, 28), (-0.3, -0.72, 28), (0.02, -0.76, 29), (0.34, -0.72, 28), (0.64, -0.62, 28), (0.9, -0.42, 26))]
        _bolhas(ctx, lob, cor, seed + 11, sombra=False)
        _espirais(ctx, P, cor, ((-0.62, -0.62), (0.02, -0.76), (0.64, -0.62)) if estilo == "cacheado" else
                  ((-0.62, -0.62), (0.02, -0.76), (0.64, -0.62), (-1.15, -0.6), (1.15, -0.6), (0.0, -1.3)), seed + 30)


def _trancas(ctx, P, cor, t, seed):
    for sx in (-1, 1):
        x0, y0 = _hp(P, sx * 0.92, 0.25)
        forma(ctx, [_hp(P, sx * 0.86, -0.3), _hp(P, sx * 1.1, -0.2), _hp(P, sx * 1.08, 0.45), (x0 + sx * 6, y0 + 30), _hp(P, sx * 0.86, 0.3)], cor, sombra=False, lw=5, seed=seed + 70 + sx, amp=0.6)
        bal = math.sin(t * 2.6 + sx) * 4
        n = 6
        for i in range(n):
            y = y0 + 28 + i * 30
            x = x0 + sx * 6 + bal * i / n
            rr = 22 - i * 1.2
            ctx.save(); ctx.translate(x, y); ctx.rotate(0.45 * (1 if i % 2 else -1))
            forma(ctx, pts_elipse(0, 0, rr * 0.85, rr, 10), cor, sombra=(i == 0), lw=4.5, seed=seed + i * 3 + sx, amp=0.5)
            ctx.restore()
        y = y0 + 28 + n * 30 - 6
        forma(ctx, pts_elipse(x0 + sx * 6 + bal, y, 14, 8, 8), VERMELHO, sombra=False, lw=4, seed=seed + 50 + sx)
        forma(ctx, [(x0 + sx * 6 + bal - 14, y + 6), (x0 + sx * 6 + bal + 14, y + 6), (x0 + sx * 6 + bal + 8, y + 36), (x0 + sx * 6 + bal - 8, y + 36)],
              cor, sombra=False, lw=4.5, seed=seed + 60 + sx, amp=0.6)


# ======================================================================== rosto
EXPR = {   # tampa da pálpebra, inclinação (+ = bravo), pupila, pálpebra de baixo, sobrancelha (dentro, meio, fora), boca
    "neutro":       dict(lid=0.26, tilt=0.0, pup=1.0, baixo=0.0, sob=(0, -3, 0), boca="leve"),
    "feliz":        dict(lid=0.16, tilt=0.0, pup=1.0, baixo=0.32, sob=(-6, -12, -4), boca="sorriso_aberto", corado=0.25),
    "gargalhada":   dict(fecha="feliz", sob=(-12, -18, -6), boca="gargalhada", corado=0.35),
    "bravo":        dict(lid=0.28, tilt=0.55, pup=0.85, baixo=0.12, sob=(16, 2, -12), boca="careta"),
    "surpreso":     dict(lid=0.0, tilt=0.0, pup=0.62, baixo=0.0, sob=(-22, -30, -20), boca="o", grande=1.22),
    "triste":       dict(lid=0.36, tilt=-0.45, pup=1.08, baixo=0.0, sob=(-16, -6, 6), boca="triste", brilho=True),
    "chorando":     dict(fecha="apertado", sob=(-18, -6, 8), boca="choro"),
    "nervoso":      dict(lid=0.0, tilt=-0.15, pup=0.6, baixo=0.0, sob=(-14, -8, 0), boca="ondulada", grande=1.08),
    "envergonhado": dict(lid=0.32, tilt=-0.2, pup=1.0, baixo=0.18, sob=(-12, -7, 0), boca="sorrisinho", corado=0.85, olhar="baixo"),
    "apaixonado":   dict(lid=0.16, tilt=0.0, pup=1.15, baixo=0.15, sob=(-10, -14, -6), boca="sorriso", corado=0.45, coracao=True),
    "charmoso":     dict(lid=0.12, tilt=0.0, pup=1.12, baixo=0.22, sob=(-8, -13, -5), boca="charme", corado=0.2, brilho=True),
    "esforco":      dict(lid=0.22, tilt=0.4, pup=0.9, baixo=0.24, sob=(14, 0, -10), boca="careta"),
    "ofegante":     dict(lid=0.42, tilt=-0.25, pup=1.0, baixo=0.0, sob=(-12, -5, 4), boca="ofegante", corado=0.55),
    "cansado":      dict(lid=0.55, tilt=-0.1, pup=1.0, baixo=0.0, sob=(4, 2, 6), boca="cansado", olheira=True),
}
LOOK = {"camera": (0, 0), "frente": (0, 0), "celular": (0.1, 0.9), "baixo": (0, 0.85), "cima": (0, -0.9),
        "esq": (-0.9, 0.05), "dir": (0.9, 0.05), "esquerda": (-0.9, 0.05), "direita": (0.9, 0.05)}


def _olho(ctx, cx, cy, rx, ry, lado, look, e, lid, cor_lid, seed, iris=None):
    fecha = e.get("fecha")
    if fecha == "feliz":
        traco(ctx, [(cx - rx * 1.1, cy + 4), (cx, cy - ry * 0.75), (cx + rx * 1.1, cy + 4)], lw=7, seed=seed, amp=0.5)
        return
    if fecha == "apertado":
        d = -lado
        traco(ctx, [(cx - d * rx, cy - ry * 0.6), (cx + d * rx * 0.8, cy), (cx - d * rx, cy + ry * 0.6)], lw=7, seed=seed, amp=0.5)
        return
    if lid >= 0.95:
        traco(ctx, [(cx - rx * 1.05, cy), (cx, cy + 5), (cx + rx * 1.05, cy)], lw=6, seed=seed, amp=0.4)
        return
    g = e.get("grande", 1.0)
    rx, ry = rx * g, ry * g
    pts = pts_elipse(cx, cy, rx, ry, 16)
    p = jitter(pts, 0.6, seed)
    path_suave(ctx, p); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.save(); path_suave(ctx, p); ctx.clip()
    px, py = cx + look[0] * rx * 0.38, cy + look[1] * ry * 0.34
    pr = rx * 0.64 * e.get("pup", 1.0)
    if e.get("coracao"):
        _coracao(ctx, px, py + 2, pr * 1.05, hexc("#FF3D6E"), lw=3)
    else:
        if iris:   # íris colorida com pupila menor (olhar de personagem bonito)
            ctx.arc(px, py, pr * 1.05, 0, 2 * math.pi); ctx.set_source_rgb(*iris); ctx.fill_preserve()
            ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
            ctx.arc(px, py + pr * 0.15, pr * 0.7, 0, math.pi); ctx.set_source_rgba(*clareia(iris, 0.35), 0.6); ctx.fill()
            ctx.arc(px, py, pr * 0.52, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
        else:
            ctx.arc(px, py, pr, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
        ctx.arc(px - pr * 0.35, py - pr * 0.4, pr * (0.42 if e.get("brilho") else 0.3), 0, 2 * math.pi); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        if e.get("brilho"):
            ctx.arc(px + pr * 0.35, py + pr * 0.35, pr * 0.16, 0, 2 * math.pi); ctx.fill()
    xi, xo = cx - lado * (rx + 3), cx + lado * (rx + 3)
    tilt = e.get("tilt", 0.0)
    if lid > 0.02 or abs(tilt) > 0.02:
        yi = cy - ry + 2 * ry * lid + tilt * ry * 0.9
        yo = cy - ry + 2 * ry * lid - tilt * ry * 0.35
        ctx.move_to(xi, cy - ry - 6); ctx.line_to(xo, cy - ry - 6); ctx.line_to(xo, yo); ctx.line_to(xi, yi); ctx.close_path()
        ctx.set_source_rgb(*cor_lid); ctx.fill()
        ctx.restore(); ctx.save(); path_suave(ctx, p); ctx.clip()
        _linha(ctx, [(xi, yi), (xo, yo)], 5, INK)
    b = e.get("baixo", 0.0)
    if b > 0.01:
        yb = cy + ry - 2 * ry * b
        ctx.move_to(cx - rx - 4, cy + ry + 6); ctx.line_to(cx - rx - 4, yb + ry * 0.25); ctx.curve_to(cx - rx * 0.4, yb - ry * 0.05, cx + rx * 0.4, yb - ry * 0.05, cx + rx + 4, yb + ry * 0.25)
        ctx.line_to(cx + rx + 4, cy + ry + 6); ctx.close_path(); ctx.set_source_rgb(*cor_lid); ctx.fill()
    ctx.restore()
    path_suave(ctx, p); ctx.set_line_width(4.5); ctx.set_source_rgb(*INK); ctx.stroke()


def _dentes_fechada(ctx, dentes, x, y, w):
    """Dentes que aparecem mesmo de boca fechada (dentuço; aparelho no sorriso discreto)."""
    if dentes == "dentuco":
        for sx in (-1, 1):
            forma(ctx, pts_ret(x + (sx - 1) * 9 + (1 if sx > 0 else 0), y - 2, 17, 22, 5, 2), (1, 1, 1), sombra=False, lw=4, seed=7 + sx, amp=0.2)


def _dentes_abertos(ctx, dentes, x, top, alto, w):
    """Detalhes na faixa de dentes de cima (boca aberta)."""
    if dentes == "separados":
        ctx.rectangle(x - 4, top - 4, 8, alto + 4); ctx.set_source_rgb(*BOCA_ESCURA); ctx.fill()
    elif dentes == "banguela":
        ctx.rectangle(x + w * 0.12, top - 4, w * 0.32, alto + 4); ctx.set_source_rgb(*BOCA_ESCURA); ctx.fill()
    elif dentes == "aparelho":
        yy = top + alto * 0.55
        _linha(ctx, [(x - w * 1.4, yy), (x + w * 1.4, yy)], 3.5, hexc("#8A8FA8"))
        for k in range(-3, 4):
            ctx.rectangle(x + k * w * 0.28 - 4, yy - 4, 8, 8); ctx.set_source_rgb(*hexc("#B8BDD0")); ctx.fill_preserve()
            ctx.set_source_rgba(*INK, 0.6); ctx.set_line_width(1.5); ctx.stroke()
    elif dentes == "dentuco":
        for sx in (-1, 1):
            ctx.rectangle(x + (sx - 1) * 9 + (1 if sx > 0 else 0), top - 2, 17, alto + 12); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
            ctx.set_source_rgb(*INK); ctx.set_line_width(3); ctx.stroke()
    else:
        _linha(ctx, [(x, top), (x, top + alto)], 2.5, INK, 0.35)


def _labios(ctx, x, y, w, cor, seed, sorri=1.0):
    """Boca fechada com lábios coloridos: arco do cupido, lábio de baixo cheio, brilho e cantinhos para cima."""
    ww = w * 0.88; c = sorri * 5
    meio = [(x + ww * 0.5, y + 2), (x, y + 5), (x - ww * 0.5, y + 2)]
    cima = [(x - ww, y - c), (x - ww * 0.5, y - 9), (x - ww * 0.14, y - 11), (x, y - 7), (x + ww * 0.14, y - 11), (x + ww * 0.5, y - 9), (x + ww, y - c)] + meio
    baixo = [(x - ww, y - c), (x - ww * 0.5, y + 2), (x, y + 5), (x + ww * 0.5, y + 2), (x + ww, y - c), (x + ww * 0.55, y + 12), (x, y + 18), (x - ww * 0.55, y + 12)]
    forma(ctx, baixo, cor, sombra=False, lw=4, seed=seed, amp=0.25)
    forma(ctx, cima, escurece(cor, 0.14), sombra=False, lw=4, seed=seed + 1, amp=0.25)
    traco(ctx, [(x - ww, y - c), (x - ww * 0.5, y + 2), (x, y + 5), (x + ww * 0.5, y + 2), (x + ww, y - c)], lw=4.5, seed=seed + 2, amp=0.2)
    ctx.save(); ctx.translate(x - ww * 0.18, y + 10); ctx.scale(ww * 0.22, 3.2); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
    ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
    for sx in (-1, 1):   # covinha do sorriso
        traco(ctx, [(x + sx * (ww + 2), y - c + 1), (x + sx * (ww + 7), y - c - 5)], lw=3.5, alpha=0.7, seed=seed + 4 + sx, amp=0.2)


def _boca(ctx, tipo, x, y, w, t, seed, dentes="normal", labios=None):
    def aberta(top, bot, dentes_k=0.0, lingua=True, wob=0.0):
        pts = top + bot
        p = jitter(pts, 0.6, seed)
        path_suave(ctx, p); ctx.set_source_rgb(*BOCA_ESCURA); ctx.fill_preserve()
        ctx.save(); ctx.clip()
        ys = [q[1] for q in pts]
        if dentes_k or dentes in ("aparelho", "dentuco", "banguela", "separados"):
            alto = (max(ys) - min(ys)) * max(dentes_k, 0.22)
            ctx.rectangle(x - w * 2, min(ys) - 4, w * 4, alto + 4); ctx.set_source_rgb(1, 1, 1); ctx.fill()
            _dentes_abertos(ctx, dentes, x, min(ys), alto, w)
        if lingua:
            ctx.save(); ctx.translate(x + wob, max(ys) + 2); ctx.scale(w * 0.62, (max(ys) - min(ys)) * 0.42); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
            ctx.set_source_rgb(*LINGUA); ctx.fill()
        ctx.restore()
        if labios:   # contorno de lábio colorido por fora da boca aberta
            path_suave(ctx, p); ctx.set_line_width(13); ctx.set_source_rgb(*labios); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
        path_suave(ctx, p); ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()

    if labios and tipo in ("charme", "leve", "sorriso", "sorrisinho"):
        _labios(ctx, x, y, w, labios, seed, sorri={"sorrisinho": 0.4, "leve": 0.6}.get(tipo, 1.0))
        return
    if tipo == "charme":   # sorriso fechado confiante (sem lábio colorido)
        traco(ctx, [(x - w * 0.7, y + 1), (x - w * 0.2, y + 9), (x + w * 0.35, y + 6), (x + w * 0.82, y - 12)], lw=6.5, seed=seed, amp=0.3)
        return
    if tipo == "ofegante":   # boca aberta puxando ar, língua de fora
        hh = w * (0.42 + 0.14 * math.sin(t * 11))
        aberta([(x - w * 0.6, y - 4), (x, y - 12), (x + w * 0.6, y - 4)], [(x + w * 0.5, y + hh), (x, y + hh * 1.35), (x - w * 0.5, y + hh)], lingua=False)
        forma(ctx, pts_elipse(x + 6, y + hh * 1.35 + 12, 15, 17 + 3 * math.sin(t * 11), 10), LINGUA, sombra=False, lw=4, seed=seed + 5, amp=0.3)
        traco(ctx, [(x + 6, y + hh * 1.35 + 2), (x + 6, y + hh * 1.35 + 18)], lw=3, alpha=0.5, seed=seed + 6, amp=0.2)
        return
    if tipo == "sorriso_aberto":
        aberta([(x - w, y - 6), (x - w * 0.5, y - 2), (x, y - 1), (x + w * 0.5, y - 2), (x + w, y - 6)],
               [(x + w * 0.72, y + w * 0.42), (x, y + w * 0.78), (x - w * 0.72, y + w * 0.42)], dentes_k=0.3)
    elif tipo == "gargalhada":
        w2 = w * 1.35; sac = 3 * math.sin(t * 22)
        aberta([(x - w2, y - 10), (x, y - 4), (x + w2, y - 10)],
               [(x + w2 * 0.8, y + w2 * 0.55 + sac), (x, y + w2 * 1.0 + sac), (x - w2 * 0.8, y + w2 * 0.55 + sac)], dentes_k=0.22)
    elif tipo == "careta":
        pts = [(x - w, y + 6), (x - w * 0.6, y - 6), (x + w * 0.6, y - 6), (x + w, y + 6), (x + w * 0.6, y + 14), (x - w * 0.6, y + 14)]
        p = jitter(pts, 0.6, seed); path_suave(ctx, p); ctx.set_source_rgb(1, 1, 1); ctx.fill_preserve()
        ctx.save(); ctx.clip()
        _linha(ctx, [(x - w, y + 4), (x + w, y + 4)], 3.5, INK, 0.8)
        for k in (-0.5, 0, 0.5):
            _linha(ctx, [(x + k * w, y - 8), (x + k * w, y + 16)], 3.5, INK, 0.8)
        if dentes in ("aparelho", "banguela", "separados"):
            _dentes_abertos(ctx, dentes, x, y - 8, 12, w)
        ctx.restore(); path_suave(ctx, p); ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.stroke()
    elif tipo == "o":
        aberta([(x, y - w * 0.55), (x + w * 0.42, y - w * 0.1)], [(x + w * 0.3, y + w * 0.45), (x - w * 0.3, y + w * 0.45), (x - w * 0.42, y - w * 0.1)])
    elif tipo == "choro":
        wob = 3 * math.sin(t * 18)
        aberta([(x - w * 0.85, y + 12), (x, y - 8 + wob), (x + w * 0.85, y + 12)], [(x + w * 0.6, y + w * 0.75), (x - w * 0.6, y + w * 0.75)], wob=wob)
    elif tipo == "triste":
        traco(ctx, [(x - w * 0.7, y + 10), (x, y - 4), (x + w * 0.7, y + 10)], lw=6.5, seed=seed, amp=0.5)
    elif tipo == "ondulada":
        pts = [(x - w * 0.8 + i * w * 0.32, y + (5 if i % 2 else -4)) for i in range(6)]
        traco(ctx, pts, lw=6, seed=seed, amp=0.3)
    elif tipo == "sorrisinho":
        traco(ctx, [(x - w * 0.45, y + 1), (x - w * 0.15, y + 6), (x + w * 0.1, y + 3), (x + w * 0.45, y - 2)], lw=6, seed=seed, amp=0.3)
    elif tipo == "sorriso":
        traco(ctx, [(x - w * 0.8, y - 6), (x, y + 13), (x + w * 0.8, y - 6)], lw=6.5, seed=seed, amp=0.4)
    elif tipo == "cansado":
        traco(ctx, [(x - w * 0.5, y + 4), (x + w * 0.5, y + 1)], lw=6, seed=seed, amp=0.3)
        forma(ctx, pts_elipse(x + w * 0.1, y + 3, 7, 5, 8), BOCA_ESCURA, sombra=False, lw=4, seed=seed + 1, amp=0.3)
    else:   # leve: sorriso discreto
        traco(ctx, [(x - w * 0.6, y - 1), (x, y + 5), (x + w * 0.6, y - 1)], lw=6, seed=seed, amp=0.4)


def _barba(ctx, P, tipo, cor, my, w, seed):
    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    if tipo in (True, "cheia", "barba"):
        pts = [_hp(P, -0.98, 0.05), _hp(P, -0.92, 0.55), _hp(P, -0.55, 0.92), (0, hc + ry * 1.12), _hp(P, 0.55, 0.92), _hp(P, 0.92, 0.55), _hp(P, 0.98, 0.05),
               _hp(P, 0.8, 0.28), (w * 1.5, my - 8), (0, my - 16), (-w * 1.5, my - 8), _hp(P, -0.8, 0.28)]
        forma(ctx, pts, cor, sombra=False, lw=5, seed=seed, amp=0.9)
    elif tipo == "rala":   # sombra de barba por fazer, sem contorno
        pts = [_hp(P, -0.96, 0.3), _hp(P, -0.88, 0.62), _hp(P, -0.52, 0.94), (0, hc + ry * 1.04), _hp(P, 0.52, 0.94), _hp(P, 0.88, 0.62), _hp(P, 0.96, 0.3),
               _hp(P, 0.74, 0.62), (w * 1.3, my + 4), (0, my + 12), (-w * 1.3, my + 4), _hp(P, -0.74, 0.62)]
        path_suave(ctx, pts); ctx.set_source_rgba(*cor, 0.22); ctx.fill()
        return
    elif tipo == "bigodao":   # bigode de guidão com pontas enroladas
        for sx in (-1, 1):
            pts = [(0, my - 16), (sx * w * 0.7, my - 22), (sx * w * 1.6, my - 10), (sx * w * 2.0, my - 26), (sx * w * 2.15, my - 8), (sx * w * 1.6, my + 4), (sx * w * 0.6, my - 2), (0, my - 6)]
            forma(ctx, pts, cor, sombra=True, sombra_off=(4, 6), lw=5, seed=seed + 5 + sx, amp=0.6)
        return
    elif tipo == "cavanhaque":
        forma(ctx, [(-w * 0.9, my + 14), (w * 0.9, my + 14), (w * 0.5, hc + ry * 1.04), (-w * 0.5, hc + ry * 1.04)], cor, sombra=False, lw=5, seed=seed, amp=0.8)
    forma(ctx, [(-w * 1.25, my + 2), (-w * 0.5, my - 18), (0, my - 13), (w * 0.5, my - 18), (w * 1.25, my + 2), (w * 0.6, my - 6), (0, my - 6), (-w * 0.6, my - 6)],
          cor, sombra=False, lw=5, seed=seed + 1, amp=0.6)


def _nariz(ctx, tipo, x, ny, pele, crianca, seed):
    tom = escurece(pele, 0.12)
    if tipo not in (None, "normal", "bolinha") and not str(tipo).startswith("_"):
        f = 1.15 if tipo == "arrebitado" else 1.45
        ctx.save(); ctx.translate(x, ny); ctx.scale(f, f); ctx.translate(-x, -ny)
        _nariz(ctx, "_" + tipo, x, ny, pele, crianca, seed)
        ctx.restore(); return
    if isinstance(tipo, str) and tipo.startswith("_"):
        tipo = tipo[1:]
    if tipo == "bolinha" or (tipo is None and crianca):
        r = 9 if crianca and tipo is None else 15
        forma(ctx, pts_elipse(x, ny, r * 1.1, r, 10), tom, sombra=False, lw=0 if r < 10 else 4, seed=seed, amp=0.3)
        ctx.arc(x - r * 0.35, ny - r * 0.35, r * 0.28, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.55); ctx.fill()
    elif tipo == "batata":
        for sx in (-1, 1):
            forma(ctx, pts_elipse(x + sx * 17, ny + 6, 11, 10, 10), tom, sombra=False, lw=4, seed=seed + sx, amp=0.4)
        forma(ctx, pts_elipse(x, ny, 22, 20, 14), tom, sombra=True, sombra_off=(4, 5), lw=4.5, seed=seed + 2, amp=0.6)
        ctx.arc(x - 7, ny - 7, 5, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.5); ctx.fill()
    elif tipo == "pontudo":
        forma(ctx, [(x - 6, ny - 26), (x + 4, ny - 8), (x + 30, ny + 12), (x + 2, ny + 10), (x - 8, ny + 6)], pele, sombra=True, sombra_off=(4, 5), lw=4.5, seed=seed, amp=0.4)
    elif tipo == "adunco":
        forma(ctx, [(x - 4, ny - 28), (x + 12, ny - 12), (x + 20, ny + 4), (x + 12, ny + 16), (x + 4, ny + 8), (x - 8, ny + 8)], pele, sombra=True, sombra_off=(4, 5), lw=4.5, seed=seed, amp=0.4)
    elif tipo == "arrebitado":
        forma(ctx, [(x - 3, ny - 20), (x + 9, ny - 2), (x + 12, ny + 6), (x - 12, ny + 6), (x - 9, ny - 2)], pele, sombra=False, lw=4.5, seed=seed, amp=0.3)
        for sx in (-1, 1):
            ctx.save(); ctx.translate(x + sx * 5, ny + 2); ctx.scale(2.2, 3); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore(); ctx.set_source_rgba(*INK, 0.7); ctx.fill()
    else:
        traco(ctx, [(x - 3, ny - 18), (x + 7, ny), (x - 5, ny + 4)], lw=4.5, alpha=0.7, seed=seed, amp=0.4)


def _sob_feita(ctx, p0, pm, p2, cor, l0, l2):
    """Sobrancelha desenhada como forma afinando: p0 (dentro) -> pm (arco) -> p2 (ponta)."""
    cx, cy = 2 * pm[0] - (p0[0] + p2[0]) / 2, 2 * pm[1] - (p0[1] + p2[1]) / 2
    cima, baixo = [], []
    n = 10
    for i in range(n + 1):
        u = i / n
        x = (1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * cx + u * u * p2[0]
        y = (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * cy + u * u * p2[1]
        dx = 2 * (1 - u) * (cx - p0[0]) + 2 * u * (p2[0] - cx); dy = 2 * (1 - u) * (cy - p0[1]) + 2 * u * (p2[1] - cy)
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        if ny > 0:
            nx, ny = -nx, -ny
        larg = (l0 + (l2 - l0) * u ** 0.8) / 2
        cima.append((x + nx * larg, y + ny * larg)); baixo.append((x - nx * larg, y - ny * larg))
    path_suave(ctx, cima + list(reversed(baixo))); ctx.set_source_rgb(*cor); ctx.fill_preserve()
    ctx.set_source_rgba(*INK, 0.5); ctx.set_line_width(1.5); ctx.stroke()


def _rosto(ctx, P, st, t, seed, pele, cab):
    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    nome = st.get("expressao", "neutro")
    nome = nome if nome in EXPR else "neutro"
    e = EXPR[nome]
    prev, k = _troca(st, "expressao", t, 0.22)
    sob = e["sob"]
    if prev and prev in EXPR:
        sob = tuple(a + (b - a) * k for a, b in zip(EXPR[prev]["sob"], sob))
    crianca = P["idade"] == "crianca"
    if crianca:
        sob = tuple(v * 0.7 for v in sob)
    ex, erx, ery = P["olho"]
    ey = hc + (16 if crianca else 6)
    olhar = st.get("olhar") or e.get("olhar", "camera")
    look = LOOK.get(olhar, (0, 0))
    pv, kl = _troca(st, "olhar", t, 0.18)
    if pv:
        l0 = LOOK.get(pv, (0, 0)); look = (l0[0] + (look[0] - l0[0]) * kl, l0[1] + (look[1] - l0[1]) * kl)
    if nome == "nervoso":
        look = (look[0] + 0.5 * math.sin(t * 7.0), look[1])
    lid = st.get("palpebra")
    lid = e.get("lid", 0.1) if not isinstance(lid, (int, float)) else lid
    r = random.Random(seed)
    tt = r.uniform(0.4, 1.8)
    while tt < t + 1:   # piscar: a cada 2,2 a 3,6 s
        if tt <= t < tt + 0.13:
            lid = 1.0
        tt += r.uniform(2.2, 3.6)
    cor_lid = escurece(pele, 0.2)
    my = hc + ry * (0.52 if crianca else 0.56)
    # ASSINATURA: bochecha-grão (grãozinho de milho rosado em cada bochecha, sempre)
    corado = e.get("corado", 0.0) + (0.15 if crianca else 0.0) + (0.25 if st.get("blush") else 0.0)
    for sx in (-1, 1):
        cx, cy = sx * (ex + 20), ey + ery + 16
        if corado > 0.3:
            ctx.save(); ctx.translate(cx, cy); ctx.scale(30, 17); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
            ctx.set_source_rgba(*ROSADO, min(0.55, corado * 0.6)); ctx.fill()
        _grao(ctx, cx, cy, 24, 18, ROSADO, giro=-sx * 0.3, alpha=0.55 + min(0.35, corado * 0.4), contorno=0.25)
        if nome == "envergonhado":
            for i in (-1, 0, 1):
                x0 = cx + i * 13
                _linha(ctx, [(x0 + 5, cy - 10), (x0 - 5, cy + 6)], 3.5, escurece(ROSADO, 0.3), 0.8)
    if st.get("sardas"):
        cs = escurece(pele, 0.38)
        rr = random.Random(seed + 77)
        for sx in (-1, 1):
            for i in range(6):
                _grao(ctx, sx * (ex + rr.uniform(-6, 30)), ey + ery + rr.uniform(-2, 26), 10, 8, cs, giro=rr.uniform(-0.6, 0.6), alpha=0.75, contorno=0.0)
        for i in range(3):
            _grao(ctx, rr.uniform(-12, 12), ey + ery + 4 + rr.uniform(-6, 6), 9, 7, cs, giro=rr.uniform(-0.6, 0.6), alpha=0.75, contorno=0.0)
    estilo_sob = st.get("sobrancelha") if isinstance(st.get("sobrancelha"), str) else "normal"
    lw_sob = {"fina": 4.5, "grossa": 16, "monocelha": 15}.get(estilo_sob, 8.5 if not crianca else 7.5)
    cb = mix(cab, INK, 0.45) if st.get("cabelo") not in ("careca",) else mix(cab, INK, 0.6)
    pontas = []
    for sx in (-1, 1):
        _olho(ctx, sx * ex, ey, erx, ery, sx, look, e, lid, cor_lid, seed + 3 + sx, iris=_cor(st["iris"], "#7A4A2A") if st.get("iris") else None)
        if st.get("cilios") == "longos" and not e.get("fecha") and lid < 0.95:   # delineado com gatinho + 3 cílios curvos
            g = e.get("grande", 1.0)
            cx_, rx_, ry_ = sx * ex, erx * g, ery * g
            topo = [(cx_ + sx * rx_ * math.cos(a), ey - ry_ * math.sin(a)) for a in [math.pi * (0.92 - 0.84 * i / 8) for i in range(9)]]
            _linha(ctx, topo + [(cx_ + sx * (rx_ + 17), ey - ry_ * 0.62)], 7, INK)
            yl = ey - ry_ + 2 * ry_ * max(0.05, lid)
            for i, f in enumerate((0.45, 0.72, 0.93)):
                x0 = cx_ + sx * rx_ * f
                y0 = ey - ry_ * math.sqrt(max(0.0, 1 - f * f)) - 2
                c = 9 + 3 * i
                traco(ctx, [(x0, y0), (x0 + sx * c * 0.35, y0 - c * 0.8), (x0 + sx * c * 0.95, y0 - c * 1.0)], lw=4.5, seed=seed + 60 + i + sx, amp=0.15)
        elif st.get("cilios") and not e.get("fecha") and lid < 0.95:
            g = e.get("grande", 1.0)
            yl = ey - ery * g + 2 * ery * g * max(0.05, lid)
            for i, f in enumerate((0.55, 0.85)):
                x0 = sx * ex + sx * erx * g * f
                ang = -1.9 + 0.4 * i if sx < 0 else -1.24 - 0.4 * i
                traco(ctx, [(x0, yl), (x0 + math.cos(ang) * 14, yl + math.sin(ang) * 14)], lw=4.5, seed=seed + 60 + i + sx, amp=0.2)
        xi, xo = sx * ex - sx * (erx + 2), sx * ex + sx * (erx + 8)
        by = ey - ery * e.get("grande", 1.0) - (10 if st.get("olhos") == "grandes" else 16) - (4 if estilo_sob == "grossa" else 0)
        if estilo_sob in ("arqueada", "marcada"):   # bem feita: grossa por dentro, arco alto, ponta fina
            _sob_feita(ctx, (xi, by + sob[0]), (sx * ex + sx * erx * 0.35, by + sob[1] - (9 if estilo_sob == "arqueada" else 5)), (xo + sx * 4, by + sob[2] + 4),
                       cb, 11 if estilo_sob == "arqueada" else 15, 3 if estilo_sob == "arqueada" else 6)
        else:
            traco(ctx, [(xo, by + sob[2]), (sx * ex, by + sob[1] - 3), (xi, by + sob[0])], lw=lw_sob, cor=cb, seed=seed + 10 + sx, amp=0.6)
        pontas.append((xi, by + sob[0]))
        if e.get("olheira") or st.get("olheiras"):
            for j in (0, 1):
                traco(ctx, [(sx * ex - erx, ey + ery + 5 + j * 7), (sx * ex, ey + ery + 10 + j * 7), (sx * ex + erx, ey + ery + 5 + j * 7)],
                      lw=3.5, cor=hexc("#6A4B7A"), alpha=0.55 - j * 0.2, seed=seed + 14 + sx + j, amp=0.3)
        if P["idade"] == "idoso":
            for i in (-1, 1):
                traco(ctx, [(sx * (ex + erx + 6), ey + i * 4), (sx * (ex + erx + 18), ey + i * 10)], lw=3, alpha=0.5, seed=seed + 16 + i + sx, amp=0.3)
    if estilo_sob == "monocelha":
        (x0, y0), (x1, y1) = pontas
        traco(ctx, [(x0 - 2, y0), (0, (y0 + y1) / 2 + 2), (x1 + 2, y1)], lw=lw_sob - 1, cor=cb, seed=seed + 13, amp=0.4)
    ny = ey + (20 if crianca else 30)
    _nariz(ctx, st.get("nariz"), 0, ny, pele, crianca, seed + 20)
    if P["idade"] == "idoso":
        for sx in (-1, 1):
            traco(ctx, [(sx * 20, ny + 4), (sx * 30, my - 2), (sx * 32, my + 8)], lw=3, alpha=0.45, seed=seed + 22 + sx, amp=0.3)
        for i in range(2):
            traco(ctx, [(-28, hc - ry * 0.48 + i * 11), (0, hc - ry * 0.51 + i * 11), (28, hc - ry * 0.48 + i * 11)], lw=3, alpha=0.4, seed=seed + 25 + i, amp=0.4)
    w = 30 if not crianca else 26
    dentes = st.get("dentes", "normal")
    if st.get("barba") and not crianca:
        _barba(ctx, P, st.get("barba"), mix(cab, INK, 0.15), my, w, seed + 30)
    boca = e.get("boca", "leve")
    labios = _cor(st["labios"], "#D8506A") if st.get("labios") else None
    _boca(ctx, boca, 0, my, w, t, seed + 40, dentes, labios)
    if boca in ("leve", "sorriso", "sorrisinho", "triste", "ondulada", "cansado") and not labios:
        _dentes_fechada(ctx, dentes, 0, my + (4 if boca != "sorriso" else 8), w)
    pinta = st.get("pinta")
    if pinta:
        sx = -1 if pinta == "esq" else 1
        ctx.arc(sx * (w * 1.25), my - 16, 4.5, 0, 2 * math.pi); ctx.set_source_rgb(*escurece(pele, 0.6)); ctx.fill()
    return my, w, boca


def _extras(ctx, P, st, t):
    """Lágrimas, gota de suor, corações, veia de bravo, riscos de susto: por cima do cabelo."""
    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    nome = st.get("expressao", "neutro")
    crianca = P["idade"] == "crianca"
    ex, erx, ery = P["olho"]
    ey = hc + (16 if crianca else 6)
    seed = 0
    if st.get("veia"):   # veia saltando na testa, pulsando
        k = 1 + 0.12 * math.sin(t * 9)
        x0, y0 = rx * 0.34, hc - ry * 0.5
        cv = hexc("#7A4FD1") if not isinstance(st.get("veia"), str) else _cor(st.get("veia"), "#7A4FD1")
        for pts in ([(0, 34), (2, 12), (-4, -6), (0, -24)], [(-4, -6), (-18, -18)], [(2, 12), (16, 2)]):
            _linha(ctx, [(x0 + u * k, y0 + v * k) for u, v in pts], 11, INK, 0.9)
            _linha(ctx, [(x0 + u * k, y0 + v * k) for u, v in pts], 6, cv)
    if st.get("suor"):   # gotas de suor voando da cabeça
        for i in range(3):
            u = (t * 1.1 + i / 3) % 1.0
            sx = 1 if i % 2 == 0 else -1
            ang = -math.pi / 2 + sx * (0.7 + 0.25 * i)
            d = ry * (1.05 + 0.7 * u)
            ctx.push_group(); _gota(ctx, math.cos(ang) * d, hc + math.sin(ang) * d, 11 - 4 * u); ctx.pop_group_to_source(); ctx.paint_with_alpha(1 - u * u)
        _gota(ctx, -rx * 0.9, hc - ry * 0.2 + ((t * 0.6) % 1.0) * 50, 10)
    if nome == "chorando":
        for sx in (-1, 1):
            x = sx * ex
            traco(ctx, [(x, ey + 6), (x + sx * 4, ey + 46), (x + sx * 2, hc + ry * 0.95)], lw=13, cor=AGUA, alpha=0.85, seed=seed + 50 + sx, amp=0.4)
            u = ((t * 1.6 + (0.5 if sx > 0 else 0)) % 1.0)
            _gota(ctx, x + sx * (18 + 30 * u), ey + 18 + u * 120, 9 - 3 * u)
    elif nome == "nervoso":
        u = (t * 0.7) % 1.0
        _gota(ctx, rx * 0.95, hc - ry * 0.45 + u * 70, 13)
    elif nome == "apaixonado":
        for i in (0, 1):
            u = (t * 0.5 + i * 0.5) % 1.0
            ctx.save(); ctx.translate((rx + 26) * (1 if i else -1), hc - ry * 0.7 - u * 90)
            a = 1 - u
            ctx.push_group(); _coracao(ctx, 0, 0, 16, hexc("#FF3D6E")); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
            ctx.restore()
    elif nome == "bravo":
        x, y = _fcab(P, math.radians(-48)); x, y = x * 0.66, hc + y * 0.66
        for a in range(4):
            ang = a * math.pi / 2 + 0.78
            _linha(ctx, [(x + math.cos(ang) * 5, y + math.sin(ang) * 5), (x + math.cos(ang) * 17, y + math.sin(ang) * 17)], 6, VERMELHO)
    elif nome == "surpreso":
        for i, a in enumerate((-0.45, 0, 0.45)):
            ang = -math.pi / 2 + a
            r0 = ry * 1.25
            _linha(ctx, [(math.cos(ang) * r0 * 0.9, hc + math.sin(ang) * r0), (math.cos(ang) * (r0 + 30) * 0.9, hc + math.sin(ang) * (r0 + 30))], 7, INK)




# ======================================================================== acessórios
def _oculos(ctx, P, cor, tipo="redondo"):
    ex, erx, ery = P["olho"]
    ey = P["hc"] + (16 if P["idade"] == "crianca" else 6)
    if tipo == "ponta":   # meia-lua na ponta do nariz, olhando por cima
        y = ey + ery + 22
        for sx in (-1, 1):
            ctx.move_to(sx * 10, y - 8); ctx.line_to(sx * 46, y - 8); ctx.curve_to(sx * 46, y + 14, sx * 10, y + 14, sx * 10, y - 8); ctx.close_path()
            ctx.set_source_rgba(0.85, 0.95, 1, 0.3); ctx.fill_preserve(); ctx.set_line_width(5); ctx.set_source_rgb(*cor); ctx.stroke()
            _linha(ctx, [(sx * 46, y - 8), (sx * (P["rx"] - 4), ey - 4)], 4, cor)
        _linha(ctx, [(-10, y - 8), (0, y - 12), (10, y - 8)], 4, cor)
        return
    if tipo == "escuro":   # óculos escuros de galã
        for sx in (-1, 1):
            pts = [(sx * (ex - erx - 10), ey - ery - 4), (sx * (ex + erx + 12), ey - ery - 6), (sx * (ex + erx + 8), ey + ery * 0.6), (sx * (ex), ey + ery + 6), (sx * (ex - erx - 8), ey + ery * 0.4)]
            forma(ctx, pts, hexc("#1B1726"), sombra=False, lw=5, seed=11 + sx, amp=0.3)
            _linha(ctx, [(sx * (ex - erx * 0.4), ey - ery * 0.5), (sx * (ex + erx * 0.3), ey + ery * 0.2)], 4, (1, 1, 1), 0.55)
            _linha(ctx, [(sx * (ex + erx + 12), ey - ery - 4), (sx * (P["rx"] - 2), ey - 10)], 5, INK)
        _linha(ctx, [(-(ex - erx - 10), ey - ery), (0, ey - ery - 4), (ex - erx - 10, ey - ery)], 5, INK)
        return
    grosso = tipo == "fundo_de_garrafa"
    r = ery + (12 if grosso else 9)
    for sx in (-1, 1):
        ctx.arc(sx * ex, ey, r, 0, 2 * math.pi); ctx.set_source_rgba(0.85, 0.95, 1, 0.22); ctx.fill_preserve()
        ctx.set_line_width(10 if grosso else 5.5); ctx.set_source_rgb(*cor); ctx.stroke()
        if grosso:   # anéis de lente grossa
            for f in (0.82, 0.66):
                ctx.arc(sx * ex, ey, r * f, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(2.5); ctx.stroke()
        _linha(ctx, [(sx * (ex + r), ey - 4), (sx * (P["rx"] - 2), ey - 8)], 5, cor)
        _linha(ctx, [(sx * ex - 8, ey - r * 0.5), (sx * ex + 2, ey - r * 0.65)], 3.5, (1, 1, 1), 0.8)
    _linha(ctx, [(-ex + r, ey - 2), (0, ey - 7), (ex - r, ey - 2)], 5, cor)


def _estrela(ctx, x, y, r, cor=(1, 1, 0.85)):
    ctx.move_to(x, y - r)
    for a in range(4):
        ang = -math.pi / 2 + a * math.pi / 2
        ang2 = ang + math.pi / 4
        ctx.line_to(x + math.cos(ang2) * r * 0.28, y + math.sin(ang2) * r * 0.28)
        ctx.line_to(x + math.cos(ang + math.pi / 2) * r, y + math.sin(ang + math.pi / 2) * r)
    ctx.close_path(); ctx.set_source_rgb(*cor); ctx.fill_preserve(); ctx.set_line_width(3); ctx.set_source_rgb(*INK); ctx.stroke()


def _brilho_gala(ctx, P, nivel, t, my, w, boca, seed):
    """Aura de galã: estrelinhas piscando em volta da cabeça e dente que brilha."""
    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    sutil = nivel == "sutil"
    pos = [(-1.3, -0.8), (1.35, -0.55), (-1.25, 0.5), (1.2, 0.75)][:2 if sutil else 4]
    for i, (u, v) in enumerate(pos):
        k = abs(math.sin(t * (2.2 if sutil else 3.5) + i * 1.7))
        if k > 0.15:
            _estrela(ctx, u * rx, hc + v * ry, (12 if sutil else 20) * k)
    if not sutil:
        k = abs(math.sin(t * 2.6 + 0.6))
        x, y = (w * 0.35, my + 8) if boca in ("sorriso_aberto", "gargalhada") else (w * 0.7, my - 2)
        if k > 0.3:
            _estrela(ctx, x, y, 16 * k, (1, 1, 1))


def _jaqueta(ctx, P, cor, seed):
    """Jaqueta/blazer aberto por cima da roupa: duas abas com lapela."""
    ow, cw, hw, sy, hy, nw = P["ow"], P["cw"], P["hw"], P["sy"], P["hy"], P["nw"]
    meio = (sy + hy) / 2
    for sx in (-1, 1):
        pts = [(nw + 6, sy - 6), (ow * 0.72, sy - 2), (ow * 0.97, sy + 16), (ow, sy + 44), (ow * 0.9, sy + 96), (cw, meio + 22), (hw, hy + 6), (hw * 0.96, hy + 28),
               (cw * 0.36, hy + 30), (cw * 0.3, meio + 10), (nw * 0.7, sy + 70), (nw + 26, sy + 34), (nw + 10, sy + 24)]
        forma(ctx, [(sx * x, y) for x, y in pts], cor, sombra=False, sombreado=0.1, seed=seed + sx, amp=0.6)
        traco(ctx, [(sx * (nw + 10), sy + 24), (sx * (nw + 26), sy + 34), (sx * nw * 0.7, sy + 70)], lw=3.5, alpha=0.6, seed=seed + 3 + sx, amp=0.3)
        _linha(ctx, [(sx * cw * 0.55, meio + 40), (sx * cw * 0.85, meio + 40)], 4, escurece(cor, 0.3))


def _colar(ctx, P, cor, seed):
    sy, nw = P["sy"], P["nw"]
    pts = [(-nw - 2, sy - 6), (-nw * 0.6, sy + 18), (0, sy + 30), (nw * 0.6, sy + 18), (nw + 2, sy - 6)]
    _linha(ctx, pts, 7, INK, 0.6); _linha(ctx, pts, 4, cor)
    forma(ctx, [(0, sy + 28), (9, sy + 40), (0, sy + 52), (-9, sy + 40)], cor, sombra=False, lw=3.5, seed=seed, amp=0.2)
    ctx.arc(-2, sy + 37, 2.5, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.9); ctx.fill()


def _brincos(ctx, P, cor, tipo, t):
    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    for sx in (-1, 1):
        ex = abs(_fcab(P, 0.15 if sx > 0 else math.pi - 0.15)[0])
        x, y = sx * (ex - 4), hc + 34
        if tipo == "brilhante":   # pontinho de brilhante com faísca
            forma(ctx, pts_elipse(x, y, 8, 8, 8), (0.92, 0.97, 1.0), sombra=False, lw=3.5, seed=3 + sx, amp=0.1)
            k = abs(math.sin(t * 3 + sx))
            if k > 0.4:
                _estrela(ctx, x + sx * 10, y - 10, 11 * k, (1, 1, 1))
        else:   # argola
            bal = 0.15 * math.sin(t * 2.4 + sx)
            ctx.save(); ctx.translate(x, y); ctx.rotate(bal)
            ctx.arc(0, 16, 15, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.set_line_width(9); ctx.stroke()
            ctx.arc(0, 16, 15, 0, 2 * math.pi); ctx.set_source_rgb(*cor); ctx.set_line_width(4.5); ctx.stroke()
            ctx.restore()


def _garrafa(ctx, x, y, cor, t, seed):
    """Garrafinha GIGANTE de academia (galão de 2 L) segura pela alça."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(-0.12)
    forma(ctx, pts_ret(-44, -190, 88, 230, 30), (0.78, 0.92, 1.0), sombra=True, lw=5, seed=seed, amp=0.5)
    ctx.save(); path_suave(ctx, pts_ret(-44, -190, 88, 230, 30)); ctx.clip()
    nivel = -60 + 6 * math.sin(t * 4)
    ctx.rectangle(-60, nivel, 120, 120); ctx.set_source_rgba(*cor, 0.85); ctx.fill()
    for i in range(3):
        yy = -150 + i * 40
        _linha(ctx, [(-44, yy), (-28, yy)], 4, INK, 0.5)
    ctx.restore()
    forma(ctx, pts_ret(-30, -226, 60, 40, 12), hexc("#2B2440"), sombra=False, lw=5, seed=seed + 1, amp=0.4)
    forma(ctx, pts_ret(-44, -40, 88, 34, 8), hexc("#FFD21F"), sombra=False, lw=4, seed=seed + 2, amp=0.3)
    _linha(ctx, [(-24, -172), (-24, -84)], 8, (1, 1, 1), 0.7)
    ctx.restore()


def _relogio(ctx, x, y, ang, cor):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    forma(ctx, pts_ret(-30, -16, 26, 32, 6), cor, sombra=False, lw=4.5, seed=4, amp=0.2)
    forma(ctx, pts_ret(-26, -12, 18, 24, 5), hexc("#1B1726"), sombra=False, lw=3, seed=5, amp=0.1)
    _linha(ctx, [(-22, 0), (-16, -6), (-12, 4)], 2.5, hexc("#7CFF6B"))
    ctx.restore()


def _numero(ctx, P, txt, seed):
    """Número de peito de corrida (preso com alfinetes)."""
    from estilo import texto
    sy, hy = P["sy"], P["hy"]
    y = sy + (hy - sy) * 0.5
    forma(ctx, pts_ret(-62, y - 44, 124, 88, 8), BRANCO, sombra=False, lw=4.5, seed=seed, amp=0.4)
    _linha(ctx, [(-62, y - 28), (62, y - 28)], 6, hexc("#E8352A"))
    texto(ctx, str(txt), 0, y + 10, 46, cor=INK, contorno=None, sombra=False, lw=0)
    for sx in (-1, 1):
        for sy_ in (-1, 1):
            ctx.arc(sx * 50, y + sy_ * 34, 3.5, 0, 2 * math.pi); ctx.set_source_rgb(*hexc("#B8BDD0")); ctx.fill()


def _faixa(ctx, P, cor):
    pts = [_hp(P, u, v) for u, v in ((-1.04, -0.5), (-0.5, -0.62), (0.0, -0.64), (0.5, -0.62), (1.04, -0.5))]
    _linha(ctx, pts, 28, INK); _linha(ctx, pts, 18, cor)
    _linha(ctx, [(p[0], p[1]) for p in pts], 4, clareia(cor, 0.5), 0.6)


def _pochete(ctx, P, cor, seed):
    hw, hy = P["hw"], P["hy"]
    _linha(ctx, [(-hw * 1.02, hy - 18), (0, hy - 8), (hw * 1.02, hy - 18)], 10, INK); _linha(ctx, [(-hw * 1.02, hy - 18), (0, hy - 8), (hw * 1.02, hy - 18)], 5, escurece(cor, 0.3))
    forma(ctx, pts_ret(hw * 0.05, hy - 34, hw * 0.85, 46, 18), cor, sombra=True, sombra_off=(5, 6), lw=5, seed=seed, amp=0.5)
    _linha(ctx, [(hw * 0.15, hy - 20), (hw * 0.8, hy - 20)], 3, INK, 0.7)


def _estampa(ctx, P, tipo, roupa, seed):
    """Estampa da camisa, dentro do contorno do tronco (o clip já está ativo)."""
    ow, sy, hy = P["ow"], P["sy"], P["hy"]
    if tipo == "listras":
        for k in range(0, 12):
            y = sy + 10 + k * 26
            ctx.rectangle(-ow - 20, y, 2 * ow + 40, 11)
        ctx.set_source_rgba(*escurece(roupa, 0.3), 0.8); ctx.fill()
    elif tipo == "xadrez":
        for k in range(-6, 7):
            ctx.rectangle(k * 36 - 7, sy - 20, 14, hy - sy + 80)
        for k in range(0, 10):
            ctx.rectangle(-ow - 20, sy + k * 36, 2 * ow + 40, 14)
        ctx.set_source_rgba(*escurece(roupa, 0.35), 0.45); ctx.fill()
    elif tipo == "natal":   # camisa natalina: faixa de zigue-zague, pinheirinhos e flocos
        yb = (sy + hy) / 2 - 8
        ctx.rectangle(-ow - 20, yb - 18, 2 * ow + 40, 36); ctx.set_source_rgb(*BRANCO); ctx.fill()
        zz = [(-ow - 20 + i * 18, yb + (8 if i % 2 else -8)) for i in range(int((2 * ow + 40) / 18) + 2)]
        _linha(ctx, zz, 6, hexc("#1E8A3C"))
        for i, x in enumerate(range(int(-ow), int(ow) + 1, 56)):
            for y0 in (sy + 40, hy - 20):
                xx = x + (28 if y0 > yb else 0)
                if i % 2 == 0 or y0 > yb:
                    ctx.move_to(xx, y0 - 18); ctx.line_to(xx + 13, y0 + 8); ctx.line_to(xx - 13, y0 + 8); ctx.close_path()
                    ctx.set_source_rgb(*hexc("#1E8A3C")); ctx.fill()
                else:
                    for a in range(3):
                        ang = a * math.pi / 3
                        _linha(ctx, [(xx - math.cos(ang) * 9, y0 - math.sin(ang) * 9), (xx + math.cos(ang) * 9, y0 + math.sin(ang) * 9)], 3.5, BRANCO)
    elif tipo == "havaiana":   # florzinhas grandes
        r = random.Random(seed)
        for y in range(int(sy) + 10, int(hy) + 40, 62):
            for x in range(int(-ow), int(ow) + 40, 70):
                xx, yy = x + r.uniform(-12, 12) + (35 if (y // 62) % 2 else 0), y + r.uniform(-8, 8)
                cor = hexc(r.choice(["#FFF3E0", "#FFD21F", "#FF5A8A"]))
                for a in range(5):
                    ang = a * 2 * math.pi / 5
                    ctx.new_sub_path(); ctx.arc(xx + math.cos(ang) * 10, yy + math.sin(ang) * 10, 8, 0, 2 * math.pi)
                ctx.set_source_rgb(*cor); ctx.fill()
                ctx.arc(xx, yy, 5, 0, 2 * math.pi); ctx.set_source_rgb(*hexc("#E8452C")); ctx.fill()


def _bone(ctx, P, cor, seed):
    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    cupula = _arco(P, 186, 354, 1.1, 12) + [_hp(P, 1.06, -0.4), _hp(P, 0, -0.5), _hp(P, -1.06, -0.4)]
    forma(ctx, cupula, cor, sombra=False, sombreado=0.12, seed=seed, amp=0.8)
    traco(ctx, [(0, hc - ry * 1.1), (0, hc - ry * 0.42)], lw=3.5, alpha=0.5, seed=seed + 1)
    forma(ctx, pts_elipse(0, hc - ry * 1.1, 10, 7, 8), escurece(cor, 0.2), sombra=False, lw=4, seed=seed + 2)
    ctx.save(); ctx.translate(0, hc - ry * 0.36); ctx.scale(rx * 0.95, 20); ctx.arc(0, 0, 1, 0, math.pi); ctx.restore()
    ctx.set_source_rgba(*INK, 0.25); ctx.fill()   # sombra da aba na testa
    aba = [_hp(P, -0.98, -0.42), _hp(P, -0.5, -0.5), _hp(P, 0.5, -0.5), _hp(P, 0.98, -0.42), _hp(P, 0.86, -0.3), _hp(P, 0.45, -0.22), _hp(P, 0.0, -0.2), _hp(P, -0.45, -0.22), _hp(P, -0.86, -0.3)]
    forma(ctx, aba, escurece(cor, 0.2), sombra=False, seed=seed + 3, amp=0.5)


def _fone(ctx, P, cor, seed):
    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    arco = _arco(P, 190, 350, 1.2, 10)
    _linha(ctx, arco, 20, INK); _linha(ctx, arco, 10, cor)
    for sx in (-1, 1):
        forma(ctx, pts_ret(sx * (rx + 6) - 22, hc - 36, 44, 72, 18), cor, sombra=True, sombra_off=(5, 7), lw=5, seed=seed + sx, amp=0.6)
        forma(ctx, pts_ret(sx * (rx + 6) - 10 - sx * 10, hc - 26, 20, 52, 10), escurece(cor, 0.35), sombra=False, lw=0, seed=seed + 3 + sx, amp=0.4)


def _mochila_tras(ctx, P, cor, seed):
    ow, sy, hy = P["ow"], P["sy"], P["hy"]
    forma(ctx, pts_ret(-ow - 22, sy - 10, 2 * ow + 44, (hy - sy) * 0.85, 40), cor, sombreado=0.1, seed=seed, amp=1)


def _mochila_alcas(ctx, P, cor, seed):
    ow, sy, hy = P["ow"], P["sy"], P["hy"]
    for sx in (-1, 1):
        pts = [(sx * ow * 0.52, sy - 2), (sx * ow * 0.62, sy + (hy - sy) * 0.45), (sx * ow * 0.8, sy + (hy - sy) * 0.72)]
        _linha(ctx, pts, 26, INK); _linha(ctx, pts, 16, escurece(cor, 0.1))


def _avental(ctx, P, cor, seed):
    ow, cw, hw, sy, hy, nw = P["ow"], P["cw"], P["hw"], P["sy"], P["hy"], P["nw"]
    y0 = sy + (hy - sy) * 0.22
    pts = [(-cw * 0.62, y0), (cw * 0.62, y0), (cw * 0.68, y0 + 40), (hw * 0.92, hy + 10), (hw * 0.95, hy + 70), (-hw * 0.95, hy + 70), (-hw * 0.92, hy + 10), (-cw * 0.68, y0 + 40)]
    for sx in (-1, 1):
        _linha(ctx, [(sx * cw * 0.55, y0 + 4), (sx * (nw + 6), sy - 2)], 9, INK); _linha(ctx, [(sx * cw * 0.55, y0 + 4), (sx * (nw + 6), sy - 2)], 3, cor)
    forma(ctx, pts, cor, sombra=True, sombra_off=(5, 7), seed=seed, amp=0.8)
    forma(ctx, pts_ret(-cw * 0.4, hy - 30, cw * 0.8, 50, 10), escurece(cor, 0.08), sombra=False, lw=4, seed=seed + 1, amp=0.5)
    _linha(ctx, [(-cw * 0.68, (y0 + hy) / 2 + 20), (cw * 0.68, (y0 + hy) / 2 + 20)], 7, escurece(cor, 0.25))


def _gravata(ctx, P, cor, seed):
    sy, hy, nw = P["sy"], P["hy"], P["nw"]
    for sx in (-1, 1):
        forma(ctx, [(sx * 2, sy - 4), (sx * (nw + 22), sy - 10), (sx * (nw + 10), sy + 26)], BRANCO, sombra=False, lw=4.5, seed=seed + sx, amp=0.4)
    forma(ctx, [(-12, sy + 6), (12, sy + 6), (8, sy + 22), (-8, sy + 22)], escurece(cor, 0.15), sombra=False, lw=4.5, seed=seed + 3, amp=0.3)
    ln = (hy - sy) * 0.72
    forma(ctx, [(-8, sy + 20), (8, sy + 20), (20, sy + ln - 22), (0, sy + ln), (-20, sy + ln - 22)], cor, sombra=True, sombra_off=(5, 7), lw=4.5, seed=seed + 4, amp=0.4)


# ======================================================================== corpo
def _pernas(ctx, P, ks, calca, sapato, seed):
    """Em pé: pernas retas com vão no meio. Sentado: coxas em 3/4 para a direita da tela (joelhos de lado), canelas descendo."""
    hy, hw, pw, chao, dq = P["hy"], P["hw"], P["pw"], P["chao"], P["queda"] * ks
    coxa = (chao - hy) * 0.42
    out = []
    for sx in (-1, 1):
        Hs = (sx * hw * 0.5, hy); Ks = (sx * (hw * 0.5 + 2 + P["joelho"]), hy + (chao - hy) * 0.5); As = (sx * (hw * 0.5 + 4), chao - 10)
        perto = sx > 0
        Hd = (sx * hw * 0.42, hy + P["queda"]); Kd = (hw * 0.5 + coxa + (14 if perto else -10), hy + P["queda"] + (14 if perto else -2))
        Ad = (Kd[0] + 8, chao - 10)
        L = lambda a, b: (a[0] + (b[0] - a[0]) * ks, a[1] + (b[1] - a[1]) * ks)
        out.append((sx, L(Hs, Hd), L(Ks, Kd), L(As, Ad)))
    if ks < 0.25:   # em pé: as duas pernas num traço só cada
        for (_, Hh, Kk, Aa) in out:
            ctx.save(); ctx.translate(9, 11); _linha(ctx, [Hh, Kk, Aa], pw * 2 + 10, INK, 0.28); ctx.restore()
        for (_, Hh, Kk, Aa) in out:
            _linha(ctx, [Hh, Kk, Aa], pw * 2 + 10, INK)
        forma(ctx, pts_ret(-hw, hy - 30, 2 * hw, 60, 24), calca, sombra=False, lw=LW, seed=seed + 1, amp=0.6)
        for (_, Hh, Kk, Aa) in out:
            _linha(ctx, [Hh, Kk, Aa], pw * 2, calca)
    else:   # sentado: perna de trás primeiro; canela, depois coxa por cima
        forma(ctx, pts_ret(-hw, hy + dq - 30, 2 * hw, 60, 24), calca, sombra=False, lw=LW, seed=seed + 1, amp=0.6)
        for (sx, Hh, Kk, Aa) in out:
            _tubo(ctx, [Kk, Aa], pw * 2, calca)
            forma(ctx, pts_elipse(Aa[0] + 18, chao + 4, pw + 22, 18, 14), sapato, sombra=True, sombra_off=(6, 6), lw=5, seed=seed + 5 + sx, amp=0.6)
            _tubo(ctx, [Hh, Kk], pw * 2 + 4, calca, sombra=(sx > 0))
        return
    for sx, Hh, Kk, Aa in out:
        if P.get("chuteira"):
            for k in (-0.6, 0.0, 0.6):
                ctx.rectangle(Aa[0] + sx * 10 + k * (pw + 6) - 4, chao + 14, 8, 12)
            ctx.set_source_rgb(*INK); ctx.fill()
        forma(ctx, pts_elipse(Aa[0] + sx * 10, chao + 4, pw + 16, 18, 14), sapato, sombra=True, sombra_off=(6, 6), lw=5, seed=seed + 5 + sx, amp=0.6)
        traco(ctx, [(Aa[0] + sx * 10 - pw * 0.5, chao - 6), (Aa[0] + sx * 10 + pw * 0.3, chao - 9)], lw=4, cor=clareia(sapato, 0.4), seed=seed + 8 + sx, amp=0.3)


def _banco(ctx, P, ks, seed):
    if ks < 0.05:
        return
    hy, hw, chao, dq = P["hy"], P["hw"], P["chao"], P["queda"]
    s = ease_out_back(clamp(ks * 1.3), 1.6)
    ctx.save(); ctx.translate(0, chao); ctx.scale(1, max(0.01, s)); ctx.translate(0, -chao)
    madeira = hexc("#C8844A")
    for sx in (-1, 1):
        forma(ctx, pts_ret((hw + 14 if sx < 0 else hw + 40) * sx - 12, hy + dq + 20, 24, chao - (hy + dq + 20) - 4, 8), escurece(madeira, 0.15), sombra=True, lw=5, seed=seed + sx, amp=0.6)
    forma(ctx, pts_ret(-hw - 30, hy + dq + 4, 2 * hw + 110, 34, 14), madeira, sombra=True, lw=5, seed=seed + 3, amp=0.6)
    ctx.restore()


def _tronco(ctx, P, roupa, pele, seed, estampa=None):
    ow, cw, hw, sy, hy, nw = P["ow"], P["cw"], P["hw"], P["sy"], P["hy"], P["nw"]
    meio = (sy + hy) / 2
    lado = [(nw + 6, sy - 6), (ow * 0.72, sy - 2), (ow * 0.97, sy + 16), (ow, sy + 44), (ow * 0.9, sy + 96), (cw, meio + 22), (hw, hy + 6), (hw * 0.96, hy + 26)]
    pts = lado + [(0, hy + 30)] + [(-x, y) for x, y in reversed(lado)] + [(0, sy + 2)]
    forma(ctx, pts, roupa, sombreado=0.13, seed=seed, amp=1.2)
    if estampa:
        ctx.save(); path_suave(ctx, pts); ctx.clip()
        _estampa(ctx, P, estampa, roupa, seed)
        ctx.restore()
        path_suave(ctx, jitter(pts, 1.2, seed)); ctx.set_line_width(LW); ctx.set_source_rgb(*INK); ctx.stroke()
    forma(ctx, [(-nw - 2, sy - 6), (0, sy + 20), (nw + 2, sy - 6)], pele, sombra=False, lw=4.5, seed=seed + 1, amp=0.4)
    traco(ctx, [(-hw * 0.9, hy + 18), (0, hy + 24), (hw * 0.9, hy + 18)], lw=3, alpha=0.35, seed=seed + 2, amp=0.4)


def _cabeca(ctx, P, pele, seed, orelhas="normal"):
    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    abano = orelhas == "abano"
    for sx in (-1, 1):   # orelhas (metade escondida atrás da cabeça)
        ex = abs(_fcab(P, 0.15 if sx > 0 else math.pi - 0.15)[0])
        if abano:
            x, y = sx * (ex + 10), hc + 4
            ctx.save(); ctx.translate(x, y); ctx.rotate(sx * 0.35)
            forma(ctx, pts_elipse(0, 0, 24, 34, 12), pele, sombra=True, sombra_off=(5, 6), lw=5, seed=seed + 9 + sx, amp=0.6)
            traco(ctx, [(sx * -2, -18), (sx * 10, 0), (sx * -2, 16)], lw=4, alpha=0.5, seed=seed + 12 + sx, amp=0.3)
            ctx.restore()
        else:
            x, y = sx * (ex - 6), hc + 10
            forma(ctx, pts_elipse(x, y, 17, 22, 10), pele, sombra=False, lw=5, seed=seed + 9 + sx, amp=0.6)
            traco(ctx, [(x + sx * 2, y - 10), (x + sx * 8, y), (x + sx * 2, y + 8)], lw=3.5, alpha=0.5, seed=seed + 12 + sx, amp=0.3)
    pts = []
    for i in range(30):
        x, y = _fcab(P, 2 * math.pi * i / 30)
        pts.append((x, hc + y))
    forma(ctx, pts, pele, sombreado=0.08, seed=seed + 8, amp=1.0)
    if P.get("queixo") == "furinho":
        traco(ctx, [(-2, hc + ry * 0.84), (1, hc + ry * 0.93)], lw=4, alpha=0.6, seed=seed + 14, amp=0.2)


# ======================================================================== principal
def _aplica_preset(st):
    nome = st.get("preset")
    if not nome:
        return st
    from elenco import ELENCO
    if nome not in ELENCO:
        raise SystemExit(f"preset '{nome}' não existe. Elenco: {', '.join(sorted(ELENCO))}")
    base = ELENCO[nome]
    out = dict(base)
    for k, v in st.items():
        if k in base and isinstance(base[k], str) and v == 0:   # trilha sem valor no JSON (antes da 1ª troca): fica o do preset
            continue
        out[k] = v
    out["_preset"] = base
    return out


def _squash_cabeca(st, t):
    """ASSINATURA: a cabeça estica ou amassa e balança quando a expressão troca (squash and stretch)."""
    tr = st.get("_troca_expressao")
    if not tr:
        return 1.0, 1.0
    u = t - tr[1]
    if u < 0 or u > 0.6:
        return 1.0, 1.0
    a = 0.17 * math.exp(-6.5 * u) * math.cos(u * 21)
    if st.get("expressao") in ("surpreso", "bravo", "nervoso", "apaixonado"):
        return 1 - a * 0.6, 1 + a
    return 1 + a * 0.6, 1 - a


def desenha_humano2(ctx, st, t, seed):
    st = _aplica_preset(st)
    P = _proporcoes(st)
    idade = P["idade"]
    pele = _cor(st.get("pele"), PELES["media"])
    if st.get("bronzeado"):   # bronze de academia: puxa para o laranja (vale para qualquer tom de pele)
        pele = mix(pele, hexc("#E07A34"), 0.3)
    cab = _cor(st.get("cabelo_cor"), CABELO_COR["grisalho" if idade == "idoso" else "preto"])
    roupa = _cor(st.get("roupa"), "#2A7DE1")
    calca = _cor(st.get("calca"), "#2B2440")
    sapato = _cor(st.get("sapato"), "#3A2E52")
    luzes = _cor(st.get("luzes"), "#C98A4B") if st.get("luzes") else None
    estilo = {"rabo": "rabo_de_cavalo", "black": "black_power", "trancas": "trancas", "tranca": "trancas"}.get(st.get("cabelo", "curto"), st.get("cabelo", "curto"))
    manga = st.get("manga", "curta")
    bone = st.get("bone")
    oculos = st.get("oculos", idade == "idoso")
    nome_expr = st.get("expressao", "neutro")

    pose = st.get("pose", "em_pe")
    pose = pose if pose in POSES else "em_pe"
    prev, k = _troca(st, "pose", t, T_POSE)
    prev = prev if prev in POSES else None
    ks = (1.0 if pose == "sentado" else 0.0)
    if prev:
        k0 = 1.0 if prev == "sentado" else 0.0
        ks = k0 + (ks - k0) * k
    # balanço do corpo por pose/emoção
    oy = P["queda"] * ks
    ox = 0.0
    if pose == "comemorando" and not prev:
        oy -= abs(math.sin(t * 8)) * 10
    if nome_expr == "gargalhada":
        oy -= abs(math.sin(t * 11)) * 6
    elif nome_expr == "nervoso":
        ox += math.sin(t * 60) * 1.8

    # "caido": o corpo todo deita no chão (cabeça para a esquerda) e rola de um lado para o outro (o cai-cai)
    kc = 1.0 if pose == "caido" else 0.0
    if prev:
        k0 = 1.0 if prev == "caido" else 0.0
        kc = k0 + (kc - k0) * k
    ctx.save()
    if kc > 0:
        dy = (P["chao"] - P["ow"] * 0.75 - P["hy"]) * kc
        ctx.translate((70 + 14 * math.sin(t * 7)) * kc, dy)
        ctx.translate(0, P["hy"]); ctx.rotate(-math.pi / 2 * kc + 0.09 * math.sin(t * 7) * kc); ctx.translate(0, -P["hy"])
    # 1. atrás de tudo: banco, cabelo de trás, mochila
    if st.get("assento", True):
        _banco(ctx, P, ks, seed + 200)
    ctx.save(); ctx.translate(ox, oy)
    if P["lean"]:
        ctx.translate(0, P["hy"]); ctx.rotate(P["lean"]); ctx.translate(0, -P["hy"])
    sup = ctx.get_matrix()
    hsx, hsy = _squash_cabeca(st, t)
    queixo_y = P["hc"] + P["ry"]

    def cabeca_tf():
        if hsx != 1.0 or hsy != 1.0:
            ctx.translate(0, queixo_y); ctx.scale(hsx, hsy); ctx.translate(0, -queixo_y)

    ctx.save(); cabeca_tf()
    if st.get("aura"):   # brilho suave atrás da cabeça (personagem bonito)
        ac = _cor(st.get("aura"), "#FFE3F0")
        g = cairo.RadialGradient(0, P["hc"], P["rx"] * 0.4, 0, P["hc"], P["rx"] * 2.1)
        g.add_color_stop_rgba(0, *ac, 0.75); g.add_color_stop_rgba(0.55, *ac, 0.35); g.add_color_stop_rgba(1, *ac, 0)
        ctx.set_source(g); ctx.arc(0, P["hc"], P["rx"] * 2.1, 0, 2 * math.pi); ctx.fill()
    _cabelo_tras(ctx, P, estilo, cab, t, seed + 100, luzes)
    ctx.restore()
    if st.get("mochila"):
        _mochila_tras(ctx, P, _cor(st.get("mochila"), "#E8452C"), seed + 150)
    ctx.restore()
    # 2. pernas (não inclinam com a corcunda)
    ctx.save(); ctx.translate(ox, min(0.0, oy - P["queda"] * ks))
    _pernas(ctx, P, ks, calca, sapato, seed + 60)
    ctx.restore()
    # 3. tronco, cabeça e rosto
    ctx.save(); ctx.set_matrix(sup)
    pescoco = escurece(pele, 0.14)
    forma(ctx, pts_ret(-P["nw"], P["hc"] + P["ry"] - 30, 2 * P["nw"], P["sy"] - (P["hc"] + P["ry"]) + 40, 10), pescoco, sombra=False, lw=5, seed=seed + 6, amp=0.5)
    _tronco(ctx, P, roupa, pele, seed + 20, st.get("estampa"))
    if st.get("jaqueta"):
        _jaqueta(ctx, P, _cor(st.get("jaqueta"), "#2B2440"), seed + 165)
    if st.get("colar"):
        _colar(ctx, P, _cor(st.get("colar"), "#F2C14E"), seed + 166)
    if st.get("numero"):
        _numero(ctx, P, st.get("numero") if st.get("numero") is not True else "42", seed + 167)
    if P["muque"] and manga == "regata":   # peitoral marcado
        for sx in (-1, 1):
            traco(ctx, [(sx * P["cw"] * 0.8, P["sy"] + 70), (sx * P["cw"] * 0.4, P["sy"] + 96), (sx * 6, P["sy"] + 88)], lw=4, alpha=0.45, seed=seed + 168 + sx, amp=0.3)
    if st.get("avental"):
        _avental(ctx, P, _cor(st.get("avental"), "#FFF8EC"), seed + 160)
    if st.get("gravata"):
        _gravata(ctx, P, _cor(st.get("gravata"), "#E8352A"), seed + 170)
    if st.get("mochila"):
        _mochila_alcas(ctx, P, _cor(st.get("mochila"), "#E8452C"), seed + 155)
    if st.get("pochete"):
        _pochete(ctx, P, _cor(st.get("pochete"), "#3A2E52"), seed + 175)
    ctx.save(); cabeca_tf()
    _cabeca(ctx, P, pele, seed, st.get("orelhas", "normal"))
    my, wb, boca = _rosto(ctx, P, st, t, seed, pele, cab)
    _cabelo_frente(ctx, P, estilo, cab, idade, seed + 110, bone, t, luzes)
    if estilo == "trancas":
        _trancas(ctx, P, cab, t, seed + 120)
    if st.get("faixa"):
        _faixa(ctx, P, _cor(st.get("faixa"), "#E8452C"))
    if oculos:
        _oculos(ctx, P, _cor(st.get("oculos_cor") or oculos, "#2B2233"), st.get("oculos_tipo", "redondo"))
    if bone:
        _bone(ctx, P, _cor(bone, "#E8352A"), seed + 180)
    if st.get("fone"):
        _fone(ctx, P, _cor(st.get("fone"), "#2B2233"), seed + 190)
    if st.get("brincos"):
        _brincos(ctx, P, _cor(st.get("brincos") if st.get("brincos") != "brilhante" else None, "#F2C14E"), "brilhante" if st.get("brincos") == "brilhante" else "argola", t)
    if st.get("brilho"):
        _brilho_gala(ctx, P, st.get("brilho"), t, my, wb, boca, seed + 210)
    _extras(ctx, P, st, t)
    ctx.restore()
    if st.get("segura") == "celular" and pose in ("em_pe", "sentado"):
        if st.get("olhar") == "celular":   # brilho da tela no rosto
            g = cairo.RadialGradient(0, P["hc"] + 30, 10, 0, P["hc"] + 30, P["rx"] * 1.3)
            g.add_color_stop_rgba(0, 0.6, 0.95, 1, 0.16); g.add_color_stop_rgba(1, 0.6, 0.95, 1, 0)
            ctx.set_source(g); ctx.arc(0, P["hc"], P["rx"] * 1.05, 0, 2 * math.pi); ctx.fill()
        ctx.save(); ctx.translate(0, P["sy"] + 0.95 * P["ua"] - 20); ctx.rotate(-0.05)
        cw_, ch_ = (100, 160) if idade != "crianca" else (80, 128)
        forma(ctx, pts_ret(-cw_ / 2, -ch_ / 2, cw_, ch_, 16), hexc("#3A2E52"), sombra=True, lw=5, seed=seed + 33, sombra_off=(6, 8))
        ctx.arc(-cw_ * 0.28, -ch_ * 0.36, 8, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
        ctx.restore()
    # 4. braços por cima (com troca suave de pose)
    bracos = []
    for sx in (-1, 1):
        a1, a2, mao = _bracos_pose(pose, P, st, t, sx, seed)
        if prev and k < 1:
            b1, b2, m0 = _bracos_pose(prev, P, st, t, sx, seed)
            a1, a2 = _lerp_ang(b1, a1, k), _lerp_ang(b2, a2, k)
            mao = m0 if k < 0.5 else mao
        bracos.append((sx, a1, a2, mao))
    if pose == "bracos_cruzados":
        bracos.sort(key=lambda b: b[0])   # o braço da esquerda por baixo
    cor_manga = _cor(st.get("jaqueta"), "#2B2440") if st.get("jaqueta") else roupa
    for sx, a1, a2, mao in bracos:
        Wr = _braco(ctx, (sx * P["ow"] * 0.88, P["sy"] + 24), a1, a2, mao, P, cor_manga, pele, manga, seed + 70 + sx)
        if st.get("relogio") and sx < 0:
            _relogio(ctx, Wr[0], Wr[1], a2, _cor(st.get("relogio"), "#FF3DA8"))
        if st.get("segura") == "garrafa" and sx > 0:
            _garrafa(ctx, Wr[0] + 4, Wr[1] + 30, _cor(st.get("garrafa_cor"), "#5BE0A0"), t, seed + 90)
    ctx.restore()
    ctx.restore()   # fim do "caido"

    rx, ry, hc = P["rx"], P["ry"], P["hc"]
    vol = {"black_power": 1.45, "cacheado": 1.25, "topete": 1.6, "moicano": 1.66, "arrepiado": 1.38, "ondulado": 1.36, "volumoso": 1.2}.get(estilo, 1.12)
    topo = hc - ry * vol + oy - (30 if estilo == "coque" else 0)
    rosto = (-rx + ox, hc - ry + oy, rx + ox, hc + ry + oy)
    if P["lean"]:
        dx = math.sin(P["lean"]) * (P["hy"] - hc)
        rosto = (rosto[0] + dx, rosto[1], rosto[2] + dx, rosto[3])
    larg = max(P["ow"] + 30, rx * vol + 10, rx * 1.5 if estilo == "volumoso" else 0)
    if st.get("segura") == "garrafa":
        larg = max(larg, P["ow"] + 120)
    if pose in ("acenando", "comemorando", "apontando", "muque"):
        larg = max(larg, P["ow"] + P["ua"] + P["fa"] * 0.6)
        topo = min(topo, hc - ry * 1.1 + oy)
    if kc > 0.5:   # deitado: caixa horizontal
        yb = P["hy"] + (P["chao"] - P["ow"] * 0.75 - P["hy"])
        cab_x = -(P["hy"] - hc) + 70
        return {"corpo": (cab_x - ry * vol - 20, yb - P["ow"] - 40, P["chao"] - P["hy"] + 40, P["chao"] + 22),
                "rosto": (cab_x - ry, yb - rx, cab_x + ry, yb + rx)}
    return {"corpo": (-larg, topo, larg, P["chao"] + 22), "rosto": rosto}
