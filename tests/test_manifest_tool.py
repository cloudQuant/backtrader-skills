"""Behavioral tests for the source-checkout distribution manifest utility."""

from __future__ import annotations

import subprocess
import sys

from backtrader_skills.distribution import verify_distribution_manifest

from .conftest import PRODUCT_ROOT


def _run_manifest(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/build_manifest.py", *arguments],
        cwd=PRODUCT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_manifest_help_and_check_are_read_only() -> None:
    manifest_path = PRODUCT_ROOT / "manifest.json"
    before = manifest_path.read_bytes()
    for arguments, marker in ((("--help",), "usage:"), (("--check",), "verified manifest:")):
        completed = _run_manifest(*arguments)
        assert completed.returncode == 0, completed.stderr
        assert marker in completed.stdout
        assert manifest_path.read_bytes() == before


def test_manifest_default_rebuilds_and_verifies() -> None:
    completed = _run_manifest()
    assert completed.returncode == 0, completed.stderr
    assert "rebuilt manifest:" in completed.stdout
    assert verify_distribution_manifest(PRODUCT_ROOT)["verified"]
