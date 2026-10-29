"""Topological orchestration over the production dependency graph in owned candidate state."""

from typing import Any

from anthroforge.core.results import Port
from anthroforge.core.skeleton_update import Finding

from . import (
    candidate_batches,
    candidate_formulas,
    candidate_outputs,
    candidate_reuse,
    dependencies,
)


def evaluate(context: Any, seeds: set[Port], restrict: set[str] | None = None) -> set[Port]:
    done: set[Port] = set(context.prepared)
    while True:
        context.check_cancelled()
        graph, pending = remaining(context, seeds, done, restrict)
        if not pending:
            return done
        ready = sorted(candidate_batches.ready(context.document, graph, pending), key=order)
        for port in ready or sorted(pending, key=order):
            failed = dependencies.closure(graph, {port}) & context.failed
            execute(context, port, port in graph.blocked or not ready or bool(failed))
            done.add(port)
            done.update(context.completed_batch)
            break


def remaining(context: Any, seeds: Any, done: Any, restrict: Any) -> Any:
    graph = dependencies.graph(context.document)
    pending = dependencies.closure(dependencies.reverse(graph), seeds) - done
    if restrict is not None:
        pending = {p for p in pending if p.owner in restrict}
    context.pending = pending
    return graph, pending


def order(port: Port) -> tuple[int, str, str]:
    ranks = dict(
        pose=0, control=1, path=2, geometry=3, base=4, rest=5, intrinsic=6, plan=7, final=8
    )
    return ranks.get(port.output, -1), port.owner, port.output


def execute(context: Any, port: Port, blocked: bool) -> None:
    context.completed_batch.clear()
    function = candidate_outputs.handler(context.document, port)
    if function is None:
        return
    try:
        perform(context, port, function, blocked)
    except (ValueError, RuntimeError) as error:
        context.check_cancelled()
        record_failure(context, port, str(error))
    context.prepared.add(port)


def record_failure(context: Any, port: Port, message: str) -> None:
    if port.output == "formula":
        candidate_formulas.failed(context, port, message)
        return
    candidate_outputs.failure(context, port, message)
    context.failed.add(port)
    context.findings.append(failure_finding(context, port, message))


def perform(context: Any, port: Port, function: Any, blocked: bool) -> None:
    if blocked and port.output == "formula":
        candidate_formulas.failed(
            context, port, "A required candidate input failed; accepted values retained."
        )
        return
    if blocked:
        raise ValueError("Cyclic or missing dependency; last accepted output retained.")
    if not candidate_reuse.install(context, port):
        context.call(port, function)


def failure_finding(context: Any, port: Port, message: str) -> Finding:
    key = "failure:" + port.owner + ":" + port.output
    required = port.owner in context.fixed_poses
    return Finding(
        key, port.owner, message, blocking=required, acknowledge=not required, kind="failure"
    )
