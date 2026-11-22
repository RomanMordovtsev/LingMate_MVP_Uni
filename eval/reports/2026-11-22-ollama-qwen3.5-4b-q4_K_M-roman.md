# Eval 2026-11-22 — ollama / qwen3.5:4b-q4_K_M — profile roman

Profile: **roman** (prompts include the profile context and transfer hints; 39/39 cases match its target language).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 6% |
| Category recall | 3% |
| Category precision | 50% |
| Corrected text matches gold | 6% |
| False positives on correct input | 0% |
| Transfer source right | 0% |
| Transfer flagged (gold transfer, detected) | — |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 34.795 / 33.637 / 52.387 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 33% | 1 | 0 | 2 |
| article | — | 0% | 0 | 0 | 3 |
| clitic | — | 0% | 0 | 0 | 2 |
| gender | — | 0% | 0 | 0 | 4 |
| lexical | — | 0% | 0 | 0 | 8 |
| mood | — | 0% | 0 | 0 | 4 |
| preposition | — | 0% | 0 | 0 | 4 |
| register | — | 0% | 0 | 0 | 3 |
| ser_estar | — | 0% | 0 | 0 | 2 |
| spelling_accent | — | 0% | 0 | 0 | 3 |
| tense_aspect | 0% | 0% | 0 | 1 | 2 |
| word_order | — | 0% | 0 | 0 | 3 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-10-queue` gold ['lexical']: no correction
- `roman-2026-10-compliment` gold ['preposition', 'spelling_accent']: no correction
- `roman-2026-11-14-lift` gold ['gender', 'lexical']: no correction
- `syn-article-1` gold ['article', 'gender']: no correction
- `syn-article-2` gold ['article']: no correction
- `syn-gender-1` gold ['gender']: no correction
- `syn-gender-2` gold ['gender']: no correction
- `syn-agreement-2` gold ['agreement', 'article']: no correction
- `syn-serestar-1` gold ['ser_estar']: no correction
- `syn-serestar-2` gold ['ser_estar']: no correction
- `syn-tense-1` gold ['tense_aspect']: no correction
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-mood-1` gold ['mood']: no correction
- `syn-mood-2` gold ['mood']: Cuando llego a casa → Cuando llegue a casa [tense_aspect]
- `syn-prep-1` gold ['preposition']: no correction
- `syn-prep-2` gold ['preposition']: no correction
- `syn-clitic-1` gold ['clitic', 'word_order']: no correction
- `syn-clitic-2` gold ['clitic']: no correction
- `syn-order-1` gold ['word_order']: no correction
- `syn-order-2` gold ['word_order', 'agreement']: no correction
- `syn-lexical-1` gold ['lexical', 'preposition']: no correction
- `syn-lexical-2` gold ['lexical']: no correction
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-accent-1` gold ['spelling_accent']: no correction
- `syn-accent-2` gold ['spelling_accent']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: no correction
- `syn-mood-3` gold ['mood']: no correction
- `syn-lexical-en-3` gold ['lexical']: no correction
- `syn-mood-4` gold ['mood']: no correction
- `syn-lexical-en-4` gold ['lexical']: no correction
