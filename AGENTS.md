# General agent instructions

## Research and scope

- Start with web research for existing APIs, approaches, algorithms, packages and tools. Prefer official documentation and primary sources; verify compatibility before choosing an implementation.
- Read the relevant documentation, confirmed requirements and existing code before changing behavior. Treat proposals as proposals; resolve material conflicts instead of silently inventing requirements.
- Inspect existing capabilities and previous attempts before replacing them. Distinguish observed failures, suspected causes and verified improvements.
- Work directly unless the user explicitly requests delegation. Proceed within authorized scope; ask only when an unresolved decision materially affects behavior, safety or scope.

## Design and implementation

- Diagnose the cause, responsible component, affected callers and invariants before choosing a fix. Correct shared causes where the behavior belongs and integrate every affected caller.
- Choose the smallest coherent solution. Reuse established mechanisms; avoid duplicated rules, hidden coupling, speculative frameworks and unrelated refactoring.
- Apply SOLID through cohesive responsibilities, narrow contracts and explicit dependencies. Prefer composition; justify each abstraction with a current requirement or necessary isolation boundary.
- Separate variable policies from shared lifecycle and validation rules. Before adding special cases to a central module, identify the owning responsibility and use or introduce its extension point.
- Keep every new or modified function at 15 physical lines or fewer. Extract meaningful helpers; never compress statements or split code into arbitrary fragments to meet the limit.
- Keep domain behavior independent of presentation and external integrations. Clients should use shared operations rather than duplicate business rules.
- Make data ownership, resource lifetime and side effects explicit. Keep authored state, accepted results, provisional work and presentation distinct; give workers owned inputs rather than mutable UI objects.
- Preserve confirmed contracts, including persistence, undo and asynchronous behavior where applicable. Do not silently weaken validation or hide failures with fallback behavior.
- Minimize the steps users need to achieve an outcome. Prefer direct controls and coherent undo; add previews, confirmations or prerequisite steps only for a concrete user need.

## Workflow and continuity

- Inspect repository status before editing. Preserve unrelated changes and stage only task-owned files; never discard work or rewrite shared history without explicit authorization.
- Follow the established branch and integration workflow. Keep one active writer per task branch and reconcile upstream changes without overwriting others' work.
- For work spanning checkpoints or handoffs, keep a concise durable record of decisions, current state, validation and next actions. Checkpoint coherent increments and push when authorized; verify success before claiming remote recovery.
- Keep generated environments, temporary outputs, secrets and large local assets out of commits unless explicitly required.
- Update affected documentation with behavior or architectural changes. For computational changes, record the old and new approach, rationale, preserved contracts, evidence and limits; retain reasons for rejected approaches.
- Give concise progress updates for substantial work, explaining findings, ownership decisions, validation and blockers. Routine implementation decisions do not need extra approval gates.

## Validation and delivery

- Verify the requested outcome and relevant failure cases through observable behavior. Run checks appropriate to the change; documentation-only edits need content and link review rather than an application rebuild.
- Support performance claims with representative measurements and visual or interactive claims with actual inspection. Report automated, GUI and packaging checks separately; passing tests alone does not establish design quality.
- Review the final diff for scope, correctness and maintainability. Report what changed, validation results, remaining limitations and any uncommitted or unpushed task work accurately.
