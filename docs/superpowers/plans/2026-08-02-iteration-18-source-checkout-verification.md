# Source Checkout Verification Forwarders Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Make the source-checkout doctor and acceptance forwarders locate a valid Backtrader repository deterministically in both supported local layouts.

**Architecture:** Put repository discovery in one small package module, make each script consume only its own path option and forward all remaining canonical CLI arguments, and preserve the established structured error shape. Exercise layout discovery without a real Backtrader dependency, then prove the real forwarders against the sibling checkout.

**Tech Stack:** Python 3.10+, argparse, pathlib, pytest, existing canonical CLI.

## Global Constraints

- Python commands use /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python.
- A valid repository root contains backtrader/version.py.
- Explicit input never silently falls back to autodiscovery.
- No new runtime dependency, network call, filesystem scan beyond the two documented candidates, or installed CLI interface change.
- Every source-checkout failure is a JSON object with a stable error code and exits 2.
- Any change below a distribution-included root requires scripts/build_manifest.py before distribution verification.

---

### Task 1: Define and test repository-root resolution

**Files:**
- Create: src/backtrader_skills/source_checkout.py
- Modify: src/backtrader_skills/errors.py
- Create: tests/test_source_checkout.py

**Interfaces:**
- Produces: resolve_backtrader_repository(product_root: Path, explicit: Path | None = None) -> Path
- Produces: SourceCheckoutNotFound, whose code is SOURCE_CHECKOUT_NOT_FOUND
- Consumes: a product root and only the documented nested/sibling candidates

- [x] **Step 1: Write failing layout and explicit-path tests**

~~~python
def test_resolve_backtrader_repository_supports_nested_and_sibling_layouts(tmp_path: Path) -> None:
    nested_root = make_repository(tmp_path / "nested")
    assert resolve_backtrader_repository(nested_root / "backtrader-skills") == nested_root

    sibling_parent = tmp_path / "sibling"
    sibling_root = make_repository(sibling_parent / "backtrader")
    assert resolve_backtrader_repository(sibling_parent / "backtrader-skills") == sibling_root

def test_resolve_backtrader_repository_honors_and_validates_explicit_path(tmp_path: Path) -> None:
    valid = make_repository(tmp_path / "valid")
    assert resolve_backtrader_repository(tmp_path / "product", valid) == valid
    with pytest.raises(SourceCheckoutNotFound):
        resolve_backtrader_repository(tmp_path / "product", tmp_path / "missing")
~~~

- [x] **Step 2: Run the focused test to verify it fails**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_source_checkout.py -q -p no:cacheprovider

Expected: FAIL because the module and resolver do not yet exist.

- [x] **Step 3: Implement the minimal resolver and stable error**

~~~python
def resolve_backtrader_repository(product_root: Path, explicit: Path | None = None) -> Path:
    candidates = [explicit] if explicit is not None else [
        product_root.parent,
        product_root.parent / "backtrader",
    ]
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "backtrader" / "version.py").is_file():
            return resolved
    raise SourceCheckoutNotFound("unable to locate a Backtrader repository root")
~~~

- [x] **Step 4: Run focused tests**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_source_checkout.py -q -p no:cacheprovider

Expected: PASS.

### Task 2: Wire both source-checkout forwarders

**Files:**
- Modify: scripts/doctor.py
- Modify: scripts/run_acceptance.py
- Modify: tests/test_source_checkout.py

**Interfaces:**
- Consumes: resolve_backtrader_repository and SourceCheckoutNotFound
- Produces: --target for doctor and --repository for acceptance
- Produces: JSON error with status, code, and message; exit code 2

- [x] **Step 1: Write the forwarder contract test**

~~~python
def test_source_doctor_forwarder_uses_explicit_target(tmp_path: Path) -> None:
    repository = make_repository(tmp_path / "backtrader")
    completed = subprocess.run(
        [sys.executable, "scripts/doctor.py", "--target", str(repository)],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    assert json.loads(completed.stdout)["passed"] is True
~~~

- [x] **Step 2: Run the forwarder test to verify it fails**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_source_checkout.py -q -p no:cacheprovider

Expected: FAIL because scripts/doctor.py currently passes its parent as the target and does not parse --target.

- [x] **Step 3: Implement parse-known forwarding and JSON failure handling**

~~~python
parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
parser.add_argument("--target", type=Path)
arguments, remaining = parser.parse_known_args()
try:
    target = resolve_backtrader_repository(PRODUCT_ROOT, arguments.target)
except SourceCheckoutNotFound as error:
    print(json.dumps({"status": "error", "code": error.code, "message": str(error)}))
    raise SystemExit(2)
raise SystemExit(main(["--target", str(target), "doctor", *remaining]))
~~~

Apply the same pattern with --repository and the canonical acceptance argument list.

- [x] **Step 4: Run focused forwarder tests**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_source_checkout.py -q -p no:cacheprovider

Expected: PASS.

### Task 3: Align the bilingual operator contract

**Files:**
- Modify: README.md
- Modify: docs/iterations/iteration-18-source-checkout-verification/requirements.md
- Modify: docs/iterations/iteration-18-source-checkout-verification/design.md
- Modify: docs/iterations/iteration-18-source-checkout-verification/acceptance.md

**Interfaces:**
- Consumes: final script flags and resolver candidate order
- Produces: reproducible English and Chinese local verification commands

- [x] **Step 1: Update the English verification section**

State that automatic discovery supports a nested product checkout and a sibling backtrader checkout, then show:

~~~bash
python scripts/doctor.py --target /path/to/backtrader
python scripts/run_acceptance.py --repository /path/to/backtrader --matrix all --require-no-mcp --require-no-agent
~~~

- [x] **Step 2: Update the equivalent Chinese verification section**

Use the same flags, path meaning, candidate order, and non-discovery fallback.

- [x] **Step 3: Search for stale implicit-root claims**

Run: rg -n "scripts/doctor.py|scripts/run_acceptance.py" README.md docs

Expected: every executable invocation matches the final argument contract.

### Task 4: Execute the documented acceptance gate

**Files:**
- Modify: docs/iterations/iteration-18-source-checkout-verification/acceptance.md

**Interfaces:**
- Consumes: the finished code and the two source-checkout command paths
- Produces: current-run evidence in the acceptance document

- [x] **Step 1: Rebuild the distribution manifest**

Run: /Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_manifest.py

Expected: the command reports a new manifest hash and includes the new source module and changed
forwarders. Do not edit manifest.json manually.

- [x] **Step 2: Run focused tests and style checks**

Run:

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests/test_source_checkout.py -q -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m ruff check .
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m black --check .
~~~

Expected: all commands exit 0.

- [x] **Step 3: Run full regression and reproducibility checks**

Run:

~~~bash
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B -m pytest tests -q -p no:cacheprovider
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/build_catalog.py --check
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/doctor.py
/Users/yunjinqi/opt/anaconda3/bin/conda run -n base python -B scripts/run_acceptance.py --matrix all --require-no-mcp --require-no-agent
git diff --check
~~~

Expected: each command exits 0; doctor reports passed=true; acceptance reports 14 passing cells and passed=true; diff check is empty.

- [x] **Step 4: Record exact observed evidence**

Add the exact command, exit status, observed test count, and full-matrix summary to acceptance.md. Mark only this iteration's requirements as passed.

## Self-Review

- Spec coverage: Task 1 covers FR-1; Task 2 covers FR-2 and FR-3; Task 3 covers FR-4; Task 4 covers FR-5 and every success criterion.
- Placeholder scan: every implementation and verification step contains an executable instruction.
- Type consistency: both forwarders consume Path | None and receive a resolved Path; both use the same resolver and SourceCheckoutNotFound code.
