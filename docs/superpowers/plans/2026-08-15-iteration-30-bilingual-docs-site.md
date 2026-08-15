# Bilingual Docs Site & README Update Implementation Plan (Iteration 30)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Publish a bilingual (EN + 中文) MkDocs Material site from `docs/` to GitHub Pages (master push only) and ReadTheDocs, wire a docs-drift contract test and a `mkdocs build --strict` CI gate, and close the README gaps (eval section, docs-site links, IMPLEMENTATION_REPORT staleness note).

**Architecture:** `docs/` becomes the MkDocs source with `mkdocs-static-i18n` suffix structure
(`<page>.en.md` / `<page>.zh.md`, default English). Nav: index, skills, evals, changelog, roadmap —
plans/iterations stay out of the nav. GitHub Pages deploys via `peaceiris/actions-gh-pages` from
`.github/workflows/docs.yml` (push to master only); the existing CI `quality` job gains a
`mkdocs build --strict` gate; `.readthedocs.yaml` (MkDocs, docs extra) lets RTD build automatically
once the user imports the repo on readthedocs.org. Contract tests pin the whole wiring.

**Tech Stack:** MkDocs + Material, mkdocs-static-i18n, GitHub Actions, ReadTheDocs v2 config,
pytest contract tests (existing pattern).

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- Site is bilingual: every nav page ships as `.en.md` + `.zh.md`; content adapted from existing
  docs (README EN/中文, evals/README.md, CHANGELOG, roadmap) — do not invent product claims.
- Deploy runs on master push only; PRs run only the build gate (consistent with the acceptance
  workflow decision).
- TDD: contract tests written first, RED recorded, then wiring/content until GREEN.
- `mkdocs build --strict` must pass locally before any commit touching the site.
- Distribution files changed → `python scripts/build_manifest.py` rebuild.
- Docs are dense and factual, matching repo tone. No secrets in workflows.

---

### Task 1: Docs infrastructure + contract tests (RED)

**Files:**
- Add: `tests/test_docs_site.py`, `mkdocs.yml`, `.readthedocs.yaml`, `.github/workflows/docs.yml`
- Modify: `pyproject.toml` (docs extra + dev extra), `.github/workflows/ci.yml` (quality job)

- [ ] **Step 1: Write the docs-site contract tests first**

Assert: `mkdocs.yml` exists and configures `mkdocs-static-i18n` with languages `en`+`zh`; nav lists
`index.md, skills.md, evals.md, changelog.md, roadmap.md`; for every nav page BOTH
`docs/<page>.en.md` and `docs/<page>.zh.md` exist; `.readthedocs.yaml` is v2 and points at
`mkdocs.yml`; `docs.yml` triggers only on push to master and runs `mkdocs build --strict` with a
Pages publish step; the CI `quality` job contains `mkdocs build --strict`; pyproject `docs` extra
declares `mkdocs-material` and `mkdocs-static-i18n`, and `dev` extra includes the docs extra.

- [ ] **Step 2: Run the tests against the current tree**

Expected: FAIL (none of the site artifacts exist).

- [ ] **Step 3: Add the configuration**

mkdocs.yml (Material theme, i18n plugin with English default and zh fallback-free setup, strict),
`.readthedocs.yaml`, `.github/workflows/docs.yml` (master-only; install `.[docs]`; `mkdocs build
--strict`; publish with `peaceiris/actions-gh-pages@v4`), pyproject extras, quality-job gate.

- [ ] **Step 4: Contract tests GREEN; `mkdocs build --strict` still fails on missing pages**

Expected: the config assertions pass; the build fails until Task 2/3 content lands. Record both.

### Task 2: English site content

**Files:**
- Add: `docs/index.en.md`, `docs/skills.en.md`, `docs/evals.en.md`, `docs/changelog.en.md`, `docs/roadmap.en.md`

- [ ] **Step 1: index.en.md** — landing page adapted from the README English sections: what the
  product is, install, doctor, data registration, author/review/test flows, security limits,
  verification, links to skills/evals pages.
- [ ] **Step 2: skills.en.md** — the three canonical skills, their pipeline (author → review →
  test, repair loop), pointers to the shipped references.
- [ ] **Step 3: evals.en.md** — golden/adversarial prompt suite, mechanical scorer usage, host
  runbook summary (adapted from evals/README.md).
- [ ] **Step 4: changelog.en.md + roadmap.en.md** — changelog adapted from CHANGELOG.md;
  roadmap copied from docs/roadmap.md content.
- [ ] **Step 5: `mkdocs build --strict` passes for English**

### Task 3: Chinese site content

**Files:**
- Add: `docs/index.zh.md`, `docs/skills.zh.md`, `docs/evals.zh.md`, `docs/changelog.zh.md`, `docs/roadmap.zh.md`

- [ ] **Step 1: index.zh.md** — adapted from the README 中文 sections, mirroring index.en.md structure.
- [ ] **Step 2: skills.zh.md + evals.zh.md** — translations mirroring the English pages.
- [ ] **Step 3: changelog.zh.md + roadmap.zh.md** — translated changelog entries and roadmap rows.
- [ ] **Step 4: `mkdocs build --strict` passes for both languages; contract tests stay green**

### Task 4: README and IMPLEMENTATION_REPORT updates

**Files:**
- Modify: `README.md` (EN + 中文), `IMPLEMENTATION_REPORT.md`, `CLAUDE.md`
- Modify: `manifest.json` (rebuild)

- [ ] **Step 1: README eval section** — "Evaluate the installed skills" after the discovery
  section: evals/ suite, runbook, record_eval.py example; mirror in 中文.
- [ ] **Step 2: README docs links** — GitHub Pages + ReadTheDocs links (site URLs with a
  placeholder note if not yet live) in the header area of both languages.
- [ ] **Step 3: IMPLEMENTATION_REPORT staleness note** — one line at top: historical snapshot of
  the Iteration 17 delivery; see CHANGELOG.md for the current release state.
- [ ] **Step 4: CLAUDE.md** — add the docs build command (`mkdocs build --strict`) and the
  contract-test pointer to the quality gates list.
- [ ] **Step 5: Rebuild manifest and verify `--check`**

### Task 5: Release acceptance

**Files:**
- Add: `docs/iterations/iteration-30-bilingual-docs-site/acceptance.md`
- Modify: `CHANGELOG.md` (Unreleased entry)

- [ ] **Step 1: Run all gates** — pytest (with and without BT_BACKTRADER_DIR), `mkdocs build
  --strict`, mypy, ruff, black, manifest/catalog checks.
- [ ] **Step 2: Enable GitHub Pages** — attempt `gh api -X POST repos/cloudQuant/backtrader-skills/pages -f build_type=workflow`; if the API is unavailable, record the manual settings steps instead.
- [ ] **Step 3: Record RTD import instructions** — exact steps for importing
  cloudQuant/backtrader-skills on readthedocs.org (cannot be done without the user's RTD account).
- [ ] **Step 4: Write acceptance.md and the CHANGELOG Unreleased entry; record evidence**

## Self-Review

- Task 1 pins the wiring before content exists, so the site cannot silently lose a language or a
  page; Tasks 2/3 adapt existing repo text rather than inventing claims; Task 4 closes the README
  gaps; Task 5 records what automation cannot do (RTD import) instead of claiming it.
