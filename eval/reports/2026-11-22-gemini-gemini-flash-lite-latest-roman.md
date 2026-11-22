# Eval 2026-11-22 — gemini / gemini-flash-lite-latest — profile roman

Profile: **roman** (prompts include the profile context and transfer hints; 39/39 cases match its target language).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 85% |
| Category recall | 79% |
| Category precision | 93% |
| Corrected text matches gold | 76% |
| False positives on correct input | 0% |
| Transfer source right | 69% |
| Transfer flagged (gold transfer, detected) | 92% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 1.116 / 1.088 / 1.512 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 33% | 1 | 0 | 2 |
| article | 100% | 50% | 1 | 0 | 1 |
| clitic | 100% | 100% | 2 | 0 | 0 |
| gender | 60% | 75% | 3 | 2 | 1 |
| lexical | 100% | 62% | 5 | 0 | 3 |
| mood | 100% | 75% | 3 | 0 | 1 |
| preposition | 100% | 100% | 2 | 0 | 0 |
| register | 100% | 33% | 1 | 0 | 2 |
| ser_estar | 100% | 100% | 2 | 0 | 0 |
| spelling_accent | 100% | 100% | 3 | 0 | 0 |
| tense_aspect | 100% | 100% | 2 | 0 | 0 |
| word_order | 100% | 50% | 1 | 0 | 1 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: no correction
- `syn-article-1` gold ['article', 'gender']: la máster → el máster [gender]
- `syn-agreement-2` gold ['agreement', 'article']: Las clases de la máster son interesante. → Las clases del máster son interesantes. [gender]
- `syn-mood-2` gold ['mood']: no correction
- `syn-order-2` gold ['word_order', 'agreement']: muy bueno → muy buen [gender]
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → por favor, ¿podría dármelo? [register]
- `syn-lexical-en-3` gold ['lexical']: comprometer → conectar [lexical]
