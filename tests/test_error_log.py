"""Error log as learner corpus (roadmap 1.6). Pure analytics + storage parity + API. No network."""
import importlib
import json
from datetime import datetime, timedelta

import pytest

from core import storage
from core.error_log import (AVOIDANCE_MIN_MESSAGES, avoided_structures, entry_from_mistake_line,
                            make_entry, summarize)
from core.feedback import correction_to_text
from core.storage import JsonStore, SqliteStore

NOW = datetime(2026, 11, 13, 20, 0)


def _e(cat, days_ago, original="la línea", corrected="la cola", **kw):
    entry = make_entry({"error_category": cat, "original": original, "corrected": corrected, **kw},
                       mode="free_talk", message=original)
    entry["created_at"] = (NOW - timedelta(days=days_ago)).isoformat(timespec="seconds")
    return entry


# --- make_entry ----------------------------------------------------------
def test_make_entry_keeps_structure_and_skips_legacy():
    c = {"original": "la línea", "corrected": "la cola", "error_category": "lexical", "cf_type": "recast",
         "is_transfer": True, "transfer_source": "en", "explanation": "калька", "diff": [{"op": "equal"}]}
    e = make_entry(c, mode="lesson", message="Estoy en la línea", scenario_id="coffee_shop", target_language="es")
    assert e["error_category"] == "lexical" and e["transfer_source"] == "en" and e["scenario_id"] == "coffee_shop"
    assert "diff" not in e
    assert make_entry("Mejor: está bien", mode="free_talk") is None
    assert make_entry({"original": "x", "corrected": "y", "error_category": "nonsense"}, mode="x") is None
    assert make_entry(None, mode="x") is None


def test_backfill_parses_lines_written_by_correction_to_text():
    line = correction_to_text({"original": "possible", "corrected": "posible",
                               "explanation": "одна s", "error_category": "spelling_accent"})
    e = entry_from_mistake_line(line)
    assert e["original"] == "possible" and e["corrected"] == "posible" and e["error_category"] == "spelling_accent"
    assert e["backfilled"] is True
    assert entry_from_mistake_line("línea → cola") is None  # pre-1.3 free text
    assert entry_from_mistake_line({"not": "a line"}) is None


# --- summarize -----------------------------------------------------------
def test_counts_and_trend():
    entries = [_e("lexical", 1), _e("lexical", 2), _e("lexical", 9),
               _e("gender", 10), _e("gender", 11),
               _e("article", 3)]
    s = summarize(entries, now=NOW)
    cats = {c["category"]: c for c in s["categories"]}
    assert s["total"] == 6
    assert [c["category"] for c in s["categories"]][0] == "lexical"
    assert cats["lexical"]["trend"] == "up" and cats["lexical"]["current_window"] == 2
    assert cats["gender"]["trend"] == "down"
    assert cats["article"]["trend"] == "new"


def test_persistent_needs_several_days_over_a_week_and_recent():
    persistent = [_e("ser_estar", d, "soy cansado", "estoy cansado") for d in (1, 5, 12)]
    one_burst = [_e("article", 0, "en tren", "en el tren")] * 5           # many, but one day
    old = [_e("gender", d, "el postal", "la postal") for d in (30, 35, 40)]  # not recent any more
    s = summarize(persistent + one_burst + old, now=NOW)
    cats = {c["category"]: c for c in s["categories"]}
    assert cats["ser_estar"]["persistent"] is True
    assert cats["article"]["persistent"] is False
    assert cats["gender"]["persistent"] is False
    assert [p["category"] for p in s["persistent"]] == ["ser_estar"]
    assert s["persistent"][0]["recurrent_forms"][0]["corrected"] == "estoy cansado"


def test_same_form_on_two_days_is_flagged_even_if_category_is_not_persistent_yet():
    s = summarize([_e("lexical", 1), _e("lexical", 3, "La Línea", "la cola")], now=NOW)
    assert s["persistent"] == [{"category": "lexical", "days_seen": 2, "span_days": 2, "reason": "same_form",
                                "recurrent_forms": [{"original": "la línea", "corrected": "la cola", "days": 2}]}]


def test_transfer_sources_and_bad_rows_ignored():
    entries = [_e("lexical", 1, is_transfer=True, transfer_source="en"),
               _e("lexical", 2, is_transfer=True, transfer_source="en"),
               {"error_category": "lexical", "created_at": "not a date"},
               {"error_category": "??", "created_at": NOW.isoformat()}]
    s = summarize(entries, now=NOW)
    assert s["total"] == 2 and s["categories"][0]["transfer_sources"] == {"en": 2}


def test_empty_log():
    s = summarize([], now=NOW)
    assert s["total"] == 0 and s["categories"] == [] and s["persistent"] == []
    assert s["avoided"]["enough_data"] is False


# --- avoidance -----------------------------------------------------------
PRESENT_ONLY = ["Hola, me llamo Roman.", "Quiero un café con leche, porfa.", "Vivo en Vitoria.",
                "Estoy en la cola.", "Me gusta la música."]


def test_avoidance_needs_enough_messages():
    r = avoided_structures(PRESENT_ONLY, "es", "A2")
    assert r["enough_data"] is False and r["items"] == []


def test_avoidance_flags_structures_never_produced_up_to_next_level():
    msgs = PRESENT_ONLY * (AVOIDANCE_MIN_MESSAGES // len(PRESENT_ONLY) + 1)
    ids = {i["id"] for i in avoided_structures(msgs, "es", "A2")["items"]}
    assert {"subjuntivo", "condicional", "preterito_perfecto", "imperfecto"} <= ids
    assert "clitics" not in ids  # "me llamo", "me gusta"
    used = msgs + ["Ayer fui al médico.", "Ojalá haga sol.", "Me gustaría un té.",
                   "Hoy he comido paella.", "Antes vivía en Rusia.", "Voy a cenar pronto."]
    assert avoided_structures(used, "es", "A2")["items"] == []


def test_avoidance_respects_stage_and_language():
    msgs = PRESENT_ONLY * 10
    a1 = {i["id"] for i in avoided_structures(msgs, "es", "A1")["items"]}
    assert "subjuntivo" not in a1 and "preterito_perfecto" in a1  # B1 is beyond A1's next stage
    assert avoided_structures(msgs, "it", "A2")["items"] == []     # no targets for this language yet
    assert avoided_structures(msgs, "es-ES", "A2")["items"]        # variant code works


# --- storage -------------------------------------------------------------
@pytest.fixture
def json_store(tmp_path, monkeypatch):
    for name in ["SETTINGS_PATH", "HISTORY_PATH", "PROGRESS_PATH", "LESSONS_PATH", "ERRORS_PATH"]:
        monkeypatch.setattr(storage, name, tmp_path / getattr(storage, name).name)
    return JsonStore()


def test_store_parity(json_store, tmp_path):
    sq = SqliteStore(tmp_path / "e.sqlite3")
    entry = make_entry({"error_category": "gender", "original": "el postal", "corrected": "la postal"},
                       mode="lesson", message="Quiero el postal")
    for st in (json_store, sq):
        st.add_error("roman", entry, created_at="2026-11-13T10:00:00")
        st.add_error("roman", entry)
    assert json_store.get_errors("roman") [0] == sq.get_errors("roman")[0]
    assert len(sq.get_errors("roman")) == 2 and sq.get_errors("ana") == []


def test_sqlite_backfills_structured_mistakes_once(tmp_path):
    path = tmp_path / "b.sqlite3"
    sq = SqliteStore(path)
    line = correction_to_text({"original": "en tren", "corrected": "en el tren", "error_category": "article"})
    sq.save_progress_note("roman", {"mistakes": [line, "old free text"]})
    assert sq.get_errors("roman") == []
    again = SqliteStore(path)  # next app start
    errs = again.get_errors("roman")
    assert len(errs) == 1 and errs[0]["error_category"] == "article" and errs[0]["backfilled"]
    SqliteStore(path)
    assert len(SqliteStore(path).get_errors("roman")) == 1  # not duplicated
    assert len(again.get_progress("roman")["mistakes"]) == 2  # mistakes untouched


# --- API -----------------------------------------------------------------
def test_api_logs_structured_corrections_and_summarizes(tmp_path, monkeypatch):
    monkeypatch.setenv("LINGMATE_DB_PATH", str(tmp_path / "api.db"))
    import main
    importlib.reload(main)
    from fastapi.testclient import TestClient

    class Svc:
        def free_talk(self, **kw):
            return {"reply": "Vale.", "source": "gemini", "vocab": [],
                    "correction": {"original": "la línea", "corrected": "la cola", "error_category": "lexical",
                                   "is_transfer": True, "transfer_source": "en"}}

    class Fallback:
        def free_talk(self, **kw):
            return {"reply": "Vale.", "source": "fallback", "vocab": [],
                    "correction": {"original": "a", "corrected": "b", "error_category": "article"}}

    client = TestClient(main.app)
    client.post("/api/setup", json={"user_id": "u", "target_language": "es", "level": "A2"})
    main.llm = Svc()
    client.post("/api/chat", json={"user_id": "u", "message": "Estoy en la línea."})
    main.llm = Fallback()
    client.post("/api/chat", json={"user_id": "u", "message": "hola"})
    body = client.get("/api/progress/u/errors").json()
    assert body["total"] == 1
    cat = body["categories"][0]
    assert cat["category"] == "lexical" and cat["trend"] == "new" and cat["transfer_sources"] == {"en": 1}
    assert body["avoided"]["messages_checked"] == 2 and body["avoided"]["enough_data"] is False
    assert json.dumps(body)  # serialisable (no sets / datetimes)
    assert client.get("/api/progress/nobody/errors").json()["total"] == 0


def test_articles_and_ia_nouns_do_not_count_as_clitics_or_imperfecto():
    msgs = ["Estoy en la cola.", "Mi familia vive en Vitoria.", "Muchas gracias.", "La farmacia está cerca."] * 10
    ids = {i["id"] for i in avoided_structures(msgs, "es", "A2")["items"]}
    assert {"clitics", "imperfecto"} <= ids
    assert "clitics" not in {i["id"] for i in avoided_structures(msgs + ["Lo compro mañana."], "es", "A2")["items"]}
