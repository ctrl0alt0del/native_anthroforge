# Authoring parity — 0.4.3

**Confirmed implementation contract — qualification pending.** Closes A1–A4 from
[the audit](authoring_audit_043.md). Recovery/project-library and feedback commands are
excluded. Existing document semantics, algorithms and schema 9 remain unchanged.

## Resolved editing state

`editing.inspect(target, category, context?, offset=0, limit=4096, expected_revision?)`
returns stable component references, resolved local/world positions and frame, position/
weight editing restrictions, topology locks, authored/accepted provenance and pending state.
Maximum page size is 16384. A supplied revision must match the complete query inputs.
Standalone/consumed curves, Fibers, Parametric points, junctions, controls, imported/base
membership points and tissue controls/fields use the same read service as the desktop.
Raw `object.inspect` remains authored data. Queries do not author, evaluate or resample curves.

## Candidate capture

`inspection.capture(kind, token)` freezes an existing completed current candidate and its
baseline/context. Adapters cover curve conversion, surface, tissue inflation, imported-mesh
replacement, tissue retarget, fitted-skin playback, skeleton update and variant review.
Only computed output stages are current; retained/unavailable stages remain explicit.

`inspection.capture.status`, `inspection.geometry`, and `inspection.release` manage one
API-held snapshot per session. Replacement releases the old slot; exports retain their
own leases. Frozen data survives subsequent source edits without mixing revisions. APIs
return local coordinates/frames, canonical connectivity and sampled paths/parameters,
with bounded pages and no native handles. Session teardown releases transient ownership.

`inspection.export` accepts a snapshot, geometry evidence and optional images. Extend the
existing renderer with an inspection-only scene bundle, without dummy document records or
applying candidates. Before/After/Overlay/Split share camera and filters. One atomic
`.afinspection.zip` contains versioned metadata, numerical buffers and optional images.
Numerical capture/export remains Qt-free. Images use the isolated desktop renderer;
failure retains the capture for retry and never publishes an incomplete archive.

## Contextual queries

Expose `assembly.mapping.targets/properties`, corresponding `skeleton_update.mapping.*`
(including destination-control remapping), `surface.options`, `skin.contributor.inspect`
and `skin.fit.refit.eligibility`. Queries use existing policies, stable identities,
readiness reasons and revision signatures. Mapping references are identified by current
preparation token/key, never client-invented descriptions. Desktop projections consume
the same services. Writes revalidate independently of earlier eligibility reads.

## JSON literal arguments

An optional request-level `literal_paths` array contains RFC 6901 pointers into arguments.
The pointed subtree bypasses `$result.path` substitution. Empty pointer means all arguments
literal. Validate pointer syntax and existence before invoking a document command.
Example: `{"operation":"scp.empty","arguments":{"name":"$pelvis","parent":"$root"},
"literal_paths":["/name"]}` keeps name literal and resolves parent. Existing requests and
direct Python commands retain their meaning. Errors identify the argument path.

## Delivery

Core owns immutable references/read records; application owns resolution, snapshots and
policies; native code retains numerical work; desktop owns rendering; transport owns
literal decoding. Reuse the coordinator, native buffers, caches, staged publication and
resource leases. No competing pool, timer or compulsory UI step. See
[task evidence](tasks/authoring-fixes-043.md) before considering any feature qualified.
