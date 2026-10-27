# AnthroForge 0.4.0 — Skin

Status: **Confirmed; implementation in progress, not release-qualified**.

October 27 review: the contributor, fitting-readiness and status-provider decisions below
are confirmed but not yet implemented. Runtime work remains paused pending the final
consolidated review; existing feature-branch behavior is not evidence of these changes.

## Authority and scope

Migrate the existing addon workflow before improving algorithms. The
[source inventory](skin_040_inventory.md) defines the audited settings, numerical
behavior, source owners and known limitations. Include envelope construction,
collagen/gaps, guided quad topology, persistent final-skin deformation, shortcut bone
fitting, independent fit preview and OBJ export. The [implementation plan](implementation_040.md)
defines delivery and acceptance. Source inspection is not geometry acceptance.

One document-owned skin system follows the anatomical root, including partial anatomy.
Selection, visibility and narrowed workspaces do not change contributors. Capture SCPs,
final tissues and their reflected instances by stable identity. Only SCP/VCP surfaces
contribute to draft skin. Exclude construction objects, controls, tissue bases and skin
itself; never substitute bare Fibers for missing tissue geometry. Construction references
remain upstream dependencies of the anatomy they build, not additional physical sources.

## Construction and deformation

Preserve addon model-relative distance/collagen/gap settings; Auto/Uniform/Painted collagen;
paint/fill/clear; contributor gap overrides and contact-versus-bridge predicates. Preserve
the scalar fallback with an Issue when painted membership no longer matches geometry.

QuadWild Muscle FLOW + Paths is default, Instant Meshes an explicit alternative. Preserve
8,100 target quads, hierarchical budgets, loop patches, FLOW guides, adaptive refinement,
muscle proximity and symmetry. Counts remain targets. No silent backend substitution.

Draft generation defines the surface; topology generation lays topology onto that surface.
The draft-source exclusion does not remove the addon's Fiber/curve topology guidance.
Keep loop/FLOW guide behavior distinct from physical contributors. Guides are evaluated
during construction or an explicit rebuild, not as independent deformation supports.

Separate accepted envelope, quad construction, immutable deformation reference and current
final skin. Reference contains connectivity/vertex identities, tetrahedral proxy, embeddings,
anatomical/material references and symmetry. Linear Elasticity is default; FAST reduced ARAP
is selectable. Compatible updates change positions only. Construction settings mark output
stale and require explicit rebuild; shortcuts do not silently remesh.
Ordinary updates, including every bone-fitting sample, preserve skin vertex count,
vertex identities, order and connectivity. SCP/VCP surfaces drive these position updates;
guide changes must not trigger automatic retopology. Construction edits can still affect
skin indirectly through their consuming SCPs/VCPs.

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

Expose a **Fit to bones...** button alongside the selected shortcut's settings, such as
attachment overrides; do not put it only in a context menu. The Skin panel manages saved
fits, independent preview, refitting and removal. Preview does not modify authored anatomy.
There is no combined Build Skin and Fit action. Without a finished skin and usable reference,
disable fitting with a tooltip explaining what is missing.

Distinguish unapplied construction settings from an incompatible deformation reference.
If the existing skin/reference remains usable, allow fitting with a warning icon and tooltip
that the fit uses the existing skin, not unapplied build settings. If contributor/material
references or skin identities/connectivity are incompatible, disable the button with an
explanatory tooltip; do not use a warning icon as a substitute for blocking the invalid action.
Validate every captured sample and its reference provenance. Never replace a failed sample
with an old mesh; initial eligibility does not guarantee success over the requested range.

## Interaction, persistence and export

Right inspector navigation becomes a vertical strip on its left edge: Shape / Shortcuts /
Inspect / Skin. Skin is document-level; selection changes do not leave it. Keep existing editors,
drafts and focus conventions. Provide focused envelope/topology/deformation/fits/export sections,
one **Build Skin** action, individual stage/retry actions and contextual contributor settings.
Build Skin runs draft generation, topology generation and reference preparation, ending with
usable deformable skin. If a later stage fails, retain valid intermediate results and offer
a retry without unnecessarily rebuilding completed stages. Existing output remains protected.
Use existing painting, numerical controls, Activity and Issues. Transient status never shifts fields.

### Shared skin status (confirmed, not yet implemented)

Implement an application-owned, Qt-independent **SkinStatusProvider** for 0.4.0. It exposes
readiness per operation (including update, fitting and export), blocking reasons, advisory
warnings and the skin/reference revisions assessed. A single global valid/stale flag is
insufficient: outdated settings can coexist with a usable accepted reference.

Skin and shortcut UI consumers subscribe through the existing document-change infrastructure.
Application/headless operations enforce the same assessment and revalidate relevant inputs at
execution. Status reads and notifications do not poll, schedule computation, mutate document
state or change undo/checkpoints. Desktop adapters present tooltips/icons and button state;
they do not duplicate eligibility rules.

Extending this pattern to other functionality whose UI reads workspace-dependent status is
planned for the **next version after 0.4.0**, not part of this release. See the
[roadmap](roadmap.md) and [architecture](architecture.md#shared-operation-status-providers).

### Persistence and export

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
ties, accepted material charts and compatible surface-tissue guidance/refinement, and
native spatial/intersection queries. Their recorded qualification gaps remain
required work. No additional algorithm changes are authorized without prior discussion.

Production backend execution must not fail solely because it exceeds an arbitrary runtime,
fixed 4 GiB ceiling or retained-log size. Retain cancellation, owned process lifetime and real
backend/allocation failures. Use scheduling/admission for resource coordination and bounded
log retention without terminating the computation. Preserve source numerical thread settings.
The addon's sparse-field working budget is not a total-process or output-mesh ceiling.
Do not subtract all retained resources and impose a new estimated assembly-size rejection;
retain the source field-storage controls and genuine allocation-failure handling.

The later October 27 interview supersedes both centerline-only and thin-tube contribution:
bare Fibers do not contribute physical skin geometry or independent deformation support.
The current thin-tube implementation and measurements remain historical implementation
evidence until the planned capture change lands; no replacement area-weighting algorithm
is required for excluded sources. Topology paths remain separate and must not be removed
with the physical-source capture. Workspace Fiber display thickness remains unrelated.

| Superseded proposal/behavior | Confirmed behavior |
| --- | --- |
| Bare Fibers contribute centerlines or thin tubes | Draft skin uses only SCP/VCP surfaces. |
| Excluding draft contributors also removes construction guidance | Preserve the addon's topology-guide behavior in the topology stage. |
| Main build stops after topology | Build Skin includes reference preparation; individual retries remain. |
| Fitting starts only from a shortcut context menu | A button lives alongside the shortcut's other settings. |
| Build Skin and Fit when no skin exists | Disable Fit with an explanatory tooltip. |
| Any stale construction flag disables fitting | Warn when the existing reference is usable; block actual incompatibility. |
| UI consumers derive their own skin eligibility | SkinStatusProvider owns shared, operation-specific assessment. |
| Broad status-provider migration in 0.4.0 | Skin only now; other functionality in the next version. |
