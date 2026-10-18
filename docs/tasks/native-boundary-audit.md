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

## Acceptance and next actions

1. Capture baseline preparation and multi-point dispatch costs; implement owning native APIs.
2. Test native parity and mixed-frame component editing; compare ordinary runtime reports.
3. Run development gate, relevant GUI and packaged application checks.
4. Record the audited boundary and measured limitations, then integrate and push.

Preserve unrelated root `__init__.py`. Captures/builds stay in ignored
`build/native-boundary-audit`; compact evidence will be committed. Prior optimization
results remain in `docs/tasks/standalone-optimizations.md`.
