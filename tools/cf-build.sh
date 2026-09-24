#!/usr/bin/env bash
# Build dla Cloudflare Pages: kopiuje stronę do dist/ bez panelu, skryptów PHP i plików roboczych.
# Ustawienia projektu w Cloudflare Pages:  Build command: bash tools/cf-build.sh   ·   Output directory: dist
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist && mkdir dist
tar --exclude='./dist' --exclude='./admin' --exclude='./api' --exclude='./content' --exclude='./tools' \
    --exclude='./node_modules' --exclude='./.git' --exclude='./.github' --exclude='*.md' --exclude='.htaccess' \
    --exclude='package.json' --exclude='package-lock.json' --exclude='.gitignore' --exclude='.DS_Store' \
    -cf - . | tar -xf - -C dist
echo "dist/ gotowy: $(find dist -type f | wc -l | tr -d ' ') plików"
