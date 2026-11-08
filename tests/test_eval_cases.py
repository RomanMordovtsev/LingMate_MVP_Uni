"""Validate the learner eval dataset (roadmap 1.3a). No network needed."""
import json
from pathlib import Path

CASES_DIR = Path(__file__).resolve().parent.parent / "eval" / "cases"
REQUIRED = {"id", "situation", "l1", "target", "original", "acceptable", "error_categories", "is_transfer"}


def _cases():
    for path in sorted(CASES_DIR.glob("*.jsonl")):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                yield path.name, n, json.loads(line)


def test_cases_are_well_formed_and_unique():
    ids = set()
    cases = list(_cases())
    assert cases, "no eval cases found"
    for name, n, case in cases:
        missing = REQUIRED - case.keys()
        assert not missing, f"{name}:{n} missing {missing}"
        assert case["acceptable"], f"{name}:{n}"
        if case.get("expect_correction", True):
            assert case["error_categories"], f"{name}:{n} error case without categories"
            assert case["original"] not in case["acceptable"], f"{name}:{n}"
        else:  # correct, natural utterance: any correction is a false positive
            assert case["error_categories"] == [] and case["original"] in case["acceptable"], f"{name}:{n}"
        assert case["id"] not in ids, f"duplicate id {case['id']}"
        ids.add(case["id"])


def test_every_category_has_a_case_and_clean_cases_exist():
    from core.feedback import ERROR_CATEGORIES
    cases = [c for _, _, c in _cases()]
    covered = {cat for c in cases for cat in c["error_categories"]}
    assert set(ERROR_CATEGORIES) <= covered, set(ERROR_CATEGORIES) - covered
    assert sum(not c.get("expect_correction", True) for c in cases) >= 3
