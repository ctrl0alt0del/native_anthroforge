"""Reviewed skeleton replacement contracts; no UI, resources or execution ownership."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BoneMatch:
    source: str
    target: str


@dataclass(frozen=True, slots=True)
class Finding:
    key: str
    owner: str
    message: str
    blocking: bool = False
    acknowledge: bool = False
    kind: str = "relationship"


@dataclass(frozen=True, slots=True)
class BoneChange:
    source: str
    target: str
    placement: bool
    construction: bool
    correspondence: str
    added: bool = False


def validate_matches(matches: tuple[BoneMatch, ...]) -> None:
    sources, targets = [m.source for m in matches], [m.target for m in matches]
    if any(not m.source or not m.target for m in matches):
        raise ValueError("Each bone match requires a source and destination.")
    if len(set(sources)) != len(sources) or len(set(targets)) != len(targets):
        raise ValueError("Bone matches must be one-to-one.")


def require_review(findings: tuple[Finding, ...], approved: list[str]) -> None:
    blocked = [f.message for f in findings if f.blocking]
    if blocked:
        raise ValueError("Resolve update findings: " + "; ".join(blocked))
    expected = {f.key for f in findings if f.acknowledge}
    if len(set(approved)) != len(approved) or set(approved) != expected:
        raise ValueError("Acknowledge the current attachment changes and calculation failures.")
