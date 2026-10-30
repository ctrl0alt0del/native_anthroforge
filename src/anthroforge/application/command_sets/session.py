"""Session operation declarations; common execution lives in command_execution."""

from anthroforge.core.units import convert

from .. import importing, operations, presentation, projects
from ..application_evaluation import evaluate
from ..command_contracts import direct, edit, method

COMMANDS = (
    edit("update_mode", operations.update_mode),
    edit("import", importing.import_mesh),
    direct("inspect", method("describe")),
    direct("wait", method("wait")),
    direct("tick", method("scheduler.tick")),
    direct("evaluate", lambda session, **a: evaluate(session, **a)),
    direct("begin", method("begin")),
    direct("commit", method("commit")),
    direct("cancel", method("cancel")),
    direct("undo", lambda session: session.navigate(-1)),
    direct("redo", lambda session: session.navigate(1)),
    direct(
        "job.cancel",
        lambda session, job_id, obsolete=False: session.scheduler.cancel_job(job_id, obsolete),
    ),
    direct("job.retry", method("scheduler.retry")),
    direct("units.convert", lambda session, **arguments: convert(**arguments)),
    direct("preferences.get", method("preferences.describe")),
    direct("preferences.set", method("preferences.update")),
    direct("save", lambda session, **a: projects.save(session, **a)),
    direct("open", lambda session, **a: projects.open_project(session, **a)),
    direct("workspace.create", lambda session, **a: presentation.create_workspace(session, **a)),
    direct("workspace.select", lambda session, **a: presentation.select_workspace(session, **a)),
    direct("workspace.update", lambda session, **a: presentation.update_workspace(session, **a)),
    direct("workspace.remove", lambda session, **a: presentation.remove_workspace(session, **a)),
    direct("workspace.preset", lambda session, **a: presentation.preset(session, **a)),
    direct("view.hide", lambda session, **a: presentation.hide(session, **a)),
    direct("view.isolate", lambda session, **a: presentation.isolate(session, **a)),
    direct("view.show_all", lambda session: presentation.update_workspace(session, hidden=[])),
)
