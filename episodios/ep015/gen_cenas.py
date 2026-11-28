#!/usr/bin/env python3
"""Gera WORK/cenas.json do ep015 (H, olhos pra frente parte 2: dinossauros). Rodar de /home/claude/pipo-canal."""
import json, re, unicodedata

WORK = "/home/claude/2026-11-28_H"
TM = json.load(open(f"{WORK}/timing.json"))
TOTAL = TM["total"]


def norm(s):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", s.lower()).encode("ascii", "ignore").decode())


def W(line, palavra, nth=0):
    ws = [w for w in TM["lines"][line]["words"] if norm(w[0]).startswith(norm(palavra))]
    return round(ws[nth][1], 2)


def L(i):
    return round(TM["lines"][i]["start"], 2)


_som = ["pop", "pop2", "pop3"]
_k = [0]


def pop_som():
    _k[0] += 1
    return _som[_k[0] % 3]


BR = "#FFF8EC"


def T(id, txt, x, y, tam, t, cor=BR, fundo=None, rot=None, jeito="pop", soco=None, som=True, extra=None, saiu=None):
    d = dict(id=id, tipo="texto", x=x, y=y, texto=txt, tam=tam, cor=cor)
    if fundo:
        d["fundo"] = fundo
    if rot is not None:
        d["rot"] = rot
    a = dict(em=t, faz="entra", jeito=jeito)
    if som:
        a["som"] = pop_som()
    d["acoes"] = [a]
    if soco:
        d["acoes"].append(dict(em=soco, faz="soco"))
    if saiu:
        d["acoes"].append(dict(em=saiu, faz="sai", jeito="some", dur=0.2))
    if extra:
        d["acoes"] += extra
    return d


def PIPO(x, y, esc, t0, t1, **k):
    d = dict(id="pipo", tipo="pipo", x=x, y=y, escala=esc, acoes=[])
    d.update(k)
    t = t0 + 0.3
    ciclo = [("olha", "esq"), ("squash", None), ("sobrancelha", 0.6), ("olha", "camera"), ("squash", None), ("olha", "dir"), ("sobrancelha", 1.0)]
    i = 0
    while t < t1 - 0.2:
        faz, para = ciclo[i % len(ciclo)]
        a = dict(em=round(t, 2), faz=faz)
        if para is not None:
            a["para"] = para
        d["acoes"].append(a)
        t += 0.8
        i += 1
    return d


def B(id, esp, vista, x, y, esc, **k):
    d = dict(id=id, tipo="bicho", especie=esp, vista=vista, x=x, y=y, escala=esc)
    d.update(k)
    return d


cenas = []
som_extra = []     # sfx manuais [arquivo, t, vol]


def C(em, cenario, elementos, **k):
    em = round(em, 2)
    d = dict(em=em, cenario=cenario)
    d.update(k)
    d["elementos"] = elementos
    cenas.append(d)
    return d


def entra(t, jeito="pop", som=True, **k):
    a = dict(em=t, faz="entra", jeito=jeito)
    if som:
        a["som"] = pop_som()
    a.update(k)
    return a


# ---------------------------------------------------------------- tempos
t_regra = W(2, "regra"); t_olho2 = W(2, "olho"); t_na = W(2, "na"); t_frente2 = W(2, "frente")
t_ligou = W(3, "ligou"); t_ele = W(3, "ele"); t_assim = W(3, "assim")
t_prof = W(4, "profundidade")
t_rugido = W(10, "Rugido")
t_ah = W(11, "ah"); t_oi = W(11, "oi")

# ============================================================ 0: QUADRO 1 (cretáceo de dia, sombra do T. rex atrás)
S0 = 0.0
C(0, "cretaceo", [
    B("sombra", "tiranossauro", "perfil", 0.66, 0.37, 1.2, silhueta=True, espelha=True, alpha=0.95, acoes=[dict(em=0, faz="escala", para=1.32, dur=3.5, curva="linear")]),
    B("pato", "bicodepato", "frente", 0.25, 0.395, 1.2, olhos="frente", pose="bicando", expressao="neutro"),
    B("samam", "bicodepato", "planta", 0.47, 0.475, 0.5),
    T("t1", "OLHO NA FRENTE\n= ALMOÇO", 0.5, 0.17, 80, -0.4, soco=W(0, "almo")),
    T("selo", "PARTE 2", 0.8, 0.54, 44, -0.4, fundo="#E8452C", rot=6),
    PIPO(0.1, 0.53, 0.4, 0, L(1)),
], luz="dia", paleta="menta", deriva=0)

# ============================================================ 1: pombo da parte 1, a sombra cresce e vira dinossauro
t_sombra = W(1, "sombra"); t_tempo = W(1, "pros")
C(L(1), "rua", [
    B("sombra", "tiranossauro", "frente", 0.55, 0.36, 0.5, silhueta=True, alpha=0.0, acoes=[
        dict(em=t_sombra, faz="muda", prop="alpha", para=0.85, dur=1.4),
        dict(em=t_sombra, faz="escala", para=1.5, dur=1.6, curva="suave")]),
    B("pb", "pombo", "perfil", 0.45, 0.44, 1.05, olhos="lado", pose="bicando", expressao="neutro"),
    T("t2", "PARTE 2", 0.5, 0.17, 84, W(1, "dois"), fundo="#1F5FD1", rot=-3),
    T("t3", "A SOMBRA CRESCEU", 0.5, 0.17, 60, t_sombra, fundo="#E8452C", rot=2, extra=[]),
    PIPO(0.86, 0.53, 0.4, L(1), t_tempo),
], luz="tarde", paleta="mostarda")
# o texto "PARTE 2" some quando a sombra cresce
cenas[-1]["elementos"][2]["acoes"].append(dict(em=t_sombra - 0.05, faz="sai", jeito="some", dur=0.15))

# ============================================================ 2: mergulho para a floresta do Cretáceo
C(t_tempo, "cretaceo", [
    B("pato", "bicodepato", "perfil", 0.22, 0.404, 1.1, olhos="lado", anda=True, acoes=[dict(em=t_tempo, faz="move", para=[0.6, 0.404], dur=1.6, curva="linear")]),
    T("t4", "CRETÁCEO", 0.5, 0.17, 84, t_tempo + 0.35, fundo="#2E9E4A", rot=-3),
    PIPO(0.9, 0.53, 0.4, t_tempo, L(2)),
], luz="dia", transicao="mergulho", mergulho_em=[0.55, 0.40])

# ============================================================ 3-4: a regra; olhos deslizam do lado para a frente
cores = [("#8A7BE0", None), ("#58B7D6", None), ("#D6A84E", "#FBF0D0")]
els = []
for i, (cor, cor2) in enumerate(cores):
    d = B(f"d{i}", "bicodepato", "frente", (0.2, 0.5, 0.8)[i], 0.447, 0.72, olhos="lado", pose="bicando", cor=cor, acoes=[])
    if cor2:
        d["cor2"] = cor2
    els.append(d)
C(L(2), "cretaceo", els + [
    T("t5", "REGRA", 0.5, 0.17, 100, round(L(2) + 0.02, 2), fundo="#E8452C", rot=-4, soco=t_regra + 0.25),
    PIPO(0.5, 0.57, 0.4, L(2), t_olho2 - 0.05),
], luz="dia")
t_s4 = round(t_olho2 - 0.08, 2)
els = []
for i, (cor, cor2) in enumerate(cores):
    d = B(f"d{i}", "bicodepato", "frente", (0.2, 0.5, 0.8)[i], 0.447, 0.72, olhos="lado", pose="bicando", cor=cor, acoes=[
        dict(em=(t_olho2, t_na + 0.05, t_frente2)[i], faz="muda", prop="olhos", para="frente", som=pop_som()),
        dict(em=(t_olho2, t_na + 0.05, t_frente2)[i], faz="squash")])
    if cor2:
        d["cor2"] = cor2
    els.append(d)
C(t_s4, "cretaceo", els + [
    T("t6", "OLHO NA FRENTE", 0.5, 0.17, 72, t_olho2, fundo="#1F5FD1", rot=2),
    PIPO(0.5, 0.57, 0.4, t_s4, L(3)),
], luz="tarde")

# ============================================================ 5-6: o T. rex nem ligou (dá de ombros), selo "JÁ ERA ASSIM"
C(L(3), "cretaceo", [
    B("rex", "tiranossauro", "frente", 0.5, 0.39, 1.3, pose="ombros", acoes=[dict(em=t_ligou, faz="soco")]),
    T("t7", "NEM LIGOU", 0.5, 0.17, 80, W(3, "nem"), fundo="#8E2F2A", rot=-3),
    PIPO(0.1, 0.53, 0.4, L(3), t_ele),
], luz="tarde")
C(t_ele - 0.05, "cretaceo", [
    B("rex", "tiranossauro", "frente", 0.5, 0.36, 1.55, pose="ombros", expressao="feliz"),
    T("t8", "JÁ ERA ASSIM", 0.5, 0.17, 76, W(3, "ja"), fundo="#7A3FBF", rot=3, soco=t_assim),
    PIPO(0.9, 0.53, 0.4, t_ele, L(4)),
], luz="dia")

# ============================================================ 9-10: estudo do crânio; visão em profundidade
C(L(4), "chapado", [
    B("cr", "tiranossauro", "cranio", 0.5, 0.38, 1.7, acoes=[dict(em=W(4, "cranio"), faz="soco")]),
    T("t11", "ESTUDO COM\nO CRÂNIO", 0.5, 0.15, 64, W(4, "estudo"), fundo="#1A0F24", rot=-2),
    PIPO(0.88, 0.54, 0.4, L(4), t_prof - 0.15),
], padrao="halftone", paleta="rosa", deriva=0)
C(round(t_prof - 0.15, 2), "cretaceo", [
    B("rex", "tiranossauro", "perfil", 0.5, 0.404, 1.1, anda=True, acoes=[dict(em=t_prof, faz="move", para=[0.58, 0.404], dur=1.6, curva="linear")]),
    T("t12", "VISÃO EM\nPROFUNDIDADE", 0.5, 0.17, 68, t_prof, fundo="#2E9E4A", rot=2, soco=W(4, "bem")),
    PIPO(0.1, 0.53, 0.4, t_prof, L(5)),
], luz="dia")

# ============================================================ 11-12: bico-de-pato real, olho do lado, leque largo
t_real = W(5, "real"); t_lado6 = W(5, "lado"); t_via = W(5, "via")
C(L(5), "cretaceo", [
    B("pato", "bicodepato", "perfil", 0.4, 0.404, 1.1, olhos="lado", anda=True, acoes=[dict(em=L(5), faz="move", para=[0.5, 0.404], dur=1.8, curva="linear")]),
    T("t13", "BICO-DE-PATO", 0.5, 0.17, 80, W(5, "bico"), fundo="#8A7BE0", rot=-3),
    PIPO(0.9, 0.53, 0.4, L(5), t_real - 0.1),
], luz="dia")
C(round(t_real - 0.1, 2), "chapado", [
    B("pato", "bicodepato", "cima", 0.5, 0.47, 1.0, olhos="lado", campo=300, cego=True, alcance=480),
    T("t14", "NA VIDA REAL:\nOLHO DO LADO", 0.5, 0.15, 60, t_real, fundo="#1F5FD1", rot=2, soco=t_lado6),
    PIPO(0.12, 0.52, 0.4, t_real, t_via),
], padrao="gradiente_vivo", paleta="menta", deriva=0)

# ============================================================ 13: "via quase tudo em volta" (mesma fala do bico-de-pato real): olhos do lado olhando em volta
t_via = W(5, "via")
C(round(t_via - 0.05, 2), "chapado", [
    B("pato", "bicodepato", "frente", 0.5, 0.36, 1.5, olhos="lado", acoes=[dict(em=W(5, "quase"), faz="olha", para="esq"), dict(em=W(5, "tudo"), faz="olha", para="dir"),
                                                                             dict(em=W(5, "volta"), faz="olha", para="camera")]),
    T("t16", "VÊ QUASE TUDO\nEM VOLTA", 0.5, 0.15, 60, t_via, fundo="#E8452C", rot=2),
    PIPO(0.9, 0.54, 0.4, t_via, L(6)),
], padrao="bokeh", paleta="laranja", deriva=0)

# ============================================================ 15-16: com a regra o olho foi pra frente; só vê o prato
t_pf = W(6, "frente"); t_agora = W(6, "agora"); t_prato = W(6, "prato")
C(L(6), "cretaceo", [
    B("pato", "bicodepato", "frente", 0.5, 0.36, 1.5, olhos="lado", acoes=[
        dict(em=t_pf, faz="muda", prop="olhos", para="frente", som="pop2"), dict(em=t_pf, faz="squash"), dict(em=t_pf, faz="expressao", para="julgando")]),
    T("t17", "REGRA: OLHO NA FRENTE", 0.5, 0.17, 56, W(6, "regra"), fundo="#E8452C", rot=-3, soco=t_pf),
    PIPO(0.9, 0.54, 0.4, L(6), t_agora - 0.1),
], luz="dia")
C(round(t_agora - 0.1, 2), "chapado", [
    B("planta", "bicodepato", "planta", 0.5, 0.27, 0.8),
    B("pato", "bicodepato", "cima", 0.5, 0.46, 0.95, olhos="frente", campo=55, cego=True, alcance=420, expressao="julgando"),
    T("t18", "SÓ VÊ O PRATO", 0.5, 0.15, 72, W(6, "so"), fundo="#1A0F24", rot=2, soco=t_prato),
    PIPO(0.1, 0.53, 0.4, t_agora, L(7)),
], padrao="gradiente_vivo", paleta="petroleo", deriva=0)

# ============================================================ 17-18: tio na churrasqueira (picanha), volta ao bico-de-pato com a mesma cara
t_pic = W(7, "picanha"); t_volta = round(t_pic + 0.28, 2)
C(L(7), "chapado", [
    dict(id="tio", tipo="humano", preset="tiozao_do_churrasco", x=0.4, y=0.37, escala=0.85, expressao="apaixonado", olhar="baixo", acoes=[
        entra(L(7), "pop", som=False), dict(em=t_pic, faz="soco")]),
    dict(id="grill", tipo="icone", qual="churrasqueira", x=0.5, y=0.54, escala=0.8, acoes=[entra(L(7) + 0.1, "sobe", som=False)]),
    T("t19", "TIO NO CHURRASCO", 0.5, 0.15, 64, W(7, "tio"), fundo="#E8452C", rot=-2),
    PIPO(0.88, 0.4, 0.4, L(7), t_volta),
], padrao="gradiente_vivo", paleta="tomate", deriva=0, camada_dummy=None)
C(t_volta, "cretaceo", [
    B("pato", "bicodepato", "frente", 0.5, 0.36, 1.5, olhos="frente", expressao="feliz"),
    T("t20", "IGUAL!", 0.5, 0.17, 100, t_volta, fundo="#2E9E4A", rot=3),
    PIPO(0.9, 0.53, 0.4, t_volta, L(8)),
], luz="dia")

# ============================================================ 19-21: tensão (noite), folhas mexendo, pegadas, curtir
t_quem = W(8, "quem"); t_lado10 = W(8, "lado")
p1 = W(9, "passo", 0); p2 = W(9, "passo", 1)
noite = dict(luz="noite", paleta="noite", brilho=0.75)
C(L(8), "cretaceo", [
    B("f1", "bicodepato", "planta", 0.1, 0.43, 1.0, acoes=[dict(em=t_lado10, faz="treme", dur=0.9, forca=10)]),
    B("f2", "bicodepato", "planta", 0.26, 0.45, 0.8, acoes=[dict(em=t_lado10 + 0.15, faz="treme", dur=0.9, forca=12)]),
    B("pato", "bicodepato", "perfil", 0.6, 0.404, 1.0, olhos="frente", pose="bicando", expressao="neutro"),
    T("t21", "E QUEM CHEGA\nPELO LADO?", 0.5, 0.17, 68, t_quem, fundo="#1A0F24", rot=-2, soco=t_lado10),
    PIPO(0.9, 0.54, 0.4, L(8), L(9)),
], **noite)
C(L(9), "cretaceo", [
    B("pg1", "tiranossauro", "pegada", 0.1, 0.50, 0.7, alpha=0.9, acoes=[entra(p1, "cai", som=False)]),
    B("pg2", "tiranossauro", "pegada", 0.26, 0.50, 0.9, alpha=0.9, acoes=[entra(p2, "cai", som=False)]),
    B("rex", "tiranossauro", "perfil", 1.3, 0.40, 1.1, silhueta=True, espelha=True, alpha=0.75, anda=True,
      acoes=[dict(em=p1, faz="move", para=[0.93, 0.40], dur=round(L(10) - p1, 2), curva="linear")]),
    B("pato", "bicodepato", "perfil", 0.4, 0.404, 1.0, olhos="frente", pose="bicando", expressao="desconfiado"),
    T("t22", "PASSO...", 0.5, 0.17, 90, p1, fundo="#1A0F24", rot=-2, extra=[dict(em=p2, faz="muda", prop="texto", para="PASSO...\nPASSO...", som="pop3")]),
    PIPO(0.9, 0.54, 0.4, L(9), L(10)),
], acoes=[dict(em=p1, faz="treme", dur=0.4, forca=14), dict(em=p2, faz="treme", dur=0.5, forca=22)], **noite)
# ============================================================ 22: RUGIDO + estouro da Pipo
C(L(10), "cretaceo", [
    B("rex", "tiranossauro", "frente", 0.6, 0.36, 1.5, pose="rugindo", expressao="assustado", acoes=[entra(t_rugido, "pop", som=False)]),
    T("t24", "RUGIDO!", 0.5, 0.15, 110, t_rugido, fundo="#E8452C", rot=-4, soco=t_rugido + 0.3),
    PIPO(0.17, 0.52, 0.55, L(10), t_rugido, acoes=None) if False else dict(id="pipo", tipo="pipo", x=0.25, y=0.5, escala=0.7, sobrancelha=1.1, acoes=[
        dict(em=L(10) + 0.05, faz="olha", para="dir"), dict(em=t_rugido, faz="estoura", som="estouro")]),
], acoes=[dict(em=t_rugido, faz="flash"), dict(em=t_rugido, faz="treme", dur=0.7, forca=30), dict(em=t_rugido, faz="soco", forca=0.14)],
    luz="noite", paleta="noite", brilho=1.0)

# ============================================================ 23: bico-de-pato vira devagar, cara a cara, sorriso amarelo; grilo
t_virou = W(11, "virou"); t_dev = W(11, "devagar")
C(L(11), "cretaceo", [
    B("rex", "tiranossauro", "perfil", 0.3, 0.385, 1.3, expressao="neutro"),
    B("pato_p", "bicodepato", "perfil", 0.72, 0.42, 0.95, olhos="frente", pose="bicando", acoes=[dict(em=t_dev, faz="muda", prop="alpha", para=0.0, dur=0.5)]),
    B("pato_f", "bicodepato", "frente", 0.76, 0.40, 1.15, olhos="frente", alpha=0.0, expressao="assustado", olhar="esq", acoes=[
        dict(em=t_dev, faz="muda", prop="alpha", para=1.0, dur=0.5),
        dict(em=t_ah, faz="expressao", para="desconfiado"), dict(em=t_ah, faz="muda", prop="suor", para=True),
        dict(em=t_oi, faz="olha", para="camera")]),
    T("t25", "AH... OI.", 0.5, 0.17, 90, t_ah, fundo="#8E2F2A", rot=-3),
    PIPO(0.5, 0.56, 0.4, L(11), L(12), forma="pipoca"),
], acoes=[dict(em=t_oi - 0.04, faz="reacao", estilo="grilo", alvo="pato_f", dur=0.6)], luz="tarde")

# ============================================================ 26-27: SPLIT caçador x presa, paleta quente, aventura
t_ca = W(12, "cacador"); t_pre = W(12, "presa")
C(L(12), "chapado", [
    dict(id="sp", tipo="split", x=0.5, y=0.37, altura=780, meio="", tam_rotulo=56, paineis=[
        dict(cenario="cretaceo", luz="tarde", rotulo="CAÇADOR", cor_rotulo="#E8452C", rotulo_pos="baixo", foco=[0.5, 0.40], zoom=1.9, elementos=[
            B("r", "tiranossauro", "frente", 0.5, 0.40, 1.0, pose="ombros", expressao="julgando")]),
        dict(cenario="cretaceo", luz="tarde", rotulo="PRESA", cor_rotulo="#1F5FD1", rotulo_pos="baixo", foco=[0.5, 0.40], zoom=1.9, elementos=[
            B("p", "bicodepato", "frente", 0.5, 0.40, 1.0, olhos="lado", pose="bicando")])]),
    T("t28", "FRENTE  x  LADO", 0.5, 0.15, 76, W(12, "cacador"), fundo="#E8452C", rot=-2),
    PIPO(0.88, 0.55, 0.4, L(12), t_pre - 0.1, forma="pipoca"),
], padrao="formas", paleta="tomate", transicao="zoom_blur", energia=0.5, deriva=0)
t_s27 = round(t_pre - 0.12, 2)
C(t_s27, "chapado", [
    dict(id="sp", tipo="split", x=0.5, y=0.37, altura=780, meio="", tam_rotulo=56, paineis=[
        dict(cenario="bokeh", paleta="laranja", rotulo="CAÇADOR", cor_rotulo="#E8452C", rotulo_pos="baixo", foco=[0.5, 0.40], zoom=1.35, elementos=[
            B("r", "tiranossauro", "cima", 0.5, 0.48, 0.9, campo=70, alcance=380)]),
        dict(cenario="bokeh", paleta="rosa", rotulo="PRESA", cor_rotulo="#1F5FD1", rotulo_pos="baixo", foco=[0.5, 0.40], zoom=1.35, elementos=[
            B("p", "bicodepato", "cima", 0.5, 0.48, 0.9, olhos="lado", campo=300, alcance=340)])]),
    T("t29", "PRESA VÊ\nQUASE TUDO", 0.5, 0.15, 64, t_pre, fundo="#1F5FD1", rot=2),
    PIPO(0.88, 0.55, 0.4, t_s27, L(13), forma="pipoca"),
], padrao="gradiente_vivo", paleta="laranja", energia=0.6, deriva=0)

# ============================================================ 28-29: pombo pousa no T. rex; árvore de parentesco
t_pomb = W(13, "pombo"); t_primo = W(13, "primo")
C(L(13), "cretaceo", [
    B("rex", "tiranossauro", "frente", 0.5, 0.393, 1.2, expressao="neutro"),
    B("pb", "pombo", "frente", 0.95, 0.24, 0.36, olhos="lado", pose="voando", acoes=[
        dict(em=t_pomb, faz="move", para=[0.5, 0.228], dur=1.1, curva="suave"), dict(em=round(t_pomb + 1.1, 2), faz="pose", para="parado"),
        dict(em=round(t_pomb + 1.1, 2), faz="squash", som="pop2")]),
    T("t30", "O POMBO\nDA PARTE 1", 0.5, 0.15, 64, t_pomb, fundo="#1F5FD1", rot=-2),
    PIPO(0.15, 0.54, 0.4, L(13), t_primo - 0.1, forma="pipoca"),
], luz="tarde")
t_s29 = round(t_primo - 0.1, 2)
C(t_s29, "chapado", [
    dict(id="arv", tipo="icone", qual="arvore", x=0.5, y=0.50, acoes=[entra(t_s29, "pop", som=False)]),
    B("pb", "pombo", "frente", 0.287, 0.31, 0.65, olhos="lado", acoes=[entra(t_primo, "pop", som=True)]),
    B("rex", "tiranossauro", "frente", 0.713, 0.31, 0.65, acoes=[entra(t_primo + 0.25, "pop", som=True)]),
    T("t31", "PRIMOS", 0.5, 0.56, 72, t_primo + 0.3, fundo="#C2410C", rot=-2),
    T("t32", "AVES SÃO\nDINOSSAUROS", 0.5, 0.15, 64, t_primo, fundo="#5B2A86", rot=2, som=False),
    PIPO(0.5, 0.40, 0.4, t_s29, L(14), forma="pipoca"),
], padrao="gradiente_vivo", paleta="uva", deriva=0)

# ============================================================ 30-31: hoje ele é a caça; olho do lado vê o gato e voa
t_caca = W(14, "caca"); t_lado18 = W(14, "lado")
C(L(14), "rua", [
    B("pb", "pombo", "perfil", 0.62, 0.44, 1.0, olhos="lado", pose="bicando", acoes=[dict(em=W(14, "caca"), faz="olha", para="esq")]),
    B("gato", "gato", "perfil", 0.0, 0.45, 1.0, pose="agachado", expressao="desconfiado", acoes=[
        dict(em=L(14), faz="move", para=[0.3, 0.45], dur=2.4, curva="linear")]),
    T("t33", "HOJE ELE É\nA CAÇA", 0.5, 0.15, 68, W(14, "hoje"), fundo="#E8452C", rot=-2),
    PIPO(0.9, 0.26, 0.4, L(14), W(14, "por")),
], luz="tarde", paleta="mostarda")
t_s31 = round(W(14, "por") - 0.1, 2)
C(t_s31, "chapado", [
    B("gato", "gato", "cima", 0.92, 0.46, 0.7, acoes=[dict(em=t_s31, faz="move", para=[0.72, 0.46], dur=1.0, curva="linear")]),
    B("pb", "pombo", "cima", 0.45, 0.47, 1.0, olhos="lado", campo=340, alcance=450, acoes=[
        dict(em=t_lado18, faz="pose", para="voando", som="pop3"),
        dict(em=t_lado18, faz="move", para=[0.45, 0.05], dur=0.9, curva="rapido")]),
    T("t34", "POR ISSO:\nOLHO DO LADO", 0.5, 0.15, 64, W(14, "isso"), fundo="#2E9E4A", rot=2),
    PIPO(0.15, 0.30, 0.4, t_s31, L(15), forma="pipoca"),
], padrao="gradiente_vivo", paleta="menta", deriva=0)

# ============================================================ 32: lição, Pipo pipoca com lupa
C(L(15), "chapado", [
    dict(id="pipo", tipo="pipo", x=0.36, y=0.42, escala=0.95, forma="pipoca", boca="sorriso", acoes=[
        entra(L(15), "pop", som=False), dict(em=W(15, "sobreviv"), faz="pula", altura=50)]),
    dict(id="lupa", tipo="icone", qual="lupa", x=0.68, y=0.40, escala=1.2, acoes=[
        entra(L(15) + 0.15, "pop", som=True), dict(em=W(15, "onde"), faz="move", para=[0.6, 0.38], dur=0.8)]),
    T("t35", "CADA OLHO NO\nSEU LUGAR", 0.5, 0.15, 72, W(15, "cada"), fundo="#1F5FD1", rot=-2, soco=W(15, "mandou")),
], padrao="formas", paleta="menta", energia=0.4, deriva=0)

# ============================================================ 33-34: E a gente? (gancho da parte 3): interrogação e silhueta de macaco
t_gente = W(16, "gente"); t_nosso = W(16, "nosso")
C(L(16), "chapado", [
    T("q", "?", 0.5, 0.36, 560, L(16) + 0.1, cor="#FFC21A", soco=t_gente, extra=[dict(em=t_gente, faz="pula", altura=40)]),
    dict(id="pipo", tipo="pipo", x=0.84, y=0.52, escala=0.4, forma="pipoca", boca="o", acoes=[
        entra(L(16) + 0.2, "pop", som=False), dict(em=t_gente + 0.2, faz="squash")]),
], padrao="ceu", ceu="noite", paleta="noite", deriva=0)
t_s34 = round(W(16, "por") - 0.05, 2)
C(t_s34, "chapado", [
    dict(id="mac", tipo="icone", qual="macaco", x=0.5, y=0.45, escala=1.4, acoes=[entra(t_s34, "desliza_dir", som=True)]),
    T("q2", "?", 0.82, 0.27, 240, t_nosso, cor="#FFC21A", extra=[dict(em=W(16, "frente"), faz="soco")]),
    T("t36", "E O NOSSO\nOLHO?", 0.38, 0.17, 68, t_nosso, fundo="#1F5FD1", rot=-2),
    PIPO(0.15, 0.5, 0.4, t_s34, L(17), forma="pipoca"),
], padrao="ceu", ceu="tarde", paleta="laranja", deriva=0)

# ============================================================ 35-36: CAÇADOR ou PRESA? + Pipo pipoca apontando
t_cacf = W(17, "cacador"); t_qual = W(17, "qual"); t_com = W(17, "comenta"); t_tres = W(17, "tres")
C(L(17), "chapado", [
    dict(id="b1", tipo="bloco", x=0.27, y=0.32, largura=400, altura=150, cor="#E8452C", texto="CAÇADOR", tam=60, acoes=[entra(round(L(17) - 0.3, 2), "pop", som=False)]),
    dict(id="b2", tipo="bloco", x=0.73, y=0.32, largura=400, altura=150, cor="#1F5FD1", texto="PRESA", tam=60, acoes=[entra(W(17, "presa"), "pop", som=True)]),
    B("rex", "tiranossauro", "frente", 0.25, 0.47, 0.75, acoes=[entra(round(L(17) - 0.3, 2), "pop", som=False)]),
    B("pato", "bicodepato", "frente", 0.75, 0.47, 0.75, olhos="lado", acoes=[entra(W(17, "presa") + 0.1, "pop", som=False)]),
    T("t37", "QUAL VOCÊ\nSERIA?", 0.5, 0.15, 68, t_qual, fundo="#1A0F24", rot=-2),
    dict(id="pipo", tipo="pipo", x=0.5, y=0.52, escala=0.5, forma="pipoca", boca="sorriso", acoes=[
        entra(round(L(17) - 0.3, 2), "pop", som=False), dict(em=t_qual, faz="pula", altura=30)]),
], padrao="gradiente_vivo", paleta="mostarda", deriva=0)
C(round(t_com - 0.08, 2), "chapado", [
    T("t38", "PARTE 3 VEM AÍ", 0.5, 0.15, 68, t_tres, fundo="#E8452C", rot=-2),
    dict(id="c1", tipo="comentario", x=0.5, y=0.44, nome="@tio_da_picanha", texto="caçador, claro!", largura=560, cor_avatar="#E8452C",
         acoes=[entra(round(t_com + 0.35, 2), "desliza_dir", som=True)]),
    dict(id="c2", tipo="comentario", x=0.5, y=0.53, nome="@pombo_da_praca", texto="presa, e voo!", largura=560, cor_avatar="#1F5FD1",
         acoes=[entra(round(t_com + 1.3, 2), "desliza_esq", som=True)]),
    dict(id="pipo", tipo="pipo", x=0.5, y=0.30, escala=0.7, forma="pipoca", boca="sorriso", pose="apontando", aponta_para=[0, 400], acoes=[
        entra(round(t_com - 0.08, 2), "pop", som=False), dict(em=t_com + 0.3, faz="pula", altura=30)]),
], padrao="gradiente_vivo", paleta="uva", deriva=0)

# ---------------------------------------------------------------- fecha: limpeza do que o motor não conhece
for c in cenas:
    c.pop("camada_dummy", None)

# ---------------------------------------------------------------- som
FILE = lambda p: "assets/" + p
VIAGEM = FILE("musica/a-mystery-travel/mystery_travel.mp3")
MISTERIO = FILE("musica/cc0-mystery/mystery%20exploration.mp3")
AVENT = FILE("musica/adventure-intro-title-cinematic-epic/Adventure%20Theme%20Intro.wav")
t_mist = L(8); t_estouro = t_rugido
t_aventura = L(12); t_gancho = L(16)
sfx = []
# música: viagem de abertura (clima "mundo antigo"); mistério só na tensão; silêncio antes do rugido; aventura na virada; viagem no gancho
sfx.append([[MISTERIO, 4.0, round(t_rugido - 0.42 - t_mist, 2), 0.5], t_mist, 0.11])
sfx.append([[AVENT, 13.0, round(t_gancho - t_aventura, 2), 0.5], t_aventura, 0.14])
sfx.append([[VIAGEM, 62.0, round(TOTAL + 0.1 - t_gancho, 2), 0.5], t_gancho, 0.13])
# rugido audível no celular + risers
sfx.append([FILE("sfx/memes/riser.ogg"), round(t_rugido - 2.07, 2), 0.6])
sfx.append([["assets/sfx/cc0-deep-monster-roar/monster_roar.wav", 0.15, 1.8, 0.5], t_rugido, 0.95])
sfx.append([FILE("sfx/75-cc0-breaking-falling-hit-sfx/bfh1_hit_07.ogg"), t_rugido, 0.7])
# passos e pulso na tensão
for tt, f in ((p1, "footstep_01"), (p2, "footstep_02")):
    sfx.append([FILE(f"sfx/100-cc0-sfx-2/sfx100v2_{f}.ogg"), tt, 0.7])
    sfx.append([FILE("sfx/75-cc0-breaking-falling-hit-sfx/bfh1_hit_03.ogg"), tt, 0.5])
for k, tt in enumerate((t_rugido - 2.6, t_rugido - 1.95, t_rugido - 1.3)):
    sfx.append([FILE("sfx/pop-sounds/pop7.ogg"), tt, 0.35])
# sons de bicho e de entrada
sfx.append([FILE("sfx/olhos-cc0/pombo.ogg"), t_pomb + 0.9, 0.4])
sfx.append([FILE("sfx/olhos-cc0/asas.ogg"), t_lado18, 0.6])
sfx.append([FILE("sfx/olhos-cc0/miado.ogg"), t_caca + 0.8, 0.4])
sfx.append([FILE("sfx/memes/boing.ogg"), t_ligou, 0.45])
sfx.append([FILE("sfx/memes/apito_sobe.ogg"), t_olho2 + 0.3, 0.35])
sfx.append([FILE("sfx/100-cc0-sfx-2/sfx100v2_hit_02.ogg"), t_regra, 0.5])
sfx.append([FILE("sfx/80-cc0-creature-sfx/eat_01.ogg"), L(0) + 1.2, 0.5])
sfx.append([FILE("sfx/memes/ohh.ogg"), t_primo + 0.6, 0.35])
sfx.append([FILE("sfx/memes/dundun.ogg"), t_quem - 0.1, 0.45])
sfx.append([FILE("sfx/80-cc0-creature-sfx/cute_03.ogg"), L(7) + 0.3, 0.5])
sfx.append([FILE("sfx/memes/errado.ogg"), t_s31 + 0.05, 0.3])
sfx.append([FILE("sfx/memes/risada.ogg"), t_oi + 1.2, 0.3])
# whoosh nos cortes (manual: o automático cairia dentro do silêncio do rugido)
WH = FILE("sfx/air-whoosh/whoosh_1passada.ogg")
for c in cenas[1:]:
    t = c["em"] if isinstance(c["em"], (int, float)) else None
    if t is None or abs(t - L(10)) < 0.05 or abs(t - L(11)) < 0.05:
        continue
    sfx.append([WH, round(t - 0.12, 2), 0.2])

d = dict(paleta="mostarda", musica="viagem", musica_inicio=6, whoosh_nos_cortes=False, volume_whoosh=0.22,
         silencios=[[round(t_mist - 0.03, 2), round(TOTAL + 1, 2)]], sfx=sfx, cauda=0.08, cenas=cenas)
json.dump(d, open(f"{WORK}/cenas.json", "w"), ensure_ascii=False, indent=1)
print("cenas:", len(cenas), "| cortes:", [c["em"] for c in cenas])
