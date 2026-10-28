"""Independent cross-project construction using only a relocated executable."""

import hashlib
import json
from zipfile import ZipFile


def assembly(executable, cwd, invoke):
    source = cwd / "construction.anthroforge"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", str(source)))
    selected = [
        v["state"]["id"] for v in state["objects"] if v["kind"] in ("curve", "reference_image")
    ]
    requests = commands(str(source), selected)
    script = cwd / "assembly-import.json"
    script.write_text(json.dumps(requests), "utf-8")
    output = invoke(executable, cwd, "--cli", "run", str(script))
    assert all(json.loads(line)["ok"] for line in output.splitlines()), output
    verify(cwd, selected)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    render(executable, cwd, invoke)


def request(operation, identity=None, **arguments):
    return dict(operation=operation, arguments=arguments, **(dict(id=identity) if identity else {}))


def commands(source, selected):
    return [
        request("assembly.inspect", "source", path=source),
        request("wait"),
        request("assembly.prepare", "prepared", source="$source.source", selected=selected),
        request("wait"),
        request("assembly.import", "imported", token="$prepared.token"),
        request("undo"),
        request("redo"),
        request("save", path="assembled.anthroforge", blocked_policy="wait"),
    ]


def verify(cwd, selected):
    with ZipFile(cwd / "assembled.anthroforge") as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["version"] == 8
        document = manifest["document"]
        assert not document["entities"] and len(document["objects"]) == len(selected)
        copied = {v["state"]["id"] for v in document["objects"]}
        assert copied.isdisjoint(selected) and document["imports"]
        assert not document["external_references"]
        assert len(manifest["images"]) == 1 and not document["skin"]["final"]["asset"]


def render(executable, cwd, invoke):
    result = invoke(executable, cwd, "--cli", "inspect", "assembled.anthroforge")
    state = json.loads(result)
    invoke(
        executable,
        cwd,
        "--cli",
        "render",
        "assembled.anthroforge",
        "assembled.png",
        "--revision",
        str(state["revision"]),
    )
    capture = json.loads((cwd / "assembled.png.json").read_text())
    assert capture["captured"] and not capture["window_visible"]
