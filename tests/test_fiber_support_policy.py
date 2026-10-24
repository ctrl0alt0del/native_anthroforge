"""Nearby tissue must not become an undeclared deformation parent."""

import numpy as np

from anthroforge.application.fiber_supports import deformation_targets
from anthroforge.core.curve_dependencies import inputs
from anthroforge.core.results import Port
from anthroforge.core.surface_references import SurfaceReference
from tests.test_fiber_creation import bind, path
from tests.test_fiber_editing import edited_point
from tests.test_tissue_fiber_material import fiber_on_tissue


def source_curve(session, fiber):
    key = session.command("curve.create", points=[dict(position=p.position) for p in fiber.points])
    session.wait()
    return key


def test_creation_and_edit_near_tissue_do_not_add_anatomical_relationships(session):
    tissue, template = fiber_on_tissue(session)
    fiber = bind(session, session.document.entities[0].id, source_curve(session, template))
    assert all(s.reference.role == "SCP_GEOMETRY" for s in fiber.supports)
    position = np.asarray(fiber.points[1].position) + [0, 0.001, 0]
    changed = edited_point(session, fiber.id, 1, position.tolist())
    assert all(s.reference.role == "SCP_GEOMETRY" for s in changed.supports)
    before = path(session, fiber.id)
    session.command("tissue.inflation", target=tissue, side="b", changes=dict(amount=0.12))
    session.wait()
    np.testing.assert_array_equal(path(session, fiber.id), before)


def test_explicit_tissue_supports_are_retained_during_creation_and_edit(session):
    tissue, fiber = fiber_on_tissue(session)
    assert {s.reference.target for s in fiber.supports} == {tissue}
    position = np.asarray(fiber.points[1].position) + [0, 0.001, 0]
    changed = edited_point(session, fiber.id, 1, position.tolist())
    assert {s.reference.target for s in changed.supports} == {tissue}


def test_tissue_backed_field_uses_selected_supports_including_selected_bone():
    bone = SurfaceReference("bone")
    other = SurfaceReference("other")
    tissue = SurfaceReference("tissue", "TISSUE_FINAL")
    assert set(deformation_targets((bone, other, tissue), (bone, tissue))) == {bone, tissue}


def test_any_parent_edit_keeps_all_candidate_surface_dependencies(session):
    tissue, template = fiber_on_tissue(session)
    bone = session.document.entities[0].id
    fiber = bind(session, bone, source_curve(session, template))
    session.command("update_mode", entity=fiber.id, mode="MANUAL")
    session.command(
        "fiber.binding.scope", curve=fiber.id, point=fiber.points[0].id, scope="ANY_PARENT"
    )
    session.command(
        "curve.point.update", curve=fiber.id, point=fiber.points[0].id, position=[-0.2, 0.1, 0.7]
    )
    current = session.document.object(fiber.id)
    assert current.edit and fiber.points[0].id in current.edit.rebind
    assert Port(tissue, "final") in inputs(current, session.document.objects)
