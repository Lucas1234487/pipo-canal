"""Motor 2D do PipoPop.
Uso:
  python3 kit2d/render2d.py WORK               # grava WORK/frames/fNNNN.png, WORK/events.json e WORK/qa_scene.json
  python3 kit2d/render2d.py WORK --previa      # só uma folha de contato (WORK/previa.jpg), 1 quadro a cada 1,5 s
  python3 kit2d/render2d.py WORK --quadros 1,45,200   # só esses quadros, em WORK/prev/
Lê WORK/cenas.json (formato em kit2d/CENAS.md) e WORK/timing.json (gerado pelo kit/tts.py).
"""
import json, math, os, sys, time, unicodedata
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
import numpy as np
from PIL import Image
import estilo as E
from estilo import W, H, FPS, clamp, ease_out_back, ease_in_back, ease_out, ease_in_out, hexc
import biblioteca as B
import cenarios2 as C2
import fundos as F

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAUDA = 0.6   # segundos depois da última palavra

SONS = {   # apelidos -> arquivos CC0 de assets/ (ver assets/LICENCAS.md)
    "pop": "assets/sfx/pop-sounds/pop1.ogg", "pop2": "assets/sfx/pop-sounds/pop4.ogg", "pop3": "assets/sfx/pop-sounds/pop7.ogg",
    "pops": "assets/sfx/3-pop-sounds/3pops.ogg", "estouro": "assets/sfx/3-pop-sounds/pop2.ogg",
    "whoosh": "assets/sfx/air-whoosh/whoosh_1passada.ogg", "slide": "assets/sfx/a-slide-pop-sound/slidepop_0.mp3",
    "impacto": "assets/sfx/75-cc0-breaking-falling-hit-sfx/bfh1_hit_03.ogg", "impacto2": "assets/sfx/75-cc0-breaking-falling-hit-sfx/bfh1_hit_07.ogg",
    "vidro": "assets/sfx/75-cc0-breaking-falling-hit-sfx/bfh1_glass_breaking_02.ogg", "queda": "assets/sfx/75-cc0-breaking-falling-hit-sfx/bfh1_falling_01.ogg",
    "metal": "assets/sfx/100-cc0-sfx-2/sfx100v2_metal_hit_01.ogg", "madeira": "assets/sfx/100-cc0-sfx-2/sfx100v2_wood_hit_01.ogg",
    "carimbo": "assets/sfx/100-cc0-sfx-2/sfx100v2_hit_02.ogg", "tique": "assets/sfx/100-cc0-sfx-2/sfx100v2_switch_01.ogg",
    "porta": "assets/sfx/100-cc0-sfx-2/sfx100v2_door_01.ogg", "passos": "assets/sfx/100-cc0-sfx-2/sfx100v2_footstep_wood_01.ogg",
    "mastiga": "assets/sfx/80-cc0-creature-sfx/eat_02.ogg", "mastiga2": "assets/sfx/80-cc0-creature-sfx/eat_04.ogg",
    "arroto": "assets/sfx/80-cc0-creature-sfx/burp_02.ogg", "ooh": "assets/sfx/80-cc0-creature-sfx/ooh.ogg",
    "fofo": "assets/sfx/80-cc0-creature-sfx/cute_02.ogg", "coracao": "assets/sfx/heartbeat-sounds/heartbeat_fast_0.wav",
}
# sons de meme (assets/sfx/memes/, CC0 do Freesound via Openverse + "fa"/"fa2" gerados por nós; ver memes/proveniencia.tsv)
SONS.update({k: f"assets/sfx/memes/{k}.ogg" for k in (
    "boom", "disco", "violino_triste", "badumtss", "palhaco", "riser", "dundun", "ohh", "risada", "grilo",
    "certo", "errado", "dinheiro", "glitch", "gongo", "apito_sobe", "apito_desce", "boing", "fa", "fa2")})

# reações de meme (ação de câmera "reacao"): duração padrão, som padrão e recorte do som [dur, fade] (None = inteiro)
REACOES = {
    "boom":      {"dur": 0.9, "som": "boom", "corte": None},
    "disco":     {"dur": 1.0, "som": "disco", "corte": None},
    "triste":    {"dur": 1.2, "som": "violino_triste", "corte": (2.6, 0.8)},
    "dramatico": {"dur": 1.2, "som": "dundun", "corte": (2.2, 0.7)},
    "ohh":       {"dur": 0.9, "som": "ohh", "corte": (2.0, 0.8)},
    "grilo":     {"dur": 1.2, "som": "grilo", "corte": None},
    "fa":        {"dur": 0.7, "som": "fa", "corte": None},
}
MUSICAS = {
    "percussao": "assets/musica/cinematic-percussion-loop/Cinematic%20percussion%20loop%202.wav",
    "misterio": "assets/musica/cc0-mystery/mystery%20exploration.mp3",
    "viagem": "assets/musica/a-mystery-travel/mystery_travel.mp3",
    "aventura": "assets/musica/adventure-intro-title-cinematic-epic/Adventure%20Theme%20Intro.wav",
}


def som(nome):
    p = SONS.get(nome, MUSICAS.get(nome, nome))
    if not os.path.exists(os.path.join(REPO, p)):
        raise SystemExit(f"som '{nome}' nao existe ({p}). Apelidos: {', '.join(SONS)}")
    return p


# ======================= tempo amarrado às palavras =======================
def norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if c.isalnum() and unicodedata.category(c) != "Mn")


class Relogio:
    def __init__(self, timing):
        self.pal = []
        for l in timing["lines"]:
            for w, s, d in l["words"]:
                self.pal.append((norm(w), s, s + d, l["i"]))
        self.fim = max(p[2] for p in self.pal)

    def t(self, ref, desde=0.0, fim=False):
        """ref: número (segundos) | 'palavra' | 'palavra#2' (2a ocorrência no vídeo todo) | 'linha3' (início da linha 3)."""
        if ref is None:
            return desde
        if isinstance(ref, (int, float)):
            return float(ref)
        ref = str(ref).strip()
        if ref.startswith("linha") and ref[5:].isdigit():
            ls = [p for p in self.pal if p[3] == int(ref[5:])]
            if not ls:
                raise SystemExit(f"'{ref}': essa linha não existe no timing.json")
            return ls[-1][2] if fim else ls[0][1]
        n = None
        if "#" in ref:
            ref, n = ref.split("#"); n = int(n)
        alvo = norm(ref)
        hits = [p for p in self.pal if p[0] == alvo]
        if not hits:
            raise SystemExit(f"palavra '{ref}' não está na narração. Palavras: {' '.join(p[0] for p in self.pal)}")
        if n:
            if n > len(hits):
                raise SystemExit(f"'{ref}#{n}': a palavra só aparece {len(hits)} vez(es)")
            h = hits[n - 1]
        else:
            h = next((p for p in hits if p[1] >= desde - 0.05), hits[0])
        return h[2] if fim else h[1]


# ======================= trilhas de propriedades =======================
class Trilha:
    def __init__(self, base):
        self.base = base; self.tw = []

    def add(self, t0, dur, para, ease=ease_in_out):
        self.tw.append((t0, max(1e-3, dur), para, ease)); self.tw.sort(key=lambda x: x[0])

    def __call__(self, t):
        v = self.base
        for t0, d, para, ease in self.tw:
            if t < t0:
                break
            if not isinstance(para, (int, float)) or not isinstance(v, (int, float)):
                v = para; continue
            k = clamp((t - t0) / d)
            v = v + (para - v) * ease(k)
        return v


CURVAS = {"suave": ease_in_out, "rapido": ease_out, "elastico": lambda x: ease_out_back(x, 1.6), "linear": lambda x: x}
PERSONAGENS = ("pipo", "humano")
ATRAS_DA_FRENTE = PERSONAGENS + ("porta",)   # desenhados antes da camada da frente do cenário (o resto fica por cima)
NUMERICAS = ("x", "y", "escala", "rot", "alpha")


class Elemento:
    def __init__(self, d, cena, rel, idx):
        self.d = d; self.id = d.get("id", f"e{idx}"); self.tipo = d["tipo"]; self.cena = cena
        self.seed = (sum(map(ord, self.id)) * 31 + idx * 7) % 100000
        self.tr = {}
        self.efeitos = []   # (tipo, t0, params)
        self.t_entra = cena.t0; self.t_sai = None; self.estouro = None
        self.sons = []
        tem_entra = False
        for a in d.get("acoes", []):
            tem_entra |= a.get("faz") == "entra"
        if tem_entra:
            self.tr_get("_vis").base = 0
        for a in d.get("acoes", []):
            self.acao(a, rel)

    def tr_get(self, k):
        if k not in self.tr:
            base = {"_vis": 1, "_pop": 1, "_dx": 0, "_dy": 0}.get(k, self.d.get(k, {"escala": 1, "rot": 0, "alpha": 1, "x": 0.5, "y": 0.5}.get(k, 0)))
            self.tr[k] = Trilha(base)
        return self.tr[k]

    def acao(self, a, rel):
        faz = a.get("faz")
        t0 = rel.t(a.get("em"), self.cena.t0) + a.get("depois", 0)
        dur = a.get("dur")
        if a.get("ate") is not None:
            dur = max(0.1, rel.t(a["ate"], t0, fim=True) - t0)
        curva = CURVAS.get(a.get("curva", "suave"), ease_in_out)
        if a.get("som"):
            self.sons.append([som(a["som"]), round(t0 + a.get("som_atraso", 0), 3), a.get("volume", 0.7)])
        if faz == "entra":
            j = a.get("jeito", "pop"); d = dur or (0.35 if j in ("pop", "carimba") else 0.45)
            self.tr_get("_vis").add(t0, 1e-3, 1)
            if j == "pop":
                self.tr_get("_pop").base = 0; self.tr_get("_pop").add(t0, d, 1, lambda x: ease_out_back(x, 2.2))
            elif j == "carimba":
                self.tr_get("_pop").base = 2.4; self.tr_get("_pop").add(t0, d * 0.5, 1, lambda x: x * x)
                self.efeitos.append(("treme_cam", t0 + d * 0.5, {"dur": 0.25, "forca": 14}))
            elif j in ("desliza_esq", "desliza_dir"):
                self.tr_get("_dx").base = -W * 1.1 if j == "desliza_esq" else W * 1.1
                self.tr_get("_dx").add(t0, d, 0, lambda x: ease_out_back(x, 1.2))
            elif j in ("sobe", "desce", "cai"):
                self.tr_get("_dy").base = H * 0.7 if j == "sobe" else -H * 0.7
                self.tr_get("_dy").add(t0, d, 0, (lambda x: 1 - abs(math.cos(x * math.pi * 1.5)) * (1 - x)) if j == "cai" else (lambda x: ease_out_back(x, 1.3)))
            elif j == "aparece":
                self.tr_get("alpha").base = 0; self.tr_get("alpha").add(t0, d, 1)
        elif faz == "sai":
            j = a.get("jeito", "pop"); d = dur or 0.25
            if j == "pop":
                self.tr_get("_pop").add(t0, d, 0, ease_in_back)
            elif j in ("desliza_esq", "desliza_dir"):
                self.tr_get("_dx").add(t0, d, -W * 1.2 if j == "desliza_esq" else W * 1.2, lambda x: x * x)
            else:
                self.tr_get("alpha").add(t0, d, 0)
            self.tr_get("_vis").add(t0 + d, 1e-3, 0)
        elif faz == "move":
            if isinstance(a["para"], str):   # "para": "porta" (âncora do cenário)
                x, y, _ = C2.posiciona(self.cena.d.get("cenario", "chapado"), dict(self.d, ancora=a["para"], dx=a.get("dx", 0), dy=a.get("dy", 0)))
            else:
                x, y = a["para"]
            self.tr_get("x").add(t0, dur or 0.5, x, curva); self.tr_get("y").add(t0, dur or 0.5, y, curva)
        elif faz in ("escala", "gira"):
            self.tr_get("escala" if faz == "escala" else "rot").add(t0, dur or 0.4, a["para"], curva)
        elif faz in ("muda", "conta", "cresce"):
            prop = a.get("prop", "valor")
            self.tr_get(prop).add(t0, dur if dur is not None else (0.8 if faz != "muda" else 0.35), a["para"], CURVAS.get(a.get("curva", "rapido" if faz != "muda" else "suave")))
        elif faz in ("olha", "sobrancelha", "boca", "palpebra", "tela", "segura", "expressao", "pose"):
            prop = {"olha": "olhar"}.get(faz, faz)
            self.tr_get(prop).add(t0, dur or 0.2, a["para"])
        elif faz == "estoura":
            self.estouro = t0
        elif faz in ("squash", "pula", "treme", "pisca", "mastiga", "soco"):
            self.efeitos.append((faz, t0, dict(a, dur=dur)))
        else:
            raise SystemExit(f"elemento {self.id}: ação desconhecida '{faz}'")

    def estado(self, t):
        st = dict(self.d)
        for k, v in (("x", 0.5), ("y", 0.5), ("escala", 1), ("rot", 0), ("alpha", 1), ("_vis", 1), ("_pop", 1), ("_dx", 0), ("_dy", 0)):
            st.setdefault(k, v)
        for k, tr in self.tr.items():
            st[k] = tr(t)
            if isinstance(st[k], str):   # troca de texto (pose, expressao...): valor anterior e hora, para o desenho suavizar
                tws = [tw[0] for tw in tr.tw if tw[0] <= t]
                if tws:
                    st["_troca_" + k] = (tr(tws[-1] - 1e-4), tws[-1])
        st["_t"] = t; st["_estouro"] = self.estouro
        return st


class Cena:
    def __init__(self, d, rel, desde, idx):
        self.d = d; self.idx = idx
        self.t0 = rel.t(d.get("em", 0), desde)
        self.pal = E.paleta(d.get("paleta"))
        self.cam = {k: Trilha(v) for k, v in (("zoom", d.get("zoom", 1.0)), ("cx", 0.5), ("cy", 0.5), ("rot", 0.0))}
        self.efeitos = []; self.congela = []; self.sons = []; self.reacoes = []
        ocup = set()
        for e in d.get("elementos", []):   # âncoras: "ancora": "sofa_assento" no lugar de x, y
            if e.get("ancora"):
                e["x"], e["y"], s = C2.posiciona(d.get("cenario", "chapado"), e)
                if s:
                    e["escala"] = s
                if e.get("tipo") in PERSONAGENS:
                    ocup.add(e["ancora"])
            for a in e.get("acoes", []):
                if a.get("faz") == "move" and isinstance(a.get("para"), str) and e.get("tipo") in PERSONAGENS:
                    ocup.add(a["para"])
        d["_ocupadas"] = sorted(ocup)
        self.els = [Elemento(e, self, rel, i) for i, e in enumerate(d.get("elementos", []))]
        for a in d.get("acoes", []):
            t0 = rel.t(a.get("em"), self.t0) + a.get("depois", 0)
            dur = a.get("dur")
            if a.get("ate") is not None:
                dur = max(0.1, rel.t(a["ate"], t0, fim=True) - t0)
            if a["faz"] == "reacao":
                self.reacao(a, t0, dur, idx); continue
            if a.get("som"):
                self.sons.append([som(a["som"]), round(t0 + a.get("som_atraso", 0), 3), a.get("volume", 0.7)])
            faz = a["faz"]
            if faz == "zoom":
                self.cam["zoom"].add(t0, dur or 0.5, a["para"], CURVAS.get(a.get("curva", "suave")))
            elif faz == "pan":
                self.cam["cx"].add(t0, dur or 0.6, a["para"][0], CURVAS.get(a.get("curva", "suave")))
                self.cam["cy"].add(t0, dur or 0.6, a["para"][1], CURVAS.get(a.get("curva", "suave")))
            elif faz == "inclina":
                self.cam["rot"].add(t0, dur or 0.4, a["para"])
            elif faz in ("soco", "treme", "flash"):
                self.efeitos.append((faz, t0, dict(a, dur=dur)))
            elif faz == "congela":
                self.congela.append((t0, dur or 0.5))
            else:
                raise SystemExit(f"cena {idx}: ação de câmera desconhecida '{faz}'")

    def reacao(self, a, t0, dur, idx):
        """Reação de meme: câmera + cor + som num pacote só (kit2d/CENAS.md, "Reações de meme")."""
        est = a.get("estilo", "boom")
        if est not in REACOES:
            raise SystemExit(f"cena {idx}: reação '{est}' não existe. Estilos: {', '.join(REACOES)}")
        cfg = REACOES[est]
        dur = clamp(dur or cfg["dur"], 0.4, 1.2)
        alvo = a.get("alvo")
        if alvo is None:   # padrão: o primeiro personagem da cena
            alvo = next((e.id for e in self.els if e.tipo in PERSONAGENS), [0.5, 0.4])
        el = None
        if isinstance(alvo, str):
            el = next((e for e in self.els if e.id == alvo), None)
            if el is None:
                raise SystemExit(f"cena {idx}: reação '{est}': alvo '{alvo}' não é id de elemento desta cena")
            st = el.estado(t0)
            px, py = st["x"] + st["_dx"] / W, st["y"] + st["_dy"] / H
            if el.tipo in PERSONAGENS:   # mira no rosto, não na barriga
                py -= (145 if el.tipo == "pipo" else 255) * st.get("escala", 1) / H
        else:
            px, py = alvo
        r = {"estilo": est, "t0": t0, "dur": dur, "alvo": (px, py), "el": el.id if el else None,
             "forca": a.get("forca", 1.0), "texto": a.get("texto", "*para tudo*"), "texto_y": a.get("texto_y", 0.1)}
        self.reacoes.append(r)
        if est == "boom":
            self.congela.append((t0 + 0.12, 0.4))
        elif est in ("disco", "grilo"):
            self.congela.append((t0, dur))
        nome = a.get("som", cfg["som"])
        if nome:
            corte = cfg["corte"] if "som" not in a else None
            if a.get("som_dur"):
                corte = (a["som_dur"], 0.3)
            spec = [som(nome), 0, corte[0], corte[1]] if corte else som(nome)
            self.sons.append([spec, round(t0 + a.get("som_atraso", 0), 3), a.get("volume", 0.8)])


# ======================= efeitos transitórios =======================
def efeitos_el(el, t):
    sx = sy = 1.0; dx = dy = 0.0; alpha = 1.0; extra = {}
    for tipo, t0, p in el.efeitos:
        u = t - t0
        if u < 0:
            continue
        if tipo == "squash" and u < 0.45:
            f = p.get("forca", 0.25) * math.exp(-u * 9) * math.cos(u * 32)
            sx *= 1 + f; sy *= 1 - f
        elif tipo == "soco" and u < 0.35:
            f = p.get("forca", 0.25) * math.exp(-u * 12)
            sx *= 1 + f; sy *= 1 + f
        elif tipo == "pula" and u < 0.45:
            dy -= p.get("altura", 120) * math.sin(math.pi * u / 0.45)
        elif tipo == "treme" and u < (p.get("dur") or 0.4):
            f = p.get("forca", 14) * (1 - u / (p.get("dur") or 0.4))
            dx += math.sin(u * 95) * f; dy += math.cos(u * 77) * f * 0.6
        elif tipo == "pisca":
            d = p.get("dur") or 99
            if u < d - 1e-3 and int(u / p.get("ritmo", 0.25) + 1e-6) % 2 == 1:
                alpha = 0.0
        elif tipo == "mastiga" and u < (p.get("dur") or 1.0):
            extra["boca_abre"] = 0.5 + 0.5 * math.sin(u * 2 * math.pi * p.get("ritmo", 4))
            f = 0.06 * math.sin(u * 2 * math.pi * p.get("ritmo", 4))
            sx *= 1 + f; sy *= 1 - f
    return sx, sy, dx, dy, alpha, extra


def reacao_ativa(c, tr):
    for r in c.reacoes:
        if r["t0"] <= tr < r["t0"] + r["dur"]:
            return r, tr - r["t0"]
    return None, 0.0


def reacao_cam(r, u):
    """(multiplicador de zoom, peso do centro no alvo, tremor dx, dy, flash) da reação no instante u (s desde o início)."""
    e, f, d = r["estilo"], r["forca"], r["dur"]
    zm, w, sx, sy, fl = 1.0, 0.0, 0.0, 0.0, 0.0
    if e == "boom":
        k = ease_out(clamp(u / 0.12)); zm = 1 + 0.8 * f * k; w = k
        if u < 0.55:
            g = 9 * f * (1 - u / 0.55); sx = math.sin(u * 90) * g; sy = math.cos(u * 73) * g
    elif e == "triste":
        k = ease_in_out(clamp(u / d)); zm = 1 + 0.18 * f * k; w = k * 0.8
    elif e == "dramatico":
        n = 0 if u < d * 0.42 else (1 if u < d * 0.875 else 2)   # 3 cortes secos, no ritmo do "dun dun dunnn"
        zm = (1.3, 1.8, 2.5)[n] ** f; w = 1.0
    elif e == "ohh":
        zm = 1 + 0.14 * f * math.exp(-u * 7) * clamp(u / 0.03); w = 0.5
    elif e == "grilo":
        k = ease_in_out(clamp(u / d)); zm = 1 + 0.07 * f * k; w = k * 0.6
    elif e == "fa":
        zm = 1 + 0.45 * f; w = 1.0
        if u < 0.5:
            g = 24 * f * (1 - u / 0.5); sx = math.sin(u * 97 + 1) * g; sy = math.cos(u * 81) * g
        fl = max(0.0, 1 - u / 0.14)
    return zm, w, sx, sy, fl


def camera(c, t, tr=None):
    tr = t if tr is None else tr
    z = c.cam["zoom"](t) * (1 + c.d.get("deriva", 0.025) * clamp((t - c.t0) / 4))
    cx, cy, rot = c.cam["cx"](t), c.cam["cy"](t), c.cam["rot"](t)
    dx = dy = 0.0; flash = 0.0
    r, u = reacao_ativa(c, tr)
    if r:
        zm, w, dx, dy, flash = reacao_cam(r, u)
        z *= zm
        px = clamp(r["alvo"][0], 0.5 / z, 1 - 0.5 / z); py = clamp(r["alvo"][1], 0.5 / z, 1 - 0.5 / z)   # não mostra fora do cenário
        cx += (px - cx) * w; cy += (py - cy) * w
    for tipo, t0, p in c.efeitos + [e for el in c.els for e in el.efeitos if e[0] == "treme_cam"]:
        u = t - t0
        if u < 0:
            continue
        if tipo == "soco" and u < 0.4:
            z *= 1 + p.get("forca", 0.12) * math.exp(-u * 10) * (1 if u > 0.02 else u / 0.02)
        elif tipo in ("treme", "treme_cam") and u < (p.get("dur") or 0.4):
            f = p.get("forca", 18) * (1 - u / (p.get("dur") or 0.4))
            dx += math.sin(u * 83 + 1) * f; dy += math.cos(u * 71) * f
        elif tipo == "flash" and u < (p.get("dur") or 0.15):
            flash = 1 - u / (p.get("dur") or 0.15)
    return z, cx, cy, rot, dx, dy, flash


# ======================= roteiro inteiro =======================
class Filme:
    def __init__(self, work):
        self.work = work
        self.cfg = json.load(open(os.path.join(work, "cenas.json")))
        timing = json.load(open(os.path.join(work, "timing.json")))
        self.rel = Relogio(timing)
        total = timing.get("total", self.rel.fim)
        self.N = int(math.ceil((max(total, self.rel.fim) + self.cfg.get("cauda", CAUDA)) * FPS))
        self.cenas = []
        desde = 0.0
        for i, c in enumerate(self.cfg["cenas"]):
            c.setdefault("paleta", self.cfg.get("paleta"))
            cena = Cena(c, self.rel, desde, i)
            if self.cenas and cena.t0 <= self.cenas[-1].t0:
                raise SystemExit(f"cena {i} começa em {cena.t0:.2f}s, antes da cena anterior: ponha as cenas em ordem")
            self.cenas.append(cena); desde = cena.t0
        self.cenas[0].t0 = 0.0
        for i, c in enumerate(self.cenas):   # início/fim de cada cena (Ken Burns do fundo_foto)
            c.d["_t0"] = c.t0; c.d["_t1"] = self.cenas[i + 1].t0 if i + 1 < len(self.cenas) else self.N / FPS
        self.congela = [z for c in self.cenas for z in c.congela]

    def tempo(self, fr):
        t = (fr - 1) / FPS
        for t0, d in self.congela:
            if t0 <= t < t0 + d:
                return t0, True
        return t, False

    def cena_em(self, t):
        c = self.cenas[0]
        for x in self.cenas:
            if x.t0 <= t + 1e-6:
                c = x
        return c

    def pos(self, ref, t, c):
        if isinstance(ref, str):
            el = next((e for e in c.els if e.id == ref), None)
            if el is None:
                raise SystemExit(f"fluxo: elemento '{ref}' não existe nesta cena")
            st = el.estado(t); return st["x"] * W + st["_dx"], st["y"] * H + st["_dy"]
        return ref[0] * W, ref[1] * H

    def quadro(self, fr, ctx, tex):
        t, frozen = self.tempo(fr)
        treal = (fr - 1) / FPS   # tempo real (as reações continuam andando durante o congela)
        c = self.cena_em(t)
        trn = c.d.get("transicao"); u = (t - c.t0) / c.d.get("transicao_dur", F.DUR_TRANSICAO.get(trn, 0.25))
        prev = None
        if trn and c.idx > 0 and 0 <= u < 1:
            if trn not in F.TRANSICOES:
                raise SystemExit(f"cena {c.idx}: transicao '{trn}' não existe. Use: {', '.join(F.TRANSICOES)}")
            prev = self.ultimo_quadro(c.idx - 1, c.t0 - 1 / FPS)
        E.set_boil(int(t * FPS))
        caixas, flash, rea, ru = self.desenha_cena(ctx, c, t, treal)
        ctx.identity_matrix()
        if prev is not None:
            F.transicao(ctx, trn, prev, u, c.pal, seed=c.idx * 13 + 1, opts=c.d)
        if rea:
            reacao_tela(ctx, rea, ru, treal)
        if flash > 0:
            ctx.set_source_rgba(1, 1, 1, flash * 0.85); ctx.paint()
        E.aplica_textura(ctx, tex, int(t * FPS))
        return caixas

    def ultimo_quadro(self, idx, t):
        """Último quadro da cena anterior (sem textura), guardado para a transição do corte."""
        if getattr(self, "_prev", (None,))[0] != idx:
            surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cp = cairo.Context(surf)
            cp.set_line_cap(cairo.LINE_CAP_ROUND); cp.set_line_join(cairo.LINE_JOIN_ROUND)
            E.set_boil(int(t * FPS))
            self.desenha_cena(cp, self.cenas[idx], t, t); surf.flush()
            self._prev = (idx, surf)
        return self._prev[1]

    def desenha_cena(self, ctx, c, t, treal):
        z, cx, cy, rot, sdx, sdy, flash = camera(c, t, treal)
        rea, ru = reacao_ativa(c, treal)
        ctx.identity_matrix()
        ctx.translate(W / 2 + sdx, H / 2 + sdy); ctx.scale(z, z); ctx.rotate(math.radians(rot)); ctx.translate(-cx * W, -cy * H)
        if c.d.get("fundo_foto"):     # foto real em tela cheia (Ken Burns, estilo, parallax): kit2d/fundos.py
            F.foto(ctx, c.pal, t, c.d, seed=c.idx * 13 + 1)
        else:
            B.cenario(ctx, c.d.get("cenario", "chapado"), c.pal, t, c.d, seed=c.idx * 13 + 1)
        caixas = {}
        nome_cen = c.d.get("cenario", "chapado")
        atras = [el for el in c.els if el.d.get("camada", "meio" if el.tipo in ATRAS_DA_FRENTE else "topo") == "meio"]
        self._rea = (rea, ru)
        for el in atras:
            self.elemento(ctx, el, t, c, caixas)
        if not c.d.get("fundo_foto"):
            C2.cenario_frente(ctx, nome_cen, c.pal, t, c.d, seed=c.idx * 13 + 1)
        for el in c.els:
            if el not in atras:
                self.elemento(ctx, el, t, c, caixas)
        return caixas, flash, rea, ru

    def elemento(self, ctx, el, t, c, caixas):
        if True:
            st = el.estado(t)
            if st.get("_vis", 1) < 0.5 or st.get("alpha", 1) <= 0.01:
                return
            if el.tipo == "fluxo":
                self.fluxo(ctx, el, st, t, c); return
            sx, sy, dx, dy, alpha, extra = efeitos_el(el, t)
            st.update(extra)
            rea, ru = getattr(self, "_rea", (None, 0))
            if rea and rea["estilo"] == "grilo" and el.id == rea["el"]:
                st["_pisca"] = 1.0 if (0.3 <= ru / rea["dur"] * 1.2 < 0.42 or 0.72 <= ru / rea["dur"] * 1.2 < 0.84) else 0.0
            a = st.get("alpha", 1) * alpha
            if a <= 0.01:
                return
            ctx.save()
            ctx.translate(st["x"] * W + st["_dx"] + dx, st["y"] * H + st["_dy"] + dy)
            ctx.rotate(math.radians(st.get("rot", 0)))
            s = st.get("escala", 1) * st["_pop"]
            if el.tipo in PERSONAGENS and st.get("respira", True):
                sy *= 1 + 0.014 * math.sin(t * 2.6 + el.seed)
            if el.d.get("espelha"):
                sx = -sx
            ctx.scale(max(1e-3, s * sx), max(1e-3, s * sy) if sy > 0 else 1e-3)
            if a < 0.99:
                ctx.push_group()
            if el.tipo == "pipo":
                bx = B.desenha_pipo(ctx, st, t, el.seed)
            elif el.tipo == "humano":
                bx = B.desenha_humano(ctx, st, t, el.seed)
            elif el.tipo in B.DESENHOS:
                bx = B.DESENHOS[el.tipo](ctx, st, t, c.pal, el.seed)
            else:
                raise SystemExit(f"tipo desconhecido '{el.tipo}'. Tipos: pipo, humano, fluxo, {', '.join(B.DESENHOS)}")
            if a < 0.99:
                ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
            entrou = st["_pop"] > 0.98 and abs(st["_dx"]) < 2 and abs(st["_dy"]) < 2 and a > 0.5
            for k, b in (bx or {}).items():
                if b:
                    caixas[(el.id, k, el.tipo, entrou, bool(el.d.get("pode_sobrepor")))] = dev_box(ctx, b)
            ctx.restore()

    def fluxo(self, ctx, el, st, t, c):
        """Folhinhas/objetos voando de um elemento para outro (o celular comendo o calendário)."""
        x0, y0 = self.pos(st["de"], t, c); x1, y1 = self.pos(st["para"], t, c)
        ritmo = st.get("ritmo", 7.0); vida = st.get("vida", 0.75)
        tin = el.t_entra if not el.tr.get("_vis") else next((tw[0] for tw in el.tr["_vis"].tw if tw[2] == 1), c.t0)
        tin -= st.get("adianta", 0)
        i0 = int((t - vida - tin) * ritmo)
        for i in range(max(0, i0), int((t - tin) * ritmo) + 1):
            nasc = tin + i / ritmo; u = (t - nasc) / vida
            if not 0 <= u <= 1:
                continue
            r = (el.seed + i * 977) % 1000 / 1000
            mx, my = (x0 + x1) / 2 + (r - 0.5) * 500, min(y0, y1) - 180 - r * 120
            e = u * u * (3 - 2 * u)
            px = (1 - e) ** 2 * x0 + 2 * (1 - e) * e * mx + e * e * x1
            py = (1 - e) ** 2 * y0 + 2 * (1 - e) * e * my + e * e * y1
            ctx.save(); ctx.translate(px, py); ctx.rotate(u * 7 * (r - 0.5) * 2 + r)
            s = st.get("escala", 1) * (1 - 0.75 * e ** 2); ctx.scale(s, s)
            B.desenha_folhinha(ctx, int(1 + r * 30), hexc(st.get("cor", "#E8352A")), el.seed + i)
            ctx.restore()


def _vinheta(ctx, a, cor=(0, 0, 0)):
    g = cairo.RadialGradient(W / 2, H * 0.45, H * 0.28, W / 2, H * 0.45, H * 0.78)
    g.add_color_stop_rgba(0, *cor, 0); g.add_color_stop_rgba(1, *cor, a)
    ctx.set_source(g); ctx.paint()


def _tinge(ctx, op, cor, a):
    ctx.save(); ctx.set_operator(op); ctx.set_source_rgb(*cor); ctx.paint_with_alpha(a); ctx.restore()


def reacao_tela(ctx, r, u, tr):
    """Cor, vinheta, linhas de impacto e texto da reação (em coordenadas de tela, por cima do cenário)."""
    e = r["estilo"]
    if e == "boom":
        k = clamp(u / 0.12)
        _tinge(ctx, cairo.OPERATOR_OVERLAY, (0.95, 0.12, 0.08), 0.45 * k)
        _vinheta(ctx, 0.7 * k)
    elif e == "disco":
        k = clamp(u / 0.08)
        _tinge(ctx, cairo.OPERATOR_HSL_SATURATION, (0.5, 0.5, 0.5), 0.9 * k)
        _vinheta(ctx, 0.35 * k)
        if r["texto"] and u > 0.1:
            p = ease_out_back(clamp((u - 0.1) / 0.18), 2.0)
            ctx.save(); ctx.translate(W / 2, H * r["texto_y"]); ctx.rotate(math.radians(-3)); ctx.scale(max(1e-3, p), max(1e-3, p))
            ctx.select_font_face(E.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(88)
            tw = min(ctx.text_extents(r["texto"])[2], W * 0.78)
            pts = E.pts_ret(-tw / 2 - 44, -78, tw + 88, 156, r=40)   # tarja escura: lê por cima de qualquer coisa
            E.forma(ctx, pts, E.INK, sombra=True, seed=7)
            E.texto(ctx, r["texto"], 0, 0, 88, contorno=None, sombra=False, max_w=W * 0.78); ctx.restore()
    elif e == "triste":
        k = clamp(u / 0.3)
        _tinge(ctx, cairo.OPERATOR_HSL_SATURATION, (0.5, 0.5, 0.5), 0.8 * k)
        _tinge(ctx, cairo.OPERATOR_MULTIPLY, (0.45, 0.6, 1.0), 0.55 * k)
        _vinheta(ctx, 0.6 * k, (0.02, 0.04, 0.15))
    elif e == "dramatico":
        _tinge(ctx, cairo.OPERATOR_OVERLAY, (0.2, 0.15, 0.3), 0.35)
        _vinheta(ctx, 0.55)
    elif e == "ohh":
        k = clamp(u / 0.06) * clamp((r["dur"] - u) / 0.15)
        _linhas_impacto(ctx, k, int(tr * FPS / 2))
    elif e == "grilo":
        _tinge(ctx, cairo.OPERATOR_HSL_SATURATION, (0.5, 0.5, 0.5), 0.35 * clamp(u / 0.3))
    elif e == "fa":
        _tinge(ctx, cairo.OPERATOR_OVERLAY, (1.0, 0.85, 0.2), 0.35 * max(0.0, 1 - u / 0.6))
        _vinheta(ctx, 0.5)


def _linhas_impacto(ctx, k, semente):
    """Linhas de mangá vindo das bordas para o centro (o miolo fica livre). Trocam a cada 2 quadros."""
    import random
    rnd = random.Random(semente)
    cx, cy = W / 2, H * 0.42
    n = 46
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-0.35, 0.35)) / n
        r0 = H * rnd.uniform(0.27, 0.36); r1 = H * 0.9; lg = rnd.uniform(8, 22)
        ux, uy = math.cos(a), math.sin(a); nx, ny = -uy, ux
        ctx.move_to(cx + ux * r0, cy + uy * r0)
        ctx.line_to(cx + ux * r1 + nx * lg, cy + uy * r1 + ny * lg)
        ctx.line_to(cx + ux * r1 - nx * lg, cy + uy * r1 - ny * lg)
        ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.95 * k); ctx.fill_preserve()
    ctx.set_line_width(4); ctx.set_source_rgba(*E.INK, 0.9 * k); ctx.stroke()


def dev_box(ctx, b):
    pts = [ctx.user_to_device(x, y) for x, y in ((b[0], b[1]), (b[2], b[1]), (b[0], b[3]), (b[2], b[3]))]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return [round(min(xs) / W, 4), round(min(ys) / H, 4), round(max(xs) / W, 4), round(max(ys) / H, 4)]


# ======================= render =======================
_F = {}


def _init(work):
    E.garante_fonte()
    _F["filme"] = Filme(work)
    _F["tex"], _F["tex_buf"] = E.textura()
    _F["surf"] = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)


def _render(args):
    fr, destino = args
    surf = _F["surf"]; ctx = cairo.Context(surf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    caixas = _F["filme"].quadro(fr, ctx, _F["tex"])
    surf.flush()
    a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    Image.fromarray(a[..., 2::-1].copy()).save(destino % fr if "%" in destino else destino, compress_level=1)
    return fr, {"|".join(map(str, k[:2])): [v, k[2], k[3], k[4]] for k, v in caixas.items()}


def qa_cena(filme, boxes):
    """Revisão por quadro: texto na faixa da legenda (60-72% da altura), fora da zona segura, textos sobrepostos."""
    issues, out = [], {}
    janelas = [(r["t0"], r["t0"] + r["dur"]) for c in filme.cenas for r in c.reacoes]
    em_reacao = lambda fr: any(a <= (fr - 1) / FPS < b for a, b in janelas)
    for fr, bx in boxes.items():
        out[fr] = {}
        textos = []
        for nome, (b, tipo, entrou, pode) in bx.items():
            el, parte = nome.split("|")
            if parte == "rosto":
                fb = [b[0], b[1], b[2], b[1] + (b[3] - b[1]) / 0.55]
                out[fr][("pipo_" if tipo == "pipo" else "rosto_") + el] = fb
                if b[3] > 0.60 and b[1] < 0.72:
                    issues.append({"tipo": "rosto_na_faixa_legenda", "alvo": el, "frame": fr})
            elif parte == "texto" and entrou:
                out[fr]["texto_" + el] = b
                textos.append((el, b, pode))
                vis_y = min(b[3], 0.72) - max(b[1], 0.60)
                if vis_y > 0.005:
                    issues.append({"tipo": "texto_na_faixa_legenda", "alvo": el, "frame": fr})
                if b[0] < 0.03 or b[2] > 0.97 or b[1] < 0.07 or b[3] > 0.84:
                    issues.append({"tipo": "fora_zona_segura", "alvo": el, "frame": fr})
            elif parte == "corpo":
                out[fr][el] = b
        for i in range(len(textos)):
            for j in range(i + 1, len(textos)):
                (e1, b1, p1), (e2, b2, p2) = textos[i], textos[j]
                if p1 or p2:
                    continue
                ix = max(0, min(b1[2], b2[2]) - max(b1[0], b2[0])); iy = max(0, min(b1[3], b2[3]) - max(b1[1], b2[1]))
                amin = min((b1[2] - b1[0]) * (b1[3] - b1[1]), (b2[2] - b2[0]) * (b2[3] - b2[1])) or 1
                if ix * iy / amin > 0.08:
                    issues.append({"tipo": "imagens_sobrepostas", "alvo": f"{e1}+{e2}", "frame": fr})
    # numa reação de meme (≤1,2 s) o zoom empurra coisas para a faixa da legenda de propósito: não acusa
    issues = [i for i in issues if not (em_reacao(i["frame"]) and i["tipo"] in ("texto_na_faixa_legenda", "rosto_na_faixa_legenda", "fora_zona_segura"))]
    return {"motor": "kit2d", "issues": issues, "boxes": out}


def eventos(filme):
    shots = [int(round(c.t0 * FPS)) + 1 for c in filme.cenas]
    sfx = [s for c in filme.cenas for s in c.sons] + [s for c in filme.cenas for el in c.els for s in el.sons]
    sfx += filme.cfg.get("sfx", [])
    mus = filme.cfg.get("musica", "percussao")
    ev = {"N": filme.N, "fps": FPS, "shots": shots, "cortes": shots, "sfx": sorted(sfx, key=lambda s: s[1]),
          "music": som(mus) if isinstance(mus, str) else mus, "pills": [], "motor": "kit2d"}
    if filme.cfg.get("musica_inicio"):
        ev["music_offset"] = filme.cfg["musica_inicio"]
    w = filme.cfg.get("whoosh_nos_cortes", True)
    ev["shot_whoosh"] = som("whoosh") if w is True else (som(w) if w else None)
    ev["shot_whoosh_gain"] = filme.cfg.get("volume_whoosh", 0.22)
    if filme.cfg.get("silencios"):
        ev["music_gaps"] = filme.cfg["silencios"]
    return ev


def folha(paths, out, cols=8):
    ims = [Image.open(p).resize((216, 384)) for p in paths]
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (cols * 216, rows * 384))
    for i, im in enumerate(ims):
        sh.paste(im, ((i % cols) * 216, (i // cols) * 384))
    sh.save(out, quality=85)


def main():
    work = os.path.abspath(sys.argv[1])
    J = int(os.environ.get("PIPO_JOBS", os.cpu_count() or 2))
    t_ini = time.time(); c_ini = os.times()
    filme = Filme(work)
    if "--quadros" in sys.argv or "--previa" in sys.argv:
        if "--previa" in sys.argv:
            frs = [int(1 + i * 1.5 * FPS) for i in range(int(filme.N / FPS / 1.5) + 1)]
        else:
            frs = [int(x) for x in sys.argv[sys.argv.index("--quadros") + 1].split(",")]
        os.makedirs(f"{work}/prev", exist_ok=True)
        with Pool(J, _init, (work,)) as p:
            p.map(_render, [(f, f"{work}/prev/p%04d.png") for f in frs])
        paths = [f"{work}/prev/p{f:04d}.png" for f in frs]
        if "--previa" in sys.argv:
            folha(paths, f"{work}/previa.jpg"); print("folha:", f"{work}/previa.jpg")
        else:
            print("\n".join(paths))
        return
    os.makedirs(f"{work}/frames", exist_ok=True)
    for f in os.listdir(f"{work}/frames"):
        if f.endswith(".png") and int(f[1:5]) > filme.N:
            os.remove(f"{work}/frames/{f}")
    boxes = {}
    with Pool(J, _init, (work,)) as p:
        for fr, bx in p.imap_unordered(_render, [(f, f"{work}/frames/f%04d.png") for f in range(1, filme.N + 1)], chunksize=8):
            boxes[fr] = bx
    json.dump(eventos(filme), open(f"{work}/events.json", "w"), indent=1, ensure_ascii=False)
    qa = qa_cena(filme, dict(sorted(boxes.items())))
    json.dump(qa, open(f"{work}/qa_scene.json", "w"))
    c_fim = os.times()
    cpu = (c_fim.children_user + c_fim.children_system + c_fim.user + c_fim.system) - (c_ini.children_user + c_ini.children_system + c_ini.user + c_ini.system)
    tipos = {}
    for i in qa["issues"]:
        tipos[(i["tipo"], i["alvo"])] = tipos.get((i["tipo"], i["alvo"]), 0) + 1
    print(f"OK {filme.N} quadros ({filme.N / FPS:.1f} s) em {time.time() - t_ini:.1f} s de relógio, {cpu:.1f} s de CPU, {J} processos")
    for (tp, al), n in sorted(tipos.items()):
        print(f"  QA: {tp} {al}: {n} quadros")


if __name__ == "__main__":
    main()
