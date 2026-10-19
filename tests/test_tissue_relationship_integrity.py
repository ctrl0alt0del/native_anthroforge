"""Failed surfaces and copied material identities obey shared relationship contracts."""

from dataclasses import replace

import pytest

from anthroforge.application import attachment_candidates, object_operations, surface_providers
from anthroforge.core.tissue_stacking import StackRelationship
from tests.test_fiber_creation import bind
from tests.test_surface_workflow import curve
from tests.test_tissue_independence import branched_tissue
from tests.test_tissue_stack_workflow import assembly


@pytest.mark.parametrize("status", ["failed", "pending"])
def test_failed_surface_is_skipped_automatically_and_rejected_explicitly(session, status):
    bone, target, _ = assembly(session)
    source = curve(session, 0)
    failed_surface(session, target, status)
    candidates = attachment_candidates.eligible(session.document, source)
    assert all(ref.target != target for ref in candidates)
    with pytest.raises(ValueError, match="Stacking failed"):
        surface_providers.get(session.engine, session.document, session.assets, target)
    assert bind(session, bone, source).result.status == "ready"


def failed_surface(session, target, status):
    session.command("update_mode", entity=target, mode="MANUAL")
    item = session.document.object(target)
    failed = replace(item.final_result, status=status, error="Stacking failed")
    object_operations.install(session, replace(item, final_result=failed))


def test_independence_remaps_self_and_external_selected_region_references(session):
    _, target, branch = branched_tissue(session)
    other = session.command("tissue.create", source=session.document.object(target).source)
    session.wait()
    relations(session, target, other, branch)
    copied = session.command("consumer.make_independent", entity=target)
    session.wait()
    replacement = session.document.object(copied).branches[0].id
    assert replacement != branch
    assert session.document.object(target).stack_relationships[0].regions == ((replacement, 0),)
    assert session.document.object(other).stack_relationships[0].regions == ((replacement, 1),)
    session.command("undo")
    session.wait()
    assert session.document.object(other).stack_relationships[0].regions == ((branch, 1),)


def relations(session, target, other, branch):
    for owner, destination, cover, face in (
        (target, other, "SELF", 0),
        (other, target, "OTHER", 1),
    ):
        item = session.document.object(owner)
        row = StackRelationship(
            destination,
            mode="EXPLICIT",
            cover=cover,
            regions=((branch, face),),
            topology="saved-material",
        )
        object_operations.install(session, replace(item, stack_relationships=(row,)))
