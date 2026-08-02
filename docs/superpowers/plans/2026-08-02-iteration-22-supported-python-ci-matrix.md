# Supported Python CI Matrix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Convert the published Python 3.10–3.13 support statement into an executable GitHub Actions test matrix while keeping quality work non-duplicated.

**Architecture:** Separate a fixed Python 3.11 `quality` job that installs `.[dev]` from a four-version `test-supported-python` job that installs `.[test]`; protect the workflow shape through a local text-based pytest contract.

**Tech Stack:** GitHub Actions, Python 3.10–3.13, pytest, standard-library text assertions.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- Preserve the published 3.10–3.13 range and do not change package runtime dependencies.
- Hosted CI must not require the separate Backtrader source checkout.
- Do not claim an untriggered remote workflow has passed.

---

### Task 1: Establish workflow-shape regression coverage

**Files:**
- Create: `tests/test_ci_python_matrix.py`

- [x] **Step 1: Assert expected quality and matrix job contracts**

Check exact four supported versions, dynamic matrix setup-python, `.[test]` in the test job, fixed
3.11 plus `.[dev]` and Mypy in quality, and a single pytest command in the matrix job.

- [x] **Step 2: Run the focused test**

Run the test before changing CI. Expected: FAIL because current workflow is one fixed-3.11 job.

### Task 2: Split CI responsibilities

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `tests/test_ci_python_matrix.py`

- [x] **Step 1: Create quality and test-supported-python jobs**

Keep lint/static/catalog/manifest gates under fixed 3.11. Configure the four-version test matrix
with `fail-fast: false`, dynamic setup-python, test extra installation, and pytest.

- [x] **Step 2: Run focused test and inspect workflow**

Expected: focused test passes; static inspection confirms only the matrix job runs pytest.

### Task 3: Full local acceptance and evidence

**Files:**
- Modify: `docs/iterations/iteration-22-supported-python-ci-matrix/acceptance.md`

- [x] **Step 1: Run full local gates**

Run documented pytest, mypy, Ruff, Black, manifest/catalog, doctor, clean-wheel, and diff gates.

- [x] **Step 2: Record local evidence and hosted boundary**

Record actual local results and state that GitHub-hosted version executions occur after PR/push.

- [x] **Step 3: Mark plan complete**

Mark checkboxes only after all local gates pass.

## Self-Review

- Task 1 prevents matrix shrinkage; Task 2 implements FR-1 and FR-2; Task 3 covers FR-4 and FR-5.
- The workflow keeps source-coupled integration proof in the existing local release acceptance path.
