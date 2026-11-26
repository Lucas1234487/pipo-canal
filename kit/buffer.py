#!/usr/bin/env python3
"""Publicação pelo Buffer (caminho 2 da cadeia do 05_CONTINUIDADE).

Chave: ~/.pipo/buffer_key (vem do Drive "PipoPop - segredos", linha BUFFER_API_KEY=).
Nunca no git.

Uso:
  python3 kit/buffer.py canais
  python3 kit/buffer.py agendar --rede instagram|facebook|youtube --video URL \
      --quando 2026-11-26T18:33:00-03:00 --texto "..." [--titulo "..."] \
      [--comentario "..."] [--tipo reel|short|story] [--imagem URL]
  python3 kit/buffer.py fila            (posts agendados por canal)

Plano grátis: 3 canais, até 10 posts na fila por canal. O script avisa quando a
fila do canal está cheia (aí usa o caminho 3, Chrome).
"""
import json, os, sys, urllib.request, argparse

API = "https://api.buffer.com"
ORG = "6b07b16bbaa038a6accbeb6f"
CANAIS = {  # ids do Buffer (26/11)
    "facebook": "6b07b2f78541f09ecba96694",   # página PipoPop
    "instagram": "6b07b2768541f09ecba9620c",  # @pipo.pop88
    "youtube": "6b07b1d58541f09ecba95bd6",    # PipoPop.
}


def chave():
    p = os.path.expanduser("~/.pipo/buffer_key")
    if os.path.exists(p):
        return open(p).read().strip()
    k = os.environ.get("BUFFER_API_KEY")
    if not k:
        sys.exit("sem chave: grave ~/.pipo/buffer_key a partir do Drive 'PipoPop - segredos'")
    return k


def gql(query, variables=None):
    req = urllib.request.Request(API, data=json.dumps({"query": query, "variables": variables or {}}).encode(),
                                 headers={"Authorization": "Bearer " + chave(), "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read())
    if out.get("errors"):
        raise RuntimeError(json.dumps(out["errors"], ensure_ascii=False))
    return out["data"]


def agendar(rede, quando, texto, video=None, imagem=None, titulo=None, comentario=None, tipo=None):
    cid = CANAIS[rede]
    # plano grátis não tem "primeiro comentário": a pergunta vai no fim da legenda
    if comentario and comentario not in texto:
        texto = texto.rstrip() + "\n\n" + comentario if "#" not in texto else texto.replace("\n\n#", "\n\n" + comentario + "\n\n#", 1)
    if video:
        assets = [{"video": {"url": video}}]
    elif imagem:
        assets = [{"image": {"url": imagem}}]
    else:
        assets = []
    meta = {}
    if rede == "instagram":
        meta["instagram"] = {"type": tipo or "reel", "shouldShareToFeed": True, "isAiGenerated": True}
    elif rede == "facebook":
        meta["facebook"] = {"type": tipo or "reel"}
    elif rede == "youtube":
        meta["youtube"] = {"type": tipo or "short", "title": (titulo or texto)[:100], "privacy": "public",
                           "madeForKids": False, "isAiGenerated": False, "notifySubscribers": True}
    inp = {"channelId": cid, "schedulingType": "automatic", "mode": "customScheduled", "dueAt": quando,
           "text": texto, "assets": assets, "metadata": meta, "needsApproval": False, "source": "pipopop-diretor"}
    q = """mutation($input: CreatePostInput!){ createPost(input:$input){
        __typename ... on PostActionSuccess { post { id dueAt status } } ... on MutationError { message } } }"""
    return gql(q, {"input": inp})["createPost"]


def fila():
    q = """query($i: PostsInput!){ posts(input:$i, first: 50){ edges{ node{ id status dueAt channelId text } } } }"""
    return gql(q, {"i": {"organizationId": ORG, "filter": {"status": ["scheduled"]}}})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("acao", choices=["canais", "agendar", "fila"])
    ap.add_argument("--rede"); ap.add_argument("--video"); ap.add_argument("--imagem")
    ap.add_argument("--quando"); ap.add_argument("--texto", default="")
    ap.add_argument("--titulo"); ap.add_argument("--comentario"); ap.add_argument("--tipo")
    a = ap.parse_args()
    if a.acao == "canais":
        print(json.dumps(gql('query($o:OrganizationId!){ channels(input:{organizationId:$o}){ id name service type } }', {"o": ORG}), indent=1, ensure_ascii=False))
    elif a.acao == "fila":
        print(json.dumps(fila(), indent=1, ensure_ascii=False))
    else:
        print(json.dumps(agendar(a.rede, a.quando, a.texto, a.video, a.imagem, a.titulo, a.comentario, a.tipo), ensure_ascii=False))
