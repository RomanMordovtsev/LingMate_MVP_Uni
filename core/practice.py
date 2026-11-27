"""Controlled practice for a curriculum unit (roadmap C.3, slice 1). Pure, no LLM, no I/O
except loading `curriculum/<lang>/practice/<unit-id>.yaml`.

Exercise kinds: `gap` (fill one gap), `choose` (pick an option), `order` (put words in
order), `transform` (rewrite a sentence). Each exercise practises one grammar point of its
unit and is checked on the server; the answer key is never sent before it is revealed.

Grounding:
- syllabus-design §6 (scaffolding, ZPD): graded hints — a nudge, then a partial cue, then the
  full answer with a short explanation.
- morphosyntax §2, §6: the revealed answer comes with a diff (noticing) and a short
  metalinguistic note; an answer that is right except for an accent / tilde is accepted but
  the accent is shown (Spanish accents are meaningful: está / esta).
- sla §6 (Lightbown 2003, Macaro & Masterman 2006): drills alone do not build accuracy in free
  production → practice results are stored as *practised*, never as "unit done" (C.4 needs
  free-production evidence), and the summary sends the learner on to the role-play.
"""
from __future__ import annotations

import hashlib
import random
import re
import unicodedata
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from core.curriculum import CURRICULUM_DIR, Unit
from core.feedback import correction_diff

MAX_ATTEMPTS = {"gap": 3, "transform": 3, "order": 3, "choose": 2}  # choose: few options → reveal sooner
SHUFFLE_SALT = "lingmate-practice-v1"
GAP = "___"


def _strip_marks(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    return unicodedata.normalize("NFC", "".join(ch for ch in text if unicodedata.category(ch) != "Mn"))


def normalize(text: str) -> str:
    """Case, outer/inner punctuation and spaces do not matter; accents do (handled separately)."""
    text = unicodedata.normalize("NFC", (text or "").lower())
    text = re.sub(r"[¿¡?!.,;:«»\"“”…()]", " ", text)
    return " ".join(text.split())


class Exercise(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9-]+$")
    kind: Literal["gap", "choose", "order", "transform"]
    grammar: str                               # grammar point id of the unit
    instruction_ru: str = Field(min_length=5)
    prompt: str = Field(min_length=2)          # gap/choose: sentence with ___; transform: source; order: RU meaning
    answers: List[str] = Field(min_length=1)   # acceptable answers; the first one is shown on reveal
    options: List[str] = []                    # choose only
    hint_ru: str = Field(min_length=5)         # first nudge (no answer in it)
    explain_ru: str = Field(min_length=5)      # shown with the answer: why

    @model_validator(mode="after")
    def _shape(self):
        if self.kind in ("gap", "choose") and self.prompt.count(GAP) != 1:
            raise ValueError(f"{self.id}: {self.kind} prompt needs exactly one {GAP}")
        if self.kind == "choose":
            if len(self.options) < 2 or any(a not in self.options for a in self.answers):
                raise ValueError(f"{self.id}: choose needs ≥ 2 options containing every answer")
        elif self.options:
            raise ValueError(f"{self.id}: options are only for choose")
        if self.kind == "order" and len(self.answers[0].split()) < 3:
            raise ValueError(f"{self.id}: order needs ≥ 3 words")
        if any(normalize(a) in normalize(self.hint_ru) for a in self.answers if len(a) > 3):
            raise ValueError(f"{self.id}: the hint gives the answer away")
        return self

    def _rng(self) -> random.Random:
        return random.Random(int(hashlib.sha256(f"{SHUFFLE_SALT}:{self.id}".encode()).hexdigest(), 16))

    def tokens(self) -> List[str]:
        """Words of the first answer in a stable shuffled order that is never the answer itself.
        Punctuation and the capital of the first word are dropped: they would give the order away."""
        words = [re.sub(r"[¿¡?!.,;:«»\"“”…()]", "", w) for w in self.answers[0].split()]
        words = [w for w in words if w]
        words[0] = words[0][:1].lower() + words[0][1:]
        rng, shown = self._rng(), list(words)
        for _ in range(20):
            rng.shuffle(shown)
            if shown != words:
                break
        if shown == words:
            shown = words[1:] + words[:1]
        return shown

    def shown_options(self) -> List[str]:
        opts = list(self.options)
        self._rng().shuffle(opts)
        return opts

    def public(self) -> dict:
        out = {"id": self.id, "kind": self.kind, "grammar": self.grammar,
               "instruction_ru": self.instruction_ru, "prompt": self.prompt,
               "max_attempts": MAX_ATTEMPTS[self.kind]}
        if self.kind == "choose":
            out["options"] = self.shown_options()
        if self.kind == "order":
            out["tokens"] = self.tokens()
        return out

    def full(self, response: str) -> str:
        """The learner's whole sentence (for the diff): gaps are filled into the prompt."""
        return self.prompt.replace(GAP, response) if self.kind in ("gap", "choose") else response


class PracticeSet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    unit: str
    exercises: List[Exercise] = Field(min_length=3)

    def by_id(self) -> Dict[str, Exercise]:
        return {e.id: e for e in self.exercises}


class PracticeError(ValueError):
    pass


def validate_set(ps: PracticeSet, unit: Unit) -> PracticeSet:
    ids = [e.id for e in ps.exercises]
    if len(set(ids)) != len(ids):
        raise PracticeError(f"{ps.unit}: duplicate exercise ids")
    grammar = {g.id for g in unit.grammar}
    bad = [e.id for e in ps.exercises if e.grammar not in grammar]
    if bad:
        raise PracticeError(f"{ps.unit}: unknown grammar point in {bad}")
    missing = grammar - {e.grammar for e in ps.exercises}
    if missing:
        raise PracticeError(f"{ps.unit}: no exercise for grammar points {sorted(missing)}")
    return ps


def load_set(language: str, unit: Unit, root: Path = CURRICULUM_DIR) -> Optional[PracticeSet]:
    path = root / language / "practice" / f"{unit.id}.yaml"
    if not path.is_file():
        return None
    try:
        ps = PracticeSet.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    except ValueError as e:
        raise PracticeError(f"{path.name}: {e}") from e
    if ps.unit != unit.id:
        raise PracticeError(f"{path.name}: unit {ps.unit} != {unit.id}")
    return validate_set(ps, unit)


@lru_cache(maxsize=32)
def practice_for(language: str, unit_id: str) -> Optional[PracticeSet]:
    from core.curriculum import get_unit
    unit = get_unit(language, unit_id)
    return load_set(language, unit) if unit else None


def cue(answer: str) -> str:
    """Partial cue: first letter of every word, the rest masked (se me ha olvidado → s_ m_ h_ o_______)."""
    return " ".join(w[0] + "_" * (len(w) - 1) if len(w) > 1 else w for w in answer.split())


def check(ex: Exercise, response: Union[str, List[str], None], attempt: int) -> dict:
    """Check one attempt (1-based). Returns result correct | accent | wrong | revealed, `done`, and
    the scaffolding step for this attempt: hint → cue → answer + explanation + diff."""
    if isinstance(response, list):
        response = " ".join(response)
    response = (response or "").strip()
    limit = MAX_ATTEMPTS[ex.kind]
    attempt = max(1, min(int(attempt), limit))
    got = normalize(response)
    out: dict = {"exercise_id": ex.id, "attempt": attempt, "max_attempts": limit}
    for ans in ex.answers:
        if got and got == normalize(ans):
            return {**out, "result": "correct", "done": True, "answer": ans, "full_answer": ex.full(ans),
                    "explain_ru": ex.explain_ru}
    for ans in ex.answers:
        if got and _strip_marks(got) == _strip_marks(normalize(ans)):
            return {**out, "result": "accent", "done": True, "answer": ans, "full_answer": ex.full(ans),
                    "explain_ru": ex.explain_ru,
                    "note_ru": "Почти! Проверь ударение или тильду — в испанском они меняют слово.",
                    "diff": correction_diff(ex.full(response), ex.full(ans))}
    if attempt >= limit:
        ans = ex.answers[0]
        return {**out, "result": "revealed", "done": True, "answer": ans, "full_answer": ex.full(ans),
                "explain_ru": ex.explain_ru,
                "diff": correction_diff(ex.full(response), ex.full(ans)) if response else []}
    step = {"result": "wrong", "done": False, "hint_ru": ex.hint_ru}
    if attempt >= 2 and ex.kind != "choose":
        first = ex.answers[0]
        step["cue"] = " ".join(first.split()[:2]) + " …" if ex.kind == "order" else cue(first)
    return {**out, **step}


def summarize(ps: PracticeSet, results: Iterable[dict], unit: Unit) -> dict:
    """Per-unit summary from the client's per-exercise outcomes ({exercise_id, result, attempts}).
    Unknown ids are ignored. `weak` = grammar points with an exercise that was not right at once."""
    by_id = ps.by_id()
    seen: Dict[str, dict] = {}
    for r in results:
        ex = by_id.get(r.get("exercise_id"))
        if ex and r.get("result") in ("correct", "accent", "revealed"):
            seen[ex.id] = {"result": r["result"], "attempts": max(1, int(r.get("attempts") or 1))}
    first_try = [i for i, r in seen.items() if r["result"] in ("correct", "accent") and r["attempts"] == 1]
    with_help = [i for i, r in seen.items() if r["result"] in ("correct", "accent") and r["attempts"] > 1]
    revealed = [i for i, r in seen.items() if r["result"] == "revealed"]
    weak_ids = {by_id[i].grammar for i in with_help + revealed}
    labels = {g.id: g.label_ru for g in unit.grammar}
    return {"unit": ps.unit, "total": len(ps.exercises), "answered": len(seen),
            "first_try": len(first_try), "with_help": len(with_help), "revealed": len(revealed),
            "weak": [{"grammar": g, "label_ru": labels[g]} for g in labels if g in weak_ids],
            "status": "practised",   # never "done": that needs free production (sla §6, C.4)
            "next_ru": "Теперь попробуй это в живом разговоре с Юдзи — там и проверим, как получается без подсказок."}


def record(summary: dict, now: Optional[datetime] = None) -> dict:
    return {**{k: summary[k] for k in ("total", "answered", "first_try", "with_help", "revealed", "status")},
            "weak": [w["grammar"] for w in summary["weak"]],
            "at": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")}
