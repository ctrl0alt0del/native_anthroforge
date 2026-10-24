# Shortcut inspection and propagation feedback 0.3.1

- Branch: `codex/shortcut-inspection-031`; integration: `main`.
- Starting revision: `00e7339`; writer: local desktop; status: implementation in progress.
- Confirmed scope: influence inspection, formula evidence, effective attachment policy,
  propagation status, existing shortcut editor and explicit Show effects overlays.
- Comparison/report capture is deferred. Geometry, attachments and schema 5 stay unchanged.
- Preserve unrelated root `__init__.py`; validation stays background-only.

## Current state

Shared inspection APIs, runtime observation, editor sections, stable status, and optional
mesh/path/anchor overlays are implemented. Formula input evidence is distinct from current
values. Inspection observes submission/coalescing/publication independently of attachment
contexts. Recent edit/effect/formula caches have entry limits. Qualification remains in progress.
Detailed design: `docs/specification_031.md` and `docs/implementation_031.md`.

## Verification

Shared inspection/lifecycle tests pass, including Manual/On Release pauses, cancellation,
and no attribution of later direct edits to a finished shortcut. Existing offscreen shortcut
editor acceptance passes; strict typing passes. Native build is running (log under build/).
Full pytest at the prior checkpoint: 2018 passed. Added four UI/lifecycle regressions pass.
Offscreen editor checks preserve numeric-field bounds during edits; texture-only D3D11
captures show cyan downstream outlines. Mask geometry now belongs to its own lazy-loaded
scene; cross-scene reparenting produced an empty mask and was replaced. Anchor endpoints
use the native control geometry's nested XYZ contract. No interactive acceptance claimed.

Production Ribs Top Radius=3 comparison against main 00e7339: exact geometry and attachment
fingerprints before/after. Counterbalanced serial timings currently baseline 7.475/7.644 s,
first candidate 10.190 s, refined candidate 7.914 s (profiling enabled in all). Avoiding
full readiness scans while related jobs remain active reduced observed status work to
13.36 ms aggregate over 397 observations. Four inspection operations together median
8.32 ms; raw reports/fingerprints under build/shortcut-inspection-profile. Further trials,
full development gate and portable release remain. Historical pending provenance is now
distinct from current pending work; Ribs completion reports complete without changing results.

All four production controls now compared analytically against main: Ribs, Humerus,
Radius and Thumb. Every vertex, pose and attachment matches exactly. Thumb's Boolean
triangles differ in enumeration only; oriented connectivity hashes match after canonical
cyclic rotation and row ordering. Other triangle arrays match byte-for-byte. Reports:
build/shortcut-inspection-profile/comparison.json, baseline/candidate *.afprofile.zip.
Median four-query costs: 8.32 / 5.89 / 4.40 / 3.54 ms respectively. Do not claim a speedup;
these are instrumented, non-isolated timings (Thumb repeat overlapped packaging).

The first package was built successfully. A final read-set qualification additionally
made pending-input inspection surface-role-aware (tissue base vs final), with a regression
test. Rebuild the same canonical package before portable validation. New version 0.3.1;
schema remains 5. Environment was restored with all locked extras and packaging/qt-sdk
groups after a default uv sync omitted optional dependencies; current runtime pins match.

## Next actions

1. Development gate passed: 2,025 pytest, 5 native tests, typing/style/numerics/doctor.
2. Canonical 0.3.1 packaging and additional production shortcut comparisons are underway.
3. Verify portable suite, finalize documentation/source archive, validated merge/push.

## Recovery

Read AGENTS.md and docs/work_continuity.md. Current app checkout is E:/development/anthroforge.
Production fixture/mappings: E:/development/WIP_models/shortcut_update_parity_20261023/plan.json.
Prior accepted current captures: E:/development/WIP_models/shortcut_remaining_previews_20261024/.
No changes to deferred Ribs/Thumb behavior are authorized in this task.
