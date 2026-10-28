# Profile recommendations R09–R11

- Task branch: `codex/profile-cache-display-042`
- Integration branch: `main`
- Starting revision: `05fb548`
- Status: in progress
- Last updated: 2026-10-28, Europe/Bucharest
- Active writer: local Codex

## Outcome and acceptance

Profile aggregate cache retention, duplicate in-flight preparation and viewport
publication on the existing assembly. Distinguish observed costs from possible
optimizations; this request does not change production algorithms or release versions.
Keep project inputs unchanged and all desktop validation hidden/offscreen.

## Decisions and relevant files

- Scope: R09–R11 in [the audit](../recommendations_042_audit.md).
- Reuse runtime profiler, resource ownership and existing shortcut workload tooling.
- Qt's partial `QQuick3DGeometry` setters do not guarantee partial GPU uploads:
  <https://doc.qt.io/qt-6/qquick3dgeometry.html>.
- Hypotheses: caches may accumulate across edits; simultaneous cache misses may
  duplicate work; full render-buffer replacement may be expensive. None is proven yet.

## Current state

Reviewed cache/resource and rendering boundaries. Measurement tooling and trials pending.

## Verification

No new runtime measurements yet. No production behavior changes.

## Next actions and blockers

1. Instrument only experiment boundaries missing from existing traces.
2. Run representative serial trials, memory retention and hidden rendering checks.
3. Review evidence and prioritize recommendations; verify tools and documentation.

## Recovery inputs

- Production input: `E:/development/WIP_models/shortcut_migration_030_20261023/skeleton_96_muscles_shortcuts_v001.anthroforge`.
- Native build: `C:/Users/alexe/AppData/Local/Temp/anthroforge-skin-040-native`;
  set `ANTHROFORGE_NATIVE_LIBRARY` to its `bin/af_native.dll`.
- Keep outputs under ignored `build/cache-display-profile`; preserve root `__init__.py`.
