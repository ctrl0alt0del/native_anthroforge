# Preserve geometry while making large projects open promptly

- Task branch: `codex/project-open-performance`
- Integration branch: `main`
- Starting revision: `35a4c7b`
- Status: in progress
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

The full development gate passed (1,685 tests, five native CTests, styles, typing,
numerical audit and doctor). One later pending-publication regression is added; final
Python regression checks remain before delivery. Actual fixture replay against frozen
baseline source is bit-for-bit equal across 1,456 arrays per snapshot: open, three bone
edits, two fiber edits and all undos (11 snapshots). The hidden GPU viewport shows the
assembly while jobs remain active; offscreen GUI drag/undo/save/reopen passes. No visible
window/input was used. GPU readback timings do not establish interactive frame rates.

Canonical 0.2.3 rebuild, portable qualification, final save/reopen timings and source
archive refresh remain pending. Original project files remain untouched.

Measured first increment: 12.55 s versus 148.95 s, with the same 956 successful jobs
and 2,968 obsolete jobs. With request coalescing, obsolete jobs fall to 34 (956 successful);
instrumented total 15.21 s, including a slower read. Contract renewal initially added
avoidable per-poll work (24.74 s); it now caches unchanged graph/observation contracts.
These single diagnostic trials are preliminary; serial delivery measurements remain.

## Verification and next steps

1. Finish recorded open/save/reopen checks with exact geometry comparison.
2. Rebuild the canonical 0.2.3 distribution, run portable and fixture opening checks.
3. Record final evidence, refresh source archive, validated merge and push.

Recovery uses the normal Windows `.venv`, native build and packaging tools. All models,
captures and temporary experiments stay outside Git. Checkpoints describe incomplete work
honestly until the full acceptance above is complete.
