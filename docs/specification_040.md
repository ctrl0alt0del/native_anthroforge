# AnthroForge 0.4.0 — Skin

Status: **Confirmed; implementation in progress, not release-qualified**.

## Authority and scope

Migrate the existing addon workflow before improving algorithms. The
[source inventory](skin_040_inventory.md) defines the audited settings, numerical
behavior, source owners and known limitations. Include envelope construction,
collagen/gaps, guided quad topology, persistent final-skin deformation, shortcut bone
fitting, independent fit preview and OBJ export. The [implementation plan](implementation_040.md)
defines delivery and acceptance. Source inspection is not geometry acceptance.

One document-owned skin system follows the anatomical root, including partial anatomy.
Selection, visibility and narrowed workspaces do not change contributors. Capture SCPs,
final tissues, applicable Fibers and reflected instances by stable identity. Exclude
controls, tissue bases and skin itself. Suppress a Fiber represented by a valid consuming
tissue; shared consumers must not duplicate its contribution.

## Construction and deformation

Preserve addon model-relative distance/collagen/gap settings; Auto/Uniform/Painted collagen;
paint/fill/clear; contributor gap overrides and contact-versus-bridge predicates. Preserve
the scalar fallback with an Issue when painted membership no longer matches geometry.

QuadWild Muscle FLOW + Paths is default, Instant Meshes an explicit alternative. Preserve
8,100 target quads, hierarchical budgets, loop patches, FLOW guides, adaptive refinement,
muscle proximity and symmetry. Counts remain targets. No silent backend substitution.

Separate accepted envelope, quad construction, immutable deformation reference and current
final skin. Reference contains connectivity/vertex identities, tetrahedral proxy, embeddings,
anatomical/material references and symmetry. Linear Elasticity is default; FAST reduced ARAP
is selectable. Compatible updates change positions only. Construction settings mark output
stale and require explicit rebuild; shortcuts do not silently remesh.

Retain accepted output on cancellation, malformed results, missing dependencies or failed
computation. Preserve the addon's usable-result quality-warning policy, including open seams,
contact findings and iteration limits. Do not claim watertightness or complete collision safety.
Publish replacement reference/construction atomically. If first reference preparation fails,
retain usable topology for retry, explicitly incomplete. Incompatible material/contributor
identity requires rebuilding/reinitializing, never silent nearest-surface reassignment.

## Fitted shortcuts

Fit one continuous scalar float shortcut at a time, with others held at captured values.
Default four bones (1–64), nine samples (odd, 5–33), increasing range. Preserve actual shortcut
attachment policies in isolated sampling. Retain training/held-out validation, determinism
checks, scale-aware fitting and four influences per vertex. Single Active stays authoring-only.
No automatic minimal-bone search, anatomical joint inference or multi-shortcut composition.

Persist independent fitted results, reference mesh, weights, transforms, sampled control
mapping and diagnostics without replacing editable anatomy. Preview must reproduce addon
playback interpolation and clamp outside the sampled range without rerunning anatomy.
Source changes mark fits stale without destroying their snapshot; refitting is explicit.

## Interaction, persistence and export

Right inspector navigation becomes a vertical strip on its left edge: Shape / Shortcuts /
Inspect / Skin. Skin is document-level; selection changes do not leave it. Keep existing editors,
drafts and focus conventions. Provide focused envelope/topology/deformation/fits/export sections,
direct Build Skin & Topology, individual stage/retry actions and contextual contributor settings.
Use existing painting, numerical controls, Activity and Issues. Transient status never shifts fields.

Schema 7 reads schemas 4–6 with empty skin state and unchanged existing anatomy, attachments,
accepted results and startup behavior. Save durable skin and fit data belonging to the selected
revision, not native handles, undo history or disposable solver caches. No blanket recalculation
on open. Preserve existing update modes, cancellation, undo and blocked-save semantics.

OBJ is the first writer behind an extensible export interface. Export a frozen skin snapshot,
preserving polygons/quads in metres/application axes, without anatomy/debug objects. OBJ does
not carry fitted bones, weights or drivers; these remain in the project. Stale/pending export
offers Last accepted, Update/Rebuild and export, or Cancel. Headless callers specify that policy.
Update-and-export freezes the requested input revision; subsequent edits cannot silently change
the output. Write atomically. No final skin means no final-skin export.

## Boundaries

Keep C++ numerical preparation/optimization and Python orchestration; no Blender dependency,
Python optimizer fallback, duplicate coordinator or per-iteration callbacks. Preserve mirrored
geometry rules, resource ownership and current selection/editing restrictions. Legacy Blender
project conversion, general animation editing and new skin algorithms remain separate tasks.

## Confirmed contributor clarification

The October 26 correction requires the actual pinned Blender Decimate/BMesh subset for
proxy simplification and symmetry cutting, rather than approximate replacement algorithms.
The accepted standalone differences are instance-aware density ownership and deterministic
ties, accepted material charts and compatible surface-tissue guidance/refinement, bare-Fiber
centerlines, and native spatial/intersection queries. Their recorded qualification gaps remain
required work. No additional algorithm changes are authorized without prior discussion.

Production backend execution must not fail solely because it exceeds an arbitrary runtime,
fixed 4 GiB ceiling or retained-log size. Retain cancellation, owned process lifetime and real
backend/allocation failures. Use scheduling/admission for resource coordination and bounded
log retention without terminating the computation. Preserve source numerical thread settings.

Bare Fibers contribute their accepted **centerlines only**. Neither workspace display
thickness nor an invented skin-specific fiber radius enters skin construction. Capture
uses explicit segments and retains path/segment correspondence separately from surface
triangle bindings. This intentionally differs from the addon's evaluated bevel meshes.
Fibers represented by an accepted tissue remain suppressed under the existing source policy.
