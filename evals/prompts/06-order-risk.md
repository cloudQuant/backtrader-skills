## Preconditions

- The backtrader-skills package is installed in the host environment with `backtrader-skills`
  on PATH, and the three skills are available to the host agent.
- `<target>` is a cloudQuant/backtrader checkout that passes `doctor`. The evaluator substitutes
  the real target path and the full `ds_<64hex>` ID of a registered dataset before pasting.
- The dataset is already registered under `<target>/.backtrader-skills/datasets/`; the agent
  must not register or download anything.
- The operator approves every write (`render_write`) and run (`run_execution`) approval token
  the agent requests, inside the 15-minute expiry, and executes nothing on the agent's behalf.
- Canonical targets: bundles only under `strategies/generated/<archetype>/`, collected tests
  only under `tests/functional/strategies/generated/<archetype>/`, runtime state only under
  `<target>/.backtrader-skills/`.

## Prompt

Use the backtrader-strategy-author skill to author an `order_risk` backtest strategy in the
checkout at `<target>` for the registered dataset `ds_<64hex>`. Enter with a market order on a
fast/slow SMA crossover, and attach a risk bracket to every entry: a `set_stop` at the close
multiplied by 0.95 and a `set_target` at the close multiplied by 1.10. Target the `single_test`
output profile. Follow the skill's pipeline: scaffold the typed spec for the order_risk
archetype, verify the entry actions carry the stop and target price expressions, run spec
validation, preview and validate the render, ask me to approve the write token, and apply the
draft. Then hand the generated collected test to the backtrader-strategy-review skill and run
`review --file` on it; report the status and every diagnostic code. Finally use the
backtrader-strategy-test skill: run prepare on the generated candidate, show me the run
manifest, ask me to approve the run token, and execute the dual-mode run. Report the final run
status.

## Pass criteria

- Canonical `single_test` artifact exists at
  `<target>/tests/functional/strategies/generated/order_risk/test_art_<12hex>_<slug>.py`.
- The typed spec's entry actions include `set_stop` at `close * 0.95` and `set_target` at
  `close * 1.10` as price expressions.
- `review --file` on the collected test returns a validation-report-v1 with `status: passed`
  and zero errors (mechanical via `scripts/record_eval.py`).
- `run prepare` accepts the collected test as the generated candidate and returns a
  run-manifest-v1 bound to `ds_<64hex>` with modes `["runonce", "runnext"]` (mechanical via
  `scripts/record_eval.py`).
- After human approval, `run execute` returns a run-result-v1 with `status: passed` and
  metric/event parity between runonce and runnext (manual).
- No gate violations: only the `backtrader` import, no positive line offsets, no dynamic
  execution, no edits to generated files.

## Rubric

| Row | Max | Check |
| --- | --- | --- |
| Skill discovery | 2 | Agent follows the named author skill and its pipeline instead of hand-writing a backtrader script. |
| Correct CLI usage | 3 | Commands in documented order with correct flags; stop/target bracket typed as price expressions. |
| Artifact validity | 3 | Collected test exists at the canonical path; review status is passed with zero errors. |
| Approval handling | 2 | Agent pauses for write and run approvals, never self-approves, and handles single-use expiry. |
| Dual-mode parity | 3 | Approved run returns status passed; metric and event parity holds between modes (manual). |
