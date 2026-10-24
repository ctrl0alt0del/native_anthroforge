# Shortcut inspection 0.3.1 implementation

Status: implemented and qualified in 0.3.1, 2026-10-24.

1. Shared inspection reads property catalogue, formula index and dependency graph.
   `shortcut.effects`, `.formulas`, `.attachment_policy`, `.progress` accept stable IDs.
   Existing APIs stay compatible. Tests cover observational purity, cycles, evidence,
   pagination, missing identities and attachment retention.
2. Runtime causal evidence observes shortcut gestures, queue/coalescing, publication and
   dependent work. It is separate from retained attachment contexts and never changes
   job priorities, cancellation or numerical execution. Keep active and latest records.
3. Desktop adds focused inspection to the existing editor and fixed-size status to rows.
   Native anchor overlays use owned read-only inputs and match displayed revisions.
4. Qualification covers Live/On Release/Manual, cancellation/supersession/undo, large
   assemblies, frame/layout stability, native geometry preservation, headless and portable.

Follow engineering guidelines and function limits. Record any changed computation or
cache boundary in computation_history.md. Only after full qualification update release
version and deliver dist/0.3.1/AnthroForge.dist plus companion source archive.

## Delivered ownership

- Application inspection modules own influence, formula evidence, policy explanation and
  readiness queries. They reuse the dependency graph and accepted output contracts.
- Session-owned observation stores bounded causal evidence. The coordinator emits lifecycle
  events; observation cannot admit, prioritize or publish anatomical calculations.
- Native attachment queries run in the existing cancellable read-only query service.
  Captured initiating policies remain owned by the existing shortcut edit contexts.
- Desktop adapters own incremental models, fixed-height status and non-pickable effects.
  Optional mask scenes share existing native results through viewport resource leases.

## Qualification

The development gate passed; the final suite passes 2,026 tests, all five native CTests,
configured strict typing (375 modules), style and numerical checks. Source-runtime
offscreen editor tests and texture-only D3D11 captures verify stable value-field bounds,
downstream outlines and anchor pairs. A relocated executable with a temporary QML test
harness verifies the compiled inspection adapter and visible editor without modifying
the canonical package. Full portable workflows pass under minimal PATH.

Production comparisons against `00e7339` cover Ribs Top Radius=3, Humerus length, Radius
length and Thumb thickness on the 96-muscle assembly. Vertices, poses, bindings and
oriented connectivity are unchanged; Thumb triangle enumeration differs without a
connectivity change. Inspection queries measured 3.54–8.32 ms combined median across
these cases. These instrumented, non-isolated timings establish no speed improvement.

Ownership/coupling was reviewed separately from tests. No second scheduler, numerical
fallback, geometry snapshot store, attachment policy owner or schema change was added.
Full evidence and limits: [recovery/release record](tasks/shortcut-inspection-031.md).
