# 0.4.2 recommendation coverage audit

- Task branch: `codex/recommendations-audit-042`
- Integration branch: `main`
- Starting revision: `6970a5713e2812e5e7962238f6ffe905e28f76be` (0.4.1)
- Status: in progress; documentation and source inspection only
- Updated: 2026-10-28, Europe/Bucharest
- Active writer: local desktop chat; direct work

## Outcome

Review every original cross-thread recommendation against the current app and list what
remains. Cover the 66 consolidated requirements and their 132 source-item mappings in
`standalone_application_recommendations.md`. Distinguish implemented capabilities,
partial workflows, missing features, explicitly deferred or superseded proposals, and
measurement/qualification limits. This does not authorize implementing the resulting
backlog, changing algorithms, bumping versions or building another package.

## Evidence and current state

Read the consolidated requirements and source coverage; inspect current core, application,
native and desktop boundaries plus maintained release/test evidence. Stale prose is not
evidence of a missing feature. In particular, comparison/replay, recovery autosave, skin,
strict mirroring and VCP inspection have shipped. Production code remains untouched.
The public verification-matrix reference consulted first is NASA's Appendix D; it is
method guidance, not evidence that any AnthroForge feature is present.

Concrete gaps found include cross-project anatomy assembly, general reconstruction
catalogue/variants, measured tightening previews, configurable profile stations, richer
placement explanations, generalized spatial findings, concurrent view presentations,
display LOD/buffer reuse and aggregate cache budgeting. Each still needs its exact scope
and evidence recorded before being presented as a 0.4.2 candidate.

## Next steps

1. Finish the requirement-by-requirement matrix with code and test/delivery references.
2. Check coverage of all 66 IDs and 132 original mappings, links and current decisions.
3. Deliver the remaining-work list and integrate this documentation checkpoint.

No application tests or GUI actions are needed for this read-only audit. Existing tests
are implementation evidence, not claims of a fresh execution. Preserve root `__init__.py`.
