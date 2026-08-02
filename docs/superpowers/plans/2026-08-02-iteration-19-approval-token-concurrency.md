# Approval Token Concurrency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Ensure a single approval token cannot authorize two successful concurrent operations.

**Architecture:** Adopt FileLock as a declared runtime dependency, make TokenStore state transitions operate through private locked helpers, add a claim context for write workflows, and keep the runner's consume-before-execute policy atomic.

**Tech Stack:** Python 3.10+, filelock, pytest multiprocessing, existing JSON token records and CLI error protocol.

## Global Constraints

- Python commands use /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python.
- Lock files use token digests only and never persist token plaintext.
- Explicit approval, binding hash, TTL, workspace binding, and terminal states keep their existing contracts.
- Render and install claims consume only after successful side effects; run consumes before child execution.
- Target-wide CLI concurrency remains unsupported and README must say so.
- Rebuild manifest.json through scripts/build_manifest.py after distribution-file changes.

---

### Task 1: Specify the race with deterministic failing tests

**Files:**
- Create: tests/test_token_concurrency.py

**Interfaces:**
- Consumes: TokenStore, RuntimePaths, approval bindings, multiprocessing processes
- Produces: a process-safe assertion that only one same-token claim can finish

- [x] **Step 1: Write failing claim-race and rollback tests**

~~~python
def test_claim_serializes_same_token_across_processes(tmp_path: Path) -> None:
    token, bindings = issue_approved_token(tmp_path)
    results = run_two_workers(tmp_path, token, bindings)
    assert sorted(result[0] for result in results) == ["consumed", "error"]

def test_claim_exception_leaves_token_available(tmp_path: Path) -> None:
    store, token, bindings = issue_approved_token(tmp_path)
    with pytest.raises(RuntimeError):
        with store.claim(token, "render_write", bindings):
            raise RuntimeError("simulated write failure")
    assert store.get(token)["state"] == "ISSUED"
~~~

- [x] **Step 2: Run focused tests to verify they fail**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_token_concurrency.py -q -p no:cacheprovider

Expected: FAIL because TokenStore has no claim context and its consume path is not serialized.

### Task 2: Implement locked token state transitions

**Files:**
- Modify: pyproject.toml
- Modify: src/backtrader_skills/errors.py
- Modify: src/backtrader_skills/state.py
- Modify: tests/test_token_concurrency.py

**Interfaces:**
- Produces: ApprovalLockTimeout with code APPROVAL_LOCK_TIMEOUT
- Produces: TokenStore.claim(token_id, kind, bindings) context manager
- Produces: atomic TokenStore.consume

- [x] **Step 1: Declare filelock and assert wheel metadata**

Add filelock>=3.16,<4 to project runtime dependencies. Extend the wheel distribution test to assert:

~~~python
metadata = archive.read(next(name for name in names if name.endswith("METADATA"))).decode()
assert "Requires-Dist: filelock" in metadata
~~~

- [x] **Step 2: Replace public-method chaining with private locked helpers**

Implement one lock path per token digest, _get_unlocked, _verify_unlocked, and _consume_unlocked.
Every public read-modify-write path holds FileLock and maps Timeout to ApprovalLockTimeout.

- [x] **Step 3: Implement claim normal-exit consumption**

~~~python
@contextmanager
def claim(self, token_id, kind, bindings):
    with self._locked(token_id):
        record = self._verify_unlocked(token_id, kind, bindings)
        yield self._public(token_id, record)
        self._consume_unlocked(token_id, record)
~~~

- [x] **Step 4: Run focused concurrency and state tests**

Run:

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_token_concurrency.py tests/test_canonical_data_state.py -v -p no:cacheprovider
~~~

Expected: all tests pass.

### Task 3: Put approval-protected side effects inside claims

**Files:**
- Modify: src/backtrader_skills/drafts.py
- Modify: src/backtrader_skills/installer.py
- Modify: src/backtrader_skills/runner.py
- Modify: tests/test_drafts_installer.py
- Modify: tests/test_runner.py

**Interfaces:**
- Consumes: TokenStore.claim for render/install/uninstall
- Consumes: atomic TokenStore.consume for run execution
- Produces: no verify-to-side-effect-to-consume window

- [x] **Step 1: Change render apply to a single claim scope**

Keep preflight, staging, commit, rollback, report writing, and manifest return in the claim scope.
Remove the trailing standalone consume call.

- [x] **Step 2: Change install and uninstall applies to claim scopes**

Keep host path verification, file copy or unlink, manifest update, and response construction inside their
respective claims. Preserve modified-file protection during uninstall.

- [x] **Step 3: Remove the redundant runner verify call**

Use only atomic consume immediately before the child modes begin, preserving failure-consumes-execution
semantics.

- [x] **Step 4: Run workflow regressions**

Run:

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_drafts_installer.py tests/test_runner.py -v -p no:cacheprovider
~~~

Expected: all tests pass.

### Task 4: Document, synchronize, and accept

**Files:**
- Modify: README.md
- Modify: manifest.json
- Modify: docs/iterations/iteration-19-approval-token-concurrency/acceptance.md

**Interfaces:**
- Produces: accurate non-global concurrency documentation and recorded evidence

- [x] **Step 1: Update English and Chinese concurrency limitations**

State that same-token approval-protected operations are serialized, while general concurrent CLI use for
one target remains unsupported.

- [x] **Step 2: Rebuild the manifest**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py

Expected: manifest.json includes changed source, scripts, README, and pyproject files.

- [x] **Step 3: Run complete verification**

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

Expected: all commands exit 0; the acceptance matrix reports 14 passed cells and built-wheel-clean-install.

- [x] **Step 4: Record current-run evidence**

Record exact test count, manifest hash and file count, doctor checks, clean-wheel summary, and diff result in
the iteration acceptance document.

## Self-Review

- Spec coverage: Task 1 proves FR-3 and FR-4 red-first; Task 2 implements FR-1 through FR-4; Task 3 applies FR-4 to real side effects; Task 4 covers FR-5, FR-6, and all success criteria.
- Placeholder scan: every coding and verification step is explicit and executable.
- Type consistency: public claim and consume receive token_id, kind, and bindings; all caller scopes use the same values already embedded in their approval tokens.
