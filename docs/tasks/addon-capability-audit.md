# Addon capability and detail audit

- Branch: codex/addon-capability-audit; baseline: f0c1caf; integration: main.
- Request: preserve the shoulder/Thumb diagnosis in durable documentation, then audit
  implemented major workflows and smaller addon features missing within those workflows.
- Scope: source/API/desktop/test inspection and documentation. No production behavior,
  project, package-version or geometry changes. Preserve unrelated __init__.py and addon edits.
- Distinguish implemented behavior, API-only access, missing details, known fidelity
  defects and deliberately deferred major systems. Specifications alone are not proof.
- Source addon has unrelated local bone-fitting work; label it separately from established
  addon functionality. No addon Git operations or edits are needed.
- No visible desktop interaction or delegation. Status: documentation and audit complete.

## Delivery

- Durable diagnosis: [addon parity findings](../addon_parity_findings.md), linked from
  README, architecture, development status, API and roadmap. Shoulder frame fidelity,
  effective Thumb policy and Boolean child-anchor correspondence remain explicitly unfixed.
- [Functionality audit](../addon_functionality_audit.md): twelve implemented major
  areas, twelve specific missing details, already-covered controls, host-specific
  replacements, and separately deferred major systems. Recommendations are not a plan
  approval or runtime implementation.
- Inspected addon registered RNA (including dynamic tissue fields), operator/UI source
  and production routing/attachment paths. Standalone core, command catalogue, QML and
  relevant tests were cross-checked. No source project or addon code was changed.
- Captured source provenance/inventories under build/addon-capability-audit. Addon's
  unrelated uncommitted shortcut-bone-fitting work is included only as a separately
  identified newer major system, not silently treated as an established release.
- In particular, cold route inspection is already implemented; accepted cold rerouting
  is not. Warm reuse, visual anchor locks, boundary power, side copy, profile scaling,
  branch controls and basic deformer weights must not be proposed again as absent.
- Documentation links and concrete evidence paths verified; git diff --check passes.
  No new runtime changes, tests, package build or version bump were required. The
  previous 2,056-test gate is labelled historical evidence, not rerun acceptance here.
