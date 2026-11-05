"""Validate the learner eval dataset (roadmap 5.3). No network needed."""
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
        assert case["acceptable"] and case["original"] not in case["acceptable"], f"{name}:{n}"
        assert case["id"] not in ids, f"duplicate id {case['id']}"
        ids.add(case["id"])
