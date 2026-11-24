"""Cenários 2 do PipoPop: fundos em 3 camadas (fundo, meio e FRENTE), vida no fundo, luz e âncoras de interação.

Como o render usa:
  fundo(ctx, nome, pal, t, opts, seed)           -> parede, móveis, janelas (antes dos elementos)
  cenario_frente(ctx, nome, pal, t, opts, seed)  -> mesa, balcão, painel... (depois dos personagens)
  posiciona(nome, el)                             -> resolve "ancora" de um elemento em x, y (e escala sugerida)
Opções da cena: luz (dia, tarde, noite), ceu (só a janela), vida (false congela), chuva (true), frente (false desliga),
sinal (semáforo fixo), lousa (texto de giz), vista (carro: "dentro" ou "motorista").
Tudo em pixels de 1080x1920, no mesmo estilo de estilo.py (contorno grosso, sombra chapada, paleta da cena)."""
import math, random
import cairo
from estilo import (W, H, INK, LW, BRANCO, AMARELO, VERMELHO, VERDE, hexc, mix, escurece, clareia, traco, texto,
                    pts_elipse, pts_ret, clamp)
from estilo import forma as _forma


def _poli(pts, passo=70):
    """Polígono de cantos vivos para o traço suave (sem virar elipse)."""
    out = []
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        d = math.hypot(x1 - x0, y1 - y0) or 1
        e = min(4.0, d / 4) / d
        out.append((x0, y0)); out.append((x0 + (x1 - x0) * e, y0 + (y1 - y0) * e))
        k = int(d // passo)
        for j in range(1, k + 1):
            u = j / (k + 1)
            out.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u))
        out.append((x1 - (x1 - x0) * e, y1 - (y1 - y0) * e))
    return out


def forma(ctx, pts, *a, reto=None, **k):
    """forma() do estilo; listas curtas de pontos viram polígono de cantos vivos (reto=False deixa arredondar)."""
    if reto is None:
        reto = len(pts) <= 8
    return _forma(ctx, _poli(pts) if reto else pts, *a, **k)

MADEIRA = hexc("#B8743F")
MADEIRA_ESC = hexc("#8A4B2A")
CINZA = hexc("#9AA3B5")
VIDRO_CLARO = hexc("#BFE6FF")

# luz: cor que multiplica o fundo (None = sem tinta) e o quanto ela pega nos personagens
LUZ = {"dia": None, "tarde": (1.0, 0.78, 0.60), "noite": (0.40, 0.44, 0.74)}
CEU = {"dia": ("#7CC8FF", "#D2F0FF"), "tarde": ("#FF7A3D", "#FFD089"), "noite": ("#0F0E2C", "#2B2766"),
       "chuva": ("#6F7F99", "#AEB9C9")}
HALO = (1.0, 0.72, 0.36)
DW, DH = 270, 760          # porta padrão (px, escala 1)


class Estado:
    def __init__(self, nome, pal, t, opts, seed):
        self.nome = nome; self.pal = pal; self.t = t; self.opts = opts; self.seed = seed
        self.vida = opts.get("vida", True) is not False
        self.tv = t if self.vida else 0.0
        luz = opts.get("luz", CENARIOS.get(nome, {}).get("luz", "dia"))
        self.luz = luz if luz in LUZ else "dia"
        ceu_pad = "noite" if (nome in ("quarto", "sala_natal") and "luz" not in opts) else self.luz
        self.ceu = opts.get("ceu", ceu_pad)
        if opts.get("chuva") and self.ceu == "dia":
            self.ceu = "chuva"
        self.T = LUZ[self.luz]
        self.apos = []          # desenhos depois da tinta de luz (vidros, telas, lâmpadas acesas)
        self.ocup = set(opts.get("_ocupadas", ()))
        self.comp = False       # True: cores divididas pela luz (céu da rua, que leva a tinta junto com o resto)

    def tc(self, c):
        """Cor já com a luz aplicada (para o que é desenhado depois da tinta)."""
        if not self.T:
            return c
        return tuple(c[i] * self.T[i] for i in range(3))


def _tinta(ctx, T, k=1.0):
    if not T:
        return
    c = mix(T, (1, 1, 1), 1 - k)
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY); ctx.set_source_rgb(*c); ctx.paint(); ctx.restore()


def _halo(ctx, x, y, r, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *HALO, a); g.add_color_stop_rgba(0.45, *HALO, a * 0.45); g.add_color_stop_rgba(1, *HALO, 0)
    ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD); ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill(); ctx.restore()


def _ret(ctx, x, y, w, h, cor, a=1.0):
    ctx.rectangle(x, y, w, h); ctx.set_source_rgba(*cor, a); ctx.fill()


# ============================ peças comuns ============================
def _nuvem_pts(cx, cy, s):
    pts = []
    for i in range(22):
        a = 2 * math.pi * i / 22
        r = 1 + 0.22 * abs(math.sin(a * 2.5))
        y = math.sin(a) * 0.55 * r
        pts.append((cx + math.cos(a) * 110 * s * r, cy + min(y, 0.28) * 90 * s))
    return pts


def _nuvem(ctx, cx, cy, s, cor, seed):
    forma(ctx, _nuvem_pts(cx, cy, s), cor, sombra=False, lw=4, seed=seed, amp=1.0)


def _passaro(ctx, x, y, s, t, cor=INK):
    b = math.sin(t * 14) * 14 * s
    traco(ctx, [(x - 26 * s, y - b), (x - 10 * s, y - 4 * s), (x, y + 4 * s)], lw=5, cor=cor, amp=0)
    traco(ctx, [(x, y + 4 * s), (x + 10 * s, y - 4 * s), (x + 26 * s, y - b)], lw=5, cor=cor, amp=0)


def _ceu(ctx, S, x, y, w, h, cidade=True, chao=None):
    """Céu de janela (sem tinta de luz: é a luz de fora). Nuvens, sol/lua, estrelas, prédios, pássaro e carrinho."""
    K = (lambda c: tuple(min(1.0, c[i] / S.T[i]) for i in range(3))) if (S.comp and S.T) else (lambda c: c)
    c1, c2 = CEU.get(S.ceu, CEU["dia"])
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *K(hexc(c1))); g.add_color_stop_rgb(1, *K(hexc(c2)))
    ctx.rectangle(x, y, w, h); ctx.set_source(g); ctx.fill()
    tv = S.tv; r = random.Random(S.seed + int(x))
    if S.ceu == "noite":
        ctx.set_source_rgba(*K((1, 1, 0.9)), 0.85)
        for i in range(14):
            sx, sy = x + r.uniform(0, w), y + r.uniform(0, h * 0.6)
            rr = 2.5 + 1.5 * (0.5 + 0.5 * math.sin(tv * 3 + i))
            ctx.arc(sx, sy, rr, 0, 2 * math.pi); ctx.new_sub_path()
        ctx.fill()
        forma(ctx, pts_elipse(x + w * 0.72, y + h * 0.24, 40, 40, 16), K(hexc("#FFF1B8")), sombra=False, lw=4, seed=S.seed + 5)
        ctx.arc(x + w * 0.72 + 18, y + h * 0.24 - 10, 34, 0, 2 * math.pi); ctx.set_source_rgb(*K(hexc(c1))); ctx.fill()
    elif S.ceu in ("dia", "tarde"):
        sol = hexc("#FFE15A") if S.ceu == "dia" else hexc("#FFB347")
        sy = y + h * (0.22 if S.ceu == "dia" else 0.55)
        forma(ctx, pts_elipse(x + w * 0.75, sy, 44, 44, 16), K(sol), sombra=False, lw=4, seed=S.seed + 5)
    # nuvens andando
    nc = K(clareia(hexc(c2), 0.6) if S.ceu != "noite" else hexc("#3A3576"))
    for k in range(2):
        ph = (tv * (14 + 7 * k) + k * w * 0.6 + r.uniform(0, w)) % (w + 300) - 150
        _nuvem(ctx, x + ph, y + h * (0.18 + 0.2 * k), 0.55 - 0.12 * k, nc, S.seed + 30 + k)
    if cidade:
        base = y + h if chao is None else chao
        cor = escurece(hexc(c2), 0.35) if S.ceu != "noite" else hexc("#1B1940")
        ctx.save()
        xx = x - 10; k = 0
        while xx < x + w:
            bw = 50 + (k * 37) % 50; bh = h * (0.18 + ((k * 53) % 40) / 100)
            ctx.rectangle(xx, base - bh, bw, bh + 4); xx += bw + 8; k += 1
        ctx.set_source_rgb(*cor); ctx.fill()
        if S.ceu == "noite":   # janelinhas acesas
            xx = x - 10; k = 0; ctx.set_source_rgb(*hexc("#FFD36A"))
            while xx < x + w:
                bw = 50 + (k * 37) % 50; bh = h * (0.18 + ((k * 53) % 40) / 100)
                for j in range(int(bh // 30)):
                    if (k * 7 + j * 3) % 4 == 0:
                        ctx.rectangle(xx + 12, base - bh + 14 + j * 30, 10, 12)
                xx += bw + 8; k += 1
            ctx.fill()
        ctx.restore()
        # carrinho passando lá longe
        cyc = 7.0; u = (tv + S.seed * 0.37) % cyc / cyc
        cx = x - 80 + u * (w + 160)
        ctx.rectangle(cx - 34, base - 26, 68, 18); ctx.set_source_rgb(*hexc("#E8452C") if S.ceu != "noite" else hexc("#FFD36A")); ctx.fill()
        ctx.rectangle(cx - 18, base - 38, 36, 14); ctx.fill()
    if S.ceu != "noite" and S.vida:   # pássaro de vez em quando
        cyc = 6.5; u = (tv + 1.3) % cyc / 2.6
        if u < 1:
            _passaro(ctx, x + w * (1.1 - u * 1.2), y + h * 0.35 + math.sin(u * 6) * 12, 0.9, tv)


def _chuva_vidro(ctx, S, x, y, w, h):
    r = random.Random(S.seed + 77)
    ctx.set_source_rgba(0.9, 0.95, 1, 0.55); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(16):
        x0 = x + r.uniform(8, w - 8); v = r.uniform(90, 220); ph = r.uniform(0, h)
        y0 = y + (ph + S.tv * v) % h
        ctx.move_to(x0, max(y, y0 - 46)); ctx.line_to(x0 + 2, y0)
    ctx.stroke()
    ctx.set_source_rgba(0.9, 0.95, 1, 0.45)
    for i in range(14):
        ctx.new_sub_path(); ctx.arc(x + r.uniform(6, w - 6), y + r.uniform(6, h - 6), r.uniform(3, 6), 0, 2 * math.pi)
    ctx.fill()


def _janela(ctx, S, x, y, w, h, cortina=True, persiana=False, cidade=True, moldura=BRANCO, seed=0):
    """Moldura agora; vidro, travessas e cortina depois da tinta de luz."""
    forma(ctx, pts_ret(x - 18, y - 18, w + 36, h + 36, 16), moldura, seed=S.seed + seed)

    def depois(ctx):
        ctx.save(); ctx.rectangle(x, y, w, h); ctx.clip()
        _ceu(ctx, S, x, y, w, h, cidade=cidade)
        if S.opts.get("chuva"):
            _chuva_vidro(ctx, S, x, y, w, h)
        ctx.restore()
        if persiana:
            for k in range(int(h // 46)):
                yy = y + 18 + k * 46
                ctx.rectangle(x, yy, w, 22)
            ctx.set_source_rgba(*S.tc(clareia(moldura, 0.0)), 0.82); ctx.fill()
            traco(ctx, [(x + w * 0.85, y), (x + w * 0.85, y + h * 0.9)], lw=4, cor=INK, seed=S.seed + seed + 4, alpha=0.7)
        else:
            traco(ctx, [(x + w / 2, y), (x + w / 2, y + h)], lw=10, cor=S.tc(moldura), seed=S.seed + seed + 1, amp=0.6)
            traco(ctx, [(x, y + h * 0.48), (x + w, y + h * 0.48)], lw=10, cor=S.tc(moldura), seed=S.seed + seed + 2, amp=0.6)
            traco(ctx, [(x + w / 2, y), (x + w / 2, y + h)], lw=3, cor=INK, seed=S.seed + seed + 1, alpha=0.5)
        forma(ctx, pts_ret(x, y, w, h, 8), moldura, sombra=False, lw=5, seed=S.seed + seed + 3, contorno=INK) if False else None
        ctx.rectangle(x, y, w, h); ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.stroke()
        if cortina:
            cc = S.tc(S.pal[2])
            bal = math.sin(S.tv * 1.6 + seed) * 16 if S.vida else 0
            for lado in (-1, 1):
                x0 = x - 30 if lado < 0 else x + w + 30
                topo = y - 34
                larg = w * 0.24
                xin = x0 - lado * larg
                pts = [(x0, topo), (xin, topo), (xin - lado * 10 + bal * 0.4, y + h * 0.35),
                       (xin + lado * 26 + bal, y + h * 0.78), (xin + lado * 4 + bal * 1.2, y + h + 40), (x0, y + h + 50)]
                forma(ctx, pts, cc, sombreado=0.12, seed=S.seed + seed + 10 + lado, sombra_off=(8, 8), reto=False)
                for f in range(2):
                    fx = x0 - lado * larg * (0.35 + 0.3 * f)
                    traco(ctx, [(fx, topo + 20), (fx + bal * 0.5, y + h * 0.5), (fx + bal, y + h + 20)], lw=3, alpha=0.4,
                          seed=S.seed + seed + 14 + f + lado)
            traco(ctx, [(x - 70, y - 34), (x + w + 70, y - 34)], lw=12, cor=INK, seed=S.seed + seed + 20)
    S.apos.append(depois)


def _ventilador(ctx, S, x, y, s=1.0, cor=None):
    cor = cor or S.pal[4]
    traco(ctx, [(x, -10), (x, y - 20 * s)], lw=10, seed=S.seed + 41)
    ang = S.tv * 2 * math.pi * 1.1
    for k in range(4):
        a = ang + k * math.pi / 2
        ex, ey = math.cos(a) * 190 * s, math.sin(a) * 34 * s
        pts = [(x + ex * 0.15 - ey * 0.25, y + ey * 0.15), (x + ex, y + ey - 10 * s), (x + ex * 1.02, y + ey + 14 * s),
               (x + ex * 0.15 + ey * 0.3, y + ey * 0.15 + 12 * s)]
        forma(ctx, pts, escurece(cor, 0.1 + 0.15 * (math.sin(a) > 0)), sombra=False, lw=4, seed=S.seed + 42 + k, amp=0.6, reto=False)
    forma(ctx, pts_elipse(x, y, 44 * s, 26 * s, 14), escurece(cor, 0.3), sombra=False, lw=5, seed=S.seed + 47)


def _vapor(ctx, S, x, y, s=1.0, n=3):
    if not S.vida and S.t > 0:
        pass
    for k in range(n):
        ph = (S.tv * 0.7 + k / n) % 1.0
        a = math.sin(ph * math.pi) * 0.75
        yy = y - ph * 120 * s
        xx = x + (k - (n - 1) / 2) * 26 * s
        pts = [(xx + math.sin(S.tv * 3 + k + j * 1.3) * 12 * s, yy - j * 26 * s) for j in range(4)]
        traco(ctx, pts, lw=9 * s, cor=(1, 1, 1), alpha=a, amp=0)


def _caneca(ctx, S, x, y, cor, s=1.0, vapor=True):
    forma(ctx, pts_ret(x - 42 * s, y - 90 * s, 84 * s, 90 * s, 14), cor, seed=S.seed + 50, sombra_off=(6, 7))
    traco(ctx, [(x + 40 * s, y - 70 * s), (x + 68 * s, y - 64 * s), (x + 66 * s, y - 30 * s), (x + 40 * s, y - 26 * s)], lw=10 * s, seed=S.seed + 51)
    if vapor:
        _vapor(ctx, S, x, y - 104 * s, s * 0.8)


def _abajur(ctx, S, x, y, cor, s=1.0, pe=True):
    """y = base do abajur (onde ele apoia). Aceso de noite (cúpula clara, depois da tinta)."""
    if pe:
        traco(ctx, [(x, y), (x, y - 150 * s)], lw=12 * s, seed=S.seed + 60)
        forma(ctx, pts_elipse(x, y, 50 * s, 16 * s, 12), INK, sombra=False, lw=0, seed=S.seed + 61)
    top = y - 150 * s
    cupula = [(x - 80 * s, top), (x + 80 * s, top), (x + 50 * s, top - 110 * s), (x - 50 * s, top - 110 * s)]
    forma(ctx, cupula, cor, seed=S.seed + 62, sombreado=0.1)
    if S.luz == "noite":
        def acesa(ctx):
            _halo(ctx, x, top - 40 * s, 420 * s, 0.42)
            forma(ctx, cupula, hexc("#FFE6A0"), sombra=False, seed=S.seed + 62)
        S.apos.append(acesa)


def _relogio(ctx, S, x, y, r, cor=None):
    forma(ctx, pts_elipse(x, y, r + 12, r + 12, 22), cor or S.pal[2], seed=S.seed + 70)
    forma(ctx, pts_elipse(x, y, r, r, 22), BRANCO, sombra=False, lw=4, seed=S.seed + 71)
    for k in range(12):
        a = k * math.pi / 6
        ctx.move_to(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78); ctx.line_to(x + math.cos(a) * r * 0.9, y + math.sin(a) * r * 0.9)
    ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
    seg = math.floor(S.tv) + 17
    for ang, L, lw in ((seg / 3600 * 2 * math.pi * 3 + 1.1, 0.5, 8), (seg / 60 * 2 * math.pi * 0.08 + 4.0, 0.72, 6),
                       (seg / 60 * 2 * math.pi, 0.82, 3)):
        traco(ctx, [(x, y), (x + math.sin(ang) * r * L, y - math.cos(ang) * r * L)], lw=lw, amp=0,
              cor=VERMELHO if lw == 3 else INK)
    ctx.arc(x, y, 7, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()


def _planta(ctx, S, x, y, s=1.0, vaso=None):
    """y = base do vaso."""
    bal = math.sin(S.tv * 1.3 + x) * 4
    for k in range(5):
        a = (k - 2) * 0.42
        cx = x + math.sin(a) * 60 * s + bal * (1 + abs(k - 2) * 0.4)
        cy = y - 150 * s - math.cos(a) * 70 * s
        forma(ctx, pts_elipse(cx, cy, 26 * s, 62 * s, 12), escurece(VERDE, 0.1 * (k % 2)), sombra=False, lw=4,
              seed=S.seed + 80 + k, amp=0.8)
    forma(ctx, [(x - 55 * s, y - 100 * s), (x + 55 * s, y - 100 * s), (x + 40 * s, y), (x - 40 * s, y)], vaso or hexc("#C8531F"),
          seed=S.seed + 86, sombra_off=(6, 7))


def _quadro(ctx, S, x, y, w, h):
    forma(ctx, pts_ret(x, y, w, h, 8), S.pal[2], seed=S.seed + 90)
    forma(ctx, pts_ret(x + 16, y + 16, w - 32, h - 32, 4), clareia(S.pal[3], 0.55), sombra=False, lw=4, seed=S.seed + 91)
    forma(ctx, [(x + 16, y + h - 16), (x + w * 0.4, y + h * 0.45), (x + w * 0.62, y + h * 0.7), (x + w * 0.78, y + h * 0.5),
                (x + w - 16, y + h - 16)], S.pal[3], sombra=False, lw=4, seed=S.seed + 92)
    ctx.arc(x + w * 0.72, y + h * 0.3, min(w, h) * 0.09, 0, 2 * math.pi); ctx.set_source_rgb(*AMARELO); ctx.fill()


def _livros(ctx, S, x, y, w, seed=0):
    """Prateleira em y com livros em pé em cima."""
    cores = [S.pal[2], S.pal[3], S.pal[4], escurece(S.pal[0], 0.35), VERDE]
    xx = x + 14; k = 0
    while xx < x + w - 40:
        bw = 26 + (k * 13 + seed) % 20; bh = 70 + (k * 29 + seed) % 40
        forma(ctx, pts_ret(xx, y - bh, bw, bh, 4), cores[(k + seed) % len(cores)], sombra=False, lw=4, seed=S.seed + 100 + k + seed, amp=0.6)
        xx += bw + 4; k += 1
    forma(ctx, pts_ret(x, y, w, 22, 4), MADEIRA, seed=S.seed + 99 + seed, sombra_off=(6, 6))


def _porta_desenho(ctx, cx, cy, w, h, abre, cor, dentro, seed, maca=True, batente=True):
    """Porta centrada em (cx, cy). abre 0 a 1 (gira para dentro, dobradiça à esquerda)."""
    x0, y0 = cx - w / 2, cy - h / 2
    if batente:
        forma(ctx, pts_ret(x0 - 24, y0 - 24, w + 48, h + 24, 8), escurece(cor, 0.35), seed=seed, sombra_off=(8, 8))
    if abre > 0.01:
        g = cairo.LinearGradient(0, y0, 0, y0 + h)
        g.add_color_stop_rgb(0, *dentro); g.add_color_stop_rgb(1, *escurece(dentro, 0.45))
        ctx.rectangle(x0, y0, w, h); ctx.set_source(g); ctx.fill()
        ctx.move_to(x0, y0 + h); ctx.line_to(x0 + w, y0 + h); ctx.line_to(x0 + w * 0.82, y0 + h * 0.86); ctx.line_to(x0 + w * 0.18, y0 + h * 0.86)
        ctx.close_path(); ctx.set_source_rgba(*INK, 0.25); ctx.fill()
    ang = clamp(abre) * math.radians(80)
    fx = x0 + w * math.cos(ang)
    enc = h * 0.06 * math.sin(ang)
    folha = [(x0, y0), (fx, y0 + enc), (fx, y0 + h - enc * 0.6), (x0, y0 + h)]
    if fx - x0 > 4:
        forma(ctx, folha, cor if ang < 0.2 else escurece(cor, 0.12 + 0.2 * math.sin(ang)), sombra=False, seed=seed + 1, amp=1.0)
        k = (fx - x0) / w
        for py0, py1 in ((0.08, 0.44), (0.52, 0.9)):
            ix0, ix1 = x0 + w * k * 0.16, x0 + w * k * 0.84
            ctx.move_to(ix0, y0 + h * py0 + enc * 0.84); ctx.line_to(ix1, y0 + h * py0 + enc * 0.16 + enc * 0.84 * 0.0)
            ctx.line_to(ix1, y0 + h * py1); ctx.line_to(ix0, y0 + h * py1); ctx.close_path()
        ctx.set_source_rgba(*INK, 0.5); ctx.set_line_width(4); ctx.stroke()
        if maca:
            mx = x0 + (fx - x0) * 0.86
            forma(ctx, pts_elipse(mx, y0 + h * 0.5, 14 * max(0.3, k), 14, 10), AMARELO, sombra=False, lw=4, seed=seed + 2)
    ctx.rectangle(x0, y0, w, h); ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.stroke()


def _batente(ctx, cx, cy, w, h, cor, seed, S=None):
    """Só o batente (vai na frente de quem está passando pela porta)."""
    x0, y0 = cx - w / 2, cy - h / 2
    c = escurece(cor, 0.35); c = S.tc(c) if S else c
    forma(ctx, pts_ret(x0 - 26, y0 - 26, 34, h + 26, 6), c, seed=seed + 5, sombra_off=(6, 6))
    forma(ctx, pts_ret(x0 + w - 8, y0 - 26, 34, h + 26, 6), c, seed=seed + 6, sombra_off=(6, 6))
    forma(ctx, pts_ret(x0 - 26, y0 - 26, w + 52, 34, 6), c, seed=seed + 7, sombra_off=(6, 6))


def _chao_tacos(ctx, S, y0, cor):
    forma(ctx, [(-20, y0), (W + 20, y0), (W + 20, H + 20), (-20, H + 20)], cor, sombra=False, seed=S.seed + 3)
    for k in range(5):
        yy = y0 + 70 + k * 110
        traco(ctx, [(-10, yy), (W + 10, yy)], lw=4, alpha=0.35, seed=S.seed + 4 + k, amp=0.8)
        for j in range(4):
            xx = (j * 300 + k * 140) % (W + 200) - 60
            traco(ctx, [(xx, yy), (xx, yy + 110)], lw=4, alpha=0.3, seed=S.seed + 20 + k * 4 + j, amp=0.5)


def _rodape(ctx, S, y, cor):
    _ret(ctx, 0, y - 34, W, 34, escurece(cor, 0.4))
    traco(ctx, [(-10, y - 34), (W + 10, y - 34)], lw=5, seed=S.seed + 9, amp=0.8)


def _papel_parede(ctx, S, cor, passo=130, tipo="listras"):
    if tipo == "listras":
        for k in range(0, W // passo + 2):
            ctx.rectangle(k * passo, 0, passo * 0.4, H)
    else:
        for yy in range(40, H, passo):
            for xx in range(40 + (passo // 2 if (yy // passo) % 2 else 0), W, passo):
                ctx.new_sub_path(); ctx.arc(xx, yy, 9, 0, 2 * math.pi)
    ctx.set_source_rgba(*cor, 0.55); ctx.fill()


def _carro(ctx, x, y, s, cor, seed, t, farol=False, sentido=1):
    """Carro de lado, (x, y) = centro da base das rodas."""
    ctx.save(); ctx.translate(x, y); ctx.scale(s * sentido, s)
    pula = math.sin(t * 22) * 2
    ctx.translate(0, pula)
    forma(ctx, [(-250, -40), (-240, -110), (-150, -125), (-90, -205), (80, -205), (160, -125), (245, -110), (255, -40)],
          cor, sombreado=0.1, seed=seed, sombra_off=(10, 10))
    for x0, x1 in ((-75, -5), (15, 125)):
        forma(ctx, [(x0, -125), (x0 + (8 if x0 < 0 else 0), -190), (x1 - (40 if x1 > 0 else 0), -190), (x1, -125)],
              VIDRO_CLARO, sombra=False, lw=4, seed=seed + 1 + x0)
    if farol:
        _halo(ctx, 260, -80, 160, 0.5)
    forma(ctx, pts_elipse(238, -82, 16, 12, 10), hexc("#FFF2A8"), sombra=False, lw=4, seed=seed + 4)
    forma(ctx, pts_elipse(-242, -82, 10, 12, 10), VERMELHO, sombra=False, lw=4, seed=seed + 5)
    for wx in (-150, 150):
        forma(ctx, pts_elipse(wx, -30, 48, 48, 16), INK, sombra=False, lw=0, seed=seed + 6 + wx)
        ctx.arc(wx, -30, 22, 0, 2 * math.pi); ctx.set_source_rgb(*CINZA); ctx.fill()
        a = t * 18
        ctx.move_to(wx + math.cos(a) * 20, -30 + math.sin(a) * 20); ctx.line_to(wx - math.cos(a) * 20, -30 - math.sin(a) * 20)
        ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    ctx.restore()


def _semaforo(ctx, S, x, ybase, ytopo):
    traco(ctx, [(x, ybase), (x, ytopo + 200)], lw=18, seed=S.seed + 120)
    forma(ctx, pts_ret(x - 55, ytopo, 110, 260, 18), hexc("#2B2440"), seed=S.seed + 121)
    fixo = S.opts.get("sinal")
    if fixo in ("verde", "amarelo", "vermelho"):
        aceso = fixo
    else:
        u = S.tv % 7.0
        aceso = "verde" if u < 3 else ("amarelo" if u < 4.2 else "vermelho")
    cores = (("vermelho", VERMELHO), ("amarelo", AMARELO), ("verde", hexc("#3DDC5A")))

    def luzes(ctx):
        for k, (nome, c) in enumerate(cores):
            cy = ytopo + 48 + k * 82
            if nome == aceso:
                _halo(ctx, x, cy, 120, 0.5 if S.luz == "noite" else 0.28)
                forma(ctx, pts_elipse(x, cy, 30, 30, 14), clareia(c, 0.15), sombra=False, lw=4, seed=S.seed + 122 + k)
            else:
                forma(ctx, pts_elipse(x, cy, 30, 30, 14), S.tc(escurece(c, 0.6)), sombra=False, lw=4, seed=S.seed + 122 + k)
    S.apos.append(luzes)


def _poste(ctx, S, x, ybase, ytopo):
    traco(ctx, [(x, ybase), (x, ytopo), (x + 40, ytopo - 40), (x + 120, ytopo - 40)], lw=16, seed=S.seed + 130)
    lamp = [(x + 80, ytopo - 50), (x + 170, ytopo - 50), (x + 150, ytopo - 20), (x + 100, ytopo - 20)]
    forma(ctx, lamp, hexc("#4A4560"), seed=S.seed + 131)
    if S.luz == "noite":
        def acesa(ctx):
            _halo(ctx, x + 125, ytopo, 380, 0.4)
            forma(ctx, lamp, hexc("#FFE6A0"), sombra=False, seed=S.seed + 131)
        S.apos.append(acesa)


# ============================ CENÁRIOS ============================
# Cada um: fundo(ctx, S) e, se tiver, frente(ctx, S). ANCORAS em pixels:
#   {"x", "y"} ponto; "assento": y do quadril; "chao": y dos pés; "escala": sugerida para personagens.

# ---------- SALA
SOFA = dict(x0=90, x1=770, assento=1135)
PORTA_SALA = (925, 1400 - DH / 2)


def _sofa(ctx, S, parte="tudo"):
    sofa = hexc(S.opts["cor_sofa"]) if S.opts.get("cor_sofa") else S.pal[3]
    tc = S.tc if parte == "frente" else (lambda c: c)
    if parte in ("tudo", "fundo"):
        forma(ctx, pts_ret(150, 900, 560, 270, 60), escurece(sofa, 0.14), seed=S.seed + 10)          # encosto
        for k, cx in enumerate((250, 610)):
            forma(ctx, pts_ret(cx - 80, 960 + k * 10, 160, 150, 44), S.pal[2] if k == 0 else S.pal[4], seed=S.seed + 11 + k,
                  sombreado=0.1, sombra_off=(6, 6))   # almofadas
    if parte in ("tudo", "frente"):
        forma(ctx, pts_ret(120, 1120, 620, 230, 46), tc(sofa), sombreado=0.05, seed=S.seed + 13)      # assento
        traco(ctx, [(430, 1132), (430, 1340)], lw=4, alpha=0.45, seed=S.seed + 14)
        for sx in (80, 640):
            forma(ctx, pts_ret(sx, 1010, 130, 350, 56), tc(escurece(sofa, 0.06)), seed=S.seed + 15 + sx)  # braços
        for fx in (150, 690):
            forma(ctx, pts_ret(fx, 1355, 34, 46, 8), tc(MADEIRA_ESC), sombra=False, lw=4, seed=S.seed + 18 + fx)


def fundo_sala(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _papel_parede(ctx, S, bg2)
    _rodape(ctx, S, 1400, bg)
    _chao_tacos(ctx, S, 1400, MADEIRA_ESC)
    forma(ctx, pts_elipse(440, 1560, 470, 90, 26), a3, sombra=False, seed=S.seed + 5)       # tapete
    forma(ctx, pts_elipse(440, 1560, 380, 62, 26), escurece(a3, 0.12), sombra=False, lw=4, seed=S.seed + 6)
    _janela(ctx, S, 230, 260, 320, 380, cortina=True)
    _quadro(ctx, S, 600, 300, 150, 140)
    _livros(ctx, S, 590, 580, 170, seed=3)
    _relogio(ctx, S, 925, 470, 52)
    _porta_desenho(ctx, *PORTA_SALA, DW, DH, 0, S.pal[2] if False else MADEIRA, hexc("#FFE7B0"), S.seed + 140)
    traco(ctx, [(75, 1395), (75, 760)], lw=12, seed=S.seed + 63)
    _abajur(ctx, S, 75, 910, a2, s=1.0, pe=False)
    forma(ctx, pts_elipse(75, 1395, 56, 16, 12), INK, sombra=False, lw=0, seed=S.seed + 64)
    _sofa(ctx, S, "tudo")
    _ventilador(ctx, S, 540, 120, 0.9)


def frente_sala(ctx, S):
    if S.ocup & {"sofa_assento", "sofa_esq", "sofa_dir"}:
        _sofa(ctx, S, "frente")
    if "porta" in S.ocup:
        _batente(ctx, *PORTA_SALA, DW, DH, MADEIRA, S.seed + 140, S)


# ---------- ESCRITÓRIO
def fundo_escritorio(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _ret(ctx, 0, 930, W, H - 930, escurece(bg, 0.18))
    traco(ctx, [(-10, 930), (W + 10, 930)], lw=5, seed=S.seed + 1, alpha=0.6)
    _janela(ctx, S, 90, 220, 360, 400, cortina=False, persiana=True)
    # quadro de avisos com post-its
    forma(ctx, pts_ret(530, 240, 280, 220, 10), hexc("#C98A4B"), seed=S.seed + 2)
    forma(ctx, pts_ret(546, 256, 248, 188, 6), hexc("#E3B27A"), sombra=False, lw=4, seed=S.seed + 3)
    for k, (px, py, c) in enumerate(((580, 300, a1), (670, 280, a3), (740, 340, AMARELO), (610, 390, a2), (700, 400, BRANCO))):
        forma(ctx, pts_ret(px - 34, py - 30, 68, 64, 4), c, sombra=True, lw=4, seed=S.seed + 4 + k, sombra_off=(4, 5))
        ctx.arc(px, py - 22, 6, 0, 2 * math.pi); ctx.set_source_rgb(*VERMELHO); ctx.fill()
    _relogio(ctx, S, 940, 300, 62)
    _livros(ctx, S, 840, 560, 210, seed=1)
    _planta(ctx, S, 1000, 538, 0.55)
    # luminária pendente
    traco(ctx, [(720, -10), (720, 120)], lw=6, seed=S.seed + 6)
    cup = [(640, 170), (800, 170), (760, 110), (680, 110)]
    forma(ctx, cup, a1, seed=S.seed + 7)
    if S.luz == "noite":
        S.apos.append(lambda c: (_halo(c, 720, 200, 520, 0.38), forma(c, cup, hexc("#FFE6A0"), sombra=False, seed=S.seed + 7)))
    # cadeira atrás da pessoa
    forma(ctx, pts_ret(250, 770, 280, 300, 60), hexc("#2B2440"), seed=S.seed + 8)
    forma(ctx, pts_ret(278, 798, 224, 240, 46), escurece(a2, 0.25), sombra=False, lw=4, seed=S.seed + 9)
    # monitor sobre a mesa
    forma(ctx, pts_ret(650, 760, 320, 230, 18), INK, seed=S.seed + 13)
    forma(ctx, pts_ret(770, 985, 80, 50, 6), INK, sombra=False, lw=0, seed=S.seed + 15)

    def tela(ctx):
        cor = a2 if S.luz != "noite" else clareia(a2, 0.15)
        forma(ctx, pts_ret(668, 778, 284, 194, 10), cor, sombra=False, lw=4, seed=S.seed + 14)
        rol = (S.tv * 30) % 34
        ctx.save(); ctx.rectangle(680, 790, 260, 170); ctx.clip()
        for k in range(7):
            yy = 800 + k * 34 - rol
            ctx.rectangle(692 + (k % 3) * 24, yy, 120 + (k * 47) % 110, 12)
        ctx.set_source_rgba(1, 1, 1, 0.75); ctx.fill(); ctx.restore()
        if S.luz == "noite":
            _halo(ctx, 810, 870, 300, 0.18)
    S.apos.append(tela)
    _abajur(ctx, S, 150, 1035, a3, s=0.85)
    _caneca(ctx, S, 575, 1032, a1, s=0.85)


def frente_escritorio(ctx, S):
    tc = S.tc
    forma(ctx, pts_ret(-30, 1030, W + 60, 56, 14), tc(hexc("#C98A4B")), seed=S.seed + 12)                 # tampo
    forma(ctx, pts_ret(20, 1080, W - 40, 520, 10), tc(hexc("#A86D36")), seed=S.seed + 16, sombreado=0.04)  # frente da mesa
    for k, x0 in enumerate((70, 760)):
        for j in range(3):
            forma(ctx, pts_ret(x0, 1110 + j * 150, 250, 130, 10), tc(hexc("#B97C42")), sombra=False, lw=4, seed=S.seed + 30 + k * 3 + j)
            traco(ctx, [(x0 + 95, 1150 + j * 150), (x0 + 155, 1150 + j * 150)], lw=8, cor=INK, seed=S.seed + 40 + j + k)
    forma(ctx, pts_ret(870, 1000, 150, 32, 4), tc(BRANCO), sombra=False, lw=4, seed=S.seed + 17)            # papéis
    forma(ctx, pts_ret(880, 978, 140, 26, 4), tc(clareia(S.pal[3], 0.6)), sombra=False, lw=4, seed=S.seed + 18)


# ---------- QUARTO
def fundo_quarto(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _papel_parede(ctx, S, bg2, passo=110, tipo="bolinhas")
    _rodape(ctx, S, 1380, bg)
    _chao_tacos(ctx, S, 1380, MADEIRA_ESC)
    forma(ctx, pts_elipse(560, 1560, 420, 80, 24), a1, sombra=False, seed=S.seed + 5)
    _janela(ctx, S, 640, 250, 320, 360, cortina=True)
    forma(ctx, pts_ret(90, 300, 280, 360, 10), a1, seed=S.seed + 4)                          # pôster
    forma(ctx, pts_elipse(230, 470, 84, 84, 18), a2, sombra=False, lw=5, seed=S.seed + 5)
    forma(ctx, [(170, 560), (230, 400), (290, 560)], AMARELO, sombra=False, lw=4, seed=S.seed + 6)
    _livros(ctx, S, 400, 760, 200, seed=5)
    # cama
    forma(ctx, pts_ret(30, 860, 720, 240, 50), escurece(a2, 0.2), seed=S.seed + 7)         # cabeceira
    forma(ctx, pts_ret(70, 990, 280, 140, 60), BRANCO, seed=S.seed + 8)                      # travesseiro
    _coberta(ctx, S, lambda c: c)
    # criado-mudo + abajur + despertador
    forma(ctx, pts_ret(800, 1080, 220, 300, 14), MADEIRA, seed=S.seed + 9)
    traco(ctx, [(860, 1230), (960, 1230)], lw=8, seed=S.seed + 10)
    _abajur(ctx, S, 870, 1080, a3, s=0.8)
    forma(ctx, pts_ret(940, 1020, 70, 60, 14), a1, seed=S.seed + 11, sombra_off=(5, 5))
    _ventilador(ctx, S, 540, 110, 0.85)


def _coberta(ctx, S, tc):
    a2 = S.pal[3]
    forma(ctx, pts_ret(10, 1090, 760, 260, 50), tc(a2), sombreado=0.05, seed=S.seed + 12)
    for k in range(4):
        traco(ctx, [(60 + k * 180, 1110), (90 + k * 180, 1330)], lw=4, alpha=0.35, seed=S.seed + 13 + k)
    forma(ctx, pts_ret(10, 1090, 760, 60, 30), tc(clareia(a2, 0.35)), sombra=False, seed=S.seed + 17)


def frente_quarto(ctx, S):
    if "cama" in S.ocup:
        _coberta(ctx, S, S.tc)


# ---------- COZINHA
def fundo_cozinha(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    # azulejo atrás do balcão
    _ret(ctx, 330, 600, W - 330, 520, clareia(bg, 0.7))
    for k in range(9):
        ctx.move_to(330, 600 + k * 70); ctx.line_to(W, 600 + k * 70)
    for k in range(10):
        ctx.move_to(330 + k * 82, 600); ctx.line_to(330 + k * 82, 1120)
    ctx.set_source_rgba(*escurece(bg, 0.2), 0.5); ctx.set_line_width(4); ctx.stroke()
    _chao_xadrez(ctx, S, 1430)
    # armários de cima
    for x0, w in ((330, 200), (850, 230)):
        forma(ctx, pts_ret(x0, 190, w, 300, 14), a2, seed=S.seed + 1 + x0, sombreado=0.06)
        traco(ctx, [(x0 + w / 2, 200), (x0 + w / 2, 480)], lw=4, alpha=0.5, seed=S.seed + 3 + x0)
        for sx in (-1, 1):
            traco(ctx, [(x0 + w / 2 + sx * 18, 420), (x0 + w / 2 + sx * 18, 460)], lw=8, seed=S.seed + 5 + x0 + sx)
    _janela(ctx, S, 580, 250, 230, 280, cortina=False, seed=2)
    # cortininha de café
    def cortininha(ctx):
        bal = math.sin(S.tv * 1.8) * 6
        pts = [(570, 400), (820, 400), (820 + bal, 470), (760 + bal, 480), (695 + bal, 470), (630 + bal, 480), (570 + bal, 470)]
        forma(ctx, pts, S.tc(a1), seed=S.seed + 20, sombra_off=(6, 6))
        traco(ctx, [(550, 400), (840, 400)], lw=10, seed=S.seed + 21)
    S.apos.append(cortininha)
    _relogio(ctx, S, 960, 600, 48, cor=a1)
    # utensílios pendurados
    traco(ctx, [(380, 700), (540, 700)], lw=8, seed=S.seed + 22)
    for k, x in enumerate((410, 460, 510)):
        bal = math.sin(S.tv * 2 + k) * 3
        traco(ctx, [(x, 700), (x + bal, 790)], lw=6, seed=S.seed + 23 + k)
        forma(ctx, pts_elipse(x + bal, 810, 18, 26, 10) if k != 1 else pts_ret(x + bal - 20, 790, 40, 40, 6), CINZA,
              sombra=False, lw=4, seed=S.seed + 26 + k)
    # geladeira
    gel = clareia(a3, 0.2) if sum(a3) > 2.4 else BRANCO
    forma(ctx, pts_ret(50, 380, 290, 1050, 34), gel, seed=S.seed + 30, sombreado=0.06)
    traco(ctx, [(56, 660), (334, 660)], lw=6, seed=S.seed + 31)
    traco(ctx, [(300, 460), (300, 600)], lw=14, seed=S.seed + 32)
    traco(ctx, [(300, 720), (300, 920)], lw=14, seed=S.seed + 33)
    for k, (mx, my, c) in enumerate(((110, 440, a1), (180, 500, a2), (130, 760, AMARELO))):
        forma(ctx, pts_elipse(mx, my, 18, 18, 10), c, sombra=False, lw=4, seed=S.seed + 34 + k)
    forma(ctx, pts_ret(150, 720, 110, 130, 4), BRANCO, sombra=True, lw=4, seed=S.seed + 37, sombra_off=(4, 4))   # bilhete
    for k in range(3):
        traco(ctx, [(165, 750 + k * 28), (240 - k * 14, 750 + k * 28)], lw=4, alpha=0.6, seed=S.seed + 38 + k)
    for fx in (80, 300):
        forma(ctx, pts_ret(fx - 10, 1428, 30, 18, 4), INK, sombra=False, lw=0, seed=S.seed + 40 + fx)


def _chao_xadrez(ctx, S, y0):
    _ret(ctx, 0, y0, W, H - y0, BRANCO)
    passo = 120
    for j, yy in enumerate(range(y0, H, passo)):
        for i, xx in enumerate(range(-60, W, passo)):
            if (i + j) % 2:
                ctx.rectangle(xx, yy, passo, passo)
    ctx.set_source_rgb(*escurece(S.pal[0], 0.55)); ctx.fill()
    traco(ctx, [(-10, y0), (W + 10, y0)], lw=6, seed=S.seed + 41)


def frente_cozinha(ctx, S):
    tc = S.tc; a1, a2 = S.pal[2], S.pal[3]
    # panela no fogão com vapor e fruteira
    forma(ctx, pts_ret(850, 960, 160, 120, 20), tc(CINZA), seed=S.seed + 50, sombreado=0.1)
    traco(ctx, [(830, 985), (1030, 985)], lw=10, cor=INK, seed=S.seed + 51)
    forma(ctx, pts_ret(905, 935, 50, 22, 8), tc(INK), sombra=False, lw=0, seed=S.seed + 52)
    _vapor(ctx, S, 930, 910, 1.0)
    forma(ctx, [(370, 1030), (480, 1030), (465, 1080), (385, 1080)], tc(a1), seed=S.seed + 53)
    for k, (fx, fy, c) in enumerate(((395, 1015, VERMELHO), (430, 1005, AMARELO), (462, 1018, hexc("#3DAA3A")))):
        forma(ctx, pts_elipse(fx, fy, 22, 22, 10), tc(c), sombra=False, lw=4, seed=S.seed + 54 + k)
    # balcão
    forma(ctx, pts_ret(330, 1080, W - 300, 52, 10), tc(hexc("#D9D4CC")), seed=S.seed + 60)
    forma(ctx, pts_ret(350, 1130, W - 340, 310, 10), tc(a2), seed=S.seed + 61, sombreado=0.05)
    for k in range(4):
        x0 = 368 + k * 180
        forma(ctx, pts_ret(x0, 1150, 166, 270, 10), tc(escurece(a2, 0.08)), sombra=False, lw=4, seed=S.seed + 62 + k)
        traco(ctx, [(x0 + 136, 1190), (x0 + 136, 1240)], lw=8, seed=S.seed + 66 + k)
    # botões do fogão
    for k in range(3):
        forma(ctx, pts_elipse(860 + k * 55, 1105, 14, 14, 10), tc(INK), sombra=False, lw=0, seed=S.seed + 70 + k)


# ---------- RUA
CALCADA = 1270


def fundo_rua(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    c1, c2 = CEU.get(S.ceu, CEU["dia"])
    S.comp = True; _ceu(ctx, S, 0, 0, W, 1000, cidade=False); S.comp = False   # céu já compensado da tinta
    # prédios do fundo (silhueta)
    far = escurece(hexc(c2), 0.3) if S.ceu != "noite" else hexc("#24214F")
    xx = -20; k = 0
    while xx < W:
        bw = 120 + (k * 41) % 80; bh = 420 + (k * 97) % 260
        ctx.rectangle(xx, 1000 - bh, bw, bh + 10); xx += bw + 10; k += 1
    ctx.set_source_rgb(*far); ctx.fill()
    # prédios da frente, coloridos
    pred = [(0, 330, 360, a2), (360, 520, 380, mix(bg, BRANCO, 0.25)), (740, 260, 360, a1)]
    for i, (x0, topo, w, cor) in enumerate(pred):
        forma(ctx, pts_ret(x0 - 10, topo, w + 20, CALCADA - topo + 20, 6), cor, seed=S.seed + 140 + i, sombreado=0.04)
        forma(ctx, pts_ret(x0 - 24, topo - 30, w + 48, 40, 6), escurece(cor, 0.25), seed=S.seed + 143 + i, sombra_off=(5, 6))
        for j in range(int((CALCADA - 260 - topo) // 150)):
            for c in range(2):
                wx, wy = x0 + 50 + c * (w - 100) / 2 + 10, topo + 50 + j * 150
                forma(ctx, pts_ret(wx, wy, (w - 160) / 2, 90, 8), VIDRO_CLARO, sombra=False, lw=4, seed=S.seed + 150 + i * 20 + j * 2 + c)
                if S.luz == "noite" and (i + j + c) % 2 == 0:
                    S.apos.append(lambda ctx, wx=wx, wy=wy, ww=(w - 160) / 2: _ret(ctx, wx + 6, wy + 6, ww - 12, 78, hexc("#FFD36A")))
    # loja com toldo listrado no prédio do meio
    forma(ctx, pts_ret(400, 1000, 300, 270, 8), escurece(a3, 0.1), seed=S.seed + 160)
    forma(ctx, pts_ret(430, 1030, 110, 240, 6), VIDRO_CLARO, sombra=False, lw=4, seed=S.seed + 161)
    forma(ctx, pts_ret(570, 1030, 100, 240, 6), MADEIRA, sombra=False, lw=4, seed=S.seed + 162)
    for k in range(6):
        xx = 380 + k * 57
        forma(ctx, [(xx, 940), (xx + 57, 940), (xx + 57, 1000), (xx + 28, 1018), (xx, 1000)], VERMELHO if k % 2 else BRANCO,
              sombra=k == 0, lw=4, seed=S.seed + 163 + k, sombra_off=(5, 8))
    # calçada, meio-fio e asfalto
    _ret(ctx, 0, CALCADA - 60, W, 140, hexc("#C9C3B8"))
    for k in range(9):
        traco(ctx, [(k * 140 - 20, CALCADA - 60), (k * 140 - 60, CALCADA + 80)], lw=4, alpha=0.3, seed=S.seed + 170 + k)
    _ret(ctx, 0, CALCADA + 80, W, 30, hexc("#8E887E"))
    traco(ctx, [(-10, CALCADA + 80), (W + 10, CALCADA + 80)], lw=5, seed=S.seed + 180)
    _ret(ctx, 0, CALCADA + 110, W, H, hexc("#3A3548"))
    for k in range(5):
        ctx.rectangle(k * 260 + 40, 1660, 150, 22)
    ctx.set_source_rgb(*BRANCO); ctx.fill()
    _poste(ctx, S, 90, CALCADA + 40, 560)
    _semaforo(ctx, S, 960, CALCADA + 40, 520)
    if S.opts.get("chuva"):
        def chuva(ctx):
            r = random.Random(7)
            ctx.set_source_rgba(0.85, 0.92, 1.0, 0.35); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            for i in range(90):
                x0 = r.uniform(-200, W + 200); v = r.uniform(1400, 2000); ph = r.uniform(0, H)
                y0 = (ph + S.tv * v) % (H + 200) - 100
                ctx.move_to(x0 - y0 * 0.15, y0); ctx.line_to(x0 - y0 * 0.15 - 10, y0 + 54)
            ctx.stroke()
        S.apos.append(chuva)


def frente_rua(ctx, S):
    """Carro passando na rua, na frente dos pés de quem está na calçada."""
    cyc = 6.0
    u = ((S.tv + 1.0) % cyc) / 1.9 if S.vida else 0.55
    if u < 1:
        x = -400 + u * (W + 800)
        cor = [S.pal[3], S.pal[2], hexc("#3DAA3A")][int((S.tv + 1.0) // cyc) % 3]
        _carro(ctx, x, 1600, 1.15, S.tc(cor), S.seed + 190, S.tv, farol=S.luz == "noite")


# ---------- ÔNIBUS
def fundo_onibus(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    bob = math.sin(S.tv * 9) * 3 if S.vida else 0
    ctx.set_source_rgb(*bg); ctx.paint()
    _ret(ctx, 0, 0, W, 200, clareia(bg, 0.35))
    traco(ctx, [(-10, 200), (W + 10, 200)], lw=6, seed=S.seed + 1)
    forma(ctx, pts_ret(120, 60, 840, 60, 30), BRANCO, seed=S.seed + 2)                 # luz do teto
    _ret(ctx, 0, 820, W, H, escurece(bg, 0.15))
    _ret(ctx, 0, 1460, W, H, hexc("#4A4560"))
    for k in range(6):
        ctx.rectangle(0, 1500 + k * 60, W, 10)
    ctx.set_source_rgba(*INK, 0.3); ctx.fill()
    # janelões com a paisagem passando
    jan = [(20, 300), (390, 300), (760, 300)]

    def paisagem(ctx):
        ctx.save()
        for x0, _ in jan:
            ctx.rectangle(x0, 290, 300, 470)
        ctx.clip()
        _ceu_simples(ctx, S, 0, 290, W, 470)
        v = S.tv
        # morros (devagar), árvores e postes (rápido)
        cm = hexc("#3DAA3A") if S.ceu != "noite" else hexc("#1E3A3A")
        ctx.move_to(0, 760)
        for i in range(0, W + 41, 40):
            ctx.line_to(i, 620 + 40 * math.sin((i + v * 60) / 160) + bob)
        ctx.line_to(W, 760); ctx.close_path(); ctx.set_source_rgb(*S.tc(cm) if S.ceu == "noite" else cm); ctx.fill()
        for k in range(5):
            x = (k * 300 - v * 520) % (W + 300) - 150
            traco(ctx, [(x, 780), (x, 600 + bob)], lw=10, seed=S.seed + 30 + k, amp=0)
            forma(ctx, pts_elipse(x, 590 + bob, 70, 80, 14), escurece(cm, 0.2), sombra=False, lw=5, seed=S.seed + 35 + k, amp=1)
        xp = (-v * 900) % (W + 400) - 200
        traco(ctx, [(xp, 780), (xp, 380 + bob)], lw=14, seed=S.seed + 41, amp=0)
        ctx.restore()
        for x0, _ in jan:
            ctx.rectangle(x0, 290, 300, 470)
        ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke()
        # barra de segurar e alças balançando
        traco(ctx, [(-10, 250), (W + 10, 250)], lw=16, cor=S.tc(CINZA), seed=S.seed + 50)
        traco(ctx, [(-10, 250), (W + 10, 250)], lw=4, cor=INK, seed=S.seed + 50, alpha=0.6)
        for k, x in enumerate((210, 540, 870)):
            a = math.sin(S.tv * 2.4 + k) * 0.18 if S.vida else 0
            ex, ey = x + math.sin(a) * 120, 250 + math.cos(a) * 120
            traco(ctx, [(x, 250), (ex, ey)], lw=10, cor=S.tc(a1), seed=S.seed + 52 + k)
            forma(ctx, pts_elipse(ex, ey + 22, 26, 26, 12), S.tc(a1), sombra=False, lw=5, seed=S.seed + 55 + k)
            ctx.arc(ex, ey + 22, 12, 0, 2 * math.pi); ctx.set_source_rgb(*S.tc(clareia(bg, 0.35))); ctx.fill()
        if S.luz == "noite":
            _halo(ctx, 540, 90, 600, 0.25)
    for x0, _ in jan:
        forma(ctx, pts_ret(x0 - 16, 274, 332, 502, 20), escurece(bg, 0.3), seed=S.seed + 3 + x0)
    S.apos.append(paisagem)
    # botão de parada
    forma(ctx, pts_ret(470, 830, 140, 70, 12), VERMELHO, seed=S.seed + 60)
    texto(ctx, "PARE", 540, 865, 34, cor=BRANCO, lw=3, sombra=False)
    # bancos de trás (encostos vistos de frente) atrás da pessoa
    for x0 in (120, 600):
        forma(ctx, pts_ret(x0, 880 + bob, 380, 420, 50), a2, seed=S.seed + 70 + x0, sombreado=0.06)
        forma(ctx, pts_ret(x0 + 30, 910 + bob, 320, 120, 40), escurece(a2, 0.15), sombra=False, lw=4, seed=S.seed + 72 + x0)


def _ceu_simples(ctx, S, x, y, w, h):
    c1, c2 = CEU.get(S.ceu, CEU["dia"])
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *hexc(c1)); g.add_color_stop_rgb(1, *hexc(c2))
    ctx.rectangle(x, y, w, h); ctx.set_source(g); ctx.fill()
    nc = clareia(hexc(c2), 0.6) if S.ceu != "noite" else hexc("#3A3576")
    for k in range(3):
        ph = (k * 420 - S.tv * 80) % (w + 400) - 200
        _nuvem(ctx, x + ph, y + 70 + 40 * k, 0.6, nc, S.seed + 90 + k)
    if S.ceu == "noite":
        forma(ctx, pts_elipse(x + w * 0.2, y + 80, 34, 34, 14), hexc("#FFF1B8"), sombra=False, lw=4, seed=S.seed + 95)


def frente_onibus(ctx, S):
    """Encosto do banco da frente (esconde as pernas de quem está sentado) e a barra dele."""
    tc = S.tc; a2 = S.pal[3]
    bob = math.sin(S.tv * 9 + 0.6) * 3 if S.vida else 0
    for x0 in (120, 610):
        forma(ctx, pts_ret(x0, 1250 + bob, 380, 330, 54), tc(escurece(a2, 0.06)), seed=S.seed + 80 + x0, sombreado=0.08)
        traco(ctx, [(x0 + 40, 1240 + bob), (x0 + 340, 1240 + bob)], lw=18, cor=tc(CINZA), seed=S.seed + 82 + x0)
        traco(ctx, [(x0 + 40, 1240 + bob), (x0 + 340, 1240 + bob)], lw=4, cor=INK, seed=S.seed + 82 + x0, alpha=0.6)


# ---------- ESCOLA
def fundo_escola(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _ret(ctx, 0, 1000, W, H, escurece(bg, 0.2))
    traco(ctx, [(-10, 1000), (W + 10, 1000)], lw=6, seed=S.seed + 1)
    _chao_xadrez(ctx, S, 1440)
    # lousa
    forma(ctx, pts_ret(70, 210, 800, 520, 14), MADEIRA, seed=S.seed + 2)
    forma(ctx, pts_ret(96, 236, 748, 468, 8), hexc("#2F5D46"), sombra=False, lw=5, seed=S.seed + 3)
    giz = S.opts.get("lousa")
    if giz is None:
        for k, (x, y, s) in enumerate(((170, 330, "2 + 2 = 4"), (170, 450, "x² - 1"), (520, 600, "SILÊNCIO"))):
            ctx.select_font_face("Fredoka Light", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(56)
            ctx.move_to(x, y); ctx.set_source_rgba(1, 1, 1, 0.7); ctx.show_text(s)
        traco(ctx, [(150, 520), (420, 540), (300, 620)], lw=5, cor=(1, 1, 1), alpha=0.5, seed=S.seed + 4)
    elif giz:
        linhas = str(giz).split("\n")
        for k, s in enumerate(linhas):
            texto(ctx, s, 470, 470 + (k - (len(linhas) - 1) / 2) * 96, 76, cor=hexc("#F4F4EC"), contorno=None, sombra=False, max_w=680)
    forma(ctx, pts_ret(100, 726, 740, 26, 6), MADEIRA_ESC, seed=S.seed + 5)
    forma(ctx, pts_ret(640, 704, 90, 30, 6), a1, sombra=False, lw=4, seed=S.seed + 6)
    for k in range(3):
        forma(ctx, pts_ret(220 + k * 40, 714, 30, 12, 4), BRANCO, sombra=False, lw=3, seed=S.seed + 7 + k)
    _relogio(ctx, S, 970, 320, 62)
    # cartaz do alfabeto
    forma(ctx, pts_ret(900, 450, 150, 230, 8), BRANCO, seed=S.seed + 8)
    texto(ctx, "Aa", 975, 530, 64, cor=a1, lw=4, sombra=False)
    texto(ctx, "Bb", 975, 625, 56, cor=a2, lw=4, sombra=False)
    # luz fluorescente
    forma(ctx, pts_ret(140, 70, 300, 40, 18), BRANCO, seed=S.seed + 9)
    forma(ctx, pts_ret(640, 70, 300, 40, 18), BRANCO, seed=S.seed + 10)
    if S.luz == "noite":
        S.apos.append(lambda c: (_halo(c, 290, 90, 420, 0.3), _halo(c, 790, 90, 420, 0.3)))
    # carteiras do fundo (menores) e cadeira da carteira da frente
    for x0 in (30, 860):
        _carteira(ctx, S, x0 + 95, 1080, 0.62, S.pal[3], lambda c: c, S.seed + x0)
    forma(ctx, pts_ret(380, 960, 320, 260, 40), escurece(a2, 0.25), seed=S.seed + 20)        # encosto da cadeira


def _carteira(ctx, S, cx, ytopo, s, cor, tc, seed):
    w = 520 * s
    forma(ctx, pts_ret(cx - w / 2, ytopo, w, 40 * s, 10), tc(MADEIRA), seed=seed)
    for sx in (-1, 1):
        traco(ctx, [(cx + sx * (w / 2 - 40 * s), ytopo + 40 * s), (cx + sx * (w / 2 - 50 * s), ytopo + 330 * s)], lw=12 * s + 2,
              cor=tc(CINZA), seed=seed + sx)
        traco(ctx, [(cx + sx * (w / 2 - 40 * s), ytopo + 40 * s), (cx + sx * (w / 2 - 50 * s), ytopo + 330 * s)], lw=3, cor=INK,
              seed=seed + sx, alpha=0.5)
    forma(ctx, pts_ret(cx - w / 2 + 20 * s, ytopo + 40 * s, w - 40 * s, 90 * s, 6), tc(escurece(cor, 0.25)), sombra=False, lw=4, seed=seed + 3)


def frente_escola(ctx, S):
    tc = S.tc
    _carteira(ctx, S, 540, 1150, 1.0, S.pal[3], tc, S.seed + 30)
    forma(ctx, pts_ret(400, 1112, 200, 40, 6), tc(BRANCO), sombra=False, lw=4, seed=S.seed + 40)          # caderno
    forma(ctx, pts_ret(400, 1112, 100, 40, 6), tc(S.pal[2]), sombra=False, lw=4, seed=S.seed + 41)
    traco(ctx, [(640, 1128), (760, 1110)], lw=12, cor=tc(AMARELO), seed=S.seed + 42)                       # lápis
    traco(ctx, [(640, 1128), (760, 1110)], lw=3, cor=INK, seed=S.seed + 42, alpha=0.6)


# ---------- CARRO
def fundo_carro(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    if S.opts.get("vista") == "motorista":
        return _carro_motorista_fundo(ctx, S)
    ctx.set_source_rgb(*escurece(bg, 0.3)); ctx.paint()          # forro do teto e laterais
    # vidro de trás com a rua passando de lado
    def vidro(ctx):
        ctx.save(); ctx.rectangle(80, 330, 920, 420); ctx.clip()
        _ceu_simples(ctx, S, 80, 330, 920, 420)
        v = S.tv
        for k in range(6):
            x = (k * 230 - v * 300) % (920 + 400) - 120
            bh = 180 + (k * 61) % 120
            forma(ctx, pts_ret(x, 750 - bh, 160, bh + 20, 6), S.tc(mix(a2, BRANCO, 0.2 + 0.1 * (k % 3))) if S.luz else mix(a2, BRANCO, 0.2 + 0.1 * (k % 3)),
                  sombra=False, lw=4, seed=S.seed + 10 + k, amp=0.8)
        for k in range(3):
            x = (k * 380 - v * 700) % (920 + 300) - 80
            traco(ctx, [(x, 760), (x, 470)], lw=12, seed=S.seed + 20 + k, amp=0)
            forma(ctx, pts_elipse(x, 470, 60, 70, 12), VERDE, sombra=False, lw=4, seed=S.seed + 23 + k)
        ctx.restore()
        forma(ctx, pts_ret(80, 330, 920, 420, 60), BRANCO, sombra=False, lw=6, seed=S.seed + 26, contorno=INK) if False else None
        ctx.rectangle(80, 330, 920, 420); ctx.set_line_width(6); ctx.set_source_rgb(*INK); ctx.stroke()
    S.apos.append(vidro)
    # bancos (encostos e apoios de cabeça) atrás das pessoas
    for cx in (320, 760):
        traco(ctx, [(cx - 50, 760), (cx - 50, 840)], lw=10, seed=S.seed + 33 + cx)
        traco(ctx, [(cx + 50, 760), (cx + 50, 840)], lw=10, seed=S.seed + 34 + cx)
        forma(ctx, pts_ret(cx - 200, 820, 400, 640, 80), a2, seed=S.seed + 30 + cx, sombreado=0.08)
        forma(ctx, pts_ret(cx - 110, 620, 220, 150, 50), escurece(a2, 0.1), seed=S.seed + 32 + cx)
    if S.luz == "noite":   # luz de poste passando pelo carro
        u = (S.tv % 2.2) / 2.2
        S.apos.append(lambda c: _halo(c, -300 + u * (W + 600), 500, 520, 0.22))


def _carro_motorista_fundo(ctx, S):
    """Visão do motorista: a rua vindo no para-brisa."""
    v = S.tv
    _ceu_simples(ctx, S, 0, 0, W, 760)
    hz = 760
    grama = hexc("#3DAA3A") if S.ceu != "noite" else hexc("#1E3A3A")
    _ret(ctx, 0, hz, W, H - hz, grama)
    ctx.move_to(W / 2 - 30, hz); ctx.line_to(W / 2 + 30, hz); ctx.line_to(W + 500, H); ctx.line_to(-500, H); ctx.close_path()
    ctx.set_source_rgb(*hexc("#3A3548")); ctx.fill()
    # faixas vindo
    for k in range(6):
        u = ((k / 6) + v * 0.9) % 1.0
        p0, p1 = u ** 2.2, min(1, (u + 0.07) ** 2.2)
        y0, y1 = hz + p0 * (H - hz), hz + p1 * (H - hz)
        w0, w1 = 4 + 40 * p0, 4 + 40 * p1
        ctx.move_to(W / 2 - w0, y0); ctx.line_to(W / 2 + w0, y0); ctx.line_to(W / 2 + w1, y1); ctx.line_to(W / 2 - w1, y1); ctx.close_path()
    ctx.set_source_rgb(*BRANCO); ctx.fill()
    for k in range(4):   # postes/árvores passando dos lados
        u = ((k / 4) + v * 0.5) % 1.0
        p = u ** 2
        for lado in (-1, 1):
            x = W / 2 + lado * (60 + p * 1100); y = hz + p * (H - hz) * 0.9
            s = 0.15 + p * 1.6
            traco(ctx, [(x, y), (x, y - 300 * s)], lw=max(3, 14 * s), seed=S.seed + 40 + k, amp=0)
            forma(ctx, pts_elipse(x, y - 300 * s, 70 * s, 80 * s, 12), escurece(VERDE, 0.1), sombra=False, lw=max(2, 5 * s),
                  seed=S.seed + 44 + k + lado, amp=0.6)


def frente_carro(ctx, S):
    tc = S.tc; bg, a2 = S.pal[0], S.pal[3]
    painel = tc(escurece(bg, 0.55))
    if S.opts.get("vista") == "motorista":
        _ret(ctx, 0, 0, W, 90, painel)
        forma(ctx, [(-40, 0), (120, 0), (40, 1100), (-40, 1100)], painel, seed=S.seed + 1)
        forma(ctx, [(W + 40, 0), (W - 120, 0), (W - 40, 1100), (W + 40, 1100)], painel, seed=S.seed + 2)
        forma(ctx, [(-40, 1180), (W + 40, 1180), (W + 40, H + 40), (-40, H + 40)], painel, seed=S.seed + 3)
        _retrovisor(ctx, S, 540, 90)
        ctx.save(); ctx.translate(300, 1500)
        ctx.arc(0, 0, 300, 0, 2 * math.pi); ctx.arc_negative(0, 0, 250, 2 * math.pi, 0)
        ctx.set_source_rgb(*tc(hexc("#2B2440"))); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
        traco(ctx, [(-250, 0), (250, 0)], lw=40, cor=tc(hexc("#2B2440")), seed=S.seed + 4); ctx.restore()
        _radio(ctx, S, 760, 1260)
        return
    # vista de dentro, de frente para as pessoas: colunas, teto e painel
    forma(ctx, [(-40, -40), (W + 40, -40), (W + 40, 170), (-40, 230)], painel, seed=S.seed + 1)
    forma(ctx, [(-40, -40), (90, -40), (40, 1200), (-40, 1200)], painel, seed=S.seed + 2)
    forma(ctx, [(W + 40, -40), (W - 90, -40), (W - 40, 1200), (W + 40, 1200)], painel, seed=S.seed + 3)
    _retrovisor(ctx, S, 540, 190)
    forma(ctx, [(-40, 1150), (W + 40, 1150), (W + 40, H + 40), (-40, H + 40)], tc(escurece(bg, 0.35)), seed=S.seed + 5)
    forma(ctx, pts_ret(-20, 1130, W + 40, 60, 24), painel, seed=S.seed + 6)
    _radio(ctx, S, 540, 1260)
    # volante na frente do motorista
    vol = tc(hexc("#2B2440"))
    ctx.save(); ctx.translate(320, 1090); ctx.scale(1, 0.8)
    ctx.arc(0, 0, 175, 0, 2 * math.pi); ctx.arc_negative(0, 0, 140, 2 * math.pi, 0)
    ctx.restore()
    ctx.set_source_rgb(*vol); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(6); ctx.stroke()
    traco(ctx, [(320, 1150), (320, 1220)], lw=34, cor=vol, seed=S.seed + 13)
    forma(ctx, pts_elipse(320, 1150, 44, 34, 14), vol, seed=S.seed + 14, sombra_off=(5, 5))
    # reflexo no para-brisa
    ctx.move_to(700, 240); ctx.line_to(800, 240); ctx.line_to(620, 700); ctx.line_to(560, 700); ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.10); ctx.fill()


def _retrovisor(ctx, S, x, y):
    traco(ctx, [(x, y - 40), (x, y)], lw=10, seed=S.seed + 7)
    forma(ctx, pts_ret(x - 110, y, 220, 60, 22), S.tc(hexc("#2B2440")), seed=S.seed + 8)
    forma(ctx, pts_ret(x - 94, y + 12, 188, 36, 14), S.tc(VIDRO_CLARO), sombra=False, lw=4, seed=S.seed + 9)
    a = math.sin(S.tv * 2.2) * 0.35 if S.vida else 0          # cheirinho pendurado balançando
    ex, ey = x + math.sin(a) * 90, y + 60 + math.cos(a) * 90
    traco(ctx, [(x, y + 60), (ex, ey)], lw=3, seed=S.seed + 10, amp=0)
    forma(ctx, [(ex, ey - 6), (ex + 30, ey + 30), (ex, ey + 80), (ex - 30, ey + 30)], S.tc(VERDE), seed=S.seed + 11, sombra_off=(4, 5), reto=False)


def _radio(ctx, S, x, y):
    forma(ctx, pts_ret(x - 120, y - 50, 240, 100, 16), S.tc(INK), sombra=False, lw=4, seed=S.seed + 12)
    cor = hexc("#38D1C6")
    ctx.select_font_face("Fredoka Light", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(40)
    ctx.move_to(x - 70, y + 14); ctx.set_source_rgb(*cor); ctx.show_text("98.5")
    for k in range(5):
        h = 10 + 24 * abs(math.sin(S.tv * 6 + k * 1.3))
        ctx.rectangle(x + 40 + k * 12, y + 20 - h, 8, h)
    ctx.fill()


# ============================ CENÁRIOS TEMÁTICOS (fundo condizente com a história, sempre com vida) ============================
CORES_LUZ = [hexc("#FF3B3B"), hexc("#FFD21F"), hexc("#3DDC5A"), hexc("#38B6FF"), hexc("#FF5FD2")]


def _lampadas(ctx, S, pts, r=9, ritmo=6, passo=3, glow=0.0, seed=0):
    """Pisca-pisca: lâmpadas coloridas acendendo em sequência (corre-corre). Desenha depois da tinta."""
    fase = int(S.tv * ritmo) if S.vida else 0
    for i, (x, y) in enumerate(pts):
        c = CORES_LUZ[(i + seed) % len(CORES_LUZ)]
        on = (i + fase) % passo != 0
        if on and glow:
            g = cairo.RadialGradient(x, y, 0, x, y, r * 4)
            g.add_color_stop_rgba(0, *c, glow); g.add_color_stop_rgba(1, *c, 0)
            ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD); ctx.set_source(g); ctx.arc(x, y, r * 4, 0, 2 * math.pi); ctx.fill(); ctx.restore()
        ctx.new_sub_path(); ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgb(*(clareia(c, 0.25) if on else S.tc(escurece(c, 0.55)))); ctx.fill_preserve()
        ctx.set_source_rgb(*INK); ctx.set_line_width(2.5); ctx.stroke()


def _fio(a, b, n, cai=30):
    """n pontos num fio pendurado de a até b (catenária simples)."""
    out = []
    for i in range(n):
        u = (i + 0.5) / n
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u + math.sin(u * math.pi) * cai))
    return out


def _arvore_natal(ctx, S, cx, base, alt, seed=0):
    verde = hexc("#1F8A4C")
    forma(ctx, pts_ret(cx - 30, base - 70, 60, 70, 6), MADEIRA_ESC, seed=S.seed + 300 + seed)
    luzes = []
    for k in range(3):
        y1 = base - 60 - k * alt * 0.27; y0 = y1 - alt * 0.42; w = alt * (0.42 - k * 0.1)
        forma(ctx, [(cx - w, y1), (cx + w, y1), (cx, y0)], escurece(verde, 0.06 * k), seed=S.seed + 301 + k + seed, sombreado=0.08)
        luzes += _fio((cx - w * 0.85, y1 - 30), (cx + w * 0.8, y1 - 60), 7, cai=20)
    topo = base - 60 - 2 * alt * 0.27 - alt * 0.42
    estrela = [(cx + math.cos(-math.pi / 2 + k * math.pi / 5) * (44 if k % 2 == 0 else 19),
                topo + math.sin(-math.pi / 2 + k * math.pi / 5) * (44 if k % 2 == 0 else 19)) for k in range(10)]

    def acesa(ctx):
        _lampadas(ctx, S, luzes, r=10, glow=0.5 if S.luz == "noite" else 0.25, seed=seed)
        brilho = 0.6 + 0.4 * math.sin(S.tv * 5)
        _halo(ctx, cx, topo, 140, 0.35 * brilho)
        forma(ctx, estrela, AMARELO, sombra=False, lw=4, seed=S.seed + 310 + seed)
    S.apos.append(acesa)
    return luzes


def _presente(ctx, S, x, base, w, h, cor, laco, seed):
    forma(ctx, pts_ret(x, base - h, w, h, 6), cor, seed=S.seed + seed, sombra_off=(6, 6))
    _ret(ctx, x + w / 2 - 9, base - h, 18, h, laco); _ret(ctx, x, base - h * 0.55, w, 16, laco)
    forma(ctx, pts_elipse(x + w / 2 - 18, base - h - 10, 18, 12, 10), laco, sombra=False, lw=4, seed=S.seed + seed + 1, reto=False)
    forma(ctx, pts_elipse(x + w / 2 + 18, base - h - 10, 18, 12, 10), laco, sombra=False, lw=4, seed=S.seed + seed + 2, reto=False)


def _estrelas(ctx, S, x, y, w, h, n=40, seed=0):
    r = random.Random(S.seed + seed)
    for i in range(n):
        sx, sy = x + r.uniform(0, w), y + r.uniform(0, h)
        a = 0.45 + 0.55 * abs(math.sin(S.tv * r.uniform(1.5, 4) + i))
        ctx.new_sub_path(); ctx.arc(sx, sy, r.uniform(2, 4.5), 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 0.92, a); ctx.fill()


# ---------- CASA DE NATAL (fachada, noite quente, vizinho exagerado)
def fundo_casa_natal_fora(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    S.comp = True; _ceu(ctx, S, 0, 0, W, 1320, cidade=False); S.comp = False
    _ret(ctx, 0, 1300, W, H, hexc("#2F7A3A"))
    forma(ctx, [(380, 1300), (520, 1300), (600, H + 20), (300, H + 20)], hexc("#C9C3B8"), sombra=False, seed=S.seed + 200)
    # casa do vizinho (direita), coberta de luz
    forma(ctx, pts_ret(780, 700, 400, 620, 6), escurece(a2, 0.1), seed=S.seed + 201)
    forma(ctx, [(740, 720), (1220, 720), (980, 470)], escurece(a1, 0.3), seed=S.seed + 202)
    forma(ctx, pts_ret(840, 830, 120, 130, 6), hexc("#FFE6A0"), sombra=False, lw=4, seed=S.seed + 203)
    # casa principal
    casa = a3 if sum(a3) < 2.6 else mix(a3, bg, 0.35)
    forma(ctx, pts_ret(130, 640, 600, 680, 8), casa, seed=S.seed + 204, sombreado=0.05)
    forma(ctx, [(80, 660), (780, 660), (430, 360)], escurece(bg, 0.25), seed=S.seed + 205)
    forma(ctx, pts_ret(560, 380, 70, 170, 6), escurece(bg, 0.35), seed=S.seed + 206)        # chaminé
    _porta_desenho(ctx, 430, 1320 - 330 / 1, 230, 560, 0, a1, hexc("#FFE7B0"), S.seed + 207)  # porta (âncora "porta")
    # guirlanda na porta
    forma(ctx, pts_elipse(430, 880, 46, 46, 16), hexc("#1F8A4C"), sombra=False, lw=5, seed=S.seed + 208, reto=False)
    ctx.arc(430, 880, 22, 0, 2 * math.pi); ctx.set_source_rgb(*casa); ctx.fill()
    forma(ctx, pts_elipse(430, 918, 14, 10, 8), VERMELHO, sombra=False, lw=3, seed=S.seed + 209)
    # janela com a árvore acesa dentro
    jx, jy, jw, jh = 170, 780, 170, 220
    forma(ctx, pts_ret(jx - 14, jy - 14, jw + 28, jh + 28, 8), BRANCO, seed=S.seed + 210)
    luzes_teto = _fio((90, 660), (430, 365), 12, cai=12) + _fio((430, 365), (770, 660), 12, cai=12)
    luzes_casa = _fio((140, 660), (720, 660), 16, cai=40)
    luzes_viz = []
    for j in range(6):
        luzes_viz += _fio((790, 740 + j * 95), (1180, 740 + j * 95), 11, cai=18)
    luzes_viz += _fio((750, 720), (980, 480), 9, cai=0) + _fio((980, 480), (1210, 720), 9, cai=0)

    def acesas(ctx):
        ctx.save(); ctx.rectangle(jx, jy, jw, jh); ctx.clip()
        _ret(ctx, jx, jy, jw, jh, hexc("#FFD98A"))
        forma(ctx, [(jx + 30, jy + jh), (jx + jw - 30, jy + jh), (jx + jw / 2, jy + 40)], hexc("#1F8A4C"), sombra=False, lw=4, seed=S.seed + 211)
        _lampadas(ctx, S, [(jx + 50 + (k * 37) % 80, jy + 90 + k * 22) for k in range(6)], r=7, ritmo=4)
        ctx.restore()
        traco(ctx, [(jx + jw / 2, jy), (jx + jw / 2, jy + jh)], lw=8, cor=S.tc(BRANCO), amp=0)
        ctx.rectangle(jx, jy, jw, jh); ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.stroke()
        _halo(ctx, jx + jw / 2, jy + jh / 2, 260, 0.25)
        # vizinho: luz demais (pisca tudo junto, alternando)
        pulsa = 0.5 + 0.5 * math.sin(S.tv * 7)
        _halo(ctx, 990, 800, 700, 0.30 + 0.15 * pulsa)
        _lampadas(ctx, S, luzes_viz, r=11, ritmo=9, passo=2, glow=0.45)
        est = [(980 + math.cos(-math.pi / 2 + k * math.pi / 5) * (70 if k % 2 == 0 else 30),
                420 + math.sin(-math.pi / 2 + k * math.pi / 5) * (70 if k % 2 == 0 else 30)) for k in range(10)]
        _halo(ctx, 980, 420, 260, 0.5 * pulsa + 0.2)
        forma(ctx, est, AMARELO, sombra=False, lw=5, seed=S.seed + 212)
        _lampadas(ctx, S, luzes_teto + luzes_casa, r=10, ritmo=5, glow=0.35)
    S.apos.append(acesas)


def frente_casa_natal_fora(ctx, S):
    """Cerquinha baixa na frente (esconde as pernas de quem está no quintal)."""
    c = S.tc(BRANCO)
    for x in range(-20, W + 40, 70):
        forma(ctx, [(x, 1530), (x + 22, 1500), (x + 44, 1530), (x + 44, 1660), (x, 1660)], c, seed=S.seed + 220 + x, sombra_off=(6, 6))
    for y in (1560, 1620):
        forma(ctx, pts_ret(-20, y, W + 40, 20, 4), c, sombra=False, lw=4, seed=S.seed + 221 + y)
    luzes = _fio((-10, 1510), (W + 10, 1510), 18, cai=16)
    _lampadas(ctx, S, luzes, r=9, ritmo=5, glow=0.3 if S.luz == "noite" else 0)


# ---------- SALA DE NATAL (calor: ventilador girando, ceia)
def fundo_sala_natal(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _papel_parede(ctx, S, bg2)
    _rodape(ctx, S, 1400, bg)
    _chao_tacos(ctx, S, 1400, MADEIRA_ESC)
    _janela(ctx, S, 470, 280, 260, 320, cortina=True)
    # festão com bolinhas no alto
    pts = _fio((-10, 200), (W + 10, 200), 9, cai=50)
    traco(ctx, [(-10, 200)] + pts + [(W + 10, 200)], lw=18, cor=hexc("#1F8A4C"), seed=S.seed + 320)
    for i, (x, y) in enumerate(pts):
        forma(ctx, pts_elipse(x, y + 26, 18, 18, 10), [VERMELHO, AMARELO, S.pal[3]][i % 3], sombra=False, lw=4, seed=S.seed + 321 + i)
    _relogio(ctx, S, 880, 380, 54)
    _arvore_natal(ctx, S, 230, 1400, 900)
    for k, (x, w, h, c, l) in enumerate(((60, 120, 100, a2, AMARELO), (190, 100, 140, VERMELHO, BRANCO), (300, 140, 90, a1, VERMELHO))):
        _presente(ctx, S, x, 1440, w, h, c, l, 330 + k * 5)
    _ventilador(ctx, S, 620, 110, 0.9)
    # ventilador de pé também (calor de dezembro)
    traco(ctx, [(980, 1400), (980, 1020)], lw=12, seed=S.seed + 340)
    forma(ctx, pts_elipse(980, 1400, 60, 16, 12), INK, sombra=False, lw=0, seed=S.seed + 341)
    forma(ctx, pts_elipse(980, 960, 95, 95, 20), clareia(a3, 0.2), seed=S.seed + 342)
    ang = S.tv * 2 * math.pi * 2.3
    for k in range(3):
        a = ang + k * 2 * math.pi / 3
        forma(ctx, pts_elipse(980 + math.cos(a) * 45, 960 + math.sin(a) * 45, 40, 22, 10), a1, sombra=False, lw=3,
              seed=S.seed + 343 + k, reto=False)
    for k in range(7):
        ctx.arc(980, 960, 30 + k * 10, 0, 2 * math.pi); ctx.new_sub_path()
    ctx.set_source_rgba(*INK, 0.5); ctx.set_line_width(2); ctx.stroke()


def frente_sala_natal(ctx, S):
    """Mesa da ceia: toalha, peru, farofa, panetone e copos."""
    tc = S.tc; a1 = S.pal[2]
    forma(ctx, pts_ret(520, 1110, 600, 60, 10), tc(BRANCO), seed=S.seed + 350)
    forma(ctx, [(530, 1160), (1100, 1160), (1100, 1330), (1020, 1300), (940, 1330), (860, 1300), (780, 1330), (700, 1300),
                (620, 1330), (530, 1300)], tc(VERMELHO), seed=S.seed + 351, sombreado=0.05)
    forma(ctx, pts_elipse(780, 1090, 130, 34, 18), tc(BRANCO), sombra=False, lw=4, seed=S.seed + 352)            # travessa
    forma(ctx, pts_elipse(780, 1050, 100, 60, 18), tc(hexc("#C9792B")), seed=S.seed + 353, sombreado=0.15)        # peru
    for sx in (-1, 1):
        traco(ctx, [(780 + sx * 70, 1030), (780 + sx * 110, 990)], lw=16, cor=tc(hexc("#C9792B")), seed=S.seed + 354 + sx)
        forma(ctx, pts_elipse(780 + sx * 114, 985, 12, 12, 8), tc(BRANCO), sombra=False, lw=3, seed=S.seed + 356 + sx)
    _vapor(ctx, S, 780, 990, 1.0)
    forma(ctx, pts_ret(590, 1030, 90, 80, 30), tc(hexc("#E8C07A")), seed=S.seed + 358)                            # panetone
    forma(ctx, pts_elipse(950, 1095, 70, 22, 14), tc(hexc("#F2D48A")), seed=S.seed + 359)                         # farofa
    for k, x in enumerate((1010, 1060)):
        forma(ctx, pts_ret(x - 14, 1040, 28, 70, 6), tc(clareia(a1, 0.3)), sombra=False, lw=4, seed=S.seed + 360 + k)


# ---------- LOJA (liquidação, gente passando atrás da vitrine)
def _silhuetas(ctx, S, x0, x1, chao, s=1.0, n=4, vel=90, cor=None, seed=0):
    cor = cor or escurece(S.pal[0], 0.6)
    w = x1 - x0
    for k in range(n):
        sent = 1 if k % 2 == 0 else -1
        ph = (k * w / n * 1.7 + sent * S.tv * vel * (0.8 + 0.15 * k)) % (w + 200) - 100
        x = x0 + ph
        b = abs(math.sin(S.tv * 6 + k)) * 6
        hs = s * (0.9 + 0.12 * (k % 3))
        ctx.new_sub_path(); ctx.arc(x, chao - 330 * hs - b, 36 * hs, 0, 2 * math.pi)
        ctx.rectangle(x - 45 * hs, chao - 290 * hs - b, 90 * hs, 170 * hs)
        for sx in (-1, 1):
            ctx.rectangle(x + sx * 22 * hs - 14 * hs + math.sin(S.tv * 6 + k) * sx * 10 * hs, chao - 125 * hs - b, 28 * hs, 125 * hs)
    ctx.set_source_rgba(*cor, 0.85); ctx.fill()


def _placa(ctx, S, cx, cy, txt, cor, rot=0.0, piscando=True, seed=0):
    on = (int(S.tv * 2.5 + seed) % 2 == 0) or not piscando or not S.vida
    bal = math.sin(S.tv * 1.8 + seed) * 0.05 + rot
    ctx.save(); ctx.translate(cx, cy - 90); ctx.rotate(bal); ctx.translate(-cx, -(cy - 90))
    traco(ctx, [(cx - 70, cy - 200), (cx - 70, cy - 60)], lw=4, amp=0); traco(ctx, [(cx + 70, cy - 200), (cx + 70, cy - 60)], lw=4, amp=0)
    c = cor if on else escurece(cor, 0.35)
    forma(ctx, pts_ret(cx - 130, cy - 70, 260, 140, 18), c, seed=S.seed + seed)
    texto(ctx, txt, cx, cy, 64, cor=AMARELO if on else BRANCO, max_w=220)
    ctx.restore()


def fundo_loja(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _ret(ctx, 0, 1400, W, H, clareia(bg2, 0.5))
    for k in range(9):
        traco(ctx, [(k * 140 - 40, 1400), (k * 180 - 260, H)], lw=4, alpha=0.25, seed=S.seed + 400 + k)
    # vitrine dos fundos: corredor do shopping com gente passando
    vx, vy, vw, vh = 70, 300, 940, 380
    forma(ctx, pts_ret(vx - 18, vy - 18, vw + 36, vh + 36, 10), escurece(bg, 0.4), seed=S.seed + 401)

    def vitrine(ctx):
        ctx.save(); ctx.rectangle(vx, vy, vw, vh); ctx.clip()
        _ret(ctx, vx, vy, vw, vh, clareia(bg2, 0.65))
        _ret(ctx, vx, vy + vh - 60, vw, 60, clareia(bg2, 0.45))
        _silhuetas(ctx, S, vx, vx + vw, vy + vh - 10, s=0.85, n=5, cor=escurece(bg, 0.5))
        ctx.move_to(vx + 120, vy); ctx.line_to(vx + 220, vy); ctx.line_to(vx + 120, vy + vh); ctx.line_to(vx + 20, vy + vh); ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.18); ctx.fill()
        ctx.restore()
        for k in (1, 2):
            traco(ctx, [(vx + vw * k / 3, vy), (vx + vw * k / 3, vy + vh)], lw=10, cor=S.tc(escurece(bg, 0.4)), amp=0)
        ctx.rectangle(vx, vy, vw, vh); ctx.set_line_width(5); ctx.set_source_rgb(*INK); ctx.stroke()
    S.apos.append(vitrine)
    # araras de roupa e prateleiras
    for k in range(2):
        y = 860 + k * 190
        forma(ctx, pts_ret(40, y, 380, 22, 4), MADEIRA, seed=S.seed + 410 + k, sombra_off=(6, 6))
        for j in range(5):
            c = [a1, a2, a3, VERDE, AMARELO][(j + k) % 5]
            forma(ctx, pts_ret(60 + j * 72, y - 90, 62, 90, 8), c, sombra=False, lw=4, seed=S.seed + 412 + j + k * 5)
            traco(ctx, [(60 + j * 72, y - 60), (122 + j * 72, y - 60)], lw=3, alpha=0.4, seed=S.seed + 420 + j)
    traco(ctx, [(560, 760), (1040, 760)], lw=10, seed=S.seed + 430)
    for j in range(6):
        bal = math.sin(S.tv * 1.5 + j) * 3
        x = 600 + j * 75
        traco(ctx, [(x, 760), (x + bal, 790)], lw=4, amp=0)
        c = [a2, a1, AMARELO, a3, VERDE, a2][j]
        forma(ctx, [(x - 40 + bal, 790), (x + 40 + bal, 790), (x + 50 + bal, 830), (x + 34 + bal, 830), (x + 34 + bal, 980),
                    (x - 34 + bal, 980), (x - 34 + bal, 830), (x - 50 + bal, 830)], c, seed=S.seed + 431 + j, sombra_off=(5, 6))
    _placa(ctx, S, 270, 250, S.opts.get("placa", "-50%"), VERMELHO, seed=1)
    _placa(ctx, S, 810, 250, S.opts.get("placa2", "PROMO"), escurece(a2, 0.1), seed=2)
    forma(ctx, pts_ret(140, 70, 300, 36, 18), BRANCO, seed=S.seed + 440); forma(ctx, pts_ret(640, 70, 300, 36, 18), BRANCO, seed=S.seed + 441)


def frente_loja(ctx, S):
    tc = S.tc; a1, a2 = S.pal[2], S.pal[3]
    forma(ctx, pts_ret(600, 1090, 520, 46, 10), tc(MADEIRA), seed=S.seed + 450)
    forma(ctx, pts_ret(620, 1130, 480, 330, 10), tc(escurece(a2, 0.1)), seed=S.seed + 451, sombreado=0.05)
    forma(ctx, pts_ret(860, 990, 170, 100, 12), tc(hexc("#2B2440")), seed=S.seed + 452)     # caixa registradora
    forma(ctx, pts_ret(880, 1005, 130, 40, 6), hexc("#38D1C6"), sombra=False, lw=3, seed=S.seed + 453)
    forma(ctx, [(660, 1090), (760, 1090), (750, 1010), (670, 1010)], tc(a1), seed=S.seed + 454)                   # sacola
    traco(ctx, [(685, 1010), (710, 975), (735, 1010)], lw=6, seed=S.seed + 455)


# ---------- SUPERMERCADO (corredor em perspectiva)
def fundo_supermercado(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    vx, vy = 540, 760
    ctx.set_source_rgb(*clareia(bg, 0.55)); ctx.paint()
    _ret(ctx, 0, 0, W, 150, BRANCO)
    for k in range(4):     # luzes do teto em perspectiva
        u = 0.25 + k * 0.22
        ctx.rectangle(vx - 200 * u, 150 + (vy - 150) * (1 - u) * 0.35 - 20 * u, 400 * u, 22 * u)
    ctx.set_source_rgb(*BRANCO); ctx.fill()
    g = cairo.LinearGradient(0, vy, 0, H)
    g.add_color_stop_rgb(0, *clareia(bg2, 0.6)); g.add_color_stop_rgb(1, *clareia(bg2, 0.3))
    ctx.move_to(vx - 60, vy); ctx.line_to(vx + 60, vy); ctx.line_to(W + 400, H); ctx.line_to(-400, H); ctx.close_path(); ctx.set_source(g); ctx.fill()
    # fundo do corredor
    forma(ctx, pts_ret(vx - 90, vy - 200, 180, 200, 6), escurece(bg, 0.1), seed=S.seed + 500)
    _silhuetas(ctx, S, vx - 90, vx + 90, vy, s=0.3, n=1, vel=40, cor=escurece(bg, 0.55))
    cores = [a1, a2, a3, VERDE, AMARELO, VERMELHO, hexc("#38B6FF")]
    for lado in (-1, 1):
        xin, xout = vx + lado * 90, (-60 if lado < 0 else W + 60)
        topo_in, base_in = vy - 260, vy
        topo_out, base_out = 120, 1500
        forma(ctx, [(xin, topo_in), (xout, topo_out), (xout, base_out), (xin, base_in)], escurece(bg, 0.25), seed=S.seed + 501 + lado)
        for p in range(5):   # prateleiras com produtos
            f0, f1 = p / 5, (p + 1) / 5
            yi0, yo0 = topo_in + (base_in - topo_in) * f0, topo_out + (base_out - topo_out) * f0
            yi1, yo1 = topo_in + (base_in - topo_in) * f1, topo_out + (base_out - topo_out) * f1
            for q in range(7):
                u0, u1 = (q + 0.1) / 7, (q + 0.85) / 7
                e0, e1 = u0 ** 1.6, u1 ** 1.6
                xa, xb = xin + (xout - xin) * e0, xin + (xout - xin) * e1
                ya0, yb0 = yi0 + (yo0 - yi0) * e0, yi0 + (yo0 - yi0) * e1
                ya1, yb1 = yi1 + (yo1 - yi1) * e0, yi1 + (yo1 - yi1) * e1
                hh = 0.72
                ctx.move_to(xa, ya1 - (ya1 - ya0) * hh); ctx.line_to(xb, yb1 - (yb1 - yb0) * hh); ctx.line_to(xb, yb1); ctx.line_to(xa, ya1)
                ctx.close_path(); ctx.set_source_rgb(*cores[(p * 3 + q + (lado > 0) * 2) % len(cores)]); ctx.fill_preserve()
                ctx.set_source_rgb(*INK); ctx.set_line_width(2.5 + 2 * e1); ctx.stroke()
            ctx.move_to(xin, yi1); ctx.line_to(xout, yo1); ctx.set_line_width(8); ctx.set_source_rgb(*BRANCO); ctx.stroke()
        traco(ctx, [(xin, topo_in), (xin, base_in)], lw=5, seed=S.seed + 505 + lado)
    # placa de preço pendurada balançando
    bal = math.sin(S.tv * 1.6) * 0.08 if S.vida else 0
    ctx.save(); ctx.translate(540, 150); ctx.rotate(bal)
    traco(ctx, [(-60, 0), (-60, 120)], lw=4, amp=0); traco(ctx, [(60, 0), (60, 120)], lw=4, amp=0)
    forma(ctx, pts_ret(-170, 120, 340, 150, 18), AMARELO, seed=S.seed + 510)
    texto(ctx, S.opts.get("preco", "R$ 9,99"), 0, 195, 70, cor=VERMELHO, max_w=300)
    ctx.restore()


def frente_supermercado(ctx, S):
    """Carrinho de compras (na frente das pernas de quem empurra) com coisas dentro."""
    tc = S.tc; x0, y0 = 560, 1080
    for k, (c, w, h) in enumerate(((S.pal[2], 90, 130), (VERDE, 70, 90), (S.pal[3], 110, 70), (AMARELO, 60, 110))):
        forma(ctx, pts_ret(x0 + 40 + k * 95, y0 + 20 - h, w, h, 8), tc(c), sombra=False, lw=4, seed=S.seed + 520 + k)
    forma(ctx, [(x0, y0), (x0 + 470, y0), (x0 + 430, y0 + 250), (x0 + 50, y0 + 250)], tc(CINZA), seed=S.seed + 525, sombra_off=(8, 8))
    ctx.save()
    for k in range(1, 9):
        ctx.move_to(x0 + k * 52, y0); ctx.line_to(x0 + 22 + k * 48, y0 + 250)
    for k in range(1, 4):
        ctx.move_to(x0 + 8 * k, y0 + 62 * k); ctx.line_to(x0 + 470 - 10 * k, y0 + 62 * k)
    ctx.set_source_rgba(*INK, 0.6); ctx.set_line_width(4); ctx.stroke(); ctx.restore()
    traco(ctx, [(x0 + 470, y0), (x0 + 530, y0 - 70)], lw=12, seed=S.seed + 526)
    traco(ctx, [(x0 + 80, y0 + 250), (x0 + 60, y0 + 340), (x0 + 430, y0 + 340), (x0 + 430, y0 + 250)], lw=8, seed=S.seed + 527)
    for wx in (x0 + 80, x0 + 420):
        forma(ctx, pts_elipse(wx, y0 + 365, 24, 24, 10), tc(INK), sombra=False, lw=0, seed=S.seed + 528 + wx)


# ---------- PRAIA
def fundo_praia(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    hz = 820
    S.comp = True
    c1, c2 = CEU.get(S.ceu, CEU["dia"])
    K = (lambda c: tuple(min(1.0, c[i] / S.T[i]) for i in range(3))) if S.T else (lambda c: c)
    g = cairo.LinearGradient(0, 0, 0, hz)
    g.add_color_stop_rgb(0, *K(hexc(c1))); g.add_color_stop_rgb(1, *K(hexc(c2)))
    ctx.rectangle(0, 0, W, hz); ctx.set_source(g); ctx.fill()
    sy = 300 if S.ceu == "dia" else 700
    if S.ceu != "noite":   # sol com raios girando
        ctx.save(); ctx.translate(800, sy); ctx.rotate(S.tv * 0.25)
        for k in range(12):
            ctx.save(); ctx.rotate(k * math.pi / 6); ctx.move_to(100, -14); ctx.line_to(150, 0); ctx.line_to(100, 14); ctx.close_path(); ctx.restore()
        ctx.set_source_rgba(*K(hexc("#FFE15A")), 0.8); ctx.fill(); ctx.restore()
        forma(ctx, pts_elipse(800, sy, 85, 85, 20), K(hexc("#FFE15A") if S.ceu == "dia" else hexc("#FFB347")), sombra=False, lw=5, seed=S.seed + 600)
    else:
        _estrelas(ctx, S, 0, 0, W, hz - 100, 50)
        forma(ctx, pts_elipse(800, 260, 60, 60, 18), K(hexc("#FFF1B8")), sombra=False, lw=4, seed=S.seed + 600)
    for k in range(2):
        ph = (S.tv * (16 + 8 * k) + k * 500) % (W + 300) - 150
        _nuvem(ctx, ph, 180 + 140 * k, 0.7 - 0.15 * k, K(clareia(hexc(c2), 0.6)) if S.ceu != "noite" else hexc("#3A3576"), S.seed + 601 + k)
    S.comp = False
    # mar com ondas
    mar = hexc("#1F8FD1") if S.ceu != "noite" else hexc("#163A6B")
    _ret(ctx, 0, hz, W, 400, mar)
    for k in range(6):
        y = hz + 30 + k * 55
        pts = [(x, y + math.sin(x / 70 + S.tv * (1.5 + k * 0.3) + k) * (5 + k * 2)) for x in range(-20, W + 60, 40)]
        traco(ctx, pts, lw=5 + k, cor=clareia(mar, 0.35 + k * 0.05), amp=0, alpha=0.8)
    # barquinho balançando no horizonte
    by = hz - 8 + math.sin(S.tv * 2) * 5
    forma(ctx, [(140, by), (260, by), (240, by + 26), (160, by + 26)], BRANCO, sombra=False, lw=4, seed=S.seed + 602)
    forma(ctx, [(200, by - 80), (200, by - 4), (250, by - 4)], a1, sombra=False, lw=4, seed=S.seed + 603)
    # areia e espuma indo e voltando
    praia_y = 1220 + math.sin(S.tv * 1.3) * 18
    areia = hexc("#F2D48A")
    pts = [(x, praia_y + math.sin(x / 90 + S.tv * 1.3) * 12) for x in range(-20, W + 60, 40)]
    forma(ctx, pts + [(W + 40, H + 20), (-40, H + 20)], areia, sombra=False, seed=S.seed + 604, reto=False)
    traco(ctx, pts, lw=16, cor=BRANCO, amp=0, alpha=0.9)
    r = random.Random(3)
    for k in range(30):
        ctx.new_sub_path(); ctx.arc(r.uniform(0, W), r.uniform(1300, H), 3, 0, 2 * math.pi)
    ctx.set_source_rgba(*escurece(areia, 0.3), 0.6); ctx.fill()
    # guarda-sol
    bal = math.sin(S.tv * 1.2) * 0.03
    ctx.save(); ctx.translate(230, 1420); ctx.rotate(-0.12 + bal)
    traco(ctx, [(0, 0), (0, -560)], lw=12, amp=0)
    for k in range(6):
        p = [(0, -700)] + [(-270 + (k + j / 4) * 90, -560 + 22 * math.sin(j / 4 * math.pi)) for j in range(5)]
        forma(ctx, p, VERMELHO if k % 2 else BRANCO, sombra=k == 0, lw=4, seed=S.seed + 612 + k, amp=0.8, reto=False)
    ctx.restore()
    if S.ceu != "noite" and S.vida:   # gaivota
        u = (S.tv % 7) / 7
        _passaro(ctx, -80 + u * (W + 160), 420 + math.sin(u * 9) * 30, 1.3, S.tv)


def frente_praia(ctx, S):
    """Cadeira de praia (âncora "cadeira") e baldinho."""
    tc = S.tc
    if "cadeira" in S.ocup:
        forma(ctx, [(600, 1200), (900, 1200), (930, 1380), (580, 1380)], tc(hexc("#38B6FF")), seed=S.seed + 620)
        for k in range(3):
            traco(ctx, [(620 + k * 4, 1240 + k * 50), (900 - k * 4, 1240 + k * 50)], lw=10, cor=tc(BRANCO), amp=0)
        traco(ctx, [(590, 1380), (620, 1460)], lw=10, seed=S.seed + 621); traco(ctx, [(920, 1380), (890, 1460)], lw=10, seed=S.seed + 622)
    forma(ctx, [(120, 1500), (210, 1500), (195, 1600), (135, 1600)], tc(AMARELO), seed=S.seed + 623)
    traco(ctx, [(120, 1500), (165, 1450), (210, 1500)], lw=5, seed=S.seed + 624)


# ---------- FESTA
def fundo_festa(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _papel_parede(ctx, S, bg2, passo=110, tipo="bolinhas")
    _rodape(ctx, S, 1420, bg)
    _ret(ctx, 0, 1420, W, H, escurece(bg, 0.45))
    for k in range(2):   # bandeirinhas
        pts = _fio((-20, 170 + k * 130), (W + 20, 230 + k * 120), 12, cai=60)
        traco(ctx, [(-20, 170 + k * 130)] + pts + [(W + 20, 230 + k * 120)], lw=4, seed=S.seed + 700 + k)
        for i, (x, y) in enumerate(pts):
            bal = math.sin(S.tv * 3 + i + k) * 4
            forma(ctx, [(x - 32, y), (x + 32, y), (x + bal, y + 70)], [a1, a2, a3, VERDE, AMARELO][(i + k) % 5], sombra=False, lw=4,
                  seed=S.seed + 702 + i + k * 20)
    # bolo na mesa
    forma(ctx, pts_ret(700, 1110, 340, 40, 8), BRANCO, seed=S.seed + 730)
    forma(ctx, pts_ret(730, 1150, 280, 270, 8), a2, seed=S.seed + 731)
    forma(ctx, pts_ret(780, 990, 180, 120, 16), clareia(a1, 0.4), seed=S.seed + 732, sombreado=0.1)
    forma(ctx, pts_ret(780, 990, 180, 30, 14), BRANCO, sombra=False, lw=4, seed=S.seed + 733)
    for k in range(3):
        x = 820 + k * 50
        forma(ctx, pts_ret(x - 6, 940, 12, 50, 4), [a3, AMARELO, VERDE][k], sombra=False, lw=3, seed=S.seed + 734 + k)
        fl = 1 + 0.25 * math.sin(S.tv * 18 + k * 2)
        forma(ctx, pts_elipse(x, 925 - 4 * fl, 9, 16 * fl, 10), hexc("#FFB347"), sombra=False, lw=3, seed=S.seed + 737 + k, reto=False)
    # balões subindo e descendo
    for k, (x, y, c) in enumerate(((90, 520, a1), (190, 610, a3), (110, 760, AMARELO), (980, 470, a2), (900, 600, VERDE))):
        dy = math.sin(S.tv * 1.4 + k) * 18; dx = math.sin(S.tv * 0.9 + k * 2) * 8
        traco(ctx, [(x + dx, y + dy + 80), (x + dx * 0.5 + 10, y + 250), (x, y + 420)], lw=3, seed=S.seed + 710 + k, amp=0)
        forma(ctx, pts_elipse(x + dx, y + dy, 66, 80, 18), c, seed=S.seed + 715 + k, sombreado=0.12, reto=False)
        ctx.arc(x + dx - 22, y + dy - 30, 12, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
    # globo espelhado girando
    traco(ctx, [(540, -10), (540, 60)], lw=6, seed=S.seed + 720)
    forma(ctx, pts_elipse(540, 115, 60, 60, 18), CINZA, seed=S.seed + 721)
    ctx.save(); ctx.arc(540, 115, 58, 0, 2 * math.pi); ctx.clip()
    for k in range(-4, 5):
        xx = 540 + ((k * 24 + S.tv * 40) % 216) - 108
        ctx.move_to(xx, 50); ctx.line_to(xx, 180)
    for k in range(-2, 3):
        ctx.move_to(470, 115 + k * 24); ctx.line_to(610, 115 + k * 24)
    ctx.set_source_rgba(*INK, 0.5); ctx.set_line_width(2); ctx.stroke(); ctx.restore()

    def feixes(ctx):   # luzes coloridas girando (por cima de tudo do fundo)
        ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD)
        for k, c in enumerate((CORES_LUZ[0], CORES_LUZ[3], CORES_LUZ[2], CORES_LUZ[4])):
            a = S.tv * 0.9 + k * math.pi / 2
            ang = math.pi / 2 + math.sin(a) * 0.9
            x1, y1 = 540 + math.cos(ang - 0.09) * 2200, 115 + math.sin(ang - 0.09) * 2200
            x2, y2 = 540 + math.cos(ang + 0.09) * 2200, 115 + math.sin(ang + 0.09) * 2200
            ctx.move_to(540, 115); ctx.line_to(x1, y1); ctx.line_to(x2, y2); ctx.close_path()
            ctx.set_source_rgba(*c, 0.16); ctx.fill()
        ctx.restore()
    S.apos.append(feixes)


def frente_festa(ctx, S):
    """Confete caindo na frente de tudo (leve)."""
    if not S.vida:
        return
    r = random.Random(11)
    for i in range(70):
        x0 = r.uniform(0, W); v = r.uniform(120, 260); ph = r.uniform(0, H)
        y = (ph + S.tv * v) % (H + 100) - 50
        x = x0 + math.sin(S.tv * 2 + i) * 30
        a = S.tv * r.uniform(2, 6) + i
        c = CORES_LUZ[i % len(CORES_LUZ)]
        ctx.save(); ctx.translate(x, y); ctx.rotate(a); ctx.scale(1, abs(math.cos(a * 1.3)) + 0.2)
        ctx.rectangle(-9, -5, 18, 10); ctx.set_source_rgb(*c); ctx.fill(); ctx.restore()


# ---------- CIDADE À NOITE VISTA DO ALTO
def fundo_cidade_noite_alto(ctx, S):
    hz = 520
    g = cairo.LinearGradient(0, 0, 0, hz)
    g.add_color_stop_rgb(0, *hexc("#0B0A24")); g.add_color_stop_rgb(1, *hexc("#3B2A6B"))
    ctx.rectangle(0, 0, W, hz); ctx.set_source(g); ctx.fill()
    _estrelas(ctx, S, 0, 0, W, hz - 120, 45, seed=1)
    forma(ctx, pts_elipse(860, 180, 46, 46, 16), hexc("#FFF1B8"), sombra=False, lw=4, seed=S.seed + 800)
    g = cairo.LinearGradient(0, hz, 0, H)
    g.add_color_stop_rgb(0, *hexc("#1A1840")); g.add_color_stop_rgb(1, *hexc("#0E0D26"))
    ctx.rectangle(0, hz, W, H - hz); ctx.set_source(g); ctx.fill()
    _halo(ctx, 540, hz + 40, 900, 0.18)
    # ruas em perspectiva (linhas de luz) e carrinhos andando nelas
    vx, vy = 540, hz - 300

    def P(u, v):   # u em [-1,1] lateral, v em [0,1] profundidade (0 = horizonte)
        y = hz + (H - hz) * v ** 1.6
        return vx + u * (200 + 1500 * v ** 1.6), y
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(-6, 7):
        a, b = P(i / 6, 0.02), P(i / 6, 1.0)
        ctx.move_to(*a); ctx.line_to(*b)
    for j in range(1, 14):
        v = j / 13
        a, b = P(-1.2, v), P(1.2, v)
        ctx.move_to(*a); ctx.line_to(*b)
    ctx.set_source_rgba(1.0, 0.75, 0.35, 0.55); ctx.set_line_width(4); ctx.stroke()
    r = random.Random(S.seed + 9)
    # prédios (topos) com janelas que acendem e apagam
    for k in range(70):
        u, v = r.uniform(-1.1, 1.1), r.uniform(0.05, 1.0)
        x, y = P(u, v)
        s = 0.25 + v ** 1.6 * 1.6
        bw, bh = r.uniform(40, 80) * s, r.uniform(60, 180) * s
        ctx.rectangle(x - bw / 2, y - bh, bw, bh); ctx.set_source_rgb(*mix(hexc("#2B2766"), hexc("#141233"), r.random())); ctx.fill()
        for j in range(4):
            on = (int(S.tv * 1.3 + k * 0.37 + j * 0.71) * 7 + k + j) % 5 > 1
            if on:
                ctx.rectangle(x - bw / 2 + bw * (0.15 + 0.4 * (j % 2)), y - bh + bh * (0.15 + 0.4 * (j // 2)), bw * 0.25, bh * 0.2)
        ctx.set_source_rgb(*hexc("#FFD36A")); ctx.fill()
    ctx.set_source_rgb(1, 1, 0.85)
    for k in range(22):   # faróis andando pelas ruas
        lado = k % 2
        if lado:
            i = r.randint(-6, 6); v = (r.random() + S.tv * r.uniform(0.03, 0.08)) % 1
            x, y = P(i / 6 + 0.015, v)
        else:
            j = r.randint(1, 13); u = ((r.random() + S.tv * r.uniform(0.05, 0.12)) % 2.4) - 1.2
            x, y = P(u, j / 13)
        ctx.new_sub_path(); ctx.arc(x, y, 3 + 5 * (y - hz) / (H - hz), 0, 2 * math.pi)
    ctx.fill()


# ---------- TERRA VISTA DO ESPAÇO À NOITE
_CIDADES = None


def fundo_espaco_terra(ctx, S):
    global _CIDADES
    ctx.set_source_rgb(*hexc("#05051A")); ctx.paint()
    _estrelas(ctx, S, 0, 0, W, H, 120, seed=2)
    cx, cy, R = 540, 1640, 1000
    # brilho da atmosfera
    g = cairo.RadialGradient(cx, cy, R * 0.96, cx, cy, R * 1.12)
    g.add_color_stop_rgba(0, 0.3, 0.6, 1.0, 0.7); g.add_color_stop_rgba(1, 0.3, 0.6, 1.0, 0)
    ctx.set_source(g); ctx.arc(cx, cy, R * 1.12, 0, 2 * math.pi); ctx.fill()
    forma(ctx, pts_elipse(cx, cy, R, R, 60), hexc("#0E1E4A"), sombra=False, lw=6, seed=S.seed + 900, amp=0.5)
    ctx.save(); ctx.arc(cx, cy, R - 3, 0, 2 * math.pi); ctx.clip()
    rot = S.tv * 0.04
    if _CIDADES is None:
        r = random.Random(42); pts = []
        for c in range(44):
            lon0, lat0 = r.uniform(-math.pi, math.pi), r.uniform(-0.1, 1.0)
            for k in range(r.randint(14, 40)):
                pts.append((lon0 + r.gauss(0, 0.10), lat0 + r.gauss(0, 0.06), r.random()))
        _CIDADES = pts
    vis = []
    for lon, lat, ph in _CIDADES:
        l = lon + rot
        if math.cos(l) <= 0.05:
            continue
        vis.append((cx + R * math.cos(lat) * math.sin(l), cy - R * math.sin(lat), ph, math.cos(l)))
    ctx.set_source_rgb(*hexc("#FFE08A"))
    for x, y, ph, c in vis:   # cada ponto pisca no seu ritmo, alguns acendem e apagam
        a = 0.6 + 0.4 * math.sin(S.tv * 3 + ph * 20)
        if (int(S.tv * 0.8 + ph * 13) % 9) == 0:
            continue
        ctx.new_sub_path(); ctx.arc(x, y, (3 + 3 * a) * (0.4 + 0.6 * c), 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    _halo(ctx, cx, cy - R + 200, 700, 0.10)
    # satélite passando
    u = (S.tv % 9) / 9
    sx, sy = -150 + u * (W + 300), 520 - u * 160
    ctx.save(); ctx.translate(sx, sy); ctx.rotate(-0.25 + S.tv * 0.2)
    for lado in (-1, 1):
        forma(ctx, pts_ret(lado * 70 - 40, -18, 80, 36, 2), hexc("#2D58D6"), sombra=False, lw=3, seed=S.seed + 910 + lado)
    forma(ctx, pts_ret(-28, -26, 56, 52, 6), CINZA, sombra=False, lw=4, seed=S.seed + 913)
    ctx.restore()
    if int(S.tv * 2) % 2 == 0:
        _halo(ctx, sx, sy, 40, 0.7)


# ---------- HOSPITAL
def fundo_hospital(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*mix(bg, BRANCO, 0.55)); ctx.paint()
    _ret(ctx, 0, 980, W, H, mix(bg, BRANCO, 0.35))
    _chao_xadrez(ctx, S, 1420)
    _janela(ctx, S, 90, 250, 300, 360, cortina=False, persiana=True)
    traco(ctx, [(430, 190), (1060, 190)], lw=8, seed=S.seed + 1000)       # trilho da cortina
    for k in range(6):
        x = 450 + k * 34 + math.sin(S.tv * 1.2 + k) * 3
        ctx.arc(x, 190, 9, 0, 2 * math.pi); ctx.set_source_rgb(*INK); ctx.fill()
    # monitor cardíaco com o traçado correndo
    forma(ctx, pts_ret(700, 330, 300, 210, 18), hexc("#2B2440"), seed=S.seed + 1001)
    traco(ctx, [(850, 540), (850, 1420)], lw=12, seed=S.seed + 1002)

    def ecg(ctx):
        forma(ctx, pts_ret(718, 348, 264, 150, 10), hexc("#0B1E1A"), sombra=False, lw=4, seed=S.seed + 1003)
        pts = []
        for i in range(60):
            x = 726 + i * 4.3
            u = (i / 60 * 2 - S.tv * 1.1) % 1
            y = 440 - (70 if 0.48 < u < 0.52 else (-24 if 0.52 <= u < 0.55 else 0)) + (8 * math.sin(u * 30) if 0.3 < u < 0.4 else 0)
            pts.append((x, y))
        traco(ctx, pts, lw=5, cor=hexc("#3DDC5A"), amp=0)
        on = (S.tv * 1.1) % 1 < 0.15
        ctx.arc(960, 520, 8, 0, 2 * math.pi); ctx.set_source_rgb(*(VERMELHO if on else escurece(VERMELHO, 0.5))); ctx.fill()
        texto(ctx, "72", 940, 380, 34, cor=hexc("#3DDC5A"), lw=2, sombra=False)
    S.apos.append(ecg)
    # soro pingando
    traco(ctx, [(560, 300), (560, 1420)], lw=8, seed=S.seed + 1004)
    traco(ctx, [(520, 300), (600, 300)], lw=8, seed=S.seed + 1005)
    forma(ctx, pts_ret(525, 310, 70, 120, 20), clareia(hexc("#BFE6FF"), 0.3), seed=S.seed + 1006)
    traco(ctx, [(560, 430), (560, 470)], lw=6, seed=S.seed + 1007)
    u = (S.tv * 1.5) % 1
    ctx.arc(560, 478 + u * 30, 5, 0, 2 * math.pi); ctx.set_source_rgb(*hexc("#38B6FF")); ctx.fill()
    traco(ctx, [(560, 520), (520, 700), (480, 950)], lw=4, alpha=0.7, seed=S.seed + 1008)
    # cama hospitalar
    forma(ctx, pts_ret(40, 880, 80, 300, 20), CINZA, seed=S.seed + 1009)
    forma(ctx, pts_ret(60, 960, 330, 120, 50), BRANCO, seed=S.seed + 1010)
    _leito(ctx, S, lambda c: c)


def _leito(ctx, S, tc):
    forma(ctx, pts_ret(30, 1080, 700, 220, 40), tc(clareia(S.pal[3], 0.45)), seed=S.seed + 1011, sombreado=0.05)
    forma(ctx, pts_ret(30, 1080, 700, 50, 24), tc(BRANCO), sombra=False, seed=S.seed + 1012)
    traco(ctx, [(60, 1300), (60, 1420)], lw=10, cor=tc(CINZA), seed=S.seed + 1013)
    traco(ctx, [(700, 1300), (700, 1420)], lw=10, cor=tc(CINZA), seed=S.seed + 1014)
    for x in (60, 700):
        forma(ctx, pts_elipse(x, 1430, 18, 18, 10), tc(INK), sombra=False, lw=0, seed=S.seed + 1015 + x)


def frente_hospital(ctx, S):
    if "leito" in S.ocup:
        _leito(ctx, S, S.tc)


# ---------- ACADEMIA
def fundo_academia(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _ret(ctx, 0, 1380, W, H, hexc("#2B2440"))
    for k in range(8):
        traco(ctx, [(k * 160, 1380), (k * 160 - 120, H)], lw=4, alpha=0.3, seed=S.seed + 1100 + k)
    # espelho
    forma(ctx, pts_ret(60, 240, 560, 520, 10), CINZA, seed=S.seed + 1101)
    forma(ctx, pts_ret(76, 256, 528, 488, 6), clareia(VIDRO_CLARO, 0.2), sombra=False, lw=4, seed=S.seed + 1102)
    for k in range(2):
        ctx.move_to(160 + k * 160, 256); ctx.line_to(260 + k * 160, 256); ctx.line_to(140 + k * 160, 744); ctx.line_to(40 + k * 160 + 36, 744)
        ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.35); ctx.fill()
    # cartaz
    forma(ctx, pts_ret(700, 250, 300, 190, 10), a1, seed=S.seed + 1103)
    texto(ctx, S.opts.get("cartaz", "FOCO!"), 850, 345, 70, cor=BRANCO, max_w=260)
    # suporte de halteres
    forma(ctx, pts_ret(650, 820, 380, 24, 6), CINZA, seed=S.seed + 1104)
    forma(ctx, pts_ret(650, 960, 380, 24, 6), CINZA, seed=S.seed + 1105)
    for row, y in enumerate((800, 940)):
        for k in range(4):
            x = 690 + k * 90
            traco(ctx, [(x - 26, y), (x + 26, y)], lw=10, seed=S.seed + 1106 + k + row * 5)
            for sx in (-1, 1):
                forma(ctx, pts_ret(x + sx * 30 - 11, y - 22 - k * 3, 22, 44 + k * 6, 6), [a2, a3, INK, a1][k], sombra=False, lw=3,
                      seed=S.seed + 1112 + k + sx + row * 10)
    traco(ctx, [(670, 844), (670, 1380)], lw=10, seed=S.seed + 1120); traco(ctx, [(1010, 844), (1010, 1380)], lw=10, seed=S.seed + 1121)
    _ventilador(ctx, S, 540, 110, 0.9)
    _relogio(ctx, S, 950, 600, 50)
    # esteira (base atrás, console na frente)
    forma(ctx, [(120, 1360), (560, 1360), (600, 1430), (80, 1430)], hexc("#2B2440"), seed=S.seed + 1122)
    rol = (S.tv * 260) % 60 if S.vida else 0
    ctx.save(); ctx.rectangle(110, 1360, 470, 60); ctx.clip()
    for k in range(10):
        x = 100 + k * 60 + rol
        ctx.move_to(x, 1366); ctx.line_to(x - 10, 1424)
    ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(5); ctx.stroke(); ctx.restore()


def frente_academia(ctx, S):
    tc = S.tc
    if "esteira" in S.ocup:
        for x in (130, 550):
            traco(ctx, [(x, 1400), (x + (20 if x < 300 else -20), 1080)], lw=16, cor=tc(CINZA), seed=S.seed + 1130 + x)
        forma(ctx, pts_ret(110, 1040, 460, 90, 20), tc(hexc("#2B2440")), seed=S.seed + 1132)
        forma(ctx, pts_ret(250, 1056, 180, 50, 8), hexc("#38D1C6"), sombra=False, lw=3, seed=S.seed + 1133)
        km = 3.2 + (S.tv * 0.05 if S.vida else 0)
        texto(ctx, f"{km:.1f} km", 340, 1081, 30, cor=INK, contorno=None, sombra=False)
    else:
        forma(ctx, pts_ret(110, 1290, 460, 70, 20), tc(hexc("#2B2440")), seed=S.seed + 1132)


# ---------- RESTAURANTE
def fundo_restaurante(ctx, S):
    bg, bg2, a1, a2, a3 = S.pal
    ctx.set_source_rgb(*bg); ctx.paint()
    _ret(ctx, 0, 900, W, H, escurece(bg, 0.25))
    for k in range(0, W, 60):
        ctx.rectangle(k, 900, 30, 520)
    ctx.set_source_rgba(*escurece(bg, 0.35), 0.6); ctx.fill()
    _chao_tacos(ctx, S, 1420, MADEIRA_ESC)
    # cardápio na lousa
    forma(ctx, pts_ret(620, 250, 380, 440, 10), MADEIRA, seed=S.seed + 1200)
    forma(ctx, pts_ret(640, 270, 340, 400, 6), hexc("#2B2B2B"), sombra=False, lw=4, seed=S.seed + 1201)
    texto(ctx, S.opts.get("cardapio", "MENU"), 810, 330, 56, cor=AMARELO, lw=3, sombra=False)
    for k in range(4):
        traco(ctx, [(670, 410 + k * 62), (850, 410 + k * 62)], lw=5, cor=(1, 1, 1), alpha=0.7, seed=S.seed + 1202 + k)
        traco(ctx, [(900, 410 + k * 62), (950, 410 + k * 62)], lw=5, cor=AMARELO, alpha=0.8, seed=S.seed + 1206 + k)
    _quadro(ctx, S, 100, 330, 220, 170)
    _planta(ctx, S, 520, 900, 0.8)
    # luminárias pendentes balançando
    for k, x in enumerate((220, 540, 860)):
        a = math.sin(S.tv * 1.1 + k) * 0.05 if S.vida else 0
        ex, ey = x + math.sin(a) * 160, 160
        traco(ctx, [(x, -10), (ex, ey - 10)], lw=5, amp=0)
        cup = [(ex - 70, ey + 50), (ex + 70, ey + 50), (ex + 30, ey - 10), (ex - 30, ey - 10)]
        forma(ctx, cup, a1, seed=S.seed + 1210 + k)
        S.apos.append(lambda c, ex=ex, ey=ey, cup=cup: (_halo(c, ex, ey + 80, 380, 0.32 if S.luz == "noite" else 0.12),
                                                         forma(c, cup, hexc("#FFE6A0"), sombra=False, seed=S.seed + 1210) if S.luz == "noite" else None))
    # garçom passando ao fundo (silhueta)
    _silhuetas(ctx, S, 0, W, 900, s=0.55, n=1, vel=70, cor=escurece(bg, 0.45))


def frente_restaurante(ctx, S):
    tc = S.tc
    forma(ctx, pts_ret(120, 1130, 840, 50, 12), tc(BRANCO), seed=S.seed + 1220)
    ctx.save(); ctx.rectangle(130, 1175, 820, 200); ctx.clip()
    _ret(ctx, 130, 1175, 820, 200, tc(BRANCO))
    for i in range(0, 820, 50):
        ctx.rectangle(130 + i, 1175, 25, 200)
    for j in range(0, 200, 50):
        ctx.rectangle(130, 1175 + j, 820, 25)
    ctx.set_source_rgba(*tc(VERMELHO), 0.55); ctx.fill(); ctx.restore()
    ctx.rectangle(130, 1175, 820, 200); ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
    for k, x in enumerate((340, 740)):
        forma(ctx, pts_elipse(x, 1125, 110, 26, 18), tc(BRANCO), sombra=False, lw=4, seed=S.seed + 1221 + k)
        forma(ctx, pts_elipse(x, 1112, 70, 22, 14), tc([hexc("#E8A33C"), hexc("#3DAA3A")][k]), sombra=False, lw=4, seed=S.seed + 1223 + k)
        _vapor(ctx, S, x, 1080, 0.8)
    forma(ctx, pts_ret(520, 1020, 40, 110, 10), tc(VERDE), seed=S.seed + 1225)        # garrafa
    forma(ctx, pts_ret(590, 1060, 34, 70, 6), tc(clareia(S.pal[2], 0.4)), sombra=False, lw=4, seed=S.seed + 1226)


# ============================ registro ============================
CENARIOS = {
    "sala": dict(fundo=fundo_sala, frente=frente_sala, ancoras={
        "sofa_assento": {"x": 430, "assento": SOFA["assento"], "escala": 0.85},
        "sofa_esq": {"x": 290, "assento": SOFA["assento"], "escala": 0.85},
        "sofa_dir": {"x": 570, "assento": SOFA["assento"], "escala": 0.85},
        "porta": {"x": PORTA_SALA[0], "y": PORTA_SALA[1], "chao": 1400, "escala": 0.9},
        "janela": {"x": 390, "y": 450}, "quadro": {"x": 675, "y": 370}, "relogio": {"x": 925, "y": 470},
        "chao": {"x": 540, "chao": 1460, "escala": 0.9}}),
    "escritorio": dict(fundo=fundo_escritorio, frente=frente_escritorio, ancoras={
        "cadeira": {"x": 390, "assento": 1070, "escala": 0.8},
        "em_pe": {"x": 640, "chao": 1290, "escala": 0.8},
        "mesa": {"x": 520, "y": 960}, "monitor": {"x": 810, "y": 875}, "janela": {"x": 270, "y": 420},
        "quadro": {"x": 670, "y": 350}, "relogio": {"x": 940, "y": 300}}),
    "quarto": dict(fundo=fundo_quarto, frente=frente_quarto, ancoras={
        "cama": {"x": 400, "assento": 1150, "escala": 0.85},
        "em_pe": {"x": 540, "chao": 1470, "escala": 0.9},
        "janela": {"x": 800, "y": 430}, "abajur": {"x": 870, "y": 900}, "poster": {"x": 230, "y": 480}}),
    "cozinha": dict(fundo=fundo_cozinha, frente=frente_cozinha, ancoras={
        "balcao": {"x": 620, "chao": 1390, "escala": 0.85},
        "geladeira": {"x": 200, "chao": 1460, "escala": 0.85},
        "fogao": {"x": 930, "y": 960}, "pia": {"x": 600, "y": 1050}, "janela": {"x": 695, "y": 390},
        "relogio": {"x": 960, "y": 600}}),
    "rua": dict(fundo=fundo_rua, frente=frente_rua, ancoras={
        "calcada": {"x": 540, "chao": CALCADA + 10, "escala": 0.85},
        "calcada_esq": {"x": 300, "chao": CALCADA + 10, "escala": 0.85},
        "calcada_dir": {"x": 760, "chao": CALCADA + 10, "escala": 0.85},
        "loja": {"x": 620, "chao": CALCADA - 10, "escala": 0.7},
        "semaforo": {"x": 960, "y": 650}, "poste": {"x": 210, "y": 520}, "ceu": {"x": 540, "y": 230}}),
    "onibus": dict(fundo=fundo_onibus, frente=frente_onibus, ancoras={
        "banco": {"x": 310, "assento": 1210, "escala": 0.85},
        "banco_dir": {"x": 800, "assento": 1210, "escala": 0.85},
        "em_pe": {"x": 560, "chao": 1560, "escala": 0.9},
        "janela": {"x": 540, "y": 520}, "pare": {"x": 540, "y": 865}}),
    "escola": dict(fundo=fundo_escola, frente=frente_escola, ancoras={
        "carteira": {"x": 540, "assento": 1260, "escala": 0.85},
        "professor": {"x": 820, "chao": 1480, "escala": 0.9},
        "lousa": {"x": 470, "y": 470}, "relogio": {"x": 970, "y": 320}}),
    "carro": dict(fundo=fundo_carro, frente=frente_carro, ancoras={
        "motorista": {"x": 320, "assento": 1220, "escala": 0.95},
        "carona": {"x": 760, "assento": 1220, "escala": 0.95},
        "para_brisa": {"x": 540, "y": 500}, "retrovisor": {"x": 540, "y": 230}, "radio": {"x": 540, "y": 1260}}),
}
CENARIOS.update({
    "casa_natal_fora": dict(fundo=fundo_casa_natal_fora, frente=frente_casa_natal_fora, luz="noite", ancoras={
        "quintal": {"x": 540, "chao": 1560, "escala": 0.9}, "quintal_esq": {"x": 200, "chao": 1560, "escala": 0.9},
        "quintal_dir": {"x": 860, "chao": 1560, "escala": 0.9},
        "porta": {"x": 430, "y": 1040, "chao": 1320, "escala": 0.7}, "janela": {"x": 255, "y": 890},
        "vizinho": {"x": 980, "y": 800}, "ceu": {"x": 540, "y": 220}}),
    "sala_natal": dict(fundo=fundo_sala_natal, frente=frente_sala_natal, ancoras={
        "mesa": {"x": 820, "chao": 1330, "escala": 0.85}, "arvore": {"x": 230, "y": 900},
        "presentes": {"x": 230, "y": 1380}, "ceia": {"x": 780, "y": 1040}, "centro": {"x": 540, "chao": 1480, "escala": 0.9},
        "janela": {"x": 600, "y": 440}}),
    "loja": dict(fundo=fundo_loja, frente=frente_loja, ancoras={
        "caixa": {"x": 800, "chao": 1400, "escala": 0.85}, "centro": {"x": 420, "chao": 1500, "escala": 0.9},
        "vitrine": {"x": 540, "y": 490}, "placa": {"x": 270, "y": 250}, "placa2": {"x": 810, "y": 250}}),
    "supermercado": dict(fundo=fundo_supermercado, frente=frente_supermercado, ancoras={
        "carrinho": {"x": 700, "chao": 1460, "escala": 0.85}, "corredor": {"x": 380, "chao": 1500, "escala": 0.85},
        "placa": {"x": 540, "y": 345}, "fundo": {"x": 540, "y": 680}}),
    "praia": dict(fundo=fundo_praia, frente=frente_praia, ancoras={
        "areia": {"x": 540, "chao": 1500, "escala": 0.9}, "areia_dir": {"x": 800, "chao": 1500, "escala": 0.9},
        "cadeira": {"x": 760, "assento": 1270, "escala": 0.85}, "guarda_sol": {"x": 300, "chao": 1480, "escala": 0.85},
        "mar": {"x": 540, "y": 960}, "ceu": {"x": 540, "y": 400}}),
    "festa": dict(fundo=fundo_festa, frente=frente_festa, luz="noite", ancoras={
        "centro": {"x": 450, "chao": 1500, "escala": 0.9}, "esq": {"x": 280, "chao": 1500, "escala": 0.9},
        "bolo": {"x": 870, "y": 1000}, "globo": {"x": 540, "y": 115}}),
    "cidade_noite_alto": dict(fundo=fundo_cidade_noite_alto, ancoras={
        "ceu": {"x": 540, "y": 260}, "cidade": {"x": 540, "y": 900}, "lua": {"x": 860, "y": 180}}),
    "espaco_terra": dict(fundo=fundo_espaco_terra, ancoras={
        "espaco": {"x": 540, "y": 330}, "terra": {"x": 540, "y": 900}, "satelite": {"x": 540, "y": 440},
        "flutuando": {"x": 540, "y": 520, "escala": 0.8}}),
    "hospital": dict(fundo=fundo_hospital, frente=frente_hospital, ancoras={
        "leito": {"x": 360, "assento": 1110, "escala": 0.85}, "medico": {"x": 840, "chao": 1500, "escala": 0.9},
        "monitor": {"x": 850, "y": 435}, "janela": {"x": 240, "y": 430}}),
    "academia": dict(fundo=fundo_academia, frente=frente_academia, ancoras={
        "esteira": {"x": 340, "chao": 1370, "escala": 0.85}, "halteres": {"x": 840, "chao": 1480, "escala": 0.9},
        "espelho": {"x": 340, "y": 500}, "cartaz": {"x": 850, "y": 345}}),
    "restaurante": dict(fundo=fundo_restaurante, frente=frente_restaurante, ancoras={
        "mesa": {"x": 340, "assento": 1190, "escala": 0.85}, "mesa_dir": {"x": 740, "assento": 1190, "escala": 0.85},
        "garcom": {"x": 930, "chao": 1480, "escala": 0.9}, "cardapio": {"x": 810, "y": 470}}),
})
ASSENTOS = {nome: {a for a, d in c["ancoras"].items() if "assento" in d} for nome, c in CENARIOS.items()}


def tem(nome):
    return nome in CENARIOS


def fundo(ctx, nome, pal, t, opts, seed=1):
    S = Estado(nome, pal, t, opts, seed)
    ctx.save()
    CENARIOS[nome]["fundo"](ctx, S)
    _tinta(ctx, S.T)
    for f in S.apos:
        f(ctx)
    if S.luz == "tarde":   # raio de sol entrando
        ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD)
        ctx.move_to(120, 200); ctx.line_to(560, 200); ctx.line_to(1100, 1500); ctx.line_to(500, 1500); ctx.close_path()
        ctx.set_source_rgba(1.0, 0.6, 0.25, 0.10); ctx.fill(); ctx.restore()
    ctx.restore()


HALOS = {"festa": [(540, 115)], "restaurante": [(220, 240), (540, 240), (860, 240)], "sala_natal": [(230, 900)],
         "sala": [(75, 700)], "quarto": [(870, 870)], "escritorio": [(720, 200), (150, 840)], "rua": [(215, 560)],
         "onibus": [(540, 90)], "escola": [(290, 90), (790, 90)]}


def cenario_frente(ctx, nome, pal, t, opts, seed=1):
    """Passo depois dos personagens: luz fraca neles, a camada da frente com a luz do cenário e o brilho das lâmpadas."""
    if nome not in CENARIOS:
        return
    S = Estado(nome, pal, t, opts, seed)
    if S.T:
        _tinta(ctx, S.T, 0.32)        # personagens pegam um pouco da luz (sem perder o contraste)
    if opts.get("frente", True) is not False and CENARIOS[nome].get("frente"):
        ctx.save()
        CENARIOS[nome]["frente"](ctx, S)
        ctx.restore()
    if S.luz == "noite":
        for x, y in HALOS.get(nome, []):
            _halo(ctx, x, y, 520, 0.16)
    elif S.luz == "tarde":
        ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD); ctx.set_source_rgba(0.35, 0.16, 0.0, 0.10); ctx.paint(); ctx.restore()


# ============================ âncoras ============================
def ancoras(nome):
    return CENARIOS.get(nome, {}).get("ancoras", {})


def posiciona(nome_cenario, el):
    """Resolve el["ancora"] em (x, y) normalizados e na escala sugerida (só personagens sem escala).
    Assento: o quadril fica no assento. Chão: os pés no chão. Outros: o centro no ponto."""
    nome = el["ancora"]
    anc = ancoras(nome_cenario)
    if nome not in anc:
        disp = ", ".join(anc) or "nenhuma (use cozinha, sala, escritorio, quarto, rua, onibus, escola ou carro)"
        raise SystemExit(f"âncora '{nome}' não existe no cenário '{nome_cenario}'. Âncoras: {disp}")
    a = anc[nome]
    tipo = el.get("tipo")
    pers = tipo in ("humano", "pipo")
    s = el.get("escala", a.get("escala", 1.0) if pers else 1.0)
    x = a["x"]
    if pers and "assento" in a:
        y = a["assento"] - (140 if tipo == "humano" else 235) * s
    elif pers and "chao" in a:
        y = a["chao"] - (335 if tipo == "humano" else 285) * s
    else:
        y = a.get("y", a.get("chao", a.get("assento", H / 2)))
    if pers:   # rosto nunca na faixa da legenda (y 0,60): sobe o personagem se precisar
        y = min(y, 0.595 * H + (150 if tipo == "humano" else 50) * s)
    return x / W + el.get("dx", 0), y / H + el.get("dy", 0), (s if pers and "escala" not in el else None)


# ============================ elemento porta ============================
def desenha_porta(ctx, st, t, pal, seed):
    """Porta que abre: abre 0 (fechada) a 1 (aberta). largura, altura, cor (folha), dentro (cor da luz do outro lado)."""
    w = st.get("largura", DW); h = st.get("altura", DH)
    cor = hexc(st["cor"]) if st.get("cor") else MADEIRA
    dentro = hexc(st["dentro"]) if st.get("dentro") else hexc("#FFE7B0")
    _porta_desenho(ctx, 0, 0, w, h, float(st.get("abre", 0)), cor, dentro, seed)
    return {"corpo": (-w / 2, -h / 2, w / 2, h / 2)}
