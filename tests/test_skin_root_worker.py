"""Root sampling policy preserves later routes and the native containment retry."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from anthroforge.avbd_runtime import root_seed


class ExistingStages:
    def __init__(self, root, meshes, frame):
        self.parent = None

    def seed(self, folder, step, active, row):
        return (self.parent, step.route, active[-1])


def test_root_target_is_only_used_before_the_first_accepted_stage(monkeypatch):
    monkeypatch.setattr(
        root_seed.worker, "module", lambda name: SimpleNamespace(SkinStages=ExistingStages)
    )
    monkeypatch.setattr(root_seed, "build", lambda folder, bone, row, vertices: (bone, vertices))
    stages = root_seed.stages(Path("out"), [], Path("frame"), 802)
    step = SimpleNamespace(route="follow")
    assert stages.seed(None, step, ["root"], {}) == ("root", 802)
    stages.parent = "accepted"
    for route in ("follow", "limb", "region"):
        result = stages.seed(None, SimpleNamespace(route=route), ["child"], {})
        assert result == ("accepted", route, "child")


def native_calls(witness):
    calls = []

    def call(args, folder, name):
        calls.append(args)
        if len(calls) == 1:
            raise RuntimeError("Invalid hull/reference: refined")
        return dict(accepted=True)

    physical = SimpleNamespace(
        NATIVE="native", call=call, read=lambda path: witness, write=lambda path, value: None
    )
    return calls, physical


@pytest.mark.parametrize("outside", [0, 2])
def test_feature_preserving_retry_uses_the_same_root_target(tmp_path, outside):
    calls, physical = native_calls(dict(self=0, degenerate=0, outside=outside, crossings=0))
    result = root_seed.isotropic(tmp_path, 802, physical)
    assert result["protected_sharp_edges"]
    assert [call[1] for call in calls] == ["sphere-isotropic", "sphere-isotropic-features"]
    assert [call[-1] for call in calls] == [802, 802]


def test_invalid_seed_geometry_is_not_hidden_by_feature_retry(tmp_path):
    calls, physical = native_calls(dict(self=1, degenerate=0, outside=2, crossings=0))
    with pytest.raises(RuntimeError, match="Invalid hull/reference"):
        root_seed.isotropic(tmp_path, 802, physical)
    assert len(calls) == 1


def test_unrelated_native_failure_does_not_select_another_mesher(tmp_path):
    with pytest.raises(RuntimeError, match="tool unavailable"):
        root_seed.containment_failure(tmp_path, None, RuntimeError("tool unavailable"))
