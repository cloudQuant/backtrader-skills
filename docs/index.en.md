# backtrader-skills

`backtrader-skills` is an offline, independently installable author/review/test product for this
Backtrader fork: it turns a registered local dataset and a typed `StrategySpec v1` into a collected
pytest strategy or a three-file Python bundle, reviews the candidate without importing it, and runs
approved candidates in separate runonce/runnext child processes.

It does not import or start sibling MCP or Agent products. The bundled catalog snapshot contains
metadata for 1,152 functional strategy tests and 1,035 three-file packages, with 1,032 mapped IDs,
so normal operation does not require either source corpus. The project follows Semantic Versioning;
the current release is 0.2.0.

## Site pages

- [Skills](skills.md) — the three canonical skills and their pipeline.
- [Evaluations](evals.md) — the golden/adversarial prompt suite and scorer.
- [Changelog](changelog.md) — release history (Keep a Changelog).
- [Roadmap](roadmap.md) — the P1 backlog and sourced limits.

## Required Backtrader source

The only Backtrader source accepted for strategy execution and acceptance is
[`cloudQuant/backtrader`](https://github.com/cloudQuant/backtrader). A matching package name or
version number is not sufficient: the tool verifies the Git remote, or PEP 610 installation
metadata that leads back to that remote.

Run `doctor` before using the product. If the active Python environment has no `backtrader`,
doctor installs `git+https://github.com/cloudQuant/backtrader.git` with that same interpreter
and verifies it again. An existing package that cannot be proven to be the cloudQuant fork
yields `BACKTRADER_SOURCE_WARNING`; it is not silently replaced, and `run` uses the same
preflight, writing that warning to stderr. Every `--target` and source-checkout `--repository`
is also required to be a cloudQuant Git checkout; a valid-looking package from another fork is
rejected with `BACKTRADER_SOURCE_MISMATCH`.

## Get started

From the `backtrader-skills` checkout, activate any supported Python 3.10–3.13 environment and
install the distribution:

```bash
python -m pip install .
backtrader-skills --target /path/to/backtrader doctor
```

Runtime state — dataset objects, manifests, drafts, token digests, and run evidence — is
always `<target>/.backtrader-skills/`. The 256-bit token handle is returned once to the caller
and never persisted in plaintext. `doctor` records the actual interpreter and environment used
by the installed command.

## Install the three canonical skills

The same distribution supports four project-level layouts:

| Host | Destination |
| --- | --- |
| Claude Code | `.claude/skills/backtrader-*` |
| Codex | `.agents/skills/backtrader-*` |
| OpenCode | `.opencode/skills/backtrader-*` |
| OpenClaw | `<workspace>/skills/backtrader-*` |

Preview, approve, and apply:

```bash
BT_TARGET=/path/to/backtrader

backtrader-skills --target "$BT_TARGET" \
  install preview --host codex
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  install apply --plan-id install_codex_... --token-id tok_...
```

Use `claude`, `opencode`, or `openclaw` for the other native locations. Installation is
create-only; for OpenClaw, `BT_TARGET` must be the actual agent workspace root (the installer
does not register an OpenClaw agent for you). Uninstall follows the same preview → approve →
apply pattern; files whose hash changed after installation are preserved.

## Verify discovery and make the first request

Applying an install plan proves that the canonical files reached the native directory; it does
not prove that an external model session discovered them. Reload the project or start a new host
session after installation, then send this read-only first request (substituting the Backtrader
project root for `/path/to/backtrader`):

```text
Without writing any files, use the backtrader-strategy-author skill. Run:
backtrader-skills --target /path/to/backtrader doctor
Return the doctor pass/fail result, the no-sibling-product-imports check, and the catalog counts.
```

The expected smoke result has `passed=true`, a passing `no-sibling-product-imports` check, and
the verified catalog baseline `1,152/1,035/1,032`; a host that cannot name or load the skill has
not completed discovery.

- Claude Code: confirm `.claude/skills/backtrader-strategy-author/SKILL.md` exists, restart the
  session, and prefix the request with "use the `backtrader-strategy-author` skill".
- Codex: confirm `.agents/skills/backtrader-strategy-author/SKILL.md` exists, start a new task,
  and invoke the skill with:

  ```text
  $backtrader-strategy-author Perform the read-only doctor smoke described above.
  ```

- OpenCode: confirm `.opencode/skills/backtrader-strategy-author/SKILL.md` exists, reload the
  project, and ask for "load and use the `backtrader-strategy-author` skill" first.
- OpenClaw: confirm `skills/backtrader-strategy-author/SKILL.md` exists below an existing,
  registered workspace, and ask the agent to "use the workspace skill
  `backtrader-strategy-author`". Its layout and protected uninstall are statically tested; live
  discovery remains unchecked until an installed OpenClaw agent completes the smoke above.

## Register local data

P0 accepts only offline local files inside explicitly registered, read-only roots; portable
manifests contain an opaque root ID and relative path, never the local absolute path.

```bash
backtrader-skills --target "$BT_TARGET" \
  data root-add --directory /path/to/fixtures --root-id prices
backtrader-skills --target "$BT_TARGET" \
  data inspect --feed-spec feed.json
backtrader-skills --target "$BT_TARGET" \
  data register --spec data-spec.json
backtrader-skills --target "$BT_TARGET" \
  data preview --dataset-id 'ds_<64hex>' --rows 5
```

`DataSpec` supports multiple named feeds, roles, timeframe/compression, timezone, explicit
column mapping, deterministic transforms, and `intersection|left|explicit_asof` declarations.
Registration normalizes header-based CSV/tabular inputs to UTF-8 canonical CSV, validates
timestamps, finite OHLC, ordering and duplicates, and stores content-addressed objects. Formats
are `generic_csv`, `backtrader_csv`, `yahoo_csv`, `mt5_csv`, `pandas`, and `pandas_custom_lines`;
Pandas profiles consume a safely materialized CSV, never pickle or a callable. Any source-byte
change invalidates the manifest and its approvals.

## Author and apply

Search the shipped catalog and create a scaffold:

```bash
backtrader-skills --target "$BT_TARGET" \
  catalog search --query "multi timeframe momentum" --archetype multi_timeframe
backtrader-skills --target "$BT_TARGET" \
  spec scaffold --archetype multi_timeframe --output-profile python_bundle \
  --dataset-id 'ds_<64hex>' --feed-count 2 > strategy-spec.json
```

Validate the JSON (removing any surrounding CLI presentation), then use the two-phase writer:

```bash
backtrader-skills --target "$BT_TARGET" \
  spec validate --spec strategy-spec.json
backtrader-skills --target "$BT_TARGET" \
  render preview --spec strategy-spec.json
backtrader-skills --target "$BT_TARGET" \
  render validate --draft-id draft_...
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  render apply --draft-id draft_... --token-id tok_...
```

Bundles are created under `strategies/generated/`, collected generated tests under
`tests/functional/strategies/generated/`; existing files require an explicit expected hash.
Multi-file apply stages every byte first and uses a journal plus rollback, so a later-file
failure does not leave a partially applied bundle. All seven archetypes-single-data indicator,
multi-indicator, multi-asset allocation, multi-timeframe, pairs/spread, order/risk, and
precomputed/ML signal-use the same restricted Expression/Action/StateRule IR for both output
profiles. Direct `bt.Strategy` templates intentionally do not call `super().__init__()` in this
fork.

## Review, repair, and run

```bash
backtrader-skills --target "$BT_TARGET" \
  review --file "$BT_TARGET/strategies/generated/.../strategy.py"
backtrader-skills --target "$BT_TARGET" \
  repair --draft-id draft_...
backtrader-skills --target "$BT_TARGET" \
  run prepare --candidate "$BT_TARGET/strategies/generated/.../strategy.py" \
  --dataset-id 'ds_<64hex>'
backtrader-skills --target "$BT_TARGET" \
  approval approve --token-id tok_...
backtrader-skills --target "$BT_TARGET" \
  run execute --run-id run_... --token-id tok_...
```

When a diagnostic requires a semantic change, revise the typed spec and bind it to the failed
ValidationReport: `repair --spec revised-strategy-spec.json --validation-report failed-validation.json`.

The controller never imports candidate code. It proves the candidate is an unchanged artifact
from an approved render/apply, recomputes candidate, dataset, source-data, and environment
hashes, consumes a separate execution approval, and invokes the distribution's active Python
interpreter with `-I` for each mode. Approval capabilities expire after 15 minutes by default
and end in `CONSUMED`, `REVOKED`, or `EXPIRED`.

## Security and current limits

- P0 runs only product-generated and explicitly approved candidates. Unknown code may receive
  a static review but cannot receive a run token.
- Generated candidates may import only top-level `backtrader`. AST gates reject controller and
  filesystem imports, dynamic execution/import, subprocess, known network clients, sockets,
  live stores, absolute paths, traversal, and positive line offsets.
- `python -I` child isolation is not a complete OS sandbox (no network namespace, container,
  seccomp, or resource cgroup), and data is offline and header-based: no download, database,
  API key, pickle, live feed, or arbitrary loader/callable is accepted.
- Alignment (`intersection`, `left`, or `explicit_asof`), resample, and replay intent is frozen
  in the DatasetManifest and validated before feed assembly; the P0 runner delegates bar-clock
  advancement to Backtrader and never silently fills missing bars or changes calendars.
- The automated P0 runner proves runonce/runnext parity. A separately checked-out, human-
  approved master/dev financial baseline remains an explicit release workflow, not an inferred
  expected return.
- Host-client UI discovery cannot be emulated without each client binary; product tests verify
  the four native paths, skill metadata, forwarders, conflicts, and protected uninstall.
  General concurrent CLI invocations against the same `--target` remain unsupported: run one
  command at a time per target.
- A single approval token is protected across local processes: render apply and install or
  uninstall hold a per-token lock through their protected writes, while run atomically consumes
  its token before launching child processes; at most one operation can consume the same token.

## Verify the distribution

Run these commands from the `backtrader-skills` checkout with the intended environment
activated. The source-checkout helpers locate a Backtrader repository only when this product is
nested below it or next to a sibling directory named `backtrader`; they return
`SOURCE_CHECKOUT_NOT_FOUND` when neither layout exists and `BACKTRADER_SOURCE_MISMATCH` for
another fork, rather than guessing.

```bash
# Automatic discovery for a nested or sibling Backtrader checkout
python scripts/doctor.py
python scripts/build_manifest.py --check
python scripts/build_catalog.py --check
python -m pytest tests -q
python scripts/run_acceptance.py \
  --matrix all --require-no-mcp --require-no-agent

# A Backtrader checkout in any other location
python scripts/doctor.py --target /path/to/backtrader
python scripts/run_acceptance.py --repository /path/to/backtrader \
  --matrix all --require-no-mcp --require-no-agent
```

After changing a distribution-included file, rebuild the tracked manifest with
`python scripts/build_manifest.py`; `--check` and `--help` are read-only validations that leave
`manifest.json` unchanged.

Continuous integration enforces this on every push to `master`: a dedicated acceptance job
checks out the cloudQuant Backtrader fork, runs the full suite with an 80% coverage gate over
`src/backtrader_skills` (except the two `python -I` child modules), then runs the complete 7×2
acceptance matrix; pull requests keep the lighter quality and supported-Python jobs.

The acceptance command builds a wheel, installs it into an isolated directory, exposes only
the Backtrader source package to a clean fixture repository, and runs the full 7×2 matrix from
that installed distribution with the source checkout absent from `sys.path`, including the
structured failure -> typed-IR repair -> revalidation -> approved dual-mode gate.
