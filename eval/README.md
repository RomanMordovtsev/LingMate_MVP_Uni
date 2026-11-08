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
```

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
