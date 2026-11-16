# LingMate: download the Ollama candidates from eval/model_candidates.txt (roadmap 5.7).
# Separate from the eval (docs/feedback/2026-11-16 §3): pulls took 1.5 h on 15.11 and ate
# the eval's time limit. Run it any time before Sunday 19:00 (by hand or as its own task),
# and nightly_eval.ps1 calls it again at the END of the night for anything still missing.
# Reads the list from origin/agent/dev without touching the working tree. Only missing
# models are pulled; installed ones are never deleted here. Log: eval\reports\pull-<date>.log
# (progress bars stripped by `python -m eval.logfilter`).

param(
    [int]$MinFreeGB = 20,
    [string]$Log = ""
)

$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
Set-Location (Join-Path $PSScriptRoot "..")
New-Item -ItemType Directory -Force -Path "eval\reports" | Out-Null
if (-not $Log) { $Log = "eval\reports\pull-$(Get-Date -Format 'yyyy-MM-dd').log" }
function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Out-File -Append -Encoding utf8 $Log }
$py = ".\.venv\Scripts\python.exe"

git fetch origin 2>&1 | Out-Null
$list = git show origin/agent/dev:eval/model_candidates.txt 2>$null
if (-not $list) { $list = Get-Content "eval\model_candidates.txt" }
$models = $list | ForEach-Object { ($_ -split "#")[0].Trim() } | Where-Object { $_ }

try { Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 5 | Out-Null }
catch { Log "starting ollama"; Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 15 }
try { $have = (Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 10).models.name }
catch { Log "ollama not reachable, nothing pulled"; exit 1 }

$modelsDir = if ($env:OLLAMA_MODELS) { $env:OLLAMA_MODELS } else { "$env:USERPROFILE\.ollama" }
$missing = @($models | Where-Object { -not ($have -contains $_ -or $have -contains "${_}:latest") })
if ($missing.Count -eq 0) { Log "pull: all $($models.Count) candidates installed"; exit 0 }

$tmp = Join-Path $env:TEMP "lingmate-pull"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
foreach ($m in $missing) {
    $freeGB = [math]::Round((Get-PSDrive ($modelsDir.Substring(0,1))).Free / 1GB)
    if ($freeGB -lt $MinFreeGB) { Log "skip pull ${m}: only $freeGB GB free on $modelsDir"; continue }
    Log "pull $m"
    $t0 = Get-Date
    # Start-Process keeps ollama's raw output out of PowerShell's error stream (no
    # NativeCommandError noise); the filter drops the redrawn progress bars.
    $p = Start-Process ollama -ArgumentList "pull", $m -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput "$tmp\out.txt" -RedirectStandardError "$tmp\err.txt"
    & $py -m eval.logfilter "$tmp\out.txt" "$tmp\err.txt" 2>&1 | Out-File -Append -Encoding utf8 $Log
    Log "pull $m exit=$($p.ExitCode) in $([math]::Round(((Get-Date) - $t0).TotalMinutes)) min"
}
