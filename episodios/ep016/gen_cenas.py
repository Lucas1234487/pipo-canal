import json, math, itertools
OUT = "/home/claude/2026-11-28_C/cenas.json"
SONS = itertools.cycle(["pop", "pop2", "tique", "pop3", "slide", "pop", "tique", "pop2"])
def S(): return next(SONS)
def ent(t, j="pop", som=True, **k):
    a = {"em": t, "faz": "entra", "jeito": j}
    if som: a["som"] = S() if som is True else som
    a.update(k); return a
def bloco(id, x, y, w, h, cor, raio=24, acoes=None, **k):
    d = {"id": id, "tipo": "bloco", "x": x, "y": y, "largura": w, "altura": h, "cor": cor, "raio": raio, "pode_sobrepor": True, "acoes": acoes or []}
    d.update(k); return d
def texto(id, x, y, s, tam=72, t=None, fundo="#1D1B3A", cor=None, acoes=None, j="pop", som=True, **k):
    d = {"id": id, "tipo": "texto", "x": x, "y": y, "texto": s, "tam": tam, "pode_sobrepor": True, "acoes": acoes or []}
    if fundo and "\n" not in s: d["fundo"] = fundo
    if cor: d["cor"] = cor
    if t is not None: d["acoes"] = [ent(t, j, som)] + d["acoes"]
    d.update(k); return d
def pipo(id, x, y, esc, t0, t1, forma=None, ent_t=None, extra=None, per=1.1, **k):
    d = {"id": id, "tipo": "pipo", "x": x, "y": y, "escala": esc, "acoes": []}
    if forma: d["forma"] = forma
    if ent_t is not None: d["acoes"].append(ent(ent_t, "pop", "pop2"))
    t = (ent_t if ent_t is not None else t0) + 0.5; i = 0
    while t < t1 - 0.2:
        d["acoes"].append({"em": round(t, 2), "faz": "pula" if i % 2 == 0 else "squash", **({"altura": 16} if i % 2 == 0 else {"forca": 0.12})})
        t += per; i += 1
    d["acoes"] += (extra or []); d.update(k); return d
def broom(id, x, y, rot=-14, L=330):
    th = math.radians(rot)
    bx = x + (-(L/2 + 38) * math.sin(th)) / 1080; by = y + ((L/2 + 38) * math.cos(th)) / 1920
    h = bloco(id + "_h", x, y, 22, L, "#8A5A2B", 10, rot=rot, camada="topo")
    b = bloco(id + "_c", bx, by, 130, 96, "#E3B23C", 22, rot=rot, camada="topo")
    return [h, b]
def sweep(parts, t0, t1, amp=0.05, per=0.55):
    t = t0; s = 1
    while t < t1:
        for p in parts:
            p["acoes"].append({"em": round(t, 2), "faz": "move", "para": [round(p["x"] + s * amp, 4), p["y"]], "dur": per * 0.9, "curva": "suave"})
        s = -s; t += per
def mae(id, x_dx, pose="mao_na_cintura", expr="feliz", acoes=None, **k):
    d = {"id": id, "tipo": "humano", "ancora": "chao", "dx": x_dx, "cabelo": "coque", "cabelo_cor": "castanho_escuro", "pele": "morena", "corpo": "curvilineo",
         "roupa": "#E8452C", "calca": "#2B2440", "expressao": expr, "pose": pose, "acoes": acoes or []}
    d.update(k); return d
POE = "#CDBA9A"

cenas = []
# ---------- S0: 0 - 3.775 : conflito sem som
m = mae("mae", -0.22, pose="mao_na_cintura", acoes=[
    {"em": "volta", "faz": "expressao", "para": "bravo"}, {"em": "volta", "faz": "pose", "para": "maos_na_cabeca"}, {"em": 0.4, "faz": "squash", "forca": 0.06}])
vb = broom("vass", 0.20, 0.50)
sweep(vb, 0.3, 2.6, amp=0.045)
for p in vb: p["x"] = round(p["x"], 4)
puffs = []
for i, xx in enumerate([0.70, 0.76, 0.82, 0.73, 0.79, 0.85]):
    puffs.append(bloco(f"pf{i}", xx, 0.30, 34, 34, POE, 17, acoes=[ent(2.15 + i * 0.1, "aparece", False), {"em": 2.2 + i * 0.1, "faz": "move", "para": [xx, 0.86], "dur": 0.9, "curva": "rapido"}, {"em": 2.78 + i * 0.1, "faz": "sai", "jeito": "some", "dur": 0.1}]))
import random
rr = random.Random(7); manchas = []
for i in range(22):
    x = rr.uniform(0.08, 0.92) if i < 14 else rr.uniform(0.60, 0.70); y = rr.uniform(0.76, 0.93) if i < 14 else rr.uniform(0.515, 0.525)
    w = rr.randint(40, 120) if i < 14 else rr.randint(20, 50)
    manchas.append(bloco(f"mc{i}", round(x, 3), round(y, 3), w, max(12, w // 4), rr.choice(["#B9B2A6", "#A39C8F", "#CFC8BA"]), 8, alpha=0.0, camada="topo",
        acoes=[{"em": round(0.2 + i * 0.12, 2), "faz": "muda", "prop": "alpha", "para": 0.9, "dur": 0.6}]))
c0 = {"em": 0, "cenario": "sala", "luz": "dia", "paleta": "menta", "elementos": [
    texto("t1", 0.5, 0.185, "VARREU ONTEM.\nVOLTOU HOJE.", 78),
    mae("mae", -0.20, acoes=m["acoes"]),
    *vb,
    {"id": "rel", "tipo": "relogio", "x": 0.70, "y": 0.335, "escala": 0.2, "horas": 3, "giro": 0.8, "pode_sobrepor": True, "camada": "topo", "acoes": [ent(0.1, "pop", False)]},
    *manchas,
    *puffs,
    pipo("pipo", 0.52, 0.47, 0.62, 0, 3.7, ent_t=0.5, olhar="dir", per=0.9),
], "acoes": [{"em": 0.05, "faz": "soco", "som": "pop2"}]}
cenas.append(c0)

# ---------- S1: 3.775 - 6.92 : mito
dust = [bloco(f"d{i}", 0.5 + dx, 0.30 + dy, w, h, POE if i % 2 else "#B8A583", 20, rot=r) for i, (dx, dy, w, h, r) in enumerate([(-0.10, 0.03, 160, 60, -8), (0.07, 0.04, 200, 70, 6), (0.0, 0.0, 240, 90, 0), (-0.04, -0.03, 120, 60, 10)])]
c1 = {"em": "linha1", "cenario": "chapado", "padrao": "gradiente_vivo", "paleta": "uva", "elementos": [
    texto("t2", 0.5, 0.17, "PELE MORTA?", 80, t="linha1", som="pop"),
    *dust,
    {"id": "lupa", "tipo": "icone", "qual": "lupa", "x": 0.5, "y": 0.29, "escala": 1.6, "acoes": [ent("linha1", "pop", "slide")]},
    bloco("cartao", 0.5, 0.43, 700, 150, "#FFF3E0", 30, texto="PELE MORTA", tam=84, cor_texto="#1D1B3A", acoes=[ent("pele", "pop", "pop3")]),
    {"id": "mito", "tipo": "carimbo", "x": 0.62, "y": 0.50, "texto": "MITO", "tam": 100, "cor": "#E8352A", "inclina": -12, "acoes": [ent("morta", "pop", "carimbo", dur=0.18)]},
    pipo("pipo", 0.13, 0.56, 0.55, 3.7, 6.9, ent_t=3.9, olhar="dir", per=0.8),
], "acoes": [{"em": "morta", "faz": "soco"}]}
cenas.append(c1)

# ---------- S2: 6.92 - 10.253 : estudo (prancheta + casa em corte)
setas = []
for i, (dx, dy, vx, vy, w) in enumerate([(-0.33, -0.01, 200, 0, "esq"), (0.33, 0.01, -200, 0, "dir"), (0.0, -0.17, 0, 130, "cima")]):
    setas.append({"id": f"s{i}", "tipo": "seta", "x": 0.5 + dx, "y": 0.34 + dy, "vetor": [vx, vy], "cor": "#E8452C", "curva": 0.0, "progresso": 1, "pode_sobrepor": True, "camada": "topo", "acoes": [ent(9.0 + i * 0.35, "aparece", S())]})
c2 = {"em": "linha2", "cenario": "chapado", "padrao": "gradiente_vivo", "paleta": "cobalto", "elementos": [
    texto("t3", 0.5, 0.165, "UM ESTUDO CALCULOU", 70, t="estudo"),
    bloco("prancheta", 0.5, 0.33, 740, 520, "#F6EAD0", 34, acoes=[ent(7.0, "desce", "slide")]),
    bloco("clip", 0.5, 0.205, 200, 46, "#8A8F99", 18, acoes=[ent(7.3, "aparece", False)]),
    {"id": "casa", "tipo": "casa", "x": 0.5, "y": 0.34, "largura": 380, "altura": 330, "natal": False, "cor": "#E8452C", "pode_sobrepor": True, "camada": "topo", "acoes": [ent("estudo", "pop", "pop2", depois=0.1)]},
    *setas,
    pipo("pipo", 0.80, 0.545, 0.55, 6.9, 10.2, ent_t=7.4, olhar="esq", per=0.8, camada="topo"),
]}
cenas.append(c2)

# ---------- S3: 10.253 - 12.454 : ESTOURO em "fora"
nuvens = []
for i in range(7):
    yy = 0.28 + (i % 4) * 0.045; xx = 0.72
    nuvens.append(bloco(f"nv{i}", xx, yy, 120 + 20 * (i % 3), 70, POE if i % 2 else "#B8A583", 35,
                        acoes=[ent(11.25 + i * 0.07, "aparece", False), {"em": 11.25 + i * 0.07, "faz": "move", "para": [0.55 - 0.03 * (i % 3), yy + 0.01], "dur": 0.5, "curva": "rapido"}]))
c3 = {"em": "linha3", "cenario": "chapado", "padrao": "halftone", "paleta": "laranja", "energia": 0.8, "elementos": [
    texto("t4", 0.5, 0.17, "MAIS DA METADE:\nDE FORA", 74, t="mais"),
    {"id": "porta", "tipo": "porta", "x": 0.74, "y": 0.38, "largura": 360, "altura": 520, "cor": "#2A3FD1", "dentro": "#FFE9B0",
     "acoes": [{"em": "entra", "faz": "muda", "prop": "abre", "para": 1, "dur": 0.4, "som": "porta"}]},
    *nuvens,
    pipo("pipo", 0.27, 0.43, 0.95, 10.2, 11.7, ent_t=None, olhar="dir", per=0.5, acoes_extra=None) if False else
    {"id": "pipo", "tipo": "pipo", "x": 0.27, "y": 0.43, "escala": 0.95, "olhar": "dir", "acoes": [
        {"em": 10.35, "faz": "pula", "altura": 14}, {"em": 10.85, "faz": "squash", "forca": 0.12}, {"em": 11.2, "faz": "treme", "dur": 0.5, "forca": 6},
        {"em": "fora", "faz": "estoura", "som": "estouro", "volume": 1.0, "som_atraso": -0.12}]},
], "acoes": [{"em": "fora", "faz": "flash"}, {"em": "fora", "faz": "soco", "forca": 0.14}, {"em": "fora", "faz": "treme", "dur": 0.4, "forca": 22}]}
cenas.append(c3)

# ---------- S4: 12.454 - 15.198 : sola de sapato
terra = []
for i, (dx, dy, w) in enumerate([(-0.08, 0.04, 70), (0.06, 0.07, 90), (0.0, 0.10, 60), (0.10, 0.02, 56), (-0.03, 0.0, 50)]):
    xx, yy = 0.55 + dx, 0.33 + dy
    terra.append(bloco(f"tr{i}", xx, yy, w, w * 0.8, "#5E3A1E", 24, acoes=[ent(12.7 + i * 0.1, "pop", False), {"em": 13.8 + i * 0.12, "faz": "move", "para": [xx + (i - 2) * 0.02, 0.49], "dur": 0.45, "curva": "rapido"}]))
pegadas = [bloco(f"pg{i}", 0.30 + i * 0.2, 0.505, 110, 62, "#5E3A1E", 30, rot=-6 + 6 * i, camada="meio", acoes=[ent(t, "pop", "pop" if i % 2 else "tique")]) for i, t in enumerate([13.9, 14.35, 14.7])]
c4 = {"em": "linha4", "cenario": "chapado", "padrao": "papel_rasgado", "paleta": "tomate", "elementos": [
    texto("t5", 0.5, 0.155, "TERRA NA SOLA", 74, t="terra"),
    bloco("piso", 0.5, 0.515, 1000, 110, "#E8D9B5", 30, camada="meio"),
    bloco("sola", 0.55, 0.33, 330, 520, "#3B2A22", 150, acoes=[ent(12.6, "desce", "slide"), {"em": "sola", "faz": "squash", "forca": 0.1}]),
    bloco("sola2", 0.55, 0.33, 250, 430, "#7A5A44", 120, acoes=[ent(12.6, "desce", False)]),
    bloco("tread1", 0.55, 0.265, 190, 22, "#3B2A22", 10), bloco("tread2", 0.55, 0.315, 190, 22, "#3B2A22", 10), bloco("tread3", 0.55, 0.365, 190, 22, "#3B2A22", 10),
    *terra, *pegadas,
    {"id": "pipo", "tipo": "pipo", "x": 0.2, "y": 0.40, "escala": 0.8, "forma": "pipoca", "pose": "apontando", "aponta_para": [200, -80], "acoes": [
        {"em": 12.7, "faz": "pula", "altura": 18}, {"em": 13.5, "faz": "squash", "forca": 0.12}, {"em": 14.2, "faz": "pula", "altura": 18}, {"em": 14.8, "faz": "squash", "forca": 0.1}]},
]}
cenas.append(c4)

# ---------- S5: 15.198 - 17.753 : janela, vento
parts = []
for i in range(14):
    yy = 0.20 + (i % 5) * 0.03; w = 24 + (i % 3) * 12
    t0 = 15.4 + i * 0.12
    parts.append(bloco(f"pz{i}", 0.34, yy, w, w, "#FFFFFF" if i % 2 else POE, w // 2,
                       acoes=[ent(t0, "aparece", False), {"em": t0, "faz": "move", "para": [0.62 + (i % 4) * 0.08, yy + 0.09 + (i % 3) * 0.03], "dur": 1.3, "curva": "linear"}, {"em": t0 + 1.1, "faz": "sai", "jeito": "some", "dur": 0.2}]))
vento = [{"id": f"v{i}", "tipo": "seta", "x": 0.22 + i * 0.04, "y": 0.30 + i * 0.07, "vetor": [330, 12], "cor": "#FFFFFF", "curva": 0.12, "progresso": 1, "pode_sobrepor": True,
          "acoes": [ent(15.5 + i * 0.3, "desliza_esq", "whoosh" if i == 0 else False)]} for i in range(2)]
c5 = {"em": "linha5", "cenario": "sala", "luz": "tarde", "paleta": "rosa", "elementos": [
    texto("t6", 0.5, 0.155, "PÓ DO VENTO", 74, t="pozinho"),
    *vento, *parts,
    {"id": "pipo", "tipo": "pipo", "x": 0.30, "y": 0.50, "escala": 0.75, "forma": "pipoca", "olhar": "esq", "acoes": [
        {"em": 15.3, "faz": "pula", "altura": 16}, {"em": 16.1, "faz": "squash", "forca": 0.12}, {"em": 16.8, "faz": "pula", "altura": 16}, {"em": 17.3, "faz": "squash", "forca": 0.1}]},
]}
cenas.append(c5)

# ---------- S6: 17.753 - 21.263 : liquidificador / mistura
def chip(id, x, y, w, h, cor, s, t, tam=52, ctexto="#1D1B3A", dy0=0.0):
    return bloco(id, x, y, w, h, cor, h // 2, texto=s, tam=tam, cor_texto=ctexto, acoes=[ent(t, "desce", S())])
c6 = {"em": "linha6", "cenario": "chapado", "padrao": "ondas", "paleta": "petroleo", "elementos": [
    texto("t7", 0.5, 0.15, "A MISTURA DA POEIRA", 62, t="pele"),
    bloco("jar", 0.62, 0.345, 460, 560, "#CFE8F0", 56, alpha=0.9),
    bloco("tampa", 0.62, 0.195, 400, 46, "#2B2440", 20),
    bloco("base", 0.62, 0.505, 500, 90, "#2B2440", 34),
    {"id": "luz", "tipo": "bloco", "x": 0.55, "y": 0.35, "largura": 40, "altura": 380, "cor": "#FFFFFF", "raio": 20, "alpha": 0.35, "pode_sobrepor": True, "acoes": []},
    chip("c_terra", 0.62, 0.43, 400, 190, "#7A4A2A", "TERRA", "mistura", 76, "#FFF3E0"),
    chip("c_pele", 0.62, 0.345, 300, 80, "#F2C9A0", "PELE", "pele", 54),
    chip("c_fiapo", 0.60, 0.275, 300, 80, "#FFFFFF", "FIAPO", "fiapo", 54, "#1D1B3A"),
    chip("c_tapete", 0.64, 0.355, 320, 80, "#FFFFFF", "TAPETE", "tapete", 54, "#1D1B3A"),
    pipo("pipo", 0.2, 0.46, 0.7, 17.7, 21.2, forma="pipoca", olhar="dir", per=0.7),
], "acoes": [{"em": "mistura", "faz": "treme", "dur": 0.9, "forca": 8}]}
c6["elementos"][4]["acoes"] = []
# chips caem na ordem certa: terra ("TERRA") entra por último mas maior
cenas.append(c6)

# ---------- S7: 21.263 - 23.405 : vassoura não vence + meme
vb2 = broom("vb", 0.27, 0.45, rot=-16)
sweep(vb2, 21.4, 23.0, amp=0.08, per=0.4)
mont = [bloco(f"mt{i}", 0.62 + i * 0.12, 0.575, 190, 64, POE, 32, acoes=[{"em": 21.55 + i * 0.05, "faz": "muda", "prop": "alpha", "para": 0, "dur": 0.15}, {"em": 22.04 + i * 0.1, "faz": "muda", "prop": "alpha", "para": 1, "dur": 0.2}]) for i in range(2)]
c7 = {"em": "linha7", "cenario": "cozinha", "luz": "dia", "paleta": "tomate", "elementos": [
    texto("t8", 0.5, 0.155, "SÓ A VASSOURA\nNÃO VENCE", 66, t="so", som="pop"),
    mae("mae", -0.15, pose="esforco" if False else "mao_na_cintura", expr="esforco", acoes=[{"em": "vence", "faz": "expressao", "para": "triste"}, {"em": 21.5, "faz": "squash", "forca": 0.06}], ancora="balcao"),
    *vb2, *mont,
], "acoes": [{"em": "vence", "faz": "reacao", "estilo": "triste", "alvo": "mae", "dur": 0.7, "som_dur": 0.8, "volume": 0.6}]}
c7["elementos"][1].pop("ancora"); c7["elementos"][1]["ancora"] = "balcao"; c7["elementos"][1]["dx"] = -0.25
cenas.append(c7)

# ---------- S8a: 23.405 - 25.15 : pergunta
c8a = {"em": "linha8", "cenario": "chapado", "padrao": "formas", "paleta": "menta", "elementos": [
    texto("t9", 0.5, 0.20, "QUER MENOS\nPOEIRA?", 84, t="quer"),
    {"id": "pipo", "tipo": "pipo", "x": 0.5, "y": 0.42, "escala": 0.95, "forma": "pipoca", "pose": "apontando", "aponta_para": [260, -60], "acoes": [
        ent(23.7, "pop", "pop2"), {"em": 24.1, "faz": "pula", "altura": 20}, {"em": 24.6, "faz": "squash", "forca": 0.14}]},
]}
cenas.append(c8a)
# ---------- S8b: 25.15 - 28.163 : porta, tapete, sapato fora
def sap(id, x, t):
    return [bloco(id + "a", x, 0.49, 150, 70, "#3B2A22", 34, acoes=[ent(t, "cai", "pop3")]), bloco(id + "b", x - 0.045, 0.5, 70, 56, "#7A5A44", 24, acoes=[ent(t, "cai", False)])]
ok = lambda id, x, y, t: bloco(id, x, y, 120, 64, "#2FAE5F", 32, texto="OK", tam=44, acoes=[ent(t, "pop", "certo", volume=0.45)])
c8b = {"em": "porta", "cenario": "chapado", "padrao": "gradiente_vivo", "paleta": "cobalto", "elementos": [
    texto("t10", 0.5, 0.15, "COMEÇA PELA PORTA", 66, t="porta"),
    {"id": "pt", "tipo": "porta", "x": 0.52, "y": 0.33, "largura": 340, "altura": 520, "cor": "#E8452C", "dentro": "#FFE9B0", "acoes": [{"em": "porta", "faz": "muda", "prop": "abre", "para": 0.4, "dur": 0.5, "som": "porta", "volume": 0.5}]},
    bloco("tapete", 0.52, 0.515, 420, 56, "#F2C14E", 22, acoes=[ent("tapete", "pop", "pop")]),
    ok("ok1", 0.52, 0.575, "tapete"),
    *sap("sa", 0.17, "sapato"), *sap("sb", 0.31, 26.75),
    ok("ok2", 0.24, 0.575, "sapato"),
    pipo("pipo", 0.80, 0.45, 0.7, 25.1, 28.1, forma="pipoca", olhar="esq", per=0.8),
]}
cenas.append(c8b)

# ---------- S9 : 28.163 - 30.954 : manda
c9 = {"em": "linha9", "cenario": "chapado", "padrao": "bokeh", "paleta": "uva", "elementos": [
    texto("t11", 0.5, 0.17, "MANDA PRA QUEM\nENTRA DE SAPATO", 66, t="manda"),
    bloco("tap2", 0.5, 0.50, 520, 56, "#F6EAD0", 22),
    bloco("sapato", 0.5, 0.30, 360, 160, "#3B2A22", 70, acoes=[ent("entra", "desce", "whoosh"), {"em": "sapato", "faz": "move", "para": [0.5, 0.44], "dur": 0.3, "curva": "rapido"}, {"em": 29.75, "faz": "squash", "forca": 0.14}]),
    bloco("sapato_s", 0.5, 0.33, 390, 34, "#F2EBDD", 16, acoes=[ent("entra", "desce", False), {"em": "sapato", "faz": "move", "para": [0.5, 0.47], "dur": 0.3, "curva": "rapido"}]),
    bloco("sapato_b", 0.43, 0.315, 150, 110, "#7A5A44", 50, acoes=[ent("entra", "desce", False), {"em": "sapato", "faz": "move", "para": [0.43, 0.455], "dur": 0.3, "curva": "rapido"}]),
    bloco("mancha", 0.5, 0.50, 300, 30, "#5E3A1E", 14, acoes=[ent(29.7, "pop", "impacto2", volume=0.5)]),
    bloco("env", 0.80, 0.40, 190, 90, "#2FAE5F", 45, texto="ENVIAR", tam=40, acoes=[ent("sua", "pop", "certo", volume=0.5), {"em": 30.5, "faz": "move", "para": [0.80, 0.33], "dur": 0.4, "curva": "rapido"}]),
    {"id": "pipo", "tipo": "pipo", "x": 0.22, "y": 0.43, "escala": 0.8, "forma": "pipoca", "pose": "apontando", "aponta_para": [200, 40], "acoes": [
        ent(28.5, "pop", "pop2"), {"em": 29.3, "faz": "pula", "altura": 16}, {"em": 30.1, "faz": "squash", "forca": 0.12}]},
]}
cenas.append(c9)

# ---------- S10 : 30.954 - fim : ENTRA ou FICA NA PORTA?
c10 = {"em": "linha10", "cenario": "chapado", "padrao": "gradiente_vivo", "paleta": "tomate", "elementos": [
    texto("t12", 0.5, 0.17, "ENTRA ou\nFICA NA PORTA?", 70, t="aí"),
    bloco("b1", 0.5, 0.265, 760, 120, "#2FAE5F", 44, texto="ENTRA", tam=76, acoes=[ent("sapato", "pop", "pop3"), {"em": "entra", "faz": "squash", "forca": 0.14}]),
    bloco("b2", 0.5, 0.35, 760, 120, "#2A3FD1", 44, texto="FICA NA PORTA", tam=70, acoes=[ent("sapato", "pop", "pop"), {"em": "porta", "faz": "squash", "forca": 0.14}]),
    {"id": "pipo", "tipo": "pipo", "x": 0.5, "y": 0.525, "escala": 0.62, "forma": "pipoca", "acoes": [
        ent(31.1, "pop", "pop2"), {"em": 31.8, "faz": "pula", "altura": 20}, {"em": 32.3, "faz": "squash", "forca": 0.12}, {"em": 32.9, "faz": "pula", "altura": 20}]},
]}
cenas.append(c10)

# ---------- som: base percussao; silencio 0.4 s antes de "fora"; riser antes
sfx = [
 ["assets/sfx/memes/riser.ogg", 9.85, 0.9],
 ["assets/sfx/memes/boom.ogg", 11.62, 0.9],
 ["assets/sfx/3-pop-sounds/pop2.ogg", 11.62, 1.0],
 ["assets/sfx/75-cc0-breaking-falling-hit-sfx/bfh1_glass_breaking_02.ogg", 11.64, 0.7],
 ["assets/sfx/100-cc0-sfx-2/sfx100v2_items_02.ogg", 12.0, 0.5],
]
M="assets/musica/cinematic-percussion-loop/Cinematic%20percussion%20loop%202.wav"
G=0.04
MUS=[[[M,0,11.3,0.1],0,G],[[M,11.74,0.26,0.02],11.74,G],[[M,0,12,0.02],12.0,G],[[M,0,9.9,0.02],24.0,G]]
top = {"paleta": "menta", "musica": "percussao", "musica_inicio": 0, "whoosh_nos_cortes": True, "volume_whoosh": 0.22, "cauda": 0.08,
       "silencios": [[0, 40]], "sfx": sfx + MUS, "cenas": cenas}
json.dump(top, open(OUT, "w"), ensure_ascii=False, indent=1)
print("ok", len(cenas))
