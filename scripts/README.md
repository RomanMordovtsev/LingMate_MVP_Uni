# scripts

## nightly_eval.ps1 — weekly model comparison (Windows)
Runs `python -m eval.run` for the Gemini models and every local Ollama model and
writes reports to `eval/reports/`. Needs the folder's `.venv`, `.env` (Gemini key)
and Ollama installed. Manual run (PowerShell, in the repo folder):

    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\nightly_eval.ps1

Scheduled: Windows Task Scheduler task "LingMate nightly eval", Monday 01:30.
A Claude scheduled task bound to Roman's computer then picks up the new reports
and opens a PR into `agent/dev`.
