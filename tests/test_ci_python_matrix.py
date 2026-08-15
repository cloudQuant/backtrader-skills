from __future__ import annotations

import re

from .conftest import PRODUCT_ROOT

WORKFLOW = PRODUCT_ROOT / ".github" / "workflows" / "ci.yml"
ACCEPTANCE_WORKFLOW = PRODUCT_ROOT / ".github" / "workflows" / "acceptance.yml"
PYPROJECT = PRODUCT_ROOT / "pyproject.toml"


def job_block(workflow: str, name: str) -> str:
    marker = f"  {name}:\n"
    start = workflow.index(marker)
    following = workflow[start + len(marker) :]
    next_job = re.search(r"\n  [a-z][a-z0-9-]*:\n", following)
    return following[: next_job.start()] if next_job else following


def test_ci_enforces_the_published_python_support_matrix() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    quality = job_block(workflow, "quality")
    supported = job_block(workflow, "test-supported-python")

    assert 'python-version: "3.11"' in quality
    assert 'python -m pip install -e ".[dev]"' in quality
    assert "python -m mypy src/backtrader_skills" in quality
    assert "python -m pytest" not in quality

    assert "fail-fast: false" in supported
    assert 'python-version: ["3.10", "3.11", "3.12", "3.13"]' in supported
    assert "python-version: ${{ matrix.python-version }}" in supported
    assert 'python -m pip install -e ".[test]"' in supported
    assert supported.count("python -m pytest tests -q") == 1


def test_ci_extras_declare_the_no_isolation_build_backend() -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    test_extra = re.search(r"^test = \[(?P<dependencies>[^\]]+)\]$", pyproject, re.MULTILINE)
    dev_extra = re.search(r"^dev = \[(?P<dependencies>[^\]]+)\]$", pyproject, re.MULTILINE)

    assert test_extra is not None
    assert dev_extra is not None
    assert '"setuptools>=68"' in test_extra.group("dependencies")
    assert '"setuptools>=68"' in dev_extra.group("dependencies")


def test_master_only_acceptance_workflow_runs_full_acceptance_with_coverage_gate() -> None:
    workflow = ACCEPTANCE_WORKFLOW.read_text(encoding="utf-8")

    assert "on:" in workflow
    assert "push:" in workflow
    assert "branches: [master]" in workflow
    assert "pull_request" not in workflow
    assert 'python-version: "3.11"' in workflow
    assert 'python -m pip install -e ".[dev]"' in workflow
    assert "repository: cloudQuant/backtrader" in workflow
    assert "path: backtrader-fork" in workflow
    assert "BT_BACKTRADER_DIR: backtrader-fork/backtrader" in workflow
    assert (
        "python -m pytest --cov=src/backtrader_skills "
        "--cov-report=term-missing --cov-fail-under=80"
    ) in workflow
    assert (
        "python scripts/run_acceptance.py --repository backtrader-fork "
        "--matrix all --require-no-mcp --require-no-agent"
    ) in workflow


def test_pyproject_declares_the_coverage_gate_and_pytest_cov_extras() -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    test_extra = re.search(r"^test = \[(?P<dependencies>[^\]]+)\]$", pyproject, re.MULTILINE)
    dev_extra = re.search(r"^dev = \[(?P<dependencies>[^\]]+)\]$", pyproject, re.MULTILINE)

    assert test_extra is not None
    assert dev_extra is not None
    assert '"pytest-cov>=4"' in test_extra.group("dependencies")
    assert '"pytest-cov>=4"' in dev_extra.group("dependencies")
    assert "[tool.coverage.run]" in pyproject
    assert 'source = ["src/backtrader_skills"]' in pyproject
    assert "[tool.coverage.report]" in pyproject
    assert "fail_under = 80" in pyproject
