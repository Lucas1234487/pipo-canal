"""Mapa estilizado do PipoPop 2D (elemento "mapa"): Brasil (com regiões opcionais) e mundo (continentes).
Desenhado à mão com polígonos simplificados em (longitude, latitude), projeção retangular simples.
Reconhecível, sem precisão cartográfica. Cores da paleta, contorno grosso e sombra chapada do estilo da casa."""
import math
import cairo
from estilo import INK, BRANCO, hexc, mix, escurece, clareia, forma, texto, pts_ret, clamp

# ---------------- Brasil (contorno, sentido horário a partir do Amapá)
BRASIL = [(-51.6, 4.2), (-50.0, 1.8), (-49.9, 0.0), (-48.5, -1.0), (-44.5, -2.5), (-41.5, -2.9), (-38.5, -3.7), (-35.3, -5.2),
          (-34.8, -7.1), (-35.7, -9.6), (-37.2, -11.0), (-38.5, -13.0), (-39.0, -15.5), (-39.7, -19.5), (-41.0, -22.0), (-43.2, -22.95),
          (-46.3, -24.0), (-48.5, -26.0), (-48.6, -28.5), (-50.2, -30.5), (-52.1, -32.2), (-53.4, -33.7), (-53.5, -32.5), (-55.5, -30.9),
          (-57.6, -30.2), (-55.7, -28.0), (-53.8, -27.1), (-54.6, -25.6), (-54.3, -24.0), (-55.5, -23.9), (-55.6, -22.6), (-57.9, -22.1),
          (-57.8, -20.0), (-58.2, -17.5), (-60.2, -16.3), (-60.0, -13.5), (-62.5, -13.0), (-65.0, -12.0), (-65.4, -9.8), (-68.0, -11.0),
          (-70.5, -11.0), (-70.6, -9.5), (-73.0, -9.4), (-74.0, -7.4), (-73.0, -5.0), (-70.0, -4.2), (-69.4, -1.0), (-69.9, 1.2),
          (-66.9, 1.2), (-64.0, 2.0), (-64.8, 4.0), (-62.8, 4.0), (-61.0, 5.2), (-60.0, 5.0), (-59.6, 2.0), (-58.5, 1.3),
          (-56.0, 1.9), (-54.0, 2.1), (-52.5, 2.3)]
# regiões (polígonos folgados: são recortados pelo contorno)
REGIOES = {
    "norte": [(-80, 8), (-46.0, 8), (-46.0, -1), (-45.5, -6), (-46.5, -10.5), (-46.3, -13.0), (-50.5, -13.0), (-50.5, -9.5),
              (-58, -7.5), (-61.5, -8.7), (-60.5, -13.7), (-80, -13.7)],
    "nordeste": [(-46.0, 8), (-30, 8), (-30, -18.3), (-39.7, -18.3), (-44.0, -14.8), (-46.3, -15.2), (-46.3, -13.0), (-46.5, -10.5),
                 (-45.5, -6), (-46.0, -1)],
    "centro_oeste": [(-50.5, -13.0), (-46.3, -13.0), (-46.3, -15.2), (-47.3, -16.0), (-50.5, -19.0), (-51.5, -20.5), (-53.5, -22.7),
                     (-55, -24.5), (-80, -24.5), (-80, -13.7), (-60.5, -13.7), (-61.5, -8.7), (-58, -7.5), (-50.5, -9.5)],
    "sudeste": [(-46.3, -15.2), (-44.0, -14.8), (-39.7, -18.3), (-30, -18.3), (-30, -26), (-48.0, -25.3), (-52.0, -22.6), (-53.5, -22.7),
                (-51.5, -20.5), (-50.5, -19.0), (-47.3, -16.0)],
    "sul": [(-80, -24.5), (-55, -24.5), (-53.5, -22.7), (-52.0, -22.6), (-48.0, -25.3), (-30, -26), (-30, -40), (-80, -40)],
}
CIDADES = {   # (lon, lat)
    "sao_paulo": (-46.6, -23.55), "rio": (-43.2, -22.9), "brasilia": (-47.9, -15.8), "salvador": (-38.5, -12.97),
    "manaus": (-60.0, -3.1), "belem": (-48.5, -1.45), "fortaleza": (-38.5, -3.73), "recife": (-34.9, -8.05),
    "porto_alegre": (-51.2, -30.03), "curitiba": (-49.27, -25.43), "belo_horizonte": (-43.94, -19.92), "goiania": (-49.25, -16.68),
    "florianopolis": (-48.55, -27.6), "natal": (-35.2, -5.8), "campo_grande": (-54.6, -20.45), "cuiaba": (-56.1, -15.6),
    "porto_velho": (-63.9, -8.76), "boa_vista": (-60.67, 2.82), "macapa": (-51.07, 0.03), "sao_luis": (-44.3, -2.53),
    "teresina": (-42.8, -5.09), "joao_pessoa": (-34.86, -7.12), "maceio": (-35.73, -9.65), "aracaju": (-37.07, -10.9),
    "vitoria": (-40.3, -20.3), "palmas": (-48.33, -10.2), "rio_branco": (-67.8, -9.97), "campinas": (-47.06, -22.9),
    "bauru": (-49.06, -22.31), "birigui": (-50.34, -21.29),
    # mundo
    "nova_york": (-74.0, 40.7), "los_angeles": (-118.2, 34.0), "cidade_do_mexico": (-99.1, 19.4), "buenos_aires": (-58.4, -34.6),
    "londres": (-0.1, 51.5), "paris": (2.35, 48.85), "lisboa": (-9.14, 38.7), "madri": (-3.7, 40.4), "roma": (12.5, 41.9),
    "moscou": (37.6, 55.75), "cairo": (31.2, 30.0), "lagos": (3.4, 6.5), "joanesburgo": (28.0, -26.2), "dubai": (55.3, 25.2),
    "mumbai": (72.9, 19.1), "pequim": (116.4, 39.9), "xangai": (121.5, 31.2), "toquio": (139.7, 35.7), "seul": (127.0, 37.5),
    "sydney": (151.2, -33.9), "polo_norte": (0, 80),
}
# ---------------- mundo (continentes estilizados)
MUNDO = {
    "america_norte": [(-168, 66), (-140, 70), (-95, 72), (-80, 68), (-62, 60), (-56, 52), (-66, 45), (-70, 42), (-76, 35), (-80, 31),
                      (-80.5, 25.2), (-82.5, 28), (-84, 30), (-90, 29.5), (-97, 26), (-97, 21), (-94, 18.5), (-87, 21), (-88, 16),
                      (-83, 15), (-83, 10), (-79, 9), (-77, 8), (-81, 7.5), (-85, 10), (-87, 13), (-92, 14.5), (-96, 15.8), (-105, 20),
                      (-106, 23.5), (-110, 23), (-112, 29), (-115, 30), (-117, 32.5), (-120.5, 34.5), (-124, 40), (-124.5, 48),
                      (-130, 54), (-137, 59), (-146, 60.5), (-152, 59), (-158, 57), (-165, 54.5), (-162, 58.5), (-166, 61),
                      (-165, 64.5)],
    "groenlandia": [(-55, 60), (-43, 60), (-20, 70), (-18, 77), (-30, 83), (-60, 82), (-72, 78), (-58, 75), (-52, 68)],
    "america_sul": [(-77, 8), (-72, 12), (-62, 10.5), (-52, 5), (-50, 0), (-44, -2.5), (-35, -5), (-35, -9), (-39, -15), (-41, -22),
                    (-48, -26), (-53, -33.7), (-58, -34.5), (-57, -38), (-62, -39), (-65, -42), (-65, -47), (-69, -51), (-68.5, -55),
                    (-72, -53.5), (-75, -48), (-73.5, -41), (-73, -37), (-71.5, -30), (-70.5, -18), (-75, -15.5), (-81, -6), (-80, -1),
                    (-79, 1.5), (-77.5, 4)],
    "eurasia": [(-9, 43), (-9, 37), (-5.6, 36), (-2, 36.8), (0, 38.5), (3, 42), (7.5, 43.8), (12, 42), (15.6, 38), (16.5, 39.5),
                (18.5, 40.2), (13.6, 45.7), (19, 42), (20, 39.5), (23, 36.5), (26, 40.5), (29, 41), (36, 36.5), (34.5, 31.5),
                (34.8, 28), (38, 24), (42.8, 14), (45, 12.8), (52, 16), (55, 17.5), (59.8, 22.5), (56.4, 26.4), (50.5, 30),
                (52, 27.5), (57, 25.8), (62, 25), (67, 24.8), (70, 21), (72.8, 19), (77, 8.1), (80, 10), (80.3, 15.8), (87, 21.5),
                (91.5, 22.5), (94.3, 16), (98, 16.5), (98.5, 13), (99, 10), (100.5, 7), (103.5, 1.4), (103.5, 4), (105, 8.6),
                (109, 12), (108.5, 16), (106, 20), (108, 21.5), (111, 21.5), (117, 23), (120, 26.5), (122, 30), (121, 32),
                (119, 35), (122.5, 37.5), (121.5, 40.8), (124.5, 40), (127, 38), (129.3, 35.5), (129.5, 42.5), (135, 43.5),
                (141, 48.5), (140.5, 53.5), (135.5, 54.7), (143, 59.3), (155, 59.5), (156.5, 51), (163, 56), (162, 61.5),
                (180, 66), (180, 69.5), (170, 70), (160, 69.8), (150, 71.5), (140, 72.5), (128, 72.5), (113, 74), (105, 77.5),
                (95, 76), (87, 74.5), (80, 72.5), (70, 73), (68, 68.5), (60, 69.8), (50, 68), (44, 68.5), (33, 69.5), (28, 71),
                (20, 70), (15, 68), (12, 65), (5, 62), (5.5, 58.5), (8, 58), (10.5, 59.3), (10.5, 57.7), (8, 56.5), (8.6, 53.9),
                (4.5, 52.5), (1.6, 51), (-1.5, 49.7), (-4.7, 48.4), (-1.2, 46.0), (-1.6, 43.4)],
    "gra_bretanha": [(-5.7, 50.1), (1.4, 51.2), (1.7, 52.7), (0, 53.5), (-1.7, 55.6), (-3, 58.6), (-5, 58.6), (-6.2, 56.5),
                     (-4.8, 54.8), (-3, 53.4), (-4.6, 52.8), (-5.2, 51.7)],
    "japao": [(130, 31), (132, 34), (135, 33.7), (140, 35), (141.5, 38.5), (140, 41.5), (141.5, 45.5), (145.5, 43.5), (142, 42),
              (141, 38), (139.5, 35), (135.5, 34.2), (131.5, 33.7)],
    "africa": [(-17, 21), (-17, 14.7), (-14.5, 10.5), (-8, 4.4), (-2, 4.7), (5, 6), (9.5, 4), (9.5, 1), (13, -6), (12, -13),
               (14.5, -23), (18.4, -34), (20, -34.8), (26, -34), (32.5, -28.5), (35.5, -23.5), (35, -20), (40.5, -15), (40, -10),
               (39, -5), (42, -0.5), (51.2, 11.8), (44, 10.5), (43.2, 12.5), (39.7, 15.5), (37, 21), (34.5, 27.5), (32.5, 30),
               (29, 30.8), (25, 31.8), (20, 30.8), (15.5, 32), (11, 33.2), (10.5, 37), (3, 36.9), (-2, 35.2), (-5.9, 35.8),
               (-9.6, 32), (-13, 27.5)],
    "madagascar": [(49.3, -12), (50.5, -15.5), (47.3, -25), (44, -25), (43.5, -21.5), (44.5, -16.2)],
    "australia": [(113, -22), (114, -26.5), (115, -34), (118, -35), (123, -34), (129, -31.6), (134, -32.5), (138, -35.5), (140, -38),
                  (146, -39), (150, -37.5), (153.5, -28), (153, -25), (149, -20.5), (146, -18.5), (145.3, -14.8), (142.5, -10.7),
                  (141.5, -13), (140.8, -17.5), (137, -15.8), (136.5, -12), (132, -11.3), (130, -13), (126.5, -14), (122, -17.5)],
    "sumatra": [(95.3, 5.6), (98, 4), (104, -2.5), (106, -6), (102, -4), (97, 1)],
    "borneo": [(109, 1.5), (111, -3), (116, -4), (119, 0), (119, 5), (116, 7), (113, 3.5)],
    "java": [(105.5, -6.6), (114.5, -7.8), (114.5, -8.7), (106, -7.5)],
    "nova_guine": [(131, -1), (141, -2.6), (150, -10.5), (144, -7.8), (138, -8.4), (134, -4)],
    "nova_zelandia": [(172.7, -34.5), (178.5, -37.7), (175, -41.6), (171.2, -44.5), (166.5, -46), (170.5, -42)],
}
GRUPO = {"america_norte": 0, "groenlandia": 0, "america_sul": 1, "eurasia": 2, "gra_bretanha": 2, "japao": 2, "africa": 3,
         "madagascar": 3, "australia": 4, "sumatra": 4, "borneo": 4, "java": 4, "nova_guine": 4, "nova_zelandia": 4}
CAIXA = {"brasil": (-74.5, 5.8, -34.3, -34.2), "mundo": (-170, 80, 180, -56), "america_sul": (-82, 13, -34, -56)}


def _poli_pts(pts, passo):
    """Densifica o polígono (cantos ficam vivos o bastante depois do path_suave)."""
    out = []
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        k = max(1, int(math.hypot(x1 - x0, y1 - y0) / passo))
        out += [(x0 + (x1 - x0) * j / k, y0 + (y1 - y0) * j / k) for j in range(k)]
    return out


def desenha_mapa(ctx, st, t, pal, seed):
    """qual: brasil | mundo | america_sul · largura (px) · regioes (Brasil: 5 regiões coloridas; 'estados' é sinônimo)
    destaque: lista de cidades (chave de CIDADES, {"cidade", "rotulo", "cor"}, {"lon", "lat", ...}) com ponto brilhando
    cor (terra), cor_mar (pílula de mar atrás; false = sem), titulo (texto em cima)."""
    qual = st.get("qual", "brasil")
    if qual not in CAIXA:
        raise SystemExit(f"mapa: qual '{qual}' não existe. Use: {', '.join(CAIXA)}")
    lo0, la0, lo1, la1 = CAIXA[qual]
    largura = st.get("largura", 960 if qual == "mundo" else 840)
    esc = largura / (lo1 - lo0)
    alt = (la0 - la1) * esc
    P = lambda lo, la: ((lo - (lo0 + lo1) / 2) * esc, ((la0 + la1) / 2 - la) * esc)
    bg, bg2, a1, a2, a3 = pal
    terra = hexc(st["cor"]) if st.get("cor") else (hexc("#3DAA3A") if qual != "mundo" else hexc("#3DAA3A"))
    caixas_txt = []
    mar = st.get("cor_mar", True)
    if mar:
        mc = hexc(mar) if isinstance(mar, str) else hexc("#2A7DE1")
        forma(ctx, pts_ret(-largura / 2 - 40, -alt / 2 - 40, largura + 80, alt + 80, 46), mc, seed=seed, sombreado=0.04)
        for k in range(3):   # ondinhas
            y = -alt / 2 + alt * (0.2 + 0.3 * k); x = -largura / 2 + (60 if k % 2 else largura - 160)
            ctx.move_to(x, y); ctx.curve_to(x + 25, y - 14, x + 45, y + 14, x + 70, y)
            ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(5); ctx.stroke()
    if qual in ("brasil", "america_sul"):
        if qual == "america_sul":
            pts = [P(*q) for q in _poli_pts(MUNDO["america_sul"], 1.5)]
            forma(ctx, pts, mix(terra, BRANCO, 0.35), seed=seed + 1, amp=1.0, lw=5)
        pts = [P(*q) for q in _poli_pts(BRASIL, 1.2)]
        forma(ctx, pts, terra, seed=seed + 2, amp=1.0, sombra=qual == "brasil", lw=7)
        if st.get("regioes") or st.get("estados"):
            from estilo import path_suave, jitter
            cores = [a1, a2, hexc("#9BE3B0"), clareia(terra, 0.1), hexc("#B57BFF")]   # norte, nordeste, centro-oeste, sudeste, sul
            ctx.save(); path_suave(ctx, jitter(pts, 1.0, seed + 2)); ctx.clip()
            for i, (nome, rp) in enumerate(REGIOES.items()):
                q = [P(*z) for z in rp]
                ctx.move_to(*q[0]); [ctx.line_to(*z) for z in q[1:]]; ctx.close_path()
                ctx.set_source_rgb(*mix(cores[i], terra, 0.35)); ctx.fill_preserve()
                ctx.set_source_rgb(*INK); ctx.set_line_width(4); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke()
            ctx.restore()
            path_suave(ctx, jitter(pts, 1.0, seed + 2)); ctx.set_source_rgb(*INK); ctx.set_line_width(7); ctx.stroke()
    else:
        cores = [a1, terra, a2, hexc("#F2B705") if a1 != hexc("#F2B705") else a3, escurece(a3, 0.1) if sum(a3) < 2.4 else hexc("#FF8A3D")]
        for nome, poli in MUNDO.items():
            pts = [P(*q) for q in _poli_pts(poli, 2.5)]
            forma(ctx, pts, cores[GRUPO[nome]], seed=seed + len(nome), amp=0.8, lw=5, sombra_off=(7, 8))
    # destaques: ponto com halo pulsando e rótulo
    for i, d in enumerate(st.get("destaque", [])):
        d = {"cidade": d} if isinstance(d, str) else dict(d)
        if "cidade" in d:
            if d["cidade"] not in CIDADES:
                raise SystemExit(f"mapa: cidade '{d['cidade']}' não existe. Cidades: {', '.join(CIDADES)}")
            lo, la = CIDADES[d["cidade"]]
        else:
            lo, la = d["lon"], d["lat"]
        x, y = P(lo, la)
        c = hexc(d["cor"]) if d.get("cor") else hexc("#FFD21F")
        pul = 0.5 + 0.5 * math.sin(t * 5 + i * 1.7)
        r = 46 + 26 * pul
        g = cairo.RadialGradient(x, y, 0, x, y, r)
        g.add_color_stop_rgba(0, *c, 0.95); g.add_color_stop_rgba(0.5, *c, 0.45); g.add_color_stop_rgba(1, *c, 0)
        ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
        ctx.arc(x, y, 14, 0, 2 * math.pi); ctx.set_source_rgb(*c); ctx.fill_preserve()
        ctx.set_source_rgb(*INK); ctx.set_line_width(5); ctx.stroke()
        rot = d.get("rotulo")
        if rot:
            tam = d.get("tam", 50)
            lado = d.get("lado", "dir" if x < largura * 0.2 else "esq")
            tx = x + 34 if lado == "dir" else x - 34
            caixas_txt.append(texto(ctx, rot, tx, y - tam * 0.7, tam, ancora="l" if lado == "dir" else "r"))
    if st.get("titulo"):
        caixas_txt.append(texto(ctx, st["titulo"], 0, -alt / 2 - 40 - st.get("tam", 80) * 0.6, st.get("tam", 80), max_w=largura))
    tb = (min(b[0] for b in caixas_txt), min(b[1] for b in caixas_txt), max(b[2] for b in caixas_txt), max(b[3] for b in caixas_txt)) if caixas_txt else None
    return {"corpo": (-largura / 2 - 40, -alt / 2 - 40, largura / 2 + 40, alt / 2 + 40), "texto": tb}
