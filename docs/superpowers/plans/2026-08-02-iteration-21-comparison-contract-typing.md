# Comparison Contract Typing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Align declared comparison `TypedDict` contracts with their implementations and make static checking a CI gate.

**Architecture:** Construct complete `MetricComparison` and `EventComparison` objects explicitly, calculate the existing canonical hash from a copy without its hash field, and protect behavior with runtime contract tests plus mypy in CI.

**Tech Stack:** Python 3.10+, `typing.TypedDict`, mypy, pytest, GitHub Actions.

## Global Constraints

- Python commands use `/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python`.
- Preserve comparison JSON field names, profile rules, and canonical hash semantics.
- Do not use a broad `cast` to silence the observed return-value errors.
- Rebuild `manifest.json` after modifying distribution source.

---

### Task 1: Add regression coverage

**Files:**
- Create: `tests/test_comparison_type_contract.py`

- [x] **Step 1: Assert complete metrics/events contracts and hash recomputation**

Use a fixture metrics pair and a normalized event pair. Assert exact public keys and that
`canonical_hash` of a copy excluding `comparison_hash` equals the returned hash.

- [x] **Step 2: Run focused test and current mypy check**

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_comparison_type_contract.py -q -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m mypy src/backtrader_skills
~~~

Expected: runtime contract test passes against current behavior; mypy fails with the two existing
`compare.py` return-value errors.

### Task 2: Make result construction type-correct

**Files:**
- Modify: `src/backtrader_skills/compare.py`
- Modify: `tests/test_comparison_type_contract.py`

- [x] **Step 1: Explicitly type differences and result mappings**

Construct full results, initially including an empty `comparison_hash`; calculate hash from a copied
mapping after removing that key, then write it back.

- [x] **Step 2: Run focused static and runtime checks**

Run the two Task 1 commands. Expected: both exit 0.

### Task 3: Enforce CI and accept the release artifact

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `manifest.json`
- Modify: `docs/iterations/iteration-21-comparison-contract-typing/acceptance.md`

- [x] **Step 1: Add explicit Mypy workflow step**

Run `python -m mypy src/backtrader_skills` after the existing formatting checks.

- [x] **Step 2: Rebuild manifest and run full gates**

Run the documented pytest, mypy, Ruff, Black, manifest/catalog, doctor, clean-wheel, and diff gates.

- [x] **Step 3: Record exact evidence and mark checkboxes complete**

Record test count, manifest hash/file count, doctor check count, clean-wheel matrix summary, and
the no-output diff check.

## Self-Review

- Task 1 covers runtime regression behavior; Task 2 covers FR-1 and FR-2; Task 3 covers FR-4 and
  FR-5.
- The plan preserves all runtime JSON behavior while making static contract drift observable.
