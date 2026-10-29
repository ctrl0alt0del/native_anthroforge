"""Shared assembly commands; a prepared graph is committed through the normal edit contract."""

from dataclasses import asdict
from typing import Any

from . import assembly_candidate


def apply(session: Any, token: str) -> dict[str, Any]:
    from .issues.assembly import finding

    candidate = session.assembly.ready(token)
    require_scope(session, candidate)
    result = assembly_candidate.install(session, candidate)
    result["issues"] = [asdict(finding(r)) for r in candidate.references if not r.target]
    session.assembly.cancel()
    return result


def require_scope(session: Any, candidate: Any) -> None:
    if session._editing.key and isinstance(candidate, assembly_candidate.Candidate):
        raise ValueError(
            "Import project anatomy into accepted anatomy, then create a variant of it."
        )
    if session._editing.key:
        from .variant_policy import require

        for row in candidate.references:
            for use in row.uses:
                require(session, use.owner)


def commands(session: Any) -> dict[str, Any]:
    return {
        "assembly.inspect": session.assembly.inspect,
        "assembly.prepare": session.assembly.prepare,
        "assembly.status": session.assembly.status,
        "assembly.cancel": session.assembly.cancel,
        "assembly.references": lambda: [asdict(r) for r in session.document.external_references],
        "assembly.resolve": session.assembly.resolve,
    }
