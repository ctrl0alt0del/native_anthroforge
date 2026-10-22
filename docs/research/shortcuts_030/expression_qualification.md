# 0.3 expression implementation qualification

Status: native service implemented on the development branch; driver and Parametric
integration, performance qualification and release acceptance remain incomplete.

## Candidate experiment

Compiled muparser 2.3.5 and ExprTk with Windows clang-cl 19.1.1, Release, C++17.
Disabled muparser OpenMP and samples. ExprTk source SHA256:
`a056126bb009b5676a0aade83f86035d384ea8fd4392037380e4774353871218`.
Temporary sources/builds are under ignored `build/expression-qualification`.

| Expression | muparser real | muparser integer | ExprTk double | AnthroForge requirement |
| --- | --- | --- | --- | --- |
| `12`, `12.0` | Both double | Second rejected | Both double | Distinct integer/real types |
| `5/2` | 2.5 | 2 | 2.5 | Real 2.5 with mixed typed arithmetic |
| `round(2.5)` | Unknown function | Unknown function | 3 as double | Integer conversion |
| `9007199254740993-9007199254740992` | 0 | Literal rejected | 0 | Exact integer result 1 |
| `1?2:3` | Accepted | Accepted | Accepted | Rejected syntax |

These probes disqualify unadapted defaults, not every possible custom adapter.
Both libraries could support a restricted floating subset behind an additional
typed front end. That front end would still need exact integer arithmetic and
dimensional validation. The implementation uses one bounded typed native compiler
and evaluator instead of maintaining two semantic evaluators. No new parser
dependency is pinned, and no source from these candidates is copied into production.

References: [muparser interfaces](https://beltoforion.de/en/muparser/interface.php),
[muparser integer implementation](https://github.com/beltoforion/muparser/blob/v2.3.5/src/muParserInt.cpp),
[ExprTk documentation](https://github.com/ArashPartow/exprtk/blob/master/readme.txt).
The parsing approach is ordinary recursive descent with precedence climbing, as
described in the [LLVM parser tutorial](https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl02.html);
LLVM is not a runtime dependency.

## Implemented native contract

- Immutable postfix programs with per-evaluation owned frames and stack; no mutable
  global variable bindings, callbacks, I/O, scripting or worker pool.
- Signed 64-bit integers with checked arithmetic; finite double reals. Division is
  real. `round` rounds halfway away from zero; `floor`/`ceil` also return integers.
- Comparisons yield dimensionless integer 0/1. Powers are right associative; unary
  minus has lower precedence than power. `^` and `**` are equivalent.
- Length and angle dimensions propagate independently of numerical type. `m` and
  `rad` are canonical unit constants; `pi` and `e` are dimensionless real constants.
  Literal zero may match a target quantity. Dimensioned powers require constant
  integer exponents. Trigonometry accepts angles or dimensionless parameters.
- Sources are bounded to 8192 bytes, 4096 tokens and 64 nesting levels; 256 inputs.
  Calls have fixed arity. Compile and evaluation failures preserve useful errors.
- The existing engine owns an 8 MiB / 128-entry expression cache. Outstanding leases
  keep evicted programs usable; nothing compiled enters serialized documents.
- Python validates and packs inputs, then invokes native batch evaluation. Parametric
  sampling will call this evaluator inside native work, not once per point in Python.

`tests/test_expressions.py` currently has 49 passing cases covering arithmetic,
dimensions, rejected syntax, non-finite results, overflow, concurrent owned frames,
cancellation and cache eviction. This is not yet full application qualification.
