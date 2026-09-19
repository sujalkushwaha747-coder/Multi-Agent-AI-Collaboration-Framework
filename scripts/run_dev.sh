#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() {
  jobs -p | xargs -r kill
}
trap cleanup EXIT

cd "$ROOT_DIR/backend"
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &

cd "$ROOT_DIR/frontend"
npm run dev &

wait

