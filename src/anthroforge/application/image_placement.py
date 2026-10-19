"""Image creation and alignment share ordinary parenting and world-axis semantics."""

from typing import TYPE_CHECKING, Any

from anthroforge.native.construction import matrix

from . import curve_sources, object_creation, workspace_policy

if TYPE_CHECKING:
    from .session import Session


def require_context(session: "Session", parent: str, owner: str = "") -> None:
    if session.waiting_save:
        raise ValueError("Editing is blocked while waiting to save.")
    object_creation.require_parent(session, parent)
    if parent and not workspace_policy.included(session.document, session.workspace, parent):
        raise ValueError("The image parent is outside the focused workspace.")
    if owner:
        session.editable(owner)


def create(
    session: "Session", parent: str, owner: str, values: list[float] | None, axis: str
) -> dict[str, Any]:
    require_context(session, parent, owner)
    location = object_creation.placement(session, parent, owner, values)
    if axis:
        location["matrix"] = aligned(session, parent, location["matrix"], axis)
    return location


def aligned(session: "Session", parent: str, frame: Any, axis: str) -> tuple[float, ...]:
    orientations = {"X": (0, 90, 0), "Y": (-90, 0, 0), "Z": (0, 0, 0)}
    if axis not in orientations:
        raise ValueError("Image alignment requires X, Y or Z.")
    parent_frame = curve_sources.world(session.engine, session.document, parent)
    absolute = matrix(session.engine, parent_frame, frame)
    values = list(session.engine.decompose(absolute))
    values[3:6] = orientations[axis]
    return matrix(session.engine, parent_frame, session.engine.transform(values), relative=True)
