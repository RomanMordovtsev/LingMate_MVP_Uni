"""Placement + diagnosis (roadmap C.2): short adaptive receptive test → level,
known gaps and the starting unit of the curriculum (C.1).

- Auto-checked without an LLM (quota strategy in ROADMAP): items live in
  `curriculum/<lang>/placement.yaml`; the answer key never leaves the server.
- Adaptive staircase by CEFR level: 4 items per level, 2 more when the result is borderline
  (2/4); pass → one level up, fail → one level down; stop when a passed level sits under a
  failed one (or at the ends). Items within a level are picked for content coverage (every
  unit of the level gets probed; research-methods §10), not in file order. The start is the profile level — only a starting point:
  the placement result, not the self-report, decides (Roman 2026-11-20: "never assume a level").
- Generic: items come from level descriptors (PCIC, CEFR CV 2020), not from one learner
  (docs/feedback/2026-11-21); their levels stay provisional until calibrated.
- Diagnosis: every wrong answer names a topic, an error category (1.3 contract) and, when
  linked, a grammar point of a unit → the start is the first open unit with a gap
  (syllabus-design §1: start from the learner's needs; morphosyntax §10: teach up to the next stage).
- Receptive knowledge is not free production (sla §6): units are only *suggested* as known,
  production prompts are stored for the tutor, and C.4 decides mastery on evidence.

Template-based: another language = another `placement.yaml` with the same shape.
"""
from __future__ import annotations

import hashlib
import random
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from core.curriculum import CURRICULUM_DIR, LEVELS, Unit, curriculum, next_units
from core.feedback import ERROR_CATEGORIES

TEST_LEVELS = ("A1", "A2", "B1", "B2")
BLOCK = 4            # items per level before a decision
EXTRA = 2            # extra items when the block is borderline
RECHECK_AFTER_UNITS = 3   # re-check every few units (C.2); used by C.4
SHUFFLE_SALT = "lingmate-placement-v1"
COVER_UNITS = True        # on a pass, use the extra items to probe units not probed yet


class Item(BaseModel):
    """One receptive item of the GENERIC entry test (docs/feedback/2026-11-21): written from a
    level descriptor (`source`), never from one learner's situations — those go to personal
    diagnostics (error log 1.6, mastery C.4, SRS 3.1)."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-c][12]-[a-z0-9-]+$")
    level: Literal["A1", "A2", "B1", "B2"]
    category: str
    topic_ru: str = Field(min_length=3)
    stem: str = Field(min_length=3)
    options: List[str] = Field(min_length=3, max_length=5)
    answer: str
    kind: Literal["gap", "meaning"] = "gap"
    grammar: Optional[str] = None       # grammar point id in curriculum/<lang>/units/*.yaml
    hint_ru: str = ""
    # Descriptor the item tests: "PCIC <band> <inventory>: <item>" and/or "CEFR CV 2020 <scale>".
    source: str = Field(pattern=r"^(PCIC|CEFR) ", min_length=12)

    @field_validator("category")
    @classmethod
    def _known(cls, v):
        if v not in ERROR_CATEGORIES:
            raise ValueError(f"unknown error category {v}")
        return v

    @model_validator(mode="after")
    def _check(self):
        if self.answer not in self.options or len(set(self.options)) != len(self.options):
            raise ValueError(f"{self.id}: answer must be one of distinct options")
        if self.kind == "gap" and "___" not in self.stem:
            raise ValueError(f"{self.id}: gap item needs ___ in the stem")
        if not self.id.startswith(self.level.lower()):
            raise ValueError(f"{self.id}: id prefix does not match level {self.level}")
        return self

    def shown_options(self) -> List[str]:
        """Options in a stable per-item shuffled order: the key position in the YAML must not
        leak (always clicking the 2nd button would otherwise "pass" levels)."""
        seed = int(hashlib.sha256(f"{SHUFFLE_SALT}:{self.id}".encode()).hexdigest(), 16)
        opts = list(self.options)
        random.Random(seed).shuffle(opts)
        return opts

    def public(self) -> dict:
        """What the client sees: no answer key."""
        return {"id": self.id, "level": self.level, "kind": self.kind, "stem": self.stem,
                "options": self.shown_options(), "hint_ru": self.hint_ru}


class ProductionPrompt(BaseModel):
    id: str
    level: Literal["A1", "A2", "B1", "B2"]
    prompt_ru: str
    prompt_es: str
    targets: List[str] = []


class PlacementBank(BaseModel):
    language: str
    variant: str
    # Item levels are provisional until calibrated on answers of many learners (5.4/5.5).
    calibration: Literal["provisional", "calibrated"] = "provisional"
    items: List[Item]
    production: List[ProductionPrompt] = []

    @model_validator(mode="after")
    def _check(self):
        ids = [i.id for i in self.items]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate item ids")
        for lvl in TEST_LEVELS:
            if sum(i.level == lvl for i in self.items) < BLOCK + EXTRA:
                raise ValueError(f"level {lvl} needs at least {BLOCK + EXTRA} items")
        return self

    def by_id(self) -> Dict[str, Item]:
        return {i.id: i for i in self.items}


def load_bank(language: str, root: Path = CURRICULUM_DIR) -> Optional[PlacementBank]:
    path = root / language / "placement.yaml"
    if not path.is_file():
        return None
    return PlacementBank.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


@lru_cache(maxsize=8)
def bank(language: str) -> Optional[PlacementBank]:
    return load_bank(language)


# --- adaptive staircase (pure) ---------------------------------------------------------

def score(b: PlacementBank, answers: Iterable[dict]) -> List[dict]:
    """[{item_id, choice}] → graded answers in order; unknown ids and repeats are dropped."""
    items, seen, out = b.by_id(), set(), []
    for a in answers:
        item = items.get(a.get("item_id"))
        if item is None or item.id in seen:
            continue
        seen.add(item.id)
        out.append({"item_id": item.id, "level": item.level, "choice": a.get("choice"),
                    "correct": a.get("choice") == item.answer})
    return out


def _decide(results: List[bool], remaining: int) -> Optional[bool]:
    """True = pass, False = fail, None = needs more items at this level."""
    n, k = len(results), sum(results)
    if n >= BLOCK + EXTRA or (n >= BLOCK and remaining == 0):
        return k / n >= 2 / 3
    if n == BLOCK:
        if k >= 3:
            return True
        if k <= 1:
            return False
        return None if remaining else k / n >= 2 / 3
    if remaining == 0 and n:      # bank too small for a full block
        return k / n >= 2 / 3
    return None


def grammar_units(units: Iterable[Unit]) -> Dict[str, str]:
    """grammar point id → unit id."""
    return {gp.id: u.id for u in units for gp in u.grammar}


def _uncovered(remaining: List[Item], asked: List[Item], g2u: Dict[str, str]) -> List[Item]:
    """Remaining items that probe a unit no answered item has probed."""
    probed = {g2u.get(i.grammar) for i in asked if i.grammar}
    return [i for i in remaining if i.grammar and g2u.get(i.grammar) not in probed | {None}]


def _pick(remaining: List[Item], asked: List[Item], g2u: Dict[str, str]) -> Item:
    """Next item at a level, chosen for content coverage (research-methods §3, §10: a short test
    must sample the curriculum, not the first items of the file): prefer an item that probes a
    unit not probed yet, then a grammar point not probed yet, then an error category not asked at
    this level; ties keep YAML order. Depends only on the answered items, so the stateless API
    replays the same path."""
    units = {g2u.get(i.grammar) for i in asked if i.grammar} - {None}
    grammar = {i.grammar for i in asked if i.grammar}
    level = remaining[0].level
    cats = {i.category for i in asked if i.level == level}

    def rank(item: Item) -> tuple:
        unit = g2u.get(item.grammar) if item.grammar else None
        return (not (unit and unit not in units),
                not (item.grammar and item.grammar not in grammar),
                item.category in cats)
    return min(remaining, key=rank)      # min() keeps the first of equal ranks


def step(b: PlacementBank, answers: Iterable[dict], start_level: Optional[str] = None,
         units: Optional[Iterable[Unit]] = None) -> dict:
    """Next item, or the final level when the staircase has settled."""
    graded = score(b, answers)
    g2u = grammar_units(curriculum(b.language) if units is None else units)
    items = b.by_id()
    asked = [items[g["item_id"]] for g in graded]
    level = start_level if start_level in TEST_LEVELS else (
        "B2" if start_level in LEVELS[4:] else "A2")
    decisions: Dict[str, bool] = {}
    # Replay the answers level by level: the order they were given in is the path.
    by_level: Dict[str, List[bool]] = {l: [] for l in TEST_LEVELS}
    for g in graded:
        by_level[g["level"]].append(g["correct"])
    used = {g["item_id"] for g in graded}
    for _ in range(len(TEST_LEVELS) * 2):
        remaining = [i for i in b.items if i.level == level and i.id not in used]
        d = decisions.get(level)
        if d is None:
            d = _decide(by_level[level], len(remaining))
            # A pass after the first block still asks the extra items when units of this
            # level were not probed yet: "you seem to know the A2 units" must rest on
            # items from those units (research-methods §10, content validity).
            if d and COVER_UNITS and len(by_level[level]) < BLOCK + EXTRA and _uncovered(remaining, asked, g2u):
                d = None
        if d is None:
            return {"done": False, "item": _pick(remaining, asked, g2u).public(), "answered": len(graded),
                    "level_now": level}
        decisions[level] = d
        idx = TEST_LEVELS.index(level)
        if d:
            if idx == len(TEST_LEVELS) - 1 or decisions.get(TEST_LEVELS[idx + 1]) is False:
                return _settled(level, decisions, graded)
            level = TEST_LEVELS[idx + 1]
        else:
            if idx == 0:
                return _settled(None, decisions, graded)
            if decisions.get(TEST_LEVELS[idx - 1]) is True:
                return _settled(TEST_LEVELS[idx - 1], decisions, graded)
            level = TEST_LEVELS[idx - 1]
    return _settled(max((l for l, d in decisions.items() if d), key=TEST_LEVELS.index, default=None),
                    decisions, graded)


def _settled(level: Optional[str], decisions: Dict[str, bool], graded: List[dict]) -> dict:
    return {"done": True, "level": level or "A1", "beginner": level is None,
            "decisions": decisions, "answered": len(graded)}


# --- diagnosis -------------------------------------------------------------------------

def diagnose(b: PlacementBank, answers: Iterable[dict], units: List[Unit],
             start_level: Optional[str] = None) -> dict:
    """Final result: level, per-level stats, gaps, suggested-known units, start unit,
    production prompts to show (placed level and the next stage)."""
    graded = score(b, answers)
    settled = step(b, answers, start_level, units)
    if not settled["done"]:
        raise ValueError("placement not finished")
    level = settled["level"]
    items = b.by_id()
    per_level = {l: {"answered": 0, "correct": 0} for l in TEST_LEVELS}
    for g in graded:
        per_level[g["level"]]["answered"] += 1
        per_level[g["level"]]["correct"] += g["correct"]
    cap = LEVELS.index(level) + 1          # gaps worth teaching: up to the next stage
    gaps, wrong_grammar, right_grammar = [], set(), set()
    for g in graded:
        item = items[g["item_id"]]
        if item.grammar:
            (right_grammar if g["correct"] else wrong_grammar).add(item.grammar)
        if not g["correct"] and LEVELS.index(item.level) <= cap:
            gaps.append({"item_id": item.id, "level": item.level, "topic_ru": item.topic_ru,
                         "category": item.category, "grammar": item.grammar,
                         "your_answer": g["choice"], "correct": item.answer})
    categories: Dict[str, int] = {}
    for gap in gaps:
        categories[gap["category"]] = categories.get(gap["category"], 0) + 1
    # Suggested known: below the placed level, or every grammar point tested and right.
    known = [u.id for u in units
             if not ({gp.id for gp in u.grammar} & wrong_grammar)
             and (LEVELS.index(u.level) < LEVELS.index(level) and not settled["beginner"]
                  or {gp.id for gp in u.grammar} <= right_grammar)]
    open_units = next_units(units, known, level=level)
    # Gaps above the placed level are expected, so only gaps at or below it move the start.
    with_gap = [u for u in open_units if {gp.id for gp in u.grammar} & wrong_grammar
                and LEVELS.index(u.level) <= LEVELS.index(level)]
    start = (with_gap or open_units or [None])[0]
    # Per-unit evidence: which units the short test actually probed (C.4 checks the rest
    # in the unit itself instead of assuming either way).
    evidence = {}
    for u in units:
        gp = {g.id for g in u.grammar}
        evidence[u.id] = ("gap" if gp & wrong_grammar else "right" if gp & right_grammar
                          else "untested")
    show = {level, LEVELS[min(cap, len(LEVELS) - 1)]}
    prompts = [p.model_dump() for p in b.production if p.level in show]
    return {"language": b.language, "level": level, "beginner": settled["beginner"],
            "decisions": settled["decisions"], "per_level": per_level, "answered": len(graded),
            "gaps": gaps, "gap_categories": categories, "suggested_known": known,
            "start_unit": start.id if start else None,
            "start_unit_title": start.title_ru if start else None,
            "start_reason": ("gap" if with_gap else "next") if start else None,
            "unit_evidence": evidence,
            # Roman 2026-11-26 (option 3): a unit answered right in the test is open right away
            # (no waiting for its prerequisites), but not counted as known — that still needs
            # every grammar point right (receptive ≠ production, sla §6; C.4 decides mastery).
            "unlocked": [u.id for u in units if evidence[u.id] == "right" and u.id not in known
                         and LEVELS.index(u.level) <= LEVELS.index(level)],
            "production_prompts": prompts, "recheck_after_units": RECHECK_AFTER_UNITS,
            "provisional": b.calibration == "provisional"}


def record(result: dict, answers: Iterable[dict], production: Iterable[dict],
           profile_level: Optional[str]) -> dict:
    """What is stored in the learner's settings under `placement` (additive, no schema change)."""
    prompts = {p["id"] for p in result["production_prompts"]}
    return {**result, "taken_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "profile_level_before": profile_level,
            "answers": [{"item_id": a.get("item_id"), "choice": a.get("choice")} for a in answers],
            "production": [{"prompt_id": p.get("prompt_id"), "text": (p.get("text") or "").strip()[:1000]}
                           for p in production if p.get("prompt_id") in prompts and (p.get("text") or "").strip()]}
