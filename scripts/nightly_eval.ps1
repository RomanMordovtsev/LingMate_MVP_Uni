# LingMate: weekly model comparison on Roman's Windows computer (roadmap 5.6).
# Run by Windows Task Scheduler (see scripts/README.md). Uses the local .env
# (Gemini key) and the local Ollama; keys never leave this computer.
# Output: eval/reports/*.json + *.md, and eval/reports/nightly-<date>.log.

param(
    [string[]]$GeminiModels = @("gemini-flash-lite-latest", "gemini-3.1-flash-lite"),
    [string[]]$OllamaModels = @(),  # empty = every model from `ollama list`
    # Each model runs once per profile: "" = no profile (legacy prompts), "roman" =
    # eval/profiles/roman.json (profile context + transfer hints), so the report shows
    # whether the hints help (docs/feedback/2026-11-11).
    [string[]]$Profiles = @("", "roman"),
    # LanguageTool (rule-based checker, docs/feedback/2026-11-14 §2): one run alone, then
    # eval.hybrid combines it with every LLM report of the night (no extra model calls).
    # Uses $env:LANGUAGETOOL_URL if set (local server), else the public API (~2 min).
    [switch]$NoLanguageTool
)

$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"   # Windows console is cp1251; eval prints Spanish text
$env:PYTHONUTF8 = "1"
Set-Location (Join-Path $PSScriptRoot "..")
$date = Get-Date -Format "yyyy-MM-dd"
New-Item -ItemType Directory -Force -Path "eval\reports" | Out-Null
$log = "eval\reports\nightly-$date.log"
function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Out-File -Append -Encoding utf8 $log }
function RunEval($provider, $model) {
    foreach ($p in $Profiles) {
        $extra = @()
        if ($p) { $extra = @("--profile", $p) }
        Log "$provider $model profile=$(if ($p) { $p } else { 'none' })"
        & $py -m eval.run --provider $provider --model $model @extra 2>&1 | Out-File -Append -Encoding utf8 $log
    }
}

Log "start"
git fetch origin 2>&1 | Out-Null
git checkout agent/dev 2>&1 | Out-File -Append -Encoding utf8 $log
# Reports from earlier runs are committed to agent/dev by the pickup PRs; the local
# untracked copies would block `git pull` ("untracked files would be overwritten").
# Move every untracked report that is not from today into a gitignored archive.
$archive = "eval\reports\_local_archive"
New-Item -ItemType Directory -Force -Path $archive | Out-Null
git ls-files --others --exclude-standard eval/reports | ForEach-Object {
    $name = Split-Path $_ -Leaf
    if ($name -notmatch $date -and $name -ne "README.md") { Move-Item -Force $_ (Join-Path $archive $name) }
}
git pull --ff-only 2>&1 | Out-File -Append -Encoding utf8 $log
if ($LASTEXITCODE -ne 0) { Log "ERROR: git pull failed - running OLD code; see lines above"; }
Log ("code: " + (git log --oneline -1))

$py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Log "no .venv found, stopping"; exit 1 }
& $py -m pip install -q -r requirements.txt 2>&1 | Out-File -Append -Encoding utf8 $log

foreach ($m in $GeminiModels) {
    RunEval "gemini" $m
}

if (-not $NoLanguageTool) {
    Log "languagetool $(if ($env:LANGUAGETOOL_URL) { $env:LANGUAGETOOL_URL } else { 'public API' })"
    & $py -m eval.run --provider languagetool 2>&1 | Out-File -Append -Encoding utf8 $log
}

# Make sure Ollama is up.
try { Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 5 | Out-Null }
catch { Log "starting ollama"; Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 15 }

# Candidate list maintained by the agent (roadmap 5.7). Missing models are pulled
# if there is enough free disk space; installed models are never deleted here.
$cand = "eval\model_candidates.txt"
if ($OllamaModels.Count -eq 0 -and (Test-Path $cand)) {
    $OllamaModels = Get-Content $cand | ForEach-Object { ($_ -split "#")[0].Trim() } | Where-Object { $_ }
    try { $have = (Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 10).models.name } catch { $have = @() }
    $modelsDir = if ($env:OLLAMA_MODELS) { $env:OLLAMA_MODELS } else { "$env:USERPROFILE\.ollama" }
    $freeGB = [math]::Round((Get-PSDrive ($modelsDir.Substring(0,1))).Free / 1GB)
    foreach ($m in $OllamaModels) {
        if ($have -contains $m -or $have -contains "${m}:latest") { continue }
        if ($freeGB -lt 20) { Log "skip pull ${m}: only $freeGB GB free on $modelsDir"; continue }
        Log "pull $m"
        ollama pull $m 2>&1 | Out-File -Append -Encoding utf8 $log
    }
}
if ($OllamaModels.Count -eq 0) {
    try { $OllamaModels = (Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 10).models.name }
    catch { Log "ollama not reachable, skipping local models" }
}
foreach ($m in $OllamaModels) {
    if ($m -match "embed") { continue }
    RunEval "ollama" $m
}
Log "compare (no profile vs profile)"
& $py -m eval.compare --out "eval\reports\compare-$date.md" 2>&1 | Out-File -Append -Encoding utf8 $log
if (-not $NoLanguageTool) {
    Log "hybrid (LLM alone vs LLM + LanguageTool)"
    & $py -m eval.hybrid --out "eval\reports\hybrid-$date.md" 2>&1 | Out-File -Append -Encoding utf8 $log
}
Log "done"
