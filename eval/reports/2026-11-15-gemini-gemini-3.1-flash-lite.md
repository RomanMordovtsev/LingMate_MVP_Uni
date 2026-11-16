# Eval 2026-11-15 — gemini / gemini-3.1-flash-lite

Profile: none (legacy prompts, no profile context or transfer hints).

Cases: 35, answered: 35 (29 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 90% |
| Category recall | 86% |
| Category precision | 93% |
| Corrected text matches gold | 76% |
| False positives on correct input | 17% |
| Transfer source right | 55% |
| Transfer flagged (gold transfer, detected) | 91% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 2.14 / 1.256 / 14.007 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 100% | 2 | 0 | 0 |
| article | 100% | 100% | 1 | 0 | 0 |
| clitic | 100% | 100% | 1 | 0 | 0 |
| gender | 100% | 100% | 3 | 0 | 0 |
| lexical | 100% | 67% | 4 | 0 | 2 |
| mood | 100% | 100% | 2 | 0 | 0 |
| preposition | 75% | 100% | 3 | 1 | 0 |
| register | 100% | 33% | 1 | 0 | 2 |
| ser_estar | 100% | 100% | 2 | 0 | 0 |
| spelling_accent | 67% | 100% | 2 | 1 | 0 |
| tense_aspect | 100% | 50% | 1 | 0 | 1 |
| word_order | 100% | 100% | 3 | 0 | 0 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: a la cero → a las doce [lexical]
- `syn-article-1` gold ['article', 'gender']: la máster → el máster [gender]
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-clitic-1` gold ['clitic', 'word_order']: la ayer → la ayer [word_order]
- `syn-lexical-3` gold ['lexical']: a la ventana → por la ventana [preposition]
- `syn-register-1` gold ['register']: no correction
- `syn-clean-aproveche` gold none: Que → ¡Que [spelling_accent]
