# Roman, 21.11.2026 — placement test must be generic (after PR #20)

PR #20 merged. Roman hasn't taken the test yet (will do later).

**Finding:** 12 of 29 placement items come from Roman's own situations (`docs/learner`). Every learner has a different path, so a placement test built on one person's errors is not fair or valid for others. The **entry test must work for everyone**:
- Items written from level descriptors, not from one learner: CEFR CV 2020 can-do + PCIC inventories per level (grammar, functions, notions), balanced across error categories and skills; neutral everyday contexts (not Vitoria-specific); valid for any L1 (no RU-only traps).
- Keep the adaptive mechanism (`core/placement.py`) — it is fine.
- Move Roman-specific items out of the placement bank: they belong to **personal diagnostics/review** (error log 1.6, mastery C.4, SRS 3.1), which come after placement.
- Document per item which descriptor/PCIC point it tests (`source` field) and its target level; add a test that no placement item references `docs/learner`.
- Later (needs real users, 5.4/5.5): calibrate item difficulty from answers of many learners; until then mark levels as provisional.
- If the bank becomes too small after removing Roman's items, write new generic items to keep ≥6 per level.
