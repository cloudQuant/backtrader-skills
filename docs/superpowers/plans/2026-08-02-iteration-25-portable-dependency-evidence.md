# Portable Dependency Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Replace ephemeral absolute module paths in clean-wheel evidence with portable install-root-relative paths without weakening origin validation.

**Architecture:** Validate the resolved module path against the live install root inside the isolated probe, serialize only its POSIX-relative representation, update both live-target and packaged-evidence tests, then regenerate the evidence artifact.

**Tech Stack:** Python 3.10+, pathlib, subprocess, pytest, current acceptance forwarder.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- Validate absolute paths before converting them to relative paths.
- Never serialize a temporary absolute path in the packaged evidence.
- Refresh evidence through scripts/run_acceptance.py and rebuild manifest.

---

### Task 1: Extend failing path-shape tests

**Files:**
- Modify: `tests/test_clean_wheel_dependencies.py`
- Modify: `tests/test_published_acceptance_evidence.py`

- [x] **Step 1: Require safe relative module paths**

Require a non-absolute module path without `..`; in the live test, resolve it under install_root and
assert it names an existing file inside that root.

- [x] **Step 2: Run focused tests against current implementation**

Expected: FAIL because the current evidence serializes a deleted temporary absolute path.

### Task 2: Normalize after source verification

**Files:**
- Modify: `src/backtrader_skills/acceptance.py`
- Modify: focused tests

- [x] **Step 1: Keep resolved origin validation**

Check `module_path.is_relative_to(install_root)` before calculating `relative_to(...).as_posix()`.

- [x] **Step 2: Return portable path and run focused tests**

Expected: tests pass and the live relative path locates filelock under the target.

### Task 3: Refresh artifact and fully accept

**Files:**
- Modify: `evidence/acceptance-7x2.json`
- Modify: `manifest.json`
- Modify: `docs/iterations/iteration-25-portable-dependency-evidence/acceptance.md`

- [x] **Step 1: Regenerate evidence and manifest**

Use the documented public forwarder and manifest builder.

- [x] **Step 2: Run full documented gates**

Run pytest, mypy, Ruff, Black, manifest/catalog, doctor, clean-wheel, and diff checks.

- [x] **Step 3: Record exact evidence and mark plan complete**

Record the portable path, test count, manifest hash, doctor checks, clean-wheel result, and diff status.

## Self-Review

- Task 1 makes the ephemeral-path defect observable; Task 2 covers FR-1 through FR-3; Task 3 covers
  FR-4 and FR-5.
- The absolute source proof remains inside the probe and is not replaced by a string-only check.
