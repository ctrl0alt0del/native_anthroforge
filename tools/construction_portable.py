"""Construction workflows using only the relocated executable and its embedded resources."""

import json
from zipfile import ZipFile

import numpy as np
from PIL import Image

KINDS = ("curve", "curve", "fiber", "fiber", "surface", "reference_image")


def construction(executable, cwd, invoke):
    invoke(executable, cwd, "--cli", "run", "examples/construction.json")
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "construction.anthroforge"))
    objects = verify_objects(state)
    image = next(o["state"] for o in objects if o["kind"] == "reference_image")
    embedded_image(executable, cwd, invoke, image)
    jpeg_image(executable, cwd, invoke, image)
    arguments = ("--project", "construction.anthroforge", "--smoke-test", "--screenshot")
    smoke = invoke(executable, cwd, *arguments, str(cwd / "construction-ui.png"))
    assert json.loads(smoke)["desktop_smoke"]


def verify_objects(state):
    objects = state["objects"]
    assert tuple(o["kind"] for o in objects) == KINDS
    assert all(o["state"]["result"]["status"] == "ready" for o in objects)
    source, fiber = objects[0]["state"], objects[2]["state"]
    assert {p["id"] for p in source["points"]}.isdisjoint(p["id"] for p in fiber["points"])
    assert len(fiber["bindings"]) == 2 and fiber["attachment_asset"]
    assert len(objects[4]["state"]["curves"]) == 2
    return objects


def embedded_image(executable, cwd, invoke, image):
    source = cwd / "large-reference.png"
    Image.new("RGB", (2048, 2048), "#e030d0").save(source)
    commands = embedded_commands(image["id"], source)
    (cwd / "embedded.json").write_text(json.dumps(commands))
    invoke(
        executable, cwd, "--cli", "run", "embedded.json", "--project", "construction.anthroforge"
    )
    source.unlink()
    verify_embedded(executable, cwd, invoke, image["id"])


def embedded_commands(target, source):
    appearance = dict(target=target, depth="FRONT", opacity=1, only_axis_aligned=True)
    return [
        request("image.replace", target=target, path=str(source)),
        request("wait"),
        request("image.presentation", **appearance),
        request("save", path="embedded.anthroforge", blocked_policy="wait"),
    ]


def verify_embedded(executable, cwd, invoke, image):
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "embedded.anthroforge"))
    view = dict(workspace=0, selected=image, editing=False)
    view.update(camera=[0, 0, 0, -90, 0, 0, 3], orthographic=True)
    (cwd / "construction-view.json").write_text(json.dumps(view))
    arguments = ("--cli", "render", "embedded.anthroforge", "embedded.png")
    view_arguments = ("--revision", str(state["revision"]), "--view", "construction-view.json")
    invoke(executable, cwd, *arguments, *view_arguments)
    verify_image_pixels(cwd)
    verify_hidden(executable, cwd, invoke, state["revision"], view)


def verify_image_pixels(cwd):
    assert magenta_pixels(cwd / "embedded.png") > 100000, (
        "Embedded image did not completely publish"
    )
    metadata = json.loads((cwd / "embedded.png.json").read_text())
    assert metadata["captured"] and not metadata["window_visible"]
    with ZipFile(cwd / "embedded.anthroforge") as archive:
        assert archive.testzip() is None


def magenta_pixels(path):
    pixels = np.asarray(Image.open(path).convert("RGB"))
    magenta = (pixels[:, :, 0] > 170) & (pixels[:, :, 1] < 100) & (pixels[:, :, 2] > 170)
    return np.count_nonzero(magenta)


def verify_hidden(executable, cwd, invoke, revision, view):
    view = dict(view, camera=[0, 0, 0, -70, 0, 0, 3])
    (cwd / "construction-view.json").write_text(json.dumps(view))
    arguments = ("--cli", "render", "embedded.anthroforge", "hidden.png")
    view_arguments = ("--revision", str(revision), "--view", "construction-view.json")
    invoke(executable, cwd, *arguments, *view_arguments)
    assert magenta_pixels(cwd / "hidden.png") < 100, (
        "Axis-only image remained visible in oblique view"
    )


def request(operation, **arguments):
    return dict(operation=operation, arguments=arguments)


def jpeg_image(executable, cwd, invoke, image):
    source = cwd / "oriented.jpeg"
    value = Image.new("RGB", (80, 40), "#4488aa")
    exif = Image.Exif()
    exif[274] = 6
    value.save(source, exif=exif)
    commands = [request("image.replace", target=image["id"], path=str(source)), request("wait")]
    commands.append(request("image.inspect", target=image["id"]))
    (cwd / "jpeg.json").write_text(json.dumps(commands))
    output = invoke(
        executable, cwd, "--cli", "run", "jpeg.json", "--project", "construction.anthroforge"
    )
    records = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
    assert all(record["ok"] for record in records), records
    assert records[-1]["result"]["dimensions"] == [2, 4]
