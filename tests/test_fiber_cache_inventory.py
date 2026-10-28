"""Fiber solver payload and retained inputs are visible without double-counting meshes."""

from anthroforge.application import fiber_deformation
from anthroforge.profiling.resource_inventory import inventory
from tests.test_fiber_creation import bind, scene


def test_fiber_inventory_distinguishes_owned_preparation_and_shared_field(session):
    target, source = scene(session)
    fiber = bind(session, target, source)
    asset = session.resources.attachments[fiber.attachment_asset]
    prepared, _ = fiber_deformation.prepare(session.engine, session.resources, fiber, asset, 0)
    session.command("profile.start")
    owners = session.profiler.resources.owners()
    assert {prepared, asset.field, asset.field.path, *prepared.meshes} <= owners["cache"]
    evidence = inventory(session.profiler, owners)
    assert evidence["by_kind"]["fiber_preparations"]["unique_bytes"] == prepared.bytes
    assert evidence["complete"]
    assert evidence["by_kind"]["attachments"]["owners"]["document"]["bytes"] >= asset.field.bytes
    session.profiler.close()
