# Tissue stages, constraint explanation and spatial findings

- Task branch: `codex/tissue-inspection`
- Integration branch: `main`
- Starting revision: `118a13499a8515f9a92940b80a8daecd8c14c1d4`
- Status: in progress
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
Existing offscreen editor acceptance passes. Dedicated GPU inspection, wider lifecycle
tests, full development gate, documentation and packaging remain incomplete.

## Verification

Passed build-native.ps1 and 13 tests in test_tissue_inspection.py/test_issue_lifecycle.py.
Required: extended native/API contracts, stale/cancel/resource lifecycle, tissue
shape fixtures, offscreen UI/render capture inspection, full development gate and
canonical 0.2.3 package qualification. Preserve unrelated root __init__.py.

## Next actions and blockers

1. Complete dedicated hidden GPU inspection and report replay acceptance.
2. Complete lifecycle/resource tests, full development gate and computation history.
3. Package one canonical build, checkpoint and validated merge.

## Recovery inputs

Windows checkout E:/development/anthroforge; normal tools/common.ps1 environment.
Keep all generated test evidence in ignored build/tissue-inspection.
