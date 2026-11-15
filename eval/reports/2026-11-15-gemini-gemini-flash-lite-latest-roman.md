# Eval 2026-11-15 — gemini / gemini-flash-lite-latest — profile roman

Profile: **roman** (prompts include the profile context and transfer hints; 35/35 cases match its target language).

Cases: 35, answered: 34 (28 with errors, 6 correct). Provider failures: 1 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 89% |
| Category recall | 79% |
| Category precision | 88% |
| Corrected text matches gold | 79% |
| False positives on correct input | 0% |
| Transfer source right | 73% |
| Transfer flagged (gold transfer, detected) | 91% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 1.085 / 1.083 / 1.495 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 67% | 67% | 2 | 1 | 1 |
| article | 100% | 100% | 1 | 0 | 0 |
| clitic | 100% | 100% | 2 | 0 | 0 |
| gender | 75% | 75% | 3 | 1 | 1 |
| lexical | 100% | 50% | 3 | 0 | 3 |
| mood | 100% | 50% | 1 | 0 | 1 |
| preposition | 67% | 100% | 2 | 1 | 0 |
| register | — | 0% | 0 | 0 | 2 |
| ser_estar | 100% | 100% | 2 | 0 | 0 |
| spelling_accent | 100% | 100% | 3 | 0 | 0 |
| tense_aspect | 100% | 100% | 2 | 0 | 0 |
| word_order | 100% | 50% | 1 | 0 | 1 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: a la cero → a las cero [agreement]
- `syn-article-1` gold ['article', 'gender']: la máster → el máster [gender]
- `syn-mood-2` gold ['mood']: no correction
- `syn-order-2` gold ['word_order', 'agreement']: muy bueno → muy buen [gender]
- `syn-lexical-3` gold ['lexical']: a la ventana → junto a la ventana [preposition]
- `syn-register-1` gold ['register']: no correction

## Provider failures (not scored)

- `syn-register-2`: fallback
