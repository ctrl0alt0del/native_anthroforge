"""Bounded cancellation checks for snapshot serialization without changing its format."""

from typing import Any


class CancellableStream:
    def __init__(self, stream: Any, cancel: Any) -> None:
        self.stream, self.cancel = stream, cancel

    def __getattr__(self, name: str) -> Any:
        return getattr(self.stream, name)

    def write(self, data: Any) -> int:
        view = memoryview(data)
        for offset in range(0, len(view), 1024 * 1024):
            if self.cancel is not None and self.cancel.is_set():
                raise ValueError("Inspection export cancelled.")
            self.stream.write(view[offset : offset + 1024 * 1024])
        return len(view)
