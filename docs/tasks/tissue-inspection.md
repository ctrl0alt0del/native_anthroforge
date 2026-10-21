# Tissue stages, constraint explanation and spatial findings

- Task branch: `codex/tissue-inspection`
- Integration branch: `main`
- Starting revision: `118a13499a8515f9a92940b80a8daecd8c14c1d4`
- Status: complete; qualified for main
- Last updated: 2026-10-21, Europe/Bucharest
- Active writer: desktop chat, direct work

## Outcome and acceptance

Implement recommendations E03/F11 (accepted tissue stage comparison), E04/F05
(point-level material/constraint explanation), and G01/F10 (locatable advisory
geometry findings). Desktop and headless inspection use shared revision-qualified
operations. Inflation, smoothing, attachment and stacking algorithms remain unchanged.
Self-intersections stay allowed. User chose on-demand **Check geometry**; no automatic
expensive scans on geometry updates. Stale evidence must be explicit.

## Decisions and relevant files

Use existing native mesh/material data, accepted stage results, scene publication,
native picking, issue repository and snapshot reports. New repeated numerical work
belongs in C++, with owned inputs and cooperative cancellation. Inspection presentation
must not mutate anatomy, undo or accepted output. Stage comparisons must not imply
correspondence across incompatible samples or input revisions. Reuse Ui controls and
keep transient messages out of changing layouts. Reference: docs/specification_022.md,
docs/engineering_guidelines.md, standalone_application_recommendations.md E03/E04/F05/F11/G01.

## Current state

Native material comparison/colored buffers, point/region lookup and bounded advisory
crossing checks are integrated with the shared API and desktop inspectors. Stage buffers
use frame-boundary activation with retained buffer types and matching picking. Point
inspection explains accepted constraints and draws surface/displacement witnesses.
Findings locate triangles and become stale without automatic reruns. Frozen report views
and profiler ownership include inspection resources. 26 focused tests pass, including
real crossing fixtures, cropped material mapping, exact backing and publication lifetime.
Dedicated offscreen UI and hidden GPU inspection pass, including frozen report replay.
Actual images were reviewed; frame-box conversion and occluded witness visibility were
corrected. The final full gate passes all 1,557 tests. The relocated canonical package
passes the complete portable suite, including frozen comparison/point report replay.
Documentation, computation history and the separate ownership review are complete.

## Verification

`tools/check.ps1` passes: 1,557 tests, five native contracts, typing of 296 modules,
lint/format, native/script function limits, numerical checks and native runtime doctor.
The initial architecture/capture-harness failures were corrected before this final run.
Offscreen controls, hidden GPU scene checks and the entire minimal-PATH portable suite
pass. The unrelated root `__init__.py` is preserved.

## Delivery

One canonical `dist/0.2.3/AnthroForge.dist` and companion
`dist/AnthroForge-0.2.3-source.zip`; runtime source is
`0561d8718986573a37fd31d1d7a10c737bcd4971`, with subsequent documentation-only commits.
Executable SHA-256: `A0FEF1175EF61FD906D5150474396F4569092C7E460C0FEBDDCFAA194E16AF3D`.
No unfinished implementation remains. Interactive physical desktop acceptance was not
performed; all GUI evidence was obtained in the background.

The interruption stopped the final gate during pytest and the package during Nuitka.
Both were restarted from pushed checkpoint `0561d8718986573a37fd31d1d7a10c737bcd4971`.
The resumed offscreen control test and hidden GPU/report replay both pass. Inspector
text/layout and the crossing-face guides were visually reviewed with Windows fonts
available to the offscreen platform. The restarted build replaces the previous executable.

## Ownership review

Direct review, separate from test results: numerical comparison, material interpolation,
region influence and triangle checks live in native code. Shared application operations
own frozen inputs and revision checks; the existing coordinator owns cancellation and
read-only job lifetime. The existing Issues provider contract now distinguishes requested
checks from automatic checks. Desktop adapters own view state and replay, never anatomy.
Staged rows retain their buffer type, frame and picking resource together; the shared
geometry-model list includes inspection during draining, activation and resource accounting.
No extra worker pool, document revision stream or numerical Python fallback was introduced.
The native findings adapter shares the existing stacking translation unit because its
internal geometry helpers are not separately linkable; the exported query stays narrow.

## Current evidence

`tools/tissue_inspection_ui.py` exercises direct controls with the offscreen platform.
`tools/tissue_inspection_scene.py` uses a hidden QQuickRenderControl window, verifies
native buffer switching, point guides, advisory crossings and matched report replay.
Captures and `.afinspection.zip`/`.afprofile.zip` are under `build/tissue-inspection`.
The latest small workload measured comparison 0.219 ms, point query 0.613 ms and
geometry scan 4.618 ms at native boundaries. These include profiler perturbation and
do not establish application latency or large-assembly performance. No physical
display/interactive desktop acceptance was performed.

Profiler review exposed repeated idle stage preparation. Revision/job/Issue-driven
projection now reuses the unchanged view; a test verifies 100 idle synchronization
calls perform no additional preparation. Native matrix calls in the recorded scripted
workload decreased from 862 to 244; this is call-count evidence, not a frame-time claim.
Switching stages also clears point evidence from the previous stage. Inspection buffers
and retained input meshes appear in profiler ownership without double-counting allocations.

## Recovery inputs

Windows checkout E:/development/anthroforge; normal tools/common.ps1 environment.
Keep all generated test evidence in ignored build/tissue-inspection.
