"""Independent construction copies retain controls and remap only internal relationships."""

from dataclasses import asdict

import pytest

from tests.test_driving_formulas import driver, reference
from tests.test_parametric_curves import circle_settings, create
from tests.test_tissue_parts_workflow import branched_tissue


def hierarchy(session):
    root = session.command("scp.empty", name="Root")
    child = session.command("scp.empty", name="Child", parent=root)
    session.wait(5)
    return root, child


def copied_driver(session, target):
    return next(
        d
        for d in session.document.driving_shortcuts
        if any(f.target.target == target for f in d.formulas)
    )


def controlled_child(session):
    root, child = hierarchy(session)
    ref = reference(child, ("transform", "position"), 0)
    wrapper = session.command("shortcut.expose", reference=ref, label="Child X")
    key, formula = driver(session, child, "value*m", value=0.25, path=ref)
    session.wait(5)
    return root, child, ref, wrapper, key, formula


def duplicate(session, target):
    copied = session.command("scp.duplicate", entity=target)
    session.wait(5)
    return copied


def test_duplicate_preserves_exposure_and_independent_formula_control(session):
    _, child, ref, wrapper, original, formula = controlled_child(session)
    copied = session.command("scp.duplicate", entity=child)
    session.wait(5)
    clone = copied_driver(session, copied)
    assert clone.id != original and clone.formulas[0].id != formula
    copied_ref = dict(ref, target=copied)
    exposed = session.command("shortcut.inspect", reference=copied_ref)
    assert exposed["exposed"] and exposed["label"] == "Child X" and exposed["id"] != wrapper
    session.command("driver.value", driver=clone.id, value=0.75)
    session.wait(5)
    assert session.command("property.get", reference=copied_ref)["value"] == pytest.approx(0.75)
    assert session.command("property.get", reference=ref)["value"] == pytest.approx(0.25)


def test_duplicate_controls_are_one_undo_action(session):
    _, child, _, _, _, _ = controlled_child(session)
    before, cursor = session.document, session.history.cursor
    copied = session.command("scp.duplicate", entity=child)
    session.wait(5)
    assert len(session.document.driving_shortcuts) == 2
    assert session.history.cursor == cursor + 1
    session.command("undo")
    assert session.document.shortcuts == before.shortcuts
    assert session.document.driving_shortcuts == before.driving_shortcuts
    assert copied not in session.document.registry.records
    session.command("redo")
    session.wait(5)
    assert len(session.document.driving_shortcuts) == 2


def test_duplicate_retains_explicit_external_virtual_input(session):
    _, child = hierarchy(session)
    external = session.command("driver.create", value=2.0)
    ref = reference(child, ("transform", "position"), 0)
    driver(
        session, child, "(offset+value)*m", inputs=[dict(name="offset", driver=external)], path=ref
    )
    session.wait(5)
    copied = session.command("scp.duplicate", entity=child)
    session.wait(5)
    assert copied_driver(session, copied).formulas[0].inputs[0].driver == external
    session.command("driver.value", driver=external, value=3.0)
    session.wait(5)
    assert session.command("property.get", reference=dict(ref, target=copied))["value"] == 3.0
    assert session.command("property.get", reference=ref)["value"] == 3.0


def test_parametric_consumer_independence_copies_variable_control(session):
    source = create(session, **circle_settings())
    body = session.command("primitive.from_curves", curves=[source], kind="BODY")
    variable = session.document.object(source).engine_settings.variables[0].id
    ref = reference(source, ("engine_settings", "variables", "@" + variable, "value"))
    driver(session, source, "value*m", value=0.4, path=ref)
    session.wait(5)
    copied = session.command("primitive.make_independent", entity=body, curve=source)
    session.wait(5)
    clone = copied_driver(session, copied)
    copied_variable = session.document.object(copied).engine_settings.variables[0].id
    assert copied_variable != variable
    assert clone.formulas[0].target.path[2] == "@" + copied_variable
    copied_ref = asdict(clone.formulas[0].target)
    assert session.command("property.get", reference=copied_ref)["value"] == 0.4


def test_independence_retargets_existing_consumer_property_addresses(session):
    source = create(session)
    body = session.command("primitive.from_curves", curves=[source], kind="BODY")
    session.command("consumer.sampling", entity=body, curve=source, samples=12)
    ref = reference(body, ("primitive", "curves", "@" + source, "samples"))
    session.command("shortcut.expose", reference=ref, label="Body samples")
    key, _ = driver(session, body, "12", path=ref)
    session.wait(5)
    copied = session.command("primitive.make_independent", entity=body, curve=source)
    session.wait(5)
    updated = reference(body, ("primitive", "curves", "@" + copied, "samples"))
    assert session.command("shortcut.inspect", reference=updated)["label"] == "Body samples"
    current = next(d for d in session.document.driving_shortcuts if d.id == key)
    assert asdict(current.formulas[0].target) == updated


def controlled_tree(session, virtual):
    _, child = hierarchy(session)
    leaf = session.command("scp.empty", name="Leaf", parent=child)
    ref = reference(child, ("transform", "position"), 0)
    first, _ = driver(session, child, "value*m", value=0.25, path=ref)
    source = dict(name="up", driver=first) if virtual else dict(name="up", property=ref)
    expression = "(up+1)*m" if virtual else "up+m"
    driver(session, leaf, expression, inputs=[source], path=dict(ref, target=leaf))
    session.wait(5)
    return child, leaf, ref


@pytest.mark.parametrize("virtual", [True, False])
def test_duplicate_remaps_internal_driver_and_property_chains_once(session, virtual):
    child, leaf, ref = controlled_tree(session, virtual)
    copied = duplicate(session, child)
    new_leaf = next(e.id for e in session.document.entities if e.parent == copied)
    first, second = copied_driver(session, copied), copied_driver(session, new_leaf)
    source = second.formulas[0].inputs[0]
    assert source.driver == first.id if virtual else source.property.target == copied
    session.command("driver.value", driver=first.id, value=0.75)
    session.wait(5)
    assert session.command("property.get", reference=dict(ref, target=new_leaf))["value"] == 1.75
    assert session.command("property.get", reference=dict(ref, target=leaf))["value"] == 1.25
    assert len(session.document.driving_shortcuts) == 4


def test_duplicate_excludes_outputs_outside_copied_construction(session):
    root, child, ref, _, key, _ = controlled_child(session)
    session.command(
        "driver.formula.add", driver=key, target=dict(ref, target=root), expression="value*m"
    )
    session.wait(5)
    copied = duplicate(session, child)
    clone = copied_driver(session, copied)
    assert len(clone.formulas) == 1 and clone.formulas[0].target.target == copied
    session.command("driver.value", driver=clone.id, value=0.5)
    session.wait(5)
    assert session.command("property.get", reference=dict(ref, target=root))["value"] == 0.25


def test_duplicate_remaps_descendant_policy_and_preserves_control_order(session):
    _, child, ref, wrapper, key, _ = controlled_child(session)
    leaf = session.command("scp.empty", name="Leaf", parent=child)
    policy = dict(descendants=[dict(target=leaf, follow_rotation="DISABLED")])
    session.command("shortcut.configure", reference=ref, policy=policy)
    session.command("shortcut.reorder", identities=[key, wrapper])
    copied = duplicate(session, child)
    new_leaf = next(e.id for e in session.document.entities if e.parent == copied)
    clone = copied_driver(session, copied)
    control = session.command("shortcut.inspect", reference=dict(ref, target=copied))
    assert control["policy"]["descendants"][0]["target"] == new_leaf
    assert session.document.shortcut_order == (key, wrapper, clone.id, control["id"])


def test_pending_manual_copy_keeps_accepted_value_and_pending_definition(session):
    _, child, ref, _, key, _ = controlled_child(session)
    session.command("update_mode", entity=child, mode="MANUAL")
    session.command("driver.value", driver=key, value=0.75)
    copied = duplicate(session, child)
    clone = copied_driver(session, copied)
    assert clone.value == 0.75
    assert session.command("property.get", reference=dict(ref, target=copied))["value"] == 0.25
    result = next(r for r in session.document.formula_results if r.formula == clone.formulas[0].id)
    assert result.status == "pending" and result.value == 0.25
    session.command("evaluate", entities=[copied])
    session.wait(5)
    assert session.command("property.get", reference=dict(ref, target=copied))["value"] == 0.75
    assert session.command("property.get", reference=ref)["value"] == 0.25


def test_branched_tissue_independence_keeps_part_formula_and_exposure(session):
    _, target, branch = branched_tissue(session)
    session.command("tissue.inflation", target=target, part=branch, changes=dict(amount=0.13))
    ref = reference(target, ("parts", "@" + branch, "a", "inflation", "amount"))
    session.command("shortcut.expose", reference=ref, label="Branch thickness")
    key, _ = driver(session, target, "0.13*m", path=ref)
    session.wait(5)
    copied = session.command("consumer.make_independent", entity=target)
    session.wait(5)
    new_branch = session.document.object(copied).branches[0].id
    new_ref = reference(target, ("parts", "@" + new_branch, "a", "inflation", "amount"))
    assert session.command("shortcut.inspect", reference=new_ref)["label"] == "Branch thickness"
    current = next(d for d in session.document.driving_shortcuts if d.id == key)
    assert asdict(current.formulas[0].target) == new_ref
    assert session.command("property.get", reference=new_ref)["value"] == 0.13
