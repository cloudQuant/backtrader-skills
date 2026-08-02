# Clean Wheel Dependency Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Make clean-wheel acceptance prove that runtime dependency resolution and loading occur from the temporary install target.

**Architecture:** Refactor the acceptance wheel-install and dependency-probe paths into shared internal helpers; force resolver installation into `install_root`, then prove `backtrader_skills.state` and `filelock` import under `-I -S` from that root before the existing 7 x 2 acceptance runs.

**Tech Stack:** Python 3.10+, pip, subprocess, pytest, wheel build API.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- Do not vendor filelock or change the package dependency range.
- Do not permit a globally installed filelock to satisfy the clean dependency probe.
- Keep current wheel sibling exclusion and 7 x 2 acceptance behavior.

---

### Task 1: Add a failing dependency-isolation regression

**Files:**
- Create: `tests/test_clean_wheel_dependencies.py`

- [x] **Step 1: Define target-only import contract**

Build the wheel into `tmp_path`, use the acceptance helper path, then assert a `-I -S` probe imports state
and reports filelock from the temporary target.

- [x] **Step 2: Run focused test against current implementation**

Expected: FAIL because the current clean installer passes `--no-deps`, leaving filelock absent from the
target when global site-packages are disabled.

### Task 2: Resolve and prove runtime dependencies

**Files:**
- Modify: `src/backtrader_skills/acceptance.py`
- Modify: `tests/test_clean_wheel_dependencies.py`

- [x] **Step 1: Extract resolver install helper**

Use pip `--disable-pip-version-check --ignore-installed --target <root> <wheel>` and provide useful
ExecutionError stderr details.

- [x] **Step 2: Extract isolated dependency probe**

Run Python with `-I -S`, insert target, import state/filelock, verify the resolved module path is inside
target, and return version/path proof.

- [x] **Step 3: Attach evidence to clean acceptance distribution output**

Preserve existing fields and add `runtime_dependencies.filelock` evidence.

- [x] **Step 4: Run focused test**

Expected: pass with target-only filelock origin evidence.

### Task 3: Full acceptance and evidence

**Files:**
- Modify: `manifest.json`
- Modify: `docs/iterations/iteration-23-clean-wheel-dependency-isolation/acceptance.md`

- [x] **Step 1: Rebuild manifest and run all documented gates**

Run focused and full pytest, mypy, Ruff, Black, manifest/catalog, doctor, clean-wheel, and diff checks.

- [x] **Step 2: Record exact evidence and mark plan complete**

Record test count, manifest hash, resolver/probe result, doctor checks, clean-wheel summary, and diff result.

## Self-Review

- Task 1 proves the old `--no-deps` blind spot; Task 2 implements FR-1 through FR-3; Task 3 covers
  FR-4 and FR-5.
- A `-I -S` probe makes global site-package leakage observable rather than inferred.
