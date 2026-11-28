#!/usr/bin/env python3
"""Portão determinístico de qualidade do PipoPop (pedido do Lucas, 26/11).

Uso:
  python3 kit/guardrails.py <pasta_da_fila> [--pilar M|H|C] [--json]
  python3 kit/guardrails.py --todas <raiz_da_fila>

Saída: lista de checagens com OK/FALHA/AVISO. Código de saída 0 = pode agendar,
1 = bloqueado (alguma FALHA). AVISO não bloqueia, mas vai para o handover.
Nenhum vídeo é agendado em rede nenhuma sem passar aqui (G5, G7, 03_CICLO).
Os limites ficam em LIMITES; mudar um limite é decisão do Diretor registrada
em EXPERIMENTOS.md ou BASE_CONHECIMENTO.md.
"""
import json, os, re, subprocess, sys
from datetime import datetime

LIMITES = {
    "tamanho_max_mb": 3.8,
    "largura": 720, "altura": 1280,
    "duracao": {"M": (20, 45), "H": (40, 70), "C": (20, 45), "_": (15, 95)},
    "titulo_max": 60,          # YouTube corta perto de 50 no celular; >60 é falha
    "titulo_ideal": 50,
    "hashtags": (3, 5),
    "nota_gemini_min": 7.0,    # média dos perfis; Gemini é leniente (~-2)
    "lufs_alvo": -14.0, "lufs_tol": 2.5,
    "pico_max_db": -0.5,
}
SLOTS = {  # 03_CICLO: seg-qui, sex, sáb, dom
    0: ["12:07", "18:33", "21:17"], 1: ["12:07", "18:33", "21:17"],
    2: ["12:07", "18:33", "21:17"], 3: ["12:07", "18:33", "21:17"],
    4: ["11:37", "17:04", "20:43"], 5: ["10:41", "15:52", "19:06"],
    6: ["11:13", "15:38", "19:09"],
}
# GUARDRAILS §1: temas proibidos (palavra inteira, sem acento comparado em minúsculas)
PROIBIDAS = [
    r"\bbolsonaro\b", r"\blula\b", r"\bpt\b(?=.*elei)", r"\belei[cç][aã]o\b", r"\bpartido\b",
    r"\bigreja\b", r"\bjesus\b", r"\bdeus\b", r"\bpastor\b", r"\bbiblia\b", r"\bb[ií]blia\b",
    r"\bflamengo\b", r"\bcorinthians\b", r"\bpalmeiras\b", r"\bs[aã]o paulo fc\b", r"\bneymar\b",
    r"\bsele[cç][aã]o brasileira\b", r"\bcbf\b",
]
GENERICOS = ["deixa o like", "se inscreve", "se inscreva", "comenta aí", "ativa o sininho"]


class Res:
    def __init__(s): s.itens = []
    def ok(s, k, m=""): s.itens.append(("OK", k, m))
    def falha(s, k, m): s.itens.append(("FALHA", k, m))
    def aviso(s, k, m): s.itens.append(("AVISO", k, m))
    @property
    def passou(s): return not any(i[0] == "FALHA" for i in s.itens)


def ffprobe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,width,height", "-of", "json", p],
                         capture_output=True, text=True).stdout
    return json.loads(out or "{}")


def loudness(p):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", p, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
    return (float(i[-1]) if i else None, float(pk[-1]) if pk else None)


NOTA_DISPENSA_QA = 7.5   # nota Gemini mínima para dispensar o QA-Claude (modo enxuto, 28/11)


def notas_gemini(pasta):
    gp = os.path.join(pasta, "avaliacao_gemini.md")
    if not os.path.exists(gp):
        return [], ""
    g = open(gp).read()
    n = [float(x.replace(",", ".")) for x in re.findall(r"Nota[^:\n]*:?\**\s*\**\s*(\d+(?:[.,]\d+)?)\s*/\s*10", g)]
    if not n:
        n = [float(x.replace(",", ".")) for x in re.findall(r"Nota de 0 a 10\**\s*:\s*\**\s*(\d+(?:[.,]\d+)?)", g, re.I)]
    return n, g


def gatilhos_qa(pasta):
    """Gatilhos que tornam o QA-Claude obrigatório (03_CICLO, modo enxuto). Lista vazia = pode dispensar."""
    g = []
    n, txt = notas_gemini(pasta)
    if not n:
        g.append("sem nota do Gemini")
    elif sum(n) / len(n) < NOTA_DISPENSA_QA:
        g.append(f"nota Gemini {sum(n)/len(n):.1f} < {NOTA_DISPENSA_QA}")
    if re.search(r"erro grave|fato errado|ofensiv", txt, re.I) and not re.search(r"sem erro grave|nenhum erro grave|falso positivo", txt, re.I):
        g.append("Gemini citou erro grave")
    try:
        m = json.load(open(os.path.join(pasta, "meta.json")))
    except Exception:
        m = {}
    if str(m.get("aposta", "")).lower().startswith("ousad"):
        g.append("aposta ousado")
    if m.get("formato_novo") or m.get("elemento_novo"):
        g.append("formato/elemento novo")
    if m.get("tema_sensivel"):
        g.append("tema sensível")
    if m.get("qa_check_avisos"):
        g.append("aviso do qa_check")
    return g


def checa(pasta, pilar=None):
    R = Res()
    nome = os.path.basename(os.path.normpath(pasta))
    if pilar is None:
        m = re.search(r"_([MHC])$", nome)
        pilar = m.group(1) if m else "_"
    if os.path.exists(os.path.join(pasta, "segurar.json")):
        R.falha("veto", "segurar.json presente: o Lucas vetou, não agendar")

    # arquivos obrigatórios
    for f in ["upload.mp4", "meta.json", "fatos.md", "avaliacao_gemini.md", "qa_claude.md"]:
        (R.ok if os.path.exists(os.path.join(pasta, f)) else R.falha)(f"arquivo:{f}", "" if os.path.exists(os.path.join(pasta, f)) else "faltando")
    up = os.path.join(pasta, "upload.mp4")
    if os.path.exists(up):
        mb = os.path.getsize(up) / 1e6
        (R.ok if mb <= LIMITES["tamanho_max_mb"] else R.falha)("tamanho", f"{mb:.2f} MB (máx {LIMITES['tamanho_max_mb']})")
        info = ffprobe(up)
        v = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
        a = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
        if v and (v[0].get("width"), v[0].get("height")) == (LIMITES["largura"], LIMITES["altura"]):
            R.ok("resolucao", "720x1280")
        else:
            R.falha("resolucao", f"{v[0].get('width') if v else '?'}x{v[0].get('height') if v else '?'} (esperado 720x1280)")
        (R.ok if a else R.falha)("audio", "tem trilha" if a else "sem áudio")
        dur = float(info.get("format", {}).get("duration", 0))
        lo, hi = LIMITES["duracao"].get(pilar, LIMITES["duracao"]["_"])
        (R.ok if lo <= dur <= hi else R.falha)("duracao", f"{dur:.1f}s (pilar {pilar}: {lo}-{hi}s)")
        if a:
            lufs, pk = loudness(up)
            if lufs is not None:
                d = abs(lufs - LIMITES["lufs_alvo"])
                (R.ok if d <= LIMITES["lufs_tol"] else R.aviso)("lufs", f"{lufs:.1f} LUFS (alvo {LIMITES['lufs_alvo']})")
            if pk is not None:
                (R.ok if pk <= LIMITES["pico_max_db"] else R.aviso)("pico", f"{pk:.1f} dBFS")

    # meta
    meta = {}
    mp = os.path.join(pasta, "meta.json")
    if os.path.exists(mp):
        try:
            meta = json.load(open(mp))
        except Exception as e:
            R.falha("meta.json", f"JSON inválido: {e}")
    tit = meta.get("titulo", "")
    desc = meta.get("descricao", "")
    if not tit:
        R.falha("titulo", "vazio")
    elif len(tit) > LIMITES["titulo_max"]:
        R.falha("titulo", f"{len(tit)} caracteres (máx {LIMITES['titulo_max']})")
    elif len(tit) > LIMITES["titulo_ideal"]:
        R.aviso("titulo", f"{len(tit)} caracteres (ideal até {LIMITES['titulo_ideal']})")
    else:
        R.ok("titulo", f"{len(tit)} caracteres")
    tags = meta.get("hashtags") or re.findall(r"#\w+", desc)
    tags = [t if t.startswith("#") else "#" + t for t in tags]
    lo, hi = LIMITES["hashtags"]
    if not tags:
        R.falha("hashtags", "nenhuma hashtag (pedido do Lucas: obrigatório)")
    else:
        msgs = []
        if not any(t.lower() == "#pipopop" for t in tags): msgs.append("sem #PipoPop")
        if not (lo <= len(tags) <= hi): msgs.append(f"{len(tags)} hashtags (use {lo}-{hi})")
        if not all(t.lower() in desc.lower() for t in tags): msgs.append("nem todas estão no fim da descrição")
        (R.falha if "sem #PipoPop" in msgs or "nem todas" in " ".join(msgs) else (R.aviso if msgs else R.ok))("hashtags", "; ".join(msgs) or " ".join(tags))
    com = meta.get("comentario_fixado", "")
    (R.ok if com else R.falha)("comentario_fixado", com or "vazio")
    texto = " ".join([tit, desc, com]).lower()
    for g in GENERICOS:
        if g in texto:
            R.aviso("interacao", f"pedido genérico '{g}' (GUARDRAILS §3.5)")
    for pat in PROIBIDAS:
        if re.search(pat, texto):
            R.falha("tema_proibido", f"bate em '{pat}' (GUARDRAILS §1). Exceção Neymaro só como caricatura, sem nome real")
    h = meta.get("horario_sugerido") or meta.get("horario")
    if h:
        try:
            dt = datetime.fromisoformat(str(h).replace("Z", "+00:00"))
            hm = dt.strftime("%H:%M")
            (R.ok if hm in SLOTS[dt.weekday()] else R.aviso)("horario", f"{hm} ({'slot da tabela' if hm in SLOTS[dt.weekday()] else 'fora da tabela do 03_CICLO'})")
        except Exception:
            R.aviso("horario", f"não entendi '{h}'")
    else:
        R.aviso("horario", "sem horário no meta.json (usar o próximo slot)")

    # fatos: pilar C e H precisam de 2 fontes por fato central (pelo menos 2 links)
    fp = os.path.join(pasta, "fatos.md")
    if os.path.exists(fp):
        n = len(set(re.findall(r"https?://[^\s)>\]]+", open(fp).read())))
        if pilar in ("C", "H", "M"):
            (R.ok if n >= 2 else R.falha)("fontes", f"{n} links em fatos.md (mín 2)")

    # QA-Claude
    qp = os.path.join(pasta, "qa_claude.md")
    if os.path.exists(qp):
        q = open(qp).read()
        # vale o ÚLTIMO veredito do arquivo (reconferência depois da correção), sem diferenciar maiúsculas (26/11)
        vs = re.findall(r"VEREDITO[^:\n]*:\s*\**\s*(APROVA|CORRIGE|REPROVA)", q, re.I) or re.findall(r"^#.*?:\s*(APROVA|CORRIGE|REPROVA)\b", q, re.M)
        ver = vs[-1].upper() if vs else ""
        disp = re.search(r"QA-Claude dispensado\s*:\s*(\S.*)", q, re.I)
        if not vs and disp:
            # modo enxuto (28/11): QA-Claude só por gatilho. Dispensa vale se NENHUM gatilho está presente.
            gat = gatilhos_qa(pasta)
            if gat:
                R.falha("qa_claude", "dispensado, mas há gatilho: " + "; ".join(gat) + " -> rodar QA-Claude")
            else:
                R.ok("qa_claude", "dispensado (sem gatilho): " + disp.group(1).strip()[:80])
        elif ver == "APROVA" or ("CORRIGE" in ver and re.search(r"Rodada de corre[cç][aã]o|corrigid|Liberado para a fila", q, re.I)):
            R.ok("qa_claude", ver)
        elif ver == "REPROVA":
            R.falha("qa_claude", "REPROVA")
        else:
            R.falha("qa_claude", f"veredito não encontrado ou pendente ('{ver}')")

    # QA-Gemini: média das notas X / 10 e termos de erro grave
    gp = os.path.join(pasta, "avaliacao_gemini.md")
    if os.path.exists(gp):
        g = open(gp).read()
        notas = [float(x.replace(",", ".")) for x in re.findall(r"Nota[^:\n]*:?\**\s*\**\s*(\d+(?:[.,]\d+)?)\s*/\s*10", g)]
        if not notas:  # formato "Nota de 0 a 10: 9" (26/11)
            notas = [float(x.replace(",", ".")) for x in re.findall(r"Nota de 0 a 10\**\s*:\s*\**\s*(\d+(?:[.,]\d+)?)", g, re.I)]
        if notas:
            med = sum(notas) / len(notas)
            (R.ok if med >= LIMITES["nota_gemini_min"] else R.falha)("nota_gemini", f"média {med:.1f} ({len(notas)} perfis, mín {LIMITES['nota_gemini_min']})")
        else:
            R.aviso("nota_gemini", "não achei notas no formato 'Nota: X / 10'")
        if re.search(r"erro grave|fato errado|ofensiv", g, re.I) and not re.search(r"sem erro grave|nenhum erro grave|falso positivo", g, re.I):
            R.aviso("gemini_grave", "o Gemini citou erro grave: confirmar no qa_claude.md")

    # foto real: proveniência
    imgd = os.path.join(pasta, "img")
    if os.path.isdir(imgd) and any(f.lower().endswith((".jpg", ".jpeg", ".png")) for f in os.listdir(imgd)):
        pv = os.path.join(imgd, "proveniencia.tsv")
        ok = os.path.exists(pv) and re.search(r"\b(cc0|pdm|public domain|dom[ií]nio p[uú]blico|nasa)\b", open(pv).read(), re.I)
        (R.ok if ok else R.falha)("proveniencia", "licença registrada" if ok else "foto sem proveniencia.tsv com licença livre")
    return R


def imprime(nome, R, js=False):
    if js:
        print(json.dumps({"pasta": nome, "passou": R.passou, "itens": R.itens}, ensure_ascii=False))
        return
    print(f"== {nome}: {'PODE AGENDAR' if R.passou else 'BLOQUEADO'}")
    for st, k, m in R.itens:
        if st != "OK" or "-v" in sys.argv:
            print(f"  [{st}] {k}: {m}")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("-")]
    js = "--json" in sys.argv
    pil = None
    if "--pilar" in sys.argv:
        pil = sys.argv[sys.argv.index("--pilar") + 1]
        a = [x for x in a if x != pil]
    if "--todas" in sys.argv:
        raiz = a[0]
        ruim = 0
        for d in sorted(os.listdir(raiz)):
            p = os.path.join(raiz, d)
            if re.match(r"\d{4}-\d{2}-\d{2}_[MHC]$", d) and not os.path.exists(os.path.join(p, "agendado.json")):
                R = checa(p); imprime(d, R, js); ruim += not R.passou
        sys.exit(1 if ruim else 0)
    R = checa(a[0], pil)
    imprime(os.path.basename(os.path.normpath(a[0])), R, js)
    sys.exit(0 if R.passou else 1)
