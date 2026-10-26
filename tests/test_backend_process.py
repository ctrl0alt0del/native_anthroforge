"""Backend execution owns its entire process tree, timeout and output budget."""

import ctypes as c
import sys
from dataclasses import replace
from threading import Timer

import pytest

from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.process import Limits, Request, run

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows runner qualification")


def request(tmp_path, code, limits=None):
    return Request(
        (sys.executable, "-c", code), tmp_path, tmp_path / "output.log", limits or Limits()
    )


def test_backend_returns_exit_status_and_captures_output(session, tmp_path):
    value = request(tmp_path, "import sys; print('hello'); sys.exit(7)")
    assert run(session.engine, value) == 7
    assert "hello" in value.log.read_text()


def test_backend_times_out_and_releases_handles(session, tmp_path):
    value = request(tmp_path, "import time; time.sleep(60)", Limits(milliseconds=100))
    with pytest.raises(ValueError, match="timed out"):
        run(session.engine, value)
    value.log.unlink()


def test_backend_cancel_stops_wait(session, tmp_path):
    cancel = NativeCancellation(session.engine)
    timer = Timer(0.2, cancel.set)
    timer.start()
    try:
        with pytest.raises(ValueError, match="[Cc]ancel"):
            run(session.engine, request(tmp_path, "import time; time.sleep(60)"), cancel.handle)
    finally:
        timer.join()


def test_backend_log_limit_is_enforced(session, tmp_path):
    code = "import time; print('x'*20000, flush=True); time.sleep(60)"
    with pytest.raises(ValueError, match="log limit"):
        run(session.engine, request(tmp_path, code, Limits(log_bytes=1024)))


def test_invalid_backend_limits_do_not_create_output(session, tmp_path):
    value = request(tmp_path, "print('no')")
    with pytest.raises(ValueError, match="limits"):
        run(session.engine, replace(value, limits=Limits(memory=-1)))
    assert not value.log.exists()


def test_backend_memory_cap_reaches_child_before_execution(session, tmp_path):
    code = "try:\n a=bytearray(512*1024**2)\nexcept MemoryError:\n raise SystemExit(23)"
    value = request(tmp_path, code, Limits(memory=128 * 1024**2))
    assert run(session.engine, value) == 23


def test_timeout_terminates_spawned_children(session, tmp_path):
    code = (
        "import subprocess,sys,time; "
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
        "print(p.pid,flush=True); time.sleep(60)"
    )
    value = request(tmp_path, code, Limits(milliseconds=1500))
    with pytest.raises(ValueError, match="timed out"):
        run(session.engine, value)
    pid = int(value.log.read_text().strip())
    assert_stopped(pid)
    value.log.unlink()


def assert_stopped(pid):
    kernel = c.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes, kernel.OpenProcess.restype = (
        [c.c_uint32, c.c_int, c.c_uint32],
        c.c_void_p,
    )
    kernel.WaitForSingleObject.argtypes = [c.c_void_p, c.c_uint32]
    kernel.CloseHandle.argtypes = [c.c_void_p]
    handle = kernel.OpenProcess(0x100000, False, pid)
    if handle:
        try:
            assert kernel.WaitForSingleObject(handle, 0) == 0
        finally:
            kernel.CloseHandle(handle)


def test_unicode_paths_and_quoted_arguments(session, tmp_path):
    folder = tmp_path / "space \u043f\u0430\u043f\u043a\u0430"
    folder.mkdir()
    value = request(folder, "import sys; print(repr(sys.argv[1:]))")
    value = replace(value, arguments=(*value.arguments, 'a "quote"', "back\\slash", ""))
    assert run(session.engine, value) == 0
    assert value.log.read_text().strip() == repr(list(value.arguments[3:]))
