"""
Error log as a learner corpus (roadmap 1.6). Pure functions, no I/O.

Every structured correction (1.3) becomes one entry; `summarize` turns the
entries into per-category counts, a week-over-week trend, *persistent* errors
(fossilization risk) and *possibly avoided* structures.

Grounding:
- morphosyntax §10 (Myles 2008): the error log is a mini learner corpus; track
  per-form accuracy over time, not a flat list of mistakes.
- sla §5 (Han 2004): errors that persist over weeks → escalate (more explicit
  feedback, targeted practice). "Persistent" here = seen on several days
  spread over ≥ 1 week and still present recently.
- sla §4 (Ortega 2009): avoidance — a structure the learner never produces is
  a signal, not an absence of errors. Detected with surface markers only, so
  it is reported as "possibly avoided" and only with enough messages.
"""

import re
import unicodedata
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional

from core.feedback import ERROR_CATEGORIES

# Thresholds (kept here so tests and the weekly report use the same numbers).
PERSISTENT_MIN_DAYS = 3        # distinct days with this error
PERSISTENT_MIN_SPAN_DAYS = 7   # first → last occurrence
PERSISTENT_RECENT_DAYS = 14    # still seen within this window
AVOIDANCE_MIN_MESSAGES = 30    # learner messages needed before claiming avoidance

_LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFD", (text or "").lower())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def _parse_ts(value: Any) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(str(value))
    except (TypeError, ValueError):
        return None


def make_entry(correction: Any, *, mode: str, message: str = "",
               scenario_id: Optional[str] = None,
               target_language: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """One log entry from a normalised correction; None for legacy strings / no category."""
    if not isinstance(correction, dict):
        return None
    category = correction.get("error_category")
    if category not in ERROR_CATEGORIES:
        return None
    return {
        "error_category": category,
        "original": correction.get("original") or "",
        "corrected": correction.get("corrected") or "",
        "cf_type": correction.get("cf_type"),
        "is_transfer": bool(correction.get("is_transfer")),
        "transfer_source": correction.get("transfer_source"),
        "explanation": correction.get("explanation") or "",
        "message": message,
        "mode": mode,
        "scenario_id": scenario_id,
        "target_language": target_language,
    }


_LEGACY_LINE = re.compile(r"^(?P<original>.+?) → (?P<corrected>.+?)(?: — (?P<explanation>.*))? \[(?P<cat>[a-z_]+)\]$")


def entry_from_mistake_line(line: Any) -> Optional[Dict[str, Any]]:
    """Back-fill: parse a progress-log line written by `correction_to_text` since 1.3."""
    if not isinstance(line, str):
        return None
    m = _LEGACY_LINE.match(line.strip())
    if not m or m.group("cat") not in ERROR_CATEGORIES:
        return None
    entry = make_entry({"error_category": m.group("cat"), "original": m.group("original"),
                        "corrected": m.group("corrected"), "explanation": m.group("explanation") or ""},
                       mode="unknown")
    entry["backfilled"] = True
    return entry


# --- avoidance markers -------------------------------------------------------
# Surface markers on accent-folded learner text. A false positive only hides an
# "avoided" flag (safe direction); a missed form can raise a false flag, hence
# the message minimum and the "possibly" wording in the UI.
AVOIDANCE_TARGETS: Dict[str, List[Dict[str, Any]]] = {
    "es": [
        {"id": "preterito_perfecto", "label": "pretérito perfecto (he hecho)", "level": "A2",
         "pattern": r"\b(he|has|ha|hemos|habeis|han) \w+(ado|ido|to|cho|sto)\b"},
        {"id": "preterito_indefinido", "label": "pretérito indefinido (hice, fui)", "level": "A2",
         "pattern": r"\b(fui|fue|fuimos|hice|hizo|tuve|tuvo|estuve|pude|dije|vine|\w+(aste|aron|ieron|io))\b|\b\w{3,}(e|o) (ayer|anoche)\b|\b(ayer|anoche) \w{3,}(e|o)\b"},
        {"id": "imperfecto", "label": "pretérito imperfecto (estaba, tenía)", "level": "A2",
         "pattern": r"\b(era|eras|eramos|eran|iba|ibas|ibamos|iban|\w+(aba|abas|abamos|aban)|"
                    r"(ten|hac|pod|quer|sab|viv|com|hab|dec|sal|ven|pon|cre|le|conoc|entend|beb|escrib|ve|"
                    r"aprend|deb|parec|sent|segu|ped|dorm|abr|sol|cog|perd|vend)(ia|ias|iamos|iais|ian))\b"},
        # -ía forms only for listed verb stems: nouns like familia, farmacia, Vitoria, gracias are not imperfecto.
        {"id": "clitics", "label": "местоимения-клитики (lo, la, se lo)", "level": "A2",
         "pattern": r"\b(me|te|nos|se|le|les) \w{2,}|\b(lo|la|los|las) \w+(o|amos|emos|imos)\b|"
                    r"\b\w+(ar|er|ir|ando|iendo)(lo|la|los|las|le|les|me|te|se|nos)\b"},
        # lo/la/los/las only before 1st-person verb endings, so "la cola" (article + noun) is not a clitic.
        {"id": "futuro_ir_a", "label": "будущее (voy a + inf., haré)", "level": "A2",
         "pattern": r"\b(voy|vas|va|vamos|vais|van) a \w+(ar|er|ir)\b|\b\w+(are|aras|ara|aremos|aran|ere|eras|era|eremos|eran|ire|iras|ira|iremos|iran)\b"},
        {"id": "subjuntivo", "label": "subjuntivo (quiero que vengas, ojalá)", "level": "B1",
         "pattern": r"\b(ojala|que aproveche|que te vaya|que te mejores|para que|antes de que|espero que|quiero que|quieres que|es importante que|no creo que|no pienso que|cuando (sea|tenga|vaya|pueda|llegue|termine|vuelva|venga))\b"},
        {"id": "condicional", "label": "condicional (me gustaría, podría)", "level": "B1",
         "pattern": r"\b\w+(aria|arias|ariamos|arian|eria|erias|eriamos|erian|iria|irias|iriamos|irian)\b|\b(podria|tendria|haria|diria|querria|sabria|pondria|saldria|vendria)\w*\b"},
    ],
}


def avoided_structures(learner_messages: Iterable[str], target_language: str = "es",
                       level: Optional[str] = None) -> Dict[str, Any]:
    """Structures expected at the learner's level (and the next one) never seen in their messages."""
    messages = [m for m in learner_messages if m and m.strip()]
    targets = AVOIDANCE_TARGETS.get((target_language or "").split("-")[0], [])
    result: Dict[str, Any] = {"messages_checked": len(messages), "min_messages": AVOIDANCE_MIN_MESSAGES,
                              "enough_data": len(messages) >= AVOIDANCE_MIN_MESSAGES, "items": []}
    if not targets or not result["enough_data"]:
        return result
    max_idx = _LEVELS.index(level) + 1 if level in _LEVELS else len(_LEVELS)
    folded = [_fold(m) for m in messages]
    for t in targets:
        if _LEVELS.index(t["level"]) > max_idx:
            continue  # beyond the learner's next stage (morphosyntax §10)
        if not any(re.search(t["pattern"], m) for m in folded):
            result["items"].append({"id": t["id"], "label": t["label"], "level": t["level"]})
    return result


# --- summary -----------------------------------------------------------------
def summarize(entries: List[Dict[str, Any]], *, now: Optional[datetime] = None,
              window_days: int = 7, learner_messages: Optional[Iterable[str]] = None,
              target_language: str = "es", level: Optional[str] = None) -> Dict[str, Any]:
    """Counts per category, trend (last window vs the one before), persistent errors, avoidance."""
    now = now or datetime.now()
    cur_start = now - timedelta(days=window_days)
    prev_start = cur_start - timedelta(days=window_days)
    recent_start = now - timedelta(days=PERSISTENT_RECENT_DAYS)

    by_cat: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        cat = e.get("error_category")
        ts = _parse_ts(e.get("created_at"))
        if cat not in ERROR_CATEGORIES or ts is None:
            continue
        c = by_cat.setdefault(cat, {"category": cat, "count": 0, "current": 0, "previous": 0,
                                    "days": set(), "first": ts, "last": ts, "recent": False,
                                    "transfer_sources": {}, "examples": [], "forms": {}})
        c["count"] += 1
        c["days"].add(ts.date())
        c["first"], c["last"] = min(c["first"], ts), max(c["last"], ts)
        if ts >= cur_start:
            c["current"] += 1
        elif ts >= prev_start:
            c["previous"] += 1
        if ts >= recent_start:
            c["recent"] = True
        if e.get("is_transfer") and e.get("transfer_source"):
            src = e["transfer_source"]
            c["transfer_sources"][src] = c["transfer_sources"].get(src, 0) + 1
        pair = (_fold(e.get("original", "")).strip(), _fold(e.get("corrected", "")).strip())
        if all(pair):
            c["forms"].setdefault(pair, {"original": e.get("original"), "corrected": e.get("corrected"),
                                         "days": set()})["days"].add(ts.date())
        c["examples"].append({"original": e.get("original"), "corrected": e.get("corrected"),
                              "created_at": e.get("created_at")})

    categories, persistent = [], []
    for c in by_cat.values():
        if c["previous"] == 0 and c["current"] > 0 and c["first"] >= cur_start:
            trend = "new"
        elif c["current"] > c["previous"]:
            trend = "up"
        elif c["current"] < c["previous"]:
            trend = "down"
        else:
            trend = "flat"
        span = (c["last"].date() - c["first"].date()).days
        recurrent_forms = [{"original": f["original"], "corrected": f["corrected"], "days": len(f["days"])}
                           for f in c["forms"].values() if len(f["days"]) >= 2]
        is_persistent = (len(c["days"]) >= PERSISTENT_MIN_DAYS and span >= PERSISTENT_MIN_SPAN_DAYS
                         and c["recent"])
        item = {"category": c["category"], "count": c["count"], "current_window": c["current"],
                "previous_window": c["previous"], "trend": trend, "days_seen": len(c["days"]),
                "first_seen": c["first"].isoformat(timespec="seconds"),
                "last_seen": c["last"].isoformat(timespec="seconds"),
                "transfer_sources": c["transfer_sources"], "recurrent_forms": recurrent_forms,
                "examples": c["examples"][-3:], "persistent": is_persistent}
        categories.append(item)
        if is_persistent or (recurrent_forms and c["recent"]):
            persistent.append({"category": c["category"], "days_seen": len(c["days"]),
                               "span_days": span, "recurrent_forms": recurrent_forms,
                               "reason": "category" if is_persistent else "same_form"})

    categories.sort(key=lambda x: (-x["count"], x["category"]))
    persistent.sort(key=lambda x: (-x["days_seen"], x["category"]))
    return {
        "total": sum(c["count"] for c in categories),
        "window_days": window_days,
        "categories": categories,
        "persistent": persistent,
        "avoided": avoided_structures(learner_messages or [], target_language, level),
    }
