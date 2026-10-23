"""Declare only the approved guide-definition and consumer-mode migration changes."""

import sys
from pathlib import Path

from check_skeleton_shortcut_preservation import compare
from skeleton_shortcut_guides import GUIDES

CONSUMED = {"ribs_curve", "ribs_profile_top", "ribs_profile_bottom", "pelvic-guide"}


def normalize(key, before, after):
    if key in GUIDES:
        before["engine_settings"] = after["engine_settings"]
    if before.get("primitive"):
        for old, new in zip(
            before["primitive"]["curves"], after["primitive"]["curves"], strict=True
        ):
            if old["curve"] in CONSUMED:
                assert new["mode"] == "SHAPE_AND_TRANSFORM"
                old["mode"], old["bind_matrix"] = new["mode"], new["bind_matrix"]
    return before


if __name__ == "__main__":
    compare(*(Path(value) for value in sys.argv[1:4]), normalize=normalize)
