"""Migration requires effective policies and applies them to both wrapper kinds."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE = Path(__file__).resolve().parents[1] / "tools/skeleton_shortcut_policies.py"
SPEC = importlib.util.spec_from_file_location("migration_policies", SOURCE)
assert SPEC and SPEC.loader
POLICIES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICIES)


def test_raw_unset_flag_is_not_a_usable_migration_policy():
    with pytest.raises(ValueError, match="Recapture"):
        POLICIES.effective_backsolve(dict(owner_backsolve=False))
    row = dict(owner_backsolve=False, owner_backsolve_effective=True)
    assert POLICIES.effective_backsolve(row) is True
    assert POLICIES.effective_backsolve(dict(row, owner_backsolve_effective=False)) is False


@pytest.mark.parametrize("mapping", [dict(driver="d"), dict(reference={"target": "s"})])
def test_driver_and_direct_wrapper_receive_effective_policy(monkeypatch, mapping):
    import sys

    monkeypatch.setitem(
        sys.modules, "skeleton_shortcut_pelvis", SimpleNamespace(override=lambda v: v)
    )
    calls = []
    session = SimpleNamespace(command=lambda *a, **kw: calls.append((a, kw)))
    POLICIES.apply(
        session, dict(owner_id="s", owner_backsolve_effective=True, overrides=[]), mapping
    )
    args, kwargs = calls[0]
    policy = kwargs["changes"]["policy"] if "driver" in mapping else kwargs["policy"]
    assert policy == dict(scope="s", backsolve=True, descendants=[])
    assert args[0] == ("driver.configure" if "driver" in mapping else "shortcut.configure")
