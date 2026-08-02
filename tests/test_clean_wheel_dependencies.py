from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import backtrader_skills.acceptance as acceptance_module
from backtrader_skills.acceptance import (
    _install_clean_wheel,
    _probe_clean_runtime_dependencies,
)

from .conftest import PRODUCT_ROOT


def build_wheel(output: Path) -> Path:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(output),
            str(PRODUCT_ROOT),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return next(output.glob("*.whl"))


def test_clean_wheel_resolves_filelock_inside_the_install_target(tmp_path: Path) -> None:
    wheel = build_wheel(tmp_path / "wheel")
    install_root = tmp_path / "installed"
    install_root.mkdir()

    _install_clean_wheel(wheel, install_root, tmp_path)
    dependencies = _probe_clean_runtime_dependencies(install_root)

    filelock = dependencies["filelock"]
    module_path = Path(filelock["module_path"])
    assert filelock["origin_verified"] is True
    assert not module_path.is_absolute()
    assert ".." not in module_path.parts
    assert (install_root / module_path).resolve(strict=True).is_relative_to(install_root.resolve())
    assert filelock["version"]


def test_clean_wheel_runs_installer_smoke_without_source_checkout(tmp_path: Path) -> None:
    wheel = build_wheel(tmp_path / "wheel")
    install_root = tmp_path / "installed"
    install_root.mkdir()

    _install_clean_wheel(wheel, install_root, tmp_path)
    assert hasattr(acceptance_module, "_smoke_clean_installer")
    smoke = acceptance_module._smoke_clean_installer(install_root, tmp_path / "installer-target")

    assert smoke["passed"] is True
    assert smoke["host"] == "codex"
    assert set(smoke["installed_skills"]) == {
        "backtrader-strategy-author",
        "backtrader-strategy-review",
        "backtrader-strategy-test",
    }
    assert smoke["installed_file_count"] > 0
