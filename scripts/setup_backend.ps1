$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location "$Root\backend"

if (Get-Command python -ErrorAction SilentlyContinue) {
  python -m venv .venv
} else {
  py -3.11 -m venv .venv
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Write-Host "Backend environment ready at backend\.venv"

