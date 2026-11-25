#!/usr/bin/env python3
"""Merge do som (O3) no cenas.json (O2). Uso: python3 merge_som.py WORK"""
import json, sys, os

work = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
cenas = json.load(open(os.path.join(work, "cenas.json")))
som = json.load(open(os.path.join(work, "som.json")))
lista = cenas["cenas"] if isinstance(cenas, dict) and "cenas" in cenas else cenas

# (a) chaves do topo
for k, v in som.get("topo", {}).items():
    cenas[k] = v

# (b) acoes
nao_casou = []
for i, a in enumerate(som.get("acoes", [])):
    cs = [c for c in lista if c.get("em") == a.get("cena_em")]
    if len(cs) != 1:
        nao_casou.append((i, "cena_em %r: %d cenas" % (a.get("cena_em"), len(cs)))); continue
    c = cs[0]
    if a.get("elemento") is None:
        if a.get("faz") != "reacao":
            nao_casou.append((i, "elemento null sem faz=reacao")); continue
        nova = {k: v for k, v in a.items() if k not in ("cena_em", "elemento")}
        c.setdefault("acoes", []).append(nova)
        continue
    alvo = [x for x in c.get("acoes", [])
            if x.get("alvo", x.get("elemento", x.get("id"))) == a["elemento"]
            and x.get("em") == a.get("em") and x.get("faz") == a.get("faz")]
    if len(alvo) != 1:
        nao_casou.append((i, "acao %s/%s/%s: %d casamentos" % (a["elemento"], a.get("em"), a.get("faz"), len(alvo)))); continue
    for k in ("som", "volume"):
        if k in a:
            alvo[0][k] = a[k]

if nao_casou:
    print("NAO CASOU:")
    for i, m in nao_casou:
        print("  acao", i, m)
    sys.exit(1)
json.dump(cenas, open(os.path.join(work, "cenas.json"), "w"), ensure_ascii=False, indent=1)
print("merge ok: topo=%d chaves, acoes=%d" % (len(som.get("topo", {})), len(som.get("acoes", []))))
