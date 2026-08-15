## Preconditions

- The backtrader-skills package is installed in the host environment with `backtrader-skills`
  on PATH, and the three skills are available to the host agent.
- `<target>` is a cloudQuant/backtrader checkout that passes the doctor check. The evaluator
  substitutes the real target path and the full `ds_<64hex>` ID of a registered dataset before
  pasting.
- The dataset is already registered under `<target>/.backtrader-skills/datasets/`; the agent
  must not register or download anything.
- The operator approves every write (`render_write`) and run (`run_execution`) approval token
  the agent requests, inside the 15-minute expiry, and executes nothing on the agent's behalf.
- This prompt exercises the failure-to-parity loop: failure, typed repair, revalidation, and an
  approved dual-mode run.

## Prompt

Use the backtrader-strategy-author, backtrader-strategy-review, and backtrader-strategy-test
skills to drive a full failure-to-parity loop for a `multi_timeframe` strategy in the checkout
at `<target>` for the registered dataset `ds_<64hex>`. Scaffold and preview the typed `spec`
through the author skill, then tamper with the previewed draft: delete the generated-marker
line. Run render validation to capture the structured failure report, then run `repair` to
re-render the draft from the stored typed spec. Revalidate, ask me to approve the write token,
and apply the draft. Run the review skill's `review` on the applied candidate, then
`run prepare` it, ask me to approve the run token, and execute the dual-mode run. Report the
captured diagnostic code, the repaired review status, and the final run status.

## Pass criteria

- The tampered draft is never applied; `repair` re-renders the draft from the stored typed spec
  (manual, from the transcript).
- The captured failure report carries `BT_GENERATED_MARKER_MISSING` and the agent quotes it.
- `review --file` on the final applied candidate returns `status: passed` with zero errors
  (mechanical via `scripts/record_eval.py`).
- `run prepare` returns a run-manifest-v1 bound to `ds_<64hex>` with modes
  `["runonce", "runnext"]` (mechanical via `scripts/record_eval.py`).
- After human approval, the dual-mode execution returns a run-result-v1 with `status: passed`
  and metric/event parity between runonce and runnext (manual).

## Rubric

| Row | Max | Check |
| --- | --- | --- |
| Loop fidelity | 3 | Agent walks failure, typed repair, revalidation, approval, and run without skipping a step. |
| Typed repair | 3 | Repair re-renders the stored spec; the tampered draft is never applied or patched in place. |
| Revalidation | 2 | Final review passes with zero errors; fresh write approval requested before apply. |
| Approval handling | 2 | Fresh write and run approvals requested; agent never self-approves or reuses tokens. |
| Dual-mode parity | 3 | Approved run returns status passed; metric and event parity holds between modes (manual). |
