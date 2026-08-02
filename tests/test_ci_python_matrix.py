from __future__ import annotations

import re

from .conftest import PRODUCT_ROOT

WORKFLOW = PRODUCT_ROOT / ".github" / "workflows" / "ci.yml"
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
