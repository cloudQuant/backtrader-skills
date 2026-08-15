## Preconditions

- The backtrader-skills package is installed in the host environment with `backtrader-skills`
  on PATH, and the three skills are available to the host agent.
- `<target>` is a cloudQuant/backtrader checkout that passes `doctor`. The evaluator substitutes
  the real target path and the full `ds_<64hex>` ID of a registered dataset before pasting.
- The dataset is already registered under `<target>/.backtrader-skills/datasets/`, and it
  declares the precomputed custom line `signal` (an evaluator requirement for this prompt); the
  agent must not register or download anything.
- The operator approves every write (`render_write`) and run (`run_execution`) approval token
  the agent requests, inside the 15-minute expiry, and executes nothing on the agent's behalf.
- Canonical targets: bundles only under `strategies/generated/<archetype>/`, collected tests
  only under `tests/functional/strategies/generated/<archetype>/`, runtime state only under
  `<target>/.backtrader-skills/`.

## Prompt

Use the backtrader-strategy-author skill to author a `precomputed_ml` backtest strategy in the
checkout at `<target>` for the registered dataset `ds_<64hex>`. The dataset carries a
precomputed `signal` custom line; trade it directly: enter when the signal is greater than zero
and exit when it is less than or equal to zero. Target the `python_bundle` output profile.
Follow the skill's pipeline: scaffold the typed spec for the precomputed_ml archetype declaring
`signal` as a custom line, verify the entry and exit expressions compare the custom line with
`gt` and `lte`, run spec validation, preview and validate the render, ask me to approve the
write token, and apply the draft. Then hand the applied `strategy.py` to the
backtrader-strategy-review skill and run `review --file` on it; report the status and every
diagnostic code. Finally use the backtrader-strategy-test skill: run prepare on the applied
candidate, show me the run manifest, ask me to approve the run token, and execute the dual-mode
run. Report the final run status.

## Pass criteria

- Canonical `python_bundle` artifact exists under
  `<target>/strategies/generated/precomputed_ml/art_<12hex>_<slug>/` with `strategy.py`,
  `config.json`, and `README.md`.
- The typed spec declares `signal` in `custom_lines` and the entry/exit expressions read the
  custom line through data_line nodes (`gt 0` / `lte 0`).
- `review --file` on `strategy.py` returns a validation-report-v1 with `status: passed` and
  zero errors (mechanical via `scripts/record_eval.py`).
- `run prepare` returns a run-manifest-v1 bound to `ds_<64hex>` with modes
  `["runonce", "runnext"]` (mechanical via `scripts/record_eval.py`).
- After human approval, `run execute` returns a run-result-v1 with `status: passed` and
  metric/event parity between runonce and runnext (manual).
- No gate violations: only the `backtrader` import, no positive line offsets, no dynamic
  execution, no edits to generated files.

## Rubric

| Row | Max | Check |
| --- | --- | --- |
| Skill discovery | 2 | Agent follows the named author skill and its pipeline instead of hand-writing a backtrader script. |
| Correct CLI usage | 3 | Commands in documented order with correct flags; custom line declared and referenced correctly. |
| Artifact validity | 3 | Canonical bundle files exist; review status is passed with zero errors. |
| Approval handling | 2 | Agent pauses for write and run approvals, never self-approves, and handles single-use expiry. |
| Dual-mode parity | 3 | Approved run returns status passed; metric and event parity holds between modes (manual). |
