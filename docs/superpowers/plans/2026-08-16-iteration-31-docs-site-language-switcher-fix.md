# Docs Site Language Switcher Fix Implementation Plan (Iteration 31)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Fix the broken language-switcher links on both deployed docs hosts. Root cause: without
`site_url`, mkdocs-static-i18n generates root-absolute alternate links (`/<locale>/`) that resolve
wrongly on GitHub Pages (project path `/backtrader-skills/`) and ReadTheDocs (`/en/latest/`
prefix). With `site_url` set, the plugin emits `<site_url path>/<locale>/`. Fix: a deterministic
build wrapper injects a host-specific `site_url` per pipeline; both hosts rebuild on the next
master push.

**Architecture:** `scripts/build_docs.py` reads `mkdocs.yml`, injects `site_url` from
`DOCS_SITE_URL` (default: the GitHub Pages URL), writes a temp config, and execs `mkdocs build`
with passthrough args. docs.yml and the CI quality job use it with the Pages URL;
`.readthedocs.yaml` switches to `build.commands` using the RTD URL and
`--site-dir $READTHEDOCS_OUTPUT/html`. Contract tests pin both pipelines and unit-test the
injection.

**Tech Stack:** Python 3.10+ stdlib (yaml via the installed pyyaml/mkdocs dependency), MkDocs,
GitHub Actions, ReadTheDocs build.commands.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- One deterministic wrapper; no sed-in-YAML; no new runtime dependencies (mkdocs already provides
  a yaml loader).
- Both deployed URLs must appear in contract tests exactly:
  `https://cloudquant.github.io/backtrader-skills/` and
  `https://backtrader-skills.readthedocs.io/en/latest/`.
- Local default build keeps current behavior (no env → Pages URL).
- Distribution files changed → `python scripts/build_manifest.py` rebuild.
- Deploy still master-push-only; PRs run the build gate only.

---

### Task 1: Host-aware site_url build wrapper + pipeline updates

**Files:**
- Add: `scripts/build_docs.py`
- Modify: `.github/workflows/docs.yml`, `.github/workflows/ci.yml`, `.readthedocs.yaml`, `CLAUDE.md`
- Modify: `tests/test_docs_site.py`, add focused unit test
- Modify: `CHANGELOG.md` (Unreleased), `manifest.json` (rebuild)

- [x] **Step 1: Unit test first (RED)**

Assert the wrapper's config-injection function: given mkdocs.yml bytes and a DOCS_SITE_URL value,
the produced config contains the injected site_url and is otherwise byte-equal modulo that line;
no env → Pages URL default.

- [x] **Step 2: Implement scripts/build_docs.py**

Read mkdocs.yml; inject/replace `site_url` from env (default Pages URL); write temp config;
exec `mkdocs build` with the temp config and passthrough args. Structured errors, no tracebacks.

- [x] **Step 3: Rewire the pipelines**

docs.yml: `DOCS_SITE_URL=https://cloudquant.github.io/backtrader-skills/ python scripts/build_docs.py --strict`.
ci.yml quality job: same command. `.readthedocs.yaml`: `build.commands` with
`DOCS_SITE_URL=https://backtrader-skills.readthedocs.io/en/latest/ python scripts/build_docs.py
--strict --site-dir $READTHEDOCS_OUTPUT/html` (follow the current RTD build.commands schema;
install docs extra via build.jobs or commands).

- [x] **Step 4: Contract tests GREEN**

Extend `tests/test_docs_site.py`: both pipelines invoke build_docs.py with their exact
DOCS_SITE_URL values; the quality job no longer calls bare `mkdocs build`. Update CLAUDE.md's
docs command to the wrapper.

- [x] **Step 5: Verify both host configurations locally**

Build with the Pages env → alternates must be `/backtrader-skills/zh/`; build with the RTD env →
alternates must be `/en/latest/zh/`. Record the grep evidence. Rebuild manifest + `--check`.

### Task 2: Acceptance and deploy

**Files:**
- Add: `docs/iterations/iteration-31-docs-site-language-switcher-fix/acceptance.md`
- Modify: plan checkboxes

- [x] **Step 1: Run all gates** — pytest, `python scripts/build_docs.py --strict` (both env
  variants), mypy, ruff, black, manifest/catalog checks.
- [x] **Step 2: Record evidence** — the two alternate-link greps, test counts, manifest hash.
- [x] **Step 3: Deploy note** — both hosts rebuild from the next master push (no manual steps).

## Self-Review

- Task 1 pins the injection behavior before the wrapper exists; Task 2 proves the exact
  alternate-link output per host, so the deployed switcher is verified before it ships.
