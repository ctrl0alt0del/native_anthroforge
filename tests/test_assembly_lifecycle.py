from dataclasses import replace
from threading import Event

import pytest

from anthroforge.application import assembly_candidate, assembly_source, storage
from anthroforge.core.fibers import Fiber
from anthroforge.core.jobs import ObsoleteInputs
from tests.test_assembly_bindings import changed_target
from tests.test_assembly_mapping import captured, prepared
from tests.test_fiber_creation import CUBE, scene


def test_mapped_target_edits_obsolete_the_prepared_graph(session, tmp_path):
    target, fiber, source = captured(session, tmp_path)
    candidate = prepared(session, source, [fiber.id], dict(mappings={target: target}))
    item = session.document.entity(target)
    session.replace_entities({target: replace(item, name="Edited while preparing")})
    with pytest.raises(ObsoleteInputs, match="mapped destination"):
        candidate.merge(session.document)


def double_support(session, tmp_path):
    first, curve = scene(session)
    second = session.command("import", path=str(CUBE), units=1, parent=first)["entity_id"]
    session.wait()
    item = session.document.object(curve)
    bindings = [
        dict(point=item.points[0].id, target=first),
        dict(point=item.points[-1].id, target=second),
    ]
    session.command("fiber.create", curve=curve, bindings=bindings)
    session.wait()
    fiber = next(v for v in session.document.objects if isinstance(v, Fiber))
    path = tmp_path / "two-supports.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    return first, second, fiber, assembly_source.inspect(str(path), Event())


def test_rebinding_one_support_keeps_other_unresolved_binding(session, tmp_path):
    first, second, fiber, source = double_support(session, tmp_path)
    destination = changed_target(session, first)
    options = dict(mappings={first: dict(action="map", target=first, rebind=True)})
    candidate = prepared(session, source, [fiber.id], options, destination)
    assert candidate.ready, candidate.findings
    item = candidate.merge(destination).object(candidate.identities[fiber.id])
    assert item.bindings[1].attachment.binding == fiber.bindings[1].attachment.binding
    assert item.result.status == "invalid"
    assert any(r.source_entity == second and not r.target for r in candidate.references)
    assert candidate.evidence[0]["before"] and candidate.evidence[0]["after"]


def test_inherited_mirror_rule_is_editable_without_anatomical_placeholder(session, tmp_path):
    from tests.test_assembly_mirrors import mirrored_source

    candidate = prepared(session, mirrored_source(session, tmp_path), ["child"])
    session.begin()
    assembly_candidate.install(session, candidate)
    session.commit()
    rule = next(r for r in session.document.mirror_rules if r.scope)
    session.command("mirror.configure", target=rule.target, shift=0.8)
    assert session.document.mirrors.rules[rule.target].shift == 0.8
    assert rule.target not in session.document.registry.records
    session.command("undo")
    assert session.document.mirrors.rules[rule.target].shift == 0.2


def test_import_cannot_merge_into_an_unfinished_gesture(session, tmp_path):
    from tests.test_assembly_commands import prepared as command_prepared

    _, token = command_prepared(session, tmp_path)
    session.begin()
    before = session.document
    with pytest.raises(ValueError, match="current gesture"):
        session.command("assembly.import", token=token)
    assert session.document is before and session.history.before is not None
    session.cancel()
    session.command("assembly.import", token=token)


def test_removing_last_consumer_releases_missing_reference_with_undo(session, tmp_path):
    from tests.test_assembly_repair import missing_import

    _, key = missing_import(session, tmp_path)
    references = session.document.external_references
    assert references
    session.command("object.delete", target=key)
    assert not session.document.external_references
    session.command("undo")
    assert session.document.external_references == references
