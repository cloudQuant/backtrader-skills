# Failure playbook: author

Each entry lists the symptom, then the exact next commands. Approval tokens are single-use and expire 15 minutes after issue by default (maximum 60 minutes).

## Token EXPIRED / REVOKED / CONSUMED

Symptom: `approval approve --token-id tok_...` or `render apply` returns
`{"status": "error", "code": "APPROVAL_REQUIRED"}` naming a state other than `ISSUED`, or the
apply fails because the capability was already consumed.

Next: obtain a fresh token and approve immediately.

```bash
backtrader-skills --target /path/to/backtrader \
  render validate --draft-id draft_...
backtrader-skills --target /path/to/backtrader \
  approval approve --token-id tok_...
backtrader-skills --target /path/to/backtrader \
  render apply --draft-id draft_... --token-id tok_...
```

If the draft was edited after validation, re-run `render preview` from the revised spec first;
an edited draft must be revalidated and re-approved.

## Validation failure with a diagnostic code

Symptom: `render validate` returns `status: failed` with one or more diagnostics, or issues no
approval token.

Next: read each diagnostic's `code` and `suggestion`. For semantic changes, revise the typed
spec and bind it to the failed report:

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

`repair --spec` fails if the revised spec does not resolve every cited diagnostic; it never
patches source text. Only `PY_SYNTAX_ERROR`, `BT_GENERATED_MARKER_MISSING`, and
`BT_DIRECT_STRATEGY_SUPER_REDUNDANT` are re-render-repairable with `repair --draft-id`.

## runonce/runnext parity mismatch

Symptom: the test skill reports `run-result-v1` with `status: failed` and metric or event
differences between the two modes.

Next: do not edit the generated file. Change the typed StrategySpec/IR, then re-render and obtain
fresh write and run approvals:

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

Then return to the test skill and run `run prepare` / `approval approve` / `run execute` again
with the new artifact.

## SOURCE_CHECKOUT_NOT_FOUND

Symptom: doctor, acceptance, or a source-bound command returns
`{"status": "error", "code": "SOURCE_CHECKOUT_NOT_FOUND"}`. The helpers only auto-locate a
Backtrader repository when this product is nested below it or next to a sibling directory named
`backtrader`.

Next: place the checkout in either layout, or pass it explicitly:

```bash
backtrader-skills --target /path/to/backtrader doctor
```

where `/path/to/backtrader` is the root of the cloudQuant/backtrader checkout.

## BACKTRADER_SOURCE_MISMATCH

Symptom: a command returns
`{"status": "error", "code": "BACKTRADER_SOURCE_MISMATCH"}`. The selected target is not provably
the required fork: it lacks `backtrader/version.py`, or its Git remote (or PEP 610 direct URL) is
not `cloudQuant/backtrader`. A matching package name or version number is not sufficient.

Next: use the mandated fork only.

```bash
git clone https://github.com/cloudQuant/backtrader.git /path/to/backtrader
backtrader-skills --target /path/to/backtrader doctor
```

Do not point `--target` at another fork, a pip-installed copy without provenance, or a copy of
the package outside a Git checkout.
