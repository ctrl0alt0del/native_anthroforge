"""A failed temporary numerical worker retains actionable evidence after cleanup."""

from types import SimpleNamespace

import pytest

from anthroforge.application import numerical_process
from anthroforge.native import process


def test_worker_failure_retains_bounded_log_when_directory_is_removed(tmp_path, monkeypatch):
    folder = tmp_path / "worker"
    folder.mkdir()
    log = folder / "tetrahedral.log"
    log.write_text("old message\n" * 10000 + "ImportError: missing numerical dependency")
    monkeypatch.setattr(process, "run", lambda *args: 1)
    with pytest.raises(ValueError) as failure:
        numerical_process.execute(
            None, ("worker",), folder, SimpleNamespace(handle=0), process.Limits(), "tetrahedral"
        )
    log.unlink()
    folder.rmdir()
    assert "ImportError: missing numerical dependency" in str(failure.value)
    assert len(str(failure.value)) < 4200
