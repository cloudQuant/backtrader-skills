# Iteration 31: Docs Site Language Switcher Fix — Acceptance

## Acceptance gates

| # | Gate | Command | Result |
| --- | --- | --- | --- |
| G-01 | Tests (execution path) | `BT_BACKTRADER_DIR=/Users/yunjinqi/Documents/new_projects/backtrader/backtrader python -m pytest tests` | PASS |
| G-02 | Tests (plain) | `python -m pytest tests` | PASS |
| G-03 | Docs build (strict, Pages env) + alternate-link grep | `DOCS_SITE_URL=https://cloudquant.github.io/backtrader-skills/ python scripts/build_docs.py --strict -d /tmp/iter31-pages-site`; `grep '/backtrader-skills/zh/' site/index.html` | PASS |
| G-04 | Docs build (strict, RTD env) + alternate-link grep | `DOCS_SITE_URL=https://backtrader-skills.readthedocs.io/en/latest/ python scripts/build_docs.py --strict -d /tmp/iter31-rtd-site`; `grep '/en/latest/zh/' site/index.html` | PASS |
| G-05 | Mypy | `python -m mypy src/backtrader_skills` | PASS |
| G-06 | Ruff | `ruff check .` | PASS |
| G-07 | Black | `black --check .` | PASS |
| G-08 | Manifest check | `python scripts/build_manifest.py --check` | PASS |
| G-09 | Catalog check | `python scripts/build_catalog.py --check` | PASS |
| G-10 | Diff hygiene | `git diff --check` | PASS |
| G-11 | Cross-contamination negative greps | Pages build must not contain `/en/latest/zh/`; RTD build must not contain `/backtrader-skills/zh/` | PASS |

## Commands

~~~bash
BT_BACKTRADER_DIR=/Users/yunjinqi/Documents/new_projects/backtrader/backtrader /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m pytest tests
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m pytest tests
DOCS_SITE_URL=https://cloudquant.github.io/backtrader-skills/ /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_docs.py --strict -d /tmp/iter31-pages-site
grep -o '/backtrader-skills/zh/' /tmp/iter31-pages-site/index.html
DOCS_SITE_URL=https://backtrader-skills.readthedocs.io/en/latest/ /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_docs.py --strict -d /tmp/iter31-rtd-site
grep -o '/en/latest/zh/' /tmp/iter31-rtd-site/index.html
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m mypy src/backtrader_skills
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_manifest.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_catalog.py --check
git diff --check
~~~

## Execution evidence

Execution date: 2026-08-16; branch: `dev`; HEAD before acceptance edits: `e9043a1`.

| Gate | Actual result |
| --- | --- |
| G-01 | PASS. `111 passed in 20.45s` (exit 0); `BT_BACKTRADER_DIR` set, so execution-path tests ran rather than skipped. |
| G-02 | PASS. `111 passed in 19.99s` (exit 0), no `BT_BACKTRADER_DIR`. |
| G-03 | PASS. Exit 0, `INFO - Documentation built in 0.82 seconds`. Alternate-link grep in `/tmp/iter31-pages-site/index.html`: 2 matches — line 21 `<link rel="alternate" href="/backtrader-skills/zh/" hreflang="zh">` and line 134 `<a href="/backtrader-skills/zh/" hreflang="zh" class="md-select__link">`. The only output besides INFO is the informational Material banner about MkDocs 2.0; it is not a strict-mode warning and the build exited 0. |
| G-04 | PASS. Exit 0, `INFO - Documentation built in 0.79 seconds`. Alternate-link grep in `/tmp/iter31-rtd-site/index.html`: 2 matches — line 21 `<link rel="alternate" href="/en/latest/zh/" hreflang="zh">` and line 134 `<a href="/en/latest/zh/" hreflang="zh" class="md-select__link">`. Same informational banner as G-03; exit 0. |
| G-05 | PASS. `Success: no issues found in 28 source files`. |
| G-06 | PASS. `All checks passed!` |
| G-07 | PASS. `All done! ✨ 🍰 ✨` / `64 files would be left unchanged.` |
| G-08 | PASS. `verified manifest: a6a7307a4fb4b0c0adb8c28cc978815ee4d9fc20ee7081cf4cb4f36414a3e6c2 (75 files)`. |
| G-09 | PASS. Exit 0; `"entries_verified": 1155`. |
| G-10 | PASS. `git diff --check` produced no output (exit 0). |
| G-11 | PASS. Pages build: `grep -c '/en/latest/zh/'` → `0`; RTD build: `grep -c '/backtrader-skills/zh/'` → `0`. Each host's switcher links contain only its own site prefix. |

## Alternate-link evidence (the fix, proven per host)

The switcher alternates are derived from `site_url` at build time by the wrapper
(`scripts/build_docs.py`), so each pipeline produces its own absolute path prefix:

- **GitHub Pages build** (`DOCS_SITE_URL=https://cloudquant.github.io/backtrader-skills/`):

  ```
  /tmp/iter31-pages-site/index.html:21: <link rel="alternate" href="/backtrader-skills/zh/" hreflang="zh">
  /tmp/iter31-pages-site/index.html:134: <a href="/backtrader-skills/zh/" hreflang="zh" class="md-select__link">
  ```

  Resolves on Pages (project path `/backtrader-skills/`) to
  `https://cloudquant.github.io/backtrader-skills/zh/`.

- **ReadTheDocs build** (`DOCS_SITE_URL=https://backtrader-skills.readthedocs.io/en/latest/`):

  ```
  /tmp/iter31-rtd-site/index.html:21: <link rel="alternate" href="/en/latest/zh/" hreflang="zh">
  /tmp/iter31-rtd-site/index.html:134: <a href="/en/latest/zh/" hreflang="zh" class="md-select__link">
  ```

  Resolves on RTD (version prefix `/en/latest/`) to
  `https://backtrader-skills.readthedocs.io/en/latest/zh/`.

Both builds were run with `--strict` into `/tmp` output dirs (`-d`), so the repo `site/`
directory was not touched.

## Deploy note

No manual deploy steps. Both hosts rebuild automatically from the **next push to `master`**:

- **GitHub Pages** — `.github/workflows/docs.yml` (master-push trigger) runs the wrapper with
  `DOCS_SITE_URL=https://cloudquant.github.io/backtrader-skills/` and publishes `site/` to the
  `gh-pages` branch.
- **ReadTheDocs** — `.readthedocs.yaml` now uses `build.commands` with
  `DOCS_SITE_URL=https://backtrader-skills.readthedocs.io/en/latest/` and
  `--site-dir $READTHEDOCS_OUTPUT/html`; RTD rebuilds the default branch on every push.

The switcher links for each host are already proven correct by G-03/G-04 before the next
master push ships them.

## Delivered scope

Iteration 31 fixes the broken language-switcher links on both docs hosts. The deterministic
wrapper `scripts/build_docs.py` injects a host-specific `site_url` into a temp copy of
`mkdocs.yml` (the checked-in config is never modified) and execs `mkdocs build` with passthrough
args; without the env var it keeps the Pages URL, preserving local behavior. The docs deploy
workflow and the CI quality job call the wrapper with the Pages URL, while `.readthedocs.yaml`
switches to `build.commands` with the RTD URL and `--site-dir $READTHEDOCS_OUTPUT/html`.
Contract tests (`tests/test_docs_site.py`) pin both pipelines and unit-test the injection.

## Verdict

All eleven gates (G-01–G-11) pass cleanly with zero code changes required during acceptance.
The two alternate-link greps prove the exact per-host output the switcher needs — Pages emits
`/backtrader-skills/zh/`, RTD emits `/en/latest/zh/` — so the deployed switcher is verified
before it ships. Release decision: **deferred to the controller**.
