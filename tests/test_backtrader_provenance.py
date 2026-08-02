"""Behavioral coverage for the required cloudQuant Backtrader provenance."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import pytest

import backtrader_skills.cli as cli_module
import backtrader_skills.doctor as doctor_module
from backtrader_skills.acceptance import run_acceptance
from backtrader_skills.backtrader_provenance import (
    CLOUDQUANT_BACKTRADER_GIT_URL,
    ensure_cloudquant_backtrader,
    install_cloudquant_backtrader,
    is_cloudquant_backtrader_url,
    require_cloudquant_backtrader_repository,
)
from backtrader_skills.doctor import run_doctor
from backtrader_skills.errors import BacktraderSourceMismatch
from backtrader_skills.source_checkout import resolve_backtrader_repository


def _make_repository(path: Path, remote: str) -> Path:
    package = path / "backtrader"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    (package / "version.py").write_text('__version__ = "test"\n', encoding="utf-8")
    subprocess.run(["git", "init", "--quiet", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "remote", "add", "origin", remote], check=True)
    return path


def test_cloudquant_repository_url_normalization_accepts_https_and_ssh() -> None:
    assert is_cloudquant_backtrader_url(CLOUDQUANT_BACKTRADER_GIT_URL)
    assert is_cloudquant_backtrader_url("https://github.com/cloudQuant/backtrader")
    assert is_cloudquant_backtrader_url("git@github.com:cloudQuant/backtrader.git")
    assert is_cloudquant_backtrader_url("ssh://git@github.com/cloudQuant/backtrader.git")
    assert not is_cloudquant_backtrader_url("https://github.com/mementum/backtrader.git")


def test_repository_provenance_requires_cloudquant_origin(tmp_path: Path) -> None:
    trusted = _make_repository(tmp_path / "trusted", CLOUDQUANT_BACKTRADER_GIT_URL)
    assert require_cloudquant_backtrader_repository(trusted) == trusted.resolve()

    foreign = _make_repository(tmp_path / "foreign", "https://github.com/mementum/backtrader.git")
    with pytest.raises(BacktraderSourceMismatch) as error:
        require_cloudquant_backtrader_repository(foreign)
    assert error.value.code == "BACKTRADER_SOURCE_MISMATCH"


def test_source_checkout_rejects_a_foreign_explicit_repository(tmp_path: Path) -> None:
    product = tmp_path / "backtrader-skills"
    product.mkdir()
    foreign = _make_repository(tmp_path / "foreign", "https://github.com/mementum/backtrader.git")
    with pytest.raises(BacktraderSourceMismatch):
        resolve_backtrader_repository(product, foreign)


def test_ensure_installs_the_cloudquant_repository_only_when_module_is_missing() -> None:
    states = iter(
        [
            {"state": "missing", "code": "BACKTRADER_NOT_INSTALLED"},
            {"state": "verified", "code": "CLOUDQUANT_BACKTRADER_VERIFIED"},
        ]
    )
    calls: list[Path] = []

    def probe() -> dict[str, object]:
        return next(states)

    def install(executable: Path) -> dict[str, object]:
        calls.append(executable)
        return {"returncode": 0, "stderr": ""}

    executable = Path("/opt/example/python")
    result = ensure_cloudquant_backtrader(
        executable=executable,
        probe=probe,
        install=install,
    )

    assert calls == [executable]
    assert result["state"] == "installed"
    assert result["code"] == "CLOUDQUANT_BACKTRADER_INSTALLED"


def test_existing_foreign_package_is_a_warning_and_is_not_replaced() -> None:
    calls: list[Path] = []

    def install(executable: Path) -> dict[str, object]:
        calls.append(executable)
        return {"returncode": 0, "stderr": ""}

    result = ensure_cloudquant_backtrader(
        executable=Path("/opt/example/python"),
        probe=lambda: {
            "state": "warning",
            "code": "BACKTRADER_SOURCE_WARNING",
            "message": "installed backtrader cannot be verified as cloudQuant/backtrader",
        },
        install=install,
    )

    assert result["code"] == "BACKTRADER_SOURCE_WARNING"
    assert calls == []


def test_missing_package_install_failure_is_a_structured_error() -> None:
    result = ensure_cloudquant_backtrader(
        executable=Path("/opt/example/python"),
        probe=lambda: {"state": "missing", "code": "BACKTRADER_NOT_INSTALLED"},
        install=lambda _: {"returncode": 1, "stderr": "network unavailable"},
    )

    assert result == {
        "state": "installation_failed",
        "code": "BACKTRADER_INSTALL_FAILED",
        "message": "failed to install cloudQuant/backtrader in the current Python environment",
        "stderr_summary": "network unavailable",
    }


def test_install_uses_the_selected_interpreter_and_cloudquant_git_url(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(
            command,
            0,
            stdout="ok",
            stderr="unable to fetch https://secret@example.invalid/repository",
        )

    monkeypatch.setattr("backtrader_skills.backtrader_provenance.subprocess.run", fake_run)
    executable = Path("/opt/example/python")
    result = install_cloudquant_backtrader(executable)

    assert result["returncode"] == 0
    assert "secret" not in result["stderr"]
    assert "<redacted>@" in result["stderr"]
    assert calls == [
        [
            str(executable),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--upgrade",
            CLOUDQUANT_BACKTRADER_GIT_URL,
        ]
    ]


def test_doctor_reports_existing_foreign_runtime_as_a_warning(monkeypatch, tmp_path: Path) -> None:
    repository = _make_repository(tmp_path / "trusted", CLOUDQUANT_BACKTRADER_GIT_URL)
    monkeypatch.setattr(
        doctor_module,
        "ensure_cloudquant_backtrader",
        lambda: {
            "state": "warning",
            "code": "BACKTRADER_SOURCE_WARNING",
            "message": "installed backtrader cannot be verified as cloudQuant/backtrader",
            "module_origin": "/tmp/foreign/backtrader/__init__.py",
        },
    )

    result = run_doctor(repository)
    check = next(
        item for item in result["checks"] if item["check"] == "runtime-backtrader-provenance"
    )
    assert result["passed"] is False
    assert check == {
        "check": "runtime-backtrader-provenance",
        "passed": False,
        "severity": "warning",
        "code": "BACKTRADER_SOURCE_WARNING",
        "message": "installed backtrader cannot be verified as cloudQuant/backtrader",
        "module_origin": "/tmp/foreign/backtrader/__init__.py",
    }


def test_acceptance_rejects_a_foreign_repository_before_running_matrix(tmp_path: Path) -> None:
    foreign = _make_repository(tmp_path / "foreign", "https://github.com/mementum/backtrader.git")
    with pytest.raises(BacktraderSourceMismatch):
        run_acceptance(foreign)


def test_run_command_warns_when_current_runtime_backtrader_is_not_cloudquant(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[Path] = []

    class DummyRunner:
        def __init__(self, paths) -> None:
            calls.append(paths.target)

        def prepare(
            self, candidate: Path, dataset_id: str, *, timeout_seconds: int
        ) -> dict[str, object]:
            return {
                "candidate": str(candidate),
                "dataset_id": dataset_id,
                "timeout": timeout_seconds,
            }

    monkeypatch.setattr(
        cli_module,
        "ensure_cloudquant_backtrader",
        lambda: {
            "state": "warning",
            "code": "BACKTRADER_SOURCE_WARNING",
            "message": "installed backtrader cannot be verified as cloudQuant/backtrader",
        },
    )
    monkeypatch.setattr(cli_module, "ControlledRunner", DummyRunner)
    candidate = tmp_path / "candidate.py"
    args = argparse.Namespace(
        command="run",
        target=tmp_path,
        run_command="prepare",
        candidate=candidate,
        dataset_id="ds_example",
        timeout=42,
    )

    with pytest.warns(RuntimeWarning, match="cannot be verified"):
        result = cli_module.dispatch(args)

    assert calls == [tmp_path]
    assert result == {
        "candidate": str(candidate.resolve()),
        "dataset_id": "ds_example",
        "timeout": 42,
    }
