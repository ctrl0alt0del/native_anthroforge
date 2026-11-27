# Canonical build delivery

- Task branch: `codex/canonical-dist-delivery`
- Integration branch: `main`
- Starting revision: `d0c9c65492cfdebaf571b6461d95c6d72cb2226b`
- Status: in progress
- Last updated: November 27, 2026, Europe/Bucharest
- Active writer: desktop build-delivery chat

## Outcome and decisions

Deliver every completed build to the main project's versioned `dist` folder. Replace
the complete same-version package and source archive; preserve other versions. See
[agent instructions](../../AGENTS.md) and [development workflow](../development.md).
Temporary qualification remains supported, but does not count as delivery.

## Current state

The viewport-worker package was qualified under a temporary worktree build directory
and had not replaced the older canonical 0.4.3 package. The packaging tool already defaults
to `dist/<version>`; this is a delivery-workflow correction, with no application changes.
The new rule is also added to the user's dirty main checkout instructions without staging
or changing unrelated assembly work.

## Verification and next actions

Documentation reviewed against the existing packaging workflow and official
[Qt deployment documentation](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html).
Next: stage and hash-verify the qualified runtime (`79371b77`), replace
`E:/development/anthroforge/dist/0.4.3/AnthroForge.dist`, verify native startup and GUI
smoke from that location, refresh the source archive, then integrate this documentation.

## Recovery inputs

Qualified package: `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge/build/viewport-ready/AnthroForge app`.
Build artifacts are local-only. Source and prior qualification are recorded in
[viewport-worker responsiveness](viewport-worker-responsiveness.md).
