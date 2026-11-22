# Eval 2026-11-22 — gemini / gemini-flash-lite-latest

Profile: none (legacy prompts, no profile context or transfer hints).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 85% |
| Category recall | 82% |
| Category precision | 96% |
| Corrected text matches gold | 73% |
| False positives on correct input | 0% |
| Transfer source right | 38% |
| Transfer flagged (gold transfer, detected) | 83% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 1.14 / 1.016 / 3.463 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 75% | 100% | 3 | 1 | 0 |
| article | 100% | 100% | 1 | 0 | 0 |
| clitic | 100% | 100% | 2 | 0 | 0 |
| gender | 100% | 75% | 3 | 0 | 1 |
| lexical | 100% | 50% | 4 | 0 | 4 |
| mood | 100% | 75% | 3 | 0 | 1 |
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
- `syn-lexical-2` gold ['lexical']: Estoy embarazado → Estoy acomplejado [lexical]
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → por favor, ¿podría dármelo? [register]
- `syn-lexical-en-3` gold ['lexical']: no correction
