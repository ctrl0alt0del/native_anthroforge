"""Explicit application composition shared by root and variant editing contexts."""

from typing import Any

from . import preparation_lifecycle, preview_lifecycle, shortcut_lifecycle
from .issues import lifecycle as issue_lifecycle
from .service_lifecycle import Lifecycle
from .skin_status import attach as attach_skin_status


def attach(session: Any) -> None:
    session.services = Lifecycle()
    for factory in (
        preparation_lifecycle.attach,
        issue_lifecycle.attach,
        shortcut_lifecycle.attach,
        attach_skin_status,
        preview_lifecycle.attach,
    ):
        session.services.register(factory(session))
