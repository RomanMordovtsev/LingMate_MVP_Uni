# LingMate: weekly model comparison on Roman's Windows computer (roadmap 5.6).
# Run by Windows Task Scheduler (see scripts/README.md). Uses the local .env
# (Gemini key) and the local Ollama; keys never leave this computer.
# Output: eval/reports/*.json + *.md, and eval/reports/nightly-<date>.log.

param(
    [string[]]$GeminiModels = @("gemini-flash-lite-latest", "gemini-2.5-flash"),
    [string[]]$OllamaModels = @()   # empty = every model from `ollama list`
)

$ErrorActionPreference = "Continue"
Set-Location (Join-Path $PSScriptRoot "..")
$date = Get-Date -Format "yyyy-MM-dd"
New-Item -ItemType Directory -Force -Path "eval\reports" | Out-Null
$log = "eval\reports\nightly-$date.log"
function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Tee-Object -FilePath $log -Append }

Log "start"
git fetch origin 2>&1 | Out-Null
git checkout agent/dev 2>&1 | Out-File -Append $log
git pull --ff-only 2>&1 | Out-File -Append $log

$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Log "no .venv found, stopping"; exit 1 }
& $py -m pip install -q -r requirements.txt 2>&1 | Out-File -Append $log

foreach ($m in $GeminiModels) {
    Log "gemini $m"
    & $py -m eval.run --provider gemini --model $m 2>&1 | Out-File -Append $log
}

# Make sure Ollama is up.
try { Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 5 | Out-Null }
catch { Log "starting ollama"; Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 15 }

if ($OllamaModels.Count -eq 0) {
    try { $OllamaModels = (Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 10).models.name }
    catch { Log "ollama not reachable, skipping local models" }
}
foreach ($m in $OllamaModels) {
    if ($m -match "embed") { continue }
    Log "ollama $m"
    & $py -m eval.run --provider ollama --model $m 2>&1 | Out-File -Append $log
}
Log "done"
