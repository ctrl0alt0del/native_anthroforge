# Shortcuts and parametric curves — 0.3 preparation

- Status: research complete; no production implementation requested in this stage.
- Branch: `codex/shortcuts-030-research`; integration: `main`; baseline: `e448291`.
- Scope: inventory every saved anatomical shortcut in the original skeleton and skull,
  resolve property targets, trace upstream/downstream Blender drivers, and research
  general formula-driven curves with editable variables. Separate observations from
  proposed standalone architecture and unresolved product decisions.
- Sources: `E:/development/WIP_models/skeleton_comb_base.blend` and
  `E:/development/WIP_models/skull_muscles.blend` (the previously named original files).
- Preserve source files; Blender inspection is background-only with automatic scripts
  disabled. No addon mutation, recomputation/export, or remote operations.
- Confirmed intent: numerical authored properties are implicit shortcuts; users expose
  explicit shortcuts; driving shortcuts apply formulas to other shortcut properties;
  a general parametric curve engine evaluates x/y/z from t and user-defined variables.
- Delivered: [analysis](../shortcuts_030_research.md), [full inventory](../research/shortcuts_030/inventory.md),
  JSON and reproduction scripts in `docs/research/shortcuts_030/`.
- Evidence: 105 skeleton + 11 skull shortcuts, all SCP-owned and resolving; 34 + 6
  driver FCurves with exact variables/formulas. None of the exposed targets is a driver
  output; 14 feed drivers. Identified attachment override/back-solve and uniform scales.
- Research: COMSOL, Creo, SOLIDWORKS, FreeCAD, Houdini; muparser and ExprTk candidates.
  Existing curve models, shared operations, path outputs and dependency graph inspected.
- Checks: hashes preserved; inventory integrity; background extraction; documentation
  links and 15-line functions. No application behavior changed or app rebuild performed.
- Local raw evidence: ignored `build/shortcuts-030/`; committed inventory is sufficient
  to inspect all shortcuts/drivers without local Blender files.
- Next product step: settle the listed 0.3 interaction/attachment/units decisions and
  produce its confirmed specification. Implementation and parser benchmarking are not
  claimed complete or authorized by this investigation alone.
