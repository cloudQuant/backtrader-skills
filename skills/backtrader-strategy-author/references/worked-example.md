# Worked example: author a multi-timeframe bundle

Golden path from scaffold to applied artifact. All placeholders (`/path/to/backtrader`,
`'ds_<64hex>'`, `draft_...`, `tok_...`) stand for values the CLI returns; do not invent exact
hashes or metric values.

## 1. Preflight and catalog evidence

```bash
backtrader-skills --target /path/to/backtrader doctor
backtrader-skills --target /path/to/backtrader \
  catalog search --query "multi timeframe momentum" --archetype multi_timeframe
```

`doctor` proves the cloudQuant/backtrader source and returns catalog counts. Catalog hits are
design evidence, not expected profitability.

## 2. Scaffold the two-feed spec

```bash
backtrader-skills --target /path/to/backtrader \
  spec scaffold --archetype multi_timeframe --output-profile python_bundle \
  --dataset-id 'ds_<64hex>' --feed-count 2 > strategy-spec.json
```

The scaffold declares `spec_version: strategy-spec-v1`, two feeds (`data0` role `execution`,
`data1` role `signal`), `fast_period`/`slow_period` parameters, `fast`/`slow` SMA indicators
placed on feed 1, and two StateRules:

```json
{
  "name": "enter",
  "stage": "next",
  "when": {
    "kind": "operator",
    "op": "cross_up",
    "args": [
      {"kind": "indicator", "name": "fast"},
      {"kind": "indicator", "name": "slow"}
    ]
  },
  "actions": [{"kind": "buy", "feed": 0, "order_type": "market"}],
  "priority": 10,
  "exclusive_group": "position"
}
```

`exit` mirrors it with `cross_down` and `{"kind": "close", "feed": 0}` at priority 20. Edit the
JSON, then validate the canonical form:

```bash
backtrader-skills --target /path/to/backtrader \
  spec validate --spec strategy-spec.json
```

The result is the normalized StrategySpec: canonical fields plus `ir` (indicators, state
variables, state rules, `minperiod`), `entry`/`exit` rule references, `run_modes`
`["runonce", "runnext"]`, `allowed_imports` `["backtrader"]`, `spec_hash`, and the four frozen
`extensions.backtrader_skills.analyzers`.

## 3. Preview, validate, approve, apply

```bash
backtrader-skills --target /path/to/backtrader \
  render preview --spec strategy-spec.json
```

The returned artifact manifest carries `draft_id` (`draft_...`), `artifact_id`
(`art_<12hex>`), `spec_hash`, `strategy_source_hash`, `output_profile: python_bundle`, and one
`files` entry per bundle member:

- `strategies/generated/multi_timeframe/art_<12hex>_multi-timeframe/strategy.py` (role `strategy`)
- `strategies/generated/multi_timeframe/art_<12hex>_multi-timeframe/config.json` (role `configuration`)
- `strategies/generated/multi_timeframe/art_<12hex>_multi-timeframe/README.md` (role `documentation`)

Each entry records `bytes`, `sha256`, `change` (`create` on a fresh target, `conflict` if the
target already exists without an expected hash), and a unified `diff`. A `single_test` profile
instead renders one collected pytest under
`tests/functional/strategies/generated/multi_timeframe/test_art_<12hex>_multi-timeframe.py`.

```bash
backtrader-skills --target /path/to/backtrader \
  render validate --draft-id draft_...
```

A passing validation report (`status: passed`, zero errors, layers `python_ast`/`fork_api`/
`security: passed`, `artifact_integrity: passed`) returns a `render_write` approval token
(`tok_<64hex>`). Ask the user before approving; the token expires 15 minutes after issue by
default and is single-use.

```bash
backtrader-skills --target /path/to/backtrader \
  approval approve --token-id tok_...
backtrader-skills --target /path/to/backtrader \
  render apply --draft-id draft_... --token-id tok_...
```

`render apply` stages every byte first, writes the three files with a journal, and returns an
`artifact-apply-result-v1` with `draft_id`, `artifact_hash`, `transaction_id`, and the applied
`files` list. Only these applied, unchanged bytes can later pass `run prepare`.

## 4. Hand off

Forward the applied paths to the review skill (`review --file`) and then to the test skill
(`run prepare` / `run execute`). Never edit a generated file in place; change the typed spec and
re-render.
