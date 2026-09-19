$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location "$Root\backend"
.\.venv\Scripts\Activate.ps1
alembic upgrade head
python -m app.database.run_seed

