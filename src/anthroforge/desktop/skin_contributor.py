"""Selection projection uses the shared contributor policy, never a second edit policy."""

from dataclasses import asdict

from anthroforge.application import skin_operations
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import geometry_asset
from anthroforge.core.tissues import TissueVCP


def describe(session, target):
    item = session.document.registry.records.get(target)
    if not isinstance(item, (SCP, TissueVCP, Fiber)):
        return {}
    reason = edit_reason(session, target)
    return dict(
        owner=target,
        name=item.name,
        scp=isinstance(item, SCP),
        fiber=isinstance(item, Fiber),
        editable=not reason,
        reason=reason,
        surface=bool(geometry_asset(item)),
        settings=asdict(skin_operations.settings_for(session.document.skin, target)),
    )


def edit_reason(session, target):
    try:
        skin_operations.require_contributor(session, target, {})
        return ""
    except ValueError as error:
        return str(error)
