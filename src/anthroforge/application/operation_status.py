"""Small read-only action assessments; operation owners supply their own policies."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Eligibility:
    available: bool
    reason: str = ""
    warnings: tuple[str, ...] = ()

    def require(self) -> None:
        if not self.available:
            raise ValueError(self.reason)


def assess(validate: Callable[[], object]) -> Eligibility:
    try:
        validate()
        return Eligibility(True)
    except (ValueError, KeyError) as error:
        return Eligibility(False, str(error))
