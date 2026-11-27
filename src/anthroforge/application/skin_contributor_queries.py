"""Effective skin contributor values are shared read-only policy projections."""

from dataclasses import asdict
from typing import Any

from anthroforge.core import skin_budgets
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import geometry_asset
from anthroforge.core.skin_tree import preorder
from anthroforge.core.tissues import TissueVCP

from . import choice_queries, skin_builder_configuration, skin_limb_geometry, skin_operations


def inspect(session: Any, owner: str) -> dict[str, Any]:
    item = session.document.registry.records.get(owner)
    if not isinstance(item, (SCP, TissueVCP, Fiber)):
        return {}
    reason = edit_reason(session, owner)
    return describe(session, item, reason)


def describe(session: Any, item: Any, reason: str) -> dict[str, Any]:
    owner = item.id
    data = dict(
        owner=owner,
        name=item.name,
        scp=isinstance(item, SCP),
        **topology(item, session.document),
        editable=not reason,
        reason=reason,
        surface=bool(geometry_asset(item)),
        revision=choice_queries.revision(session, owner),
        settings=settings(session.document.skin, owner),
    )
    return data | builder_details(session, item)


def builder_details(session: Any, item: Any) -> dict[str, Any]:
    from .skin_builder_registry import BUILDERS

    skin = session.document.skin
    selected = skin.draft_settings.backend
    rows = list(skin.contributors)
    if selected in BUILDERS:
        rows += list(skin_builder_configuration.decode(skin).contributors)
    details = draft(session, item) if isinstance(item, SCP) and selected == "AVBD" else {}
    return dict(draft=details, authored_override=any(r.owner == item.id for r in rows))


def settings(skin: Any, owner: str) -> dict[str, Any]:
    from .skin_builder_registry import BUILDERS

    common = asdict(skin_operations.settings_for(skin, owner))
    if skin.draft_settings.backend in BUILDERS:
        common.update(asdict(skin_builder_configuration.settings_for(skin, owner)))
    return common


def draft(session: Any, item: Any) -> dict[str, Any]:
    doc = session.document
    policy = next(state for owner, state in preorder(doc) if owner == item.id)
    data = dict(
        mode=policy.mode,
        mode_source=doc.object(policy.mode_owner).name if policy.mode_owner else "",
        limb_source=doc.object(policy.limb_owner).name if policy.limb_owner else "",
        child=bool(item.parent),
    )
    return data | auto_dimensions(session, item) if policy.limb_owner == item.id else data


def auto_dimensions(session: Any, item: Any) -> dict[str, Any]:
    try:
        radius = skin_limb_geometry.dimensions(session.engine, item, session.resources.meshes)
        return dict(auto_rest=radius, auto_boundary=0.75 * radius)
    except (ValueError, KeyError) as error:
        return dict(radius_reason=str(error))


def edit_reason(session: Any, target: str) -> str:
    try:
        skin_operations.require_contributor(session, target, {})
        return ""
    except ValueError as error:
        return str(error)


def topology(item: Any, document: Any) -> dict[str, Any]:
    return dict(
        effective=effective(document, item.id),
        fiber=isinstance(item, Fiber),
        flow_available=isinstance(item, Fiber) and not item.closed,
        budget_errors=list(skin_budgets.errors(document)),
        budget=budget_context(document, item.id) if isinstance(item, SCP) else {},
    )


def budget_context(document: Any, owner: str) -> dict[str, Any]:
    rules = skin_budgets.explicit(document)
    ancestor = skin_budgets.parent(document, owner, rules)
    count = (
        rules[ancestor].target_quads if ancestor else document.skin.topology_settings.target_quads
    )
    return dict(
        owner=ancestor,
        name=document.object(ancestor).name if ancestor else "Document",
        target_quads=count,
    )


def effective(document: Any, owner: str) -> dict[str, Any]:
    from .skin_builder_registry import BUILDERS

    if document.skin.draft_settings.backend not in BUILDERS:
        return settings(document.skin, owner)
    common = asdict(skin_operations.settings_for(document.skin, owner))
    return common | asdict(skin_operations.effective_settings(document, owner))
