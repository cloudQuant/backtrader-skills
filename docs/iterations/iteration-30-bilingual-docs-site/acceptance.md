# Iteration 30: Bilingual Docs Site — Acceptance

## Acceptance gates

| # | Gate | Command | Result |
| --- | --- | --- | --- |
| G-01 | Tests (execution path) | `BT_BACKTRADER_DIR=/Users/yunjinqi/Documents/new_projects/backtrader/backtrader python -m pytest tests` | PASS |
| G-02 | Tests (plain) | `python -m pytest tests` | PASS |
| G-03 | Docs build (strict) | `mkdocs build --strict` | PASS |
| G-04 | Site structure | en nav pages at `site/` root, zh at `site/zh/`; `find site \( -path '*superpowers*' -o -path '*iterations*' \)` | PASS |
| G-05 | Mypy | `python -m mypy src/backtrader_skills` | PASS |
| G-06 | Ruff | `ruff check .` | PASS |
| G-07 | Black | `black --check .` | PASS |
| G-08 | Manifest check | `python scripts/build_manifest.py --check` | PASS |
| G-09 | Catalog check | `python scripts/build_catalog.py --check` | PASS |
| G-10 | GitHub Pages enable | `gh api -X POST repos/cloudQuant/backtrader-skills/pages -f 'source[branch]=gh-pages' -f 'source[path]=/'` | BLOCKED |
| G-11 | Diff hygiene | `git diff --check` | PASS |

## Commands

~~~bash
BT_BACKTRADER_DIR=/Users/yunjinqi/Documents/new_projects/backtrader/backtrader /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m pytest tests
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m pytest tests
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base mkdocs build --strict
find site \( -path '*superpowers*' -o -path '*iterations*' \)
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -m mypy src/backtrader_skills
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_manifest.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python scripts/build_catalog.py --check
gh api -X POST repos/cloudQuant/backtrader-skills/pages -f 'source[branch]=gh-pages' -f 'source[path]=/'
git diff --check
~~~

## Execution evidence

Execution date: 2026-08-15; branch: `dev`; HEAD before acceptance edits: `992fb07`.

| Gate | Actual result |
| --- | --- |
| G-01 | PASS. `101 passed in 20.50s` (exit 0); `BT_BACKTRADER_DIR` set, so execution-path tests ran rather than skipped. |
| G-02 | PASS. `101 passed in 18.65s` (exit 0), no `BT_BACKTRADER_DIR`. |
| G-03 | PASS. Exit 0, `INFO - Documentation built in 0.90 seconds`; en built to `site/`, zh to `site/zh`. The only output besides INFO is an informational banner from the Material theme ("WARNING – MkDocs 2.0 is incompatible with Material for MkDocs"); it is not a strict-mode build warning and the build exited 0. |
| G-04 | PASS. `site/` contains the five en nav pages (`index.html`, `skills/`, `evals/`, `changelog/`, `roadmap/`) plus `sitemap.xml`, `search/`, `assets/`, `404.html`; `site/zh/` contains the same five zh pages. The `find` command for `superpowers`/`iterations` paths produced no output, confirming the `exclude_docs` dev artifacts are absent from the published site. |
| G-05 | PASS. `Success: no issues found in 28 source files`. |
| G-06 | PASS. `All checks passed!` |
| G-07 | PASS. `All done! ✨ 🍰 ✨` / `62 files would be left unchanged.` (The iteration-29 G-08 black failure on `tests/test_skill_reference_contract.py` is resolved.) |
| G-08 | PASS. `verified manifest: 4048c26eda8ff512c572114c453af5efb61270ed49f5f1bbf0cd6ac98f0b494a (74 files)`. |
| G-09 | PASS. Exit 0; `"entries_verified": 1155`. |
| G-10 | BLOCKED (environmental, not a product failure). The API call returned `HTTP 422` with message `The gh-pages branch must exist before GitHub Pages can be built.` The repo currently has no `gh-pages` branch (verified via `gh api repos/cloudQuant/backtrader-skills/branches`: only `master`, `dev`, `codex/continuous-optimization`, `improve-quality-gates`), because the master-only `docs.yml` deploy workflow has not run yet — `peaceiris/actions-gh-pages` creates the branch on its first publish. Pages is not yet enabled (`GET /pages` → 404). This is not a permissions/scope failure. One attempt was made, exactly as ruled; no alternate API shape was retried. |
| G-11 | PASS. `git diff --check` produced no output (exit 0). |

## GitHub Pages enablement

**API outcome.** The exact command from the controller ruling failed with `HTTP 422: The gh-pages branch
must exist before GitHub Pages can be built.` Root cause: no `gh-pages` branch exists yet. The
`.github/workflows/docs.yml` workflow runs only on pushes to `master` and creates the `gh-pages` branch
via `peaceiris/actions-gh-pages@v4` on its first successful publish. This acceptance task commits to
`dev` only (no push), so the branch cannot exist until the first master-push pipeline run.

**Workflow permission fix (this iteration).** `docs.yml` now declares `permissions: contents: write`
on the build job, so the peaceiris `gh-pages` push will not fail with 403 on repositories whose
workflow tokens default to read-only. `tests/test_docs_site.py` pins `contents: write` with a new
assertion in `test_docs_workflow_publishes_the_site_on_master_push_only`.

**Manual steps for the user (Settings → Pages).** After the first successful `docs.yml` run on
`master` has created the `gh-pages` branch:

1. Open the repository on github.com: `cloudQuant/backtrader-skills` → **Settings**.
2. In the left sidebar, click **Pages** (under "Code and automation").
3. Under **Build and deployment → Source**, select **Deploy from a branch**.
4. Under **Branch**, select **gh-pages** and **/ (root)**, then click **Save**.
5. Wait for the deployment; verify the bilingual site at
   `https://cloudquant.github.io/backtrader-skills/` (English at the root, Chinese at `/zh/`).

Alternatively, once the `gh-pages` branch exists, the same API command can be re-run:

```bash
gh api -X POST repos/cloudQuant/backtrader-skills/pages -f 'source[branch]=gh-pages' -f 'source[path]=/'
```

## ReadTheDocs import status

Not yet imported: RTD import requires the owner's readthedocs.org account and cannot be performed by
automation in this task. The repository is fully prepared (`.readthedocs.yaml` builds the mkdocs site
with Python 3.11 and the `docs` extra). Exact steps for the user:

1. Go to <https://readthedocs.org> and **Sign in with GitHub** (the same account that owns
   `cloudQuant/backtrader-skills`).
2. Click **Import a Project** and select **cloudQuant/backtrader-skills** from the repository list.
   If prompted, authorize the Read the Docs GitHub app to access the repository.
3. RTD auto-detects `.readthedocs.yaml` (mkdocs build, Python 3.11, `docs` extra) — accept the
   detected configuration; no manual settings are needed.
4. Trigger the first build (**Build version → Build**) and verify the bilingual site at
   <https://backtrader-skills.readthedocs.io/> (English default, Chinese at `/zh/`).

## Site URL notes

- **GitHub Pages** (after the steps above): `https://cloudquant.github.io/backtrader-skills/` —
  published by `.github/workflows/docs.yml` on every push to `master`, from `site/` to the
  `gh-pages` branch; English at the site root, Chinese under `/zh/`.
- **ReadTheDocs** (after import): `https://backtrader-skills.readthedocs.io/` — built by RTD from
  `.readthedocs.yaml` on every push to the default branch.
- Dev artifacts (`docs/superpowers/`, `docs/iterations/`, `.superpowers/`) are excluded from the
  published site via the `exclude_docs` block in `mkdocs.yml` and verified by G-04.

## Delivered scope

Iteration 30 ships the bilingual MkDocs Material documentation site: five nav pages in English and
Chinese (`index`, `skills`, `evals`, `changelog`, `roadmap`) wired through the
`mkdocs-static-i18n` plugin in fallback-free suffix mode (every page must exist in both languages or
the strict build fails), with `exclude_docs` keeping developer plan and acceptance artifacts out of
the published site. The master-only `docs.yml` deploy workflow (peaceiris → `gh-pages` branch) gains
the `contents: write` permission fix carried from the T1 review, pinned by a contract-test
assertion. `.readthedocs.yaml` prepares the RTD import. Contract tests (`tests/test_docs_site.py`)
pin the mkdocs config, bilingual page coverage, the RTD config, the deploy workflow, and the
CI quality-job docs gate. README and `IMPLEMENTATION_REPORT.md` gain the docs-site links and eval
section.

## Verdict

All ten code gates (G-01–G-09, G-11) pass cleanly with zero product-code changes required during
acceptance. G-10 (GitHub Pages enablement) is blocked by a pre-existing environmental condition —
the `gh-pages` branch cannot exist until the first master-push deploy — and is handed to the user as
recorded manual steps, along with the RTD import steps. Release decision: **deferred to the
controller**; no version bump applied per the controller ruling.
