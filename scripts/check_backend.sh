#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:-http://localhost:8000/api/health}"

echo "Checking $API_URL"
if curl -fsS "$API_URL" >/tmp/shodhai_backend_health.json; then
  cat /tmp/shodhai_backend_health.json
  echo
  echo "Backend is reachable."
else
  echo "Backend is not reachable."
  echo "Start it with:"
  echo "  ./scripts/run_backend_local.sh"
  exit 1
fi
