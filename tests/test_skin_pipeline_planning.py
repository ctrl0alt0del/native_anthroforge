"""The pure planner repairs explicit incompatibility and never infers it from failure."""

from dataclasses import replace

import pytest

from anthroforge.core.skin_pipeline import Assessment, Condition, Inputs, plan

READY = Assessment()
MISSING = Assessment(Condition.MISSING, "missing")
STALE = Assessment(Condition.STALE, "stale")
INCOMPATIBLE = Assessment(Condition.INCOMPATIBLE, "identity changed")


def state(**changes):
    return replace(Inputs(READY, READY, READY, READY, False), **changes)


@pytest.mark.parametrize("draft", [MISSING, STALE, INCOMPATIBLE])
def test_draft_repairs_without_running_later_stages(draft):
    assert plan("DRAFT", state(draft=draft)).stage == "envelope"


def test_compatible_final_update_preserves_stale_draft():
    assert plan("FINAL", state(draft=STALE)).stage == "deformation"
    assert plan("FINAL", state(draft=STALE, final_current=True)).stage == ""


def test_explicit_final_handoff_waits_for_current_draft_even_with_retained_reference():
    assert plan("FINAL", state(draft=STALE), handoff=True).stage == "envelope"
    assert plan("FINAL", state(draft=READY), handoff=True).stage == "deformation"


@pytest.mark.parametrize(
    "draft,topology,reference,expected",
    [
        (STALE, READY, MISSING, "reference"),
        (READY, MISSING, MISSING, "downstream"),
        (STALE, MISSING, MISSING, "construction"),
        (READY, READY, INCOMPATIBLE, "construction"),
    ],
)
def test_final_requests_only_required_prerequisites(draft, topology, reference, expected):
    inputs = state(draft=draft, topology=topology, reference=reference)
    assert plan("FINAL", inputs).stage == expected


@pytest.mark.parametrize("condition", [Condition.WAITING, Condition.FAILED, Condition.UNAVAILABLE])
def test_unready_sources_do_not_trigger_a_repair_loop(condition):
    result = plan("FINAL", state(sources=Assessment(condition, "source problem")))
    assert result.stage == "" and result.reason == "source problem"


def test_numerical_failure_is_not_a_rebuild_instruction():
    result = plan("FINAL", state(reference=Assessment(Condition.FAILED, "solver failed")))
    assert result.stage == "" and result.reason == "solver failed"
