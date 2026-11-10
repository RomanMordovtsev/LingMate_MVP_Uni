# Eval 2026-11-09 — gemini / gemini-flash-lite-latest

Cases: 34, answered: 34 (28 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 86% |
| Category recall | 86% |
| Category precision | 100% |
| Corrected text matches gold | 75% |
| False positives on correct input | 0% |
| Transfer source right | 46% |
| Transfer flagged (gold transfer, detected) | 82% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 0.956 / 0.941 / 1.522 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 100% | 3 | 0 | 0 |
| article | 100% | 100% | 1 | 0 | 0 |
| clitic | 100% | 100% | 1 | 0 | 0 |
| gender | 100% | 100% | 3 | 0 | 0 |
| lexical | 100% | 60% | 3 | 0 | 2 |
| mood | 100% | 50% | 1 | 0 | 1 |
| preposition | 100% | 100% | 2 | 0 | 0 |
| register | 100% | 33% | 1 | 0 | 2 |
| ser_estar | 100% | 100% | 2 | 0 | 0 |
| spelling_accent | 100% | 100% | 3 | 0 | 0 |
| tense_aspect | 100% | 100% | 2 | 0 | 0 |
| word_order | 100% | 100% | 2 | 0 | 0 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `syn-article-1` gold ['article', 'gender']: la máster → el máster [gender]
- `syn-mood-2` gold ['mood']: no correction
- `syn-lexical-2` gold ['lexical']: Estoy embarazado → Tengo vergüenza / Me da vergüenza [lexical]
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → por favor, ¿puede dármelo? [register]
