"""Named numerical evidence; current values never impersonate historical inputs."""

import json
from dataclasses import asdict
from typing import Any

from anthroforge.core.formula_dependencies import property_port
from anthroforge.core.numeric_properties import overlaps
from anthroforge.core.results import Port
from anthroforge.core.shortcuts import Shortcut

from . import dependencies, formula_inputs, property_operations, shortcut_effects
from .dependency_inspection import cycle_records


def retain(session: Any, evaluation: Any, results: Any) -> None:
    for key in evaluation.selected:
        _, formula = evaluation.context.document.formula_index.formulas[key]
        session.shortcut_observation.formulas[key] = dict(
            revision=results[key].revision,
            document_revision=evaluation.context.document.revision,
            **bounded_inputs(evaluation.evidence.get(key, {})),
            expression=formula.expression,
        )


def bounded_inputs(values: Any) -> dict[str, Any]:
    if len(json.dumps(values).encode("utf-8")) > 32768:
        return dict(values={}, omitted="Captured inputs exceed the 32 KiB evidence limit.")
    return dict(values=values, omitted="")


def inspect(session: Any, shortcut: str) -> dict[str, Any]:
    value = shortcut_effects.selected(session, shortcut)
    if isinstance(value, Shortcut):
        matches = [
            d
            for d in session.document.driving_shortcuts
            if any(overlaps(f.target, value.reference) for f in d.formulas)
        ]
    else:
        matches = [value]
    return dict(
        revision=session.document.revision,
        shortcut=shortcut,
        rows=[row(session, d, f) for d in matches for f in d.formulas],
    )


def row(session: Any, driver: Any, formula: Any) -> dict[str, Any]:
    result = session.document.formula_index.results.get(formula.id)
    evidence = retained(session, formula.id, result)
    return dict(
        id=formula.id,
        driver=driver.id,
        target=describe_property(session, formula.target),
        result=asdict(result) if result else None,
        inputs=inputs(session, driver, formula, evidence),
        captured_revision=evidence.get("document_revision"),
        evaluated_expression=evidence.get("expression"),
        evidence_note=evidence.get("omitted", ""),
        **formula_context(session, formula),
    )


def formula_context(session: Any, formula: Any) -> dict[str, Any]:
    return dict(
        expression=formula.expression,
        enabled=formula.enabled,
        dependencies=sorted(formula_inputs.dependencies(session.document, formula)),
        causes=causes(session, formula),
        **cycle_records(session.document, Port(formula.id, "formula")),
    )


def causes(session: Any, formula: Any) -> list[dict[str, Any]]:
    from .dependency_inspection import port_record

    ports = dependencies.ports(session.document, Port(formula.id, "formula"))
    return [
        dict(port_record(session.document, p), **shortcut_effects.readiness(session.document, p))
        for p in sorted(ports, key=lambda p: (p.owner, p.output))
        if p.owner != formula.id and p.output == "formula"
    ]


def retained(session: Any, key: str, result: Any) -> dict[str, Any]:
    evidence = session.shortcut_observation.formulas.get(key, {})
    return dict(evidence) if evidence.get("revision") == getattr(result, "revision", None) else {}


def describe_property(session: Any, reference: Any) -> dict[str, Any]:
    try:
        value = property_operations.get(session, asdict(reference))
        value["object_name"] = session.document.object(reference.target).name
        return dict(value, available=True)
    except (ValueError, KeyError) as error:
        return dict(reference=asdict(reference), available=False, error=str(error))


def inputs(session: Any, driver: Any, formula: Any, evidence: Any) -> list[dict[str, Any]]:
    rows = [driver_input(driver, "value")]
    rows += [input_row(session, i) for i in formula.inputs]
    for value in rows:
        name = value["name"]
        value["captured_available"] = name in evidence.get("values", {})
        value["captured_value"] = evidence.get("values", {}).get(name)
    return rows


def input_row(session: Any, entry: Any) -> dict[str, Any]:
    if entry.property:
        value = describe_property(session, entry.property)
        ports = dependencies.ports(session.document, property_port(entry.property))
        value["source"] = [shortcut_effects.readiness(session.document, p) for p in ports]
        return dict(value, name=entry.name)
    driver = session.document.formula_index.drivers.get(entry.driver)
    if driver is None:
        return dict(name=entry.name, available=False, error="Missing driver", driver=entry.driver)
    return driver_input(driver, entry.name)


def driver_input(driver: Any, name: str) -> dict[str, Any]:
    return dict(
        name=name,
        driver=driver.id,
        label=driver.label,
        value=driver.value,
        numeric_type=driver.numeric_type,
        dimension=driver.dimension,
        available=True,
    )
