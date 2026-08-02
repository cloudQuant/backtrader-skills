# Manifest Tool Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Make the public distribution-manifest script safe to inspect and capable of non-mutating verification.

**Architecture:** Retain the existing distribution module as the single implementation of build and verify semantics; give the source-checkout script a small argparse adapter; verify behavior by subprocess and byte-for-byte manifest checks; invoke the adapter in CI and documentation.

**Tech Stack:** Python 3.10+, argparse, subprocess pytest, existing distribution manifest API.

## Global Constraints

- Python commands use /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python.
- Default no-argument behavior rebuilds manifest.json exactly as before.
- --help and --check must not change manifest bytes.
- No new dependency, manifest schema, or hash algorithm.
- Rebuild manifest.json through the default script after distribution-file changes.

---

### Task 1: Write red tests for command safety

**Files:**
- Create: tests/test_manifest_tool.py

**Interfaces:**
- Consumes: scripts/build_manifest.py and manifest.json
- Produces: subprocess assertions for help, check, default rebuild, and byte preservation

- [x] **Step 1: Add failing help and check tests**

~~~python
def test_manifest_help_and_check_are_read_only() -> None:
    before = (PRODUCT_ROOT / "manifest.json").read_bytes()
    for arguments, marker in [(["--help"], "usage:"), (["--check"], "verified manifest:")]:
        completed = run_manifest(*arguments)
        assert completed.returncode == 0
        assert marker in completed.stdout
        assert (PRODUCT_ROOT / "manifest.json").read_bytes() == before
~~~

- [x] **Step 2: Run the focused test**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_manifest_tool.py -q -p no:cacheprovider

Expected: FAIL because --help currently rebuilds the manifest and --check is ignored.

### Task 2: Implement a safe script adapter and CI gate

**Files:**
- Modify: scripts/build_manifest.py
- Modify: .github/workflows/ci.yml
- Modify: tests/test_manifest_tool.py

**Interfaces:**
- Produces: main(argv: list[str] | None = None) -> int
- Produces: --check read-only verification with exit 0 or 2
- Consumes: build_distribution_manifest and verify_distribution_manifest

- [x] **Step 1: Add argparse and error handling**

Implement default rebuild and --check paths, catch IntegrityError and OSError, and retain nonzero failures.

- [x] **Step 2: Add default rebuild regression**

~~~python
def test_manifest_default_rebuilds_and_verifies() -> None:
    completed = run_manifest()
    assert completed.returncode == 0
    assert "rebuilt manifest:" in completed.stdout
    assert verify_distribution_manifest(PRODUCT_ROOT)["verified"]
~~~

- [x] **Step 3: Route the CI gate through the script**

Replace the inline distribution check with:

~~~yaml
- name: Distribution manifest check
  run: python scripts/build_manifest.py --check
~~~

- [x] **Step 4: Run focused tests**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_manifest_tool.py -v -p no:cacheprovider

Expected: all tests pass.

### Task 3: Document and fully accept

**Files:**
- Modify: README.md
- Modify: manifest.json
- Modify: docs/iterations/iteration-20-manifest-tool-safety/acceptance.md

**Interfaces:**
- Produces: unambiguous build versus check commands and exact evidence

- [x] **Step 1: Update English and Chinese README verification instructions**

Show default build only after changing a distribution file, and show --check for routine read-only validation.

- [x] **Step 2: Rebuild manifest**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py

Expected: generated manifest includes the changed script and README hash.

- [x] **Step 3: Run all gates**

Run:

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests -v -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m black --check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_catalog.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/doctor.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
git diff --check
~~~

Expected: all commands exit 0; acceptance has 14 passed cells and built-wheel-clean-install.

- [x] **Step 4: Record exact evidence**

Record the test count, manifest hash and file count, doctor checks, clean-wheel summary, and diff result.

## Self-Review

- Spec coverage: Task 1 proves FR-1 and FR-3 before code; Task 2 implements FR-1 through FR-4; Task 3 covers FR-5 and all success criteria.
- Placeholder scan: every coding and verification action is executable.
- Type consistency: script main returns int and delegates manifest values unchanged from the distribution module.
