"""First-class object contracts independent of SCP ownership and rendering."""

import json
import zipfile
from dataclasses import replace

import pytest

from anthroforge.application import storage
from anthroforge.application.changes import ChangeJournal
from anthroforge.application.resources import Resources
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import fields as curve_fields
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, Attachment
from anthroforge.core.fibers import Fiber, FiberBinding
from anthroforge.core.reference_images import ReferenceImage
from anthroforge.core.surfaces import Surface


def curve(**options):
    points = (CurvePoint(position=(0, 0, 0)), CurvePoint(position=(1, 0, 0)))
    return Curve(points, **curve_fields(options))


def bound_fiber(source, target):
    bindings = tuple(
        FiberBinding(point.id, target.id, Attachment(binding=(0.0,) * 28))
        for point in (source.points[0], source.points[-1])
    )
    return Fiber(points=source.points, bindings=bindings)


def test_curve_only_document_is_valid_and_uses_generic_lookup():
    source = curve()
    document = Document(objects=(source,))
    assert document.object(source.id) is source
    assert not document.entities
    with pytest.raises(ValueError, match="Unknown SCP"):
        document.entity(source.id)


def test_registry_reuses_unchanged_records_for_document_metadata():
    document = Document(objects=(curve(),))
    changed = replace(document, name="Renamed", revision=1)
    assert changed.registry is document.registry
    with pytest.raises(TypeError):
        document.registry.records["injected"] = curve()


def test_anatomical_and_object_identity_spaces_cannot_overlap():
    with pytest.raises(ValueError, match="unique"):
        Document(entities=(SCP("Root", id="same"),), objects=(curve(id="same"),))


def test_points_cannot_share_identity_by_coincidence():
    first = curve()
    with pytest.raises(ValueError, match="unique"):
        Document(objects=(first, replace(first, id="second")))


def test_parenting_and_workspace_association_remain_independent():
    root = SCP("Root")
    source = curve(owners=(root.id,))
    document = Document(entities=(root,), objects=(source,))
    assert not document.object(source.id).parent
    assert document.object(source.id).owners == (root.id,)


def test_reference_image_cannot_parent_a_curve():
    image = ReferenceImage(source="image-bytes")
    with pytest.raises(ValueError, match="cannot be a reference image"):
        Document(objects=(image, curve(parent=image.id)))


def test_missing_and_cyclic_transform_parenting_are_rejected():
    with pytest.raises(ValueError, match="Transform parent must exist"):
        Document(objects=(curve(parent="missing"),))
    with pytest.raises(ValueError, match="Cyclic ordinary"):
        Document(objects=(curve(id="a", parent="b"), curve(id="b", parent="a")))


def test_closed_curve_requires_three_authored_points():
    source = curve()
    with pytest.raises(ValueError, match="three authored points"):
        replace(source, closed=True)
    third = CurvePoint(position=(0, 1, 0))
    assert replace(source, points=(*source.points, third), closed=True).closed


def test_fiber_is_curve_and_accepted_by_surface_contract():
    root = SCP("Root")
    fiber = bound_fiber(curve(), root)
    other = curve()
    surface = Surface(curves=(CurveUse(fiber.id), CurveUse(other.id)))
    document = Document(entities=(root,), objects=(fiber, other, surface))
    assert isinstance(document.object(fiber.id), Curve)
    assert document.object(surface.id).curves[0].curve == fiber.id


def test_unbound_and_partially_bound_open_fibers_are_rejected():
    source = curve()
    with pytest.raises(ValueError, match="both endpoint bindings"):
        Fiber(source.points)
    fiber = bound_fiber(source, SCP("Root"))
    with pytest.raises(ValueError, match="both endpoint bindings"):
        replace(fiber, bindings=fiber.bindings[:1])


def test_closed_fiber_needs_one_binding_not_three():
    fiber = bound_fiber(curve(), SCP("Root"))
    points = (*fiber.points, CurvePoint(position=(0, 1, 0)))
    closed = replace(fiber, points=points, closed=True, bindings=fiber.bindings[:1])
    assert len(closed.bindings) == 1
    with pytest.raises(ValueError, match="at least one"):
        replace(closed, bindings=())


def test_fiber_copy_remaps_points_and_bindings_atomically():
    from anthroforge.application.curve_copy import clone, mapping

    root = SCP("Root")
    original = bound_fiber(curve(), root)
    copied = clone(original, mapping(original))
    assert isinstance(copied, Fiber)
    assert copied.id != original.id
    assert {b.point for b in copied.bindings} == {p.id for p in copied.points}
    assert {b.target for b in copied.bindings} == {root.id}


def test_fiber_cannot_bind_to_another_curve():
    target = curve()
    fiber = bound_fiber(curve(), target)
    with pytest.raises(ValueError, match="anatomical surface provider"):
        Document(objects=(target, fiber))


def test_generic_objects_round_trip_without_indexes_or_type_loss():
    root = SCP("Root")
    fiber = bound_fiber(curve(), root)
    image = ReferenceImage(source="source", parent=fiber.id)
    document = Document(entities=(root,), objects=(fiber, image))
    state = json.loads(json.dumps(storage.document_state(document)))
    assert not any(key.startswith("_") for key in state)
    restored = storage.decode_document(state)
    assert restored == document
    assert isinstance(restored.object(fiber.id), Fiber)


def test_construction_changes_are_incremental_and_distinct_from_anatomy():
    source = curve()
    before = Document(objects=(source,))
    journal = ChangeJournal()
    journal.record(before, replace(before, objects=(replace(source, name="Changed"),)))
    delta = journal.since(0)
    assert delta.objects == {source.id: {"name"}}
    assert not delta.entities and not delta.controls


@pytest.mark.parametrize("version", [1, 2, 3, 7])
def test_other_project_schemas_rejected_before_loading_assets(tmp_path, session, version):
    path = tmp_path / "unsupported.anthroforge"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "manifest.json", json.dumps({"format": storage.FORMAT, "version": version})
        )
    with pytest.raises(ValueError, match="Unsupported AnthroForge project"):
        storage.read_package(path, session.engine)


def test_curve_only_package_round_trips_with_current_schema(tmp_path, session):
    path = tmp_path / "curves.anthroforge"
    document = Document(objects=(curve(engine="POLYLINE"),))
    storage.atomic_save(path, document, Resources())
    restored, assets = storage.read_package(path, session.engine)
    assert restored == document and assets == Resources()
    with zipfile.ZipFile(path) as archive:
        assert json.loads(archive.read("manifest.json"))["version"] == storage.VERSION
