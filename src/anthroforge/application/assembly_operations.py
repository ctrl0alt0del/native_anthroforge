"""Shared assembly commands; a prepared graph is committed through the normal edit contract."""

from dataclasses import asdict
from typing import Any

from . import assembly_candidate


def apply(session: Any, token: str) -> dict[str, Any]:
    candidate = session.assembly.ready(token)
    result = assembly_candidate.install(session, candidate)
    session.assembly.cancel()
    return result


def commands(session: Any) -> dict[str, Any]:
    return {
        "assembly.inspect": session.assembly.inspect,
        "assembly.prepare": session.assembly.prepare,
        "assembly.status": session.assembly.status,
        "assembly.cancel": session.assembly.cancel,
        "assembly.references": lambda: [asdict(r) for r in session.document.external_references],
        "assembly.resolve": session.assembly.resolve,
    }
