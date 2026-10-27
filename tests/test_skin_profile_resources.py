"""Profiler includes owned skin preparations and independent preview geometry."""

from anthroforge.native import skin_deformation
from anthroforge.profiling.resource_inventory import inventory
from tests.test_profile_diagnostics import report
from tests.test_skin_fit_jobs import fit, setup


def test_skin_preparation_and_preview_have_distinct_owners(session, tmp_path):
    item = fit(session, setup(session))
    session.command("profile.start", memory_mib=16)
    check_preparation(session)
    session.command("skin.fit.preview", identity=item.id, value=0.1)
    session.wait()
    owners = session.profiler.resources.owners()
    mesh = session.skin_fit_preview.asset.mesh
    assert mesh in owners["skin_fit_preview"] and mesh not in owners["document"]
    session.command("skin.fit.preview.cancel")
    assert mesh not in session.profiler.resources.owners()["skin_fit_preview"]
    report(session, tmp_path / "skin-memory.zip")


def check_preparation(session):
    ref = session.resources.skin[session.document.skin.reference]
    value = skin_deformation.cached(
        session.engine, ref.digest, ref.arrays, session.document.skin.deformation_settings
    )
    owners = session.profiler.resources.owners()
    assert value in owners["cache"]
    evidence = inventory(session.profiler, owners)["by_kind"]["skin_preparations"]
    assert evidence["unique_bytes"] >= value.bytes > 0
    assert evidence["owners"]["cache"]["bytes"] >= value.bytes
