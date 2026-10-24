# Shortcut inspection and propagation feedback 0.3.1

- Branch: `codex/shortcut-inspection-031`; integration: `main`.
- Starting revision: `00e7339`; writer: local desktop; status: implementation and qualification complete.
- Runtime checkpoint: `5c70d53`. Final documentation and portable harness follow that commit.
- Scope: influence inspection, formula evidence, effective attachment policy,
  propagation status, existing shortcut editor and explicit Show effects overlays.
- Comparison/report capture is deferred. Geometry, attachments and schema 5 stay unchanged.
- Unrelated root `__init__.py` preserved; validation remains background-only.

## Delivered

Shared `shortcut.effects`, `.formulas`, `.attachment_policy` and `.progress` operations
are available to desktop and headless clients. The editor retains direct value editing,
fixed status rows and optional sections. Show effects highlights affected displayed meshes
and paths, and revision-qualified authored/effective anchor pairs. It is off by default.
Runtime causal evidence is independent of attachment contexts and never controls scheduling.
Recent edit/effect/formula records are bounded; missing captured evidence is explicit.
See [specification](../specification_031.md), [implementation](../implementation_031.md)
and [walkthrough](../shortcuts_031.md).

## Verification

- The full development gate passed at the prior runtime checkpoint (2,025 tests).
  Final role-aware pending-input regression plus the complete final suite: **2,026 passed**.
  Five native CTests, configured strict typing (375 modules), style/function limits,
  numerical checks and native doctor pass. Existing Qt property-map warnings remain.
- Lifecycle tests cover purity, cycles, Manual/On Release pauses, cancellation, undo,
  retry attribution, coalescing, bounded history, captured/current evidence and no
  attribution of unrelated later edits to a completed shortcut.
- Source-runtime offscreen editor checks keep numeric field bounds unchanged during edits.
  Texture-only D3D11 captures visibly show cyan downstream outlines and green anchor pairs.
  Mask geometry belongs to its own lazy scene; an initial cross-scene reparenting experiment
  produced an empty mask and was replaced. Anchor inputs use the native nested XYZ contract.
- Full portable checks pass against the canonical executable with minimal PATH and developer
  Python/Qt settings removed. The new four APIs, saved geometry, rendering and existing
  workflows pass. A relocated package under `build/` additionally runs a temporary QML
  harness against compiled desktop adapters: the inspection editor opens, effects enable,
  formulas and influence rows populate, and status completes without QML warnings.
  This harness does not modify the canonical distribution.
- No visible test windows or desktop input were used. Offscreen 2D captures do not prove
  physical viewport presentation; separate texture-only native renders cover geometry and
  effects. No physical interactive acceptance is claimed.

## Production comparisons and profiler evidence

Source fixture/mappings:
`E:/development/WIP_models/shortcut_update_parity_20261023/plan.json`.
The standalone 96-muscle project was loaded into memory; source files were not saved.
Baseline source `00e7339` and candidate use the same numerical native library.

| Control | Baseline seconds | Candidate seconds | Four inspection queries, median ms |
| --- | ---: | ---: | ---: |
| Ribs Top Radius = 3 | 7.475 (repeat 7.644) | 7.914 | 8.32 |
| Humerus length | 3.775 | 3.970 | 5.89 |
| Radius length | 3.277 | 3.309 | 4.40 |
| Thumb thickness | 1.118 | 1.213 | 3.54 |

All four cases preserve every vertex, pose and attachment exactly. Oriented connectivity
also matches. Thumb Boolean triangles differ only in enumeration; cyclic orientation and
sorted triangle hashes agree. The other three raw triangle arrays match byte-for-byte.
All completion reports finish without errors. Deferred Ribs/Thumb addon parity differences
remain untouched; these comparisons establish preservation of the current standalone.

The first Ribs candidate took 10.190 seconds. Avoiding repeated readiness scans while
related jobs remain active reduced observed settlement to 13.36 ms aggregate over 397 calls.
Timings are instrumented and non-isolated; the Thumb repeat overlapped packaging. Do not
infer a speed improvement, frame-time guarantee or isolated overhead estimate from them.

## Ownership and coupling review

The application modules own semantic inspection and the session owns transient evidence.
The graph remains the influence authority; accepted results retain readiness and provenance.
Coordinator event observation carries edit causes through queueing, coalescing and retries
without changing task priority, reservations or publication rules. Numerical attachment
queries reuse the native read-only query service with owned inputs and stale-result rejection.
The desktop owns status and overlays; it does not copy attachment rules. Masks own their
scene nodes and use existing native resource leases. No native algorithm or schema changed.

Evidence retention is bounded by record counts and encoded input size, not a total process
RSS ceiling. Active causal records remain until their jobs finish. Inspection is on demand;
formula evidence and edit lifecycle observation add measured runtime work. There is no
zero-overhead claim. Captured evidence is intentionally unavailable after reopening or eviction.

## Local artifacts and reproducible tools

- `build/shortcut-inspection-gate.log`, `shortcut-inspection-pytest-final.log`,
  `shortcut-inspection-native-final.log`, `shortcut-inspection-mypy-final.log`.
- `build/shortcut-inspection-review/`: editor, effect-mask and anchor captures.
- `build/shortcut-inspection-profile/`: baseline/candidate `.afprofile.zip`, fingerprints,
  and `comparison.json`; tool: `tools/shortcut_inspection_profile.py`.
- `build/shortcut-inspection-portable/portable-check.json` and corresponding log.
- `build/shortcut-inspection-packaged-ui/packaged-inspection.json`, screenshot and log;
  tool: `tools/shortcut_inspection_portable.py` (only its temporary copy has harness QML).
- Canonical delivery: `dist/0.3.1/AnthroForge.dist/AnthroForge.exe` and
  `dist/AnthroForge-0.3.1-source.zip`. Packaging log: `build/shortcut-inspection-package-final.log`.

## Recovery

No implementation work remains. The canonical package and companion source archive are
local release artifacts; Git contains source and reproducible qualification tools. Integration
is recorded by the merge of `codex/shortcut-inspection-031` into `main`. No deferred parity
behavior changes are authorized by this task.
