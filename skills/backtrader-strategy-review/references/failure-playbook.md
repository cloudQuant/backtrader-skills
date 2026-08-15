# Failure playbook: review

Each entry lists the symptom, then the exact next commands. Review never imports or executes a
candidate.

## Token EXPIRED / REVOKED / CONSUMED

Symptom: `approval show --token-id tok_...` reports a state other than `ISSUED`, or `render
apply` fails with `APPROVAL_REQUIRED` naming `EXPIRED`, `REVOKED`, or `CONSUMED`. Tokens expire
15 minutes after issue by default and are single-use.

Next: ask the user to approve a freshly issued token without delay.

```bash
backtrader-skills --target /path/to/backtrader \
  render validate --draft-id draft_...
backtrader-skills --target /path/to/backtrader \
  approval approve --token-id tok_...
backtrader-skills --target /path/to/backtrader \
  render apply --draft-id draft_... --token-id tok_...
```

Never reuse an old token; every repaired draft needs a new validation and a new approval.

## Validation failure with a diagnostic code

Symptom: `review --file ...` or `render validate --draft-id ...` returns `status: failed` with
diagnostics carrying stable codes.

Next: classify each code against the catalog in `review-rules.md`.

- Re-render-repairable (`PY_SYNTAX_ERROR`, `BT_GENERATED_MARKER_MISSING`,
  `BT_DIRECT_STRATEGY_SUPER_REDUNDANT`):

```bash
backtrader-skills --target /path/to/backtrader \
  repair --draft-id draft_...
```

- All other codes require a StrategySpec change:

```bash
backtrader-skills --target /path/to/backtrader \
  repair --spec revised-strategy-spec.json --validation-report failed-validation.json
```

`repair --spec` refuses if the revised spec does not resolve every cited diagnostic. Then
revalidate, obtain a fresh write approval, and apply. Never patch arbitrary source text.

## runonce/runnext parity mismatch

Symptom: the test skill's `run-result-v1` shows `status: failed` with metric or event
differences between modes.

Next: read the stored `run-result.json` and `report.md`. If the divergence traces to the typed
IR, send the spec back through the author loop:

```bash
backtrader-skills --target /path/to/backtrader \
  repair --spec revised-strategy-spec.json --validation-report failed-validation.json
backtrader-skills --target /path/to/backtrader \
  render validate --draft-id draft_...
```

Then approve and apply, and have the test skill prepare and execute again with fresh approvals.
Parity is a release gate; never waive it by editing the generated file.

## SOURCE_CHECKOUT_NOT_FOUND

Symptom: a source-bound command returns
`{"status": "error", "code": "SOURCE_CHECKOUT_NOT_FOUND"}`. The product is neither nested in a
Backtrader checkout nor next to a sibling `backtrader` directory.

Next: place the product accordingly or point every command at the checkout explicitly:

```bash
backtrader-skills --target /path/to/backtrader doctor
```

## BACKTRADER_SOURCE_MISMATCH

Symptom: a command returns
`{"status": "error", "code": "BACKTRADER_SOURCE_MISMATCH"}`. The target lacks
`backtrader/version.py` or its Git remote/PEP 610 URL is not `cloudQuant/backtrader`.

Next: install or select the mandated fork, then re-run:

```bash
backtrader-skills --target /path/to/backtrader doctor
```

A package with a matching name or version from another fork is rejected; do not continue with an
unverifiable source.
