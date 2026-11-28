"""Testes das guardas do modo enxuto (Órion de Vídeo, 28/11).
Rodar: python3 -m pytest -q kit/testes   (ou python3 kit/testes/test_guardas.py)
"""
import json, os, subprocess, sys, tempfile

KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, KIT)
import guardrails  # noqa: E402

GEM_OK = "Perfil 1\nNota: 8 / 10\nPerfil 2\nNota: 8.5 / 10\nSem erro grave.\n"
GEM_BAIXA = "Nota: 7 / 10\nNota: 7 / 10\n"


def pasta(qa, gem=GEM_OK, meta=None):
    d = tempfile.mkdtemp(prefix="2026-11-29_C_")
    d2 = d + "_C"
    os.rename(d, d2)
    open(os.path.join(d2, "qa_claude.md"), "w").write(qa)
    open(os.path.join(d2, "avaliacao_gemini.md"), "w").write(gem)
    json.dump(meta or {"aposta": "seguro"}, open(os.path.join(d2, "meta.json"), "w"))
    return d2


def item(d, chave):
    R = guardrails.checa(d)
    return [i for i in R.itens if i[1] == chave][0][0]


def test_dispensa_sem_gatilho_passa():
    assert item(pasta("QA-Claude dispensado: formato recorrente, nota 8,2"), "qa_claude") == "OK"


def test_dispensa_com_nota_baixa_falha():
    assert item(pasta("QA-Claude dispensado: pressa", gem=GEM_BAIXA), "qa_claude") == "FALHA"


def test_dispensa_com_ousado_falha():
    assert item(pasta("QA-Claude dispensado: x", meta={"aposta": "ousado"}), "qa_claude") == "FALHA"


def test_dispensa_sem_gemini_falha():
    d = pasta("QA-Claude dispensado: x")
    os.remove(os.path.join(d, "avaliacao_gemini.md"))
    assert item(d, "qa_claude") == "FALHA"


def test_dispensa_com_erro_grave_falha():
    assert item(pasta("QA-Claude dispensado: x", gem="Nota: 9 / 10\nHá um fato errado no segundo 12."), "qa_claude") == "FALHA"


def test_veredito_aprova_continua_valendo():
    assert item(pasta("## VEREDITO: APROVA"), "qa_claude") == "OK"


def test_sem_veredito_nem_dispensa_falha():
    assert item(pasta("rascunho"), "qa_claude") == "FALHA"


def test_buffer_recusa_video_sem_pasta():
    r = subprocess.run([sys.executable, os.path.join(KIT, "buffer.py"), "agendar", "--rede", "youtube",
                        "--video", "https://x/y.mp4", "--quando", "2026-11-29T12:07:00-03:00"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "--pasta" in r.stderr


def test_buffer_recusa_pasta_reprovada():
    d = pasta("rascunho")  # sem upload.mp4, sem veredito -> guardrails reprova
    r = subprocess.run([sys.executable, os.path.join(KIT, "buffer.py"), "agendar", "--rede", "youtube", "--pasta", d,
                        "--video", "https://x/y.mp4", "--quando", "2026-11-29T12:07:00-03:00"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "guardrails" in r.stderr


import tem_trabalho  # noqa: E402
from datetime import datetime  # noqa: E402


def fila_fake(pastas, trava=None):
    f = tempfile.mkdtemp()
    for n, ok in pastas.items():
        os.makedirs(os.path.join(f, n))
        if ok:
            json.dump({"youtube": {"id": 1}, "meta_ig_fb": {"instagram": "x"}}, open(os.path.join(f, n, "agendado.json"), "w"))
    if trava:
        json.dump({"inicio": trava}, open(os.path.join(f, "_trava_producao.json"), "w"))
    return f


def test_vigia_noite_sem_trabalho():
    # sáb 28/11 20:23: slots de hoje já passaram; amanhã ainda não existe (é da madrugada) -> nada
    r = tem_trabalho.triagem(fila_fake({}), datetime(2026, 11, 28, 20, 23))
    assert not r["produzir"] and not r["agendar"]


def test_vigia_manha_produz_pilar_faltando():
    r = tem_trabalho.triagem(fila_fake({"2026-11-28_M": True}), datetime(2026, 11, 28, 9, 23))
    assert r["produzir"] == ["2026-11-28_H", "2026-11-28_C"]


def test_vigia_respeita_trava():
    r = tem_trabalho.triagem(fila_fake({}, trava="2026-11-28T08:00:00-03:00"), datetime(2026, 11, 28, 9, 23))
    assert r["trava_ativa"] and not r["produzir"]


def test_vigia_acha_pasta_sem_agendar():
    r = tem_trabalho.triagem(fila_fake({"2026-11-29_M": False, "2026-11-29_H": True}), datetime(2026, 11, 28, 20, 23))
    assert r["agendar"] == ["2026-11-29_M"]


if __name__ == "__main__":
    fs = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for f in fs:
        f(); print("ok", f.__name__)
    print(len(fs), "testes ok")
