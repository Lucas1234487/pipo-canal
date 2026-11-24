"""Imagens reais para os vídeos: só CC0 ou domínio público (Openverse e NASA), com proveniência.

  python3 kit/imagens.py buscar "tyrannosaurus skeleton" WORK [--n 8] [--fonte openverse|nasa]
      baixa candidatos para WORK/img/cand/ e monta WORK/img/candidatas.jpg (olhe e escolha)
  python3 kit/imagens.py usar WORK <n>        copia a candidata n para WORK/img/fotoN.jpg e registra em WORK/img/proveniencia.tsv

No cenas.json: {"tipo": "foto", "arquivo": "/caminho/WORK/img/foto1.jpg", "largura": 700, "legenda": "...", "credito": "..."}
Nunca: foto de pessoa real identificável, logo/marca, obra de arte, still de filme/série, imagem de jogo/esporte licenciado.
"""
import json, os, ssl, sys, urllib.parse, urllib.request

CTX = ssl.create_default_context(cafile=os.path.expanduser("~/.ccr/ca-bundle.crt")) if os.path.exists(os.path.expanduser("~/.ccr/ca-bundle.crt")) else None
UA = {"User-Agent": "PipoPop/1.0 (canal educativo; contato via YouTube @pipopo.88)"}


def get(url, binario=False):
    r = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(r, context=CTX, timeout=40) as resp:
        d = resp.read()
    return d if binario else json.loads(d)


def openverse(q, n):
    d = get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": q, "license": "cc0,pdm", "page_size": n * 2}))
    out = []
    for r in d.get("results", []):
        out.append({"url": f"https://api.openverse.org/v1/images/{r['id']}/thumb/", "titulo": r.get("title", ""),
                    "autor": r.get("creator") or "?", "licenca": r.get("license", ""), "origem": r.get("foreign_landing_url") or r.get("url")})
    return out


def nasa(q, n):
    d = get("https://images-api.nasa.gov/search?" + urllib.parse.urlencode({"q": q, "media_type": "image"}))
    out = []
    for it in d["collection"]["items"][: n * 2]:
        nid = it["data"][0]["nasa_id"]
        out.append({"url": f"https://images-assets.nasa.gov/image/{urllib.parse.quote(nid)}/{urllib.parse.quote(nid)}~medium.jpg",
                    "titulo": it["data"][0].get("title", ""), "autor": "NASA", "licenca": "domínio público (NASA)",
                    "origem": f"https://images.nasa.gov/details/{nid}"})
    return out


def buscar(q, work, n=8, fonte="openverse"):
    from PIL import Image
    cand = os.path.join(work, "img", "cand"); os.makedirs(cand, exist_ok=True)
    lista = (nasa if fonte == "nasa" else openverse)(q, n)
    ok = []
    for c in lista:
        if len(ok) >= n:
            break
        try:
            dados = get(c["url"], binario=True)
            f = os.path.join(cand, f"c{len(ok)}.jpg"); open(f, "wb").write(dados)
            Image.open(f).convert("RGB").save(f, quality=92)
            ok.append(c)
        except Exception as e:
            sys.stderr.write(f"pulei {c['url'][:60]}: {e}\n")
    json.dump(ok, open(os.path.join(cand, "lista.json"), "w"), ensure_ascii=False, indent=1)
    th = 300; folha = Image.new("RGB", (th * 4, th * ((len(ok) + 3) // 4 or 1)), "white")
    for i in range(len(ok)):
        im = Image.open(os.path.join(cand, f"c{i}.jpg")); im.thumbnail((th - 10, th - 10))
        folha.paste(im, ((i % 4) * th + 5, (i // 4) * th + 5))
    folha.save(os.path.join(work, "img", "candidatas.jpg"), quality=85)
    for i, c in enumerate(ok):
        print(i, c["licenca"], c["titulo"][:50], "|", c["autor"][:30])


def usar(work, n):
    import shutil
    cand = os.path.join(work, "img", "cand"); lista = json.load(open(os.path.join(cand, "lista.json")))
    k = len([x for x in os.listdir(os.path.join(work, "img")) if x.startswith("foto")]) + 1
    dst = os.path.join(work, "img", f"foto{k}.jpg"); shutil.copy(os.path.join(cand, f"c{n}.jpg"), dst)
    c = lista[n]
    with open(os.path.join(work, "img", "proveniencia.tsv"), "a") as f:
        f.write("\t".join([os.path.basename(dst), c["titulo"], c["autor"], c["licenca"], c["origem"]]) + "\n")
    print(dst, "| crédito:", f"{c['autor']} ({c['licenca']})")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "buscar":
        n = int(a[a.index("--n") + 1]) if "--n" in a else 8
        fonte = a[a.index("--fonte") + 1] if "--fonte" in a else "openverse"
        buscar(a[1], a[2], n, fonte)
    elif a and a[0] == "usar":
        usar(a[1], int(a[2]))
    else:
        print(__doc__)
