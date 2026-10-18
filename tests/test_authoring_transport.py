import json
import subprocess
import sys
from pathlib import Path
from time import sleep

import pytest


@pytest.fixture
def server():
    process = subprocess.Popen(
        [sys.executable, "-m", "anthroforge", "serve"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    yield process
    process.stdin.close()
    process.wait(timeout=10)
    assert process.returncode == 0, process.stderr.read()


def request(server, operation, **arguments):
    server.stdin.write(json.dumps(dict(operation=operation, arguments=arguments)) + "\n")
    server.stdin.flush()
    response = json.loads(server.stdout.readline())
    assert response["ok"], response
    return response["result"]


def test_headless_server_publishes_while_waiting_for_input(server):
    cube = Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj"
    request(server, "import", path=str(cube), units=1)
    sleep(0.2)
    result = request(server, "inspect")
    assert result["entity_count"] == 1 and not result["save_blocked"]
    request(server, "scp.rename", entity=result["entities"][0]["id"], name="Renamed")
    assert request(server, "inspect")["entities"][0]["name"] == "Renamed"


def test_batch_splits_curve_referenced_from_inspection(session):
    from anthroforge.authoring import dispatch

    entity = session.command("primitive.create", kind="BODY")
    results = {"entity": entity, "definition": session.command("primitive.inspect", entity=entity)}
    arguments = dict(
        entity="$entity", curve="$definition.primitive.curves.0.id", segment=0, parameter=0.5
    )
    response = dispatch(session, dict(operation="curve.split", arguments=arguments), results)
    curve = session.document.object(session.document.entity(entity).primitive.curves[0].id)
    assert len(curve.points) == 3 and curve.points[1].id == response["result"]
