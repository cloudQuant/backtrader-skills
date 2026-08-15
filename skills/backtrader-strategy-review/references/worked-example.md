# Worked example: review an injected-fault candidate

Static review never imports candidate code. This example copies an applied bundle candidate to a
scratch file, injects two representative faults, and shows the expected ValidationReport excerpt.
Use `<...>` for values that vary per run; do not fabricate exact hashes or line numbers.

## 1. Inject faults

```python
import os  # injected: forbidden import

import backtrader as bt


class GeneratedStrategy(bt.Strategy):
    params = ()
    backtrader_skills_generated = True

    def __init__(self):
        self._skills_indicators = {}

    def next(self):
        if self.datas[0].close[1] > 0:  # injected: positive line index
            self.buy()
```

The first fault violates the import allowlist; the second reads a positive (future) line offset.

## 2. Review

```bash
backtrader-skills --target /path/to/backtrader \
  review --file /path/to/backtrader/strategies/generated/.../injected-candidate.py
```

## 3. Expected ValidationReport excerpt

```json
{
  "schema_version": "validation-report-v1",
  "validation_id": "val_<24hex>",
  "artifact_hash": "<64hex>",
  "dataset_id": null,
  "status": "failed",
  "diagnostics": [
    {
      "code": "SEC_FORBIDDEN_IMPORT",
      "severity": "error",
      "file": "injected-candidate.py",
      "line": <n>,
      "column": 0,
      "rule": "import-allowlist",
      "message": "forbidden module import: os",
      "suggestion": "Remove operating-system, process, network, and dynamic-import access."
    },
    {
      "code": "BT_LOOKAHEAD_POSITIVE_INDEX",
      "severity": "error",
      "file": "injected-candidate.py",
      "line": <n>,
      "column": <c>,
      "rule": "no-lookahead",
      "message": "positive line index can read future data",
      "suggestion": "Use index 0 for the current bar and negative indices for history."
    }
  ],
  "evidence": {
    "candidate": {"file": "injected-candidate.py", "sha256": "<64hex>"},
    "layers": {
      "specification": "not_applicable",
      "python_ast": "failed",
      "fork_api": "failed",
      "security": "failed",
      "import_collection": "pending",
      "smoke": "pending",
      "runonce_runnext": "pending",
      "target_test": "pending",
      "baseline": "pending",
      "artifact_integrity": "pending"
    },
    "strategy_classes": ["GeneratedStrategy"],
    "summary": {"errors": 2, "warnings": 0, "passed": false}
  },
  "layers": {
    "specification": "not_applicable", "python_ast": "failed", "fork_api": "failed",
    "security": "failed", "import_collection": "pending", "smoke": "pending",
    "runonce_runnext": "pending", "target_test": "pending", "baseline": "pending",
    "artifact_integrity": "pending"
  },
  "summary": {"errors": 2, "warnings": 0, "passed": false},
  "validation_hash": "<64hex>"
}
```

The `layers` object appears at top level and inside `evidence`; `fork_api` and `security` fail
because at least one error carries the respective prefix. Report diagnostics by stable code,
severity, file, line, column, rule, message, and remediation.

## 4. Repair path

Neither `SEC_FORBIDDEN_IMPORT` nor `BT_LOOKAHEAD_POSITIVE_INDEX` is re-render-repairable, so
`repair --draft-id` refuses and the typed spec must change:

```bash
backtrader-skills --target /path/to/backtrader \
  repair --spec revised-strategy-spec.json --validation-report failed-validation.json
```

`repair --spec` renders the revised spec and fails if any cited diagnostic code reappears in the
new draft. Then the author skill re-runs `render validate`, obtains a fresh write approval, and
applies the new draft.
