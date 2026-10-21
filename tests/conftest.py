from pathlib import Path

import pytest

from anthroforge.application.session import Session

CUBE = Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj"


@pytest.fixture(autouse=True)
def isolated_preferences(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROFORGE_PREFERENCES_PATH", str(tmp_path / "preferences.json"))


@pytest.fixture
def session():
    value = Session("Fixture")
    yield value
    value.close()


@pytest.fixture
def assembly(session):
    root = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.command("wait")
    child = session.command("import", path=str(CUBE), units=0.2, parent=root)["entity_id"]
    session.command("wait")
    session.command("scp.transform", entity=child, values=[1, 0, 0, 0, 0, 0, 1, 1, 1])
    session.command("wait")
    return root, child
