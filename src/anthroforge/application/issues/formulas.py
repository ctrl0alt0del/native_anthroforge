"""Advisory formula failures retain accepted data and identify the actual target."""

from dataclasses import asdict
from threading import Event
from typing import Any

from anthroforge.core.issues import Issue, evidence, fingerprint

from ..formula_inputs import formulas
from .providers import Provider


def source(document: Any, scope: str) -> Any:
    return tuple(asdict(r) for r in document.formula_results)


def check(document: Any, scope: str, cancel: Event) -> tuple[Issue, ...]:
    records, rows = formulas(document), []
    for result in document.formula_results:
        if cancel.is_set():
            break
        if result.formula in records and (result.status == "failed" or result.pending):
            rows.append(finding(records[result.formula], result))
    return tuple(rows)


def finding(record: Any, result: Any) -> Issue:
    driver, formula = record
    return Issue(
        "formulas.v1",
        "document",
        **labels(driver, result),
        target=formula.target.target,
        kind="FORMULA",
        stage="formula",
        source=fingerprint(asdict(result)),
        local_key=formula.id,
        evidence=formula_evidence(driver, formula, result),
    )


def labels(driver: Any, result: Any) -> dict[str, Any]:
    failed = result.status == "failed"
    return dict(
        code="FORMULA_FAILED" if failed else "FORMULA_PENDING_INPUT",
        summary=driver.label + (": formula failed" if failed else ": uses accepted pending input"),
        details=result.error
        or "A prerequisite has unpublished edits; its last accepted value was used.",
    )


def formula_evidence(driver: Any, formula: Any, result: Any) -> str:
    return evidence(
        driver=driver.id, formula=formula.id, target=asdict(formula.target), result=asdict(result)
    )


def provider() -> Provider:
    return Provider(
        "formulas.v1",
        lambda _: {"document"},
        lambda d, c: (
            {"document"} if c.document & {"formula_results", "driving_shortcuts"} else set()
        ),
        source,
        check,
    )
