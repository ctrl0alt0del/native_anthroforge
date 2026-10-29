import pytest

from tests.test_variants import rename_bone, variant


def review(session, key, **options):
    session.command("variant.review.prepare", variant=key, **options)
    result = session.command("variant.review.status", wait=True)
    assert result["state"] == "ready", result
    return result


def apply(session, result):
    approved = [f["key"] for f in result["findings"] if f["acknowledge"]]
    return session.command("variant.review.apply", token=result["token"], approved=approved)


def test_promotion_is_one_undo_and_keeps_previous_accepted_checkpoint(session, assembly):
    _, child = assembly
    before = session.document
    key = variant(session, child)
    rename_bone(session, child, "Alternative")
    session.command("variant.leave")
    cursor = session.history.cursor
    result = apply(session, review(session, key))
    assert session.document.entity(child).name == "Alternative"
    assert session.history.cursor == cursor + 1
    checkpoint_matches(session, result["checkpoint"], before, child)
    session.command("undo")
    assert session.document.entities == before.entities


def checkpoint_matches(session, key, before, child):
    checkpoint = session.document.reconstruction.variant(key)
    assert session.document.reconstruction.snapshot(checkpoint.current).entity(
        child
    ) == before.entity(child)


def test_shared_tissue_sources_copy_once_and_promote_without_touching_other_consumer(session):
    from tests.test_tissue_workflow import assembly

    _, source, tissue = assembly(session)
    other = session.command("tissue.create", source=source)
    session.wait()
    original = session.document
    key = variant(session, tissue)
    assert session.document.object(tissue).source != source
    session.command("tissue.inflation", target=tissue, changes=dict(amount=0.08))
    session.wait()
    session.command("variant.leave")
    apply(session, review(session, key))
    assert session.document.object(other).source == source
    assert session.document.object(source) == original.object(source)


def test_refresh_preserves_variant_edits_and_moves_fibers_with_accepted_support(session):
    from tests.test_tissue_workflow import assembly, mesh

    bone, _, tissue = assembly(session)
    key = variant(session, tissue)
    session.command("tissue.inflation", target=tissue, changes=dict(amount=0.08))
    session.wait()
    before = mesh(session, tissue)
    session.command("variant.leave")
    session.command("scp.transform", entity=bone, values=[0, 0, 0.3, 0, 0, 0, 1, 1, 1])
    session.wait()
    apply(session, review(session, key, mode="refresh"))
    session.command("variant.enter", variant=key)
    assert_shift(mesh(session, tissue), before)


def assert_shift(after, before):
    import numpy as np

    np.testing.assert_allclose(after, before + [0, 0, 0.3], atol=1e-8)


def test_accepted_conflict_requires_explicit_choice(session, assembly):
    _, child = assembly
    key = variant(session, child)
    rename_bone(session, child, "Alternative")
    session.command("variant.leave")
    rename_bone(session, child, "Accepted edit")
    result = review(session, key)
    assert any(f["kind"] == "conflict" for f in result["findings"])
    with pytest.raises(ValueError, match="Resolve"):
        apply(session, result)
    apply(session, review(session, key, choices={child: "VARIANT"}))
    assert session.document.entity(child).name == "Alternative"


def test_variant_edit_after_preparation_rejects_stale_promotion(session, assembly):
    _, child = assembly
    key = variant(session, child)
    result = review(session, key)
    rename_bone(session, child, "Changed since preparation")
    assert session.command("variant.review.status")["state"] == "stale"
    with pytest.raises(ValueError):
        apply(session, result)
