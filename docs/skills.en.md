# Skills

`backtrader-skills` ships three canonical skills, one per pipeline stage. Installation puts them in
your host's native skill directory (see [Home](index.md)); each installed skill has one thin
`scripts/backtrader_skills.py` forwarder, and deterministic behavior lives only in
`src/backtrader_skills/`.

| Skill | Role |
| --- | --- |
| `backtrader-strategy-author` | Create auditable Backtrader strategies from registered offline datasets using `StrategySpec v1` and the restricted Expression/Action/StateRule IR. |
| `backtrader-strategy-review` | Review `StrategySpec` and generated Python artifacts without importing candidate code; return the structured `ValidationReport v1`. |
| `backtrader-strategy-test` | Run approved candidates in fixed isolated child processes and compare runonce with runnext. |

## The pipeline

Author → review → test.

1. **Author** runs `doctor`, registers data roots and datasets, searches the bundled catalog, and
   produces a canonical `StrategySpec v1`. It resolves feed roles, direction, sizing, entry, exit,
   and risk before rendering, then previews, validates, and applies the rendered artifact under a
   `render_write` approval token.
2. **Review** statically validates authored drafts and applied artifacts — `review --file` for an
   applied candidate or `render validate --draft-id` for a product draft — and reports diagnostics
   by stable code, severity, file, line, rule, explanation, and remediation. It never imports or
   executes a candidate.
3. **Test** is the final gate: `run prepare` recomputes hashes and static validation evidence for
   an applied candidate against a DatasetManifest, and a separately approved `run execute` runs it
   in two fixed `python -I` child processes for runonce/runnext comparison. The controlling process
   never imports candidate code.

## The repair loop

A failed validation or parity run repairs back through the author/review loop: revise the typed
spec (or bind a revised spec to the failed `ValidationReport` with
`repair --spec ... --validation-report ...`), create a new draft, and obtain fresh write and run
approvals before retrying. Repair only returns to the stored StrategySpec and re-renders; it never
patches arbitrary third-party source. Catalog examples are design evidence, not expected
profitability, and a backtest never implies predicted returns.

## Shipped references

Each skill ships its reference contracts, worked examples, and failure playbooks, drift-locked to
runtime facts by tests. The files live next to each `SKILL.md`; the CLI is the only supported way
to exercise them.

**`backtrader-strategy-author`**

- `references/authoring-contract.md` — canonical fields, IR grammar, operator table, and the two-phase write contract.
- `references/worked-example.md` — a two-feed `multi_timeframe` scaffold-to-apply sequence.
- `references/failure-playbook.md` — token, validation, parity, and source-error recovery.

**`backtrader-strategy-review`**

- `references/review-rules.md` — diagnostic catalog, severity, remediation, and trust boundaries.
- `references/worked-example.md` — an injected-fault candidate and the expected `ValidationReport` excerpt.
- `references/failure-playbook.md` — token, diagnostic, parity, and source-error recovery.

**`backtrader-strategy-test`**

- `references/metric-contract.md` — the 11 metric units and nullable rules.
- `references/worked-example.md` — prepare → approve → execute and the expected report fields.
- `references/failure-playbook.md` — token, parity, and source-error recovery.

## Author invariants

The author skill keeps runtime state under `<target>/.backtrader-skills/`, generates bundles only
under `strategies/generated/`, generates collected tests only under
`tests/functional/strategies/generated/`, and emits direct `bt.Strategy` subclasses without
`super().__init__()` for this fork. It rejects positive line offsets, arbitrary imports, dynamic
execution, network access, live stores, absolute data paths, and unknown operators.
