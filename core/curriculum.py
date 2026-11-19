"""Curriculum map (roadmap C.1): units loaded from `curriculum/<lang>/units/*.yaml`.

One unit = can-do goals (CEFR CV 2020 scales) + linguistic layer referenced to the
Plan Curricular del Instituto Cervantes (PCIC) + key chunks + vocabulary + linked
situations (existing scenarios, Roman's real situations in `docs/learner/`) + culture note
+ prerequisites. The unit of the course is a task; grammar is a secondary map used to pick
focus-on-form targets (syllabus-design §2), chunks are taught whole (§2), progress is shown
as can-do descriptors (§8), and units come from the learner's real needs (§1).

Template-based: another language = another folder with the same YAML shape; no code change.
Content is authored once and stored (quota strategy in ROADMAP), never generated per learner.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List, Literal, Optional

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from core.feedback import ERROR_CATEGORIES

CURRICULUM_DIR = Path(__file__).resolve().parent.parent / "curriculum"
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
Level = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
# PCIC inventories (chapter names as on cvc.cervantes.es); section numbers are given only
# where they were checked against the PCIC page (`verified: true`), see curriculum/es/SOURCES.md.
PcicInventory = Literal[
    "gramatica", "pronunciacion", "ortografia", "funciones", "tacticas_pragmaticas",
    "generos_discursivos", "nociones_generales", "nociones_especificas", "referentes_culturales",
    "saberes_socioculturales", "habilidades_interculturales", "procedimientos_aprendizaje",
]
_ID = re.compile(r"^[a-z]{2}-[a-c][12]-[a-z0-9-]+$")


class CanDo(BaseModel):
    ru: str = Field(min_length=10)          # learner-facing, "Могу …" (UI labels in Russian)
    cefr_scale: str = Field(min_length=3)   # CEFR CV 2020 scale name (descriptor paraphrased)
    cefr_level: Level


class PcicRef(BaseModel):
    inventory: PcicInventory
    band: Literal["A1-A2", "B1-B2", "C1-C2"]
    title: str = Field(min_length=3)        # item as named in PCIC (Spanish)
    section: Optional[str] = None           # e.g. "4.3" — only when verified
    verified: bool = False

    @model_validator(mode="after")
    def _section_needs_check(self):
        if self.section and not self.verified:
            raise ValueError(f"PCIC section {self.section} given without verified: true")
        return self


class Example(BaseModel):
    es: str = Field(min_length=2)           # target-language text (learning content)
    ru: str = Field(min_length=2)


class GrammarPoint(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9_]+$")
    label_ru: str = Field(min_length=3)
    tip_ru: str = Field(min_length=10)      # one short focus-on-form tip (pre-task, syllabus-design §3)
    examples: List[str] = Field(min_length=1)
    error_categories: List[str] = Field(min_length=1)

    @field_validator("error_categories")
    @classmethod
    def _known(cls, v):
        bad = [c for c in v if c not in ERROR_CATEGORIES]
        if bad:
            raise ValueError(f"unknown error categories {bad}")
        return v


class Situations(BaseModel):
    scenarios: List[str] = []               # ids in core.scenarios.SCENARIOS
    learner: List[str] = []                 # heading prefixes in docs/learner/*.md ("31.10.2026 — Ordering")
    seeds: List[str] = []                   # scenario seeds not built yet (relocation pack 4.3)


class Unit(BaseModel):
    id: str
    language: str = Field(pattern=r"^[a-z]{2}$")
    variant: str
    level: Level
    order: int = Field(ge=1)
    title_ru: str = Field(min_length=3)
    title_target: str = Field(min_length=3)
    can_do: List[CanDo] = Field(min_length=1, max_length=3)   # 1–3 descriptors per task (§8)
    pcic: List[PcicRef] = Field(min_length=1)
    grammar: List[GrammarPoint] = Field(min_length=1)
    chunks: List[Example] = Field(min_length=3, max_length=8)  # 3–6 key chunks per task (§3), some slack
    vocabulary: List[Example] = []
    situations: Situations
    culture_ru: str = ""
    prerequisites: List[str] = []

    @field_validator("id")
    @classmethod
    def _id(cls, v):
        if not _ID.match(v):
            raise ValueError(f"unit id {v!r} must look like 'es-a2-topic'")
        return v

    @model_validator(mode="after")
    def _id_matches(self):
        if not self.id.startswith(f"{self.language}-{self.level.lower()}-"):
            raise ValueError(f"unit id {self.id} does not match language/level {self.language}/{self.level}")
        return self

    @property
    def error_categories(self) -> List[str]:
        seen: List[str] = []
        for g in self.grammar:
            seen += [c for c in g.error_categories if c not in seen]
        return seen

    def summary(self) -> dict:
        return {"id": self.id, "level": self.level, "order": self.order, "title_ru": self.title_ru,
                "title_target": self.title_target, "can_do": [c.ru for c in self.can_do],
                "grammar": [g.label_ru for g in self.grammar], "error_categories": self.error_categories,
                "prerequisites": self.prerequisites}


class CurriculumError(ValueError):
    pass


def validate_units(units: List[Unit]) -> List[Unit]:
    """Cross-unit checks: unique ids/orders, known prerequisites, no cycles, prerequisites come
    earlier (lower order, level not higher). Returns units sorted by `order`."""
    ids = [u.id for u in units]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise CurriculumError(f"duplicate unit ids: {sorted(dup)}")
    orders = [u.order for u in units]
    if len(set(orders)) != len(orders):
        raise CurriculumError("duplicate unit order")
    by_id = {u.id: u for u in units}
    for u in units:
        for p in u.prerequisites:
            if p not in by_id:
                raise CurriculumError(f"{u.id}: unknown prerequisite {p}")
            pre = by_id[p]
            if pre.order >= u.order or LEVELS.index(pre.level) > LEVELS.index(u.level):
                raise CurriculumError(f"{u.id}: prerequisite {p} must come earlier")
    return sorted(units, key=lambda u: u.order)


def load_units(language: str, root: Path = CURRICULUM_DIR) -> List[Unit]:
    folder = root / language / "units"
    if not folder.is_dir():
        return []
    units = []
    for path in sorted(folder.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        try:
            unit = Unit.model_validate(data)
        except ValueError as e:
            raise CurriculumError(f"{path.name}: {e}") from e
        if unit.language != language:
            raise CurriculumError(f"{path.name}: language {unit.language} in folder {language}")
        units.append(unit)
    return validate_units(units)


@lru_cache(maxsize=8)
def curriculum(language: str) -> tuple:
    return tuple(load_units(language))


def next_units(units: Iterable[Unit], done: Iterable[str], level: Optional[str] = None) -> List[Unit]:
    """Units not done whose prerequisites are all done, in course order. With `level`, units
    above the learner's next stage are left for later (morphosyntax §10: teach up to the next stage)."""
    done = set(done)
    cap = LEVELS.index(level) + 1 if level in LEVELS else len(LEVELS) - 1
    return [u for u in units
            if u.id not in done and all(p in done for p in u.prerequisites) and LEVELS.index(u.level) <= cap]


def get_unit(language: str, unit_id: str) -> Optional[Unit]:
    return next((u for u in curriculum(language) if u.id == unit_id), None)


def units_for_category(units: Iterable[Unit], category: str) -> List[Unit]:
    """Units that practise an error category (link to the error log, 1.6 → C.4)."""
    return [u for u in units if category in u.error_categories]
