"""Transfer maps (roadmap 1.5): which structures a learner is likely to transfer
from each language they know, with an explicit contrast to show next to a correction.

Grounding: docs/research/morphosyntax.md §7 (keep an L1-specific difficulty map; show the
explicit RU vs ES contrast for transfer errors), sla.md §4 (multilingual learners transfer
from *all* their languages; explain via the closest known language),
multilingual-education.md §1 (plurilingual design: known languages are a resource).

One module per language pair (`ru_es`, `en_es`, `it_es`), each exporting `RULES`.
Another pair plugs in by adding a module and registering it in `_PAIRS`; nothing else changes.

Two kinds of rules:
- "negative": a likely transfer error; shown as "source says X → target says Y".
- "bridge": positive transfer; a known language works like the target here
  ("like Italian *stare*…"), shown as a hint next to the correction.
Pure functions, no I/O.
"""
import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional, Tuple

from . import en_es, it_es, ru_es
from .base import TransferRule


_PAIRS: Dict[Tuple[str, str], Tuple[TransferRule, ...]] = {}
for _module in (ru_es, en_es, it_es):
    for _rule in _module.RULES:
        _PAIRS.setdefault((_rule.source, _rule.target), ())
        _PAIRS[(_rule.source, _rule.target)] += (_rule,)


def fold(text: str) -> str:
    """Lower-case, accents stripped: markers match "línea" and "linea" alike."""
    decomposed = unicodedata.normalize("NFD", (text or "").lower())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def get_map(source: str, target: str) -> Tuple[TransferRule, ...]:
    return _PAIRS.get((source.lower(), target.lower().split("-")[0]), ())


def repertoire(settings: Optional[Dict[str, Any]]) -> List[str]:
    """Learner's known languages, L1 first, without the target."""
    settings = settings or {}
    target = str(settings.get("target_language", "")).lower()
    langs = settings.get("languages") or [{"code": settings.get("native_language") or "ru", "level": "L1"}]
    ordered = sorted(langs, key=lambda l: 0 if l.get("level") == "L1" else 1)
    out: List[str] = []
    for lang in ordered:
        code = str(lang.get("code", "")).lower()
        if code and code != target and code not in out:
            out.append(code)
    return out


def _markers_match(rule: TransferRule, original: str, corrected: str) -> bool:
    if rule.original_markers and not any(re.search(m, original) for m in rule.original_markers):
        return False
    if rule.corrected_markers and not any(re.search(m, corrected) for m in rule.corrected_markers):
        return False
    return True


def _rules_for(sources: Iterable[str], target: str) -> List[TransferRule]:
    return [r for s in sources for r in get_map(s, target)]


def match_rule(correction: Dict[str, Any], settings: Dict[str, Any], kind: str = "negative") -> Optional[TransferRule]:
    """Best rule of `kind` for a normalised correction, or None.

    Specific rules (word markers) win over category-level ones. A category-level
    rule needs the correction's category and comes from the flagged source (or the
    L1 when nothing was flagged): we never contradict the model's flag with a guess.
    Bridges come from any known language."""
    target = str(settings.get("target_language", "")).lower()
    sources = repertoire(settings)
    native = sources[0] if sources else None
    flagged = correction.get("transfer_source")
    if flagged in sources:  # the model's flag first, then L1, then the rest
        sources = [flagged] + [s for s in sources if s != flagged]
    category = correction.get("error_category")
    original, corrected = fold(correction.get("original", "")), fold(correction.get("corrected", ""))
    candidates = [r for r in _rules_for(sources, target) if r.kind == kind]

    for rule in candidates:
        if rule.specific and _markers_match(rule, original, corrected) \
                and (category in (None, rule.category)):
            return rule
    if not category:
        return None
    for rule in candidates:
        if rule.specific or rule.category != category:
            continue
        if kind == "negative":
            # Category-level contrast: the language the model flagged; if none was
            # flagged, only the L1 (a guess from another language would mislead).
            if (flagged or native) != rule.source:
                continue
        return rule
    return None


def _note(rule: TransferRule, native: str) -> str:
    return rule.note.get(native) or rule.note.get("en") or next(iter(rule.note.values()), "")


def _as_dict(rule: TransferRule, native: str) -> Dict[str, Any]:
    return {"rule_id": rule.id, "source": rule.source, "kind": rule.kind, "title": rule.title,
            "source_example": rule.source_example, "target_example": rule.target_example,
            "note": _note(rule, native)}


def transfer_note(correction: Optional[Dict[str, Any]], settings: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Contrast to show under a correction: {"contrast": {...} | None, "bridge": {...} | None},
    or None when no rule applies. Does not change `is_transfer`: that stays the model's call."""
    if not correction or not settings:
        return None
    native = repertoire(settings)[0] if repertoire(settings) else "ru"
    contrast = match_rule(correction, settings, "negative")
    bridge = match_rule(correction, settings, "bridge")
    if bridge and contrast and bridge.source == contrast.source:
        bridge = None
    if not (contrast or bridge):
        return None
    return {"contrast": _as_dict(contrast, native) if contrast else None,
            "bridge": _as_dict(bridge, native) if bridge else None}


def prompt_hints(settings: Optional[Dict[str, Any]], limit: int = 7, per_source: int = 3) -> str:
    """A few short system-prompt lines on likely transfer for this learner's repertoire.
    Only for learners with a completed profile (prompts for legacy users stay unchanged)."""
    if not settings or not settings.get("onboarding_completed"):
        return ""
    target = str(settings.get("target_language", "")).lower()
    lines: List[str] = []
    for source in repertoire(settings):  # a few per language, so L2s are not crowded out
        hints = [r.prompt_hint for r in get_map(source, target) if r.prompt_hint][:per_source]
        lines.extend(f"- [{source}] {h}" for h in hints)
    lines = lines[:limit]
    if not lines:
        return ""
    return ("Likely transfer for this learner (watch for these; set is_transfer/transfer_source "
            "when they occur, and explain by contrast):\n" + "\n".join(lines) + "\n")
