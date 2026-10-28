"""Addon worker budget policy: at most 35% available RAM, capped at four GiB."""

import ctypes as c
import os
import sys
from pathlib import Path


class MemoryStatus(c.Structure):
    _fields_ = [("length", c.c_ulong), ("load", c.c_ulong)] + [
        (name, c.c_ulonglong)
        for name in (
            "total_phys",
            "avail_phys",
            "total_page",
            "avail_page",
            "total_virtual",
            "avail_virtual",
            "avail_extended",
        )
    ]


def available() -> int:
    if sys.platform == "win32":
        status = MemoryStatus()
        status.length = c.sizeof(status)
        return (
            int(status.avail_phys) if c.windll.kernel32.GlobalMemoryStatusEx(c.byref(status)) else 0
        )
    try:
        sysconf = os.sysconf
        host = int(sysconf("SC_AVPHYS_PAGES") * sysconf("SC_PAGE_SIZE"))
        return min(host, cgroup_available(host))
    except (AttributeError, ValueError, OSError):
        return 4 * 1024**3


def cgroup_available(fallback: int) -> int:
    folder = Path("/sys/fs/cgroup")
    try:
        maximum = (folder / "memory.max").read_text().strip()
        used = int((folder / "memory.current").read_text())
        return fallback if maximum == "max" else max(0, int(maximum) - used)
    except (OSError, ValueError):
        return fallback


def budget() -> int:
    return int(min(4 * 1024**3, (available() or 4 * 1024**3) * 0.35))
