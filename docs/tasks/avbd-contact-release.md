# Complete AVBD contact optimization and full-project qualification

- Task branch: `codex/avbd-contact-release`
- Integration branch: `main`
- Starting revision: `6ac2f11561aa6b8101ea9ca6281a4d907959eea1`
- Status: in progress
- Last updated: 28 November 2026, Europe/Bucharest
- Active writer: current desktop chat

## Outcome and acceptance

The user selected no vertex elimination and asked to finish the full project. Integrate the measured contact optimizations with the full skin active, qualify the complete AVBD draft build of `skeleton_all_reconstructed_muscles_v001.anthroforge` (58 bone instances and 265 muscle instances), and deliver the rebuilt portable app to `E:/development/anthroforge/dist/0.4.3/AnthroForge.dist` with its matching source archive. Test ordinary packaged startup and skin generation without runtime environment configuration. Preserve the authored source document by working on a copy.

## Decisions and relevant files

- D1 — Confirmed by user: no dynamic sleeping, inherited sleeping or experimental SCP activity masks. Keep the SCP skin fully active; preserve the existing VCP boundary conditions.
- D2 — Native ownership: canonical GPU sorting and candidate allocation belong to the AVBD native contact pipeline. Preserve canonical contact order, force state, conservative motion bounds, fallback processing, and the existing 2 GiB owned GPU limit. Tests cover key boundaries, buffer budget cases, numerical parity, and native telemetry.
- D3 — Initial-radius policy: use a typed radius initialization setting in the local SCP solver profile, not application environment-variable switches. Preserve the established root initialization and fixed-radius VCP behavior; use the measured `0.0065` adaptive start for subsequent local SCP additions. Test a fresh root and every stage in the complete document.
- D4 — Candidate sizing: prefer eight candidates per contact, bounded by the shared memory estimator and existing capacity contract. Large or constrained cases may retain a smaller supported candidate buffer; a larger preferred buffer must not defeat the GPU ownership limit.
- D5 — Workspace safety: the clean app checkout is at `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge`. Its qualified numerical source is `E:/development/anthroforge/build/application-boundaries`, which has extensive pre-existing changes. Save exact native preimages and a task-only patch; preserve unrelated work. The shipped AVBD source archive and manifest must describe the exact qualified inputs.
- D6 — Existing content-based runtime identities include the bundle manifest and native executables. Regenerating them invalidates incompatible old checkpoints without inventing another cache protocol.

## Current state

Prior isolated tests showed approximately 166 to 4.18 seconds on the same Fibula seed with smaller adaptive startup radius, full-width GPU contact keys, and an eight-times candidate buffer. The native bone chain completed all additions; muscle stages and the persistent app worker remain unqualified. Sleeping follow-up tests did not show a net gain and are excluded.

Native production changes compile for both packaged workers. Host policy tests cover
200,032 randomized/duplicate/boundary contact keys, candidate budget bounds and invalid
inputs, and root/local/fixed radius isolation. Matched Fibula, Radius and finger seeds
reproduce the verified optimized positions, faces, velocities and contact states byte for
byte. Geometry audits pass, radius guard violations are zero, and owned GPU memory stays
below 2 GiB. Fibula took 4.78 s during concurrent application checks; this is qualification,
not a new isolated speedup claim. A 2.3-million-contact cache selects 16,927,730 candidates
instead of its preferred 18.4 million and passes the same parity/geometry checks. An
explicit 2.8-million cache on this large fixture cannot fit and is rejected before allocation.

The source delta and portable host checks are preserved in
[`avbd-contact-release/`](avbd-contact-release/README.md). They apply to the exact local
runtime baseline, not to the older tracked native branch alone. The complete baseline and
delta will be retained in the shipped `avbd-sources.zip`. Application release packaging
and its full development gate are running; full-document and GUI qualification are pending.

The fresh portable build is complete at `build/avbd-release-20261128/package/AnthroForge.dist`
in the main project directory. Build identity is clean application revision `906b0499`;
executable SHA-256 is `cdf6b61b5fdf33a47135386d025359d5d06537caf8b33bc78207e4fb42962e44`.
Both candidate and fresh package pass 8,536 manifest file checks and 1,166 isolated import
checks. A normal launch with no command-line options and no external runtime configuration
has been visually inspected; GUI evidence is in the local task's `gui` folder.

The full model is running through packaged Authoring on a preserved input copy. To overlap
compilation, it uses the previously compiled application with the new complete runtime;
`git diff 67b7d41b HEAD -- src native tools pyproject.toml uv.lock launch.py` was empty.
The fresh executable will also validate the resulting document. The full run passed the
previously failing Fibula stage (index 37) and has accepted 43 bone stages so far; muscle
processing has not started. Hard-linked diagnostic files survive worker cleanup under
`full-project/diagnostics/afskin-kgvzb7n3`. Run `progress.py` or inspect `authoring.jsonl`
and `exit.json` in the local task folder before resuming; do not start a duplicate solve.

The first complete packaged attempt accepted all 58 bones in 1,236.24 s of stage wall
time (20 min 36 s), with two already-clear muscles, then exposed an existing VCP limit:
its unbatched contact path rejected more than 32,768 physical vertices. The failed worker
and every accepted checkpoint were retained; Authoring saved the partial checkpoint
document (`complete-result.anthroforgex`, despite that harness filename, is not a complete
skin result). End-to-end attempt wall time was 1,307.53 s.

D7 — Contact-key ownership is shared by batched SCP and unbatched VCP execution. Initialize
the same compact/base/full-width policy before selecting storage. Retain signed 32-bit
vertex-ID bounds and all capacity/geometry checks. The exact formerly failing muscle input
now completes 63 frames in 12.80 s, reaches the full pose and passes native containment,
crossing, clearance, self-intersection and degeneracy checks. No muscle radius, mobility,
material or acceptance policy changed. A native-worker continuation using the explicit
accepted 58-bone/two-muscle fixture passed 22 muscle instances under `muscles-v2`, including
movement and the existing regional-fill/shield fallback. The current owned diagnostic
process tree was intentionally stopped after that qualification, rather than duplicating
the remainder of the final application run. Its stop receipt preserves the accepted count
and process identity. This is numerical qualification, not a bypass of runtime identities.

Runtime v2 packaging is complete in the same temporary package directory. Its VCP solver
SHA-256 is `fc5bea5a5455f4ba943ef348f3cc9d20abbf1ce565e309fd4b7016b68ca577f7`.
The final full project is now running from a fresh original-input copy through the fresh
packaged executable (PID recorded in `full-project-final/process.json`, initially 46624).
Diagnostics are retained in `full-project-final/diagnostics/afskin-ndrs650c`.
Use `final_progress.py`, `full-project-final/authoring.jsonl`, `stderr.log` and `exit.json`
to resume monitoring. Do not start another solve. Changed runtime fingerprints correctly
invalidate old application prefixes; the final run rebuilds from the root. All 58 bone
stages are now accepted in 895.73 s of stage wall time (14 min 56 s). All four numerical
checkpoint files for every bone are byte-identical to v1. Native audits report zero
self-intersections, outside vertices, crossings and degenerate faces; radius guard
violations are zero, and maximum owned GPU bytes are 2,113,992,300 (below 2 GiB).
Forty of 265 muscle instances are accepted at this checkpoint. Final v2 package
verification passes all 8,536 file hashes/sizes and 1,166 isolated imports.

The normal GUI v1 control rebuilt the small bone-and-muscle document, reached current
state, saved `gui/generation-probe.anthroforge`, and was closed. It must be repeated for
the final runtime. The saved screenshot and accessibility evidence are in `gui/v1-generation.*`.

## Verification

Passed: native compilation, targeted policy tests, four successful parity/geometry/resource
cases and explicit insufficient-workspace rejection. Forty changed/test/harness functions
are within 15 physical lines (69 after orchestration/report/final-audit additions). Python static
checks, six native CTests, native style and PowerShell checks pass. The combined gate hit
the known absent worktree-local Qt SDK path; its remaining stages resumed using the
installed SDK explicitly. QML validation passes (187 files, 46 model types, zero API
errors). The full pytest run finished with 3,026 passes and one access violation from the
unchanged tetrahedralization subprocess in the X/INSTANT topology case. Its entire six-test
module passed when rerun separately (97.55 s); numerical import checks and native doctor
also pass. Do not describe the initial suite as clean or claim that dependency crash is
fixed. Pending: complete muscle qualification, fresh full-document validation, final GUI
generation, promotion and source archive verification.

## Next actions and blockers

1. Apply native contact changes against saved preimages and build the two packaged numerical workers.
2. Qualify representative stages and build a temporary complete portable package.
3. Run all bone and muscle stages through the app's real worker; analyze and resolve failures without skipping required stages.
4. Promote the qualified package and refresh the corresponding source archive.

## Recovery inputs

Full captured model input and prior diagnostics: `E:/development/anthroforge/build/avbd-full-muscles-001-20261127`.
Measured prototypes and reports: `build/avbd-performance-20261128` and `build/avbd-sleeping-optimized-20261128` in the main project directory.
Task artifacts and native preimages: `E:/development/anthroforge/build/avbd-release-20261128`.
Native compilation uses the existing CUDA 13.0 toolkit and VS 2019 Build Tools. Release packaging uses the existing app packaging tools and bundled Python environment.

The native checkout's earlier uncommitted runtime implementation is a local recovery dependency; do not claim it is backed up by an app-branch commit. The release source archive must retain the complete exact runtime source.
