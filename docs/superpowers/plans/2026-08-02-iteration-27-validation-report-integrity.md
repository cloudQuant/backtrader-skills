# Validation Report Integrity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Make `render apply` verify the persisted ValidationReport hash and its draft binding before a token claim or target write.

**Architecture:** Add a focused report loader in `DraftManager` that verifies the schema marker, x-hash-contract, manifest identity, and passed state. Reuse the verified report to derive existing token bindings; leave the token store and transaction code unchanged.

**Tech Stack:** Python 3.10+, canonical JSON hashing, current DraftManager/TokenStore, pytest.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- Validate report integrity before `TokenStore.claim()`.
- Do not consume a token or mutate target files when validation evidence is invalid.
- Keep general same-target CLI concurrency outside this iteration's scope.

---

### Task 1: Expose persisted-report tampering

**Files:**
- Modify: `tests/test_drafts_installer.py`

- [x] **Step 1: Add a tampered report regression test**

Create and validate a real draft, alter the persisted report status without recomputing `validation_hash`, approve
the original token, and require apply to fail before token consumption or target writes.

- [x] **Step 2: Run the focused test against current implementation**

Expected: FAIL because apply trusts `summary.passed` and does not validate the stored report hash.

### Task 2: Verify report integrity before the claim

**Files:**
- Modify: `src/backtrader_skills/drafts.py`
- Modify: focused tests

- [x] **Step 1: Add validated report loading**

Check canonical `validation_hash`, schema marker, four report-to-manifest identity fields, then valid passed state.

- [x] **Step 2: Derive bindings only from verified report**

Call the loader before entering `TokenStore.claim()`; keep the remaining apply transaction unchanged.

- [x] **Step 3: Run focused tests**

Expected: tampering is rejected with `IntegrityError`, while normal apply remains green.

### Task 3: Fully accept the release state

**Files:**
- Modify: `evidence/acceptance-7x2.json`
- Modify: `manifest.json`
- Modify: `docs/iterations/iteration-27-validation-report-integrity/acceptance.md`

- [x] **Step 1: Regenerate evidence and manifest**

Use the public acceptance forwarder and manifest builder.

- [x] **Step 2: Run all documented gates**

Run pytest, mypy, Ruff, Black, manifest/catalog, doctor, clean-wheel, and diff checks.

- [x] **Step 3: Record exact evidence and mark plan complete**

Record the rejection behavior, test count, manifest hash, doctor checks, clean-wheel result, and diff status.

## Self-Review

- Task 1 proves the actual trust gap; Task 2 fixes it at the authorization boundary; Task 3 preserves
  published evidence and release integrity.
