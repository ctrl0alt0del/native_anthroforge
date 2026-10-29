"""Effective skin contributor values are shared read-only policy projections."""

from dataclasses import asdict
from typing import Any

from anthroforge.core import skin_budgets
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import geometry_asset
from anthroforge.core.tissues import TissueVCP

from . import choice_queries, skin_operations


def inspect(session: Any, owner: str) -> dict[str, Any]:
    item = session.document.registry.records.get(owner)
    if not isinstance(item, (SCP, TissueVCP, Fiber)):
        return {}
    reason = edit_reason(session, owner)
    return describe(session, item, reason)


def describe(session: Any, item: Any, reason: str) -> dict[str, Any]:
    owner = item.id
    return dict(
        owner=owner,
        name=item.name,
        scp=isinstance(item, SCP),
        **topology(item, session.document),
        editable=not reason,
        reason=reason,
        surface=bool(geometry_asset(item)),
        revision=choice_queries.revision(session, owner),
        settings=asdict(skin_operations.settings_for(session.document.skin, owner)),
        authored_override=any(r.owner == owner for r in session.document.skin.contributors),
    )


def edit_reason(session: Any, target: str) -> str:
    try:
        skin_operations.require_contributor(session, target, {})
        return ""
    except ValueError as error:
        return str(error)


def topology(item: Any, document: Any) -> dict[str, Any]:
    return dict(
        effective=asdict(skin_operations.effective_settings(document, item.id)),
        fiber=isinstance(item, Fiber),
        flow_available=isinstance(item, Fiber) and not item.closed,
        budget_errors=list(skin_budgets.errors(document)),
    )
