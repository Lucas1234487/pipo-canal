"""Narracao com tempos por palavra.
Uso: python3 tts.py WORK [lang]   -> le WORK/roteiro.json (ou roteiro_en.json), grava WORK/aud*/ e WORK/timing*.json
roteiro.json: {"voice": "pt-BR-ThalitaMultilingualNeural", "rate": "+6%", "pitch": "+2Hz", "lead": 0.45,
               "lines": [{"text": "...", "pause": 0.35}, ...]}
               "trim": true corta o silencio do fim de cada frase (recomendado; "trim_tail" = folga em s, padrao 0.12)
Vozes: leve PT = pt-BR-ThalitaMultilingualNeural (+6%,+2Hz) | serio PT = pt-BR-AntonioNeural (+4%,-2Hz)
       alternativas a testar: en-US-AndrewMultilingualNeural / en-US-BrianMultilingualNeural falando PT
       EN leve = en-US-EmmaMultilingualNeural (+10%,+3Hz) | EN serio = en-US-AndrewMultilingualNeural (+5%,-2Hz)
"""
import certifi, os
if os.path.exists("/root/.ccr/ca-bundle.crt"):
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import asyncio, edge_tts, json, subprocess, sys
WORK = sys.argv[1]
lang = sys.argv[2] if len(sys.argv) > 2 else ""
suf = "_" + lang if lang else ""
R = json.load(open(f"{WORK}/roteiro{suf}.json"))
AD = f"{WORK}/aud{suf}"
os.makedirs(AD, exist_ok=True)


async def one(i, t):
    c = edge_tts.Communicate(t, R["voice"], rate=R.get("rate", "+0%"), pitch=R.get("pitch", "+0Hz"), boundary="WordBoundary")
    ws = []; buf = b""
    async for ch in c.stream():
        if ch["type"] == "audio":
            buf += ch["data"]
        elif ch["type"] == "WordBoundary":
            ws.append((ch["text"], ch["offset"] / 1e7, ch["duration"] / 1e7))
    if not buf:
        raise RuntimeError("audio vazio")
    open(f"{AD}/l{i}.mp3", "wb").write(buf)
    return ws


async def go():
    out = []; t0 = R.get("lead", 0.45)
    ref = None
    if R.get("align_to_pt") and os.path.exists(f"{WORK}/timing.json"):
        ref = json.load(open(f"{WORK}/timing.json"))["lines"]   # EN alinhado frase a frase com o PT (faixa de audio do mesmo video)
    for i, ln in enumerate(R["lines"]):
        if ref and i < len(ref):
            t0 = max(t0, ref[i]["start"])
        for k in range(4):
            try:
                ws = await one(i, ln["text"]); break
            except Exception as e:
                print("retry", i, e); await asyncio.sleep(2 + 3 * k)
        else:
            raise SystemExit("TTS falhou")
        cut = []
        if R.get("trim") and ws:   # corta o silencio que o edge-tts deixa no fim de cada frase
            cut = ["-t", f"{ws[-1][1] + ws[-1][2] + R.get('trim_tail', 0.12):.3f}", "-af", "afade=t=out:st=%.3f:d=0.06" % (ws[-1][1] + ws[-1][2] + R.get('trim_tail', 0.12) - 0.06)]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{AD}/l{i}.mp3", "-ar", "48000", "-ac", "1"] + cut + [f"{AD}/l{i}.wav"], check=True)
        d = float(subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", f"{AD}/l{i}.wav"], capture_output=True, text=True).stdout)
        out.append(dict(i=i, text=ln["text"], start=t0, dur=d, words=[(w, t0 + o, du) for w, o, du in ws]))
        t0 += d + ln.get("pause", 0.3)
    json.dump(dict(lines=out, total=t0, aud=AD), open(f"{WORK}/timing{suf}.json", "w"), ensure_ascii=False, indent=1)
    print("total", round(t0, 2), "s ->", int(t0 * 30) + 25, "quadros sugeridos")


asyncio.run(go())
