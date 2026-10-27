"""Compact skin fixture for background UI inspection; full remeshing is qualified separately."""

from dataclasses import replace
from pathlib import Path

from anthroforge.application import skin_assets
from anthroforge.core.skin import SkinStage


def setup(session):
    source = Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj"
    bone = session.command("import", path=str(source), units=1)["entity_id"]
    session.wait()
    seed_topology(session, bone)
    session.command("skin.reference.build")
    session.wait()
    assert session.document.skin.reference
    reference = dict(target=bone, path=["transform", "position"], component=1)
    return session.command("shortcut.expose", reference=reference, label="Translate Y")


def seed_topology(session, bone):
    data = skin_assets.create({}, {})
    session.resources.skin[data.digest] = data
    stage = SkinStage(asset=session.document.entity(bone).result.asset, data=data.digest)
    settings = replace(session.document.skin.deformation_settings, proxy_resolution=8)
    session.replace_document(
        skin=replace(session.document.skin, topology=stage, deformation_settings=settings)
    )
