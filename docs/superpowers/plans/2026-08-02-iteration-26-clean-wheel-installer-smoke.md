# Clean-Wheel Installer Smoke Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Prove a clean-installed wheel can locate and install its canonical skills without source-checkout or global site-package leakage.

**Architecture:** Add an `-I -S` installer sub-process probe to the existing clean-wheel acceptance flow. It performs preview, explicit approval, and apply for the Codex host, then returns a small portable JSON result that is stored under distribution evidence.

**Tech Stack:** Python 3.10+, pathlib, subprocess, current TokenStore and SkillInstaller, pytest.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- The probe may add only the clean install root to `sys.path`.
- Do not serialize temporary absolute paths in evidence.
- Preserve the existing general same-target CLI concurrency boundary.

---

### Task 1: Make the missing runtime boundary observable

**Files:**
- Modify: `tests/test_clean_wheel_dependencies.py`
- Modify: `tests/test_published_acceptance_evidence.py`

- [x] **Step 1: Add installer smoke assertions**

Require the clean-wheel helper and published evidence to report a successful Codex installation of exactly
the three canonical skills and a positive installed file count.

- [x] **Step 2: Run focused tests against current implementation**

Expected: FAIL because no installer smoke field exists.

### Task 2: Run the packaged installer in isolation

**Files:**
- Modify: `src/backtrader_skills/acceptance.py`
- Modify: focused tests

- [x] **Step 1: Implement bounded child protocol**

Run the installed `SkillInstaller` under `-I -S`, execute preview/approve/apply for Codex, and validate its
portable JSON response in the parent.

- [x] **Step 2: Attach result to distribution evidence**

Store the verified result as `distribution.installer_smoke`; no absolute path may cross the boundary.

- [x] **Step 3: Run focused tests**

Expected: the helper executes the true clean-installed resource lookup and both tests pass.

### Task 3: Refresh artifact and fully accept

**Files:**
- Modify: `evidence/acceptance-7x2.json`
- Modify: `manifest.json`
- Modify: `docs/iterations/iteration-26-clean-wheel-installer-smoke/acceptance.md`

- [x] **Step 1: Regenerate evidence and manifest**

Use the public acceptance forwarder and manifest builder.

- [x] **Step 2: Run full documented gates**

Run pytest, mypy, Ruff, Black, manifest/catalog, doctor, clean-wheel, and diff checks.

- [x] **Step 3: Record exact evidence and mark plan complete**

Record smoke output, test count, manifest hash, doctor checks, clean-wheel result, and diff status.

## Self-Review

- Task 1 proves the prior coverage gap; Task 2 tests the installed distribution rather than archive names;
  Task 3 ensures published evidence and release integrity remain current.
