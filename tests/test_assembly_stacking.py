from pathlib import Path
from threading import Event

from anthroforge.application import assembly_candidate, assembly_source, storage
from tests.test_assembly_mapping import prepared
from tests.test_assembly_repair import resolve
from tests.test_tissue_stack_workflow import assembly


def source_scene(session, tmp_path, mode="LIVE", mirrored=False):
    bone, provider, receiver = assembly(session)
    session.command("update_mode", entity=receiver, mode=mode)
    if mirrored:
        session.command("mirror.configure", target=bone, enabled=True, shift=0)
    session.wait(30)
    path = tmp_path / "stacking.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    source = assembly_source.inspect(str(path), Event())
    session.replace_document(objects=tuple(v for v in session.document.objects if v.id != receiver))
    session.wait(30)
    return bone, provider, receiver, source


def install(session, candidate):
    assert candidate.ready, candidate.findings
    session.begin()
    result = assembly_candidate.install(session, candidate)
    session.commit()
    session.wait(30)
    return result


def test_missing_automatic_provider_blocks_only_final_and_repairs_without_source(session, tmp_path):
    bone, provider, receiver, source = source_scene(session, tmp_path)
    candidate = prepared(session, source, [receiver], dict(mappings={bone: bone}))
    install(session, candidate)
    key = candidate.identities[receiver]
    before = session.document.object(key)
    missing = [r for r in session.document.external_references if not r.target]
    assert len(missing) == 1 and missing[0].source_entity == provider
    assert_missing(before, missing[0])
    Path(source.original).unlink()
    resolve(session, {missing[0].id: dict(action="map", target=provider)})
    session.wait(30)
    after = session.document.object(key)
    assert after.final_result.status == "ready"
    assert after.final_result.asset == before.final_result.asset


def assert_missing(item, reference):
    assert item.intrinsic_result.status == "ready" and item.final_result.status == "invalid"
    assert item.final_result.asset and reference.surface_asset


def test_same_provider_retains_accepted_stages_and_remaps_order_evidence(session, tmp_path):
    bone, provider, receiver, source = source_scene(session, tmp_path)
    original = source.document.object(receiver)
    mappings = {bone: bone, provider: provider}
    candidate = prepared(session, source, [receiver], dict(mappings=mappings))
    result = install(session, candidate)
    copied = session.document.object(candidate.identities[receiver])
    assert copied.stack_plan.providers == (provider,) and copied.final_result.status == "ready"
    jobs = [job for job in session.scheduler.jobs if job.id in result["jobs"]]
    assert all(copied.id not in job.outputs for job in jobs) and not session.scheduler.errors
    assert copied.final_result.revision == original.final_result.revision
    assert all(o.first != receiver and o.second != receiver for o in copied.stack_plan.orders)


def test_changed_provider_recalculates_stack_without_rebuilding_intrinsic(session, tmp_path):
    bone, provider, receiver, source = source_scene(session, tmp_path)
    session.command("tissue.inflation", target=provider, changes=dict(amount=0.05))
    session.wait(30)
    candidate = prepared(
        session, source, [receiver], dict(mappings={bone: bone, provider: provider})
    )
    before = candidate.merge(session.document).object(candidate.identities[receiver])
    assert_stack_pending(before)
    result = install(session, candidate)
    after = session.document.object(before.id)
    assert result["jobs"] and after.final_result.status == "ready", session.scheduler.errors
    assert after.base_result == before.base_result and after.rest_result == before.rest_result
    assert after.intrinsic_result == before.intrinsic_result
    assert after.final_result.asset != before.final_result.asset


def assert_stack_pending(item):
    assert item.intrinsic_result.status == "ready" and item.plan_result.status == "pending"
