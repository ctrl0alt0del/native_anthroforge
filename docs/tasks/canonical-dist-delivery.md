# Canonical build delivery

- Task branch: `codex/canonical-dist-delivery`
- Integration branch: `main`
- Starting revision: `d0c9c65492cfdebaf571b6461d95c6d72cb2226b`
- Status: delivery and validation complete; ready to integrate
- Last updated: November 27, 2026, Europe/Bucharest
- Active writer: desktop build-delivery chat

## Outcome and decisions

Deliver every completed build to the main project's versioned `dist` folder. Replace
the complete same-version package and source archive; preserve other versions. See
[agent instructions](../../AGENTS.md) and [development workflow](../development.md).
Temporary qualification remains supported, but does not count as delivery.

## Current state

The viewport-worker package was qualified under a temporary worktree build directory
and had not replaced the older canonical 0.4.3 package. It now replaces that complete
package at `E:/development/anthroforge/dist/0.4.3/AnthroForge.dist`; the matching source
archive is refreshed at `E:/development/anthroforge/dist/AnthroForge-0.4.3-source.zip`.
The packaging tool already defaults to `dist/<version>`; this is a delivery-workflow
correction, with no application changes or recompilation. Runtime source is `79371b77`;
the source archive includes policy checkpoint `2d422423`, whose intervening changes are
documentation only. Other versions are preserved.
The new rule is also added to the user's dirty main checkout instructions without staging
or changing unrelated assembly work.

## Verification

Documentation reviewed against the existing packaging workflow and official
[Qt deployment documentation](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html).
- All 3,402 package files (371,927,877 bytes) match the qualified package by SHA-256,
  verified before replacement and again at the canonical destination.
- Windows native doctor (`--cli doctor --require-native`) passes with minimal PATH and
  no developer Qt/Python settings; its native DLL resolves inside the delivered package.
- Existing `check_portable.primitives` passes creation, inspection, native-window GUI
  smoke and screenshot capture from the canonical executable. Screenshot visually inspected.
- Source archive passes ZIP CRC, version and delivery-instruction checks: 24,408 entries,
  48,045,529 bytes. No application regression suite rerun for this documentation/publication change.
- Generated evidence is local-only under
  `E:/development/anthroforge/build/canonical-dist-delivery-20261127`.
- Automatic approval review rejected deleting the temporary `previous-build` backup.
  It is retained under that evidence directory; no cleanup bypass was attempted.

## Next actions

Integrate the reviewed documentation branch into `main` and verify its remote ancestry.
No application delivery work remains.

## Recovery inputs

Qualified package: `C:/Users/alexe/.codex/worktrees/general-agent-instructions/anthroforge/build/viewport-ready/AnthroForge app`.
Build artifacts are local-only. Source and prior qualification are recorded in
[viewport-worker responsiveness](viewport-worker-responsiveness.md).
