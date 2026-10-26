"""Skin contribution is anatomical, not controlled by the active viewport."""

from dataclasses import replace

from anthroforge.core import skin_sources
from tests.test_tissue_workflow import assembly


def test_valid_tissue_suppresses_its_fibers_once_and_excludes_construction(session):
    bone, membrane, tissue = assembly(session)
    document = session.document
    sources = skin_sources.selected(document, skin_sources.accepted_tissues(document))
    assert {(source.owner, source.kind) for source in sources} == {
        (bone, "SCP"),
        (tissue, "TISSUE"),
    }
    assert membrane not in {source.owner for source in sources}
    workspace = replace(document.workspaces[0], members=(tissue,), hidden=(bone,))
    hidden = replace(document, workspaces=(workspace,))
    assert skin_sources.candidates(hidden) == skin_sources.candidates(document)


def test_failed_tissue_does_not_suppress_source_fibers(session):
    _bone, membrane, tissue = assembly(session)
    item = session.document.object(tissue)
    failed = replace(
        item, final_result=replace(item.final_result, status="failed", error="fixture")
    )
    document = replace(
        session.document,
        objects=tuple(failed if o.id == tissue else o for o in session.document.objects),
    )
    sources = skin_sources.selected(document, skin_sources.accepted_tissues(document))
    fiber_ids = {use.curve for use in document.object(membrane).curves}
    assert {source.owner for source in sources if source.kind == "FIBER"} == fiber_ids


def test_mirror_sources_are_distinct_without_duplicating_the_original(session):
    bone, _membrane, tissue = assembly(session)
    session.command("mirror.configure", target=bone, enabled=True)
    session.wait()
    document = session.document
    sources = skin_sources.selected(document, skin_sources.accepted_tissues(document))
    assert len(sources) == len(set(sources))
    assert sum(source.owner == tissue and not source.instance for source in sources) == 1
    assert all(source.kind != "FIBER" for source in sources)
