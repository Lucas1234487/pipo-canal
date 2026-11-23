#!/bin/bash
# Prepara um notebook do Kaggle (GPU T4, Internet ligada) para renderizar um episódio.
# Uso: bash kaggle_setup.sh ep003
set -e
EP=${1:-ep003}
mkdir -p /home/claude
[ -d /home/claude/pipo-canal ] || git clone -q --depth 1 -b render/$EP https://github.com/Lucas1234487/pipo-canal /home/claude/pipo-canal
rm -rf /home/claude/$EP && cp -r /home/claude/pipo-canal/render/$EP /home/claude/$EP
python3 -c "import bpy" 2>/dev/null || pip install -q bpy==5.3.0
(ldconfig -p | grep -q libEGL.so.1) || (apt-get install -y -q libegl1 libgl1 libxkbcommon0 libsm6 libxi6 libxrender1 libxxf86vm1 libxfixes3 >/dev/null 2>&1 || true)
nvidia-smi -L
echo PRONTO
