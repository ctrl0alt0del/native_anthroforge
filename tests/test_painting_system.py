"""Application strokes complete without Qt, including finalization and undo."""

import sys

import pytest

from tests.test_skin_jobs import imported
from tests.test_tissue_painting import setup
from tests.test_tissue_painting_native import VIEW


@pytest.fixture(params=["tissue_weights", "collagen"])
def painting_case(session, monkeypatch, request):
    kind = request.param
    target = setup(session) if kind == "tissue_weights" else imported(session, monkeypatch)
    if kind == "collagen":
        session.command("skin.collagen.fill", owner=target, value=0)
    options = dict(consumer=kind, target=target, view=VIEW, brush=[1000, 1, 1, 1, True])
    if kind == "tissue_weights":
        options.update(name="paint", stage="final")
    return options


def begin(session, options):
    return session.command("painting.begin", **options)["token"]


def append(session, token, x=0):
    return session.command("painting.append", token=token, samples=[[x, 0]])


def test_finish_before_preview_completes_commits_once_without_desktop(session, painting_case):
    before, cursor = session.document, session.history.cursor
    token = begin(session, painting_case)
    append(session, token)
    session.command("painting.finish", token=token)
    assert session.scheduler.blocked
    session.wait()
    assert session.command("painting.status", token=token)["state"] == "committed"
    assert session.history.cursor == cursor + 1
    after = session.document
    session.command("undo")
    assert session.document.objects == before.objects and session.document.skin == before.skin
    session.command("redo")
    assert session.document.objects == after.objects and session.document.skin == after.skin


def test_cancellation_of_finalization_never_publishes(session, painting_case):
    before, cursor = session.document, session.history.cursor
    token = begin(session, painting_case)
    append(session, token)
    session.command("painting.finish", token=token)
    session.command("painting.cancel", token=token)
    session.wait()
    assert session.document is before and session.history.cursor == cursor
    with pytest.raises(ValueError):
        session.command("painting.commit", token=token)


def test_repeated_finish_and_commit_are_rejected(session, painting_case):
    token = begin(session, painting_case)
    append(session, token)
    session.command("painting.finish", token=token)
    with pytest.raises(ValueError, match="finished"):
        session.command("painting.finish", token=token)
    session.wait()
    cursor = session.history.cursor
    with pytest.raises(ValueError, match="committed"):
        session.command("painting.commit", token=token)
    assert session.history.cursor == cursor


def test_noop_stroke_has_no_undo_or_collagen_override(session, painting_case):
    painting_case["brush"][2] = 0
    before, cursor = session.document, session.history.cursor
    token = begin(session, painting_case)
    append(session, token)
    session.command("painting.finish", token=token)
    session.wait()
    assert session.document is before and session.history.cursor == cursor


def test_paging_rejects_replaced_candidate_without_mixing_values(session, painting_case):
    token = begin(session, painting_case)
    append(session, token)
    session.wait()
    page = session.command("painting.result", token=token, limit=1)
    append(session, token, 5)
    session.wait()
    with pytest.raises(ValueError, match="changed"):
        session.command("painting.result", token=token, expected_revision=page["revision"])
    values = session.command("painting.result", token=token)
    assert len(values["values"]) == values["total"]
    with pytest.raises(ValueError, match="limit"):
        session.command("painting.result", token=token, limit=16385)


def test_one_stroke_at_a_time_and_fixed_input_settings(session, painting_case):
    options = dict(painting_case, brush=dict(radius=1000, through=True))
    token = begin(session, options)
    options["brush"]["radius"] = 1
    with pytest.raises(ValueError, match="Finish"):
        begin(session, painting_case)
    append(session, token)
    session.wait()
    value = session.painting.values[painting_case["consumer"]]
    assert value.inputs.brush.radius == 1000
    assert value.asset["options"]["brush"][0] == 1000


def test_changed_baseline_blocks_pending_commit(session, painting_case):
    token = begin(session, painting_case)
    append(session, token)
    session.wait()
    target = painting_case["target"]
    if painting_case["consumer"] == "collagen":
        session.command("skin.collagen.fill", owner=target, value=0.2)
    else:
        session.command("tissue.field.remove", target=target, name="paint")
    before = session.document
    with pytest.raises(ValueError, match="inputs changed"):
        session.command("painting.finish", token=token)
    assert session.document is before


def test_sample_limit_and_empty_finish_are_atomic(session, painting_case):
    token = begin(session, painting_case)
    with pytest.raises(ValueError, match="sample"):
        session.command("painting.finish", token=token)
    with pytest.raises(ValueError, match="4,096"):
        session.command("painting.append", token=token, samples=[[0, 0]] * 4097)
    assert not session.painting.values[painting_case["consumer"]].inputs.samples
    append(session, token)
    session.command("painting.finish", token=token)
    session.wait()
    assert session.command("painting.status", token=token)["state"] == "committed"


def test_describe_is_readonly_and_unsupported_brush_is_rejected(session, painting_case):
    before, count = session.document, len(session.scheduler.jobs)
    value = session.command("painting.describe", **painting_case)
    assert value["available"] and value["radius_space"] == "SCREEN"
    assert session.document is before and len(session.scheduler.jobs) == count
    painting_case["brush"] = dict(space="WORLD")
    with pytest.raises(ValueError, match="screen"):
        begin(session, painting_case)


def test_previews_use_shared_application_not_qt(session, painting_case):
    loaded = {name for name in sys.modules if name.startswith("PySide6")}
    token = begin(session, painting_case)
    append(session, token)
    session.command("painting.finish", token=token)
    session.wait()
    assert {name for name in sys.modules if name.startswith("PySide6")} == loaded
