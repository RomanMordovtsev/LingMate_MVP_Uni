# Eval 2026-11-22 — ollama / qwen3.5:4b-q4_K_M

Profile: none (legacy prompts, no profile context or transfer hints).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 18% |
| Category recall | 12% |
| Category precision | 67% |
| Corrected text matches gold | 6% |
| False positives on correct input | 0% |
| Transfer source right | 0% |
| Transfer flagged (gold transfer, detected) | 0% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 29.473 / 28.118 / 47.993 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | — | 0% | 0 | 0 | 3 |
| article | — | 0% | 0 | 0 | 3 |
| clitic | — | 0% | 0 | 0 | 1 |
| gender | 0% | 0% | 0 | 2 | 4 |
| lexical | — | 0% | 0 | 0 | 8 |
| mood | — | 0% | 0 | 0 | 4 |
| preposition | — | 0% | 0 | 0 | 4 |
| register | 100% | 33% | 1 | 0 | 2 |
| ser_estar | — | 0% | 0 | 0 | 2 |
| spelling_accent | — | 0% | 0 | 0 | 3 |
| tense_aspect | 100% | 50% | 1 | 0 | 1 |
| word_order | 100% | 67% | 2 | 0 | 1 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-10-queue` gold ['lexical']: no correction
- `roman-2026-10-compliment` gold ['preposition', 'spelling_accent']: no correction
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: no correction
- `syn-article-1` gold ['article', 'gender']: no correction
- `syn-article-2` gold ['article']: no correction
- `syn-gender-1` gold ['gender']: no correction
- `syn-gender-2` gold ['gender']: no correction
- `syn-agreement-1` gold ['agreement']: simpático → simpáticos [gender]
- `syn-agreement-2` gold ['agreement', 'article']: las clases de la máster → las clases de la maestra [gender]
- `syn-serestar-1` gold ['ser_estar']: no correction
- `syn-serestar-2` gold ['ser_estar']: no correction
- `syn-tense-1` gold ['tense_aspect']: no correction
- `syn-tense-2` gold ['tense_aspect']: Cuando era niño, viví en Moscú. → Cuando **estaba** niño, **vivía** en Moscú. [tense_aspect]
- `syn-mood-1` gold ['mood']: no correction
- `syn-mood-2` gold ['mood']: no correction
- `syn-prep-1` gold ['preposition']: no correction
- `syn-prep-2` gold ['preposition']: no correction
- `syn-clitic-1` gold ['clitic', 'word_order']: la ayer → ayer [word_order]
- `syn-clitic-2` gold ['clitic']: no correction
- `syn-order-2` gold ['word_order', 'agreement']: no correction
- `syn-lexical-1` gold ['lexical', 'preposition']: no correction
- `syn-lexical-2` gold ['lexical']: no correction
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-accent-1` gold ['spelling_accent']: no correction
- `syn-accent-2` gold ['spelling_accent']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: dámelo → póngame [register]
- `syn-mood-3` gold ['mood']: no correction
- `syn-lexical-en-3` gold ['lexical']: no correction
- `syn-mood-4` gold ['mood']: no correction
- `syn-lexical-en-4` gold ['lexical']: no correction
