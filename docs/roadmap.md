# AnthroForge release roadmap

- **0.3.1 — qualification in progress:** shortcut influence, formula evidence, effective
  attachment inspection and downstream propagation status; optional displayed-geometry
  effects. [Walkthrough](shortcuts_031.md), [qualification](tasks/shortcut-inspection-031.md).
  Schema 5, geometry and attachment behavior remain unchanged.

- **0.3 / 0.3.0 — qualified:** numerical-property shortcut wrappers,
  explicit controls, driving formulas with inferred ownership and addon attachment-edit
  policies, and the Parametric curve engine. [Contract](specification_030.md),
  [implementation plan](implementation_030.md), [review state](tasks/shortcuts-parametric-030.md).
  Schema 5 includes a reader for
  existing 0.2.4/schema-4 projects; source Blender shortcut migration is separate.

- **0.2.4 — qualified baseline:** VCP preparation, collision/stacking reuse and height
  smoothing performance work, preserving geometry/attachments and schema 4.
  [Measurements and validation](performance_024.md).

- **0.2.3 — qualified:** Preferences and per-job Custom/sparse PIQP
  ROUTED choice, future calculations only. [Contract](specification_023.md),
  [delivery evidence](tasks/preferences-routing-023.md). Schema 4 remains unchanged.
  Confirmed placement also [reuses qualified original geometry](tasks/confirmed-query-reuse.md).

- **0.2.0 / 0.2.1 — qualified baseline:** curves, fibers, surfaces, images and editing
  improvements. See [0.2.0](specification_020.md), [0.2.1](specification_021.md) and
  [observed validation](development_status.md).
- **0.2.2 — qualified:** unified tissues, attached construction, native inflation,
  relaxation and surface-based stacking. [Contract](specification_022.md),
  [implementation plan](implementation_022.md), [task](tasks/unified-tissues-022.md).
  Canonical package evidence is recorded with [release validation](development_status.md#unified-tissues-022).
- **Later releases:** mirroring, skin, legacy Blender conversion, anatomical
  reconstruction/fitting and other explicitly deferred workflows. No version or
  completion date is assigned here. General physical simulation is not a 0.2.2 goal.

Historical release records remain evidence of their own tested revisions. A confirmed
specification or roadmap entry does not establish implementation or release acceptance.
