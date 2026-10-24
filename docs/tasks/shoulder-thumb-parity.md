# Shoulder and Thumb shortcut parity diagnosis

- Branch: codex/shoulder-thumb-parity; baseline: 51ff0af; integration: main.
- Request: isolate the remaining Ribs shoulder/Clavicle and Thumb differences from
  Blender. Explain actual causes and approach before changing attachment behavior.
- Background-only investigation; preserve source projects and unrelated __init__.py.
- References: tasks/shortcut-update-parity.md and tasks/shortcut-owner-binding.md.
- Compare baseline and edits on the same paired 96-muscle fixtures. Trace parent
  geometry, retained bindings, control transforms, curve endpoints and final poses.
- Test Hook and Shrinkwrap contributions separately rather than assuming either.
- Production behavior changes are outside this diagnosis until the approach is discussed.
- Local evidence: build/shoulder-thumb-parity; source parity fixtures remain untouched.
- Status: investigation started; no attachment/geometry behavior changes.
