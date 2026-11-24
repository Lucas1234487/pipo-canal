"""Gemini pela API (mão de obra barata do PipoPop). Ver docs/sistema/05_GEMINI.md.
Chave: variável GEMINI_API_KEY ou arquivo ~/.pipo/gemini_key (NUNCA no git).
Uso:
  python3 kit/gemini.py modelos
  python3 kit/gemini.py texto --prompt p.txt [--busca] [--json] [--modelo NOME] [--tipo pro|flash]
  python3 kit/gemini.py video --arquivo final.mp4 --prompt p.txt [--modelo NOME] [--tipo pro|flash]
A resposta vai para a saída padrão. Erros vão para a saída de erro com código 1 (2 = sem chave)."""
import argparse, json, os, re, ssl, sys, time, urllib.error, urllib.request

BASE = "https://generativelanguage.googleapis.com"
CA = "/root/.ccr/ca-bundle.crt"
CTX = ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()


def chave():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    f = os.path.expanduser("~/.pipo/gemini_key")
    if not k and os.path.exists(f):
        k = open(f).read().strip()
    if not k:
        sys.stderr.write("SEM CHAVE: defina GEMINI_API_KEY ou ~/.pipo/gemini_key (ver docs/sistema/05_GEMINI.md)\n")
        sys.exit(2)
    return k


def req(url, data=None, headers=None, method=None, raw=False, timeout=600):
    h = {"x-goog-api-key": chave()}
    h.update(headers or {})
    body = data if isinstance(data, (bytes, type(None))) else json.dumps(data).encode()
    if body is not None and "Content-Type" not in h:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=body, headers=h, method=method)
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(r, context=CTX, timeout=timeout) as resp:
                return resp if raw else json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf8", "ignore")[:600]
            if e.code in (429, 500, 503) and tentativa < 2:
                time.sleep(8 * (tentativa + 1)); continue
            sys.stderr.write(f"ERRO HTTP {e.code}: {msg}\n"); sys.exit(1)
        except urllib.error.URLError as e:
            if tentativa < 2:
                time.sleep(5); continue
            sys.stderr.write(f"ERRO DE REDE: {e}\n"); sys.exit(1)


def modelos():
    out, tok = [], ""
    while True:
        d = req(f"{BASE}/v1beta/models?pageSize=200" + (f"&pageToken={tok}" if tok else ""))
        out += d.get("models", [])
        tok = d.get("nextPageToken")
        if not tok:
            return out


def escolhe(tipo):
    ruins = ("tts", "image", "embed", "lyria", "live", "audio", "veo", "imagen", "aqa", "learnlm", "gemma", "robotics", "computer", "lite", "cyber")
    cands = []
    for m in modelos():
        n = m["name"].split("/")[-1]
        if "generateContent" not in m.get("supportedGenerationMethods", []) or tipo not in n or any(b in n for b in ruins):
            continue
        ver = [int(x) for x in re.findall(r"\d+", n.split(tipo)[0])][:2] or [0]
        prev = 1 if ("preview" in n or "exp" in n) else 0
        cands.append((ver, -prev, -len(n), n))
    if not cands:
        sys.stderr.write(f"nenhum modelo '{tipo}' na chave; rode 'modelos'\n"); sys.exit(1)
    return max(cands)[3]


def gerar(modelo, partes, busca=False, como_json=False):
    corpo = {"contents": [{"role": "user", "parts": partes}], "generationConfig": {"temperature": 0.7}}
    if busca:
        corpo["tools"] = [{"google_search": {}}]
    elif como_json:
        corpo["generationConfig"]["responseMimeType"] = "application/json"
    d = req(f"{BASE}/v1beta/models/{modelo}:generateContent", corpo)
    cands = d.get("candidates") or []
    if not cands:
        sys.stderr.write("RESPOSTA VAZIA: " + json.dumps(d)[:500] + "\n"); sys.exit(1)
    txt = "".join(p.get("text", "") for p in cands[0].get("content", {}).get("parts", []))
    fontes = [c.get("web", {}).get("uri") for c in cands[0].get("groundingMetadata", {}).get("groundingChunks", []) if c.get("web")]
    if fontes:
        txt += "\n\nFONTES:\n" + "\n".join(f"- {u}" for u in fontes if u)
    return txt


def sobe(caminho, mime="video/mp4"):
    tam = os.path.getsize(caminho)
    r = req(f"{BASE}/upload/v1beta/files", {"file": {"display_name": os.path.basename(caminho)}},
            headers={"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
                     "X-Goog-Upload-Header-Content-Length": str(tam), "X-Goog-Upload-Header-Content-Type": mime}, raw=True)
    url = r.headers.get("X-Goog-Upload-URL")
    d = req(url, open(caminho, "rb").read(), headers={"Content-Length": str(tam), "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize", "Content-Type": mime})
    f = d["file"]
    for _ in range(60):
        if f.get("state") == "ACTIVE":
            return f
        if f.get("state") == "FAILED":
            sys.stderr.write("o Gemini não conseguiu processar o arquivo\n"); sys.exit(1)
        time.sleep(4)
        f = req(f"{BASE}/v1beta/{f['name']}")
    sys.stderr.write("tempo esgotado processando o arquivo\n"); sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["modelos", "texto", "video"])
    ap.add_argument("--prompt"); ap.add_argument("--arquivo"); ap.add_argument("--modelo")
    ap.add_argument("--tipo", default=None); ap.add_argument("--busca", action="store_true"); ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.modo == "modelos":
        for m in modelos():
            if "generateContent" in m.get("supportedGenerationMethods", []):
                print(m["name"].split("/")[-1], "|", m.get("displayName", ""))
        return
    prompt = open(a.prompt).read() if a.prompt and os.path.exists(a.prompt) else (a.prompt or "")
    if not prompt:
        sys.stderr.write("faltou --prompt (arquivo ou texto)\n"); sys.exit(1)
    modelo = a.modelo or escolhe(a.tipo or ("pro" if a.modo == "video" else "flash"))
    sys.stderr.write(f"modelo: {modelo}\n")
    partes = [{"text": prompt}]
    if a.modo == "video":
        f = sobe(a.arquivo)
        partes = [{"file_data": {"mime_type": f.get("mimeType", "video/mp4"), "file_uri": f["uri"]}}, {"text": prompt}]
    print(gerar(modelo, partes, a.busca, a.json))


if __name__ == "__main__":
    main()
