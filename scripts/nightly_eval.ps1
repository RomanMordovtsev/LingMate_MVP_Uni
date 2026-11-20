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
    [switch]$NoLanguageTool,
    # Stop starting new model runs after this many hours, so compare/hybrid still run
    # and the night ends cleanly (15.11: the 3 h Task Scheduler limit killed the run
    # mid-model). Keep it below the task's own "stop the task if it runs longer than".
    [double]$MaxHours = 9,
    # Pull missing candidates BEFORE the eval (old behaviour). Default: models that are
    # not installed yet are skipped and pulled at the end of the night by
    # scripts\pull_candidates.ps1, so downloads never eat the eval's time
    # (docs/feedback/2026-11-16 §3).
    [switch]$PullFirst
)

$ErrorActionPreference = "Continue"
$env:PYTHONIOENCODING = "utf-8"   # Windows console is cp1251; eval prints Spanish text
$env:PYTHONUTF8 = "1"
Set-Location (Join-Path $PSScriptRoot "..")
$date = Get-Date -Format "yyyy-MM-dd"   # one date for the whole night, even past midnight
$start = Get-Date
New-Item -ItemType Directory -Force -Path "eval\reports" | Out-Null
$log = "eval\reports\nightly-$date.log"
function Log($msg) { "$(Get-Date -Format 'HH:mm:ss') $msg" | Out-File -Append -Encoding utf8 $log }
function OverBudget() { ((Get-Date) - $start).TotalHours -ge $MaxHours }
function RunEval($provider, $model) {
    foreach ($p in $Profiles) {
        if (OverBudget) { Log "SKIP $provider $model profile=$(if ($p) { $p } else { 'none' }): over the $MaxHours h budget"; continue }
        $extra = @()
        if ($p) { $extra = @("--profile", $p) }
        Log "$provider $model profile=$(if ($p) { $p } else { 'none' })"
        & $py -m eval.run --provider $provider --model $model --date $date @extra 2>&1 | Out-File -Append -Encoding utf8 $log
    }
}

Log "start"
git fetch origin 2>&1 | Out-Null
git checkout agent/dev 2>&1 | Out-File -Append -Encoding utf8 $log
# Reports from earlier runs are committed to agent/dev by the pickup PRs; the local
# untracked copies would block `git pull` ("untracked files would be overwritten").
# Move ONLY the untracked reports that agent/dev already has (= already picked up).
# Reports not picked up yet stay where the pickup looks for them, whatever their date
# (docs/feedback/2026-11-16 §4: a run past midnight or a re-run the next day used to
# archive the previous night's reports before the pickup copied them).
$archive = "eval\reports\_local_archive"
New-Item -ItemType Directory -Force -Path $archive | Out-Null
$pickedUp = @(git ls-tree -r --name-only origin/agent/dev eval/reports)
git ls-files --others --exclude-standard eval/reports | ForEach-Object {
    if ($pickedUp -contains $_) { Move-Item -Force $_ (Join-Path $archive (Split-Path $_ -Leaf)) }
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
    & $py -m eval.run --provider languagetool --date $date 2>&1 | Out-File -Append -Encoding utf8 $log
}

# Make sure Ollama is up.
try { Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 5 | Out-Null }
catch { Log "starting ollama"; Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 15 }

# Candidate list maintained by the agent (roadmap 5.7). Downloads are a separate step
# (scripts\pull_candidates.ps1); here we only evaluate what is installed.
$cand = "eval\model_candidates.txt"
if ($OllamaModels.Count -eq 0 -and (Test-Path $cand)) {
    if ($PullFirst) { & (Join-Path $PSScriptRoot "pull_candidates.ps1") -Log $log }
    $OllamaModels = Get-Content $cand | ForEach-Object { ($_ -split "#")[0].Trim() } | Where-Object { $_ }
    try { $have = (Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 10).models.name } catch { $have = @() }
    $OllamaModels = @($OllamaModels | Where-Object {
        if ($have -contains $_ -or $have -contains "${_}:latest") { $true }
        else { Log "not installed yet: $_ (pulled at the end of the night)"; $false }
    })
}
if ($OllamaModels.Count -eq 0 -and -not (Test-Path $cand)) {
    try { $OllamaModels = (Invoke-RestMethod http://127.0.0.1:11434/api/tags -TimeoutSec 10).models.name }
    catch { Log "ollama not reachable, skipping local models" }
}
foreach ($m in $OllamaModels) {
    if ($m -match "embed") { continue }
    RunEval "ollama" $m
}
Log "compare (no profile vs profile)"
& $py -m eval.compare --date $date --out "eval\reports\compare-$date.md" 2>&1 | Out-File -Append -Encoding utf8 $log
if (-not $NoLanguageTool) {
    Log "hybrid (LLM alone vs LLM + LanguageTool)"
    & $py -m eval.hybrid --date $date --out "eval\reports\hybrid-$date.md" 2>&1 | Out-File -Append -Encoding utf8 $log
}
# Downloads last: new candidates are ready for next week (or run pull_candidates.ps1
# earlier by hand). Separate log: pull-<date>.log.
Log "pull missing candidates (see pull-$date.log)"
& (Join-Path $PSScriptRoot "pull_candidates.ps1") -Log "eval\reports\pull-$date.log"
Log "done"
