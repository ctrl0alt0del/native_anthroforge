"""Exact surface-role identities and readiness shared by every client."""

from typing import Any

from anthroforge.core import anatomical_surfaces
from anthroforge.core.mirroring import MirrorInstance
from anthroforge.core.results import geometry_asset

from . import choice_queries, surface_providers


def rows(session: Any) -> list[dict[str, Any]]:
    document = session.document
    return [row(document, ref) for ref in surface_providers.references(document)]


def row(document: Any, ref: Any) -> dict[str, Any]:
    item = document.object(ref.target)
    result = anatomical_surfaces.result(item, ref.role)
    label = {"SCP_GEOMETRY": "Surface", "TISSUE_BASE": "Base", "TISSUE_FINAL": "Final"}[ref.role]
    available = bool(geometry_asset(item) if ref.role == "SCP_GEOMETRY" else result.asset)
    identity = MirrorInstance(ref.target, ref.instance).id if ref.instance else ref.target
    return dict(
        id=identity,
        role=ref.role,
        key=identity + ":" + ref.role,
        name=item.name + (" · mirrored" if ref.instance else "") + " · " + label,
        ready=available and result.status not in ("failed", "invalid", "cancelled"),
        status=result.status,
        reason=result.error,
    )


def options(session: Any, **paging: Any) -> dict[str, Any]:
    return choice_queries.project(session, rows(session), "surfaces", **paging)
