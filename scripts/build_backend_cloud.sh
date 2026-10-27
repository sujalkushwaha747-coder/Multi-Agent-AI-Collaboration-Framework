#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/backend"
# Render runs CPU inference for embeddings; avoid downloading CUDA dependencies.
python -m pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install --no-cache-dir -r requirements.txt
