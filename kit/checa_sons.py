"""Confere se cada efeito sonoro é audível em alto-falante de celular (que quase não toca grave).
python3 kit/checa_sons.py [pasta ...]   (padrão: assets/sfx)
Simula o celular com passa-alta de 300 Hz e acusa arquivo cujo pico fica abaixo de -14 dB (some no celular)."""
import glob, os, re, subprocess, sys
pastas = sys.argv[1:] or ["assets/sfx"]
ruins = 0
for p in pastas:
    for f in sorted(glob.glob(os.path.join(p, "**", "*.*"), recursive=True)):
        if not f.lower().endswith((".ogg", ".wav", ".mp3", ".flac")):
            continue
        o = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "highpass=f=300:poles=2,highpass=f=300:poles=2,volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
        m = re.search(r"max_volume: (-?[\d.]+) dB", o)
        if m and float(m.group(1)) < -14:
            ruins += 1
            print(f"SOME NO CELULAR ({m.group(1)} dB): {f}")
print("ok" if not ruins else f"{ruins} arquivo(s) fracos no celular")
