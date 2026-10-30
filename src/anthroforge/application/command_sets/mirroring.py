"""Mirroring operation declarations; common execution lives in command_execution."""

from .. import mirror_bindings, mirror_operations, mirror_policy, symmetric_paths
from ..command_contracts import direct, edit

COMMANDS = (
    edit("mirror.loop.create", symmetric_paths.create),
    edit("mirror.configure", mirror_operations.configure),
    edit("mirror.attachment.share", mirror_operations.share_target),
    direct("mirror.attachment.inspect", lambda session, **a: mirror_bindings.inspect(session, **a)),
    direct("mirror.list", lambda session, **a: mirror_operations.listing(session, **a)),
    direct("mirror.inspect", lambda session, **a: mirror_operations.inspect(session, **a)),
    direct("mirror.source", lambda session, **a: mirror_operations.source(session, **a)),
    direct("mirror.removal.inspect", lambda session, **a: mirror_operations.removal(session, **a)),
    direct("mirror.attachment.shared", lambda session, **a: mirror_operations.shared(session, **a)),
    direct("mirror.planes", lambda session: mirror_operations.planes(session)),
    direct(
        "mirror.source.removal.inspect",
        lambda session, target: mirror_policy.removing(session.document, target),
    ),
)
