"""Topological orchestration over the production dependency graph in owned candidate state."""

from typing import Any

from anthroforge.core.results import Port
from anthroforge.core.skeleton_update import Finding

from . import candidate_outputs, dependencies


def evaluate(context: Any, seeds: set[Port], restrict: set[str] | None = None) -> set[Port]:
    done: set[Port] = set()
    while True:
        context.check_cancelled()
        graph, pending = remaining(context, seeds, done, restrict)
        if not pending:
            return done
        ready = sorted((p for p in pending if not (graph.get(p, set()) & pending)), key=order)
        for port in ready or sorted(pending, key=order):
            execute(context, port, port in graph.blocked or not ready)
            done.add(port)
            break


def remaining(context: Any, seeds: Any, done: Any, restrict: Any) -> Any:
    graph = dependencies.graph(context.document)
    pending = dependencies.closure(dependencies.reverse(graph), seeds) - done
    if restrict is not None:
        pending = {p for p in pending if p.owner in restrict}
    return graph, pending


def order(port: Port) -> tuple[int, str, str]:
    ranks = dict(
        pose=0, control=1, path=2, geometry=3, base=4, rest=5, intrinsic=6, plan=7, final=8
    )
    return ranks.get(port.output, -1), port.owner, port.output


def execute(context: Any, port: Port, blocked: bool) -> None:
    function = candidate_outputs.handler(context.document, port)
    if function is None:
        return
    try:
        if blocked:
            raise ValueError("Cyclic or missing dependency; last accepted output retained.")
        context.call(port, function)
    except (ValueError, RuntimeError) as error:
        context.check_cancelled()
        candidate_outputs.failure(context, port, str(error))
        context.findings.append(failure_finding(context, port, str(error)))
    context.prepared.add(port)


def failure_finding(context: Any, port: Port, message: str) -> Finding:
    key = "failure:" + port.owner + ":" + port.output
    required = port.owner in context.fixed_poses
    return Finding(
        key, port.owner, message, blocking=required, acknowledge=not required, kind="failure"
    )
