# Review rules

Validation layers are specification, Python AST, current-fork API, security/path/dependency,
import/collection, smoke, runonce/runnext, target tests, baseline, and artifact integrity.

Static review never imports candidate code. P0 execution accepts only product-generated candidates.
Unknown third-party candidates may be reviewed with `--allow-third-party`, but cannot obtain a run
approval. Stable `SEC_*` codes identify trust-boundary failures; `BT_*` codes identify fork API,
construction, or look-ahead failures; `PY_SYNTAX_ERROR` identifies a candidate that cannot be
parsed.

Repair changes typed IR or re-renders it. It does not use textual `exec`, `eval`, `compile`, dynamic
imports, or guessed source edits.

## Diagnostic catalog

Every diagnostic is reported by stable code, severity, file, line, column, rule, message, and
suggestion. Severity is `error` (blocks execution approval) or `warning` (reported, does not block).

| Code | Severity | Trigger | Remediation |
| --- | --- | --- | --- |
| `PY_SYNTAX_ERROR` | error | `ast.parse` raises `SyntaxError` | Fix the syntax before requesting execution approval. |
| `SEC_FORBIDDEN_IMPORT` | error | Import of `os`, `subprocess`, `socket`, `requests`, `httpx`, `urllib`, `http.client`, `ftplib`, `telnetlib`, `importlib`, `shutil`, or `asyncio.subprocess` (or a submodule) | Remove operating-system, process, network, and dynamic-import access. |
| `SEC_IMPORT_NOT_ALLOWLISTED` | error | Top-level module other than `backtrader` is imported | Generated candidates may import only the top-level backtrader module. |
| `SEC_IMPORT_FORM_NOT_ALLOWLISTED` | error | Generated candidate uses `from backtrader import ...` or imports any module other than exactly `backtrader` | Use `import backtrader as bt`; controller and filesystem modules are never available to candidate code. |
| `SEC_DYNAMIC_EXECUTION` | error | Call to `exec`, `eval`, `compile`, or `__import__` | Represent logic in StrategySpec Expression/Action/StateRule IR. |
| `SEC_COMMAND_EXECUTION` | error | Call to `os.system` or `os.popen` | Remove command execution from the strategy. |
| `SEC_DUNDER_ESCAPE` | error | Attribute access on `__subclasses__`, `__bases__`, `__mro__`, `__globals__`, `__builtins__`, or `__code__` | Represent logic in StrategySpec Expression/Action/StateRule IR. |
| `SEC_ABSOLUTE_PATH` | error | String constant that is an absolute filesystem path (`/...` or a drive letter) | Bind data through an opaque dataset_id. |
| `BT_LIVE_COMPONENT_FORBIDDEN` | error | Instantiation or call of `IBStore`, `CCXTStore`, `OandaStore`, or `VCStore` | Use a registered offline DatasetManifest. |
| `BT_LOOKAHEAD_POSITIVE_INDEX` | error | Positive constant index into a data-line-like attribute (`close[1]`, `lines[2]`, indicator array) | Use index 0 for the current bar and negative indices for history. |
| `BT_DIRECT_STRATEGY_SUPER_REDUNDANT` | warning | Direct `bt.Strategy` subclass calls `super().__init__()` | Omit `super().__init__()` in a direct bt.Strategy generated template. |
| `BT_COOPERATIVE_INIT_REQUIRED` | error | Non-direct parent (custom parent, `Indicator`, `Analyzer`, `Observer`, `DataBase`, `FeedBase`) does not call `super().__init__()` first | Place `super().__init__()` before accessing params, data, or lines. |
| `BT_STRATEGY_CLASS_MISSING` | error | No direct `bt.Strategy` subclass found | Declare one class that directly subclasses bt.Strategy. |
| `BT_GENERATED_MARKER_MISSING` | error | No class carries the `backtrader_skills_generated = True` marker | Generate the candidate from a validated StrategySpec. |

Classification rules: a class is a direct strategy when one of its bases is named `Strategy`; a
framework component when a base tail is `Indicator`, `Analyzer`, `Observer`, `DataBase`,
`AbstractDataBase`, or `FeedBase`; otherwise it is a custom parent. In `__init__`, docstrings do not
count as executable statements for the cooperative-init check.

Only `BT_DIRECT_STRATEGY_SUPER_REDUNDANT`, `BT_GENERATED_MARKER_MISSING`, and `PY_SYNTAX_ERROR`
are re-render-repairable (`repair --draft-id` re-renders the stored StrategySpec). Every other
diagnostic requires a StrategySpec change and is repaired with
`repair --spec <revised-spec.json> --validation-report <failed-validation.json>`.

## Report shape

A review returns a `validation-report-v1` object with `validation_id` (`val_` plus 24 hex
characters of the artifact hash), `artifact_hash`, `dataset_id`, `status` (`passed` only when zero
errors), `diagnostics`, and `layers`. Layer verdicts: `python_ast` fails on any error; `fork_api`
and `security` fail on errors with their respective prefixes; `specification`, `import_collection`,
`smoke`, `runonce_runnext`, `target_test`, `baseline`, and `artifact_integrity` are
`not_applicable`/`pending` outside their own gates. The report ends in a canonical
`validation_hash`.

## Coverage boundaries

The AST and import gate is defense-in-depth on top of the hash-bound execution path, not an
operating-system sandbox. It statically rejects forbidden imports, dynamic execution, command
execution, live stores, absolute paths, positive-constant line indices, and a denylist of dunder
escape primitives (`__subclasses__`, `__bases__`, `__mro__`, `__globals__`, `__builtins__`,
`__code__`). It does not restrict `getattr`/`setattr` (the generated evaluator uses `getattr`) or
attribute access in general, and it does not statically catch positive indices produced by computed
expressions or variables. Candidate execution is therefore additionally gated by a separately
approved, hash-bound run token that only accepts unchanged artifacts from an approved render/apply.
