# Célula única para "Save Version" (job em segundo plano) no Kaggle. Troque EP se precisar.
import os, subprocess
from kaggle_secrets import UserSecretsClient
os.environ["GH_TOKEN"] = UserSecretsClient().get_secret("GH_TOKEN")
EP = os.environ.setdefault("EP", "ep004v2"); W, H, SPP = "1080", "1920", "16"
sh = f"""set -e; rm -rf /home/claude; mkdir -p /home/claude
git clone -q --depth 1 -b render/{EP} https://github.com/Lucas1234487/pipo-canal /home/claude/pipo-canal
bash /home/claude/pipo-canal/render/kaggle_setup.sh {EP}
python3 /home/claude/pipo-canal/render/render_kaggle.py /home/claude/{EP}/blend {W} {H} {SPP}"""
r = subprocess.run(["bash", "-c", sh]); print("SAIDA", r.returncode)
