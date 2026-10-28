"""New authored support intent round trips without recomputing accepted resources."""

import json
from zipfile import ZipFile

from anthroforge.application import storage
from tests.test_fiber_creation import bind, scene


def write_legacy(source, target, version):
    with ZipFile(source) as original, ZipFile(target, "w") as converted:
        for name in original.namelist():
            data = original.read(name)
            if name == "manifest.json":
                state = json.loads(data)
                state["version"] = version
                for row in state["document"]["objects"]:
                    row["state"].pop("support_policy", None)
                data = json.dumps(state).encode()
            converted.writestr(name, data)


def test_legacy_loading_keeps_accepted_geometry_and_defaults(session, tmp_path):
    target, source = scene(session)
    fiber = bind(session, target, source)
    saved, legacy = tmp_path / "current.anthroforge", tmp_path / "legacy.anthroforge"
    session.command("save", path=str(saved), blocked_policy="wait")
    for version in (4, 5):
        write_legacy(saved, legacy, version)
        session.command("open", path=str(legacy))
        session.wait()
        current = session.document.object(fiber.id)
        assert current.result.asset == fiber.result.asset
        assert current.support_policy.automatic and not current.support_policy.included
        assert not session.scheduler.active_jobs
    assert storage.VERSION == 8 and {4, 5, 6, 7}.issubset(storage.READ_VERSIONS)
