#!/usr/bin/env python3
"""Base de dados do canal (pedido do Lucas, 26/11): tudo vira dado, no git.

Arquivos (pasta dados/):
  videos.jsonl    1 linha por vídeo: características (o que FIZEMOS).
  posts.jsonl     1 linha por vídeo x rede: id, horário, caminho (metricool/buffer/studio).
  metricas.jsonl  1 linha por medição: vídeo x rede x momento (24h, 72h, 7d, 30d) com N métricas.

Uso:
  python3 kit/dados.py video <pasta_da_fila>          registra/atualiza as características
  python3 kit/dados.py post <pasta> <rede> <id> <iso> <caminho>
  python3 kit/dados.py metrica <pasta> <rede> <janela> '<json com métricas>'
  python3 kit/dados.py tabela [saida.csv]              junta tudo numa tabela (1 linha por vídeo x rede x janela)
  python3 kit/dados.py analise                          comparação por característica (rodar na semanal; regressão na mensal)
Métricas padrão (preencher as que a rede der): views, alcance, curtidas, comentarios, compartilhamentos,
salvamentos, seguidores_ganhos, retencao_media_pct, visualizado_pct (Visualizado vs. Deslizado),
duracao_media_s, cliques_perfil.
"""
import json, os, sys, re, subprocess
from datetime import datetime

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dados")
os.makedirs(RAIZ, exist_ok=True)


def _ler(nome):
    p = os.path.join(RAIZ, nome)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def _escrever(nome, linhas):
    with open(os.path.join(RAIZ, nome), "w") as f:
        for l in linhas:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")


def _upsert(nome, chave, novo):
    L = [l for l in _ler(nome) if not all(l.get(k) == novo.get(k) for k in chave)]
    L.append(novo)
    _escrever(nome, L)


def caracteristicas(pasta):
    nome = os.path.basename(os.path.normpath(pasta))
    meta = json.load(open(os.path.join(pasta, "meta.json"))) if os.path.exists(os.path.join(pasta, "meta.json")) else {}
    rot = {}
    for cand in ("roteiro.json",):
        p = os.path.join(pasta, cand)
        if os.path.exists(p):
            rot = json.load(open(p))
    up = os.path.join(pasta, "upload.mp4")
    dur = None
    if os.path.exists(up):
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", up],
                             capture_output=True, text=True).stdout.strip()
        dur = round(float(out), 1) if out else None
    m = re.search(r"_([MHC])$", nome)
    desc = meta.get("descricao", "")
    tags = meta.get("hashtags") or re.findall(r"#\w+", desc)
    gem = os.path.join(pasta, "avaliacao_gemini.md")
    notas = []
    if os.path.exists(gem):
        notas = [float(x.replace(",", ".")) for x in re.findall(r"Nota[^:\n]*:?\**\s*\**\s*(\d+(?:[.,]\d+)?)\s*/\s*10", open(gem).read())]
    return {
        "video": nome,
        "data": nome[:10],
        "pilar": m.group(1) if m else meta.get("pilar"),
        "aposta": meta.get("aposta") or rot.get("aposta"),
        "titulo": meta.get("titulo"),
        "titulo_len": len(meta.get("titulo", "")),
        "titulo_tem_numero": bool(re.search(r"\d", meta.get("titulo", ""))),
        "titulo_tem_pergunta": "?" in meta.get("titulo", ""),
        "descricao_len": len(desc),
        "hashtags": tags, "n_hashtags": len(tags),
        "comentario_fixado": meta.get("comentario_fixado"),
        "interacao": meta.get("interacao"), "humor": meta.get("humor"),
        "duracao_s": dur,
        "horario": meta.get("horario_sugerido") or meta.get("horario"),
        "gancho": rot.get("gancho") or (rot.get("falas") or [{}])[0].get("texto") if isinstance(rot.get("falas"), list) else rot.get("gancho"),
        "tema": meta.get("tema") or rot.get("tema"),
        "emocao": meta.get("emocao") or rot.get("emocao"),
        "reconhecivel": meta.get("reconhecivel") or rot.get("reconhecivel"),
        "estilo_animacao": meta.get("estilo_animacao", "2D kit2d"),
        "versao_pipo": meta.get("versao_pipo", "espiga/pipoca 2D v1"),
        "voz": meta.get("voz"), "musica": meta.get("musica"),
        "foto_real": os.path.isdir(os.path.join(pasta, "img")),
        "meme": meta.get("meme"), "erro_proposital": meta.get("erro_proposital"),
        "serie": meta.get("serie"), "parte": meta.get("parte"),
        "nota_gemini": round(sum(notas) / len(notas), 2) if notas else None,
        "experimentos": meta.get("experimentos"),
        "registrado_em": datetime.now().isoformat(timespec="minutes"),
    }


def tabela(saida=None):
    V = {v["video"]: v for v in _ler("videos.jsonl")}
    linhas = []
    for m in _ler("metricas.jsonl"):
        row = dict(V.get(m["video"], {"video": m["video"]}))
        row.update({"rede": m["rede"], "janela": m["janela"]})
        row.update({k: v for k, v in m.get("metricas", {}).items()})
        linhas.append(row)
    if saida:
        import csv
        cols = sorted({k for r in linhas for k in r})
        with open(saida, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for r in linhas:
                w.writerow({k: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for k, v in r.items()})
    return linhas


def analise(janela="72h"):
    L = [r for r in tabela() if r.get("janela") == janela and r.get("views") is not None]
    if not L:
        print("sem métricas ainda"); return
    print(f"n = {len(L)} (vídeo x rede, janela {janela})")
    for chave in ("rede", "pilar", "aposta", "emocao", "reconhecivel", "titulo_tem_numero", "titulo_tem_pergunta", "foto_real", "meme", "estilo_animacao"):
        g = {}
        for r in L:
            g.setdefault(str(r.get(chave)), []).append(r)
        if len(g) < 2: continue
        print(f"\n{chave}:")
        for k, rs in sorted(g.items(), key=lambda x: -sum(r["views"] for r in x[1]) / len(x[1])):
            mv = sum(r["views"] for r in rs) / len(rs)
            sh = sum(r.get("compartilhamentos") or 0 for r in rs) / len(rs)
            sg = sum(r.get("seguidores_ganhos") or 0 for r in rs) / len(rs)
            print(f"  {k:<24} n={len(rs):<3} views={mv:9.0f} compart={sh:6.1f} seguidores={sg:5.1f}")
    print("\nAtenção: com n pequeno é sinal, não prova. Regressão só na mensal, com n >= 60 e poucas variáveis.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "video":
        c = caracteristicas(a[1]); _upsert("videos.jsonl", ["video"], c); print(json.dumps(c, ensure_ascii=False)[:400])
    elif a[0] == "post":
        _upsert("posts.jsonl", ["video", "rede"], {"video": a[1].rstrip("/").split("/")[-1], "rede": a[2], "id": a[3], "publicado": a[4], "caminho": a[5]})
    elif a[0] == "metrica":
        _upsert("metricas.jsonl", ["video", "rede", "janela"], {"video": a[1].rstrip("/").split("/")[-1], "rede": a[2], "janela": a[3],
                                                               "metricas": json.loads(a[4]), "coletado": datetime.now().isoformat(timespec="minutes")})
    elif a[0] == "tabela":
        print(len(tabela(a[1] if len(a) > 1 else os.path.join(RAIZ, "tabela.csv"))), "linhas")
    elif a[0] == "analise":
        analise(a[1] if len(a) > 1 else "72h")
