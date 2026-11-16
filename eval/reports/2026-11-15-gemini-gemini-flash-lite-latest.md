# Eval 2026-11-15 — gemini / gemini-flash-lite-latest

Profile: none (legacy prompts, no profile context or transfer hints).

Cases: 35, answered: 35 (29 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 86% |
| Category recall | 83% |
| Category precision | 96% |
| Corrected text matches gold | 76% |
| False positives on correct input | 0% |
| Transfer source right | 46% |
| Transfer flagged (gold transfer, detected) | 91% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 1.025 / 1.01 / 1.502 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 75% | 100% | 3 | 1 | 0 |
| article | 100% | 100% | 1 | 0 | 0 |
| clitic | 100% | 100% | 2 | 0 | 0 |
| gender | 100% | 75% | 3 | 0 | 1 |
| lexical | 100% | 50% | 3 | 0 | 3 |
| mood | 100% | 50% | 1 | 0 | 1 |
| preposition | 100% | 100% | 2 | 0 | 0 |
| register | 100% | 33% | 1 | 0 | 2 |
| ser_estar | 100% | 100% | 2 | 0 | 0 |
| spelling_accent | 100% | 100% | 3 | 0 | 0 |
| tense_aspect | 100% | 100% | 2 | 0 | 0 |
| word_order | 100% | 100% | 1 | 0 | 0 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: a la cero → a las cero [agreement]
- `syn-article-1` gold ['article', 'gender']: la máster → el máster [gender]
- `syn-mood-2` gold ['mood']: no correction
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → por favor, ¿podría dármelo? [register]
