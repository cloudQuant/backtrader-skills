# Failure playbook: test

Each entry lists the symptom, then the exact next commands. Execution tokens are single-use and expire 15 minutes after issue by default (maximum 60 minutes).

## Token EXPIRED / REVOKED / CONSUMED

Symptom: `approval approve --token-id tok_...` or `run execute` returns
`{"status": "error", "code": "APPROVAL_REQUIRED"}` naming a state other than `ISSUED`, or the
token was consumed by an earlier attempt.

Next: prepare again and approve the fresh token immediately.

```bash
backtrader-skills --target /path/to/backtrader \
  run prepare --candidate /path/to/backtrader/strategies/generated/.../strategy.py \
  --dataset-id 'ds_<64hex>'
backtrader-skills --target /path/to/backtrader \
  approval approve --token-id tok_...
backtrader-skills --target /path/to/backtrader \
  run execute --run-id run_... --token-id tok_...
```

If the candidate, dataset, or environment changed after the original prepare, `prepare` again so the bindings match reality.

## Validation failure with a diagnostic code

Symptom: `run prepare` fails with `CONTRACT_INVALID` "candidate failed static validation" and a
`diagnostics` list, or the candidate is rejected as not an unchanged applied artifact.

Next: send the diagnostics to the review skill and repair the typed spec, never the generated
file:

```bash
backtrader-skills --target /path/to/backtrader \
  repair --spec revised-strategy-spec.json --validation-report failed-validation.json
backtrader-skills --target /path/to/backtrader \
  render validate --draft-id draft_...
backtrader-skills --target /path/to/backtrader \
  approval approve --token-id tok_...
backtrader-skills --target /path/to/backtrader \
  render apply --draft-id draft_... --token-id tok_...
```

Then return here and run `run prepare` again against the newly applied bytes.

## runonce/runnext parity mismatch

Symptom: `run-result.json` has `status: failed` with metric or event `differences` in
`comparison`.

Next: read `run-result.json` and `report.md` under
`<target>/.backtrader-skills/runs/<run_id>/`; integer differences are exact-count mismatches,
float differences cite the tolerance rule, event differences list the index and both
normalized events. Then repair the typed IR and re-render with fresh approvals:

```bash
backtrader-skills --target /path/to/backtrader \
  repair --spec revised-strategy-spec.json --validation-report failed-validation.json
backtrader-skills --target /path/to/backtrader \
  render validate --draft-id draft_...
backtrader-skills --target /path/to/backtrader \
  approval approve --token-id tok_...
backtrader-skills --target /path/to/backtrader \
  render apply --draft-id draft_... --token-id tok_...
```

Then `run prepare`, approve, and `run execute` again. Parity is a release gate; do not waive it or hand-edit the generated artifact.

## SOURCE_CHECKOUT_NOT_FOUND

Symptom: `run prepare`/`run execute` (or doctor) returns
`{"status": "error", "code": "SOURCE_CHECKOUT_NOT_FOUND"}`. The helpers cannot auto-locate the
Backtrader repository because the product is neither nested in it nor next to a sibling
`backtrader` directory.

Next: place the checkout in either layout or pass it explicitly on every command:

```bash
backtrader-skills --target /path/to/backtrader doctor
backtrader-skills --target /path/to/backtrader \
  run prepare --candidate /path/to/backtrader/strategies/generated/.../strategy.py \
  --dataset-id 'ds_<64hex>'
```

## BACKTRADER_SOURCE_MISMATCH

Symptom: `run prepare` returns
`{"status": "error", "code": "BACKTRADER_SOURCE_MISMATCH"}`. The target is not provably the
cloudQuant/backtrader fork: no `backtrader/version.py`, or the Git remote/PEP 610 URL is
elsewhere.

Next: use the mandated fork only, then re-prepare:

```bash
backtrader-skills --target /path/to/backtrader \
  run prepare --candidate /path/to/backtrader/strategies/generated/.../strategy.py \
  --dataset-id 'ds_<64hex>'
```

If the environment package cannot be verified, doctor reports `BACKTRADER_SOURCE_WARNING`; fix the environment before relying on any run result.
