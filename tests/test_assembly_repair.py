from anthroforge.application import assembly_candidate, storage
from tests.test_assembly_mapping import captured, prepared


def missing_import(session, tmp_path):
    target, fiber, source = captured(session, tmp_path)
    candidate = prepared(session, source, [fiber.id])
    session.begin()
    assembly_candidate.install(session, candidate)
    session.commit()
    Path(source.original).unlink()
    key = candidate.identities[fiber.id]
    return target, key


def test_repair_without_source_file_is_atomic_and_preserves_original(session, tmp_path):
    target, key = missing_import(session, tmp_path)
    before = session.document.object(key)
    refs = session.command("assembly.references")
    mappings = {r["id"]: dict(action="map", target=target) for r in refs if not r["target"]}
    result = session.command("assembly.resolve", mappings=mappings)
    session.wait()
    status = session.command("assembly.status")
    assert status["state"] == "ready", status
    assert status["ready"], status
    session.command("assembly.import", token=result["token"])
    session.wait()
    assert session.document.object(key).bindings[0].target == target
    session.command("undo")
    assert session.document.object(key) == before


def test_pending_surface_evidence_round_trips_without_source(session, tmp_path):
    _, key = missing_import(session, tmp_path)
    path = tmp_path / "destination.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    loaded, resources = storage.read_package(path, session.engine)
    assert loaded.object(key).result.asset
    assert loaded.external_references
    resources.require(loaded)


from pathlib import Path
