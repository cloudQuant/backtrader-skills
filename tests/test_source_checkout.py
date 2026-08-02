"""Tests for deterministic source-checkout Backtrader discovery."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from backtrader_skills.errors import SourceCheckoutNotFound
from backtrader_skills.source_checkout import resolve_backtrader_repository

PRODUCT_ROOT = Path(__file__).resolve().parents[1]


def _make_repository(path: Path) -> Path:
    package = path / "backtrader"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "version.py").write_text('__version__ = "test"\n', encoding="utf-8")
    subprocess.run(["git", "init", "--quiet", str(path)], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "remote",
            "add",
            "origin",
            "https://github.com/cloudQuant/backtrader.git",
        ],
        check=True,
    )
    return path


def test_resolve_backtrader_repository_supports_nested_and_sibling_layouts(tmp_path: Path) -> None:
    nested_root = _make_repository(tmp_path / "nested")
    nested_product = nested_root / "backtrader-skills"
    nested_product.mkdir()
    assert resolve_backtrader_repository(nested_product) == nested_root.resolve()

    sibling_parent = tmp_path / "sibling"
    sibling_root = _make_repository(sibling_parent / "backtrader")
    sibling_product = sibling_parent / "backtrader-skills"
    sibling_product.mkdir()
    assert resolve_backtrader_repository(sibling_product) == sibling_root.resolve()


def test_resolve_backtrader_repository_honors_and_validates_explicit_path(tmp_path: Path) -> None:
    valid = _make_repository(tmp_path / "valid")
    product_root = tmp_path / "product"
    product_root.mkdir()
    assert resolve_backtrader_repository(product_root, valid) == valid.resolve()

    with pytest.raises(SourceCheckoutNotFound) as error:
        resolve_backtrader_repository(product_root, tmp_path / "missing")
    assert error.value.code == "SOURCE_CHECKOUT_NOT_FOUND"


def test_source_doctor_forwarder_uses_explicit_target(tmp_path: Path) -> None:
    repository = _make_repository(tmp_path / "backtrader")
    completed = subprocess.run(
        [sys.executable, "scripts/doctor.py", "--target", str(repository)],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["passed"] is True


def test_source_doctor_forwarder_reports_an_invalid_explicit_target(tmp_path: Path) -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/doctor.py", "--target", str(tmp_path / "missing")],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert payload["code"] == "SOURCE_CHECKOUT_NOT_FOUND"
    assert payload["status"] == "error"


def test_source_acceptance_forwarder_reports_an_invalid_explicit_repository(
    tmp_path: Path,
) -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/run_acceptance.py", "--repository", str(tmp_path / "missing")],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 2
    payload = json.loads(completed.stdout)
    assert payload["code"] == "SOURCE_CHECKOUT_NOT_FOUND"
    assert payload["status"] == "error"
