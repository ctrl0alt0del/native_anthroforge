"""Transient list presentation delegates reference qualification to application queries."""

from anthroforge.application import mapping_queries
from anthroforge.core.jobs import ObsoleteInputs


def rows(panel, kind, properties=False, **arguments):
    session = panel.controller.session
    token = "" if getattr(panel, "repair", False) else panel._state.get("token", "")
    reference = arguments.pop("reference", panel.focus)
    if not reference:
        return []
    operation = mapping_queries.property_rows if properties else mapping_queries.target_rows
    try:
        return operation(session, kind, token, reference, **arguments)
    except (ValueError, ObsoleteInputs):
        return []  # Preparation status owns stale/unavailable feedback.
