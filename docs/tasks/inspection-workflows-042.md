# 0.4.2 status, diagnostics, placement and inspection workflows

- Task branch: `codex/inspection-workflows-042`
- Integration branch: `main`
- Starting revision: `44a80ab` (qualified 0.4.1 plus recommendation audit)
- Status: in progress
- Updated: 2026-10-28, Europe/Bucharest
- Active writer: local desktop chat, direct work; no delegation

## Outcome and acceptance

The user selected audit items R01, R02, R03 and R06 for implementation. Deliver shared
operation status assessments, spatial findings beyond tissues, placement explanation
and recovery, and more useful anatomical inspection views/measurements. Preserve all
existing geometry, attachment, skin and solver algorithms. Numerical diagnostics run
in C++ on owned inputs. New diagnostics are advisory, bounded and revision-aware;
expensive checks remain on demand. Do not repair self-intersections or change placement.

Use existing Issues, task coordination, native query/inspection services, presentation
and API contracts. Extend owning boundaries rather than adding parallel systems.
Keep testing background/offscreen; no desktop control. Preserve root `__init__.py`.

## Decisions and investigation

- Follow [audit scope](../recommendations_042_audit.md),
  [engineering guidelines](../engineering_guidelines.md), and
  [status-provider inventory](release-041.md).
- R01 begins with Change tissue source and Replace imported mesh: both API guards and
  UI consume the same read-only application eligibility. Reuse lifecycle/events.
- R02 preserves existing skin reports and tissue witnesses; introduce a shared
  spatial-evidence contract and route current consumers through it. Any additional
  containment/clearance measurement must declare method and invalid-input limits.
- R03 explains the existing qualified placement; do not select a new nearest surface
  or change stored bindings to improve a diagnostic result.
- R06 measurement scope and temporary neighborhood view behavior were asked through
  asynchronous questions; independent R01 work proceeds meanwhile.
- Official Qt model notification and CGAL predicate documentation consulted first.
  These guide integration; existing qualified native kernels remain authoritative.

## Current state

Initial inventory only. No production implementation or new validation completed.

## Verification

Pending targeted shared API/desktop tests, native diagnostic tests, geometry/attachment
invariance, development gate, offscreen visual evidence and canonical packaging.
Do not claim interactive desktop acceptance from hidden/offscreen checks.

## Next actions

1. Trace replacement assessment/guard/desktop refresh events and implement R01.
2. Establish shared spatial witness ownership and implement R02/R03/R06 integration.
3. Qualify complete desktop/headless workflows; document evidence and remaining limits.
4. Release one canonical 0.4.2 package only after acceptance, then validated merge/push.

The containing commit identifies the checkpoint; inspect Git history for push state.
