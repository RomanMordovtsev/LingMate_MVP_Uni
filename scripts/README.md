# scripts

## nightly_eval.ps1 — weekly model comparison (Windows)
Runs `python -m eval.run` for the Gemini models and every local Ollama model and
writes reports to `eval/reports/`. Needs the folder's `.venv`, `.env` (Gemini key)
and Ollama installed. Manual run (PowerShell, in the repo folder):

    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\nightly_eval.ps1

Every model runs twice: without a profile (legacy prompts) and with `--profile roman`
(profile context + transfer hints). At the end `python -m eval.compare` writes
`eval/reports/compare-<date>.md` (without → with, per model: detection, text match,
false positives, transfer source, `lexical` and `register` recall). Put that table into
the Monday report. Only one variant: `-Profiles ""` or `-Profiles roman`.
Note: gemini-2.5-flash free tier (20 requests/day) cannot finish even one run; the
second run stops at once on the quota (no wasted retries).

Scheduled: Windows Task Scheduler task "LingMate nightly eval", Monday 01:30.
A Claude scheduled task bound to Roman's computer then picks up the new reports
and opens a PR into `agent/dev`.
