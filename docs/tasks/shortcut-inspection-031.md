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
Pending detailed UI/overlay acceptance, broader contracts, production geometry preservation,
profiling, full development gate and portable release. This checkpoint is not release-ready.

## Next actions

1. Finish explanatory UI details and verify fixed layouts/overlay revision agreement.
2. Broaden causal lifecycle coverage and qualify performance on production assembly.
3. Run complete gates, package canonical 0.3.1, validated merge/push.

## Recovery

Read AGENTS.md and docs/work_continuity.md. Current app checkout is E:/development/anthroforge.
Production fixture/mappings: E:/development/WIP_models/shortcut_update_parity_20261023/plan.json.
Prior accepted current captures: E:/development/WIP_models/shortcut_remaining_previews_20261024/.
No changes to deferred Ribs/Thumb behavior are authorized in this task.
