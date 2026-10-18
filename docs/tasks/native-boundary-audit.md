# Python/native algorithm boundary audit

- Task branch: `codex/native-boundary-audit`
- Integration: `main`
- Starting revision: `7c55151999d043269d09a417623e6ac73e92302c`
- Status: implementation in progress
- Writer: desktop, direct work; 2026-10-18 Europe/Bucharest

## Outcome

Audit migrated standalone algorithms and remove unnecessary Python numerical loops.
Explain the existing Python choice from actual implementation and original stack
decision. This is not a whole-application rewrite or migration of future skin/fiber tools.

## Findings and ownership

The current C++ library already owns attachment capture/propagation, curves, loft/body
construction, Hook/Lattice/Solidify, spatial queries and transforms. The standalone has
no Blender runtime dependency. Python owns immutable records, commands, transactions,
scheduling, validation, persistence and Qt adapters by the original stack decision.

Confirmed remaining boundary problems: influence inversion/membership masking in
`native/construction.py`; display curve/cage connectivity and cubic query packing in
Python; per-point native transform dispatch in `desktop/authoring_actions.py`.
Move geometry preparation to batched C++ APIs and group point transforms by target.
Preserve membership, curve ordering/closing, transforms, snapshots, undo and native
cancellation. Keep constant-size UI calculations and record/identity operations in
Python. Dense UI projection costs require separate evidence, not a claim that these
small kernels alone eliminate the previously measured dense-cage latency.

## Implemented checkpoint

Added native influence evaluation (default influence requires no allocated weight
array), display polyline/cage connectivity and cubic query packing. Grouped selected
point conversion by target frame while preserving input order and command semantics.
Native construction/Blender parity tests pass (143); focused preparation, curve-query,
gesture and architecture tests pass (55). Full gate/GUI/package still pending.

Serial ABBA, 25 unrecorded calls per case per leg, identical rounded output hashes:

| Preparation workload | Before median ms | After median ms |
| --- | ---: | ---: |
| 100,000-point default Hook | 0.740–0.749 | 0.588–0.605 |
| 100,000-point weighted/restricted Hook | 4.099–4.260 | 3.122–3.141 |
| 1,000-point cage display lines | 0.776–0.788 | 0.545–0.558 |
| 1,000-point closed curve query packing | 1.614–1.641 | 0.571–0.572 |
| 1,000 selected points, coordinate conversion | 22.379–22.968 | 1.116–1.165 |

The last experiment intercepts command publication to isolate preparation; it does
not establish full multi-point gesture speed. Each leg also exports an ordinary
runtime report; [compact evidence](native-boundary-audit-evidence.json) records timings,
output checksums and native calls. Source snapshots/reports remain local ignored data.

## Acceptance and next actions

1. Run development gate, relevant GUI and packaged application checks.
2. Record the audited boundary and measured limitations, then integrate and push.

Preserve unrelated root `__init__.py`. Captures/builds stay in ignored
`build/native-boundary-audit`; compact evidence will be committed. Prior optimization
results remain in `docs/tasks/standalone-optimizations.md`.
