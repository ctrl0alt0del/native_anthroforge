# Standalone optimization audit

- Branch: codex/standalone-optimization-audit
- Integration: main
- Starting revision: 966ae1224a11c8c6a2948be7be58525998e84529 (0.1.5)
- Status: investigating
- Writer: desktop analysis chat; no delegation

## Scope

Review the migrated application for remaining addon constraints and opportunities
enabled by owning document, evaluation, scheduling and rendering. Inspect both the
current code and migration provenance. Use existing runtime captures and bounded
experiments to distinguish measured bottlenecks from scaling risks and hypotheses.
No production behavior changes or new release are authorized by this analysis task.

## Measured findings (checkpoint)

Activity's 0.1.5 fix is present. Mesh BVHs, native batch picking, immutable snapshots,
revision guards and staged rendering already exist; do not recommend adding them again.
The existing 0.1.5 Ctrl-drag/open-Activity capture has 80 Controller.refresh spans
averaging 20.55 ms inclusive while recording. It still rebuilds the entire scene
projection and broadcasts selectionChanged; authoring state serializes complete
definitions and replaces curve-choice models. Hidden ControlInspector bindings also
execute. These overlapping recorded durations must not be summed or treated as
unrecorded input latency. The previous unrecorded confirmation is 12.19-14.17 ms.

New unrecorded synthetic star-hierarchy measurements (nine repeats, one Body and
remaining empty groups, no GUI or worker dispatch):

| SCPs | Revision-only document replacement | Dependency graph | Scene projection | Live point-edit admission |
| ---: | ---: | ---: | ---: | ---: |
| 16 | 0.021 ms | 0.026 ms | 0.364 ms | 0.374 ms |
| 64 | 0.157 ms | 0.201 ms | 1.521 ms | 1.169 ms |
| 256 | 1.443 ms | 1.322 ms | 7.390 ms | 7.312 ms |
| 1024 | 19.666 ms | 13.152 ms | 50.532 ms | 86.845 ms |

A separately instrumented 512-SCP edit rebuilds the dependency graph three times
and validates the document twice before dispatch. Document.entity is linear;
descendants and native.attachments.ordered repeatedly scan the entire hierarchy.

The current Body path finalizes five native meshes per reevaluation with an accepted
previous mesh: base, base deformation, bending, curve-frame transform, topology reuse.
Each builds bounds, BVH and render chunks. A diagnostic-only, cached-base experiment
for one open capsule with identity curve frame and no deformers/thickness takes
0.43-0.57 ms versus 2.22-2.38 ms (482 vertices), 5.08-5.26 ms versus 26.39-28.40 ms
(4,034 vertices), and 27.33-27.80 ms versus 137.42-138.13 ms (16,258 vertices).
Serial ABBA, 12 evaluations per leg; all five canonical arrays, counts, bounds and
one picking ray match at eight edited positions per size (24 total, tolerance 1e-12).
This validates an opportunity, not a general replacement or full-app speedup.

Coordinator.jobs is append-only. Tick and invalidation scan terminal history too;
terminal jobs retain snapshots. In artificial completed-job histories, the latest
25-repeat run has idle tick medians 0.001/0.213/4.916/32.533 ms at
0/1,000/10,000/50,000 records. This is a scaling stress case, not a real-session soak.
The Activity model's 40-row limit does not bound coordinator retention.

## Next work and validation

Finalize evidence extraction/provenance and ranked recommendations with owning layers,
preserved semantics and acceptance cases. Separate measured gains from hypotheses.
Ruff and the two architecture tests pass for the diagnostic scripts. Both experiments
ran successfully. Full development gate and final evidence review are pending.

Keep raw captures/experiments in ignored build/standalone-audit. Preserve the unrelated
untracked root __init__.py. Final findings should state ownership, unchanged semantics,
evidence limits and discriminating acceptance for each proposed change.
