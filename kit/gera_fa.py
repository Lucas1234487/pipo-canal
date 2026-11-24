"""Gera o efeito "Fá" do canal (grito curto de uma sílaba com eco, queda de tom e corte seco), 100% nosso.
O "FAAH" que viralizou é de um streamer (não é livre): este é refeito do zero com edge-tts + processamento.
Uso: python3 kit/gera_fa.py   -> assets/sfx/memes/fa.ogg (pt-BR-AntonioNeural) e fa2.ogg (pt-BR-FranciscaNeural)
"""
import certifi, os
if os.path.exists("/root/.ccr/ca-bundle.crt"):
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import asyncio, subprocess, tempfile, wave
import edge_tts
import numpy as np
from scipy.signal import fftconvolve, lfilter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
TEXTO, RATE, PITCH = "FÁÁÁÁÁÁ!", "-25%", "+70Hz"


def rd(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.int16).astype(float) / 32768


def lp(s, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], s)


def processa(x, total=1.5, queda=0.55, seed=1):
    env = np.convolve(np.abs(x), np.ones(480) / 480, "same"); on = np.where(env > env.max() * 0.08)[0]
    x = x[max(0, on[0] - int(0.02 * SR)):on[-1] + int(0.03 * SR)]
    x = x / np.abs(x).max()
    x = x + 1.2 * (lp(x, 5000) - lp(x, 1500))            # presença (cara de grito)
    x = np.tanh(2.2 * x) / np.tanh(2.2)                    # saturação
    n = len(x); k0 = int(n * 0.55); pos = []; p = 0.0      # queda de tom: "fita desacelerando" nos últimos 45%
    while p < n - 1:
        pos.append(p); p += 1.0 if p < k0 else 1.0 - (1 - queda) * min(1, (p - k0) / (n - k0))
    y = np.interp(np.array(pos), np.arange(n), x)
    L = int(1.2 * SR); rng = np.random.default_rng(seed)  # reverb: cauda de ruído que decai (IR gerada aqui)
    ir = rng.standard_normal(L) * np.exp(-np.arange(L) / SR / 0.28); ir[:int(0.012 * SR)] = 0; ir /= np.abs(ir).sum() ** 0.5 * 8
    wet = fftconvolve(y, ir)[:len(y) + L]; wet = np.concatenate([wet, np.zeros(len(y) + L - len(wet))])
    dry = np.concatenate([y, np.zeros(L)]); ec = np.zeros_like(dry)
    for d, g in ((0.11, 0.45), (0.22, 0.28), (0.33, 0.16)):  # eco
        s = int(d * SR); ec[s:] += dry[:len(dry) - s] * g
    mix = dry + 0.55 * ec + 0.9 * wet
    N = int(total * SR); mix = np.concatenate([mix, np.zeros(max(0, N - len(mix)))])[:N]
    f = int(0.004 * SR); mix[-f:] *= np.linspace(1, 0, f)   # corte seco
    return mix / np.abs(mix).max() * 0.708


def main():
    out = os.path.join(REPO, "assets/sfx/memes"); os.makedirs(out, exist_ok=True)
    for nome, voz, seed, ganho_db in (("fa", "pt-BR-AntonioNeural", 1, -3.6), ("fa2", "pt-BR-FranciscaNeural", 2, -5.0)):
        with tempfile.TemporaryDirectory() as td:
            mp3 = f"{td}/v.mp3"; wv = f"{td}/v.wav"
            asyncio.run(edge_tts.Communicate(TEXTO, voz, rate=RATE, pitch=PITCH).save(mp3))
            y = processa(rd(mp3), seed=seed)
            w = wave.open(wv, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes()); w.close()
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wv, "-af", f"volume={ganho_db}dB,alimiter=limit=0.708:attack=2:release=60:level=false",
                            "-ar", "48000", "-ac", "1", "-c:a", "libvorbis", "-q:a", "6", f"{out}/{nome}.ogg"], check=True)
        print("OK", f"{out}/{nome}.ogg")


if __name__ == "__main__":
    main()
