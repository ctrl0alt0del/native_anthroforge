"""Private child-process adapters for native libraries without cooperative cancellation."""

from pathlib import Path
from typing import Any

INSTANT_OPTIONS = dict(
    rosy=4,
    posy=4,
    pure_quad=True,
    deterministic=True,
    smooth_iterations=6,
    align_to_boundaries=True,
)


def instant(source: Path, output: Path, count: int) -> None:
    import pyinstantmeshes  # type: ignore[import-untyped]

    if type(count) is not int or not 1 <= count <= 500000:
        raise ValueError("Instant Meshes requires 1–500000 target vertices.")
    pyinstantmeshes.remesh_file(
        str(source), str(output), target_vertex_count=count, **INSTANT_OPTIONS
    )


def execute(args: Any) -> int:
    operations = {"instant": instant}
    operations[args.backend](Path(args.source).resolve(), Path(args.output).resolve(), args.count)
    return 0


def add_parser(commands: Any) -> None:
    parser = commands.add_parser("numerical-worker", help="Internal isolated numerical backend")
    parser.add_argument("backend", choices=("instant",))
    parser.add_argument("source")
    parser.add_argument("output")
    parser.add_argument("count", type=int)
