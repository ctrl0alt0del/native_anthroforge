"""No implicit writer disabling or lost shortcuts during identity-preserving replacement."""

from dataclasses import replace

import pytest

from anthroforge.application.storage import write_package
from tests.test_driving_formulas import driver, reference
from tests.test_skeleton_update_commands import prepare


def conflicting_source(session, bone, tmp_path):
    key, formula = driver(session, bone, "64", path=reference(bone, ("primitive", "samples")))
    session.wait()
    item = session.document.entity(bone)
    changed = replace(item, primitive=replace(item.primitive, samples=96))
    source = replace(
        session.document,
        entities=tuple(changed if e.id == bone else e for e in session.document.entities),
    )
    path = tmp_path / "conflict.anthroforge"
    write_package(path, source, session.resources)
    return path, key, formula


def apply(session, state):
    session.command(
        "skeleton_update.apply",
        token=state["token"],
        approved=[f["key"] for f in state["findings"] if f["acknowledge"]],
    )


def test_formula_value_conflict_requires_choice(session, assembly, tmp_path):
    _, bone = assembly
    path, _, formula = conflicting_source(session, bone, tmp_path)
    state = prepare(session, path, {bone: bone})
    assert not state["ready"]
    assert any(f["key"] == "driver_value:" + formula for f in state["findings"]), state["findings"]
    with pytest.raises(ValueError):
        apply(session, state)
    state = prepare(session, path, {bone: bone}, use_formula_values=[formula])
    assert state["ready"], state["findings"]
    apply(session, state)
    assert session.document.entity(bone).primitive.samples == 64
    assert len(session.document.driving_shortcuts) == 1


def test_explicit_disabling_preserves_replacement_value(session, assembly, tmp_path):
    _, bone = assembly
    path, key, formula = conflicting_source(session, bone, tmp_path)
    state = prepare(session, path, {bone: bone}, disable_formulas=[formula])
    assert state["ready"], state["findings"]
    apply(session, state)
    session.wait()
    assert session.document.entity(bone).primitive.samples == 96
    assert not session.document.formula_index.drivers[key].formulas[0].enabled
