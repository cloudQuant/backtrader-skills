# Iteration 29: Skill Grounding & Agent Quality — Acceptance

## Acceptance gates

| # | Gate | Command | Result |
| --- | --- | --- | --- |
| G-01 | Doctor | `python scripts/doctor.py --target /Users/yunjinqi/Documents/new_projects/backtrader` | PASS |
| G-02 | Manifest check | `python scripts/build_manifest.py --check` | PASS |
| G-03 | Catalog check | `python scripts/build_catalog.py --check` | PASS |
| G-04 | Tests (execution path) | `python -m pytest tests -q` with `BT_BACKTRADER_DIR=/Users/yunjinqi/Documents/new_projects/backtrader/backtrader` | PASS |
| G-05 | Coverage (≥ 80) | `python -m pytest tests -q --cov=src/backtrader_skills --cov-report=term-missing --cov-fail-under=80` (same `BT_BACKTRADER_DIR`) | PASS |
| G-06 | Mypy | `python -m mypy src/backtrader_skills` | PASS |
| G-07 | Ruff | `ruff check .` | PASS |
| G-08 | Black | `black --check .` | FAIL |
| G-09 | Full 7×2 matrix | `python scripts/run_acceptance.py --repository /Users/yunjinqi/Documents/new_projects/backtrader --matrix all --require-no-mcp --require-no-agent --output evidence/acceptance-7x2.json` | PASS |
| G-10 | Manifest rebuild + re-check | `python scripts/build_manifest.py` then `python scripts/build_manifest.py --check` | PASS |
| G-11 | Diff hygiene | `git diff --check` | PASS |

## Commands

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/doctor.py --target /Users/yunjinqi/Documents/new_projects/backtrader
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_manifest.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_catalog.py --check
BT_BACKTRADER_DIR=/Users/yunjinqi/Documents/new_projects/backtrader/backtrader /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m pytest tests -q
BT_BACKTRADER_DIR=/Users/yunjinqi/Documents/new_projects/backtrader/backtrader /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m pytest tests -q --cov=src/backtrader_skills --cov-report=term-missing --cov-fail-under=80
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m mypy src/backtrader_skills
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/run_acceptance.py --repository /Users/yunjinqi/Documents/new_projects/backtrader --matrix all --require-no-mcp --require-no-agent --output evidence/acceptance-7x2.json
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_manifest.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_manifest.py --check
git diff --check
~~~

## Execution evidence

Execution date: 2026-08-15; branch: `dev`.

| Gate | Actual result |
| --- | --- |
| G-01 | PASS. Doctor 15/15 checks passed. `no-sibling-product-imports`: observed `[]`, passed. `catalog-counts`: functional_tests 1152, mapped 1032, strategy_packages 1035. `target-backtrader-source` passed against `/Users/yunjinqi/Documents/new_projects/backtrader`; runtime provenance `CLOUDQUANT_BACKTRADER_VERIFIED`. |
| G-02 | PASS. `verified manifest: d7367bf7a78259e938422358c30e4bdca4ea2f9e0fcdad1531236c08d1e80894 (74 files)` (pre-rebuild baseline). |
| G-03 | PASS. `entries_verified: 1155`; header counts match the doctor catalog-counts. |
| G-04 | PASS. `94 passed in 24.49s`; `BT_BACKTRADER_DIR` was set, so execution-path tests ran rather than skipped. |
| G-05 | PASS. `TOTAL 2823 513 82%`; `Required test coverage of 80% reached. Total coverage: 81.83%`. |
| G-06 | PASS. `Success: no issues found in 28 source files`. |
| G-07 | PASS. `All checks passed!` |
| G-08 | FAIL. `1 file would be reformatted, 60 files would be left unchanged` — `would reformat tests/test_skill_reference_contract.py` (import line over 88 columns and non-parenthesized multi-line asserts). Per the controller ruling for this task, the file was not modified; the controller decides the response. |
| G-09 | PASS. 14/14 cells passed (7 archetypes × 2 output profiles). Top-level `passed: true`, `doctor_passed: true`, `require_no_mcp`/`require_no_agent: true`, sibling checks `agent_absent`/`mcp_absent: true`. Repair gate: `passed: true` with the 3 required scenarios (`multi_asset_allocation/single_test`, `multi_timeframe/python_bundle`, `precomputed_ml/single_test`) each going injected failure (`BT_LOOKAHEAD_POSITIVE_INDEX`) → `typed-ir-revision-and-rerender` → revalidation passed. Data-profile gate: passed, 6 declared adapters = 6 observed, 7 distinct dataset manifests. Clean-wheel result: mode `built-wheel-clean-install`, `wheel_sha256 173f02c2ec5ab08c18fddf3acc431c4e7e0f74b47e035a8a21d5d5ebc5ccb1d7`, `source_checkout_on_sys_path: false`, `installed_origin_verified: true`, `sibling_packages_absent: true`, `filelock 3.32.3` origin verified; installer smoke passed (host `codex`, all 3 canonical skills installed, 21 files). |
| G-10 | PASS. Evidence changed → manifest rebuilt to `d9893ec942e738b44a67513f94aad730adeb5e4da71e8109d9c02c781f1b956d (74 files)` and the read-only `--check` re-verifies the same hash. |
| G-11 | PASS. `git diff --check` produced no output (exit 0). |

## Delivered scope

Iteration 29 closes the four gap groups from the 2026-08-15 best-practice review. The three canonical
skills (backtrader-strategy-author/review/test) now ship complete reference contracts, diagnostic
catalogs, worked examples, failure playbooks, and pipeline handoffs, drift-locked to runtime facts
by tests. CI gains a master-only full-acceptance workflow that checks out the cloudQuant backtrader
fork and enforces an 80% coverage gate over `src/backtrader_skills`, with the full 7×2 acceptance
matrix run on master. A golden-prompt skill eval suite (seven archetype prompts plus adversarial and
cross-skill prompts) with a mechanical scorer and host runbook makes agent quality measurable.
Repo hygiene (CLAUDE.md, AGENTS.md, CHANGELOG, roadmap) lands with the version bump to 0.2.0.

## Verdict

10 of 11 gates pass cleanly; G-08 (Black) fails on one test file. Per the controller ruling, the
failure was recorded, not fixed, in this task. Release decision: **deferred to the controller**.
