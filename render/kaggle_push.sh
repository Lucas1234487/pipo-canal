#!/bin/bash
# Envia uma pasta do Kaggle para um branch do GitHub. Uso: bash kaggle_push.sh <pasta> <branch> "<mensagem>"
# Precisa de GH_TOKEN no ambiente (vem dos Secrets do Kaggle). Nunca imprime o token.
set -eo pipefail
SRC=$1; BR=$2; MSG=${3:-"render do Kaggle"}
[ -n "$GH_TOKEN" ] || { echo "SEM GH_TOKEN"; exit 1; }
T=$(mktemp -d)
cd $T && git init -q && git checkout -q -b $BR
git config user.email "kaggle@pipopop" && git config user.name "PipoPop Kaggle"
cp -r $SRC/. .
git add -A && git commit -qm "$MSG"
git push -q -f "https://x-access-token:${GH_TOKEN}@github.com/Lucas1234487/pipo-canal.git" $BR 2>&1 | sed "s/${GH_TOKEN}/***/g"
echo "ENVIADO $BR"
