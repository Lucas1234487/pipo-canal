"""ESTADO.md compacto para a posse (Órion de Vídeo, 28/11): o Diretor lê ESTE arquivo em vez de ~20 docs.

Uso: python3 kit/estado.py <pasta da branch fila> [saida.md]   (padrão: docs/diretor/ESTADO.md)
Teto: 14 mil caracteres (~4 mil tokens). Passou disso, o script corta e avisa (linter de orçamento).
Os docs de origem continuam sendo a verdade; este é só o resumo gerado. Nunca edite à mão.
"""
import glob, json, os, re, sys
from datetime import datetime, timedelta

KIT = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.normpath(os.path.join(KIT, ".."))
sys.path.insert(0, KIT)
import guardrails, tem_trabalho  # noqa: E402

TETO = 14000


def ler(p):
    try:
        return open(os.path.join(RAIZ, p)).read()
    except Exception:
        return ""


def secao(txt, titulo):
    """Corpo da seção '## <titulo...>' até a próxima '## '."""
    m = re.search(r"^##\s*" + re.escape(titulo) + r".*?$\n(.*?)(?=^##\s|\Z)", txt, re.M | re.S)
    return m.group(1).strip() if m else ""


def linha_video(fila, nome):
    p = os.path.join(fila, nome)
    try:
        m = json.load(open(os.path.join(p, "meta.json")))
    except Exception:
        m = {}
    n, _ = guardrails.notas_gemini(p)
    q = open(os.path.join(p, "qa_claude.md")).read() if os.path.exists(os.path.join(p, "qa_claude.md")) else ""
    v = re.findall(r"VEREDITO[^:\n]*:\s*\**\s*(APROVA|CORRIGE|REPROVA)", q, re.I)
    qa = v[-1].upper() if v else ("dispensado" if "dispensado" in q.lower() else "-")
    ag = "sim" if tem_trabalho.agendado_ok(p) else "NÃO"
    return f"| {nome} | {m.get('tema', m.get('titulo', '?'))[:60]} | {m.get('aposta', '-')} | {sum(n)/len(n):.1f} | {qa} | {ag} |" if n else \
           f"| {nome} | {m.get('tema', m.get('titulo', '?'))[:60]} | {m.get('aposta', '-')} | - | {qa} | {ag} |"


def gerar(fila, agora=None):
    agora = agora or datetime.now()
    out = [f"# ESTADO do PipoPop (gerado por kit/estado.py em {agora:%d/%m %H:%M}; não editar)", ""]
    t = tem_trabalho.triagem(fila, agora)
    out += ["## Agora", f"- produzir: {t['produzir'] or '-'} · agendar: {t['agendar'] or '-'} · trava ativa: {t['trava_ativa']} · comentários pendentes: {t['comentarios_pendentes']}", ""]
    ini = (agora - timedelta(days=7)).date().isoformat()
    vids = sorted(n for n in os.listdir(fila) if re.match(r"\d{4}-\d\d-\d\d_[MHC]$", n) and n >= ini) if os.path.isdir(fila) else []
    out += ["## Fila, últimos 7 dias (evite repetir tema)", "| pasta | tema | aposta | Gemini | QA-Claude | agendado |", "|---|---|---|---|---|---|"]
    out += [linha_video(fila, n) for n in vids] + [""]
    pautas = ler("docs/sistema/PAUTAS.md")
    out += ["## Pedidos do Lucas (prioridade)", secao(pautas, "Pedidos do Lucas") or "-", ""]
    usadas = secao(pautas, "Usadas").splitlines()[-12:]
    out += ["## Pautas usadas (últimas 12)"] + usadas + [""]
    dec = ler("docs/diretor/DECISOES_LUCAS.md")
    out += ["## Decisões do Lucas", re.sub(r"^#.*\n", "", dec).strip(), ""]
    hs = sorted(glob.glob(os.path.join(RAIZ, "docs/diretor/handovers/*.md")))
    if hs:
        h = open(hs[-1]).read()
        out += [f"## Último handover ({os.path.basename(hs[-1])})"]
        for s in ("Estado em uma frase", "Pendências", "1 lição"):
            c = secao(h, s)
            if c:
                out += [f"**{s}:**", c]
        out += [""]
    out += ["## Lições vivas do Diretor", re.sub(r"^#.*\n", "", ler("docs/diretor/cadernos/Diretor.md")).strip(), ""]
    out += ["## Sob demanda (não leia na posse)",
            "Bíblia e regras de roteiro: docs/biblia_do_canal.md §5-8 · crescimento: docs/sistema/06_CRESCIMENTO.md · dados: 07_DADOS.md · "
            "experimentos: docs/diretor/EXPERIMENTOS.md · placar: docs/diretor/PLACAR.md · cadernos dos papéis: docs/diretor/cadernos/"]
    txt = "\n".join(out).rstrip() + "\n"
    if len(txt) > TETO:
        txt = txt[:TETO] + f"\n\n[CORTADO: passou do teto de {TETO} caracteres; enxugue a fonte maior]\n"
    return txt


if __name__ == "__main__":
    from zoneinfo import ZoneInfo
    fila = sys.argv[1] if len(sys.argv) > 1 else "fila"
    saida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(RAIZ, "docs/diretor/ESTADO.md")
    txt = gerar(fila, datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None))
    open(saida, "w").write(txt)
    print(f"{saida}: {len(txt)} caracteres (~{len(txt)//4} tokens), teto {TETO}")
