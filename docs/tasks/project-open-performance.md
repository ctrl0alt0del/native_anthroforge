# Preserve geometry while making large projects open promptly

- Task branch: `codex/project-open-performance`
- Integration branch: `main`
- Starting revision: `35a4c7b`
- Status: complete — implementation, qualification and canonical distribution
- Last updated: 2026-10-22, Europe/Bucharest
- Active writer: local Codex chat, direct work; no agents

## Outcome and acceptance

Implement the measured optimizations in order: incremental document relationship/
validation reuse and batched pending publication; avoid unchanged startup results
invalidating downstream work; coalesce dependent updates; present saved geometry
while required startup work runs. Preserve actual geometry, attachments, authoring,
undo/checkpoints, Manual provenance, missing/cyclic-input handling and cancellation.
Keep the original project untouched and all desktop checks background/offscreen.

## Decisions and evidence

The authored-only skeleton/muscle assembly takes 148.95 s in the source runtime and
155.28 s in the recorded packaged run. Loading takes about 5 s; main-thread publication
takes about 141 s. Instrumentation found 2,559 document replacements, 120 s rebuilding
relationship signatures, 16 s rebuilding/validating the registry, and 2,968 obsolete
jobs out of 3,924. Bone pose drift on reopen is at most 6.573e-14, yet exact comparisons
invalidate downstream consumers. Saved geometry renders offscreen in about 10 s.

The baseline diagnosis and immutable fixture copies are external:
`E:/development/WIP_models/muscle_reconstruction_workflow/runs/2026-10-21-standalone-all-muscle-transfer-958f7969/diagnostics/open-performance-20261022/`.
Source SHA256: `2bcd72212488a5ea5ca4a19f2d5d2900a9ff9a814560156203f42e3721bf07b6`.
See `analysis.md`, recorder-off/recorded summaries, job/pose data and both profiler zips.
Profiler memory-reference observations were truncated; task/native timing events were retained.

Responsibility belongs to snapshot-owned structural indexes and shared publication/
dependency boundaries. Do not disable validation or startup synchronization globally,
introduce arbitrary coordinate tolerances, or change numerical inflation/attachment kernels
without evidence. The unrelated untracked root `__init__.py` must remain untouched.

## Current state

All four implementation areas are integrated. Exact receipts carry an evaluator version;
pending contracts cache unchanged graph/observation sets, release superseded request
payloads, and adopt current workspace priority. Geometry and tissue pending states publish
in batches; empty/already-pending geometry requests create no document revision.

The full development gate passed (five native CTests, styles, typing, numerical audit
and doctor); final Python regression checks pass 1,687 tests. Actual fixture replay against frozen
baseline source is bit-for-bit equal across 1,456 arrays per snapshot: open, three bone
edits, two fiber edits and all undos (11 snapshots). The hidden GPU viewport shows the
assembly while jobs remain active; offscreen GUI drag/undo/save/reopen passes. No visible
window/input was used. GPU readback timings do not establish interactive frame rates.

Canonical 0.2.3 rebuild and portable qualification pass. Compiled source identity is
`2e903c23ae74cd7b46c752eacbc74ee3608f9639` with no tracked changes at staging.
Original project files remain untouched.

Final source trials: original opening 16.247 s; save/fresh reopen 9.436 s, including
0.775 s startup synchronization and no document revision change. All 1,456 arrays are
bit-for-bit identical to baseline. Recorder-on opening takes 26.327 s. Evidence:
`diagnostics/open-optimization-20261022/final/` beside the baseline directory.
Ownership review identified that queued tissue-final
jobs must retain restart contracts because plans can change the required group/output
reservations; a new failing regression now passes with static final contracts. This
narrow correction is included in the final package and 1,687-test regression run.

Measured first increment: 12.55 s versus 148.95 s, with the same 956 successful jobs
and 2,968 obsolete jobs. With request coalescing, obsolete jobs fall to 34 (956 successful);
instrumented total 15.21 s, including a slower read. Contract renewal initially added
avoidable per-poll work (24.74 s); it now caches unchanged graph/observation contracts.
These single diagnostic trials are intermediate evidence; use the delivery trials below.

## Final delivery evidence

| Same complete assembly | Before | Optimized |
| --- | ---: | ---: |
| Packaged recorder-on process, open through settled/exported capture | 155.280 s | 26.383 s |
| Recorded result publication, inclusive | 136.672 s | 5.485 s |
| Packaged recorder-off process, open through settled | Not captured | 17.423 / 16.507 / 16.730 s |
| Packaged reopen after saving exact pose receipts, recorder off | Not available | 7.842 s |

Serial package trials used the same native build and minimal-PATH environment. System
busy fraction was 9.65% in the recorded baseline and 10.04% in the recorded candidate;
the three ordinary trials ranged 9.21–10.75%. Background activity and thermal state were
not controlled. Do not compare the recorded baseline directly with recorder-off results
or infer interactive frame latency. Both profiles retain all timing events but report
truncated bounded resource-reference observations. Candidate recording has no failed or
unfinished jobs; it coalesces 2,102 requests and has 36 obsolete jobs.

Packaged saved geometry is bit-for-bit equal across all 1,456 arrays against baseline;
the actual installed rendering was inspected alongside the baseline. Reopen leaves the
saved revision 52,447 unchanged. The source replay covers three SCP parent edits, two
Fiber edits and all undos; each of 11 snapshots is identical to baseline. Source files
retain the SHA256 above. All temporary inputs/outputs and frozen baseline code are local
under `diagnostics/open-optimization-20261022/`, especially `packaged-final/` and
`behavior-comparison.json`. Repo logs: `build/open-development-gate.log`,
`build/open-final-pytest.log`, `build/open-portable.log`, `build/open-gui-acceptance.log`.

## Ownership review

Snapshot validation/index reuse belongs to immutable document indexes, with current
record maps and conservative authored-field invalidation. Pose receipts are versioned
value provenance, not persistent native handles or coordinate tolerances. Coalescing
is opt-in for dispatch-captured, fixed-output jobs; final/group/recapture/payload jobs
retain restart rules. All publication read checks and resource ownership remain in the
existing coordinator. Numerical geometry/attachment kernels are unchanged. Desktop
startup reuses the existing worker load/adoption path rather than introducing a loader.
Review caught and regression-tested final-job group/reservation changes separately from
the successful geometry and performance tests.

Delivery uses one `dist/0.2.3/AnthroForge.dist` and one
`dist/AnthroForge-0.2.3-source.zip`. Integration target is unchanged `origin/main`
(`35a4c7b` at final fetch), through the normal validated merge/push workflow.
Offscreen evidence does not claim an interactive desktop acceptance session.

Recovery uses the normal Windows `.venv`, native build and packaging tools. All models,
captures and temporary experiments stay outside Git. Checkpoints describe incomplete work
honestly until the full acceptance above is complete.
