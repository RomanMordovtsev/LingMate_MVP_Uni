# Eval 2026-11-22 — gemini / gemini-3.1-flash-lite — profile roman

Profile: **roman** (prompts include the profile context and transfer hints; 39/39 cases match its target language).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 94% |
| Category recall | 91% |
| Category precision | 94% |
| Corrected text matches gold | 70% |
| False positives on correct input | 17% |
| Transfer source right | 92% |
| Transfer flagged (gold transfer, detected) | 100% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 7.722 / 3.378 / 54.225 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 100% | 2 | 0 | 0 |
| article | 100% | 100% | 1 | 0 | 0 |
| clitic | 100% | 100% | 1 | 0 | 0 |
| gender | 100% | 100% | 3 | 0 | 0 |
| lexical | 100% | 88% | 7 | 0 | 1 |
| mood | 100% | 100% | 4 | 0 | 0 |
| preposition | 67% | 100% | 2 | 1 | 0 |
| register | 100% | 50% | 1 | 0 | 1 |
| ser_estar | 100% | 100% | 2 | 0 | 0 |
| spelling_accent | 75% | 100% | 3 | 1 | 0 |
| tense_aspect | 100% | 50% | 1 | 0 | 1 |
| word_order | 100% | 100% | 3 | 0 | 0 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: Perdona, ¿puedo? → Perdona, ¿puedo pasar? [lexical]
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: a la cero → a las doce [lexical]
- `syn-article-1` gold ['article', 'gender']: la máster → el máster [gender]
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-clitic-1` gold ['clitic', 'word_order']: la ayer → la ayer [word_order]
- `syn-order-2` gold ['word_order', 'agreement']: muy bueno → buen [word_order]
- `syn-lexical-3` gold ['lexical']: a la ventana → por la ventana [preposition]
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → me lo podría dar, por favor [register]
- `syn-clean-aproveche` gold none: Que aproveche → ¿Qué aproveche? [spelling_accent]
- `syn-lexical-en-3` gold ['lexical']: comprometer → interesar [lexical]
