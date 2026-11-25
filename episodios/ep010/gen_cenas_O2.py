"""Gerador do cenas.json (só visual) do ep010 H. O2 Cenário, 25/11/2026.
Uso: python3 gen_cenas_O2.py  (grava cenas.json ao lado). Sem chaves de som: o O3 escreve som.json."""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
N = 31
L = lambda n: round(n / N, 4)          # luzes da casa = n/31
AMARELO, VERMELHO = "#FFC21A", "#E8452C"

ANA = dict(tipo="humano", idade="adulto", cabelo="rabo_de_cavalo", cabelo_cor="castanho_escuro", pele="morena",
           olheiras=True, roupa="#5B6C8F", manga="longa", segura="celular")
AVO = dict(tipo="humano", idade="idoso", cabelo="coque", cabelo_cor="branco", pele="media", avental=True,
           oculos=True, oculos_tipo="redondo", expressao="feliz")


def ana(**kw):
    d = dict(ANA, id="ana"); d.update(kw); return {k: v for k, v in d.items() if v is not None}


def avo(**kw):
    d = dict(AVO, id="avo"); d.update(kw); return d


def suf(n):
    return " LÂMPADA" if n == 1 else " LÂMPADAS"


def cont(n, acoes=(), y=0.155, cor=AMARELO, **kw):
    d = dict(id="cont", tipo="contador", x=0.33, y=y, valor=n, sufixo=suf(n), tam=68, cor=cor, acoes=list(acoes)); d.update(kw); return d


def data(txt, acoes=(), y=0.155):
    return dict(id="data", tipo="texto", x=0.80, y=y, texto=txt, tam=60, fundo="#1D1B3A", cor="#FFF3E0", acoes=list(acoes))


def casa(n, x=0.5, y=0.42, escala=1.0, acoes=(), id="casa_ana", **kw):
    d = dict(id=id, tipo="casa", x=x, y=y, escala=escala, luzes=L(n), acoes=list(acoes)); d.update(kw); return d


def queda(de, para, em, dur=0.18, ate=None):
    """Mesma curva e mesmo tempo para a casa e o contador: o número nunca desencontra das lâmpadas."""
    t = {"em": em, "curva": "linear"}
    if ate:
        t["ate"] = ate
    else:
        t["dur"] = dur
    a_casa = dict(t, faz="muda", prop="luzes", para=L(para))
    a_cont = [dict(t, faz="conta", para=para)]
    if suf(de) != suf(para):   # singular/plural troca quando o número chega
        a_cont.append({"em": em, "depois": round(dur if para == 1 else dur / 2, 3), "faz": "muda", "prop": "sufixo", "para": suf(para)} if not ate
                      else {"em": ate, "faz": "muda", "prop": "sufixo", "para": suf(para)})
    return a_casa, a_cont


def pipo(x, y, esc, acoes, **kw):
    d = dict(id="pipo", tipo="pipo", x=x, y=y, escala=esc, acoes=acoes); d.update(kw); return d


def tit(txt, y=0.255, tam=84, em=None, acoes=None, **kw):
    a = acoes if acoes is not None else ([{"em": em, "faz": "entra", "jeito": "pop"}] if em is not None else [])
    d = dict(id="tit", tipo="texto", x=0.5, y=y, texto=txt, tam=tam, cor=AMARELO, acoes=a); d.update(kw); return d


cenas = []

# C1 0-3,00: rua à noite, a casa do meio apaga
c_apaga, n_apaga = queda(1, 0, "apagou", 0.15)
PISCA_FRACO = [{"em": t, "faz": "muda", "prop": "luzes", "para": v, "dur": 0.06} for t, v in
               ((0.35, 0.012), (0.5, L(1)), (0.95, 0.008), (1.08, L(1)), (1.55, 0.014), (1.62, L(1)), (1.9, 0.01), (2.0, L(1)))]
cenas.append({"em": 0, "cenario": "rua", "luz": "noite", "paleta": "cobalto", "chuva": True, "brilho": 0.6, "elementos": [
    casa(31, x=0.17, y=0.43, escala=0.58, id="casa_e", cor="#E9A23B", camada="topo", acoes=[{"em": 0, "faz": "pisca", "brilho": True, "ritmo": 1.4, "dur": 3, "cor": "#FFD98A"}]),
    casa(31, x=0.83, y=0.43, escala=0.58, id="casa_d", cor="#3FA37A", camada="topo", acoes=[{"em": 0.4, "faz": "pisca", "brilho": True, "ritmo": 1.2, "dur": 3, "cor": "#FFD98A"}]),
    casa(1, x=0.5, y=0.43, escala=0.66, cor="#8A7FA8", acoes=PISCA_FRACO + [c_apaga, {"em": "apagou", "faz": "treme", "dur": 0.5, "forca": 10}]),
    pipo(0.5, 0.52, 0.5, [{"em": 0, "faz": "olha", "para": "cima"}, {"em": "Ana", "faz": "squash"},
                             {"em": "unica", "faz": "olha", "para": "camera"}, {"em": "apagou", "faz": "pula", "altura": 40},
                             {"em": "apagou", "faz": "boca", "para": "o"}], sobrancelha=1.1),
    tit("SÓ A DELA APAGOU", y=0.26, tam=82),
    cont(1, n_apaga + [{"em": "apagou", "faz": "muda", "prop": "cor", "para": VERMELHO}, {"em": "apagou", "faz": "soco"}]),
    data("24 DEZ"),
], "acoes": [{"em": "apagou", "faz": "treme", "forca": 10, "dur": 0.3}]})

# C2 linha1 3,00-4,82: a conta de luz está paga
cenas.append({"em": "linha1", "cenario": "cozinha", "luz": "noite", "paleta": "petroleo", "chuva": True, "elementos": [
    dict(id="conta", tipo="bloco", x=0.5, y=0.36, largura=640, altura=420, cor="#FFF3E0", cor_texto="#1D1B3A", texto="CONTA DE LUZ", tam=76,
         rot=-4, acoes=[{"em": "linha1", "faz": "entra", "jeito": "desliza_esq"}, {"em": "conta", "faz": "soco"}]),
    dict(id="carimbo", tipo="carimbo", x=0.55, y=0.45, texto="PAGA", cor="#16A57A", tam=120, inclina=-12, pode_sobrepor=True,
         acoes=[{"em": "luz", "faz": "entra", "jeito": "pop"}, {"em": "luz", "depois": 0.3, "faz": "treme", "dur": 0.25, "forca": 8}]),
    tit("NÃO FOI ISSO", y=0.2, tam=80, em="nao"),
]})

# C3 linha2 4,82-7,82: a árvore apagada, 1882
cenas.append({"em": "linha2", "cenario": "chapado", "padrao": "luzes", "paleta": "uva", "energia": 0.4, "transicao": "wipe_diagonal", "elementos": [
    dict(id="arv", tipo="arvore_natal", x=0.42, y=0.41, altura=560, luzes=0, luz="noite", acoes=[{"em": "eletrica", "faz": "treme", "dur": 0.3, "forca": 6}]),
    pipo(0.8, 0.5, 0.6, [{"em": "primeira", "faz": "pula", "altura": 30}, {"em": "eletrica", "faz": "olha", "para": "esq"},
                          {"em": "noticia", "faz": "sobrancelha", "para": 1.2}, {"em": "noticia", "faz": "squash"}]),
    tit("A PRIMEIRA COM\nLUZ ELÉTRICA", y=0.18, tam=78, em="primeira"),
]})

# C4 "acendeu" 7,82-10,02: a árvore acende, 1882
cenas.append({"em": "acendeu", "cenario": "chapado", "padrao": "bokeh", "paleta": "noite", "elementos": [
    dict(id="arv", tipo="arvore_natal", x=0.42, y=0.41, altura=560, luzes=0, luz="noite", camada="topo",
         acoes=[{"em": "acendeu", "faz": "muda", "prop": "luzes", "para": 1, "dur": 0.5}, {"em": "acendeu", "faz": "squash"},
                {"em": "dois", "faz": "pisca", "brilho": True, "dur": 0.6, "cor": "#FFD98A"}]),
    pipo(0.8, 0.5, 0.6, [{"em": "acendeu", "faz": "pula", "altura": 50}, {"em": "acendeu", "faz": "boca", "para": "o"},
                          {"em": "oitocentos", "faz": "olha", "para": "cima"}, {"em": "dois", "faz": "boca", "para": "sorriso"}], sobrancelha=1.0),
    tit("1882", y=0.19, tam=190, em="oitocentos", acoes=[{"em": "oitocentos", "faz": "entra", "jeito": "pop"}, {"em": "dois", "faz": "soco"}]),
]})

# C5 "Nova" 10,02-12,77: Nova York, 80 lâmpadas
cenas.append({"em": "Nova", "cenario": "chapado", "padrao": "cidade", "paleta": "petroleo", "elementos": [
    dict(id="arv", tipo="arvore_natal", x=0.33, y=0.42, altura=520, luzes=1, luz="noite", camada="topo",
         acoes=[{"em": "oitenta#2", "faz": "pisca", "brilho": True, "dur": 1.0, "cor": "#FFD98A"}]),
    dict(id="cont80", tipo="contador", x=0.74, y=0.40, valor=0, tam=170, cor="#38D1C6",
         acoes=[{"em": "oitenta#2", "faz": "conta", "para": 80, "ate": "oitenta#2", "curva": "rapido"}, {"em": "lampadas", "faz": "soco"}]),
    tit("NOVA YORK", y=0.2, tam=100, em="Nova"),
]})

# C6 linha4 12,77-15,06: a regra em ação (lâmpada gigante balançando)
import math


def lampada(t0, t1, apaga=None, amp=6.0, per=0.9):
    """Lâmpada gigante de blocos: o fio tem o centro no topo da tela (girar = pêndulo); soquete, halo e bulbo
    acompanham com move + gira no mesmo tempo e curva. apaga: segundo em que ela apaga (cor cinza, halo some, faísca)."""
    partes = [("lamp_fio", 0, dict(tipo="bloco", largura=14, altura=900, cor="#1D1B3A", raio=7)),
              ("lamp_halo", 640, dict(tipo="bloco", largura=430, altura=430, raio=215, cor="#FFF3B0", alpha=0.35)),
              ("lamp_soq", 490, dict(tipo="bloco", largura=120, altura=100, cor="#8A8FA8", raio=14)),
              ("lamp", 640, dict(tipo="bloco", largura=250, altura=250, raio=125, cor="#FFE14D"))]
    els = []
    for pid, r, d in partes:
        acs = []
        t, k = t0, 0
        while t < t1:
            th = amp * (1 if k % 2 == 0 else -1) * (1.6 if apaga and t >= apaga else 1.0)
            acs.append({"em": round(t, 3), "faz": "gira", "para": th, "dur": per})
            if r:
                acs.append({"em": round(t, 3), "faz": "move", "para": [round(0.5 - r * math.sin(math.radians(th)) / 1080, 4),
                                                                      round(r * math.cos(math.radians(th)) / 1920, 4)], "dur": per})
            t += per; k += 1
        if apaga and pid == "lamp":
            acs += [{"em": apaga, "faz": "pisca", "brilho": True, "dur": 0.3, "cor": "#FFFFFF"},
                    {"em": apaga, "depois": 0.12, "faz": "muda", "prop": "cor", "para": "#5B5670"},
                    {"em": apaga, "faz": "treme", "dur": 0.4, "forca": 14}]
        if apaga and pid == "lamp_halo":
            acs.append({"em": apaga, "depois": 0.12, "faz": "muda", "prop": "alpha", "para": 0, "dur": 0.08})
        e = dict(d, id=pid, x=0.5, y=round(r / 1920, 4), pode_sobrepor=True, acoes=acs)
        if pid == "lamp_fio":
            e["y"] = 0.0
        els.append(e)
    return els


cenas.append({"em": "linha4", "cenario": "chapado", "padrao": "bokeh", "paleta": "noite", "chuva": True, "transicao": "zoom_blur", "elementos":
    lampada(12.77, 15.06, amp=5) + [
    pipo(0.76, 0.52, 0.7, [{"em": "imagina", "faz": "olha", "para": "cima"}, {"em": "mundo", "faz": "squash"},
                            {"em": "regra", "faz": "sobrancelha", "para": 1.2}, {"em": "regra", "faz": "pula", "altura": 25}]),
    dict(id="carimbo", tipo="carimbo", x=0.40, y=0.49, texto="UMA REGRA:", cor="#FF5A3C", tam=86, inclina=-10,
         acoes=[{"em": "regra", "faz": "entra", "jeito": "pop"}, {"em": "regra", "depois": 0.3, "faz": "treme", "dur": 0.25, "forca": 8}]),
]})

# C7 linha5 15,06-17,16: celular "depois eu te ligo" sem resposta
cenas.append({"em": "linha5", "cenario": "celular", "paleta": "cobalto", "hora": "19:42", "elementos": [
    dict(id="bal", tipo="comentario", x=0.5, y=0.3, nome="você", texto="depois eu te ligo", largura=600, cor_avatar="#FFC21A",
         acoes=[{"em": "depois", "faz": "entra", "jeito": "desliza_dir"}]),
    dict(id="sem", tipo="texto", x=0.5, y=0.45, texto="(e não ligou)", tam=66, cor="#EAF0FF", acoes=[{"em": "nao", "faz": "entra", "jeito": "pop"}]),
    pipo(0.78, 0.56, 0.5, [{"em": "ligo", "faz": "olha", "para": "cima"}, {"em": "voce", "faz": "squash"},
                            {"em": "cumpre", "faz": "sobrancelha", "para": 1.2}, {"em": "cumpre", "faz": "boca", "para": "reta"}]),
]})

# C8 "apaga" 17,16-19,18: a lâmpada gigante apaga na hora
cenas.append({"em": "apaga", "cenario": "chapado", "padrao": "bokeh", "paleta": "petroleo", "chuva": True, "elementos":
    lampada(17.16, 19.18, apaga=17.22, amp=5) + [
    pipo(0.76, 0.52, 0.7, [{"em": "apaga", "depois": 0.1, "faz": "pula", "altura": 110}, {"em": "apaga", "depois": 0.1, "faz": "boca", "para": "o"},
                            {"em": "apaga", "depois": 0.1, "faz": "palpebra", "para": 0}, {"em": "apaga", "depois": 0.1, "faz": "sobrancelha", "para": 1.2},
                            {"em": "lampada", "faz": "squash", "forca": 0.3}, {"em": "casa", "faz": "olha", "para": "camera"}], olhar="cima"),
    dict(id="menos1", tipo="texto", x=0.3, y=0.47, texto="-1 LÂMPADA", tam=80, cor="#FF5A3C", acoes=[{"em": "lampada", "faz": "entra", "jeito": "pop"}]),
], "acoes": [{"em": "apaga", "depois": 0.12, "faz": "treme", "forca": 16, "dur": 0.35}, {"em": "apaga", "depois": 0.12, "faz": "brilho", "para": 0.55, "dur": 0.15}]})

# C9 linha6 19,18-21,64: Ana na porta da casa dela, 31
cenas.append({"em": "linha6", "cenario": "rua", "luz": "noite", "paleta": "cobalto", "chuva": True, "elementos": [
    casa(31, x=0.5, y=0.40, escala=1.2, acoes=[{"em": "trinta", "faz": "pisca", "brilho": True, "dur": 0.8, "cor": "#FFD98A"}]),
    ana(x=0.6, y=0.47, escala=0.6, olhar="camera", expressao="neutro",
        acoes=[{"em": "comecou", "faz": "olha", "para": "cima"}, {"em": "trinta", "faz": "expressao", "para": "feliz"},
               {"em": "trinta", "faz": "pula", "altura": 20}, {"em": "uma", "faz": "olha", "para": "camera"}]),
    cont(31, [{"em": "trinta", "faz": "soco"}]),
    data("1º DEZ", [{"em": "dezembro", "faz": "entra", "jeito": "pop"}]),
]})

# C10 21,64-23,07: close na casa com as 31 acesas
cenas.append({"em": 21.64, "cenario": "chapado", "padrao": "ceu", "ceu": "noite", "paleta": "uva", "chuva": True, "elementos": [
    casa(31, x=0.5, y=0.44, escala=1.4, acoes=[{"em": "uma#4", "faz": "pisca", "brilho": True, "dur": 1.3, "cor": "#FFD98A"}, {"em": "dia", "faz": "squash"}]),
    tit("UMA PRA CADA DIA", y=0.255, tam=76, em="uma#4"),
    cont(31, [{"em": "cada", "faz": "soco"}]),
    data("1º DEZ"),
]})

# C11 linha7 23,07-24,67: quarto, áudio da amiga
cenas.append({"em": "linha7", "cenario": "quarto", "luz": "noite", "paleta": "noite", "chuva": True, "elementos": [
    ana(ancora="cama", pose="sentado", assento=False, olhar="celular", expressao="cansado",
        acoes=[{"em": "audio", "faz": "olha", "para": "camera"}, {"em": "mandou", "faz": "squash", "forca": 0.12}]),
    dict(id="bal", tipo="comentario", x=0.5, y=0.29, nome="amiga", texto="áudio de 4 min", largura=560, cor_avatar="#FF5A8A",
         acoes=[{"em": "mandou", "faz": "entra", "jeito": "desliza_dir"}]),
    cont(31), data("3 DEZ"),
]})

# C12 "depois#2" 24,67-26,75: depois eu te ligo, 30
c, n = queda(31, 30, "trinta#2")
cenas.append({"em": "depois#2", "cenario": "chapado", "padrao": "ceu", "ceu": "noite", "paleta": "cobalto", "chuva": True, "elementos": [
    casa(31, x=0.5, y=0.43, escala=1.15, acoes=[c, {"em": "trinta#2", "faz": "treme", "dur": 0.35, "forca": 8}]),
    dict(id="bal", tipo="comentario", x=0.5, y=0.285, nome="Ana", texto="depois eu te ligo", largura=600, cor_avatar="#5B6C8F",
         acoes=[{"em": "depois#2", "faz": "entra", "jeito": "pop"}]),
    ana(x=0.8, y=0.47, escala=0.5, olhar="celular", expressao="cansado", acoes=[{"em": "ligo#2", "faz": "olha", "para": "cima"}, {"em": "trinta#2", "faz": "expressao", "para": "surpreso"}]),
    cont(31, n + [{"em": "trinta#2", "faz": "soco"}]), data("3 DEZ"),
]})

# C13 linha8 26,75-28,62: cozinha, "e a ceia?"
cenas.append({"em": "linha8", "cenario": "cozinha", "luz": "noite", "paleta": "petroleo", "chuva": True, "transicao": "papel", "elementos": [
    ana(ancora="balcao", olhar="celular", expressao="cansado", acoes=[{"em": "ceia", "faz": "olha", "para": "camera"}, {"em": "perguntou", "faz": "squash", "forca": 0.12}]),
    dict(id="bal", tipo="comentario", x=0.5, y=0.29, nome="irmão", texto="e a ceia?", largura=520, cor_avatar="#38D1C6",
         acoes=[{"em": "perguntou", "faz": "entra", "jeito": "desliza_esq"}]),
    cont(30), data("9 DEZ"),
]})

# C14 "depois#3" 28,62-31,05: depois eu te ligo, 29
c, n = queda(30, 29, "nove")
cenas.append({"em": "depois#3", "cenario": "rua", "luz": "noite", "paleta": "noite", "chuva": True, "elementos": [
    casa(30, x=0.5, y=0.42, escala=1.15, acoes=[c, {"em": "nove", "faz": "treme", "dur": 0.35, "forca": 8}]),
    dict(id="bal", tipo="comentario", x=0.5, y=0.285, nome="Ana", texto="depois eu te ligo", largura=600, cor_avatar="#5B6C8F",
         acoes=[{"em": "depois#3", "faz": "entra", "jeito": "pop"}]),
    ana(x=0.2, y=0.47, escala=0.5, olhar="celular", expressao="cansado", acoes=[{"em": "Vinte", "faz": "olha", "para": "cima"}, {"em": "nove", "faz": "expressao", "para": "triste"}]),
    cont(30, n + [{"em": "nove", "faz": "soco"}]), data("9 DEZ"),
]})

# C15 linha9 31,05-32,36: PRAZO e REUNIÃO carimbando, 29 -> 15
c, n = queda(29, 15, "Prazo", ate="reuniao")
cenas.append({"em": "linha9", "cenario": "chapado", "padrao": "cidade", "paleta": "uva", "chuva": True, "elementos": [
    casa(29, x=0.5, y=0.43, escala=1.0, acoes=[c]),
    dict(id="carimbo", tipo="carimbo", x=0.36, y=0.36, texto="PRAZO", cor=VERMELHO, tam=110, inclina=-14, pode_sobrepor=True,
         acoes=[{"em": "Prazo", "faz": "entra", "jeito": "pop"}, {"em": "Prazo", "depois": 0.3, "faz": "treme", "dur": 0.25, "forca": 8}]),
    dict(id="carimbo2", tipo="carimbo", x=0.62, y=0.49, texto="REUNIÃO", cor="#FFC21A", tam=100, inclina=9, pode_sobrepor=True,
         acoes=[{"em": "reuniao", "faz": "entra", "jeito": "pop"}, {"em": "reuniao", "depois": 0.3, "faz": "treme", "dur": 0.25, "forca": 8}]),
    cont(29, n), data("16 DEZ"),
]})

# C16 32,36-34,91: split ANA x RUA, 15 -> 1 em "ela"
c, n = queda(15, 1, 32.36, dur=34.10 - 32.36)
cenas.append({"em": 32.36, "cenario": "chapado", "padrao": "chuva", "paleta": "petroleo", "elementos": [
    dict(id="sp", tipo="split", x=0.5, y=0.39, altura=780, paineis=[
        {"cenario": "ceu", "ceu": "noite", "paleta": "petroleo", "rotulo": "ANA", "rotulo_pos": "baixo", "chuva": True, "brilho": 0.7, "foco": [0.5, 0.45],
         "elementos": [casa(15, x=0.5, y=0.45, escala=1.1, acoes=[c])]},
        {"cenario": "casa_natal_fora", "paleta": "petroleo", "rotulo": "RUA", "rotulo_pos": "baixo", "foco": [0.72, 0.5],
         "acoes": [{"em": "brilhando", "faz": "brilho", "para": 1.4, "dur": 0.3}],
         "elementos": [dict(id="viz", tipo="humano", preset="vizinho_exagerado", ancora="quintal_dir", pose="comemorando",
                            acoes=[{"em": "brilhando", "faz": "pula", "altura": 40}, {"em": "menos", "faz": "squash"}])]}]),
    cont(15, n + [{"em": "ela", "faz": "soco"}], y=0.14),
    data("16 DEZ", [{"em": "ela", "faz": "muda", "prop": "texto", "para": "23 DEZ"}], y=0.14),
]})

# C17 linha10 34,91-37,12: véspera, sobrou uma
cenas.append({"em": "linha10", "cenario": "chapado", "padrao": "ceu", "ceu": "noite", "paleta": "cobalto", "chuva": True, "chuva_forca": 1.8, "elementos": [
    casa(1, x=0.5, y=0.43, escala=1.4, acoes=[dict(a, em=round(34.91 + a["em"], 2)) for a in PISCA_FRACO] +
         [dict(a, em=round(36.0 + a["em"] * 0.5, 2)) for a in PISCA_FRACO] + [{"em": "sobrou", "faz": "treme", "dur": 0.4, "forca": 4}]),
    pipo(0.2, 0.56, 0.5, [{"em": "Natal", "faz": "squash"}, {"em": "sobrou", "faz": "sobrancelha", "para": 1.2},
                           {"em": "uma", "faz": "boca", "para": "triste"}, {"em": "uma", "faz": "pula", "altura": 15}], olhar="cima", boca="reta"),
    cont(1, [{"em": "uma", "faz": "soco"}]), data("24 DEZ", [{"em": "vespera", "faz": "entra", "jeito": "pop"}]),
]})

# C18 linha11 37,12-38,91: celular vibrando no criado-mudo
cenas.append({"em": "linha11", "cenario": "quarto", "luz": "noite", "paleta": "petroleo", "chuva": True, "elementos": [
    ana(ancora="cama", pose="sentado", assento=False, segura=None, olhar="dir", expressao="cansado",
        acoes=[{"em": "mensagem", "faz": "olha", "para": "dir"}, {"em": "avo", "faz": "expressao", "para": "surpreso"}]),
    dict(id="cel", tipo="celular", x=0.8, y=0.47, escala=0.28, rot=80, tela="texto", linhas=["VÓ"], cor_tela="#2747C9", pode_sobrepor=True,
         acoes=[{"em": "chegou", "faz": "treme", "dur": 0.5, "forca": 10}, {"em": "mensagem", "faz": "treme", "dur": 0.5, "forca": 10},
                {"em": "avo", "faz": "treme", "dur": 0.5, "forca": 10}, {"em": "chegou", "faz": "pisca", "brilho": True, "dur": 1.6, "cor": "#9FC3FF"}]),
    cont(1), data("24 DEZ"),
]})

# C19 38,91-40,83: a mensagem da avó, 21:17
cenas.append({"em": 38.91, "cenario": "celular", "paleta": "uva", "hora": "21:17", "elementos": [
    dict(id="bal", tipo="comentario", x=0.5, y=0.34, nome="Vó", texto="me liga quando puder, filha", largura=780, cor_avatar="#FF5A8A",
         acoes=[{"em": "me", "faz": "entra", "jeito": "pop"}, {"em": "filha", "faz": "treme", "dur": 0.3, "forca": 6}]),
    dict(id="hora", tipo="texto", x=0.5, y=0.245, texto="21:17", tam=70, cor="#F3E8FF", acoes=[{"em": "me", "faz": "entra", "jeito": "pop"}]),
    pipo(0.8, 0.53, 0.5, [{"em": "liga", "faz": "olha", "para": "cima"}, {"em": "puder", "faz": "squash"}, {"em": "filha", "faz": "boca", "para": "triste"}]),
    cont(1), data("24 DEZ"),
]})

# C20 linha12 40,83-42,02: close da Ana digitando
cenas.append({"em": "linha12", "cenario": "quarto", "luz": "noite", "paleta": "noite", "chuva": True, "zoom": 1.05, "elementos": [
    ana(x=0.5, y=0.47, escala=1.2, olhar="celular", expressao="triste", acoes=[{"em": "digitou", "faz": "squash", "forca": 0.1}, {"em": "Ana", "faz": "olha", "para": "celular"}]),
    cont(1), data("24 DEZ"),
]})

# C21 "depois#4" 42,02-43,90: enviada; em "ligo#4" a última apaga, 0 vermelho, brilho 0,08
c, n = queda(1, 0, "ligo#4", 0.15)
cenas.append({"em": "depois#4", "cenario": "celular", "paleta": "cobalto", "hora": "21:18", "elementos": [
    dict(id="bal", tipo="comentario", x=0.5, y=0.29, nome="Ana", texto="depois eu te ligo", largura=600, cor_avatar="#5B6C8F",
         acoes=[{"em": "depois#4", "faz": "entra", "jeito": "desliza_dir"}]),
    dict(id="sem", tipo="texto", x=0.68, y=0.365, texto="enviada", tam=50, cor="#EAF0FF", acoes=[{"em": "te#4", "faz": "entra", "jeito": "pop"}]),
    casa(1, x=0.5, y=0.48, escala=0.6, acoes=[c, {"em": "ligo#4", "faz": "treme", "dur": 0.5, "forca": 10}]),
    cont(1, n + [{"em": "ligo#4", "faz": "muda", "prop": "cor", "para": VERMELHO}, {"em": "ligo#4", "faz": "soco"}]), data("24 DEZ"),
], "acoes": [{"em": "ligo#4", "faz": "brilho", "para": 0.08, "dur": 0.4}]})

# C22 linha13 43,90-46,22: escuro, só a tela; "LIGANDO... VÓ"
cenas.append({"em": "linha13", "cenario": "quarto", "luz": "noite", "paleta": "petroleo", "brilho": 0.08, "elementos": [
    ana(x=0.5, y=0.46, escala=1.1, olhar="celular", expressao="triste", camada="topo", alpha=0.9,
        acoes=[{"em": "olhou", "faz": "olha", "para": "cima"}, {"em": "escuro", "faz": "olha", "para": "celular"},
               {"em": "ligou", "faz": "expressao", "para": "nervoso"}, {"em": "ligou", "faz": "squash", "forca": 0.12}]),
    dict(id="veu", tipo="bloco", x=0.5, y=0.5, largura=1200, altura=2100, cor="#05060F", raio=0, alpha=0.45, camada="topo", pode_sobrepor=True),
    dict(id="lig", tipo="texto", x=0.5, y=0.255, texto="LIGANDO... VÓ", tam=76, fundo="#16A57A", cor="#FFFFFF",
         acoes=[{"em": "ligou", "faz": "entra", "jeito": "pop"}, {"em": "ligou", "faz": "pisca", "brilho": True, "dur": 0.8, "cor": "#7CFFB0"}]),
    cont(0, cor=VERMELHO), data("24 DEZ"),
]})

# C23 linha14 46,22-48,11: split ANA x AVÓ, atende em "atendeu"
cenas.append({"em": "linha14", "cenario": "chapado", "padrao": "bokeh", "paleta": "cobalto", "transicao": "wipe_diagonal", "elementos": [
    dict(id="sp", tipo="split", x=0.5, y=0.39, altura=780, paineis=[
        {"cenario": "quarto", "luz": "noite", "paleta": "cobalto", "rotulo": "ANA", "rotulo_pos": "baixo", "brilho": 0.3, "foco": [0.5, 0.4],
         "elementos": [ana(x=0.5, y=0.46, escala=1.0, olhar="celular", expressao="nervoso", camada="topo",
                           acoes=[{"em": "atendeu", "faz": "expressao", "para": "surpreso"}, {"em": "toque", "faz": "expressao", "para": "feliz"}])]},
        {"cenario": "cozinha", "luz": "noite", "paleta": "laranja", "rotulo": "VÓ", "rotulo_pos": "baixo", "foco": [0.5, 0.4],
         "elementos": [avo(x=0.5, y=0.47, escala=1.0, segura="celular", olhar="celular",
                           acoes=[{"em": "atendeu", "faz": "pula", "altura": 25}, {"em": "atendeu", "faz": "olha", "para": "camera"}, {"em": "primeiro", "faz": "squash"}])]}]),
    cont(0, cor=VERMELHO, y=0.14), data("24 DEZ", y=0.14),
]})

# C24 "tava" 48,11-50,22: close da avó feliz, calor crescendo
cenas.append({"em": "tava", "cenario": "cozinha", "luz": "noite", "paleta": "uva", "brilho": 0.85, "elementos": [
    avo(x=0.5, y=0.47, escala=1.15, segura="celular", olhar="camera",
        acoes=[{"em": "esperando", "faz": "expressao", "para": "gargalhada"}, {"em": "esperando", "faz": "pula", "altura": 20}, {"em": "trinta#3", "faz": "squash"}]),
    dict(id="veu", tipo="bloco", x=0.5, y=0.5, largura=1200, altura=2100, cor="#F57C1F", raio=0, alpha=0, camada="meio", pode_sobrepor=True,
         acoes=[{"em": "tava", "faz": "muda", "prop": "alpha", "para": 0.28, "ate": "uma#6"}]),
    cont(0, cor=VERMELHO), data("24 DEZ"),
], "acoes": [{"em": "tava", "faz": "brilho", "para": 1.15, "ate": "uma#6"}]})

# C25 "acenderam" 50,22-51,73: ESTOURO
c, n = queda(0, 31, "acenderam", 0.3)
cenas.append({"em": "acenderam", "cenario": "chapado", "padrao": "raios_hq", "paleta": "laranja", "energia": 0.9, "brilho": 0.08, "transicao": "flash_cor", "elementos": [
    casa(31, x=0.17, y=0.40, escala=0.58, id="casa_e", cor="#E9A23B"),
    casa(31, x=0.83, y=0.40, escala=0.58, id="casa_d", cor="#3FA37A"),
    casa(0, x=0.5, y=0.40, escala=0.66, cor="#8A7FA8", acoes=[c, {"em": "acenderam", "faz": "pisca", "brilho": True, "dur": 1.4, "cor": "#FFD98A"}]),
    pipo(0.5, 0.54, 0.6, [{"em": "acenderam", "faz": "estoura"}, {"em": "uma#7", "faz": "pula", "altura": 50}, {"em": "vez", "faz": "squash"}], olhar="camera"),
    cont(0, n + [{"em": "acenderam", "faz": "muda", "prop": "cor", "para": AMARELO}, {"em": "acenderam", "faz": "soco"}], cor=VERMELHO),
    data("24 DEZ"),
], "acoes": [{"em": "acenderam", "faz": "brilho", "para": 1.3, "dur": 0.3}, {"em": "acenderam", "faz": "flash", "dur": 0.2},
             {"em": "acenderam", "faz": "soco", "forca": 0.14}]})

# C26 linha16 51,73-53,25: quintal da casa acesa, Ana sorrindo no celular
cenas.append({"em": "linha16", "cenario": "casa_natal_fora", "paleta": "rosa", "elementos": [
    casa(31, x=0.398, y=0.4385, largura=600, altura=955, escala=1.0, cor="#A6B5EC", telhado="#2439A0", acoes=[{"em": "Dois", "faz": "pisca", "brilho": True, "dur": 1.2, "cor": "#FFD98A"}]),
    ana(ancora="quintal_dir", dy=-0.04, olhar="camera", expressao="gargalhada",
        acoes=[{"em": "minutos", "faz": "pula", "altura": 25}, {"em": "ligacao", "faz": "squash"}]),
    cont(31), data("24 DEZ"),
]})

# C27 "acendem" 53,25-55,66: a lição, Pipo pipoca pulando
cenas.append({"em": "acendem", "cenario": "sala_natal", "paleta": "laranja", "elementos": [
    pipo(0.5, 0.5, 0.8, [{"em": "acendem", "faz": "pula", "altura": 60}, {"em": "mes", "faz": "pula", "altura": 45},
                          {"em": "desculpa", "faz": "squash"}, {"em": "apagou#2", "faz": "pula", "altura": 60}], forma="pipoca", olhar="camera", boca="sorriso"),
    tit("DOIS MINUTOS\nACENDEM", y=0.22, tam=92, em="acendem"),
    dict(id="tit2", tipo="texto", x=0.5, y=0.355, texto="UM MÊS DE DESCULPA", tam=62, cor="#FFF4E6", fundo="#2A3FD1", acoes=[{"em": "mes", "faz": "entra", "jeito": "pop"}]),
]})

# C28 linha17 55,66-58,22: a pergunta, contador "?"
cenas.append({"em": "linha17", "cenario": "chapado", "padrao": "luzes", "paleta": "mostarda", "transicao": "papel", "elementos": [
    pipo(0.5, 0.5, 0.8, [{"em": "Quantas", "faz": "pula", "altura": 40}, {"em": "sua", "faz": "squash"}, {"em": "perdeu", "faz": "soco"}],
         forma="pipoca", pose="apontando", olhar="camera", boca="sorriso_torto"),
    tit("QUANTAS A SUA\nJÁ PERDEU?", y=0.27, tam=90, em="Quantas"),
    dict(id="cont", tipo="texto", x=0.33, y=0.155, texto="? LÂMPADAS", tam=68, cor=AMARELO, fundo="#1D1B3A", acoes=[{"em": "lampadas#2", "faz": "entra", "jeito": "pop"}, {"em": "perdeu", "faz": "soco"}]),
]})

# C29 linha18 58,22-60,75: manda pra quem você deve uma ligação
cenas.append({"em": "linha18", "cenario": "chapado", "padrao": "bokeh", "paleta": "rosa", "elementos": [
    pipo(0.5, 0.5, 0.8, [{"em": "Manda", "faz": "pula", "altura": 40}, {"em": "devendo", "faz": "squash"}, {"em": "ligacao#2", "faz": "pula", "altura": 30}],
         forma="pipoca", segura="celular", olhar="celular", boca="sorriso"),
    tit("MANDA PRA QUEM\nVOCÊ DEVE\nUMA LIGAÇÃO", y=0.22, tam=72, em="Manda"),
]})

# C30 "Ou" 60,75-fim: ou liga agora, congela
cenas.append({"em": "Ou", "cenario": "chapado", "padrao": "formas", "paleta": "laranja", "energia": 0.5, "elementos": [
    pipo(0.5, 0.5, 0.85, [{"em": "Ou", "faz": "pula", "altura": 40}, {"em": "agora", "faz": "soco"}], forma="pipoca", pose="apontando", olhar="camera", boca="sorriso"),
    tit("OU LIGA AGORA", y=0.24, tam=104, em="Ou", acoes=[{"em": "Ou", "faz": "entra", "jeito": "pop"}, {"em": "agora", "faz": "soco"}]),
], "acoes": [{"em": 62.05, "faz": "congela", "dur": 0.5}]})

out = {"paleta": "cobalto", "cenas": cenas}
json.dump(out, open(os.path.join(AQUI, "cenas.json"), "w"), indent=1, ensure_ascii=False)
print("cenas:", len(cenas))
