# Published Acceptance Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Synchronize the packaged 7 x 2 acceptance JSON with current clean-wheel dependency-origin behavior and prevent structural evidence drift.

**Architecture:** Define a stable JSON-shape regression test, refresh the artifact through the existing public acceptance forwarder, clarify historic versus current evidence in the implementation report, then rebuild the distribution manifest.

**Tech Stack:** Python 3.10+, pytest, existing acceptance forwarder, JSON, distribution manifest.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- Generate evidence only through the public source-checkout forwarder.
- Assert stable structural facts, never random run IDs, wheel SHA, or temporary directories.
- Rebuild manifest after evidence/report changes.

---

### Task 1: Establish the failing published-evidence contract

**Files:**
- Create: `tests/test_published_acceptance_evidence.py`

- [x] **Step 1: Assert expected clean-wheel and filelock evidence fields**

Require schema version, passed status, 14 cells, clean-install mode/source proof, and nonempty
filelock version/module path plus true origin verification.

- [x] **Step 2: Run focused test before refresh**

Expected: FAIL because the shipped evidence does not contain `runtime_dependencies.filelock`.

### Task 2: Refresh artifact and report semantics

**Files:**
- Modify: `evidence/acceptance-7x2.json`
- Modify: `IMPLEMENTATION_REPORT.md`
- Modify: `tests/test_published_acceptance_evidence.py`

- [x] **Step 1: Generate evidence through scripts/run_acceptance.py**

Use full matrix, both sibling absence requirements, and `--output evidence/acceptance-7x2.json`.

- [x] **Step 2: Clarify historic report counts**

Retain Iteration 17 provenance while explaining that the packaged JSON contains the current exact
release acceptance data.

- [x] **Step 3: Run focused test**

Expected: pass.

### Task 3: Rebuild distribution and accept

**Files:**
- Modify: `manifest.json`
- Modify: `docs/iterations/iteration-24-published-acceptance-evidence/acceptance.md`

- [x] **Step 1: Rebuild manifest and run all documented gates**

Run full pytest, mypy, Ruff, Black, manifest/catalog, doctor, clean-wheel, and diff checks.

- [x] **Step 2: Record exact evidence and mark plan complete**

Record test count, evidence runtime dependency data, manifest hash, doctor checks, and clean-wheel result.

## Self-Review

- Task 1 prevents the observed evidence gap; Task 2 updates FR-1 through FR-3; Task 3 covers FR-4.
- The plan does not turn nondeterministic release values into brittle test constants.
