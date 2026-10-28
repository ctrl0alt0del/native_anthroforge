# Cross-project anatomy assembly — confirmed 0.4.2 contract

Status: implementation in progress; not yet qualified.

## Workflow

File → Import Anatomy from Project loads a saved `.anthroforge` inventory asynchronously.
One searchable dialog selects anatomy/construction, shows required sources, and maps external
references. SCP selection includes descendants; Include attached tissues is optional. Required
curves, membranes, controls, junction participants and resources are copied once. Supports and
other consumers are not implicitly imported. Import creates independent editable identities
with source document/entity/revision/package provenance; the source remains untouched.

Preserve source world placement. A populated destination requires an SCP parent; suggest the
selected SCP or root. In an empty destination, one root establishes the hierarchy; multiple
roots receive an empty grouping root. Construction alone needs no SCP. Excluded ordinary
parents/Hook-follow targets must be mapped, included, or explicitly detached to world.

External references offer Map, Include, and (where valid) Resolve later. Use names only for
searching. Suggest unambiguous provenance matches without silently authorizing them. Retain
bindings only after verified material correspondence. Explicit Rebind prepares existing
confirmed exterior/current-shape capture and shows original/proposed locations and errors.
No automatic anatomical fitting or role substitution. One Import action and one undo step;
no extra mandatory Preview/Accept. Preparation follows edits automatically in a stable footer.

Unresolved references persist, remain visible through Issues/Resolve references, and block
only affected calculations. Retain source geometry for display without presenting it as a
current successful result. Repair uses the same mapping/capture policy and coherent undo.

## Relationships and boundaries

Copy SCPs, tissues, Points/Anchors, Curves/Fibers, Surfaces/Membranes, selected images,
shared controls/deformers/junctions, related shortcuts/drivers, mirror rules and owned assets.
Preserve internal sharing and inherited mirror behavior through explicit boundary rules.
Keep external driver outputs disabled until explicitly mapped and enabled; never overwrite
an existing formula. Preserve types, dimensions, material roles and component ownership.

Exclude source skin, fitted bone solutions, workspaces/bookmarks, undo history and active jobs.
No live project link, synchronization, Blender conversion, or geometry algorithm changes.
Destination global state remains authoritative; existing dependency/update policies apply.

## Ownership and implementation

Core owns immutable provenance/external references and relationship invariants. Typed adapters
enumerate owned identities, construction dependencies, relationships, resources and remapping;
no recursive string replacement. Application owns selective package loading, selection closure,
mapping/compatibility, transactions and result readiness. C++ owns numerical transforms,
correspondence and attachment queries through existing kernels. Desktop presents these same
operations with shared controls, virtualized lists, keyboard routing and staged previews.

Use the existing coordinator and authored publication contracts. Pin a source snapshot;
validate the complete destination read set, allow unrelated edits, reject stale candidates.
Cancel/failure leaves no partial graph. Load only required assets, retain owned metadata and
resource leases through preparation/history/display, and release discarded source resources.

Schema 8 reads schemas 4–7 and saves provenance/unresolved references, never native handles or
transient sessions. Assets remain self-contained after deleting/moving the source project.
Operations: assembly.inspect, prepare, status, cancel, import, references and resolve.

## Delivery sequence and acceptance

1. Typed reference/provenance/readiness foundations, schema and contract tests.
2. Complete graph copying, resource transfer and existing-copy integration.
3. External mapping/rebinding, mirrors, drivers and lifecycle.
4. Desktop import/repair workflow and interaction inspection.
5. Production comparisons, profiler, development gate, portable qualification and docs.

Require shared-source and subclass fidelity; repeated independent imports; exact unchanged
internal geometry/bindings; explicit incompatible-material repair; ordinary-parent and actual
dependency cycles; missing references and recovery; source/destination safety; cancellation,
stale inputs, undo/redo/historical saves; schema/asset portability; large searchable lists;
96-muscle-to-skeleton mapped import and matching shortcut responses; hooks/lattices and
construction-only fixtures. Record offscreen limits and separate ownership/coupling review.

Deliver one `dist/0.4.2/AnthroForge.dist` and `dist/AnthroForge-0.4.2-source.zip` after checks.
