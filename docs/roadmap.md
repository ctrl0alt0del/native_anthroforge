# AnthroForge release roadmap

- **0.4.2 — selected inspection extensions:** R01–R03 and R06 from the
  [complete recommendation audit](recommendations_042_audit.md): shared replacement status,
  spatial findings, placement explanation, dimensions/sections and temporary neighborhood
  inspection. [Workflow and limits](inspection_042.md), [qualification](tasks/inspection-workflows-042.md).
  Other audit entries remain unselected.

- **0.4.1 — qualified skin audit corrections:** restore draft-based
  reference preparation, final diagnostics, achieved topology budgets, persistent FAST
  weights, effective inherited settings, envelope reset and moving-region fit summaries.
  See [scope and evidence](tasks/release-041.md) and [workflow](skin_workflow.md).

- **Status-provider direction — replacement integration in 0.4.2:** extend shared,
  operation-specific status providers to other functionality whose UI currently derives
  readiness, warnings or availability from workspace/document state. Inventory existing
  consumers and reuse their notifications and shared policies; do not introduce global
  polling or a universal status manager. The pattern starts with SkinStatusProvider in
  0.4.0. [Architecture](architecture.md#shared-operation-status-providers),
  [initial inventory](tasks/release-041.md). This refactoring is not included in 0.4.1.

- **0.4.0 — qualified with accepted quality limits:** migrates the addon's skin envelope,
  guided topology, final-skin updates and shortcut-to-bone fitting. Reproduce existing
  addon behavior first; behavioral improvements follow the qualified migration. OBJ is the first
  exporter behind an extensible format interface. Skin joins the existing right
  inspector's tabs, arranged vertically. The [source inventory](skin_040_inventory.md)
  separates current behavior from legacy update paths and records local fitting source; see
  [the task record](tasks/skin-040.md). Implementation follows the confirmed
  [specification](specification_040.md) and [delivery plan](implementation_040.md).
  The October 27 review restricts draft/deformation sources to SCP/VCP surfaces while
  preserving topology guides, completes one-action Build Skin, places bone fitting in
  shortcut settings and adds shared SkinStatusProvider readiness. These review changes
  are implemented and pass the complete portable checks. The full-body draft matches
  the addon exactly, including accepted banding/non-manifold findings documented in the
  task record. No wider status-provider migration is included.

- **0.3.7 — qualified:** recent projects, periodic committed recovery
  copies and UI polish. [Walkthrough](usability_037.md), [evidence](tasks/usability-037.md).

- **0.3.6 — qualified:** integrates the preserved 0.3.4
  D01–D12 workflows and retained-owner attachment corrections with mirroring and smooth
  propagation. No source-project migration or exact welded-Ribs parity claim.
  [Walkthrough](workflows_036.md), [delivery evidence](tasks/workflows-036.md).

- **0.3.5 — qualified:** strict source-linked, read-only mirroring,
  hierarchy rules, instance-aware surfaces and symmetric construction. Mirrors never
  solve independent geometry. [Specification](specification_035.md),
  [implementation plan](implementation_035.md), [runtime/evidence](mirroring_035.md).
  Schema 6 reads 4/5/6 without reflected payload duplication. Existing independent
  counterpart migration remained untouched; the preserved 0.3.4 work is integrated in 0.3.6.

- **0.3.3 — qualified:** targeted shortcut metadata/formula observation, immutable
  publication and incremental priority links. [Evidence](shortcuts_033.md).
  This preserves standalone behavior; [addon parity findings](addon_parity_findings.md)
  remain unresolved. The [functionality audit](addon_functionality_audit.md) records
  smaller gaps separately from deferred major systems; it is not a release commitment.

- **0.3.2 — qualified:** shortcut baselines, Before/After/Overlay inspection, paired
  reports and optional isolated replay. [Walkthrough](shortcuts_032.md).

- **0.3.1 — qualified:** shortcut influence, formula evidence, effective
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
- **Later releases:** legacy Blender conversion, anatomical
  reconstruction/fitting and other explicitly deferred workflows. No version or
  completion date is assigned here. General physical simulation is not a 0.2.2 goal.

Historical release records remain evidence of their own tested revisions. A confirmed
specification or roadmap entry does not establish implementation or release acceptance.
