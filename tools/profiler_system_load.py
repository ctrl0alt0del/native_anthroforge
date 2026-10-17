"""Windows system-wide utilization context for serial diagnostic trials."""

import ctypes
from ctypes.wintypes import FILETIME
from time import perf_counter, process_time


def system_times():
    idle, kernel, user = FILETIME(), FILETIME(), FILETIME()
    ctypes.windll.kernel32.GetSystemTimes(
        ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
    )
    values = [(v.dwHighDateTime << 32) | v.dwLowDateTime for v in (idle, kernel, user)]
    return (*values, perf_counter(), process_time())


def system_load(before):
    after = system_times()
    idle, kernel, user, wall, cpu = (a - b for a, b in zip(after, before, strict=True))
    return dict(
        system_busy_fraction=1 - idle / max(1, kernel + user),
        application_cpu_seconds=cpu,
        wall_seconds=wall,
        note="System busy includes this app; other processes and thermal state are uncontrolled.",
    )
