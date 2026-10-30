"""Assembly operation declarations; common execution lives in command_execution."""

from dataclasses import asdict

from .. import assembly_operations, mapping_queries, skeleton_operations
from ..command_contracts import direct, edit, method

COMMANDS = (
    edit("skeleton_update.apply", skeleton_operations.apply, isolated=True, project_scope=True),
    edit("assembly.import", assembly_operations.apply, isolated=True),
    direct("assembly.inspect", method("assembly.inspect")),
    direct("assembly.prepare", method("assembly.prepare")),
    direct("assembly.status", method("assembly.status")),
    direct("assembly.cancel", method("assembly.cancel")),
    direct("assembly.resolve", method("assembly.resolve")),
    direct("skeleton_update.inspect", method("skeleton_update.inspect")),
    direct("skeleton_update.prepare", method("skeleton_update.prepare")),
    direct("skeleton_update.status", method("skeleton_update.status")),
    direct("skeleton_update.cancel", method("skeleton_update.cancel")),
    direct(
        "assembly.references",
        lambda session: [asdict(r) for r in session.document.external_references],
    ),
    direct(
        "assembly.mapping.targets",
        lambda session, **arguments: mapping_queries.targets(session, "assembly", **arguments),
    ),
    direct(
        "assembly.mapping.properties",
        lambda session, **arguments: mapping_queries.properties(session, "assembly", **arguments),
    ),
    direct(
        "skeleton_update.mapping.targets",
        lambda session, **arguments: mapping_queries.targets(
            session, "skeleton_update", **arguments
        ),
    ),
    direct(
        "skeleton_update.mapping.properties",
        lambda session, **arguments: mapping_queries.properties(
            session, "skeleton_update", **arguments
        ),
    ),
)
