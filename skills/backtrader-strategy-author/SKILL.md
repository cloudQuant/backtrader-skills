---
name: backtrader-strategy-author
description: Create auditable Backtrader strategies from registered offline datasets using StrategySpec v1 and the restricted Expression/Action/StateRule IR. Use for authoring backtests: new strategy scaffolds, converting trading intent into typed specifications, searching the bundled strategy catalog, or previewing and applying generated single-test or Python-bundle artifacts.
---

# Backtrader Strategy Author

Create strategy artifacts through the product CLI. Do not hand-write a second implementation for
the two output profiles; both must render from the same validated IR.

## Workflow

1. Run `python -m backtrader_skills --target /path/to/backtrader doctor`.
2. Register a read-only root with `data root-add`, then inspect and register a `DataSpec`.
3. Search the bundled snapshot with `catalog search`; treat examples as design evidence, not expected
   profitability.
4. Produce a canonical `StrategySpec v1`. Resolve feed roles, direction, sizing, entry, exit, and
   risk before rendering. Bind only the full `ds_<64hex>` dataset ID.
5. Run `spec validate`, then `render preview`. Show paths, hashes, diffs, and conflicts.
6. Run `render validate`. Ask the user to approve the returned `render_write` token.
7. Run `approval approve`, then `render apply` with that token.

Use the installed distribution command from the environment selected during setup:

```text
backtrader-skills --target /path/to/backtrader ...
```

## Invariants

- Keep runtime state under `<target>/.backtrader-skills/`.
- Generate bundles only under `strategies/generated/`.
- Generate collected tests only under `tests/functional/strategies/generated/`.
- Generate direct `bt.Strategy` subclasses without `super().__init__()` for this fork.
- Reject positive line offsets, arbitrary imports, dynamic execution, network access, live stores,
  absolute data paths, and unknown operators.
- Never imply that a backtest predicts returns.

## Pipeline

Author → review → test. Author writes the StrategySpec and applies the rendered artifact; review
validates and repairs failing drafts statically; test prepares and executes approved candidates in
runonce/runnext. On a failed review or parity run, repair the typed spec, create a new draft, and
obtain fresh write and run approvals before retrying.

## References

- [authoring-contract.md](references/authoring-contract.md) — canonical fields, IR grammar, operator table, and the two-phase write contract.
- [worked-example.md](references/worked-example.md) — two-feed `multi_timeframe` scaffold-to-apply sequence.
- [failure-playbook.md](references/failure-playbook.md) — token, validation, parity, and source-error recovery.

The script in `scripts/backtrader_skills.py` is only a thin CLI forwarder.
