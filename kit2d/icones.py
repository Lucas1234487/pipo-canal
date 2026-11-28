"""Ícones soltos do PipoPop 2D ("tipo": "icone", ep015): qual = curtir | churrasqueira | macaco | arvore | lupa.
curtir: joinha pulsando (anime com `escala`). churrasqueira: grelha com brasa, chamas, espeto de carne e fumaça (sem marca).
macaco: silhueta de macaco num galho (gancho da parte 3). arvore: Y de parentesco (nó de baixo em 0,0 e braços para cima, `rotulo` no nó)."""
import math
import cairo
from estilo import INK, LW, BRANCO, hexc, escurece, clareia, forma, traco, texto, pts_elipse


def _F(ctx, pts, cor, seed, **k):
    forma(ctx, pts, cor, seed=seed, **k)


def _curtir(ctx, st, t, pal, seed):
    cor = hexc(st.get("cor", "#FFC21A"))
    pul = 1 + 0.08 * math.sin(t * 7)
    ctx.save(); ctx.scale(pul, pul)
    _F(ctx, [(-120, -10), (-60, -10), (-60, 110), (-120, 110)], hexc("#2A7DE1"), seed + 1, lw=6, amp=0.6)   # punho da manga
    forma(ctx, [(-50, -4), (10, -70), (30, -150), (70, -150), (84, -100), (70, -36), (150, -36), (166, 10), (150, 100), (130, 114), (-50, 114)], cor, seed=seed + 2, lw=6, amp=0.8, sombreado=0.1)
    for k in range(3):
        traco(ctx, [(60, 20 + k * 30), (140, 20 + k * 30)], lw=5, cor=escurece(cor, 0.35), seed=seed + 5 + k, amp=0.4, alpha=0.8)
    ctx.restore()
    return {"corpo": (-130, -160, 175, 120), "texto": None}


def _churrasqueira(ctx, st, t, pal, seed):
    # chamas atrás/abaixo da grelha
    for i in range(7):
        x = -190 + i * 63
        h = 70 + 34 * math.sin(t * 9 + i * 1.7) + 14 * math.sin(t * 17 + i)
        ctx.move_to(x - 26, 0); ctx.curve_to(x - 22, -h * 0.5, x + 6, -h * 0.55, x, -h)
        ctx.curve_to(x + 20, -h * 0.5, x + 34, -h * 0.3, x + 26, 0); ctx.close_path()
        ctx.set_source_rgb(*hexc("#FF8A1F")); ctx.fill_preserve(); ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.stroke()
        ctx.move_to(x - 10, 0); ctx.curve_to(x - 8, -h * 0.3, x + 2, -h * 0.35, x, -h * 0.55)
        ctx.curve_to(x + 12, -h * 0.3, x + 14, -h * 0.15, x + 10, 0); ctx.close_path(); ctx.set_source_rgb(*hexc("#FFD21F")); ctx.fill()
    # espeto com carne
    ctx.save(); ctx.translate(0, -112); ctx.rotate(-0.05)
    traco(ctx, [(-260, 0), (260, 0)], lw=9, cor=hexc("#C9CED8"), seed=seed + 1, amp=0.4)
    for k, x in enumerate((-120, -30, 60, 150)):
        forma(ctx, pts_elipse(x, 0, 42, 38, 14), hexc("#B5382A") if k % 2 == 0 else hexc("#D9574B"), seed=seed + 4 + k, lw=5, amp=1.0, sombra=False)
        traco(ctx, [(x - 22, -10), (x + 20, 8)], lw=6, cor=hexc("#F6D6B8"), seed=seed + 9 + k, amp=0.4, alpha=0.8)
    ctx.restore()
    # corpo da churrasqueira
    forma(ctx, [(-250, 0), (250, 0), (206, 150), (-206, 150)], hexc("#3A3440"), seed=seed + 20, lw=6, amp=0.8, sombreado=0.1)
    for k in range(5):
        traco(ctx, [(-200 + k * 6, 30 + k * 24), (200 - k * 6, 30 + k * 24)], lw=7, cor=hexc("#5A5360"), seed=seed + 21 + k, amp=0.4)
    # fumaça
    for i in range(4):
        u = (t * 0.4 + i / 4) % 1.0
        ctx.arc(-120 + i * 80 + 20 * math.sin(u * 6 + i), -160 - u * 220, 22 + u * 30, 0, 2 * math.pi)
        ctx.set_source_rgba(0.85, 0.85, 0.88, 0.6 * (1 - u)); ctx.fill()
    return {"corpo": (-260, -420, 260, 150), "texto": None}


def _macaco(ctx, st, t, pal, seed):
    esc = hexc("#1B1330")
    bal = math.sin(t * 1.6) * 0.04
    traco(ctx, [(-260, -60), (-100, -48), (80, -70), (260, -40)], lw=34, cor=hexc("#6B4A32"), seed=seed + 1, amp=0.6)
    for k, (x, y) in enumerate(((-200, -100), (150, -120), (230, -80))):
        _F(ctx, pts_elipse(x, y, 60, 26, 14), hexc("#35A24A"), seed + 2 + k, lw=4, sombra=False, amp=0.8)
    ctx.save(); ctx.translate(0, -50); ctx.rotate(bal)
    traco(ctx, [(60, 40), (130, 90), (150, 20), (110, -20)], lw=18, cor=esc, seed=seed + 10, amp=0.4)   # rabo
    forma(ctx, pts_elipse(0, -20, 62, 80, 18), esc, seed=seed + 11, lw=5, amp=0.8, sombra=False)           # corpo
    for sg in (-1, 1):
        traco(ctx, [(sg * 50, -50), (sg * 96, -20), (sg * 120, -90)], lw=20, cor=esc, seed=seed + 12 + sg, amp=0.4)
    forma(ctx, pts_elipse(0, -130, 50, 48, 16), esc, seed=seed + 14, lw=5, amp=0.8, sombra=False)
    for sg in (-1, 1):
        forma(ctx, pts_elipse(sg * 56, -130, 20, 22, 10), esc, seed=seed + 15 + sg, lw=5, amp=0.6, sombra=False)
    forma(ctx, pts_elipse(0, -118, 32, 30, 14), hexc("#3A2D55"), seed=seed + 18, lw=0, amp=0.4, sombra=False)
    for sg in (-1, 1):
        ctx.arc(sg * 16, -138, 6, 0, 2 * math.pi); ctx.set_source_rgb(1, 0.85, 0.2); ctx.fill()
    ctx.restore()
    return {"corpo": (-270, -260, 270, 60), "texto": None}


def _arvore(ctx, st, t, pal, seed):
    cor = hexc(st.get("cor", "#FFF8EC"))
    dx, dy = st.get("dx", 200), st.get("dy", 230)
    for sg in (-1, 1):
        traco(ctx, [(0, 0), (sg * dx * 0.2, -dy * 0.35), (sg * dx, -dy)], lw=18, cor=INK, seed=seed + 1 + sg, amp=0.5)
        traco(ctx, [(0, 0), (sg * dx * 0.2, -dy * 0.35), (sg * dx, -dy)], lw=9, cor=cor, seed=seed + 3 + sg, amp=0.5)
    r = 44 + 4 * math.sin(t * 4)
    forma(ctx, pts_elipse(0, 0, r, r, 18), hexc("#FFC21A"), seed=seed + 7, lw=6, amp=0.6)
    tb = texto(ctx, st.get("rotulo", "PRIMOS"), 0, 0, 30, cor=INK, contorno=(1, 0.97, 0.9), sombra=False, max_w=r * 1.7) if st.get("rotulo") else None
    return {"corpo": (-dx - 60, -dy - 60, dx + 60, 50), "texto": tb}


def _lupa(ctx, st, t, pal, seed):
    ang = 0.1 * math.sin(t * 2.4)
    ctx.save(); ctx.rotate(ang)
    traco(ctx, [(60, 60), (140, 150)], lw=26, cor=hexc("#8A4B2A"), seed=seed + 1, amp=0)
    ctx.arc(0, 0, 100, 0, 2 * math.pi); ctx.set_source_rgba(0.75, 0.92, 1.0, 0.3); ctx.fill_preserve()
    ctx.set_source_rgb(*INK); ctx.set_line_width(20); ctx.stroke()
    ctx.arc(0, 0, 100, 0, 2 * math.pi); ctx.set_source_rgb(*hexc("#FFC21A")); ctx.set_line_width(10); ctx.stroke()
    traco(ctx, [(-52, -40), (-26, -66)], lw=11, cor=BRANCO, amp=0)
    ctx.restore()
    return {"corpo": (-120, -120, 160, 170), "texto": None}


QUAIS = {"lupa": _lupa, "curtir": _curtir, "churrasqueira": _churrasqueira, "macaco": _macaco, "arvore": _arvore}


def desenha_icone(ctx, st, t, pal, seed):
    q = st.get("qual", "curtir")
    if q not in QUAIS:
        raise SystemExit(f"icone: qual '{q}' não existe. Use: {', '.join(QUAIS)}")
    return QUAIS[q](ctx, st, t, pal, seed)
