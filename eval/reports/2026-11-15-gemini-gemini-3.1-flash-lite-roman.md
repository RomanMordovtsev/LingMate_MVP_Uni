# Eval 2026-11-15 — gemini / gemini-3.1-flash-lite — profile roman

Profile: **roman** (prompts include the profile context and transfer hints; 35/35 cases match its target language).

Cases: 35, answered: 35 (29 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 93% |
| Category recall | 90% |
| Category precision | 93% |
| Corrected text matches gold | 72% |
| False positives on correct input | 17% |
| Transfer source right | 73% |
| Transfer flagged (gold transfer, detected) | 100% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 4.78 / 2.092 / 32.792 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 100% | 2 | 0 | 0 |
| article | 100% | 100% | 1 | 0 | 0 |
| clitic | 100% | 100% | 1 | 0 | 0 |
| gender | 100% | 100% | 3 | 0 | 0 |
| lexical | 100% | 83% | 5 | 0 | 1 |
| mood | 100% | 100% | 2 | 0 | 0 |
| preposition | 67% | 100% | 2 | 1 | 0 |
| register | 100% | 50% | 1 | 0 | 1 |
| ser_estar | 100% | 100% | 2 | 0 | 0 |
| spelling_accent | 75% | 100% | 3 | 1 | 0 |
| tense_aspect | 100% | 50% | 1 | 0 | 1 |
| word_order | 100% | 100% | 3 | 0 | 0 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: ¿puedo? → ¿puedo pasar? [lexical]
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: a la cero → a las doce [lexical]
- `syn-article-1` gold ['article', 'gender']: la máster → el máster [gender]
- `syn-article-2` gold ['article']: Busco piso cerca de universidad. → Busco un piso cerca de la universidad. [article]
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-lexical-3` gold ['lexical']: a la ventana → por la ventana [preposition]
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → ¿podría solicitarlo, por favor? [register]
- `syn-clean-aproveche` gold none: Que aproveche! → ¡Que aproveche! [spelling_accent]
