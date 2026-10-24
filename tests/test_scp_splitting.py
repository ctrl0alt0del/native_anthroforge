"""Connected SCP splitting preserves hierarchy and coherent authoring transactions."""

import numpy as np
import pytest

from anthroforge.application import primitive_operations
from anthroforge.native import paths
from tests.conftest import CUBE


def body(session):
    root = session.command("import", path=str(CUBE), units=1)["entity_id"]
    session.wait(5)
    target = session.command("primitive.create", kind="BODY", shape="BOX", parent=root)
    session.wait(5)
    curve = primitive_operations.definition(session, target).curves[0]
    session.command(
        "point.insert", entity=target, curve=curve.id, index=1, point=dict(position=[0, 0.25, 0.15])
    )
    session.wait(5)
    return target, primitive_operations.definition(session, target).curves[0]


def test_split_keeps_first_identity_children_and_shared_hook(session):
    target, source = body(session)
    child = session.command("scp.empty", parent=target, name="Child")
    before = session.history.cursor
    result = session.command("scp.split", entity=target, points=[source.points[1].id])
    session.wait(5)
    first, second = result["entities"]
    assert first == target and session.document.entity(child).parent == first
    assert session.document.entity(second).parent == session.document.entity(first).parent
    assert len(result["controls"]) == 1 and session.history.cursor == before + 1
    assert all(session.document.entity(k).result.status == "ready" for k in (first, second))
    check_joint(session, result)
    session.command("undo")
    assert second not in session.document.registry.records
    assert len(session.document.object(source.id).points) == 3


def check_joint(session, result):
    hook = result["controls"][0]
    session.command("control.transform", control=hook, values=[0, 0.5, 0, 0, 0, 0, 1, 1, 1])
    session.wait(5)
    definitions = [primitive_operations.definition(session, k) for k in result["entities"]]
    bindings = [session.document.entity(k).deformers for k in result["entities"]]
    assert all(any(b.control == hook and b.restrict for b in group) for group in bindings)
    assert definitions[0].curves[0].points[-1].id != definitions[1].curves[0].points[0].id
    endpoints = resolved_ends(session, result["entities"])
    np.testing.assert_allclose(endpoints[0], endpoints[1], atol=1e-12)
    session.command("undo")


def test_invalid_split_is_atomic(session):
    target, source = body(session)
    document, cursor = session.document, session.history.cursor
    with pytest.raises(ValueError, match="interior"):
        session.command("scp.split", entity=target, points=[source.points[0].id])
    assert session.document == document and session.history.cursor == cursor


def test_native_segment_preserves_positions_and_roll(session):
    from anthroforge.native import curve_editing

    _, source = body(session)
    original = paths.body(paths.evaluate(session.engine, source))
    for first, last in ((0, 1), (1, 2)):
        segment = curve_editing.segment(session.engine, source, first, last)
        actual = paths.body(paths.evaluate(session.engine, segment))
        expected = original[first * source.resolution : last * source.resolution + 1]
        np.testing.assert_allclose(actual[:, :3], expected[:, :3], atol=1e-12)
        np.testing.assert_allclose(actual[1:-1, 6:9], expected[1:-1, 6:9], atol=0.02)


def resolved_ends(session, entities):
    from anthroforge.application.construction_evaluator import Evaluation
    from anthroforge.native.mesh import NativeCancellation

    evaluation = make_evaluator(session, Evaluation, NativeCancellation)
    result = []
    for i, target in enumerate(entities):
        item = session.document.entity(target)
        definition = primitive_operations.definition(session, target)
        samples = evaluation.curve(item, definition.curves[0], definition)
        result.append(samples[-1 if i == 0 else 0, :3])
    return result


def make_evaluator(session, evaluator, cancellation):
    return evaluator(
        session.engine,
        session.document,
        {k: a.mesh for k, a in session.assets.items()},
        cancellation(session.engine),
        session.resources.paths,
    )


def test_split_roundtrip_and_redo_keep_shared_control(session, tmp_path):
    target, source = body(session)
    result = session.command("scp.split", entity=target, points=[source.points[1].id])
    session.wait(5)
    session.command("undo")
    session.command("redo")
    session.wait(5)
    assert all(k in session.document.registry.records for k in result["entities"])
    output = tmp_path / "split.anthroforge"
    session.command("save", path=str(output), blocked_policy="wait")
    session.command("open", path=str(output))
    check_joint(session, result)
