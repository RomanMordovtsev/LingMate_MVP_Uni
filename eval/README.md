# Correction eval harness (roadmap 1.3a)

Runs every learner utterance in `cases/*.jsonl` through the same prompts and
normaliser as the app (`LLMService.free_talk`) and scores the structured
correction. Method: research-methods §2–3 (fixed versioned test set,
precision/recall per error category).

```bash
python -m eval.run --provider rule                                  # baseline, no model
python -m eval.run --provider ollama --model qwen2.5:7b-instruct    # local Ollama running
python -m eval.run --provider gemini --model gemini-2.5-flash       # GEMINI_API_KEY in .env
python -m eval.run --provider ollama --model llama3.1:8b --id roman-2026-10-queue   # one case
python -m eval.run --provider gemini --model gemini-2.5-flash --sleep 8   # more pause for free-tier limits
python -m eval.run --provider ollama --model qwen2.5:7b-instruct --profile roman   # as an onboarded learner
python -m eval.compare                    # table: no profile → with profile, latest date
python -m eval.run --provider languagetool                           # LanguageTool alone (no LLM)
python -m eval.run --provider ollama --model gemma4:e2b --precheck languagetool   # LLM + LanguageTool live
python -m eval.hybrid                     # table: LLM alone → LLM + LanguageTool, from saved reports
```

## LanguageTool (docs/feedback/2026-11-14 §2)
Rule-based checker, no quota. `LANGUAGETOOL_URL` picks the server: default the public API
`https://api.languagetool.org/v2` (free, ~20 requests/min → the checker waits 3.5 s between calls;
only the learner's sentence is sent), or a local server (`java -jar languagetool-server.jar --port 8081`,
then `LANGUAGETOOL_URL=http://localhost:8081/v2`, no wait). LT matches become one correction in the
same contract (`core/checkers/languagetool.py`): spelling/accents/¿¡ → `spelling_accent`, el↔la → `gender`,
ser↔estar, article, preposition, clitic, other grammar → `agreement`; style/typography/colloquialisms
are dropped so *porfa* is not flagged. Several matches: all fixes go into `corrected`, the category is
the most important one. Hybrid policy **"fill"**: the LLM's correction wins, LT fills turns without one.
`eval.hybrid` applies the same policy to the saved per-case corrections, so the nightly needs one LT run,
not one per model. Report names: `…-languagetool-public.json`, live hybrid `…-<model>-lt.json`.

## Profiles
`--profile <name>` loads `profiles/<name>.json` (validated as a `LearnerProfile`, like the
onboarding form) and runs every case of the same target language as that learner: the
prompts get the profile context (1.2) and the transfer-map hints (1.5), and corrections get
`transfer_note`, exactly as in the app. Without `--profile` the prompts are the legacy ones.
The report header says which profile was used and the file name ends with it
(`…-gemini-2.5-flash-roman.json`), so both runs of a night are kept.
`profiles/roman.json`: L1 ru, en C1, target es-ES A2, relocated, Vitoria-Gasteiz (no Italian).
Caveat: the hints were written from Roman's real errors (e.g. *línea*), so gains on the
`roman-*` cases are partly taught to the test; look at the synthetic cases.

Rate limits: `--sleep` seconds between cases (default 4 for gemini, 0 otherwise); on
429/503 the runner retries after 5, 15 and 30 s. Model names keep their dots in file names
(`gemini-2.5-flash`), `:` and `/` become `-` (`qwen2.5-7b-instruct`).

Output: `reports/<date>-<provider>-<model>.json` (every case + correction) and `.md` (summary).

## Metrics
- **Detection**: share of error cases where the tutor gave any correction.
- **Category recall / precision**: predicted `error_category` is one of the gold ones
  (one correction per turn, so recall is per case). Precision counts wrong categories and
  corrections on correct input as false positives.
- **Corrected text matches gold**: `corrected` (alone or substituted into the sentence)
  equals an `acceptable` sentence, ignoring case and punctuation, keeping accents.
- **False positives on correct input**: cases with `"expect_correction": false` (e.g.
  *porfa* in a café, docs/feedback/2026-11-05 §5) that still got a correction.
- **Transfer source right**: on transfer cases, `is_transfer` and `transfer_source` match.
  Diagnostics: *transfer flagged* (gold transfer cases with a correction where the model set
  `is_transfer`) and *transfer_source filled* (flagged corrections that name a language).
- **Provider failures** (429/503/timeouts after all retries) are listed separately and
  **excluded** from every quality metric: metrics are over answered cases.
- **Latency**: per answered call.

## Cases
- `es_roman.jsonl`: Roman's real utterances (from `docs/learner/roman-spanish.md`).
- `es_synthetic.jsonl`: 2+ per error category and 6 correct utterances, built from
  his situations (bus, café, renting, heating, postcard).
Add a case: one JSON line; error cases need `error_categories` from `core/feedback.py`
and `acceptable` must not contain `original`; correct cases set `"expect_correction": false`,
`error_categories: []` and `acceptable: [original]`. `tests/test_eval_cases.py` checks this.

API keys are read from the environment only; they are never written to reports.
