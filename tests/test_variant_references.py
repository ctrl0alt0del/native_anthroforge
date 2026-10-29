from threading import Event

from anthroforge.application import assembly_candidate, assembly_source, storage
from tests.test_assembly_mapping import prepared
from tests.test_assembly_repair import resolve
from tests.test_tissue_workflow import assembly
from tests.test_variants import variant


def unresolved_tissue(session, tmp_path):
    bone, _, tissue = assembly(session)
    path = tmp_path / "tissue.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    source = assembly_source.inspect(str(path), Event())
    candidate = prepared(session, source, [tissue])
    session.begin()
    assembly_candidate.install(session, candidate)
    session.commit()
    session.wait()
    return bone, candidate.identities[tissue]


def test_variant_repairs_its_copied_references_without_changing_original(session, tmp_path):
    bone, tissue = unresolved_tissue(session, tmp_path)
    previous = session.document.external_references
    variant(session, tissue)
    references = [r for r in session.document.external_references if r not in previous]
    assert references and all(
        u.owner in session.document.editing_scope.editable for r in references for u in r.uses
    )
    resolve(session, {r.id: dict(action="map", target=bone) for r in references})
    session.wait()
    assert all(r in session.document.external_references for r in previous)
    session.command("variant.leave")
    assert session.document.external_references == previous
