"""Explicit read-operation catalogue for shared contextual authoring policies."""

from functools import partial
from typing import Any

from . import mapping_queries, skin_contributor_queries, skin_fit_results, surface_options


def commands(session: Any) -> dict[str, Any]:
    return {
        **mapping_commands(session, "assembly"),
        **mapping_commands(session, "skeleton_update"),
        "surface.options": partial(surface_options.options, session),
        "skin.contributor.inspect": partial(skin_contributor_queries.inspect, session),
        "skin.fit.refit.eligibility": partial(skin_fit_results.refit_eligibility, session),
    }


def mapping_commands(session: Any, kind: str) -> dict[str, Any]:
    return {
        kind + ".mapping.targets": partial(mapping_queries.targets, session, kind),
        kind + ".mapping.properties": partial(mapping_queries.properties, session, kind),
    }
