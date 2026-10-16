"""Headless commands; never import the desktop entry point here."""

import argparse
import json
from collections.abc import Sequence

from anthroforge.application.session import Session
from anthroforge.diagnostics import environment_report


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="anthroforge")
    commands = result.add_subparsers(dest="command", required=True)
    doctor = commands.add_parser("doctor", help="Inspect runtime without initializing Qt")
    doctor.add_argument("--require-native", action="store_true")
    new = commands.add_parser("new", help="Describe a new in-memory empty document")
    new.add_argument("--name", default="Untitled")
    authoring_parsers(commands)
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


def execute(args: argparse.Namespace) -> int:
    from anthroforge import authoring

    if args.command in ("run", "serve", "inspect", "render"):
        return authoring_command(args, authoring)
    if args.command == "new":
        print(json.dumps(Session(args.name).describe(), indent=2))
        return 0
    report = environment_report()
    print(json.dumps(report, indent=2))
    return int(args.require_native and not report["native"]["available"])


def authoring_command(args, authoring):
    if args.command == "run":
        return authoring.batch(args.file, args.project)
    if args.command == "serve":
        return authoring.serve()
    if args.command == "inspect":
        print(json.dumps(authoring.inspect_project(args.project), indent=2))
        return 0
    from anthroforge.desktop.capture import capture

    return capture(args.project, args.output, args.revision)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        return execute(parser().parse_args(argv))
    except (ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}))
        return 1
