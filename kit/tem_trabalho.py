"""Triagem barata da vigia (Órion de Vídeo, 28/11): "há algo a fazer?" sem gastar modelo.

Uso: python3 kit/tem_trabalho.py <pasta da branch fila> [--agora 2026-11-28T20:23] [--json]
Saída 0 = nada a fazer (a vigia só coleta métricas e encerra); 10 = há trabalho (lista no stdout).

Olha:
- pilares (M, H, C) de hoje cujo horário (guardrails.SLOTS) ainda não passou e que não têm pasta na fila;
- pastas de hoje e de amanhã sem agendado.json completo (youtube + meta_ig_fb);
- trava de produção ativa (< 5 h): se ativa, não manda produzir;
- comentários pendentes (feito=false), que só importam se o Chrome do Lucas responder.
"""
import json, os, sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guardrails import SLOTS  # noqa: E402

PILARES = "CMH"  # ordem dos slots do dia (03_CICLO §3: C no 1º, M no 2º, H no 3º; corrigido 28/11)
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def agendado_ok(p):
    try:
        a = json.load(open(os.path.join(p, "agendado.json")))
    except Exception:
        return False
    return bool(a.get("youtube")) and bool(a.get("meta_ig_fb"))


def triagem(fila, agora):
    out = {"agora": agora.isoformat(timespec="minutes"), "produzir": [], "agendar": [], "trava_ativa": False,
           "comentarios_pendentes": 0}
    tv = os.path.join(fila, "_trava_producao.json")
    if os.path.exists(tv):
        try:
            ini = datetime.fromisoformat(json.load(open(tv))["inicio"]).replace(tzinfo=None)
            out["trava_ativa"] = agora - ini < timedelta(hours=5)
        except Exception:
            out["trava_ativa"] = True  # trava ilegível: falha fechada (não produz)
    pastas = set(os.listdir(fila)) if os.path.isdir(fila) else set()
    hoje = agora.date()
    for dia in (hoje, hoje + timedelta(days=1)):
        for i, pil in enumerate(PILARES):
            nome = f"{dia.isoformat()}_{pil}"
            hh, mm = map(int, SLOTS[dia.weekday()][i].split(":"))
            slot = datetime(dia.year, dia.month, dia.day, hh, mm)
            if nome in pastas:
                if not agendado_ok(os.path.join(fila, nome)) and slot > agora:
                    out["agendar"].append(nome)
            elif dia == hoje and slot - agora > timedelta(hours=2) and not out["trava_ativa"]:
                out["produzir"].append(nome)  # só se ainda dá tempo (2 h de folga); amanhã é da madrugada
    try:
        L = json.load(open(os.path.join(RAIZ, "docs", "diretor", "redes", "comentarios_pendentes.json")))
        out["comentarios_pendentes"] = sum(1 for x in L if not x.get("feito"))
    except Exception:
        pass
    return out


if __name__ == "__main__":
    from zoneinfo import ZoneInfo
    v = sys.argv[sys.argv.index("--agora") + 1] if "--agora" in sys.argv else None
    a = [x for x in sys.argv[1:] if not x.startswith("--") and x != v]
    agora = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)  # horário do canal, não do servidor
    if "--agora" in sys.argv:
        agora = datetime.fromisoformat(sys.argv[sys.argv.index("--agora") + 1])
    r = triagem(a[0] if a else "fila", agora)
    print(json.dumps(r, ensure_ascii=False) if "--json" in sys.argv else
          f"produzir: {r['produzir'] or '-'} | agendar: {r['agendar'] or '-'} | trava: {r['trava_ativa']} | comentários: {r['comentarios_pendentes']}")
    sys.exit(10 if (r["produzir"] or r["agendar"]) else 0)
