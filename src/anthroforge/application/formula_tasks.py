"""Formula calculations share coordinator reservations, cancellation and save checkpoints."""

from dataclasses import replace
from functools import partial
from typing import Any

from anthroforge.core.formula_dependencies import property_port
from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.core.shortcuts import FormulaResult
from anthroforge.native.mesh import NativeCancellation

from . import dependencies, formula_evaluation, formula_inputs, formula_observation, property_guards
from .construction_policy import mode, revisions


def selected(session: Any, targets: set[str], explicit: bool, released: bool) -> set[str]:
    records = formula_inputs.formulas(session.document)
    pending_ids = {r.formula for r in session.document.formula_results if r.status == "pending"}
    return {
        key
        for key, (driver, formula) in records.items()
        if (not targets or {key, driver.id, formula.target.target} & targets)
        and (explicit or key in pending_ids)
        and (
            explicit
            or mode(session.document, formula.target.target) == "LIVE"
            or released
            and mode(session.document, formula.target.target) == "ON_RELEASE"
        )
    }


def schedule(
    session: Any, targets: set[str], explicit: bool = False, released: bool = False
) -> list[str]:
    ids = selected(session, targets, explicit, released)
    if explicit:
        ids |= {
            p.owner
            for p in formula_inputs.observations(session.document, ids)
            if p.output == "formula"
        }
    return [request(session, ids)] if ids else []


def request(session: Any, ids: set[str]) -> str:
    records = formula_inputs.formulas(session.document)
    ids &= records.keys()
    targets = {records[key][1].target.target for key in ids}
    job = make_job(session, ids, targets)
    job.cancel = NativeCancellation(session.engine)
    job.interactive, job.priority = session.history.before is not None, session.priority(targets)
    job.publish_during_edit = job.restart_on_redo = job.restart_on_input_change = True
    job.retry = partial(request, session, ids)
    job.workload = partial(workload, ids)
    job.inputs_key = partial(key, ids=ids)
    job.renew_inputs = partial(contract, ids=ids)
    contract(job, session.document, ids)
    return str(session.scheduler.submit(job))


def make_job(session: Any, ids: set[str], targets: set[str]) -> Job:
    return Job(
        "Evaluate driving shortcuts",
        frozenset(targets | ids),
        lambda document: formula_inputs.Captured(
            document, session.resources.snapshot(), session.engine
        ),
        lambda context, cancel: formula_evaluation.evaluate(context, ids, cancel),
        partial(publish, session),
        key="driving-formulas",
        kind="formulas",
    )


def key(document: Any, ids: set[str]) -> Any:
    return dependencies.graph(document), frozenset(ids & formula_inputs.formulas(document).keys())


def contract(job: Job, document: Any, ids: set[str]) -> None:
    records, graph = formula_inputs.formulas(document), dependencies.graph(document)
    outputs = {Port(value, "formula") for value in ids if value in records}
    outputs |= {property_port(records[value][1].target) for value in ids if value in records}
    observations = formula_inputs.observations(document, ids)
    valid = {p for p in outputs if p not in graph.blocked}
    job.provides, job.observes = frozenset(outputs), frozenset(observations - outputs)
    job.prerequisites = frozenset(dependencies.closure(graph, valid) - outputs)
    job.reads = frozenset(p.owner for p in observations)
    job.accepted_inputs_key = key(document, ids)


def workload(ids: set[str], document: Any) -> Workload:
    records = formula_inputs.formulas(document)
    return Workload(
        affected=len(ids),
        candidates=sum(len(records[key][1].expression) for key in ids if key in records),
    )


def publish(session: Any, evaluation: Any) -> None:
    from .property_writes import install

    document, ids = evaluation.context.document, evaluation.selected
    observations = formula_inputs.observations(document, ids)
    if revisions(document, observations) != revisions(session.document, observations):
        raise ObsoleteInputs()
    with property_guards.publication(session, ids):
        for before, after in evaluation.candidates:
            install(session, before, after)
        install_results(session, evaluation)
    formula_observation.changed(session, document, frozenset(ids))
    from .output_tasks import propagate

    propagate(session, {Port(key, "formula") for key in ids})


def install_results(session: Any, evaluation: Any) -> None:
    records = {r.formula: r for r in session.document.formula_results}
    for key in evaluation.selected:
        old = records.get(key, FormulaResult(key))
        records[key] = accepted_result(evaluation, key, old)
    session.replace_document(formula_results=tuple(records.values()))


def accepted_result(evaluation: Any, key: str, old: FormulaResult) -> FormulaResult:
    document, error = evaluation.context.document, evaluation.failures.get(key, "")
    inputs = dependencies.ports(document, Port(key, "formula")) - {Port(key, "formula")}
    return replace(
        old,
        value=evaluation.values.get(key, old.value),
        revision=old.revision + 1,
        status="failed" if error else "ready",
        error=error,
        inputs=revisions(document, inputs),
        pending=formula_observation.pending_upstream(document, key, evaluation.selected),
    )


def pending(session: Any, released: bool = False) -> None:
    schedule(session, set(), released=released)


def edited(session: Any, seeds: set[Port]) -> None:
    # Source comparison in Session owns authored invalidation; accepted publication uses propagate.
    pass
