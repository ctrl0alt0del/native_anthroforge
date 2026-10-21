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

Inspected current contracts and official Qt custom geometry/libigl geometry-query APIs.
Accepted tissue stages and material provenance exist; point explanation and spatial
tissue findings are missing. Beginning native/application and presentation integration.

## Verification

Not yet run. Required: native/API contracts, stale/cancel/resource lifecycle, tissue
shape fixtures, offscreen UI/render capture inspection, full development gate and
canonical 0.2.3 package qualification. Preserve unrelated root __init__.py.

## Next actions and blockers

1. Integrate revision-qualified stage and point inspection with native comparison.
2. Add on-demand geometry checks, issue witnesses and viewport navigation.
3. Validate, document, package one canonical build, checkpoint and merge.

## Recovery inputs

Windows checkout E:/development/anthroforge; normal tools/common.ps1 environment.
Keep all generated test evidence in ignored build/tissue-inspection.
