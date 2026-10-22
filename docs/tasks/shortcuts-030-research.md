# Shortcuts and parametric curves — 0.3 preparation

- Status: investigating; no production implementation requested in this stage.
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
- Next: capture saved properties/drivers and source hashes; inspect implementation
  boundaries; compare official application documentation and native expression tools.
- Local raw evidence: ignored `build/shortcuts-030/`; publish compact inventories and
  findings in repository documentation for cloud recovery.
