# Worked example: prepare, approve, execute

Golden path for an applied, product-generated candidate. Placeholders (`run_...`, `tok_...`,
`'ds_<64hex>'`, `<...>`) stand for values the CLI returns; do not invent exact hashes or metric
values.

## 1. Prepare

```bash
backtrader-skills --target /path/to/backtrader \
  run prepare --candidate /path/to/backtrader/strategies/generated/.../strategy.py \
  --dataset-id 'ds_<64hex>'
```

`run prepare` rejects candidates outside the generated roots, proves the file is an unchanged
artifact from an approved render/apply, re-runs static validation, verifies the DatasetManifest,
and returns a run manifest plus a `run_execution` approval token. Key run manifest fields:

```json
{
  "schema_version": "run-manifest-v1",
  "run_id": "run_<20hex>",
  "artifact_hash": "<64hex>",
  "dataset_id": "ds_<64hex>",
  "engine": {"name": "backtrader", "source": "target-checkout",
             "version_file_hash": "<64hex>"},
  "run_profile": {"modes": ["runonce", "runnext"],
                  "comparison_profile": "comparison-profile-v1",
                  "timeout_seconds": 120},
  "approval_id": "approval_<24hex>",
  "candidate": {"relative_path": "strategies/generated/.../strategy.py",
                "sha256": "<64hex>",
                "strategy_spec_hash": "<64hex>",
                "source_draft_id": "draft_...",
                "source_artifact_hash": "<64hex>"},
  "dataset": {"dataset_id": "ds_<64hex>", "manifest_hash": "<64hex>",
              "semantic_hash": "<64hex>"},
  "modes": ["runonce", "runnext"],
  "fixed_argv": ["<python>", "-I", "<isolate-entry>", "--target", "<target>",
                 "--candidate", "strategies/generated/.../strategy.py",
                 "--dataset-id", "ds_<64hex>", "--mode", "<mode>"],
  "cwd": "<isolated-temporary-directory>",
  "allowed_environment": ["PATH", "LANG", "LC_ALL", "TMPDIR",
                          "PYTHONDONTWRITEBYTECODE", "PYTHONNOUSERSITE", "NO_PROXY"],
  "manifest_hash": "<64hex>"
}
```

The approval token binds the run manifest, candidate, dataset, and environment hashes; any drift
revokes the binding at execute time.

## 2. Approve

```bash
backtrader-skills --target /path/to/backtrader \
  approval show --token-id tok_...
backtrader-skills --target /path/to/backtrader \
  approval approve --token-id tok_...
```

`show` displays the issued capability (`kind: run_execution`, `state`, `binding_hash`,
`expires_at`); `approve` marks it approved. Ask the user before approving; the token is
single-use and expires 15 minutes after issue by default.

## 3. Execute

```bash
backtrader-skills --target /path/to/backtrader \
  run execute --run-id run_... --token-id tok_...
```

Execute consumes the token atomically, then runs the fixed interpreter with `-I` twice (once per
mode) in isolated working directories. Expected result shape:

```json
{
  "schema_version": "run-result-v1",
  "run_id": "run_<20hex>",
  "manifest_hash": "<64hex>",
  "status": "passed",
  "metrics": { },
  "modes": {"runonce": { }, "runnext": { }},
  "comparison": {
    "metrics": {"profile_version": "comparison-profile-v1",
                "profile_hash": "<64hex>",
                "diagnostics": [], "differences": [], "passed": true,
                "comparison_hash": "<64hex>"},
    "events": {"fields": ["sequence", "kind", "data", "size", "price", "status"],
               "left_count": <n>, "right_count": <n>, "differences": [],
               "truncated": false, "passed": true,
               "comparison_hash": "<64hex>"}
  },
  "artifacts": [{"path": "report.md", "role": "run_report_markdown",
                 "bytes": <n>, "sha256": "<64hex>"}],
  "diagnostics": [],
  "result_hash": "<64hex>"
}
```

`status` is `passed` only when both metric and event comparisons pass.

## 4. Read the reports

```bash
ls /path/to/backtrader/.backtrader-skills/runs/run_<20hex>/
```

- `run-manifest.json` — hash-bound run plan written by prepare
- `static-validation.json` — revalidation evidence
- `runonce.json` / `runnext.json` — per-mode child results with the 11 metrics
- `run-result.json` — the merged result above
- `report.md` — Markdown table of `metric | unit | runonce | runnext` plus parity and isolation
  notes

Parity passes only when integer metrics and normalized events match exactly, floating metrics
satisfy the frozen tolerance profile (`rel_tol=1e-7`, `abs_tol=1e-9`; `final_value` uses
`rel_tol=1e-9`, `abs_tol=1e-6`), and null occurs only where declared.
