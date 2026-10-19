"""Geometry reachability across documents, history, jobs, and renderer leases."""

from typing import TYPE_CHECKING

from anthroforge.core.document import Document

from .resources import referenced

if TYPE_CHECKING:
    from .session import Session


def assets_used(document: Document) -> set[str]:
    return referenced(document)["meshes"]


def retained_documents(session: "Session") -> list[Document]:
    documents = [session.document, session.scheduler.checkpoint]
    documents.extend(entry.document for entry in session.history.entries)
    documents.extend(job.snapshot for job in session.scheduler.active_jobs if job.snapshot)
    if session.history.before:
        documents.append(session.history.before)
    return documents


def collect(session: "Session") -> None:
    references = [referenced(d) for d in retained_documents(session)]
    for kind in session.resources.__dataclass_fields__:
        used = set().union(*(keys[kind] for keys in references))
        catalogue = getattr(session.resources, kind)
        for key in tuple(catalogue):
            if key not in used:
                del catalogue[key]
