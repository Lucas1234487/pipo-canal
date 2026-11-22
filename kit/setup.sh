#!/bin/bash
# Prepara o ambiente de producao do canal (rodar 1x por sessao). Uso: bash setup.sh
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"
ldconfig -p | grep -q libEGL.so.1 || (apt-get install -y -q libegl1 libgl1 libxkbcommon0 libsm6 libxi6 libxrender1 libxxf86vm1 libxfixes3 >/dev/null 2>&1 || (apt-get update -q >/dev/null && apt-get install -y -q libegl1 libgl1 libxkbcommon0 libsm6 libxi6 libxrender1 libxxf86vm1 libxfixes3 >/dev/null))   # bpy aborta sem libEGL
python3 -c "import bpy" 2>/dev/null || pip install --break-system-packages -q bpy
python3 -c "import edge_tts" 2>/dev/null || pip install --break-system-packages -q edge-tts
python3 -c "import numpy, PIL" 2>/dev/null || pip install --break-system-packages -q numpy pillow
[ -d "$KIT/sfx" ] || python3 "$KIT/sfx_procedural.py" "$KIT/sfx"
which ffmpeg >/dev/null
echo "KIT pronto em $KIT"
