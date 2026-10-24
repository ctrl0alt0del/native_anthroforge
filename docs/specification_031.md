# AnthroForge 0.3.1: shortcut inspection

Implemented and qualified in 0.3.1 (2026-10-24). This release implements
influence inspection, formula evidence, effective attachment policies and propagation
feedback. It does not change geometry or attachment behavior. Ribs/Thumb parity defects
remain deferred. Comparison and report extensions are deferred; their future defaults
are explicit baseline capture and optional replay data.

## Product behavior

Keep Selected SCP/VCP and All tabs. Inspect opens the existing shortcut editor and keeps
its value editable. Collapsible sections expose affected anatomy, numerical formula
evidence, attachment effects and update details. Show effects is explicit and off by default.
Overlays are non-pickable and never alter selection, visibility, anatomy or workspace scope.

Potential dependency influence differs from outputs published by an edit and from actual
spatial movement. Show direct targets, downstream consumers and outside-workspace context.
Show current input values separately from captured evaluation values, types, units,
accepted outputs, failures and causal prerequisites. Missing historical evidence is unavailable.

Show authored policies separately from effective initiating-shortcut policies. Retained
bindings and owner backsolve are distinct. Prospective overrides do not invent captured
anchors. Native anchor queries are read-only and revision-qualified.

Status distinguishes updating, waiting for release, waiting for Manual calculation,
failed/retained results, complete, cancelled and superseded. Formula completion is not
downstream completion. Desktop distinguishes computation readiness from staged display;
headless status makes no display claims. Transient feedback cannot move numeric fields.

## Ownership and persistence

Shared commands read the authoritative dependency graph and accepted results. Runtime
observation never controls scheduling, save eligibility, attachment policy or undo.
Geometry queries remain native; read-only jobs use the existing coordinator. No geometry
snapshots or compiled expressions are retained for inspection. Evidence is bounded and
discarded on document replacement. Schema 5 and existing loading behavior remain intact.

## Acceptance

See [implementation and qualification](implementation_031.md). Inspection must leave
geometry, poses, bindings, document revisions and undo intact. Release acceptance requires
actual render inspection, production comparisons, profiling and portable qualification.
These checks passed with background/offscreen evidence; physical interactive acceptance
is not claimed. See the [release evidence](tasks/shortcut-inspection-031.md).
