# Eval 2026-11-22 — ollama / granite4.1:3b

Profile: none (legacy prompts, no profile context or transfer hints).

Cases: 39, answered: 39 (33 with errors, 6 correct). Provider failures: 0 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 9% |
| Category recall | 6% |
| Category precision | 67% |
| Corrected text matches gold | 6% |
| False positives on correct input | 0% |
| Transfer source right | 0% |
| Transfer flagged (gold transfer, detected) | 0% |
| transfer_source filled when flagged | — |
| Latency mean / median / max, s | 7.98 / 7.843 / 18.123 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| agreement | 100% | 33% | 1 | 0 | 2 |
| article | — | 0% | 0 | 0 | 2 |
| clitic | — | 0% | 0 | 0 | 2 |
| gender | 0% | 0% | 0 | 1 | 4 |
| lexical | — | 0% | 0 | 0 | 8 |
| mood | — | 0% | 0 | 0 | 4 |
| preposition | — | 0% | 0 | 0 | 4 |
| register | — | 0% | 0 | 0 | 3 |
| ser_estar | 100% | 50% | 1 | 0 | 1 |
| spelling_accent | — | 0% | 0 | 0 | 3 |
| tense_aspect | — | 0% | 0 | 0 | 2 |
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
- `syn-agreement-1` gold ['agreement']: no correction
- `syn-serestar-2` gold ['ser_estar']: no correction
- `syn-tense-1` gold ['tense_aspect']: no correction
- `syn-tense-2` gold ['tense_aspect']: no correction
- `syn-mood-1` gold ['mood']: no correction
- `syn-mood-2` gold ['mood']: no correction
- `syn-prep-1` gold ['preposition']: no correction
- `syn-prep-2` gold ['preposition']: no correction
- `syn-clitic-1` gold ['clitic', 'word_order']: no correction
- `syn-clitic-2` gold ['clitic']: no correction
- `syn-order-1` gold ['word_order']: no correction
- `syn-order-2` gold ['word_order', 'agreement']: no correction
- `syn-lexical-1` gold ['lexical', 'preposition']: no correction
- `syn-lexical-2` gold ['lexical']: Estoy embarazado → Estoy embarazada [gender]
- `syn-lexical-3` gold ['lexical']: no correction
- `syn-accent-1` gold ['spelling_accent']: no correction
- `syn-accent-2` gold ['spelling_accent']: no correction
- `syn-register-1` gold ['register']: no correction
- `syn-register-2` gold ['register']: no correction
- `syn-mood-3` gold ['mood']: no correction
- `syn-lexical-en-3` gold ['lexical']: no correction
- `syn-mood-4` gold ['mood']: no correction
- `syn-lexical-en-4` gold ['lexical']: no correction
