# Eval 2026-11-09 — gemini / gemini-2.5-flash

Cases: 34, answered: 6 (6 with errors, 0 correct). Provider failures: 28 (excluded from the metrics below).

| Metric | Value |
|---|---|
| Detection (error cases) | 67% |
| Category recall | 67% |
| Category precision | 100% |
| Corrected text matches gold | 67% |
| False positives on correct input | — |
| Transfer source right | 33% |
| Transfer flagged (gold transfer, detected) | 50% |
| transfer_source filled when flagged | 100% |
| Latency mean / median / max, s | 7.487 / 3.609 / 24.671 |

## Per category

| Category | P | R | tp | fp | fn |
|---|---|---|---|---|---|
| article | 100% | 100% | 1 | 0 | 0 |
| gender | 100% | 100% | 1 | 0 | 0 |
| lexical | — | 0% | 0 | 0 | 2 |
| register | — | 0% | 0 | 0 | 1 |
| ser_estar | 100% | 100% | 1 | 0 | 0 |
| spelling_accent | 100% | 100% | 1 | 0 | 0 |

## Misses

- `roman-2026-10-31-bus` gold ['register', 'lexical']: no correction
- `roman-2026-10-queue` gold ['lexical']: no correction

## Provider failures (not scored)

- `syn-gender-1`: fallback
- `syn-gender-2`: fallback
- `syn-agreement-1`: fallback
- `syn-agreement-2`: fallback
- `syn-serestar-1`: fallback
- `syn-tense-1`: fallback
- `syn-tense-2`: fallback
- `syn-mood-1`: fallback
- `syn-mood-2`: fallback
- `syn-prep-1`: fallback
- `syn-prep-2`: fallback
- `syn-clitic-1`: fallback
- `syn-clitic-2`: fallback
- `syn-order-1`: fallback
- `syn-order-2`: fallback
- `syn-lexical-1`: fallback
- `syn-lexical-2`: fallback
- `syn-lexical-3`: fallback
- `syn-accent-1`: fallback
- `syn-accent-2`: fallback
- `syn-register-1`: fallback
- `syn-register-2`: fallback
- `syn-clean-porfa`: fallback
- `syn-clean-mepones`: fallback
- `syn-clean-cola`: fallback
- `syn-clean-calefaccion`: fallback
- `syn-clean-aproveche`: fallback
- `syn-clean-avena`: fallback
