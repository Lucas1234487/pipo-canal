"""Memes do PipoPop 2D: o FORMATO do meme (a estrutura) redesenhado no estilo do canal.
Nunca a foto original de um meme famoso, nunca pessoa real: só painéis, textos e os nossos personagens.

Elemento {"tipo": "meme", "formato": ...}. O (x, y) é o centro da caixa do meme (`largura` x `altura`, padrão 900 x 900).
Padrão sugerido: x 0,5 e y 0,33 (a caixa fica entre y 0,10 e 0,56, longe da legenda).
`revela`: quantos painéis/níveis já apareceram (padrão: todos). Anime com "muda": cada painel entra com pop.
Personagens: `pers` = identidade (ex. {"tipo": "humano", "cabelo": "coque"}; padrão Pipo); `pers_a`, `pers_b`... sobrepõem por painel.
Os personagens são desenhados chamando biblioteca.desenha_pipo / biblioteca.desenha_humano na hora (herdam versões novas)."""
import math, random
import cairo
import biblioteca as B
from estilo import (INK, LW, AMARELO, BRANCO, VERMELHO, VERDE, hexc, mix, escurece, clareia, forma, traco, texto, medir,
                    pts_elipse, pts_ret, path_suave, jitter, ease_out_back, clamp)

TAM_MIN = 48          # regra do canal: nenhum texto menor que isto
LW_PAINEL = 9         # contorno grosso dos painéis
CINZA = hexc("#8E8AA0")
AZUL_SUOR = hexc("#7FD3FF")


# ============================ texto ============================
def _quebra(ctx, s, max_w, tam, max_linhas=3):
    """Quebra em linhas que cabem em max_w; diminui a fonte (nunca abaixo de TAM_MIN) se passar de max_linhas."""
    while True:
        linhas = []
        for par in str(s).split("\n"):
            atual = ""
            for p in par.split(" "):
                cand = (atual + " " + p).strip()
                if atual and medir(ctx, cand, tam) > max_w:
                    linhas.append(atual); atual = p
                else:
                    atual = cand
            linhas.append(atual)
        if len(linhas) <= max_linhas or tam <= TAM_MIN:
            return linhas, tam
        tam = max(TAM_MIN, tam * 0.9)


def _txt(ctx, s, x, y, max_w, tam, cor=BRANCO, contorno=INK, max_linhas=3, ancora="c", sombra=True, entre=1.12):
    """Bloco de texto centrado verticalmente em y. Devolve a caixa (local)."""
    if not s:
        return None
    linhas, tam = _quebra(ctx, s, max_w, tam, max_linhas)
    caixas = []
    n = len(linhas)
    for i, ln in enumerate(linhas):
        yy = y + (i - (n - 1) / 2) * tam * entre
        caixas.append(texto(ctx, ln, x, yy, tam, cor=cor, contorno=contorno, sombra=sombra, ancora=ancora,
                            max_w=max_w if tam > TAM_MIN else None, lw=None if contorno is not None else 0))
    return _une(caixas)


def _tinta(ctx, s, x, y, max_w, tam, **kw):
    """Texto escuro sem contorno (para cartões claros)."""
    return _txt(ctx, s, x, y, max_w, tam, cor=INK, contorno=None, sombra=False, **kw)


def _une(caixas):
    cx = [c for c in caixas if c]
    if not cx:
        return None
    return (min(c[0] for c in cx), min(c[1] for c in cx), max(c[2] for c in cx), max(c[3] for c in cx))


# ============================ painel com pop ============================
class Painel:
    """with Painel(ctx, ret, cor, p, seed) as ok: ... desenha o conteúdo recortado; contorno grosso por cima ao sair."""

    def __init__(self, ctx, ret, cor, p, seed, recorta=True, rot=0.0):
        self.ctx, self.ret, self.cor, self.p, self.seed, self.recorta, self.rot = ctx, ret, cor, p, seed, recorta, rot

    def __enter__(self):
        if self.p <= 0.001:
            return False
        ctx = self.ctx; x, y, w, h = self.ret
        k = ease_out_back(clamp(self.p), 2.2)
        ctx.save()
        ctx.translate(x + w / 2, y + h / 2); ctx.scale(max(0.01, k), max(0.01, k)); ctx.rotate(math.radians(self.rot))
        ctx.translate(-x - w / 2, -y - h / 2)
        self.pts = jitter(pts_ret(x, y, w, h, 22), 1.4, self.seed)
        ctx.save(); ctx.translate(10, 12); path_suave(ctx, self.pts); ctx.set_source_rgba(*INK, 0.30); ctx.fill(); ctx.restore()
        path_suave(ctx, self.pts); ctx.set_source_rgb(*self.cor); ctx.fill()
        ctx.save()
        if self.recorta:
            path_suave(ctx, self.pts); ctx.clip()
        return True

    def __exit__(self, *a):
        if self.p <= 0.001:
            return False
        ctx = self.ctx
        ctx.restore()
        path_suave(ctx, self.pts); ctx.set_line_width(LW_PAINEL); ctx.set_source_rgb(*INK); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
        ctx.restore()
        return False


def _faixa(ctx, x, y, w, h, cor):
    """Faixa de rótulo dentro de um painel (já recortada pelo painel)."""
    ctx.rectangle(x, y, w, h); ctx.set_source_rgb(*cor); ctx.fill()
    traco(ctx, [(x - 10, y + h), (x + w / 2, y + h + 1), (x + w + 10, y + h)], lw=LW, amp=0.8)


# ============================ personagens ============================
EXPR = {   # chaves dos dois personagens: pipo usa boca/sobrancelha/palpebra, humano usa expressao; ambos usam olhar
    "recusa":   {"boca": "triste", "sobrancelha": 0.0, "palpebra": 0.55, "olhar": "esq", "expressao": "bravo"},
    "aprova":   {"boca": "sorriso", "sobrancelha": 1.0, "palpebra": 0.1, "olhar": "dir", "expressao": "feliz"},
    "feliz":    {"boca": "sorriso", "sobrancelha": 0.7, "palpebra": 0.0, "olhar": "camera", "expressao": "feliz"},
    "acabado":  {"boca": "triste", "sobrancelha": 0.0, "palpebra": 0.68, "olhar": "baixo", "expressao": "triste"},
    "choque":   {"boca": "o", "sobrancelha": 1.2, "palpebra": 0.0, "olhar": "camera", "expressao": "surpreso"},
    "maroto":   {"boca": "sorriso_torto", "sobrancelha": 1.2, "palpebra": 0.15, "olhar": "camera", "expressao": "feliz"},
    "nada":     {"boca": "reta", "sobrancelha": 0.0, "palpebra": 0.5, "olhar": "camera", "expressao": "neutro"},
    "nervoso":  {"boca": "o", "sobrancelha": 1.2, "palpebra": 0.0, "olhar": "esq", "expressao": "surpreso"},
    "empolgado": {"boca": "sorriso", "sobrancelha": 1.1, "palpebra": 0.0, "olhar": "dir", "expressao": "feliz"},
}
ALT = {"pipo": (-360, 290), "humano": (-380, 350)}   # topo e base locais de cada personagem (para encaixar)


def _st_pers(st, expr, chave=None, **extra):
    s = {"tipo": "pipo"}
    s.update(st.get("pers") or {})
    s.update(EXPR.get(expr, {}))
    s.update(extra)
    if chave and st.get(chave):
        s.update(st[chave])
    s["_t"] = st.get("_t", 0); s["_estouro"] = None
    return s


def _pers(ctx, sp, x, y, altura, t, seed, rot=0.0):
    """Desenha o personagem com o TOPO em y e `altura` px de altura total. Devolve (caixas no espaço do meme, escala)."""
    tipo = sp.get("tipo", "pipo")
    top, base = ALT.get(tipo, ALT["humano"])
    esc = altura / (base - top) * sp.get("escala", 1)
    cy = y - top * esc
    ctx.save(); ctx.translate(x, cy); ctx.rotate(math.radians(rot))
    sy = 1 + 0.014 * math.sin(t * 2.6 + seed)
    sx = -1 if sp.get("espelha") else 1
    ctx.scale(esc * sx, esc * sy)
    f = B.desenha_pipo if tipo == "pipo" else B.desenha_humano   # por nome, na hora: herda o humano novo
    bx = f(ctx, sp, t, seed) or {}
    out = {}
    for k, b in bx.items():
        if b:
            pts = [ctx.user_to_device(px, py) for px, py in ((b[0], b[1]), (b[2], b[1]), (b[0], b[3]), (b[2], b[3]))]
            out[k] = pts
    ctx.restore()
    # caixas de volta ao espaço do meme
    m = ctx.get_matrix(); m.invert()
    res = {}
    for k, pts in out.items():
        loc = [m.transform_point(*p) for p in pts]
        res[k] = (min(p[0] for p in loc), min(p[1] for p in loc), max(p[0] for p in loc), max(p[1] for p in loc))
    return res, esc


def _cor_mao(sp):
    if sp.get("tipo", "pipo") == "pipo":
        return B.MILHO
    return B._cor(sp.get("pele"), B.PELES["media"])


def _cor_manga(sp):
    if sp.get("tipo", "pipo") == "pipo":
        return B.MILHO
    return B._cor(sp.get("roupa"), "#2A7DE1")


def _braco(ctx, p0, p1, cor, esc, seed):
    mx, my = (p0[0] + p1[0]) / 2, max(p0[1], p1[1]) + 30 * esc
    traco(ctx, [p0, (mx, my), p1], lw=max(14, 30 * esc), seed=seed)
    traco(ctx, [p0, (mx, my), p1], lw=max(7, 17 * esc), cor=cor, seed=seed, amp=0)


def _mao(ctx, jeito, x, y, esc, rot, cor, seed):
    """Mão desenhada: 'pare' (palma aberta, dedos para cima), 'aponta' (indicador para +x), 'baixo' (indicador para baixo)."""
    ctx.save(); ctx.translate(x, y); ctx.rotate(math.radians(rot)); ctx.scale(esc, esc)
    if jeito == "pare":
        for i, (dx, ln) in enumerate(((-33, 70), (-11, 84), (11, 80), (33, 66))):
            forma(ctx, pts_ret(dx - 11, -40 - ln, 22, ln + 20, 11, 3), cor, sombra=False, lw=5, seed=seed + i, amp=0.6)
        ctx.save(); ctx.translate(-50, 10); ctx.rotate(-0.7)
        forma(ctx, pts_ret(-12, -50, 24, 62, 12, 3), cor, sombra=False, lw=5, seed=seed + 7, amp=0.6); ctx.restore()
        forma(ctx, pts_ret(-46, -46, 92, 96, 30), cor, sombra=True, lw=5, seed=seed + 9, amp=0.8, sombra_off=(6, 7))
        traco(ctx, [(-20, 0), (0, 14), (22, 4)], lw=3, alpha=0.45, seed=seed + 11)
    else:
        if jeito == "baixo":
            ctx.rotate(math.pi / 2)
        forma(ctx, pts_ret(56, -40, 74, 24, 12, 3), cor, sombra=False, lw=5, seed=seed + 1, amp=0.6)    # indicador
        forma(ctx, pts_ret(-46, -44, 104, 84, 28), cor, sombra=True, lw=5, seed=seed + 2, amp=0.8, sombra_off=(6, 7))
        for k in range(3):
            traco(ctx, [(40, -8 + k * 18), (56, -6 + k * 18)], lw=4, seed=seed + 3 + k)
        forma(ctx, pts_elipse(-4, 30, 30, 14, 10), cor, sombra=False, lw=5, seed=seed + 8, amp=0.6)      # polegar
    ctx.restore()


# ============================ enfeites ============================
def _estrela(ctx, x, y, r, cor, seed, giro=0.0, pontas=5):
    pts = []
    for i in range(pontas * 2):
        a = giro + math.pi * i / pontas - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    forma(ctx, pts, cor, sombra=False, lw=5, seed=seed, amp=0.6)


def _brilho(ctx, x, y, r, t, seed):
    """Brilhinho de 4 pontas que pisca."""
    k = 0.65 + 0.35 * math.sin(t * 6 + seed)
    _estrela(ctx, x, y, r * k, BRANCO, seed, giro=0.0, pontas=4)


def _gota(ctx, x, y, r, seed, cor=AZUL_SUOR):
    forma(ctx, [(x, y - r * 1.9), (x + r * 0.8, y - r * 0.5), (x + r, y + r * 0.2), (x + r * 0.6, y + r * 0.85), (x, y + r),
                (x - r * 0.6, y + r * 0.85), (x - r, y + r * 0.2), (x - r * 0.8, y - r * 0.5)], cor, sombra=False, lw=4, seed=seed, amp=0.5)
    ctx.arc(x - r * 0.35, y + r * 0.05, r * 0.22, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.8); ctx.fill()


def _nuvem(ctx, x, y, esc, cor, seed):
    pts = []
    for i in range(18):
        a = 2 * math.pi * i / 18
        rr = 1 + 0.18 * math.cos(a * 5)
        pts.append((x + math.cos(a) * 120 * rr * esc, y + math.sin(a) * 55 * rr * esc))
    forma(ctx, pts, cor, sombra=True, lw=6, seed=seed, sombra_off=(6, 8))


def _rajada(ctx, cx, cy, r_in, r_out, n, seed, t, cor=INK, alpha=1.0):
    """Linhas de impacto radiais (cunhas)."""
    rng = random.Random(seed + int(t * 12))
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.05, 0.05)
        ri = r_in * rng.uniform(1.0, 1.25)
        larg = rng.uniform(0.012, 0.03)
        ctx.move_to(cx + math.cos(a - larg) * r_out, cy + math.sin(a - larg) * r_out)
        ctx.line_to(cx + math.cos(a) * ri, cy + math.sin(a) * ri)
        ctx.line_to(cx + math.cos(a + larg) * r_out, cy + math.sin(a + larg) * r_out)
        ctx.close_path()
    ctx.set_source_rgba(*cor, alpha); ctx.fill()


def _explosao(ctx, cx, cy, rx, ry, cor, seed, pontas=14, t=0.0):
    rng = random.Random(seed)
    pts = []
    for i in range(pontas * 2):
        a = 2 * math.pi * i / (pontas * 2)
        k = 1.0 if i % 2 == 0 else rng.uniform(0.66, 0.78)
        k *= 1 + 0.03 * math.sin(t * 9 + i)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    forma(ctx, pts, cor, sombra=True, lw=LW + 2, seed=seed, amp=1.2)


def _cerebro(ctx, x, y, r, nivel, n, t, seed):
    """Cérebro desenhado; quanto maior o nível, mais brilha (aura, raios, faíscas)."""
    b = nivel / max(1, n - 1)
    if b > 0.2:   # aura
        g = cairo.RadialGradient(x, y, r * 0.3, x, y, r * (1.5 + 1.2 * b))
        g.add_color_stop_rgba(0, 1, 1, 0.85, 0.85 * b); g.add_color_stop_rgba(0.5, 1, 0.85, 0.3, 0.45 * b); g.add_color_stop_rgba(1, 1, 0.8, 0.2, 0)
        ctx.set_source(g); ctx.paint()
    if b > 0.5:   # raios girando
        nr = 10 + int(10 * b)
        for i in range(nr):
            a = 2 * math.pi * i / nr + t * (0.6 + b)
            ctx.move_to(x + math.cos(a - 0.06) * r * 1.1, y + math.sin(a - 0.06) * r * 1.1)
            ctx.line_to(x + math.cos(a) * r * (2.0 + b), y + math.sin(a) * r * (2.0 + b))
            ctx.line_to(x + math.cos(a + 0.06) * r * 1.1, y + math.sin(a + 0.06) * r * 1.1)
            ctx.close_path()
        ctx.set_source_rgba(1, 0.95, 0.6, 0.55 * b); ctx.fill()
    cor = mix(mix(hexc("#C9A7B5"), hexc("#FF8FB8"), min(1, b * 1.6)), (1, 1, 0.9), max(0, b - 0.55) * 1.6)
    rr = r * (0.72 + 0.28 * b)
    pts = []
    for i in range(28):
        a = 2 * math.pi * i / 28
        k = 1 + 0.08 * math.cos(a * 7)
        pts.append((x + math.cos(a) * rr * 1.18 * k, y + math.sin(a) * rr * 0.92 * k))
    forma(ctx, pts, cor, sombra=True, sombreado=0.1, lw=LW, seed=seed, amp=1.0, sombra_off=(6, 8))
    traco(ctx, [(x, y - rr * 0.85), (x - rr * 0.06, y - rr * 0.3), (x + rr * 0.05, y + rr * 0.25), (x, y + rr * 0.8)], lw=5, seed=seed + 1)
    rng = random.Random(seed)
    for k in range(6):   # dobrinhas
        sx = -1 if k % 2 else 1
        cx, cy = x + sx * rr * rng.uniform(0.35, 0.8), y + rr * rng.uniform(-0.55, 0.5)
        traco(ctx, [(cx - sx * rr * 0.2, cy), (cx, cy - rr * 0.12), (cx + sx * rr * 0.15, cy + rr * 0.05)], lw=4, alpha=0.7, seed=seed + 10 + k)
    if nivel == 0:   # cérebro miudinho: um mosquito voando em volta
        a = t * 5
        ctx.arc(x + math.cos(a) * rr * 1.5, y + math.sin(a) * rr * 0.9, 5, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    if b > 0.7:   # faíscas
        for k in range(5):
            a = t * 1.3 + k * 1.26
            _brilho(ctx, x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.1, 18 + 6 * b, t, seed + 30 + k)


# ============================ formatos ============================
def _p(st, i):
    return clamp(st.get("_rev", 99) - i)


def f_aprova_reprova(ctx, st, t, pal, seed, w, h):
    x0, y0, g = -w / 2, -h / 2, 18
    rh = (h - g) / 2; lw_ = w * 0.44; tw = w - lw_ - g
    textos = []; caras = []
    fundo = [hexc(st.get("cor_a", "#FF8A3D")), hexc(st.get("cor_b", "#38C6B5"))]
    for i, (expr, chave, txt) in enumerate((("recusa", "pers_a", st.get("nao", "coisa chata")), ("aprova", "pers_b", st.get("sim", "coisa legal")))):
        p = _p(st, i); y = y0 + i * (rh + g)
        with Painel(ctx, (x0, y, lw_, rh), fundo[i], p, seed + i) as ok:
            if ok:
                sp = _st_pers(st, expr, chave)
                bx, esc = _pers(ctx, sp, x0 + lw_ * 0.47, y + rh * 0.10, rh * 1.25, t, seed + 10 + i, rot=-7 if i == 0 else 5)
                ro = bx.get("rosto") or bx.get("corpo")
                caras.append(ro)
                cm = _cor_mao(sp)
                fx = ro[2] + 4; fy = (ro[1] + ro[3]) / 2
                if i == 0:   # mão de "nem vem" na frente, entre a cara e o texto
                    _braco(ctx, (x0 + lw_ * 0.60, y + rh * 1.02), (fx + 20, fy + 30), _cor_manga(sp), esc, seed + 20)
                    _mao(ctx, "pare", fx + 20, fy - 6 + math.sin(t * 3) * 3, 0.95, 12, cm, seed + 21)
                else:        # apontando para o texto
                    _braco(ctx, (x0 + lw_ * 0.62, y + rh * 1.02), (fx + 4, fy + 46), _cor_manga(sp), esc, seed + 22)
                    _mao(ctx, "aponta", fx + 10 + math.sin(t * 5) * 6, fy + 40, 0.95, -8, cm, seed + 23)
        with Painel(ctx, (x0 + lw_ + g, y, tw, rh), BRANCO, p, seed + 5 + i) as ok:
            if ok:
                cx = x0 + lw_ + g + tw / 2
                textos.append(_tinta(ctx, txt, cx, y + rh * 0.47, tw - 60, st.get("tam", 72), max_linhas=4))
                # selinho: X vermelho / certo verde no canto
                sx_, sy_ = x0 + lw_ + g + tw - 52, y + 52
                forma(ctx, pts_elipse(sx_, sy_, 34, 34, 16), VERMELHO if i == 0 else VERDE, sombra=False, lw=5, seed=seed + 30 + i)
                if i == 0:
                    traco(ctx, [(sx_ - 13, sy_ - 13), (sx_ + 13, sy_ + 13)], lw=8, cor=BRANCO, seed=seed + 31)
                    traco(ctx, [(sx_ + 13, sy_ - 13), (sx_ - 13, sy_ + 13)], lw=8, cor=BRANCO, seed=seed + 32)
                else:
                    traco(ctx, [(sx_ - 15, sy_), (sx_ - 4, sy_ + 12), (sx_ + 16, sy_ - 12)], lw=8, cor=BRANCO, seed=seed + 33)
    return textos, caras


def _conteudo(ctx, st, t, pal, seed, ret, foto, txt, chave, expr, extra=None):
    """Conteúdo de um painel: foto CC0 (polaroide de desenha_foto) > texto > personagem."""
    x, y, w, h = ret; caras = []; caixa = None
    if foto:
        k = 0.86
        fw = w * k
        surf = B._foto_surface(foto)
        fh = min(h * k - 40, fw * surf.get_height() / surf.get_width())
        fw = min(fw, fh * surf.get_width() / surf.get_height())
        ctx.save(); ctx.translate(x + w / 2, y + h / 2); ctx.rotate(math.radians(-2.5 if chave.endswith("a") else 2.5))
        B.desenha_foto(ctx, {"arquivo": foto, "largura": fw, "altura": fh, "zoom_lento": 0.05, "_t": t}, t, pal, seed)
        ctx.restore()
    elif txt:
        caixa = _txt(ctx, txt, x + w / 2, y + h / 2, w - 80, st.get("tam", 78), max_linhas=3)
    else:
        sp = _st_pers(st, expr, chave, **(extra or {}))
        bx, _ = _pers(ctx, sp, x + w / 2, y + h * 0.12, h * 1.15, t, seed)
        caras.append(bx.get("rosto"))
    return caixa, caras


def f_expectativa_realidade(ctx, st, t, pal, seed, w, h):
    x0, y0, g = -w / 2, -h / 2, 18
    rh = (h - g) / 2; fh = 92
    textos = []; caras = []
    cfg = (("EXPECTATIVA", "foto_a", "texto_a", "pers_a", "feliz", hexc("#9BE3FF"), VERDE),
           ("REALIDADE", "foto_b", "texto_b", "pers_b", "acabado", hexc("#B9B3C6"), VERMELHO))
    for i, (rot, kf, kt, kp, expr, cor, cfaixa) in enumerate(cfg):
        p = _p(st, i); y = y0 + i * (rh + g)
        with Painel(ctx, (x0, y, w, rh), cor, p, seed + i) as ok:
            if not ok:
                continue
            area = (x0, y + fh, w, rh - fh)
            if i == 1 and not st.get(kf) and not st.get(kt):   # nuvenzinha de chuva na realidade
                for k in range(5):
                    yy = y + fh + 70 + ((t * 260 + k * 53) % 150)
                    traco(ctx, [(x0 + w * 0.72 + k * 22 - 40, yy), (x0 + w * 0.72 + k * 22 - 46, yy + 22)], lw=5, cor=hexc("#3F7BD6"), seed=seed + 40 + k)
                _nuvem(ctx, x0 + w * 0.72, y + fh + 60, 0.75, hexc("#6E6A80"), seed + 45)
            cx, cr = _conteudo(ctx, st, t, pal, seed + 10 + i, area, st.get(kf), st.get(kt), kp, expr)
            textos.append(cx); caras += cr
            if i == 0 and not st.get(kf) and not st.get(kt):
                for k, (bx_, by_) in enumerate(((0.18, 0.35), (0.82, 0.30), (0.25, 0.80), (0.78, 0.75))):
                    _brilho(ctx, x0 + w * bx_, y + fh + (rh - fh) * by_, 34, t, seed + 50 + k)
            _faixa(ctx, x0, y, w, fh, cfaixa)
            textos.append(_txt(ctx, st.get("rotulo_a" if i == 0 else "rotulo_b", rot), x0 + w / 2, y + fh / 2 + 2, w - 80, 64, max_linhas=1))
    return textos, caras


def f_ninguem_eu(ctx, st, t, pal, seed, w, h):
    x0, y0, g = -w / 2, -h / 2, 18
    h1 = h * 0.26; h2 = h - h1 - g
    textos = []; caras = []
    with Painel(ctx, (x0, y0, w, h1), BRANCO, _p(st, 0), seed) as ok:
        if ok:
            textos.append(_tinta(ctx, st.get("ninguem", "Ninguém:"), x0 + 50, y0 + 70, w - 100, 72, max_linhas=1, ancora="l"))
            # o vazio é a piada: só uma linha tracejada bem clarinha
            for k in range(6):
                traco(ctx, [(x0 + 50 + k * 70, y0 + h1 - 55), (x0 + 90 + k * 70, y0 + h1 - 55)], lw=4, alpha=0.18, seed=seed + k)
    y2 = y0 + h1 + g
    with Painel(ctx, (x0, y2, w, h2), BRANCO, _p(st, 1), seed + 1) as ok:
        if ok:
            eu = st.get("eu", "Eu:")
            txt = st.get("texto", "")
            linhas, tam = _quebra(ctx, (eu + " " + txt).strip(), w - 100, 66, 2)
            th = len(linhas) * tam * 1.12 + 40
            textos.append(_tinta(ctx, "\n".join(linhas), x0 + 50, y2 + th / 2 + 6, w - 100, tam, max_linhas=2, ancora="l"))
            cena = (x0 + 26, y2 + th + 14, w - 52, h2 - th - 40)
            with Painel(ctx, cena, hexc(st.get("cor_cena", "#FF6F91")), 1, seed + 2) as ok2:
                bx, _ = _pers(ctx, _st_pers(st, "maroto", "pers_b"), x0 + w / 2, cena[1] + cena[3] * 0.06, cena[3] * 1.45, t, seed + 3)
                caras.append(bx.get("rosto"))
    return textos, caras


def f_pov(ctx, st, t, pal, seed, w, h):
    x0, y0 = -w / 2, -h / 2
    textos = []; caras = []
    linhas, tam = _quebra(ctx, st.get("texto", "você abriu o app só para ver as horas"), w - 220, 62, 3)
    fh = max(140, len(linhas) * tam * 1.12 + 60)
    with Painel(ctx, (x0, y0, w, h), hexc(st.get("cor_cena", "#5BB8FF")), _p(st, 1), seed + 1) as ok:
        if ok:
            for k in range(7):   # chão + raiozinhos ao fundo
                a = -math.pi / 2 + (k - 3) * 0.35
                traco(ctx, [(0, y0 + h), (math.cos(a) * w, y0 + h + math.sin(a) * w)], lw=40, cor=BRANCO, alpha=0.12, amp=0, seed=seed + k)
            bx, _ = _pers(ctx, _st_pers(st, st.get("expr", "choque"), "pers_b"), 0, y0 + fh + 50, (h - fh) * 1.1, t, seed + 3)
            caras.append(bx.get("rosto"))
    with Painel(ctx, (x0 + 20, y0 + 20, w - 40, fh), INK, _p(st, 0), seed) as ok:
        if ok:
            textos.append(texto(ctx, "POV:", x0 + 50, y0 + 20 + fh / 2, 76, cor=AMARELO, ancora="l", sombra=False))
            textos.append(_txt(ctx, "\n".join(linhas), x0 + 230, y0 + 20 + fh / 2, w - 290, tam, max_linhas=3, ancora="l", sombra=False))
    return textos, caras


def f_plot_twist(ctx, st, t, pal, seed, w, h):
    x0, y0 = -w / 2, -h / 2
    textos = []; caras = []
    p1 = _p(st, 1)
    fh = 0
    with Painel(ctx, (x0, y0, w, h), hexc(st.get("cor_cena", "#B18CFF")), _p(st, 0), seed) as ok:
        if ok:
            if st.get("texto"):
                linhas, tam = _quebra(ctx, st["texto"], w - 100, 62, 2)
                fh = len(linhas) * tam * 1.12 + 44
                _faixa(ctx, x0, y0, w, fh, BRANCO)
                textos.append(_tinta(ctx, "\n".join(linhas), 0, y0 + fh / 2, w - 100, tam, max_linhas=2))
            expr = "choque" if p1 > 0 else st.get("expr", "feliz")
            bx, _ = _pers(ctx, _st_pers(st, expr, "pers_a"), 0, y0 + fh + 120, (h - fh) * 1.0, t, seed + 3)
            caras.append(bx.get("rosto"))
    if p1 > 0:
        cy = y0 + h * 0.80
        k = 1 + 1.5 * (1 - p1) ** 2
        ctx.save(); ctx.translate(0, cy)
        for j in range(7):   # estrelinhas em volta, piscando e girando
            a = 2 * math.pi * j / 7 + t * 0.8
            r = 360 + 25 * math.sin(t * 4 + j)
            _estrela(ctx, math.cos(a) * r, math.sin(a) * 150, 26 + 8 * math.sin(t * 7 + j), AMARELO if j % 2 else BRANCO, seed + 60 + j, giro=t * 2 + j)
        ctx.scale(k, k)
        ctx.push_group()
        tw_ = medir(ctx, st.get("carimbo", "PLOT TWIST").upper(), st.get("tam", 112)) + 130
        ctx.save(); ctx.rotate(math.radians(-13))
        forma(ctx, pts_ret(-tw_ / 2, -st.get("tam", 112) * 0.95, tw_, st.get("tam", 112) * 1.9, 24), BRANCO, sombra=True, lw=LW, seed=seed + 69)
        ctx.restore()
        bc = B.desenha_carimbo(ctx, {"texto": st.get("carimbo", "PLOT TWIST"), "cor": st.get("cor_carimbo", "#E8352A"), "inclina": -13,
                                     "tam": st.get("tam", 112)}, t, pal, seed + 70)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(clamp(p1 * 2))
        ctx.restore()
        bt = bc.get("texto")
        if bt and p1 > 0.9:
            # caixa do carimbo girado (aprox. pela diagonal)
            textos.append((bt[0] - 30, cy + bt[1] - 60, bt[2] + 30, cy + bt[3] + 60))
    return textos, caras


def _rabiscos(ctx, x, y, w, h, t, seed):
    """Quadro rabiscado: setas, círculos, fórmulas sem sentido (decoração, não é texto do QA)."""
    rng = random.Random(seed)
    cores = [hexc("#2A3FD1"), VERMELHO, hexc("#16A57A"), INK]
    for k in range(9):
        c = cores[k % 4]
        px, py = x + rng.uniform(0.1, 0.8) * w, y + rng.uniform(0.15, 0.8) * h
        tipo = k % 4
        if tipo == 0:
            pts = [(px + math.cos(a) * 40 + rng.uniform(-6, 6), py + math.sin(a) * 28) for a in [i * 0.6 for i in range(12)]]
            traco(ctx, pts, lw=5, cor=c, seed=seed + k, amp=1.5)
        elif tipo == 1:
            qx, qy = px + rng.uniform(60, 120), py + rng.uniform(-60, 60)
            traco(ctx, [(px, py), ((px + qx) / 2, min(py, qy) - 40), (qx, qy)], lw=5, cor=c, seed=seed + k)
            traco(ctx, [(qx - 18, qy - 14), (qx, qy), (qx - 20, qy + 10)], lw=5, cor=c, seed=seed + k + 50)
        elif tipo == 2:
            pts = [(px + i * 14, py + (10 if i % 2 else -10) * rng.uniform(0.5, 1.4)) for i in range(8)]
            traco(ctx, pts, lw=5, cor=c, seed=seed + k)
        else:
            ctx.select_font_face("Fredoka Light", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(40)
            ctx.move_to(px, py); ctx.set_source_rgb(*c)
            ctx.show_text(rng.choice(["x+y=?", "A>B?", "???", "=42", "2+2=5", "%$#!"]))


def f_eu_explicando(ctx, st, t, pal, seed, w, h):
    x0, y0, g = -w / 2, -h / 2, 18
    h1 = h * 0.56; h2 = h - h1 - g; fh = 96
    textos = []; caras = []
    with Painel(ctx, (x0, y0, w, h1), hexc(st.get("cor_a", "#FFE27A")), _p(st, 0), seed) as ok:
        if ok:
            qx, qy, qw, qh = x0 + w * 0.36, y0 + fh + 40, w * 0.58, h1 - fh - 80
            forma(ctx, pts_ret(qx, qy, qw, qh, 10), BRANCO, sombra=True, lw=LW, seed=seed + 1, sombra_off=(8, 9))
            _rabiscos(ctx, qx, qy, qw, qh, t, seed + 2)
            sp = _st_pers(st, "empolgado", "pers_a")
            bx, esc = _pers(ctx, sp, x0 + w * 0.19, y0 + fh + 40, (h1 - fh) * 1.15, t, seed + 3, rot=math.sin(t * 4) * 3)
            ro = bx.get("rosto") or bx.get("corpo")
            caras.append(ro)
            ponta = (qx + 60 + math.sin(t * 7) * 40, qy + qh * 0.45 + math.cos(t * 5) * 30)   # varinha apontando
            mao = (ro[2] + 20, ro[3] + 30)
            traco(ctx, [mao, ponta], lw=8, cor=hexc("#8B5A2B"), seed=seed + 4, amp=0.5)
            _mao(ctx, "aponta", mao[0], mao[1], 0.7, math.degrees(math.atan2(ponta[1] - mao[1], ponta[0] - mao[0])), _cor_mao(sp), seed + 5)
            _faixa(ctx, x0, y0, w, fh, INK)
            textos.append(_txt(ctx, "eu explicando " + st.get("texto", "o meu plano"), 0, y0 + fh / 2 + 2, w - 60, 60, max_linhas=1, sombra=False))
    y2 = y0 + h1 + g
    with Painel(ctx, (x0, y2, w, h2), hexc(st.get("cor_b", "#9AA0B4")), _p(st, 1), seed + 6) as ok:
        if ok:
            eles = st.get("eles_pers") or [{"tipo": "humano", "cabelo": "coque", "cabelo_cor": "ruivo", "pele": "clara", "roupa": "#E8452C"},
                                           {"tipo": "humano", "cabelo": "careca", "pele": "escura", "roupa": "#16A57A"},
                                           {"tipo": "humano", "cabelo": "cacheado", "cabelo_cor": "castanho", "pele": "morena", "roupa": "#5B2A86"}]
            n = len(eles)
            for k, e in enumerate(eles):
                sp = {"tipo": "humano"}; sp.update(EXPR["nada"]); sp.update(e); sp["_t"] = t; sp["_estouro"] = None
                bx, _ = _pers(ctx, sp, x0 + w * (k + 0.5) / n, y2 + 90, h2 * 1.55, t, seed + 10 + k)
                caras.append(bx.get("rosto"))
            _faixa(ctx, x0, y2, w * 0.36, 86, INK)
            textos.append(_txt(ctx, st.get("eles", "eles:"), x0 + w * 0.18, y2 + 45, w * 0.32, 60, max_linhas=1, sombra=False))
    return textos, caras


def f_cerebro_niveis(ctx, st, t, pal, seed, w, h):
    niv = st.get("niveis") or ["ler o manual", "ver um tutorial", "apertar todos os botões", "desligar e ligar de novo"]
    n = len(niv); x0, y0, g = -w / 2, -h / 2, 14
    rh = (h - g * (n - 1)) / n; tw = w * 0.58; bw = w - tw - g
    textos = []
    for i, s in enumerate(niv):
        p = _p(st, i); y = y0 + i * (rh + g); b = i / max(1, n - 1)
        with Painel(ctx, (x0, y, tw, rh), BRANCO, p, seed + i) as ok:
            if ok:
                textos.append(_tinta(ctx, s, x0 + tw / 2, y + rh / 2, tw - 50, st.get("tam", 60), max_linhas=3))
        fundo = mix(hexc("#3B3850"), hexc("#FFB347"), b * 0.9) if b < 1 else hexc("#FF9F1C")
        with Painel(ctx, (x0 + tw + g, y, bw, rh), fundo, p, seed + 10 + i) as ok:
            if ok:
                _cerebro(ctx, x0 + tw + g + bw / 2, y + rh / 2, min(bw, rh) * 0.30 * (0.8 + 0.4 * b), i, n, t, seed + 20 + i)
    return textos, []


def _botao(ctx, x, y, r, apertado, seed):
    forma(ctx, pts_ret(x - r * 1.5, y - r * 0.15, r * 3, r * 0.9, 18), hexc("#5D5A70"), sombra=True, lw=LW, seed=seed)   # base
    dy = r * 0.18 if apertado else 0
    forma(ctx, pts_ret(x - r, y - r * 0.55 + dy, r * 2, r * 0.75, r * 0.4), escurece(VERMELHO, 0.3), sombra=False, lw=LW, seed=seed + 1)
    forma(ctx, pts_elipse(x, y - r * 0.55 + dy, r, r * 0.42, 20), VERMELHO, sombra=False, lw=LW, seed=seed + 2)
    ctx.save(); ctx.translate(x - r * 0.35, y - r * 0.66 + dy); ctx.scale(r * 0.3, r * 0.1); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()
    ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()


def f_botoes_dificil(ctx, st, t, pal, seed, w, h):
    x0, y0, g = -w / 2, -h / 2, 18
    h1 = h * 0.54; h2 = h - h1 - g
    textos = []; caras = []
    with Painel(ctx, (x0, y0, w, h1), hexc(st.get("cor_a", "#8FD3FF")), _p(st, 0), seed) as ok:
        if ok:
            for k, (chave, padrao) in enumerate((("botao_a", "dormir cedo"), ("botao_b", "só mais um vídeo"))):
                bx_ = x0 + w * (0.27 + 0.46 * k)
                _botao(ctx, bx_, y0 + h1 * 0.80, 100, False, seed + 2 + k * 5)
                cw, ch = w * 0.42, h1 * 0.44
                ctx.save(); ctx.translate(bx_, y0 + 36 + ch / 2); ctx.rotate(math.radians(-4 if k == 0 else 4))
                forma(ctx, pts_ret(-cw / 2, -ch / 2, cw, ch, 16), BRANCO, sombra=True, lw=LW, seed=seed + 20 + k, sombra_off=(6, 8))
                c = _tinta(ctx, st.get(chave, padrao), 0, 0, cw - 40, st.get("tam", 58), max_linhas=3)
                ctx.restore()
                if c:
                    r = math.radians(4); ex = abs(math.sin(r)) * (c[3] - c[1]) / 2 + 4
                    textos.append((bx_ + c[0] - ex, y0 + 36 + ch / 2 + c[1] - ex * 3, bx_ + c[2] + ex, y0 + 36 + ch / 2 + c[3] + ex * 3))
            # dedo indeciso, vai e volta entre os dois botões
            u = 0.5 + 0.5 * math.sin(t * 2.6)
            _mao(ctx, "baixo", x0 + w * (0.27 + 0.46 * u), y0 + h1 * 0.50 + 10 * math.sin(t * 5.2), 0.9, 0, B.MILHO, seed + 30)
    y2 = y0 + h1 + g
    with Painel(ctx, (x0, y2, w, h2), hexc(st.get("cor_b", "#FF8A80")), _p(st, 1), seed + 1) as ok:
        if ok:
            tre = math.sin(t * 40) * 3
            sp = _st_pers(st, "nervoso", "pers_b")
            bx, esc = _pers(ctx, sp, x0 + w / 2 + tre, y2 + 30, h2 * 1.35, t, seed + 3)
            ro = bx.get("rosto") or bx.get("corpo")
            caras.append(ro)
            for k in range(7):   # suor: gotas fixas na testa + gotas caindo
                rng = random.Random(seed + k)
                lado = -1 if k % 2 else 1
                gx = (ro[0] + ro[2]) / 2 + lado * (ro[2] - ro[0]) * rng.uniform(0.45, 0.75)
                u = (t * 1.1 + k * 0.37) % 1.0
                gy = ro[1] + (ro[3] - ro[1]) * 0.1 + u * 200
                _gota(ctx, gx, gy, 14 + 5 * rng.random(), seed + 40 + k)
            _gota(ctx, ro[2] - (ro[2] - ro[0]) * 0.18, ro[1] + (ro[3] - ro[1]) * 0.12, 24, seed + 50)   # gotona na testa
    return textos, caras


def f_grafico_mentiroso(ctx, st, t, pal, seed, w, h):
    x0, y0 = -w / 2, -h / 2
    textos = []
    explode = st.get("direcao", "despenca") == "explode"
    p0, p1 = _p(st, 0), _p(st, 1)
    ttl = st.get("texto", "meu salário" if not explode else "minha conta de luz")
    linhas, tam = _quebra(ctx, ttl, w - 100, 64, 2)
    fh = len(linhas) * tam * 1.12 + 40
    gx0, gy0, gx1, gy1 = x0 + 90, y0 + fh + 40, x0 + w - 50, y0 + h - 70
    # pontos do gráfico (0..1): sobe devagar, zigue-zague
    sobe = [(0, 0.55), (0.12, 0.5), (0.22, 0.56), (0.34, 0.45), (0.45, 0.48), (0.56, 0.38), (0.66, 0.40)]
    if explode:
        sobe = [(0, 0.40), (0.12, 0.42), (0.22, 0.37), (0.34, 0.44), (0.45, 0.40), (0.56, 0.47), (0.66, 0.45)]
        fim = [(0.66, 0.45), (0.80, 0.05), (0.92, -0.25)]
    else:
        fim = [(0.66, 0.40), (0.70, 0.62), (0.76, 0.98)]

    def P(u, v):
        return (gx0 + u * (gx1 - gx0), gy0 + v * (gy1 - gy0))

    def parcial(pts, prog):
        if prog <= 0:
            return []
        segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
        alvo = sum(segs) * clamp(prog); out = [pts[0]]
        for i, s in enumerate(segs):
            if alvo >= s:
                out.append(pts[i + 1]); alvo -= s
            else:
                k = alvo / s if s else 0
                out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * k, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * k)); break
        return out
    prog0 = clamp(st.get("progresso", 1.0)) if p0 >= 1 else p0
    fim_px = parcial([P(*q) for q in fim], p1)
    with Painel(ctx, (x0, y0, w, h), BRANCO, p0, seed) as ok:
        if ok:
            for k in range(1, 5):   # grade
                yy = gy0 + (gy1 - gy0) * k / 5
                traco(ctx, [(gx0, yy), (gx1, yy)], lw=3, alpha=0.15, seed=seed + k, amp=0.4)
            traco(ctx, [(gx0, gy0 - 20), (gx0, (gy0 + gy1) / 2), (gx0, gy1)], lw=LW + 1, seed=seed + 10)
            traco(ctx, [(gx0, gy1), ((gx0 + gx1) / 2, gy1), (gx1 + 10, gy1)], lw=LW + 1, seed=seed + 9)
            traco(ctx, [(gx0 - 14, gy0 - 2), (gx0, gy0 - 22), (gx0 + 14, gy0 - 2)], lw=LW, seed=seed + 11)
            traco(ctx, [(gx1 - 8, gy1 - 14), (gx1 + 12, gy1), (gx1 - 8, gy1 + 14)], lw=LW, seed=seed + 12)
            pts = parcial([P(*q) for q in sobe], prog0)
            if len(pts) > 1:
                traco(ctx, pts, lw=22, cor=INK, seed=seed + 13, amp=0.8)
                traco(ctx, pts, lw=12, cor=VERDE, seed=seed + 13, amp=0)
            if len(fim_px) > 1 and not explode:
                traco(ctx, fim_px, lw=22, cor=INK, seed=seed + 14, amp=0.8)
                traco(ctx, fim_px, lw=12, cor=VERMELHO, seed=seed + 14, amp=0)
                if p1 >= 1:   # buraco no chão do gráfico
                    bx_, by_ = fim_px[-1]
                    _explosao(ctx, bx_, gy1, 90, 40, hexc("#FFB020"), seed + 15, 10, t)
                    traco(ctx, [(bx_ - 90, gy1 + 10), (bx_ - 40, gy1 + 30), (bx_ - 60, gy1 + 50)], lw=5, seed=seed + 16)
                    traco(ctx, [(bx_ + 70, gy1 + 8), (bx_ + 40, gy1 + 34), (bx_ + 80, gy1 + 50)], lw=5, seed=seed + 17)
            _faixa(ctx, x0, y0, w, fh, hexc(st.get("cor_faixa", "#FFE27A")))
            textos.append(_tinta(ctx, "\n".join(linhas), 0, y0 + fh / 2, w - 100, tam, max_linhas=2))
    if explode and len(fim_px) > 1 and p0 > 0:   # foguete sai do quadro, rasgando a borda
        traco(ctx, fim_px, lw=22, cor=INK, seed=seed + 14, amp=0.8)
        traco(ctx, fim_px, lw=12, cor=VERMELHO, seed=seed + 14, amp=0)
        ex, ey = fim_px[-1]
        if p1 >= 1:
            _explosao(ctx, ex, ey, 70, 70, hexc("#FFB020"), seed + 18, 12, t)
            for k in range(5):
                a = t * 2 + k * 1.25
                _estrela(ctx, ex + math.cos(a) * 110, ey + math.sin(a) * 90, 18, AMARELO, seed + 19 + k, giro=t * 3)
    if p1 >= 0.95 and st.get("valor"):
        k = 1 + 0.06 * math.sin(t * 10)
        vx = gx0 + (gx1 - gx0) * 0.40; vy = gy0 + (gy1 - gy0) * (0.80 if not explode else 0.15)
        ctx.save(); ctx.translate(vx, vy); ctx.rotate(math.radians(-6)); ctx.scale(k, k)
        c = texto(ctx, st["valor"], 0, 0, st.get("tam", 120), cor=VERMELHO if not explode else hexc("#FF8A00"), max_w=w * 0.6)
        ctx.restore()
        textos.append((vx + c[0] * 1.08, vy + c[1] * 1.08 - 30, vx + c[2] * 1.08, vy + c[3] * 1.08 + 30))
    return textos, []


def f_legenda_choque(ctx, st, t, pal, seed, w, h):
    x0, y0 = -w / 2, -h / 2
    textos = []; caras = []
    tem_pers = bool(st.get("pers"))
    with Painel(ctx, (x0, y0, w, h), hexc(st.get("cor_cena", "#E8352A")), _p(st, 0), seed) as ok:
        if ok:
            cy = y0 + h * (0.36 if tem_pers else 0.5)
            _rajada(ctx, 0, cy, w * 0.30, w * 1.2, 46, seed, t, cor=BRANCO, alpha=0.55)
            _explosao(ctx, 0, cy, w * 0.50, h * (0.30 if tem_pers else 0.36), hexc(st.get("cor_explosao", "#FFD21F")), seed + 1, 16, t)
            if tem_pers and _p(st, 1) > 0:
                k = ease_out_back(_p(st, 1), 2.2)
                ctx.save(); ctx.translate(0, y0 + h); ctx.scale(k, k); ctx.translate(0, -(y0 + h))
                bx, _ = _pers(ctx, _st_pers(st, "choque", "pers_b"), 0, y0 + h * 0.66, h * 0.62, t, seed + 3)
                ctx.restore()
                caras.append(bx.get("rosto"))
            dx = math.sin(t * 71) * 9 + math.sin(t * 43) * 5
            dy = math.cos(t * 59) * 7
            ctx.save(); ctx.translate(dx, dy); ctx.rotate(math.radians(math.sin(t * 37) * 1.8))
            s = st.get("texto", "NÃO É POSSÍVEL").upper()
            c = _txt(ctx, s, 0, cy, w * 0.80, st.get("tam", 150), cor=BRANCO, max_linhas=3, entre=1.02)
            ctx.restore()
            if c:
                textos.append((c[0] - 16, c[1] - 14, c[2] + 16, c[3] + 14))
    return textos, caras


# ============================ formatos novos (pesquisa 24/11/2026) ============================
ROSTO = {"pipo": (-145, 190), "humano": (-255, 210)}   # centro (y local) e altura do rosto de cada personagem


def _rosto(ctx, sp, cx, cy, alt_rosto, t, seed, rot=0.0):
    """Desenha o personagem inteiro com o ROSTO centrado em (cx, cy) e `alt_rosto` px de rosto (o painel recorta o resto)."""
    tipo = sp.get("tipo", "pipo")
    top, base = ALT.get(tipo, ALT["humano"])
    rc, rh = ROSTO.get(tipo, ROSTO["humano"])
    e = alt_rosto / rh
    return _pers(ctx, sp, cx, cy - (rc - top) * e, e * (base - top) / sp.get("escala", 1), t, seed, rot=rot)


def _faixa_txt(ctx, st, chave, padrao, x0, y0, w, cor=INK, tam=60, linhas=2):
    """Faixa de título no topo do painel, com altura que cabe o texto. Devolve (altura, caixa)."""
    s = st.get(chave, padrao)
    if not s:
        return 0, None
    ls, tm = _quebra(ctx, s, w - 90, tam, linhas)
    fh = len(ls) * tm * 1.12 + 40
    _faixa(ctx, x0, y0, w, fh, cor)
    if cor == INK or sum(cor) < 1.3:
        c = _txt(ctx, "\n".join(ls), 0, y0 + fh / 2 + 2, w - 90, tm, max_linhas=linhas, sombra=False)
    else:
        c = _tinta(ctx, "\n".join(ls), 0, y0 + fh / 2 + 2, w - 90, tm, max_linhas=linhas)
    return fh, c


def _coracao(ctx, x, y, r, cor, seed, lw=5):
    pts = []
    for i in range(30):
        a = 2 * math.pi * i / 30
        px = 16 * math.sin(a) ** 3
        py = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((x + px * r / 16, y + py * r / 16))
    forma(ctx, pts, cor, sombra=False, lw=lw, seed=seed, amp=0.6)


def _carimbo_em(ctx, s, x, y, tam, cor, inclina, p, seed, fundo=None):
    """Carimbo que bate (cresce e assenta) em (x, y). Devolve a caixa do texto."""
    if p <= 0:
        return None
    k = 1 + 1.4 * (1 - clamp(p)) ** 2
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    ctx.push_group()
    if fundo is not None:
        tw_ = medir(ctx, s.upper(), tam) + 110
        ctx.save(); ctx.rotate(math.radians(inclina))
        forma(ctx, pts_ret(-tw_ / 2, -tam * 0.85, tw_, tam * 1.7, 20), fundo, sombra=True, lw=LW, seed=seed + 1, sombra_off=(6, 7))
        ctx.restore()
    b = B.desenha_carimbo(ctx, {"texto": s, "cor": cor, "inclina": inclina, "tam": tam}, 0, None, seed)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(clamp(p * 2))
    ctx.restore()
    c = b.get("texto")
    return (x + c[0] * k, y + c[1] * k, x + c[2] * k, y + c[3] * k) if c and p > 0.9 else None


def f_carregando(ctx, st, t, pal, seed, w, h):
    """Trend 'Recharged' / 'carregando...': bateria de 1% a 100% e a Pipo vai de acabada a pipoca. Anime `nivel`."""
    x0, y0 = -w / 2, -h / 2
    niv = clamp(st.get("nivel", 100) / 100)
    cheio = niv >= 0.995
    textos = []; caras = []
    fundo = mix(hexc("#6E6A80"), hexc(st.get("cor_cena", "#38C6B5")), niv)
    with Painel(ctx, (x0, y0, w, h), fundo, _p(st, 0), seed) as ok:
        if ok:
            bh = 150; by = y0 + h - bh - 44
            if cheio:
                _rajada(ctx, 0, y0 + h * 0.45, w * 0.22, w * 1.1, 40, seed, t, cor=BRANCO, alpha=0.35)
            else:   # quanto menos carga, mais "pesado" o ar: listrinhas caindo
                for k in range(6):
                    yy = y0 + 160 + ((t * 120 * (1.2 - niv) + k * 90) % 420)
                    traco(ctx, [(x0 + 70 + k * 150, yy), (x0 + 70 + k * 150, yy + 30)], lw=5, alpha=0.25 * (1 - niv), seed=seed + k)
            fh, c = _faixa_txt(ctx, st, "texto", "eu depois do primeiro café", x0, y0, w)
            textos.append(c)
            expr = "acabado" if niv < 0.34 else "nada" if niv < 0.67 else "feliz" if not cheio else "empolgado"
            sp = _st_pers(st, expr, "pers_a")
            if cheio and sp.get("tipo", "pipo") == "pipo" and st.get("vira_pipoca", True):
                sp["forma"] = "pipoca"; sp["boca"] = "sorriso"; sp["palpebra"] = 0.0
            topo = y0 + fh + 30 + (1 - niv) * 70
            alt = (by - 24 - topo) * 1.15
            bx, _ = _pers(ctx, sp, 0, topo, alt, t, seed + 3, rot=(1 - niv) * -9)
            caras.append(bx.get("rosto"))
            if cheio:
                for k in range(6):
                    a = t * 1.2 + k * 1.05
                    _brilho(ctx, math.cos(a) * w * 0.36, y0 + h * 0.45 + math.sin(a) * h * 0.2, 30, t, seed + 40 + k)
            # bateria deitada
            bw = w * 0.66; bx0 = -bw / 2 - 14
            forma(ctx, pts_ret(bx0 + bw, by + bh * 0.3, 30, bh * 0.4, 8), BRANCO, sombra=False, lw=LW, seed=seed + 5)
            forma(ctx, pts_ret(bx0, by, bw, bh, 30), INK, sombra=True, lw=LW, seed=seed + 6, sombra_off=(8, 9))
            cor = mix(VERMELHO, AMARELO, clamp(niv * 2)) if niv < 0.5 else mix(AMARELO, VERDE, clamp(niv * 2 - 1))
            fw = (bw - 32) * max(0.04, niv)
            forma(ctx, pts_ret(bx0 + 16, by + 16, fw, bh - 32, 18), cor, sombra=False, lw=4, seed=seed + 7, amp=0.4)
            c = texto(ctx, f"{int(round(niv * 100))}%", bx0 + bw / 2, by + bh / 2, 92, cor=BRANCO)
            textos.append(c)
            # raio de carregando ao lado
            rx, ry = bx0 - 70, by + bh / 2
            kk = 1 + 0.12 * math.sin(t * 8)
            ctx.save(); ctx.translate(rx, ry); ctx.scale(kk, kk)
            forma(ctx, [(10, -62), (-30, 8), (-4, 8), (-14, 62), (30, -10), (4, -10)], AMARELO, sombra=True, lw=5, seed=seed + 8, sombra_off=(5, 6))
            ctx.restore()
    return textos, caras


EXPR_SEQ = ["feliz", "aprova", "nada", "nervoso", "acabado"]


def f_estagios(ctx, st, t, pal, seed, w, h):
    """Trend '5 estágios de...': do confiante ao destruído, uma linha por estágio com a cara da Pipo."""
    itens = st.get("estagios") or ["isso é fácil", "hmm, peraí", "tá tudo sob controle", "PÂNICO", "aceitei"]
    n = len(itens); x0, y0, g = -w / 2, -h / 2, 12
    textos = []; caras = []
    titulo = st.get("titulo") or f"{n} estágios de {st.get('texto', 'fazer o trabalho na véspera')}"
    ls, tm = _quebra(ctx, titulo, w - 90, 58, 2)
    fh = len(ls) * tm * 1.12 + 40
    with Painel(ctx, (x0, y0, w, fh), INK, _p(st, 0), seed) as ok:
        if ok:
            textos.append(_txt(ctx, "\n".join(ls), 0, y0 + fh / 2 + 2, w - 90, tm, max_linhas=2, sombra=False))
    rh = (h - fh - g * n) / n
    exprs = st.get("exprs") or [EXPR_SEQ[round(i * (len(EXPR_SEQ) - 1) / max(1, n - 1))] for i in range(n)]
    for i, s in enumerate(itens):
        p = _p(st, i); y = y0 + fh + g + i * (rh + g); b = i / max(1, n - 1)
        cor = mix(hexc("#9BF0A8"), hexc("#FF8A80"), b)
        with Painel(ctx, (x0, y, w, rh), cor, p, seed + 10 + i, rot=(-1.2 if i % 2 else 1.2)) as ok:
            if ok:
                forma(ctx, pts_elipse(x0 + 62, y + rh / 2, 38, 38, 16), BRANCO, sombra=False, lw=5, seed=seed + 20 + i)
                textos.append(_tinta(ctx, str(i + 1), x0 + 62, y + rh / 2 + 2, 70, 56, max_linhas=1))
                fx = x0 + w - rh * 0.75
                fundo_r = mix(cor, BRANCO, 0.45)
                forma(ctx, pts_elipse(fx, y + rh / 2, rh * 0.62, rh * 0.62, 20), fundo_r, sombra=False, lw=0, seed=seed + 30 + i)
                sp = _st_pers(st, exprs[i], "pers_" + "abcdefg"[min(i, 6)])
                bx, _ = _rosto(ctx, sp, fx, y + rh * 0.52, rh * 0.70, t, seed + 40 + i, rot=(b - 0.5) * 14 + math.sin(t * (3 + 6 * b)) * 2 * b)
                caras.append(bx.get("rosto"))
                if b > 0.7:
                    _gota(ctx, fx + rh * 0.42, y + rh * 0.3, 13, seed + 50 + i)
                textos.append(_tinta(ctx, s, x0 + 122, y + rh / 2 + 2, w - 122 - rh * 1.5, st.get("tam", 58), max_linhas=2, ancora="l"))
    return textos, caras


MESES = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


def f_retrospectiva(ctx, st, t, pal, seed, w, h):
    """Trend 'sinto que não fiz nada esse ano': um quadrinho por mês, provando o contrário (ou não)."""
    x0, y0, g = -w / 2, -h / 2, 12
    meses = st.get("meses") or ["virei o ano", "dieta", "desisti", "fiz nada", "dormi", "quentão", "dormi mais",
                                "boleto", "calor", "provas", "promoção", "estourei"]
    n = len(meses); cols = st.get("colunas", 3); rows = math.ceil(n / cols)
    textos = []
    ls, tm = _quebra(ctx, st.get("texto", "sinto que não fiz nada esse ano..."), w - 70, 54, 2)
    fh = len(ls) * tm * 1.12 + 40
    with Painel(ctx, (x0, y0, w, fh), INK, _p(st, 0), seed) as ok:
        if ok:
            textos.append(_txt(ctx, "\n".join(ls), 0, y0 + fh / 2 + 2, w - 90, tm, max_linhas=2, sombra=False))
    cw = (w - g * (cols - 1)) / cols; ch = (h - fh - g * rows) / rows
    cores = ["#9BE3FF", "#FFE27A", "#FFB3C7", "#B8F2A6", "#D7C2FF", "#FFC48A"]
    dest = st.get("destaque", n - 1)
    for i, s in enumerate(meses):
        p = _p(st, i); cx = x0 + (i % cols) * (cw + g); cy = y0 + fh + g + (i // cols) * (ch + g)
        final = i == dest and _p(st, n - 1) >= 1
        cor = hexc("#FFC21A") if final else hexc(cores[i % len(cores)])
        with Painel(ctx, (cx, cy, cw, ch), cor, p, seed + 10 + i, rot=((i * 37) % 5 - 2) * 0.8) as ok:
            if ok:
                if final:
                    _rajada(ctx, cx + cw / 2, cy + ch / 2, cw * 0.25, cw, 22, seed + 3, t, cor=BRANCO, alpha=0.5)
                rot = st.get("rotulos") or MESES
                lab = rot[i % len(rot)]
                lw_ = medir(ctx, lab, 48) + 34
                forma(ctx, pts_ret(cx + cw / 2 - lw_ / 2, cy + 10, lw_, 56, 18), INK, sombra=False, lw=0, seed=seed + 30 + i)
                textos.append(texto(ctx, lab, cx + cw / 2, cy + 40, 48, cor=AMARELO if not final else BRANCO, sombra=False, lw=0, contorno=None))
                textos.append(_tinta(ctx, s, cx + cw / 2, cy + 66 + (ch - 66) / 2, cw - 24, 50, max_linhas=2))
                if final:
                    _brilho(ctx, cx + cw - 26, cy + 30, 22, t, seed + 60)
                    _brilho(ctx, cx + 26, cy + ch - 26, 18, t, seed + 61)
    return textos, []


def f_carta_noel(ctx, st, t, pal, seed, w, h):
    """Trend 'Querido Papai Noel, eu visto tamanho...': a carta e a resposta que não tem tamanho."""
    x0, y0 = -w / 2, -h / 2
    textos = []; caras = []
    p1 = _p(st, 1)
    with Painel(ctx, (x0, y0, w, h), hexc(st.get("cor_cena", "#D9322B")), _p(st, 0), seed) as ok:
        if ok:
            rng = random.Random(seed)
            for k in range(26):   # bolinhas de enfeite ao fundo
                ctx.arc(x0 + rng.uniform(0, w), y0 + rng.uniform(0, h), rng.uniform(6, 16), 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.18); ctx.fill()
            px, py, pw, ph = x0 + 56, y0 + 44, w - 112, h - 250
            forma(ctx, pts_ret(px, py, pw, ph, 12), hexc("#FFF4DA"), sombra=True, lw=LW, seed=seed + 1, sombra_off=(9, 11))
            for k in range(1, 9):   # pautas
                yy = py + 40 + k * (ph - 60) / 9
                traco(ctx, [(px + 30, yy), (px + pw - 30, yy)], lw=3, cor=hexc("#7FB3E8"), alpha=0.55, seed=seed + 10 + k, amp=0.5)
            traco(ctx, [(px + 70, py + 10), (px + 70, py + ph - 10)], lw=3, cor=VERMELHO, alpha=0.5, seed=seed + 9, amp=0.4)
            textos.append(_tinta(ctx, st.get("inicio", "Querido Papai Noel,\neu visto tamanho:"), px + 96, py + 120, pw - 130, 64,
                                 max_linhas=3, ancora="l"))
            if p1 > 0:   # resposta escrita à mão, com rabisco em volta
                k = ease_out_back(p1, 2.0)
                cx, cy = px + pw / 2, py + ph * 0.66
                ctx.save(); ctx.translate(cx, cy); ctx.rotate(math.radians(-4)); ctx.scale(k, k)
                c = _txt(ctx, st.get("tamanho", "férias de 3 meses"), 0, 0, pw - 120, st.get("tam", 84), cor=hexc("#C8102E"),
                         contorno=None, sombra=False, max_linhas=3)
                if c:
                    pts = [(math.cos(a) * ((c[2] - c[0]) / 2 + 40) * (1 + 0.05 * math.sin(a * 3)), math.sin(a) * ((c[3] - c[1]) / 2 + 34))
                           for a in [i * 0.3 for i in range(23)]]
                    traco(ctx, pts, lw=6, cor=hexc("#C8102E"), seed=seed + 20, amp=1.2)
                ctx.restore()
                if c:
                    textos.append((cx + c[0] - 30, cy + c[1] - 40, cx + c[2] + 30, cy + c[3] + 40))
            sp = _st_pers(st, "maroto" if p1 > 0 else "feliz", "pers_a")
            bx, esc = _pers(ctx, sp, x0 + w * 0.76, y0 + h - 300, 620, t, seed + 3, rot=-6)
            caras.append(bx.get("rosto"))
            ro = bx.get("rosto") or (0, 0, 0, 0)
            # lápis na mão
            lx, ly = ro[0] - 40, ro[3] + 40
            ctx.save(); ctx.translate(lx, ly); ctx.rotate(math.radians(-35 + math.sin(t * 9) * 6 * (1 if p1 < 1 else 0.2)))
            forma(ctx, pts_ret(-14, -110, 28, 150, 6), AMARELO, sombra=False, lw=5, seed=seed + 30)
            forma(ctx, [(-14, 40), (14, 40), (0, 76)], hexc("#F3C89A"), sombra=False, lw=5, seed=seed + 31)
            forma(ctx, pts_ret(-14, -130, 28, 24, 6), hexc("#FF8FB8"), sombra=False, lw=5, seed=seed + 32)
            ctx.restore()
            _mao(ctx, "pare", lx + 10, ly + 30, 0.55, -20, _cor_mao(sp), seed + 33)
            for k, (ex, ey) in enumerate(((0.08, 0.93), (0.32, 0.95), (0.5, 0.9))):
                _estrela(ctx, x0 + w * ex + 20, y0 + h * ey, 24, AMARELO, seed + 40 + k, giro=t + k)
    return textos, caras


def f_soft_launch(ctx, st, t, pal, seed, w, h):
    """Trend 'soft launch' (My Moon My Man, sem o áudio): só uma pista do novo amor, depois a revelação absurda."""
    x0, y0 = -w / 2, -h / 2
    textos = []; caras = []
    p1 = _p(st, 1)
    with Painel(ctx, (x0, y0, w, h), hexc(st.get("cor_cena", "#FF8FB8")), _p(st, 0), seed) as ok:
        if ok:
            fh, c = _faixa_txt(ctx, st, "texto", "soft launch do meu novo amor", x0, y0, w)
            textos.append(c)
            # quadro do amor (direita)
            fx, fy, fw, fhh = x0 + w * 0.42, y0 + fh + 60, w * 0.52, h - fh - 120
            mx, my = fx + fw / 2, fy + fhh * 0.42
            if p1 > 0:
                for k in range(8):   # coraçõezinhos subindo
                    u = (t * 0.5 + k * 0.13) % 1.0
                    _coracao(ctx, fx + fw * ((k * 0.37) % 1), fy + fhh - u * fhh, 20 + 8 * (k % 3), hexc("#FF3D7F"), seed + 60 + k)
                k = ease_out_back(clamp(p1 * 1.3), 2.2)
                ctx.save(); ctx.translate(mx, my); ctx.scale(k, k)
                _coracao(ctx, 0, 0, fw * 0.52, BRANCO, seed + 10, lw=LW + 2)
                ctx.restore()
                c = _tinta(ctx, st.get("amor", "o ventilador"), mx, my - 10, fw * 0.80, st.get("tam", 62), max_linhas=3)
                if p1 >= 1:
                    textos.append(c)
                cy_ = fy + fhh - 60
                textos.append(_carimbo_em(ctx, st.get("carimbo", "OFICIAL"), mx, cy_, 64, "#C8102E", -8, clamp(p1 * 2 - 1), seed + 70, fundo=BRANCO))
            # cortina por cima (sobe na revelação)
            sobe = clamp(p1) * (fhh + 40)
            if sobe < fhh + 30:
                ctx.save(); ctx.rectangle(fx - 10, fy - 30, fw + 20, fhh + 60); ctx.clip()
                cy0 = fy - sobe
                forma(ctx, pts_ret(fx, cy0, fw, fhh, 16), hexc("#6B2FA0"), sombra=True, lw=LW, seed=seed + 20)
                for k in range(1, 5):
                    traco(ctx, [(fx + fw * k / 5, cy0 + 10), (fx + fw * k / 5 + 8, cy0 + fhh / 2), (fx + fw * k / 5, cy0 + fhh - 10)],
                          lw=4, alpha=0.45, seed=seed + 21 + k)
                if p1 <= 0:   # a pista: uma sombra misteriosa espiando + "?"
                    ox = math.sin(t * 2) * 10
                    forma(ctx, pts_elipse(fx + fw - 30 + ox, cy0 + fhh * 0.45, 46, 70, 18), hexc("#2B1A3A"), sombra=False, lw=5, seed=seed + 25)
                    c = texto(ctx, "?", fx + fw / 2, cy0 + fhh * 0.45, 150, cor=AMARELO)
                    textos.append(c)
                ctx.restore()
            # Pipo apaixonada (esquerda)
            sp = _st_pers(st, "empolgado" if p1 > 0 else "maroto", "pers_a")
            bx, _ = _pers(ctx, sp, x0 + w * 0.22, y0 + fh + 110, (h - fh) * 0.95, t, seed + 3, rot=6 * math.sin(t * 2))
            ro = bx.get("rosto")
            caras.append(ro)
            if ro:
                for k in range(3):
                    a = t * 2 + k * 2.1
                    _coracao(ctx, (ro[0] + ro[2]) / 2 + math.cos(a) * 130, ro[1] - 40 + math.sin(a) * 30, 22, hexc("#FF3D7F"), seed + 80 + k)
    return textos, caras


def f_remoendo(ctx, st, t, pal, seed, w, h):
    """Trend 'paid me no mind' / remoendo: a mesma mensagem relida com outra ênfase e outra cara a cada vez."""
    x0, y0, g = -w / 2, -h / 2, 14
    leit = st.get("leituras") or ["ok.", "ok?", "OK.", "o...k."]
    n = len(leit); cols = 2; rows = math.ceil(n / cols)
    textos = []; caras = []
    bh = 200
    with Painel(ctx, (x0, y0, w, bh), hexc(st.get("cor_a", "#DCEBFF")), _p(st, 0), seed) as ok:
        if ok:
            forma(ctx, pts_elipse(x0 + 80, y0 + bh / 2, 44, 44, 16), hexc(st.get("cor_avatar", "#FF8A3D")), sombra=False, lw=5, seed=seed + 1)
            bx0 = x0 + 150
            forma(ctx, [(bx0, y0 + bh / 2), (bx0 + 26, y0 + bh / 2 - 22), (bx0 + 26, y0 + bh / 2 + 18)], BRANCO, sombra=False, lw=5, seed=seed + 2)
            forma(ctx, pts_ret(bx0 + 20, y0 + 30, w - 200, bh - 60, 30), BRANCO, sombra=True, lw=LW, seed=seed + 3, sombra_off=(6, 7))
            textos.append(_tinta(ctx, st.get("de", "@amiga") + ":  " + st.get("mensagem", "ok."), bx0 + 56, y0 + bh / 2 + 2, w - 270, 62,
                                 max_linhas=2, ancora="l"))
    cw = (w - g * (cols - 1)) / cols; ch = (h - bh - g * rows) / rows
    exprs = st.get("exprs") or ["nada", "choque", "nervoso", "acabado", "recusa", "maroto"]
    cores = ["#FFE27A", "#FF8A80", "#B18CFF", "#9AA0B4", "#8FD3FF", "#B8F2A6"]
    for i, s in enumerate(leit):
        p = _p(st, i + 1); cx = x0 + (i % cols) * (cw + g); cy = y0 + bh + g + (i // cols) * (ch + g)
        with Painel(ctx, (cx, cy, cw, ch), hexc(cores[i % len(cores)]), p, seed + 10 + i, rot=(1.5 if i % 2 else -1.5)) as ok:
            if ok:
                sp = _st_pers(st, exprs[i % len(exprs)], "pers_" + "abcdef"[min(i, 5)])
                tre = math.sin(t * 40) * 3 if exprs[i % len(exprs)] == "nervoso" else 0
                bx, _ = _rosto(ctx, sp, cx + cw / 2 + tre, cy + ch * 0.68, ch * 0.5, t, seed + 20 + i)
                caras.append(bx.get("rosto"))
                tam = st.get("tam", 78) * (1.0 + 0.12 * (i % 2))
                cor = [INK, VERMELHO, hexc("#5B2A86"), hexc("#3B3850")][i % 4]
                ls, tm = _quebra(ctx, s, cw - 50, tam, 1)
                tw_ = medir(ctx, ls[0], tm) + 50
                forma(ctx, pts_ret(cx + cw / 2 - tw_ / 2, cy + 18, tw_, tm * 1.25, 20), BRANCO, sombra=False, lw=5, seed=seed + 30 + i)
                textos.append(_txt(ctx, ls[0], cx + cw / 2, cy + 18 + tm * 0.64, cw - 50, tm, cor=cor, contorno=None, sombra=False, max_linhas=1))
                if exprs[i % len(exprs)] in ("nervoso", "acabado"):
                    _gota(ctx, cx + cw / 2 + ch * 0.3, cy + ch * 0.55, 14, seed + 40 + i)
    return textos, caras


def f_vai_vai_vai(ctx, st, t, pal, seed, w, h):
    """Trend 'go go go': algo lento demais e a Pipo torcendo 'VAI VAI VAI'. Anime `revela` de 1 a 2 com dur: os VAI vão brotando."""
    x0, y0 = -w / 2, -h / 2
    textos = []; caras = []
    p1 = _p(st, 1)
    with Painel(ctx, (x0, y0, w, h), hexc(st.get("cor_cena", "#FFB347")), _p(st, 0), seed) as ok:
        if ok:
            if p1 > 0:
                _rajada(ctx, 0, y0 + h * 0.75, w * 0.3, w * 1.2, 36, seed, t, cor=BRANCO, alpha=0.35 * p1)
            fh, c = _faixa_txt(ctx, st, "texto", "o download nos últimos 1%", x0, y0, w)
            textos.append(c)
            # visor com a barra que não anda
            vx, vy, vw, vh = x0 + 90, y0 + fh + 30, w - 180, 170
            forma(ctx, pts_ret(vx, vy, vw, vh, 22), hexc("#2B2238"), sombra=True, lw=LW, seed=seed + 1, sombra_off=(7, 8))
            prog = clamp(st.get("progresso", 0.99)) + 0.002 * math.sin(t * 3)
            forma(ctx, pts_ret(vx + 26, vy + vh - 66, vw - 52, 40, 16), hexc("#4A4060"), sombra=False, lw=4, seed=seed + 2)
            forma(ctx, pts_ret(vx + 26, vy + vh - 66, (vw - 52) * prog, 40, 16), VERDE, sombra=False, lw=4, seed=seed + 3, amp=0.3)
            textos.append(texto(ctx, st.get("rotulo", f"{int(prog * 100)}%"), vx + vw / 2, vy + 58, 64, cor=hexc("#7CFF8A"), sombra=False, lw=0, contorno=None))
            # Pipo debruçada, tremendo
            tre = math.sin(t * 45) * (2 + 6 * p1)
            sp = _st_pers(st, "nervoso", "pers_a", olhar="cima")
            topo = vy + vh + 30
            bx, _ = _pers(ctx, sp, tre, topo, (y0 + h - topo) * 1.25, t, seed + 4, rot=4 * math.sin(t * 6) * p1)
            ro = bx.get("rosto") or bx.get("corpo")
            caras.append(ro)
            _gota(ctx, ro[2] - 10, ro[1] + 20, 18, seed + 5)
    # os VAI brotam em volta (fora do recorte, por cima de tudo)
    if p1 > 0:
        pos = [(-0.33, 0.50, 96, -8), (0.33, 0.47, 104, 7), (-0.30, 0.68, 84, 6), (0.31, 0.66, 92, -6),
               (-0.32, 0.86, 110, -4), (0.32, 0.84, 118, 5)]
        nv = min(len(pos), int(p1 * len(pos) + 0.999))
        g = st.get("grito", "VAI")
        for k in range(nv):
            dx, dy, tam, rot = pos[k]
            loc = clamp((p1 * len(pos)) - k)
            kk = ease_out_back(loc, 2.4) * (1 + 0.05 * math.sin(t * 14 + k))
            x, y = dx * w, y0 + dy * h
            ctx.save(); ctx.translate(x + math.sin(t * 50 + k) * 3, y); ctx.scale(kk, kk)
            c = texto(ctx, g, 0, 0, tam, cor=BRANCO if k % 2 else AMARELO)
            ctx.restore()
            if loc >= 1:
                textos.append((x + c[0] - 6, y + c[1] - 6, x + c[2] + 6, y + c[3] + 6))
    return textos, caras


def f_nao_nao_sim(ctx, st, t, pal, seed, w, h):
    """Trend 'não, não, não... SIM!': coisas chatas carimbadas NÃO em sequência e a última vira festa."""
    itens = st.get("itens") or ["acordar cedo", "reunião que era e-mail", "calor de 40 graus", "sextou"]
    n = len(itens); x0, y0, g = -w / 2, -h / 2, 14
    textos = []; caras = []
    rs = st.get("altura_linha", 126)
    for i, s in enumerate(itens[:-1]):
        p = _p(st, i); y = y0 + i * (rs + g)
        with Painel(ctx, (x0, y, w, rs), BRANCO, p, seed + i, rot=(-1 if i % 2 else 1)) as ok:
            if ok:
                textos.append(_tinta(ctx, s, x0 + 40, y + rs / 2 + 2, w - 380, st.get("tam", 56), max_linhas=2, ancora="l"))
                sp = _st_pers(st, "recusa", "pers_a")
                forma(ctx, pts_elipse(x0 + w - 70, y + rs / 2, 56, 56, 16), hexc("#FFD6D1"), sombra=False, lw=0, seed=seed + 5 + i)
                bx, _ = _rosto(ctx, sp, x0 + w - 70, y + rs * 0.56, rs * 0.72, t, seed + 10 + i, rot=-8)
                caras.append(bx.get("rosto"))
        if p >= 0.6:
            textos.append(_carimbo_em(ctx, st.get("nao", "NÃO"), x0 + w - 270, y + rs / 2, 60, "#E8352A", -9, clamp((p - 0.6) / 0.4), seed + 20 + i))
    yf = y0 + (n - 1) * (rs + g); hf = h - (yf - y0)
    pf = _p(st, n - 1)
    with Painel(ctx, (x0, yf, w, hf), hexc(st.get("cor_sim", "#3DDC84")), pf, seed + 40) as ok:
        if ok:
            _rajada(ctx, x0 + w * 0.7, yf + hf * 0.6, w * 0.2, w * 1.1, 40, seed + 41, t, cor=BRANCO, alpha=0.45)
            textos.append(_txt(ctx, itens[-1], 0, yf + 64, w - 80, st.get("tam_sim", 76), max_linhas=1))
            sp = _st_pers(st, "empolgado", "pers_b")
            bx, _ = _pers(ctx, sp, x0 + w * 0.70, yf + 120 - 14 * abs(math.sin(t * 6)), (hf - 100) * 1.25, t, seed + 42, rot=8 * math.sin(t * 5))
            caras.append(bx.get("rosto"))
            for k in range(5):
                a = t * 1.5 + k * 1.25
                _estrela(ctx, x0 + w * 0.70 + math.cos(a) * 230, yf + hf * 0.55 + math.sin(a) * 110, 22, AMARELO, seed + 50 + k, giro=t * 2)
    if pf > 0:
        textos.append(_carimbo_em(ctx, st.get("sim", "SIM!"), x0 + w * 0.26, yf + hf * 0.58, 120, "#1E7B34", -12, pf, seed + 60, fundo=BRANCO))
    return textos, caras


def _cadeira(ctx, x, y, larg, alt, cor, seed):
    """Encosto de cadeira atrás de um personagem (topo em y)."""
    forma(ctx, pts_ret(x - larg / 2, y, larg, alt, 30), cor, sombra=True, lw=LW, seed=seed, sombra_off=(6, 8))
    forma(ctx, pts_ret(x - larg / 2 + 22, y + 22, larg - 44, alt * 0.5, 20), clareia(cor, 0.25), sombra=False, lw=4, seed=seed + 1)


def f_nao_julgamos(ctx, st, t, pal, seed, w, h):
    """Trend 'a gente escuta e não julga': roda de conversa, a confissão inofensiva e a plateia que... julga um pouquinho."""
    x0, y0 = -w / 2, -h / 2
    textos = []; caras = []
    p1, p2 = _p(st, 1), _p(st, 2)
    with Painel(ctx, (x0, y0, w, h), hexc(st.get("cor_cena", "#8FC1FF")), _p(st, 0), seed) as ok:
        if ok:
            fh, c = _faixa_txt(ctx, st, "titulo", "a gente escuta e não julga", x0, y0, w)
            textos.append(c)
            chao = y0 + h * 0.78
            forma(ctx, pts_elipse(0, chao, w * 0.55, 80, 30), hexc("#F2C46D"), sombra=False, lw=LW, seed=seed + 1)   # tapete
            ouv = st.get("ouvintes") or [{"tipo": "humano", "cabelo": "coque", "cabelo_cor": "ruivo", "pele": "clara", "roupa": "#16A57A"},
                                         {"tipo": "humano", "cabelo": "cacheado", "pele": "escura", "roupa": "#E8452C"}]
            reac = st.get("reacoes") or ["feliz", "surpreso", "neutro"]
            for k, e in enumerate(ouv):
                hx = x0 + w * (0.58 + 0.27 * k)
                topo = y0 + h * 0.50
                _cadeira(ctx, hx, topo - 20, 230, 300, hexc("#8B5A2B"), seed + 10 + k)
                sp = {"tipo": "humano"}; sp.update(EXPR["nada"]); sp.update(e); sp["_t"] = t; sp["_estouro"] = None
                sp["olhar"] = "esq"
                if p2 > 0:
                    sp["expressao"] = reac[k % len(reac)]
                bob = 10 * abs(math.sin(t * 5)) if (p2 > 0 and sp["expressao"] == "feliz") else 0
                bx, _ = _pers(ctx, sp, hx, topo + bob, h * 0.46, t, seed + 20 + k)
                ro = bx.get("rosto"); caras.append(ro)
                if p2 > 0 and sp["expressao"] == "surpreso" and ro:
                    _gota(ctx, ro[2] + 6, ro[1] + 26, 16, seed + 30 + k)
                    _gota(ctx, ro[0] - 6, ro[1] + 50, 12, seed + 31 + k)
            _cadeira(ctx, x0 + w * 0.22, y0 + h * 0.40, 280, 380, hexc("#6B2FA0"), seed + 40)
            sp = _st_pers(st, "nervoso" if p1 > 0 else "nada", "pers_a", olhar="camera")
            bx, _ = _pers(ctx, sp, x0 + w * 0.22, y0 + h * 0.43, h * 0.56, t, seed + 41)
            caras.append(bx.get("rosto"))
    if p1 > 0:   # balão da confissão
        k = ease_out_back(p1, 2.2)
        bx0, by0, bw, bh = x0 + w * 0.40, y0 + 150, w * 0.56, 230
        ctx.save(); ctx.translate(bx0 + bw * 0.2, by0 + bh); ctx.scale(k, k); ctx.translate(-(bx0 + bw * 0.2), -(by0 + bh))
        forma(ctx, [(bx0 + 40, by0 + bh - 10), (bx0 - 70, by0 + bh + 90), (bx0 + 110, by0 + bh - 6)], BRANCO, sombra=False, lw=LW, seed=seed + 50)
        forma(ctx, pts_ret(bx0, by0, bw, bh, 40), BRANCO, sombra=True, lw=LW, seed=seed + 51, sombra_off=(7, 8))
        forma(ctx, pts_ret(bx0 + 34, by0 + bh - 26, 100, 40, 10), BRANCO, sombra=False, lw=0, seed=seed + 52)
        c = _tinta(ctx, st.get("confissao", "eu como o recheio e devolvo a bolacha"), bx0 + bw / 2, by0 + bh / 2, bw - 50, st.get("tam", 54), max_linhas=4)
        ctx.restore()
        if c and p1 >= 1:
            textos.append(c)
    if p2 > 0 and st.get("reacao"):
        k = ease_out_back(p2, 2.4)
        rx, ry = x0 + w * 0.80, y0 + h * 0.47
        ctx.save(); ctx.translate(rx, ry); ctx.scale(k, k)
        tw_ = medir(ctx, st["reacao"], 52) + 50
        forma(ctx, pts_ret(-tw_ / 2, -40, tw_, 80, 30), BRANCO, sombra=True, lw=5, seed=seed + 60, sombra_off=(5, 6))
        c = _tinta(ctx, st["reacao"], 0, 2, tw_, 52, max_linhas=1)
        ctx.restore()
        if c and p2 >= 1:
            textos.append((rx + c[0], ry + c[1], rx + c[2], ry + c[3]))
    return textos, caras


def f_distraida(ctx, st, t, pal, seed, w, h):
    """Trend 'getting robbed': a Pipo presa no celular enquanto uma mão leva embora algo precioso. Anime `revela` 1 -> 2 com dur."""
    x0, y0 = -w / 2, -h / 2
    textos = []; caras = []
    p1 = _p(st, 1)
    with Painel(ctx, (x0, y0, w, h), hexc(st.get("cor_cena", "#9AD7FF")), _p(st, 0), seed) as ok:
        if ok:
            chao = y0 + h * 0.84
            ctx.rectangle(x0, chao, w, h); ctx.set_source_rgb(*hexc(st.get("cor_chao", "#C99A6B"))); ctx.fill()
            traco(ctx, [(x0, chao), (0, chao + 2), (x0 + w, chao)], lw=LW, seed=seed + 1)
            # relógio de parede: já são 3 da manhã (`hora` 0..12)
            rx, ry, rr = x0 + w * 0.70, y0 + h * 0.33, 62
            forma(ctx, pts_elipse(rx, ry, rr, rr, 24), BRANCO, sombra=True, lw=LW, seed=seed + 2, sombra_off=(5, 6))
            hr = st.get("hora", 3) + t / 30
            for ang, ln, lw_ in ((hr / 12, rr * 0.5, 9), (t / 4 % 1, rr * 0.78, 6)):
                a_ = 2 * math.pi * ang - math.pi / 2
                traco(ctx, [(rx, ry), (rx + math.cos(a_) * ln, ry + math.sin(a_) * ln)], lw=lw_, seed=seed + 3, amp=0)
            fh, c = _faixa_txt(ctx, st, "texto", "eu vendo 'só mais um vídeo'", x0, y0, w)
            textos.append(c)
            # o saco precioso (atrás, à direita); arrastado na revelação
            ida = clamp(p1 / 0.45); arrasta = clamp((p1 - 0.45) / 0.55)
            sx = x0 + w * 0.70 + arrasta * w * 0.10 + (math.sin(t * 30) * 3 if 0 < arrasta < 1 else 0)
            sy = y0 + h * 0.66
            if arrasta > 0:
                for k in range(3):
                    traco(ctx, [(sx - 190 - k * 10, sy + 40 + k * 40), (sx - 120 - k * 10, sy + 40 + k * 40)], lw=6, alpha=0.5, seed=seed + 10 + k)
            forma(ctx, [(sx - 30, sy - 140), (sx + 30, sy - 140), (sx + 18, sy - 110), (sx + 150, sy - 40), (sx + 150, sy + 120),
                        (sx - 150, sy + 120), (sx - 150, sy - 40), (sx - 18, sy - 110)], hexc("#B07A4A"), sombra=True, sombreado=0.12, lw=LW, seed=seed + 4)
            traco(ctx, [(sx - 34, sy - 110), (sx + 34, sy - 112)], lw=10, cor=hexc("#6B3E1F"), seed=seed + 5)
            tw, th = 260, 150
            ctx.save(); ctx.translate(sx, sy + 10); ctx.rotate(math.radians(-4))
            forma(ctx, pts_ret(-tw / 2, -th / 2, tw, th, 14), BRANCO, sombra=False, lw=5, seed=seed + 6)
            c = _tinta(ctx, st.get("roubado", "minhas 8 horas de sono"), 0, 0, tw - 30, st.get("tam", 50), max_linhas=3)
            ctx.restore()
            if c:
                textos.append((sx + c[0] - 12, sy + 10 + c[1] - 12, sx + c[2] + 12, sy + 10 + c[3] + 12))
            # a mão sorrateira entra pela direita
            if p1 > 0:   # vem de fora, agarra o nó do saco e puxa
                hx = x0 + w + 120 + ida * ((sx + 30) - (x0 + w + 120))
                hy = sy - 132
                ombro = (x0 + w + 100, hy - 110)
                traco(ctx, [ombro, ((ombro[0] + hx) / 2 + 20, hy - 90), (hx + 40, hy - 10)], lw=60, seed=seed + 20)
                traco(ctx, [ombro, ((ombro[0] + hx) / 2 + 20, hy - 90), (hx + 40, hy - 10)], lw=42, cor=hexc("#3B3850"), seed=seed + 20, amp=0)
                luva = hexc(st.get("cor_luva", "#2B2238"))
                forma(ctx, pts_elipse(hx + 26, hy, 52, 40, 16), luva, sombra=True, lw=5, seed=seed + 21, sombra_off=(5, 6))
                for k in range(3):   # dedos fechados no nó
                    forma(ctx, pts_elipse(hx - 14, hy - 22 + k * 22, 22, 13, 10), luva, sombra=False, lw=5, seed=seed + 22 + k)
            # Pipo no celular, feliz e alheia
            sp = _st_pers(st, "feliz", "pers_a", segura="celular", olhar="celular")
            bx, _ = _pers(ctx, sp, x0 + w * 0.30, y0 + fh + 70, (chao - (y0 + fh + 70)) * 1.05, t, seed + 30)
            caras.append(bx.get("rosto"))
            ro = bx.get("rosto")
            if ro:
                for k in range(3):   # notinhas de "tô de boa"
                    a = t * 2 + k * 2.1
                    _coracao(ctx, ro[0] - 40 + k * 30 + math.cos(a) * 10, ro[1] - 30 - ((t * 40 + k * 30) % 80), 14, hexc("#FF3D7F"), seed + 40 + k)
    return textos, caras


FORMATOS = {"aprova_reprova": (f_aprova_reprova, 2), "expectativa_realidade": (f_expectativa_realidade, 2),
            "ninguem_eu": (f_ninguem_eu, 2), "pov": (f_pov, 2), "plot_twist": (f_plot_twist, 2), "eu_explicando": (f_eu_explicando, 2),
            "cerebro_niveis": (f_cerebro_niveis, None), "botoes_dificil": (f_botoes_dificil, 2), "grafico_mentiroso": (f_grafico_mentiroso, 2),
            "legenda_choque": (f_legenda_choque, 2),
            # pesquisa 24/11/2026 (docs/pesquisa/2026-11-24_memes_em_alta.md)
            "carregando": (f_carregando, 1), "estagios": (f_estagios, lambda st: len(st.get("estagios") or [0] * 5)),
            "retrospectiva": (f_retrospectiva, lambda st: len(st.get("meses") or [0] * 12)), "carta_noel": (f_carta_noel, 2),
            "soft_launch": (f_soft_launch, 2), "remoendo": (f_remoendo, lambda st: 1 + len(st.get("leituras") or [0] * 4)),
            "vai_vai_vai": (f_vai_vai_vai, 2), "nao_nao_sim": (f_nao_nao_sim, lambda st: len(st.get("itens") or [0] * 4)),
            "nao_julgamos": (f_nao_julgamos, 3), "distraida": (f_distraida, 2)}


def paineis(st):
    """Quantos painéis/níveis o formato tem (valor de `revela` com tudo à mostra)."""
    f, n = FORMATOS[st.get("formato")]
    if callable(n):
        return n(st)
    return n if n else len(st.get("niveis") or [0, 0, 0, 0])


def desenha_meme(ctx, st, t, pal, seed):
    fmt = st.get("formato", "aprova_reprova")
    if fmt not in FORMATOS:
        raise SystemExit(f"meme: formato desconhecido '{fmt}'. Formatos: {', '.join(FORMATOS)}")
    st = dict(st); st.setdefault("_t", t)
    st["_rev"] = st.get("revela", paineis(st))
    w, h = st.get("largura", 900), st.get("altura", 900)
    f, _ = FORMATOS[fmt]
    textos, _caras = f(ctx, st, t, pal, seed, w, h)
    return {"corpo": (-w / 2, -h / 2, w / 2, h / 2), "texto": _une(textos or [])}
