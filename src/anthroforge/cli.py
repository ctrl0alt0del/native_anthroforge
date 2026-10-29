"""Headless commands; never import the desktop entry point here."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from anthroforge.application import numerical_worker
from anthroforge.application.projects import adopt
from anthroforge.application.session import Session
from anthroforge.application.storage import read_package
from anthroforge.diagnostics import environment_report


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="anthroforge")
    commands = result.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="Inspect runtime without initializing Qt")
    doctor.add_argument("--require-native", action="store_true")
    new = commands.add_parser("new", help="Describe a new in-memory empty document")
    new.add_argument("--name", default="Untitled")
    authoring_parsers(commands)
    inspection_parser(commands)
    numerical_worker.add_parser(commands)
    return result


def authoring_parsers(commands):
    run = commands.add_parser("run", help="Execute a JSON command file")
    run.add_argument("file")
    run.add_argument("--project")
    commands.add_parser("serve", help="Read JSON operations from stdin; one response per line")
    inspect = commands.add_parser("inspect", help="Read a saved project without a write lock")
    inspect.add_argument("project")
    render = commands.add_parser("render", help="Capture a saved revision without a visible UI")
    render.add_argument("project")
    render.add_argument("output")
    render.add_argument("--revision", required=True, type=int)
    render.add_argument("--view", help="Explicit inspection camera/selection JSON")


def inspection_parser(commands):
    scene = commands.add_parser("render-inspection", help="Render a frozen inspection scene")
    scene.add_argument("bundle")
    scene.add_argument("output")
    report = commands.add_parser("report", help="Export a frozen image/metadata inspection archive")
    report.add_argument("project")
    report.add_argument("output")
    report.add_argument("--revision", required=True, type=int)
    report.add_argument("--selected", default="")
    report.add_argument("--workspace", type=int, default=0)


def execute(args: argparse.Namespace) -> int:
    from anthroforge import authoring

    if args.command == "numerical-worker":
        return numerical_worker.execute(args)
    if args.command == "report":
        return inspection_command(args)
    if args.command in ("run", "serve", "inspect", "render", "render-inspection"):
        return authoring_command(args, authoring)
    if args.command == "new":
        print(json.dumps(Session(args.name).describe(), indent=2))
        return 0
    report = environment_report()
    print(json.dumps(report, indent=2))
    return int(args.require_native and not report["native"]["available"])


def authoring_command(args, authoring):
    if args.command == "render-inspection":
        return inspection_scene_command(args)
    if args.command == "run":
        return authoring.batch(args.file, args.project)
    if args.command == "serve":
        return authoring.serve()
    if args.command == "inspect":
        print(json.dumps(authoring.inspect_project(args.project), indent=2))
        return 0
    from anthroforge.desktop.capture import capture

    return capture(args.project, args.output, args.revision, args.view)


def inspection_scene_command(args):
    from anthroforge.desktop.inspection_capture import capture

    return capture(args.bundle, args.output)


def inspection_command(args):
    session = Session()
    try:
        adopt(session, *read_package(Path(args.project), session.engine))
        if session.document.revision != args.revision:
            raise ValueError("Requested revision does not match the saved document.")
        session.command("workspace.select", index=args.workspace)
        result = session.command(
            "inspection.export", path=args.output, selected=args.selected, wait=True
        )
        print(json.dumps(result))
        return 0
    finally:
        session.close()


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return execute(parser().parse_args(argv))
    except (ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}))
        return 1
