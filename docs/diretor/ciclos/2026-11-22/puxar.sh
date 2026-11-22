#!/bin/bash
# Traz o vídeo de quadros do Kaggle (branch render-out/ep003) e extrai em frames/fNNNN.png
set -e
cd /home/claude/pipo-canal && git fetch -q --depth 1 origin render-out/ep003
rm -rf /tmp/rout && mkdir /tmp/rout && git archive FETCH_HEAD | tar -x -C /tmp/rout
cat /tmp/rout/info.json
W=/home/claude/ep003; rm -rf $W/frames && mkdir -p $W/frames
FIRST=$(python3 -c "import json;print(json.load(open('/tmp/rout/info.json'))['first'])")
ffmpeg -v error -i /tmp/rout/quadros.mp4 -start_number $FIRST $W/frames/f%04d.png
ls $W/frames | wc -l
