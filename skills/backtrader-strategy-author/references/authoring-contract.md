# Authoring contract

Canonical StrategySpec output uses `spec_version=strategy-spec-v1`, name, slug, category, one of the
seven archetypes, output profile, full DatasetManifest ID, feeds, typed parameters, entry/exit
StateRule references, sizing, risk, run modes, allowed imports, and a restricted `strategy-ir-v1`.

## Archetypes

| Archetype | Purpose | Feed shape | Typical entry/exit |
| --- | --- | --- | --- |
| `single_data_indicator` | One execution feed driven by indicators computed on that feed | 1 feed, role `execution` | Fast/slow SMA cross over/under (`cross_up` / `cross_down`) |
| `multi_indicator_system` | Combine several indicators on one feed | 1 feed, role `execution` | Fast/slow SMA cross, extended with further indicator expressions |
| `multi_asset_allocation` | Route orders across several feeds | At least 2 feeds; index 0 is `execution`, the rest `signal` | Cross-based entry on the indicator feed; `feed` field on each Action selects the order target |
| `multi_timeframe` | Signal from one timeframe, execution on another | 2 feeds; indicators are computed on feed 1 (`signal`) | Fast/slow SMA cross computed on the signal feed; orders on feed 0 |
| `pairs_spread` | Trade the spread of two price series | 2 feeds | Entry when `close[feed 0] - close[feed 1] > 0` (`sub` of two `data_line` nodes compared by `gt`); exit cross under |
| `order_risk` | Entry plus stop/target bracket on one feed | 1 feed, role `execution` | Market entry plus `set_stop` at `close * 0.95` and `set_target` at `close * 1.10` |
| `precomputed_ml` | Trade a precomputed custom line | 1 feed with a `custom_lines` entry such as `signal` | Entry when `signal > 0`, exit when `signal <= 0` (`data_line` on the custom line compared by `gt`/`lte`) |

All seven archetypes use the same restricted Expression/Action/StateRule IR for both output
profiles. The scaffold for `multi_timeframe` places indicators on feed 1; `multi_asset_allocation`
and `pairs_spread` force at least two feeds; `precomputed_ml` thresholds read the declared custom
line. Direct `bt.Strategy` templates intentionally omit `super().__init__()` in this fork.

## Output profiles

| Profile | Renderer output |
| --- | --- |
| `single_test` | One collected pytest file: `tests/functional/strategies/generated/<archetype>/test_<artifact_id>_<slug>.py` |
| `python_bundle` | Three files under `strategies/generated/<archetype>/<artifact_id>_<slug>/`: `strategy.py`, `config.json`, `README.md` |

`artifact_id` is `art_` plus the first 12 hex characters of the canonical spec hash. Both profiles
render from the same validated IR; do not hand-write a second implementation.

## Expression grammar

An Expression is an object with `kind` set to one of six values and a maximum nesting depth of 20:

| Kind | Form | Validation |
| --- | --- | --- |
| `constant` | `{"kind": "constant", "value": <finite bool/int/float>}` | Scalar must be finite |
| `parameter` | `{"kind": "parameter", "name": "<name>"}` | Name must be declared in `parameters` |
| `data_line` | `{"kind": "data_line", "feed": <index>, "line": "<line>", "offset": <int>}` | Feed within `0..feed_count-1`; line in the six data lines or custom lines; offset `-10000..0` |
| `indicator` | `{"kind": "indicator", "name": "<id>", "offset": <int>}` | Id declared in `ir.indicators`; offset `-10000..0` |
| `state` | `{"kind": "state", "name": "<name>"}` | Name declared in `ir.state_variables` |
| `operator` | `{"kind": "operator", "op": "<op>", "args": [<Expression>...]}` | Op in the operator table; arity checked per op |

Positive offsets are look-ahead and are forbidden. Data lines are `open`, `high`, `low`, `close`,
`volume`, `openinterest` plus declared `custom_lines`. Parameter types are `int`, `float`, `bool`,
`str`; `int` defaults reject bools, `float` defaults must be finite, and `minimum`/`maximum` bounds
are enforced.

## Operators

| Operator | Arity | Meaning |
| --- | --- | --- |
| `and` | 2..16 | True if all arguments are truthy |
| `or` | 2..16 | True if any argument is truthy |
| `not` | 1 | Logical negation |
| `eq` | 2 | Equal |
| `ne` | 2 | Not equal |
| `gt` | 2 | Greater than |
| `gte` | 2 | Greater than or equal |
| `lt` | 2 | Less than |
| `lte` | 2 | Less than or equal |
| `add` | 2..16 | Sum of arguments |
| `sub` | 2 | First argument minus second |
| `mul` | 2..16 | Product of arguments |
| `div` | 2 | First argument divided by second |
| `abs` | 1 | Absolute value |
| `min` | 2..16 | Minimum of arguments |
| `max` | 2..16 | Maximum of arguments |
| `cross_up` | 2 | `a[0] > b[0]` and `a[-1] <= b[-1]` |
| `cross_down` | 2 | `a[0] < b[0]` and `a[-1] >= b[-1]` |
| `highest` | 2 | Maximum of the first argument over the last `period` bars; second argument must be an integer constant in `1..10000` |
| `lowest` | 2 | Minimum of the first argument over the last `period` bars; second argument must be an integer constant in `1..10000` |

The table is the complete operator vocabulary. Any other `op` is rejected as an unsupported
operator.

## StateRule and Action form

A StateRule has `name`, `stage`, `when` (one Expression), `actions` (a non-empty list), `priority`
(int, default 100), and optional `exclusive_group`. Stages are `prenext`, `nextstart`, `next`, or
`always`; `always` rules fire in every stage. In a stage, at most one rule per fired
`exclusive_group` runs, in ascending `(priority, name)` order.

Actions have `kind` in `buy`, `sell`, `close`, `cancel`, `set_stop`, `set_target` and a `feed`
index:

- `buy`/`sell`: `order_type` in `market`, `limit`, `stop`; optional `size` Expression; `limit` and
  `stop` require a `price` Expression.
- `close`: close the position on the feed.
- `cancel`: cancel the tracked order on the feed.
- `set_stop`/`set_target`: require a `price` Expression evaluated each bar; positions are closed
  when the feed close crosses the stored stop or target level.

`entry`/`exit` reference StateRule names through `{"rule_names": [...]}`. At least one entry rule
and one exit rule must exist and be referenced. The scaffold defaults are `enter` (priority 10) and
`exit` (priority 20), both in `exclusive_group` `position`, staged at `next`.

## Canonical StrategySpec fields

Normalized output of `spec validate` (schema required fields are `spec_version`, `name`, `slug`,
`category`, `archetype`, `output_profile`, `dataset_id`, `feeds`, `parameters`, `entry`, `exit`,
`sizing`, `risk`, `run_modes`, `allowed_imports`, `spec_hash`):

| Field | Contract |
| --- | --- |
| `spec_version` | `strategy-spec-v1` |
| `name` | 1 to 100 characters |
| `slug` | Lowercase kebab-case, `[a-z][a-z0-9-]{0,62}` |
| `category` | Free text; defaults to the archetype |
| `archetype` | One of the seven archetype values above |
| `output_profile` | `single_test` or `python_bundle` |
| `dataset_id` | `ds_` plus the full 64-hex semantic hash; bind only the full ID |
| `feeds` | 1..32 entries: `name` (unique), `role` in `execution`, `signal`, `benchmark`, `hedge`, `cash_proxy`, `symbol`, `timeframe` (default `manifest`), `lines` |
| `parameters` | Named typed defaults as above |
| `entry` / `exit` | `{"rule_names": [...]}` |
| `sizing` | `{"type": "fixed", "stake": <int >= 1>}`; P0 supports fixed positive stake only |
| `risk` | Free object; the scaffold sets `live_trading: false`, `profit_guarantee: false`, and the entry/exit `rule_names` |
| `cash` / `commission` | Finite positive cash; finite non-negative commission |
| `run_modes` | Exactly `["runonce", "runnext"]` |
| `allowed_imports` | Exactly `["backtrader"]` |
| `non_goals` / `undecided` | String lists |
| `ir` | `ir_version: strategy-ir-v1`, `custom_lines`, `indicators` (id, type in `sma`, `ema`, `rsi`, `atr`, `stddev`, feed, line, period int in `1..10000` or a parameter name), `state_variables` (name, finite scalar `initial`), `state_rules`, `minperiod` (positive) |
| `extensions` | `backtrader_skills.analyzers`: `sharpe_ratio`, `annual_return`, `max_drawdown`, `trade_analyzer` |
| `spec_hash` | Canonical hash computed by the validator; never hand-written |

## Two-phase write contract

`render preview` stores candidate bytes and a hash manifest under the runtime root. `render
validate` creates a hash-bound, expiring issued capability. Only an explicitly approved,
unconsumed token can apply those exact bytes. The persisted record contains only the token digest.
Existing targets require an expected hash; create-only is the default. Multi-file apply stages all
bytes first and uses a journal plus rollback.

Runtime state stays under `<target>/.backtrader-skills/`. Generated bundles live only under
`strategies/generated/`; collected generated tests only under
`tests/functional/strategies/generated/`.
