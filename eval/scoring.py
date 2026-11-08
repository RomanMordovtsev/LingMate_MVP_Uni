"""
Scoring for the correction eval harness (roadmap 1.3a). Pure functions, no I/O.

A case is a learner utterance with gold corrections (`acceptable`) and gold
`error_categories`. Cases with `"expect_correction": false` are correct,
natural utterances: any correction there is a false positive (over-correction,
e.g. flagging "porfa" in a bar, docs/feedback/2026-11-05 §5).

The tutor gives at most ONE correction per turn (core/feedback.py), so
category recall is case-level: a case counts as found if the predicted
category is any of the gold ones. (research-methods §2: fixed versioned set,
precision/recall per category.)
"""

import re
import statistics
import unicodedata
from typing import Any, Dict, Iterable, List, Optional

_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)


def norm(text: str) -> str:
    """Lowercase, drop punctuation (incl. ¿ ¡ « »), collapse spaces. Accents are KEPT:
    está vs esta is a real error category (spelling_accent)."""
    text = unicodedata.normalize("NFC", text or "").lower()
    return " ".join(_PUNCT.sub(" ", text).split())


def expects_correction(case: Dict[str, Any]) -> bool:
    return bool(case.get("expect_correction", True))


def _candidates(case: Dict[str, Any], corr: Dict[str, Any]) -> List[str]:
    """Full-sentence readings of the model's correction."""
    out = []
    original, corrected = corr.get("original") or "", corr.get("corrected") or ""
    if corrected:
        out.append(corrected)
        src = case["original"]
        if original and original in src:
            out.append(src.replace(original, corrected, 1))
        elif original and norm(original) in norm(src):
            out.append(norm(src).replace(norm(original), norm(corrected), 1))
    return out


def text_matches(case: Dict[str, Any], corr: Optional[Dict[str, Any]]) -> bool:
    """True if the corrected text equals an acceptable sentence (after norm), either as a
    full sentence or as the fragment substituted into the learner's sentence. A fragment
    that is merely contained in an acceptable sentence (and not in the original) also
    counts, since models often return only the corrected words."""
    if not corr:
        return False
    acceptable = {norm(a) for a in case.get("acceptable", [])}
    cands = [norm(c) for c in _candidates(case, corr)]
    if any(c in acceptable for c in cands if c):
        return True
    frag = norm(corr.get("corrected") or "")
    src = norm(case["original"])
    return bool(frag) and frag not in src and any(
        re.search(rf"(^| ){re.escape(frag)}( |$)", a) for a in acceptable)


def score_case(case: Dict[str, Any], corr: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    gold = list(case.get("error_categories") or [])
    expected = expects_correction(case)
    predicted = (corr or {}).get("error_category")
    result = {
        "id": case["id"],
        "expected_correction": expected,
        "detected": corr is not None,
        "gold_categories": gold,
        "predicted_category": predicted,
        "category_hit": bool(expected and predicted and predicted in gold),
        "text_match": bool(expected and text_matches(case, corr)),
        "false_positive": bool(not expected and corr is not None),
        "predicted_is_transfer": bool(corr and corr.get("is_transfer")),
        "predicted_transfer_source": (corr or {}).get("transfer_source"),
    }
    if expected and case.get("is_transfer"):
        result["transfer_hit"] = bool(corr and corr.get("is_transfer")
                                      and (corr.get("transfer_source") or "") ==
                                      (case.get("transfer_source") or ""))
    return result


def _ratio(num: int, den: int) -> Optional[float]:
    return round(num / den, 3) if den else None


def aggregate(scored: Iterable[Dict[str, Any]], latencies: Iterable[float] = ()) -> Dict[str, Any]:
    # Provider failures (429/503, timeouts) are not the model's misses: score only
    # answered cases and report failures separately (docs/feedback/2026-11-08 §2).
    every = list(scored)
    scored = [s for s in every if not s.get("provider_failed")]
    lat = [x for x in latencies if x is not None]
    err = [s for s in scored if s["expected_correction"]]
    clean = [s for s in scored if not s["expected_correction"]]
    transfer = [s for s in err if "transfer_hit" in s]

    tp: Dict[str, int] = {}
    fp: Dict[str, int] = {}
    fn: Dict[str, int] = {}
    for s in scored:
        p = s["predicted_category"] if s["detected"] else None
        if s["category_hit"]:
            tp[p] = tp.get(p, 0) + 1
            continue
        if p:
            fp[p] = fp.get(p, 0) + 1
        for g in s["gold_categories"]:
            fn[g] = fn.get(g, 0) + 1
    cats = sorted(set(tp) | set(fp) | set(fn))
    per_category = {c: {"tp": tp.get(c, 0), "fp": fp.get(c, 0), "fn": fn.get(c, 0),
                        "precision": _ratio(tp.get(c, 0), tp.get(c, 0) + fp.get(c, 0)),
                        "recall": _ratio(tp.get(c, 0), tp.get(c, 0) + fn.get(c, 0))}
                    for c in cats}
    total_tp, total_fp = sum(tp.values()), sum(fp.values())

    flagged = [s for s in scored if s["detected"] and s.get("predicted_is_transfer")]
    gold_transfer_detected = [s for s in transfer if s["detected"]]
    return {
        "cases": len(every),
        "answered": len(scored),
        "provider_failures": len(every) - len(scored),
        "error_cases": len(err),
        "clean_cases": len(clean),
        "detection_rate": _ratio(sum(s["detected"] for s in err), len(err)),
        "category_recall": _ratio(sum(s["category_hit"] for s in err), len(err)),
        "category_precision": _ratio(total_tp, total_tp + total_fp),
        "text_match_rate": _ratio(sum(s["text_match"] for s in err), len(err)),
        "false_positive_rate": _ratio(sum(s["false_positive"] for s in clean), len(clean)),
        "transfer_accuracy": _ratio(sum(s["transfer_hit"] for s in transfer), len(transfer)),
        # Diagnostics for §5: does the model flag transfer at all, and name the source?
        "transfer_flagged_rate": _ratio(sum(s.get("predicted_is_transfer", False) for s in gold_transfer_detected),
                                        len(gold_transfer_detected)),
        "transfer_source_filled": _ratio(sum(bool(s.get("predicted_transfer_source")) for s in flagged),
                                         len(flagged)),
        "per_category": per_category,
        "latency_s": {
            "mean": round(statistics.mean(lat), 3) if lat else None,
            "median": round(statistics.median(lat), 3) if lat else None,
            "max": round(max(lat), 3) if lat else None,
        },
    }
