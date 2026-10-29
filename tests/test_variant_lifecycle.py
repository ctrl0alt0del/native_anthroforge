import pytest

from tests.test_driving_formulas import curve, driver, reference
from tests.test_shortcut_copy import copied_driver
from tests.test_variant_review import apply, review
from tests.test_variants import variant


def shared_control(session):
    source = curve(session)
    root = session.command("scp.empty", name="Root")
    first = session.command("primitive.from_curves", curves=[source], kind="BODY", parent=root)
    second = session.command("primitive.from_curves", curves=[source], kind="BODY", parent=root)
    control, _ = driver(session, source, "value", value=24, kind="INTEGER")
    session.wait()
    return source, first, second, control


def test_variant_driver_does_not_disable_shared_source_for_outside_consumer(session):
    source, first, second, original = shared_control(session)
    key = variant(session, first)
    copied = session.document.entity(first).primitive.curves[0].curve
    clone = copied_driver(session, copied)
    assert copied_driver(session, source).id == original
    session.command("driver.value", driver=clone.id, value=30)
    session.wait()
    assert session.document.object(source).resolution == 24
    promoted_driver_values(session, key, original, source, copied)
    assert session.document.entity(second).primitive.curves[0].curve == source


def promoted_driver_values(session, key, original, source, copied):
    session.command("variant.leave")
    apply(session, review(session, key))
    session.command("driver.value", driver=original, value=32)
    session.wait()
    assert session.document.object(source).resolution == 32
    assert session.document.object(copied).resolution == 30


def test_root_undo_releases_runtime_context_and_redo_restores_saved_edits(session, assembly):
    key = variant(session, assembly[1])
    session.command("scp.rename", entity=assembly[1], name="Variant edit")
    session.command("variant.leave")
    session.command("undo")
    session.wait()
    assert key not in session.contexts.states
    session.command("redo")
    session.command("variant.enter", variant=key)
    assert session.document.entity(assembly[1]).name == "Variant edit"


def test_removal_protects_checkpoint_links_and_is_undoable(session, assembly):
    key = variant(session, assembly[1])
    checkpoint = session.command("variant.checkpoint")["id"]
    with pytest.raises(ValueError, match="dependent"):
        session.command("variant.remove", variant=key)
    session.command("variant.remove", variant=checkpoint)
    session.command("variant.remove", variant=key)
    session.wait()
    assert key not in session.contexts.states
    session.command("undo")
    session.command("variant.enter", variant=key)
    assert session.contexts.visible == key


def test_support_status_changes_and_refresh_does_not_change_accepted(session):
    from tests.test_tissue_workflow import assembly

    bone, _, tissue = assembly(session)
    key = variant(session, tissue)
    session.command("variant.leave")
    session.command("scp.transform", entity=bone, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    session.wait()
    before = session.document
    assert session.command("variant.inspect")["variants"][0]["outdated"]
    apply(session, review(session, key, mode="refresh"))
    assert session.document.entities == before.entities
    assert not session.command("variant.inspect")["variants"][0]["outdated"]


def test_promotion_evaluates_manual_required_formula_failure_as_blocking(session):
    source, target, _, _ = shared_control(session)
    key = variant(session, target)
    copied = session.document.entity(target).primitive.curves[0].curve
    clone = copied_driver(session, copied)
    session.command("update_mode", entity=target, mode="MANUAL")
    session.command("driver.formula.remove", driver=clone.id, formula=clone.formulas[0].id)
    driver(session, copied, "12.0", path=reference(copied))
    session.wait()
    session.command("variant.leave")
    result = review(session, key)
    assert any(f["blocking"] and f["kind"] == "failure" for f in result["findings"])
    with pytest.raises(ValueError, match="Resolve"):
        apply(session, result)


def test_refresh_copies_accepted_driven_support_values_without_rewriting_formulas(session):
    source, first, second, original = shared_control(session)
    key = variant(session, first)
    session.command("variant.leave")
    session.command("driver.value", driver=original, value=32)
    session.wait()
    apply(session, review(session, key, mode="refresh"))
    session.command("variant.enter", variant=key)
    assert session.document.object(source).resolution == 32
    with pytest.raises(ValueError, match="pinned"):
        session.command("object.rename", target=source, name="Pinned edit")
