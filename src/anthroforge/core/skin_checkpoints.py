"""Portable identities for builder-owned reusable construction prefixes."""

import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Checkpoint:
    builder: str
    version: int
    kind: str
    source: str
    prefix: str
    resource: str
    durable: bool = True

    def __post_init__(self) -> None:
        if not self.builder or self.version < 1 or self.kind not in ("SCP", "VCP"):
            raise ValueError("Invalid skin construction checkpoint identity.")
        if not self.source or any(
            not re.fullmatch(r"[a-f0-9]{64}", v) for v in (self.prefix, self.resource)
        ):
            raise ValueError("Invalid skin construction checkpoint digest.")


def matching(
    records: tuple[Checkpoint, ...], prefixes: tuple[str, ...], builder: str, version: int
) -> tuple[Checkpoint, ...]:
    index = {
        row.prefix: row for row in records if row.builder == builder and row.version == version
    }
    result = []
    for prefix in prefixes:
        row = index.get(prefix)
        if row is None:
            break
        result.append(row)
    return tuple(result)
