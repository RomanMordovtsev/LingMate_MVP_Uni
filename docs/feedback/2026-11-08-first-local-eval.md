# First local eval run on Roman's computer, 08.11.2026

`scripts/nightly_eval.ps1` run by hand on Windows (agent/dev @ 03d46f6, 34 cases).

| Model | Detection | Text matches gold | FP on correct | Transfer src | Provider failures | Mean latency |
|---|---|---|---|---|---|---|
| gemini-flash-lite-latest | 50% | 46% | 0% | 0% | **14/34** | 1.8 s |
| gemini-2.5-flash | 43% | 32% | 0% | 9% | **17/34** | 4.8 s |
| ollama qwen2.5:7b-instruct | **7%** | 7% | 0% | 0% | 0 | **18.3 s** |

## Findings → fix in eval / app
1. **Report file names are truncated at the first dot**: `gemini-2.5-flash` → `2026-11-08-gemini-gemini-2.*`, `qwen2.5:7b-instruct` → `…-ollama-qwen2.*` (looks like `with_suffix`/`stem` on the model name). Different models would overwrite each other. Sanitise the model name (replace `:`/`/` etc.) and append the extension, don't use `with_suffix`. Add a test with `gemini-2.5-flash` and `qwen2.5:7b-instruct`.
2. **Gemini provider failures (14–17 of 34)** — free-tier rate limits (429/503). Failed calls must not be scored as misses: report metrics over answered cases and show failures separately (check what scoring does now), and add `--sleep SECONDS` between cases (default ~4 s for gemini, 0 for ollama) plus a longer backoff/retry for 429 in eval mode. Otherwise the comparison is unfair.
3. **qwen2.5:7b is not usable for corrections** (7% detection, 18 s per answer). It was answering in Roman's 05.11 manual test. Note in AGENT_LOG; roadmap 5.6/5.7 should look for better local candidates within Roman's hardware limits.
4. `print(to_markdown(report))` crashed with `UnicodeEncodeError` (cp1251 console) after reports were written. Script now sets `PYTHONIOENCODING=utf-8`; make `eval.run` robust anyway (reconfigure stdout to utf-8 or `errors="replace"`).
5. Transfer source is almost never right (0–9%) — check whether models fill `transfer_source` at all; maybe the prompt needs a clearer instruction.
