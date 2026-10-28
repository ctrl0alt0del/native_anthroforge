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
    references = session.reachability.references(retained_documents(session))
    for kind in session.resources.__dataclass_fields__:
        used = set().union(*(keys[kind] for keys in references))
        catalogue = getattr(session.resources, kind)
        for key in tuple(catalogue):
            if key not in used:
                del catalogue[key]


class Reachability:
    """Retain reference sets only while their immutable documents have live owners."""

    def __init__(self) -> None:
        self.documents: dict[int, tuple[Document, dict[str, set[str]]]] = {}

    def references(self, documents: list[Document]) -> list[dict[str, set[str]]]:
        current = {id(document): document for document in documents}
        self.documents = {key: value for key, value in self.documents.items() if key in current}
        for key, document in current.items():
            if key not in self.documents:
                self.documents[key] = (document, referenced(document))
        return [entry[1] for entry in self.documents.values()]
