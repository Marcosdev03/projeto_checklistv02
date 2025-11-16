#!/usr/bin/env bash
set -euo pipefail

# scripts/build_frontend_and_collectstatic.sh
# 1) Instala dependências do frontend
# 2) Cria build (Vite)
# 3) Copia `frontend/dist` para `staticfiles/frontend`
# 4) Roda collectstatic do Django (settings de dev: local_sqlite)

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
STATIC_TARGET="$ROOT_DIR/staticfiles/frontend"

echo "[frontend build] working directory: $FRONTEND_DIR"

if ! command -v npm >/dev/null 2>&1; then
  echo "ERROR: npm não encontrado. Instale Node.js/npm e tente novamente." >&2
  exit 2
fi

pushd "$FRONTEND_DIR" >/dev/null

echo "Installing frontend dependencies (this may take a while)..."
npm install --no-audit --no-fund

echo "Building frontend (vite)..."
npm run build

echo "Copying build to project staticfiles..."
mkdir -p "$STATIC_TARGET"
rm -rf "$STATIC_TARGET"/* || true
cp -r dist/* "$STATIC_TARGET/"

popd >/dev/null

echo "Running Django collectstatic (local_sqlite)..."
python3 manage.py collectstatic --noinput --settings=config.settings.local_sqlite

echo "Done. Built frontend copied to: $STATIC_TARGET"
