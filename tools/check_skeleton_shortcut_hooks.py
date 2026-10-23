"""Qualify compact deformation, allowing exactly six controls and three Hook bindings."""

import sys
from pathlib import Path

from check_skeleton_shortcut_migrated import normalize
from check_skeleton_shortcut_preservation import compare

PARTS = ("SCP_8", "SCP_9", "SCP_12")
EXTRAS = tuple(p + suffix for p in PARTS for suffix in (":driver-frame", ":driver-motion"))


def permitted(key, before, after):
    before = normalize(key, before, after)
    if key in {p + ":base-cage" for p in PARTS}:
        old, new = before["deformers"], after["deformers"]
        assert len(new) == len(old) + 1 and new[:-1] == old
        binding = new[-1]
        assert (
            binding["kind"] == "HOOK" and binding["control"] == key.split(":")[0] + ":driver-motion"
        )
        assert binding["target"] == dict(owner=key, stage="LATTICE", component="")
        assert not binding["restrict"] and binding["strength"] == 1 and binding["falloff"] == "NONE"
        before["deformers"] = new
    return before


if __name__ == "__main__":
    compare(*(Path(value) for value in sys.argv[1:4]), normalize=permitted, extras=EXTRAS)
