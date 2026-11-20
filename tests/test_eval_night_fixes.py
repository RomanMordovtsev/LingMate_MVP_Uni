"""docs/feedback/2026-11-16: phantom corrections (§5), one date per night (§4),
`ollama pull` progress bars out of the log (§3). No network."""
import json

import eval.run as runner
from core.feedback import is_phantom_correction
from eval.logfilter import clean_pull_output, main as logfilter_main
from tests.test_eval_harness import QUEUE
from tests.test_feedback import PROGRESS, SETTINGS, FlakyProvider, _svc


def _c(original, corrected):
    return {"original": original, "corrected": corrected}


# --- §5 phantom corrections -------------------------------------------------------

def test_flash_lite_aproveche_corrections_are_phantom():
    # Both real 15.11 outputs (with and without profile) on the clean case.
    assert is_phantom_correction(_c("Que aproveche!", "¡Que aproveche!"), "¡Que aproveche!")
    assert is_phantom_correction(_c("Que", "¡Que"), "¡Que aproveche!")


def test_real_corrections_are_kept():
    assert not is_phantom_correction(_c("esta bien", "está bien"), "esta bien")
    assert not is_phantom_correction(_c("Que aproveche!", "¡Que aproveche!"), "Que aproveche!")
    # "la" is not inside any "el": a genuine swap even though "el" is in the message.
    assert not is_phantom_correction(_c("la", "el"), "el chico y la problema")
    # the original occurs once uncovered next to an already-correct occurrence
    assert not is_phantom_correction(_c("esta", "está"), "Está bien, esta casa")
    # model paraphrased: neither span is in the message -> not our call
    assert not is_phantom_correction(_c("yo es", "estoy"), "Yo soy cansado")
    # case and accents are exact: a capitalisation fix is real
    assert not is_phantom_correction(_c("madrid", "Madrid"), "vivo en madrid")


def test_edge_inputs():
    assert not is_phantom_correction(None, "hola")
    assert not is_phantom_correction(_c("a", "b"), "")
    assert not is_phantom_correction(_c("hola", "hola"), "hola")
    assert is_phantom_correction(_c("", "Muchas gracias."), "Muchas  gracias.")
    assert not is_phantom_correction(_c("", "gracias"), "Muchas gracias.")


def test_no_true_detection_lost_on_eval_cases():
    """Every case's gold pair (original -> first acceptable) is a real correction."""
    from tests.test_eval_cases import _cases
    for _, _, case in _cases():
        for good in case.get("acceptable") or []:
            if good != case["original"]:
                assert not is_phantom_correction(_c(case["original"], good), case["original"]), case["id"]


def test_service_drops_phantom_in_chat_and_lesson():
    resp = {"reply": "¡Igualmente!", "roleplay_reply": "Gracias.", "vocab": [], "encouragement": "",
            "progress_note": "", "should_finish": False,
            "correction": {"original": "Que", "corrected": "¡Que", "error_category": "spelling_accent"}}
    svc = _svc(FlakyProvider([], resp))
    r1 = svc.free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="¡Que aproveche!")
    resp["correction"] = {"original": "Que", "corrected": "¡Que", "error_category": "spelling_accent"}
    r2 = svc.lesson_turn(settings=SETTINGS, lesson={"scenario_id": "coffee_shop"}, history=[],
                         message="¡Que aproveche!")
    assert r1["correction"] is None and r2["correction"] is None
    resp["correction"] = {"original": "Que", "corrected": "¡Que", "error_category": "spelling_accent"}
    r3 = svc.free_talk(settings=SETTINGS, progress=PROGRESS, history=[], message="Que aproveche!")
    assert r3["correction"]["corrected"] == "¡Que"


# --- §4 one date per night ----------------------------------------------------------

def test_eval_run_date_flag(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    cases = tmp_path / "c.jsonl"
    cases.write_text(json.dumps(dict(QUEUE, target="es-ES", l1="ru")) + "\n", encoding="utf-8")
    out = tmp_path / "r"
    assert runner.main(["--provider", "rule", "--cases", str(cases), "--out", str(out),
                        "--date", "2026-11-15"]) == 0
    names = sorted(p.name for p in out.iterdir())
    assert names[0].startswith("2026-11-15-rule-none")
    assert json.loads((out / names[0]).read_text(encoding="utf-8"))["meta"]["date"] == "2026-11-15"


def test_nightly_script_passes_one_date_and_keeps_unpicked_reports():
    ps = open("scripts/nightly_eval.ps1", encoding="utf-8").read()
    assert "--date $date" in ps and "eval.compare --date $date" in ps and "eval.hybrid --date $date" in ps
    assert "git ls-tree -r --name-only origin/agent/dev eval/reports" in ps
    assert "-notmatch $date" not in ps          # the date-based archive rule is gone
    assert "ollama pull" not in ps              # downloads live in pull_candidates.ps1


# --- §3 pull log ---------------------------------------------------------------------

PULL = ("pulling manifest \x1b[?25l\x1b[1G\x1b[K⠋ pulling manifest \x1b[1G\x1b[Kpulling manifest\n"
        + "".join(f"\rpulling 4e30e2665218:  {p}% ▕██████        ▏ 1.{p} GB/4.6 GB  30 MB/s  1m"
                  for p in range(0, 100))
        + "\rpulling 4e30e2665218: 100% ▕████████████████▏ 4.6 GB\n"
        + "\rpulling 7a1b2c3d4e5f:  50% ▕████    ▏ 10 B/20 B\rpulling 7a1b2c3d4e5f: 100% ▕████████▏ 20 B\n"
        + "verifying sha256 digest\nwriting manifest\nsuccess\n")


def test_pull_progress_is_collapsed():
    out = clean_pull_output(PULL).splitlines()
    assert out == ["pulling manifest",
                   "pulling 4e30e2665218: 100% 4.6 GB",
                   "pulling 7a1b2c3d4e5f: 100% 20 B",
                   "verifying sha256 digest", "writing manifest", "success"]


def test_pull_errors_survive(tmp_path, capsys):
    f = tmp_path / "err.txt"
    f.write_text("pulling manifest\nError: pull model manifest: file does not exist\n", encoding="utf-8")
    assert logfilter_main([str(f), str(tmp_path / "missing.txt")]) == 0
    assert "Error: pull model manifest: file does not exist" in capsys.readouterr().out


def test_big_log_shrinks():
    assert len(clean_pull_output(PULL)) < len(PULL) / 20
