$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Join-Path $ScriptDir ".."
$VenvPython = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$DbScript = Join-Path $ProjectRoot "scripts\manage_db.py"

if (!(Test-Path $VenvPython)) {
  Write-Host "[ERROR] Virtual environment not found. Did you create it?" -ForegroundColor Red
  exit 1
}

# Ensure Python can find lounasvahti
$env:PYTHONPATH = $ProjectRoot

& $VenvPython $DbScript @args
