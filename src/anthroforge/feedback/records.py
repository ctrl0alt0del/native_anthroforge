"""Immutable report contract; annotations use original screenshot pixels."""

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Protocol


@dataclass(frozen=True)
class Annotation:
    kind: str
    x1: float
    y1: float
    x2: float
    y2: float
    text: str = ""
    stroke: float = 4.0
    font_size: float = 24.0


@dataclass(frozen=True)
class Report:
    id: str
    created_at: str
    category: str
    description: str
    context_json: str
    width: int
    height: int
    annotations: tuple[Annotation, ...]
    original_png: bytes
    annotated_png: bytes


@dataclass(frozen=True)
class Receipt:
    location: str
    reveal: str


class ReportConsumer(Protocol):
    @property
    def description(self) -> str: ...

    def submit(self, report: Report) -> Receipt:
        """Durably accept a report and return its location; raise on failure."""
        ...


def metadata(report: Report) -> dict[str, object]:
    return dict(
        schema_version=1,
        report_id=report.id,
        created_at=report.created_at,
        category=report.category,
        description=report.description,
        context=json.loads(report.context_json),
        image=dict(width=report.width, height=report.height, coordinates="source pixels"),
        annotation_color="#ff3434",
        annotations=[asdict(a) for a in report.annotations],
        attachments={name: sha256(data).hexdigest() for name, data in images(report).items()},
    )


def images(report: Report) -> dict[str, bytes]:
    return {"original.png": report.original_png, "annotated.png": report.annotated_png}
