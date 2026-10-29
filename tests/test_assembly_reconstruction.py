import pytest

from tests.test_reconstruction_stages import imported_stage
from tests.test_variants import variant


def prepare(session, source, selected, **options):
    session.command("assembly.inspect", path=str(source))
    session.wait()
    state = session.command("assembly.status")
    session.command("assembly.prepare", source=state["source"], selected=selected, **options)
    session.wait()
    state = session.command("assembly.status")
    assert state["state"] == "ready", state
    return state


def source_records(session, target, tmp_path):
    kind = session.command("catalogue.type.create", name="Bone", aliases=["Reference"])
    session.command("catalogue.assign", target=target, type_id=kind, side="LEFT", label="Example")
    stage = imported_stage(session, target)
    region = session.command("catalogue.region.set", target=target, name="Patch", triangles=[0])
    session.command("catalogue.collection.set", name="Review", members=[target, region])
    record_review(session, target, stage)
    path = tmp_path / "source.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    return path


def record_review(session, target, stage):
    session.command(
        "review.set",
        subject=target,
        dimension="ANATOMY",
        stage=stage,
        decision="APPROVED",
        reviewer="Reviewer",
    )


def test_assembly_copies_catalogue_stages_regions_and_historical_reviews(
    session, assembly, tmp_path
):
    root, child = assembly
    path = source_records(session, child, tmp_path)
    state = prepare(session, path, [root], parent=root)
    result = session.command("assembly.import", token=state["token"])
    session.wait()
    target = result["identities"][child]
    verify_metadata(session, target)
    session.resources.require(session.document)
    session.command("undo")
    assert not any(a.target == target for a in session.document.reconstruction.assignments)


def verify_metadata(session, target):
    metadata = session.document.reconstruction
    assert next(a for a in metadata.assignments if a.target == target).label == "Example"
    assert next(s for s in metadata.stages if s.subject == target).asset in session.assets
    assert next(r for r in metadata.regions if r.target == target).asset in session.assets
    assert (
        session.command("review.inspect", subject=target)["reviews"][0]["freshness"] == "OUTDATED"
    )


def variant_source(session, assembly, tmp_path):
    root, child = assembly
    key = variant(session, child)
    session.command("scp.rename", entity=child, name="Alternative child")
    session.command("variant.leave")
    path = tmp_path / "alternative.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    return root, child, key, path


@pytest.mark.parametrize("include", [False, True])
def test_import_variants_is_explicit_and_keeps_independent_identities(
    session, assembly, tmp_path, include
):
    root, child, key, path = variant_source(session, assembly, tmp_path)
    state = prepare(session, path, [root], parent=root, variants=[key] if include else [])
    assert state["ready"], state
    result = session.command("assembly.import", token=state["token"])
    session.wait()
    alternatives = session.document.reconstruction.variants
    assert len(alternatives) == (2 if include else 1)
    if include:
        imported_variant(session, alternatives[-1], result["identities"][child], key)


def imported_variant(session, row, child, original):
    assert row.id != original and row.subjects == (child,)
    session.command("variant.enter", variant=row.id)
    assert session.document.entity(child).name == "Alternative child"
    session.command("scp.rename", entity=child, name="Imported edit")
    session.command("variant.enter", variant=original)
    assert child not in session.document.registry.records
