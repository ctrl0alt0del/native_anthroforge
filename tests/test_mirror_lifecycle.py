"""Reflection follows accepted source lifetime, without creating derived mesh catalogues."""

from anthroforge.application import surface_providers
from anthroforge.core.surface_references import SurfaceReference
from tests.test_tissue_stack_workflow import assembly


def test_repeated_plane_edits_reuse_source_assets_and_restore_plane_on_undo(session, assembly):
    root, child = assembly
    session.command("mirror.configure", target=root, enabled=True)
    accepted = set(session.assets)
    source = session.document.entity(child)
    for shift in (0.5, 0.8, 1.0, 2.0) * 4:
        session.command("mirror.configure", target=root, shift=shift)
        session.wait()
    assert set(session.assets) == accepted
    assert session.document.entity(child) is source
    session.command("undo")
    session.wait()
    assert session.document.mirrors.rules[root].shift == 1.0


def provider(session, ref):
    return surface_providers.get(session.engine, session.document, session.assets, ref)


def test_manual_tissue_mirror_uses_accepted_result_until_source_explicitly_evaluates(session):
    root, first, _ = assembly(session)
    session.command("mirror.configure", target=root, enabled=True, shift=3)
    session.wait()
    ref = SurfaceReference(first, "TISSUE_FINAL", root)
    accepted = provider(session, ref)
    session.command("update_mode", entity=first, mode="MANUAL")
    session.command("tissue.inflation", target=first, changes=dict(amount=0.05))
    session.wait()
    assert provider(session, ref).resource is accepted.resource
    session.command("evaluate", entities=[first])
    session.wait()
    assert provider(session, ref).resource is provider(session, first).resource
    assert provider(session, ref).asset_id != accepted.asset_id
