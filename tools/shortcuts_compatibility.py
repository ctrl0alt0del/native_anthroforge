"""Qualify schema-4 compatibility with a real 0.2.4 executable and project copy."""

import hashlib
import json
import shutil
import subprocess
import sys
from contextlib import closing
from pathlib import Path
from zipfile import ZipFile

from anthroforge.application import storage
from anthroforge.application.session import Session


def manifest(path):
    with ZipFile(path) as archive:
        return json.loads(archive.read("manifest.json"))


def invoke(command, project, requests, output):
    script = output.with_suffix(".json")
    script.write_text(json.dumps(requests), encoding="utf-8")
    result = subprocess.run(
        [*command, "run", str(script), "--project", str(project)],
        capture_output=True,
        text=True,
        timeout=300,
    )
    output.with_suffix(".log").write_text(result.stdout + result.stderr, encoding="utf-8")
    assert result.returncode == 0, result.stdout + result.stderr
    rows = [json.loads(row) for row in result.stdout.splitlines() if row.startswith("{")]
    assert rows and all(row["ok"] for row in rows), rows


def save(path):
    return dict(operation="save", arguments=dict(path=str(path), blocked_policy="wait"))


def resource_hashes(path):
    with ZipFile(path) as archive:
        return {
            name: hashlib.sha256(archive.read(name)).hexdigest()
            for name in archive.namelist()
            if name != "manifest.json"
        }


def unchanged(baseline, output):
    with closing(Session()) as session:
        before, _ = storage.read_package(baseline, session.engine)
        session.command("open", path=str(baseline))
        session.wait(60)
        assert session.document == before, "Opening changed authored or accepted records"
        assert not session.document.shortcuts and not session.document.driving_shortcuts
        session.command("save", path=str(output), blocked_policy="wait")
    assert resource_hashes(baseline) == resource_hashes(output)
    assert manifest(output)["version"] == 5


def edit(baseline, entity):
    with closing(Session()) as session:
        document, _ = storage.read_package(baseline, session.engine)
        values = session.engine.decompose(document.entity(entity).matrix)
    values[0] += 0.003
    return dict(operation="scp.transform", arguments=dict(entity=entity, values=values))


def resource_ids(path):
    groups = {}
    for name, digest in resource_hashes(path).items():
        parts = name.split("/")
        key = parts[1].removesuffix(".npy")
        groups.setdefault(key, []).append(("/".join(parts[2:]), digest))
    return {
        key: hashlib.sha256(json.dumps(sorted(rows)).encode()).hexdigest()
        for key, rows in groups.items()
    }


def canonical(value, resources):
    if isinstance(value, str):
        return resources.get(value, value)
    if isinstance(value, list):
        return [canonical(v, resources) for v in value]
    if isinstance(value, dict):
        return {key: canonical(v, resources) for key, v in value.items()}
    return value


def compare_edits(before, after):
    with closing(Session()) as session:
        first, _ = storage.read_package(before, session.engine)
        second, _ = storage.read_package(after, session.engine)
        a = canonical(storage.document_state(first), resource_ids(before))
        b = canonical(storage.document_state(second), resource_ids(after))
    assert a == b, "Old/new edited document state differs after resource-ID normalization"


def continued_edit(old, baseline, output, entity):
    first, second = output / "old-edit.anthroforge", output / "new-edit.anthroforge"
    invoke(old, baseline, [edit(baseline, entity), save(first)], first)
    invoke(
        [sys.executable, "-m", "anthroforge"],
        baseline,
        [edit(baseline, entity), save(second)],
        second,
    )
    compare_edits(first, second)


def run(source, executable, output, entity):
    output.mkdir(parents=True, exist_ok=True)
    copied, baseline = output / "input.anthroforge", output / "baseline.anthroforge"
    shutil.copyfile(source, copied)
    old = [str(executable), "--cli"]
    invoke(old, copied, [save(baseline)], baseline)
    assert manifest(baseline)["version"] == 4
    unchanged(baseline, output / "schema5.anthroforge")
    continued_edit(old, baseline, output, entity)
    print("Schema-4 read/schema-5 save retains all records and buffers; continued edits agree.")


if __name__ == "__main__":
    run(*(Path(arg) for arg in sys.argv[1:4]), sys.argv[4])
