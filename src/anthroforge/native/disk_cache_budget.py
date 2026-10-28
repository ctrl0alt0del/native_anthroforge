"""Best-effort bounded disposable products; never delete active temporary writes."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast

BUDGET = 2 * 1024**3
CAPACITY = 256


def acquire(stream: Any) -> None:
    if os.name == "nt":
        import msvcrt

        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
    else:
        import fcntl

        locking = cast(Any, fcntl)
        locking.flock(stream.fileno(), locking.LOCK_EX | locking.LOCK_NB)


@contextmanager
def transaction(folder: Path) -> Any:
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / ".budget.lock").open("a+b") as stream:
        if not stream.tell():
            stream.write(b"\0")
            stream.flush()
        acquire(stream)
        remove_abandoned_staging(folder)
        yield


def remove_abandoned_staging(folder: Path) -> None:
    # Every publisher holds this same OS lock, so no matching write can be active.
    for path in folder.glob("af-weights-*.tmp"):
        try:
            path.unlink()
        except OSError:
            pass


def products(folder: Path) -> list[Any]:
    result = []
    for path in folder.glob("*.zip"):
        try:
            stat = path.stat()
            result.append((stat.st_mtime_ns, path, stat.st_size))
        except OSError:
            continue
    return sorted(result)


def trim(folder: Path, incoming: int = 0, replacing: Path | None = None) -> bool:
    rows = [r for r in products(folder) if r[1] != replacing]
    total, count = sum(r[2] for r in rows) + incoming, len(rows) + bool(incoming)
    for _, path, size in rows:
        if total <= BUDGET and count <= CAPACITY:
            break
        try:
            path.unlink()
            total, count = total - size, count - 1
        except OSError:
            continue
    return total <= BUDGET and count <= CAPACITY


def used(path: Path) -> None:
    try:
        os.utime(path, None)
        with transaction(path.parent):
            trim(path.parent)
    except OSError:
        pass
