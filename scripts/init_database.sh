#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

alembic upgrade head
python -m app.database.run_seed

