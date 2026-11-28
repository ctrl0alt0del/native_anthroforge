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

- D1 — Confirmed by user: no dynamic sleeping, inherited sleeping, geometric activity masks, or vertex elimination in production. Keep all existing skin vertices active.
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

## Verification

Passed: native compilation, targeted policy tests, four successful parity/geometry/resource
cases and explicit insufficient-workspace rejection. Forty changed/test/harness functions
are within 15 physical lines. Pending: complete document through Authoring, application
development gate, clean-environment bundle verification, normal GUI launch, promotion and
source archive verification.

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
