"""Geometry reachability across documents, history, jobs, and renderer leases."""

from typing import TYPE_CHECKING

from anthroforge.core.document import Document
from anthroforge.core.results import geometry_asset

if TYPE_CHECKING:
    from .session import Session


def assets_used(document: Document) -> set[str]:
    results = {geometry_asset(item) for item in document.entities}
    sources = {item.primitive.source for item in document.entities if item.primitive}
    return (results | sources) - {""}


def retained_documents(session: "Session") -> list[Document]:
    documents = [session.document, session.scheduler.checkpoint]
    documents.extend(entry.document for entry in session.history.entries)
    documents.extend(job.snapshot for job in session.scheduler.active_jobs if job.snapshot)
    if session.history.before:
        documents.append(session.history.before)
    return documents


def collect(session: "Session") -> None:
    used = set().union(*(assets_used(d) for d in retained_documents(session)))
    for key in tuple(session.assets):
        if key not in used:
            del session.assets[key]
