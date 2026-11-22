"""Render paralelo: divide os quadros em J blocos (cortando nos shots), roda J processos do Blender ao mesmo tempo.
Uso: python3 render_par.py WORK/ep.py WORK [J]
Depois rode o compose.py normalmente (ele ja monta em blocos paralelos e concatena)."""
import json, os, subprocess, sys, time
ep, WORK = sys.argv[1], sys.argv[2]
J = int(sys.argv[3]) if len(sys.argv) > 3 else 2
cores = os.cpu_count() or 2
env0 = dict(os.environ, PIPO_WORK=WORK, PIPO_KIT=os.path.dirname(os.path.abspath(__file__)))
# gera events.json (shots e N) sem renderizar
subprocess.run([sys.executable, ep, "qa"], env=env0, check=True, stdout=subprocess.DEVNULL)
E = json.load(open(f"{WORK}/events.json"))
N = E["N"]
# blocos de tamanho parecido, alternando os quadros pesados: intercala por quadros (a, a+J, ...) nao funciona no Blender,
# entao usamos faixas contiguas equilibradas
size = (N + J - 1) // J
ranges = [(1 + i * size, min(N, (i + 1) * size)) for i in range(J)]
th = max(1, cores // J)
procs = []
t0 = time.time()
for a, b in ranges:
    env = dict(env0, PIPO_RANGE=f"{a}-{b}", PIPO_THREADS=str(th))
    log = open(f"{WORK}/render_{a}_{b}.log", "w")
    procs.append(subprocess.Popen([sys.executable, ep, "full"], env=env, stdout=log, stderr=subprocess.STDOUT))
codes = [p.wait() for p in procs]
print("blocos", ranges, "codigos", codes, "tempo", round(time.time() - t0), "s")
missing = [i for i in range(1, N + 1) if not os.path.exists(f"{WORK}/frames/f{i:04d}.png") or os.path.getsize(f"{WORK}/frames/f{i:04d}.png") == 0]
if missing:
    raise SystemExit(f"faltam {len(missing)} quadros, ex. {missing[:5]}: rode de novo (retoma de onde parou)")
print("OK todos os quadros")
