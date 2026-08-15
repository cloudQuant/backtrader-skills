# Skill Grounding & Agent Quality Implementation Plan (Iteration 29)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Close the four gap groups from the 2026-08-15 best-practice review: (A) ground the three
canonical skills with complete references, worked examples, failure playbooks, and pipeline
handoffs; (B) make CI run the real execution path with a coverage gate; (C) add a skill-level
golden-prompt eval system; (D) add repo hygiene (CLAUDE.md/AGENTS.md, CHANGELOG, P1 roadmap).

**Architecture:** Phase A locks skill documentation to runtime facts with drift-lock tests, so
later phases reference stable ground truth. Phase B extends the existing CI-contract test pattern
(`tests/test_ci_python_matrix.py`) to a full-acceptance job plus coverage gate. Phase C adds
golden-prompt evals with a mechanical artifact scorer plus a manual host runbook. Phase D makes the
repo self-documenting and versions the release as 0.2.0.

**Tech Stack:** Python 3.10+, pytest + pytest-cov, `backtrader_skills.ir`/`validation` as ground
truth, GitHub Actions, cloudQuant/backtrader fork checkout.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- Preserve progressive disclosure: SKILL.md files stay ≤ 60 lines; each reference stays ≤ 300 lines.
- TDD: drift-lock and CI-contract tests are written first and must FAIL before content changes.
- CI uses only public repositories; no secrets.
- Keep the existing auto-skip behavior for dev machines without the backtrader source package.
- Full acceptance runs on master push only; PRs keep the quality and test-matrix jobs.
- Docs are English (repo convention); update the bilingual README only for user-facing changes.

---

### Task 1: Drift-lock tests for skill references (RED)

**Files:**
- Add: `tests/test_skill_reference_contract.py`

- [x] **Step 1: Assert the author contract enumerates the runtime vocabulary**

Import `ARCHETYPES`, `OUTPUT_PROFILES`, `EXPRESSION_KINDS`, `OPERATORS` from
`backtrader_skills.ir` and require every value to appear in
`skills/backtrader-strategy-author/references/authoring-contract.md`.

- [x] **Step 2: Assert the review catalog covers every diagnostic code**

Scan `src/backtrader_skills/validation.py` for string literals matching `^(SEC_|BT_|PY_)` and
require each code to have a row in `skills/backtrader-strategy-review/references/review-rules.md`.

- [x] **Step 3: Assert skill structure invariants**

Require every relative link in each SKILL.md to resolve, each SKILL.md to stay ≤ 60 lines, and each
skill to link a worked-example and a failure-playbook reference.

- [x] **Step 4: Run the new tests against the current tree**

Expected: FAIL — the references enumerate none of the runtime vocabulary today
(`authoring-contract.md` is 15 lines and names the IR without defining it).

### Task 2: Ground the three skills until GREEN

**Files:**
- Modify: `skills/backtrader-strategy-author/references/authoring-contract.md`
- Modify: `skills/backtrader-strategy-review/references/review-rules.md`
- Add: one `references/worked-example.md` and one `references/failure-playbook.md` per skill
- Modify: all three `SKILL.md` files

- [x] **Step 1: Authoring contract**

Add the seven-row archetype table (purpose, feed shape, typical entry/exit), the Expression grammar
(five kinds: constant/parameter/data_line/indicator/state/operator), the operator table
(derived from `backtrader_skills.ir.OPERATORS`) with arity and meaning, the StateRule/Action form,
and the canonical StrategySpec field enumeration.

- [x] **Step 2: Review catalog**

Add the full diagnostic catalog table: every `SEC_*`, `BT_*`, and `PY_SYNTAX_ERROR` code with
severity, trigger, and remediation, sourced from `validation.py`.

- [x] **Step 3: Worked examples**

One golden path per skill, ≤ 150 lines each: author renders a two-feed `multi_timeframe` spec from
scaffold to apply; review shows an injected-fault candidate and the expected ValidationReport
excerpt; test shows prepare → approve → execute and the expected report fields.

- [x] **Step 4: Failure playbooks**

Per skill: token `EXPIRED`/`REVOKED`/`CONSUMED`, validation failure, runonce/runnext parity
mismatch, `SOURCE_CHECKOUT_NOT_FOUND`, and `BACKTRADER_SOURCE_MISMATCH` → exact next actions.

- [x] **Step 5: Pipeline handoffs and triggers**

Each SKILL.md gains a handoff section (author → review → test order, repair loops back to
author/render with fresh approvals); descriptions gain backtest/backtesting trigger keywords.

- [x] **Step 6: Run the drift-lock tests**

Expected: GREEN, and link/structure invariants hold.

### Task 3: CI full acceptance + coverage gate

**Files:**
- Modify: `tests/test_ci_python_matrix.py`
- Modify: `pyproject.toml`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md` (Verification section)

- [x] **Step 1: Extend the CI-contract test (RED)**

Assert a new `.github/workflows/acceptance.yml` exists with `on: push: branches: [master]` and no
PR trigger, checks out `cloudQuant/backtrader`, runs pytest with `--cov=src/backtrader_skills
--cov-fail-under=80`, then runs `scripts/run_acceptance.py --repository <fork-checkout> --matrix all
--require-no-mcp --require-no-agent`; assert pyproject declares `pytest-cov` in the test extra and
`[tool.coverage.report] fail_under = 80`.

- [x] **Step 2: Measure current coverage with the source package present**

Run `pytest --cov=src/backtrader_skills --cov-report=term-missing` locally. If below 80, add
targeted execution-path tests until the gate is reachable.

- [x] **Step 3: Add the config and the master-only workflow**

Add coverage config to pyproject; add `.github/workflows/acceptance.yml` (ubuntu, Python 3.11,
sibling checkout of the fork, `BT_BACKTRADER_DIR` for execution tests, `--repository` for the
matrix), triggered only by push to master.

- [x] **Step 4: Run the extended CI-contract tests and local gates**

Expected: GREEN; coverage ≥ 80 locally; acceptance matrix passes.

- [x] **Step 5: Document CI evidence in the README Verification section**

State what CI now proves (execution path + 7×2 matrix + coverage on master) and what remains
local-only.

### Task 4: Skill-level eval system

**Files:**
- Add: `evals/prompts/*.md` (7 archetype prompts + 3 adversarial/cross-skill prompts)
- Add: `evals/README.md` (runbook + score sheet)
- Add: `scripts/record_eval.py` (mechanical scorer)
- Modify: `tests/test_skill_reference_contract.py`

- [x] **Step 1: Golden prompts**

One prompt per archetype: precondition (registered dataset), exact prompt text, pass criteria
(artifact exists under the canonical path, passes review, dual-mode parity), and rubric.

- [x] **Step 2: Adversarial and cross-skill prompts**

Look-ahead injection, AST-gate bypass attempt (expect structured rejection), and a
failure → repair → re-render → re-run loop.

- [x] **Step 3: Mechanical scorer**

`record_eval.py` snapshots target state, runs `review` and `run` checks against produced artifacts,
and emits a JSON score sheet; human judgment fills the remaining rubric rows.

- [x] **Step 4: Eval runbook**

Host-session instructions (Claude Code/Codex), transcript retention, and the score sheet template.

- [x] **Step 5: Prompt validity drift test**

Extend the drift-lock test to assert every eval prompt references only valid archetypes, output
profiles, and dataset-role terms.

### Task 5: Repo hygiene

**Files:**
- Add: `CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md`, `docs/roadmap.md`
- Modify: `pyproject.toml` (version 0.2.0), `README.md`

- [x] **Step 1: CLAUDE.md (canonical) + AGENTS.md (pointer)**

Environment selection, test/gate commands, the manifest rebuild rule (`python
scripts/build_manifest.py` after touching distributed files), iteration workflow, and security
notes. AGENTS.md is a short pointer for Codex/OpenCode hosts.

- [x] **Step 2: CHANGELOG.md (Keep a Changelog)**

Unreleased section plus a 0.2.0 entry covering iterations 18–27 highlights and this iteration;
adopt a semver statement in README.

- [x] **Step 3: docs/roadmap.md P1 backlog**

Container/network-namespace sandbox, HTML reports, per-target CLI serialization, OpenClaw live
discovery, Windows CI, embedding catalog search — each with status and a rough plan.

- [x] **Step 4: Version bump and README cross-links**

Bump 0.1.0 → 0.2.0; link CLAUDE.md and CHANGELOG from README.

### Task 6: Release acceptance

**Files:**
- Modify: `evidence/acceptance-7x2.json`, `manifest.json`
- Add: `docs/iterations/iteration-29-skill-grounding-and-agent-quality/acceptance.md`
- Modify: `CHANGELOG.md`

- [x] **Step 1: Regenerate evidence and manifest**

Use the public acceptance forwarder and manifest builder.

- [x] **Step 2: Run all documented gates**

pytest (with the fork present, coverage ≥ 80), mypy, Ruff, Black, manifest/catalog checks,
clean-wheel install, and the full 7×2 matrix.

- [x] **Step 3: Record exact evidence and mark the plan complete**

Record test counts, coverage number, manifest hash, doctor checks, clean-wheel result, and diff
status; date the CHANGELOG entry.

## Self-Review

- Task 1 turns documentation drift into a test failure, so Task 2's content is provably complete;
  Task 3 closes the execution-path CI hole with a coverage floor; Task 4 makes agent quality
  measurable; Task 5 makes the repo self-documenting for the next iteration. Phases are ordered
  this way so later tasks never restate ground truth that the drift-lock tests have not yet pinned.
