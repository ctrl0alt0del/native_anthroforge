"""Skin operation declarations; common execution lives in command_execution."""

from functools import partial

from .. import (
    skin_collagen,
    skin_contributor_queries,
    skin_export,
    skin_fit_capture,
    skin_fit_jobs,
    skin_fit_preview,
    skin_fit_results,
    skin_jobs,
    skin_operations,
    skin_painting,
    skin_update_tasks,
    tissue_inspection,
)
from ..command_contracts import direct, edit, method, query

COMMANDS = (
    edit("skin.collagen.paint.commit", skin_painting.commit, isolated=True, project_scope=True),
    edit("skin.collagen.set", skin_collagen.set_weights, project_scope=True),
    edit("skin.collagen.fill", skin_collagen.fill, project_scope=True),
    edit("skin.collagen.clear", skin_collagen.clear, project_scope=True),
    edit("skin.envelope.build", partial(skin_jobs.build, stage="envelope"), project_scope=True),
    edit("skin.topology.build", partial(skin_jobs.build, stage="topology"), project_scope=True),
    edit("skin.reference.build", partial(skin_jobs.build, stage="reference"), project_scope=True),
    edit("skin.evaluate", skin_update_tasks.evaluate, project_scope=True),
    edit("skin.fit", skin_fit_jobs.start, project_scope=True),
    edit("skin.fit.authoring", partial(skin_fit_jobs.start, authoring=True), project_scope=True),
    edit("skin.fit.remove", skin_fit_results.remove, project_scope=True),
    edit("skin.build", skin_jobs.build, project_scope=True),
    edit("skin.configure", skin_operations.configure, project_scope=True),
    edit("skin.envelope.reset", skin_operations.reset_envelope, project_scope=True),
    edit("skin.contributor.configure", skin_operations.contributor, project_scope=True),
    direct("skin.inspect", lambda session: skin_operations.inspect(session)),
    direct("skin.report", lambda session: skin_operations.report(session)),
    direct("skin.status", method("skin_status.describe")),
    direct("skin.export", lambda session, **a: skin_export.export(session, **a)),
    direct("skin.fit.inspect", lambda session, **a: skin_fit_results.inspect(session, **a)),
    direct("skin.fit.eligibility", lambda session, **a: skin_fit_capture.describe(session, **a)),
    direct("skin.fit.preview", lambda session, **a: skin_fit_preview.request(session, **a)),
    direct("skin.fit.preview.status", lambda session: skin_fit_preview.status(session)),
    direct("skin.fit.preview.cancel", lambda session: skin_fit_preview.cancel(session)),
    direct("skin.contributor.inspect", skin_contributor_queries.inspect),
    direct("skin.fit.refit.eligibility", skin_fit_results.refit_eligibility),
    query(
        "skin.inspect.paint",
        lambda session, **arguments: tissue_inspection.start(session, "collagen", **arguments),
    ),
    query(
        "skin.inspect.status",
        lambda session, **arguments: tissue_inspection.status(session, "collagen", **arguments),
    ),
    query(
        "skin.inspect.cancel",
        lambda session, **arguments: tissue_inspection.cancel(session, "collagen", **arguments),
    ),
)
