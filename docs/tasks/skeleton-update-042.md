# Whole-skeleton updates — 0.4.2

- Status: **Complete, qualified and merged into main.**
- Task branch: `codex/skeleton-update-042`
- Integration branch: `main`
- Starting revision: `5ed212a`
- Runtime checkpoint: `c8ca02d` (later edits are documentation only)
- Validated integration: `7b76336`; no concurrent main changes required reconciliation.
- Writer/reviewer: local desktop Codex; no independent agent review claimed
- Date: 2026-10-29, Europe/Bucharest

## Delivered behavior

[Confirmed contract](../skeleton_update_042.md). File → Update Skeleton from Project prepares
matched SCP construction/placement while retaining destination identities, organization,
compatible controls, mirror rules and update modes. Required construction copies independently.
Bindings and formula conflicts require explicit review; affected dependents evaluate in owned
candidate state using existing algorithms, including Manual objects. Paired views, placement
corrections, optional compatible final-skin deformation, findings, Cancel and one-action Apply/
Undo share the headless operation family. Source packages remain unchanged and are unnecessary
after adoption. Schema 8 remains unchanged.

## Qualification

- `tools/check.ps1 -BuildDirectory C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`
  passes: 2,722 pytest cases (368.61 s), six native suites, Ruff/style/function limits, mypy,
  numerical imports and native runtime doctor. Existing Qt deprecation warnings remain.
- 34 relocated portable checks pass under a minimal PATH, including the new skeleton operation,
  Undo/Redo, schema-8 persistence, hidden rendering and Qt-free headless execution.
- Lifecycle coverage includes unrelated edits, stale reads, retained dependent failures,
  exact acknowledgment sets, source removal, cancellation/resource ownership and optional
  fixed-topology skin. A recaptured bone pose survives subsequent ordinary attachment evaluation.
- Unchanged and Humerus-length production replacements agree with the ordinary evaluation
  reference. Preview and committed coordinates, poses, tissue stages and oriented connectivity
  agree at 1e-8 m; normalized retained Fiber binding records agree exactly.
- Ribs Top Radius→3, Humerus Length, Radius Length and Thumb Radius follow-up trials have no
  geometry or retained-Fiber-binding differences from the reference.
- Reordered same-count Tibia correctly requires explicit Rebind. Only its enumeration and
  reviewed material captures change; dependent paths/tissue coordinates remain equal.
- Source SHA256 is unchanged. Saved results remain self-contained after source removal.
- Four actual before/after GPU views and the packaged result were inspected. Paired-view
  visibility, shared camera/zoom, native displayed-revision picking and zero QML warnings are
  checked. These are background/hidden results, not physical interactive acceptance.

The first full gate reported 2,715 passes and two failures: a tool function-length violation
and a controller stub exposing direct coupling to the skeleton panel. Both were fixed, with
focused regressions and the complete successful rerun above. A QML visibility regression found
by image inspection was also corrected and the paired views recaptured before delivery.

## Performance and limits

On the 59-SCP / 96-tissue fixture, recorded source inspection takes 1.4–1.8 s, preparation
8.0–9.8 s and Apply 0.109–0.112 s. Peak working set reaches about 1.93 GiB. Three running
full-scene cancellations finish in 88–100 ms; live authored state is unchanged.

Initial GUI publication copied a ~1.5 MB nested QVariant report repeatedly, producing a
37–39 s UI pause. Compact cached review data now crosses into JavaScript once, separate from
small status/selection updates. Final paired-view run: installation 0.569 s, hidden-render
iteration maximum 0.733 s and p95 46 ms. These include profiler cost and GPU readback, not
physical display latency or disabled-profiler guarantees. No anatomy algorithm changed.

The production and GPU profiler manifests mark three and one `resource_payload_limit` losses
respectively. Detailed memory attribution is therefore incomplete; process peak working-set
measurements provide coarse memory evidence. Timed events remain usable. Automatic Qt binding
collection is unavailable in the hidden helper; boundary timings and controlled presentation
changes diagnosed the pause. No loss-free resource inventory or GPU execution claim is made.

## Ownership review

Typed assembly copy/source contracts own identity/resource transfer. Candidate EvaluationContext
owns unpublished document/results/preferences; the existing coordinator owns scheduling,
cancellation and publication. There is no second Session/pool or new propagation/routing/
inflation/relaxation/stacking kernel. Read validation includes affected relationships and
automatic routing/stacking membership. Selected resources transfer at Apply; history and
staged/displayed frames retain normal leases. UI owns compact presentation. Generic
PublicationGroup coordinates paired render models without controller knowledge of a feature.

## Reproduction and artifacts

- Source: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`
- SHA256: `308c216c85d9458d83e163bc3ed2ab85338bccd3adeb496981ffe35ec8275dac`
- Native runtime: `C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`
- Tools: `tools/skeleton_update_qualification.py`, `tools/skeleton_update_cancellation.py`,
  `tools/skeleton_update_scene.py`, `tools/skeleton_update_portable.py`.
- Local-only reports, source copies, captures and logs: `build/skeleton-update-042/`.
- Canonical delivery: `dist/0.4.2/AnthroForge.dist` and `dist/AnthroForge-0.4.2-source.zip`.
- Unrelated root `__init__.py` remains untouched. No WIP_models byproducts were created.
