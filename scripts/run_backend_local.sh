#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"

cd "$BACKEND_DIR"

if [ ! -d ".venv" ]; then
  echo "Backend virtualenv not found. Creating it now..."
  "$ROOT_DIR/scripts/setup_backend.sh"
fi

source .venv/bin/activate

export APP_ENV="${APP_ENV:-development}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./shodhai_local.db}"
export CORS_ORIGIN_REGEX="${CORS_ORIGIN_REGEX:-https?://(localhost|127\.0\.0\.1):[0-9]+}"

echo "Using database: $DATABASE_URL"
echo "Applying database migrations..."
python -m alembic upgrade head

echo "Seeding benchmark prompts..."
python -m app.database.run_seed

echo "Starting FastAPI at http://127.0.0.1:8000"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
