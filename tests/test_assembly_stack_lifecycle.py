from anthroforge.application import storage
from anthroforge.core.mirroring import MirrorInstance
from tests.test_assembly_mapping import prepared
from tests.test_assembly_stacking import install, source_scene


def test_missing_provider_cannot_disappear_when_plan_is_explicitly_recalculated(session, tmp_path):
    bone, provider, receiver, source = source_scene(session, tmp_path)
    candidate = prepared(session, source, [receiver], dict(mappings={bone: bone}))
    install(session, candidate)
    key = candidate.identities[receiver]
    original = session.document.object(key)
    session.command("evaluate", entities=[key])
    session.wait(30)
    after = session.document.object(key)
    assert after.plan_result.status == "failed" and after.final_result.status == "failed"
    assert after.stack_plan.providers == original.stack_plan.providers
    verify_retained_package(session, tmp_path, provider)


def verify_retained_package(session, tmp_path, provider):
    path = tmp_path / "retained.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    loaded, resources = storage.read_package(path, session.engine)
    resources.require(loaded)
    assert any(r.source_entity == provider and r.surface_asset for r in loaded.external_references)


def test_changed_provider_preserves_manual_stage_until_requested(session, tmp_path):
    bone, provider, receiver, source = source_scene(session, tmp_path, mode="MANUAL")
    session.command("tissue.inflation", target=provider, changes=dict(amount=0.05))
    session.wait(30)
    options = dict(mappings={bone: bone, provider: provider})
    candidate = prepared(session, source, [receiver], options)
    before = candidate.merge(session.document).object(candidate.identities[receiver])
    install(session, candidate)
    assert session.document.object(before.id).final_result == before.final_result
    session.command("evaluate", entities=[before.id])
    session.wait(30)
    assert session.document.object(before.id).final_result.status == "ready"


def test_mirrored_automatic_provider_maps_to_its_explicit_surface_instance(session, tmp_path):
    bone, first, second, source = source_scene(session, tmp_path, mirrored=True)
    pending = prepared(session, source, [second], dict(mappings={bone: bone, first: first}))
    mirror = next(r for r in pending.mappings if r["source"] == first and r["instance"])
    mappings = {bone: bone, first: first}
    mappings[mirror["key"]] = dict(action="map", target=first, instance=bone)
    candidate = prepared(session, source, [second], dict(mappings=mappings))
    copied = candidate.merge(session.document).object(candidate.identities[second])
    assert candidate.ready and copied.final_result.status == "ready"
    assert MirrorInstance(first, bone).id in copied.stack_plan.providers
    assert any(r.source_instance == bone and r.instance == bone for r in candidate.references)
