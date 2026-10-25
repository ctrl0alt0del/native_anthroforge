# Preferences actions, tooltips and UI redesign

- Branch: `codex/preferences-ui-design`; integration: `main`.
- Baseline: `030719d`; release remains 0.3.7.
- Status: in progress. Direct work; background/offscreen validation only.

## Confirmed scope

Implement Preferences buttons for opening the autosave folder and setting up Windows
`.anthroforge` file associations. Implement readable multiline tooltips through a shared
boundary. Design the broader copy/layout overhaul for review; do not replace the
production shell or rewrite unrelated labels in this pass.

File association is an explicit user action: register the current portable executable
per user, then open Windows Default Apps. Preserve the OS user's default-choice control;
never modify UserChoice or require elevation. Tests must not open Settings/Explorer on
the user's desktop. Cover executable/path quoting and existing project opening behavior.

## Investigation

Qt's attached tooltip is shared and must be styled through a custom style, rather than
adding an unrelated tooltip to each field. Qualify a tooltip-only style with Basic fallback.
The current theme already uses charcoal and amber, without gradients/glows. The observed
problems are crowded action placement, long inspectors, technical explanatory copy and
similar emphasis for primary edits, optional tools and diagnostic detail.

## Delivery / verification

1. Preferences integration and OS adapter; shared bounded multiline tooltip styling.
2. Audit representative SCP/curve/tissue/shortcut/Preferences screens; prepare an
   interactive concept and a staged design/copy plan grounded in existing capabilities.
3. Unit/offscreen/package checks; preserve geometry/history and root `__init__.py`.
4. Checkpoint/push and validated merge. Replace the canonical 0.3.7 distribution and
   source archive; never create an alternate distribution directory.

References: Microsoft Default Programs, file-type registration and Default Apps URI;
Qt custom styles, ToolTip and QQuickStyle documentation. Broader design is proposed,
not implemented or approved. Record concrete findings and evidence before completion.

## Runtime checkpoint

Implemented a per-user Windows registration adapter and desktop setup action, reusing
the existing recovery-folder action. Setup registers quoted `--project "%1"` commands
for this packaged executable, then requests Windows Default Apps; it never writes
UserChoice. Development launches explain why registration is unavailable.

The tooltip-only AnthroForgeStyle falls back to Qt Basic. Attached tooltips share the
same 380 px maximum width, plain-text wrapping, padding and palette. No per-control
popup duplication or background measurement was introduced.

Five OS-adapter tests and the architecture checks pass. Actual offscreen Preferences
at 1440×900 and 1050×680 have no detected clipped text. Hover/dismiss and short, long,
newline and path tooltips pass. Folder/setup success and failure paths use intercepted
OS calls, leave the document identical, and never open Explorer/Settings. Source smoke
loads the custom style without QML warnings. Full gate/package checks remain pending;
the broader design remains in progress. Evidence: `build/preferences-ui-design/ui`.
