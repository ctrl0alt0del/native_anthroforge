"""JSON authoring transport; commands invoke the same application API as the UI."""

import json
import sys
from pathlib import Path
from queue import Empty, SimpleQueue
from threading import Thread

from anthroforge.application.session import Session


def resolve(value, results):
    if isinstance(value, str) and value.startswith("$"):
        parts = value[1:].split(".")
        result = results[parts[0]]
        for part in parts[1:]:
            result = result[int(part)] if isinstance(result, (list, tuple)) else result[part]
        return result
    if isinstance(value, dict):
        return {key: resolve(item, results) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve(item, results) for item in value]
    return value


def dispatch(session, request, results):
    session.scheduler.tick()
    arguments = resolve(request.get("arguments", {}), results)
    value = session.command(request["operation"], **arguments)
    if "id" in request:
        results[request["id"]] = value
    return {
        "id": request.get("id"),
        "ok": True,
        "revision": session.document.revision,
        "result": value,
    }


def response(session, request, results):
    try:
        return dispatch(session, request, results)
    except Exception as error:
        return {
            "id": request.get("id"),
            "ok": False,
            "error": str(error),
            "revision": session.document.revision,
        }


def batch(path, project=None):
    requests = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(requests, list):
        raise ValueError("A command file must contain a JSON array of operations.")
    session, results, failed = Session(), {}, False
    try:
        if project:
            session.command("open", path=project)
        for request in requests:
            result = response(session, request, results)
            print(json.dumps(result, allow_nan=False), flush=True)
            failed |= not result["ok"]
        return int(failed)
    finally:
        session.close()


def serve():
    session, results = Session(), {}
    lines = SimpleQueue()
    Thread(target=read_lines, args=(lines,), daemon=True).start()
    try:
        serve_lines(session, results, lines)
    finally:
        session.close()
    return 0


def read_lines(lines):
    for line in sys.stdin:
        lines.put(line)
    lines.put(None)


def serve_lines(session, results, lines):
    while True:
        session.scheduler.tick()
        try:
            line = lines.get(timeout=0.016)
        except Empty:
            continue
        if line is None:
            return
        emit_response(session, results, line)


def emit_response(session, results, line):
    try:
        result = response(session, json.loads(line), results)
    except (ValueError, TypeError) as error:
        result = {"ok": False, "error": str(error)}
    print(json.dumps(result, allow_nan=False), flush=True)


def inspect_project(path):
    from anthroforge.application.projects import adopt
    from anthroforge.application.storage import read_package

    session = Session()
    try:
        adopt(session, *read_package(Path(path), session.engine))
        return session.describe()
    finally:
        session.close()
