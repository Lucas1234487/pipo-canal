#!/bin/bash
# Prepara o ambiente de producao do canal (rodar 1x por sessao). Uso: bash setup.sh
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"
python3 -c "import bpy" 2>/dev/null || pip install --break-system-packages -q bpy
python3 -c "import edge_tts" 2>/dev/null || pip install --break-system-packages -q edge-tts
python3 -c "import numpy, PIL" 2>/dev/null || pip install --break-system-packages -q numpy pillow
[ -d "$KIT/sfx" ] || python3 "$KIT/sfx_procedural.py" "$KIT/sfx"
which ffmpeg >/dev/null
echo "KIT pronto em $KIT"
