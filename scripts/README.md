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

Scheduled: Windows Task Scheduler task "LingMate nightly eval", Sunday 19:00.
A Claude scheduled task bound to Roman's computer then picks up the new reports
and opens a PR into `agent/dev`.

### Time limit, downloads, dates (docs/feedback/2026-11-16)
- **Time budget.** `-MaxHours 9` (default): after 9 h no new model run starts; the
  night still writes `compare-`/`hybrid-` and ends cleanly. In Task Scheduler set
  "Stop the task if it runs longer than" **above** it (10 h). With the old 3 h limit
  pass `-MaxHours 2.5`.
- **Downloads are separate.** The eval only runs candidates that are already installed
  (others: `not installed yet` in the log). `scripts\pull_candidates.ps1` downloads the
  missing ones from `eval/model_candidates.txt` on `origin/agent/dev`; the nightly calls
  it at the very end, so a new candidate is evaluated the following Sunday. To have it
  the same Sunday, run it earlier by hand or as a second task (e.g. Sunday 17:00):

      powershell -NoProfile -ExecutionPolicy Bypass -File scripts\pull_candidates.ps1

  Log: `eval/reports/pull-<date>.log`, progress bars stripped (`python -m eval.logfilter`).
  `-PullFirst` on the nightly restores the old "pull, then evaluate" order.
- **One date per night.** Every report, `compare-` and `hybrid-` gets the start date
  (`eval.run --date`), even when the run crosses midnight.
- **Archive.** Before `git pull` only the untracked reports that `agent/dev` already has
  are moved to `_local_archive`; reports not picked up yet stay in `eval/reports/`
  whatever their date, so the pickup finds them after a late or repeated run.
