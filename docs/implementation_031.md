# Shortcut inspection 0.3.1 implementation

Status: in progress; not release-qualified.

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
