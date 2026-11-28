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

No production kernel changes or complete-project build have yet been qualified in this task. Existing application and native runtime work must remain intact during implementation.

## Verification

Pending: targeted native policy tests, parity and resource checks, complete document through Authoring, representative app regression tests, clean-environment bundled-runtime verification, normal GUI launch, release promotion and source archive verification.

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
