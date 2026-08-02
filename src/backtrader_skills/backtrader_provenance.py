"""Verify and bootstrap the required cloudQuant Backtrader fork without importing it."""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import json
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .errors import BacktraderSourceMismatch

CLOUDQUANT_BACKTRADER_GIT_URL = "git+https://github.com/cloudQuant/backtrader.git"
_CLOUDQUANT_REPOSITORY = "github.com/cloudquant/backtrader"
_MAX_DIAGNOSTIC_CHARS = 1000

Probe = Callable[[], dict[str, Any]]
Installer = Callable[[Path], dict[str, Any]]


def _repository_identity(value: str) -> str | None:
    """Return a normalized host/owner/repository identity for a Git URL."""

    url = value.strip()
    if url.lower().startswith("git+"):
        url = url[4:]
    if url.lower().startswith("git@"):
        host_path = url[4:]
        host, separator, path = host_path.partition(":")
        if not separator:
            return None
    else:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        path = parsed.path
    normalized_path = unquote(path).strip("/")
    if normalized_path.lower().endswith(".git"):
        normalized_path = normalized_path[:-4]
    if not host or not normalized_path:
        return None
    return f"{host.lower()}/{normalized_path.lower()}"


def is_cloudquant_backtrader_url(value: str) -> bool:
    """Return whether a Git URL denotes the mandated cloudQuant repository."""

    return _repository_identity(value) == _CLOUDQUANT_REPOSITORY


def _git_repository_root(path: Path) -> Path | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return Path(lines[-1]).resolve() if lines else None


def _git_remote_urls(repository: Path) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repository), "config", "--get-regexp", r"^remote\..*\.url$"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return []
    if completed.returncode != 0:
        return []
    urls = []
    for line in completed.stdout.splitlines():
        _, separator, url = line.partition(" ")
        if separator and url.strip():
            urls.append(url.strip())
    return urls


def _cloudquant_repository_for_package(package: Path) -> Path | None:
    """Return the cloudQuant worktree owning a package directory, if provable."""

    resolved_package = package.resolve()
    if not (resolved_package / "version.py").is_file():
        return None
    repository = _git_repository_root(resolved_package.parent)
    if repository is None:
        return None
    expected_package = repository / "backtrader"
    if not expected_package.is_dir() or expected_package.resolve() != resolved_package:
        return None
    if any(is_cloudquant_backtrader_url(url) for url in _git_remote_urls(repository)):
        return repository
    return None


def require_cloudquant_backtrader_repository(path: Path) -> Path:
    """Return the owning cloudQuant repository or raise a stable source error."""

    resolved = path.resolve()
    package = resolved / "backtrader"
    if not (package / "version.py").is_file():
        raise BacktraderSourceMismatch(
            "selected target does not contain a Backtrader source package",
            details={"path": str(resolved)},
        )
    repository = _cloudquant_repository_for_package(package)
    if repository is None:
        raise BacktraderSourceMismatch(
            "selected Backtrader source is not the required cloudQuant/backtrader fork",
            details={
                "path": str(resolved),
                "required_repository": "https://github.com/cloudQuant/backtrader.git",
            },
        )
    return repository


def _path_from_file_url(value: str) -> Path | None:
    parsed = urlparse(value)
    if parsed.scheme.lower() != "file":
        return None
    if parsed.netloc and parsed.netloc not in {"", "localhost"}:
        return None
    return Path(unquote(parsed.path)).resolve()


def _distribution_direct_url_evidence() -> list[str]:
    """Inspect PEP 610 records without importing the Backtrader package."""

    evidence: list[str] = []
    try:
        distributions = importlib.metadata.packages_distributions().get("backtrader", [])
    except importlib.metadata.PackageNotFoundError:
        distributions = []
    for distribution_name in distributions:
        try:
            direct_url = importlib.metadata.distribution(distribution_name).read_text(
                "direct_url.json"
            )
            payload = json.loads(direct_url) if direct_url else {}
        except (OSError, TypeError, ValueError, json.JSONDecodeError):
            continue
        raw_url = payload.get("url")
        if not isinstance(raw_url, str):
            continue
        if is_cloudquant_backtrader_url(raw_url):
            evidence.append("distribution-direct-url")
            continue
        local_checkout = _path_from_file_url(raw_url)
        if local_checkout is not None and _cloudquant_repository_for_package(
            local_checkout / "backtrader"
        ):
            evidence.append("distribution-local-git-remote")
    return evidence


def inspect_cloudquant_backtrader() -> dict[str, Any]:
    """Describe whether the current interpreter resolves the required fork.

    This performs metadata and Git inspection only; it intentionally does not
    import ``backtrader`` so that a foreign package cannot execute during its
    own provenance check.
    """

    importlib.invalidate_caches()
    spec = importlib.util.find_spec("backtrader")
    origin = spec.origin if spec is not None else None
    if origin is None or origin in {"built-in", "frozen"}:
        return {
            "state": "missing",
            "code": "BACKTRADER_NOT_INSTALLED",
            "message": "backtrader is not installed in the current Python environment",
        }
    try:
        module_origin = Path(origin).resolve()
    except (OSError, TypeError):
        module_origin = Path(origin)
    evidence = _distribution_direct_url_evidence()
    if _cloudquant_repository_for_package(module_origin.parent) is not None:
        evidence.append("module-local-git-remote")
    evidence = sorted(set(evidence))
    if evidence:
        return {
            "state": "verified",
            "code": "CLOUDQUANT_BACKTRADER_VERIFIED",
            "message": "installed backtrader is verified as cloudQuant/backtrader",
            "module_origin": str(module_origin),
            "evidence": evidence,
        }
    return {
        "state": "warning",
        "code": "BACKTRADER_SOURCE_WARNING",
        "message": "installed backtrader cannot be verified as cloudQuant/backtrader",
        "module_origin": str(module_origin),
    }


def _sanitize_diagnostic(value: str) -> str:
    compact = " ".join(value.split())[-_MAX_DIAGNOSTIC_CHARS:]
    return re.sub(r"((?:git\+)?https?://)[^/@\s]+@", r"\1<redacted>@", compact)


def install_cloudquant_backtrader(executable: Path) -> dict[str, Any]:
    """Install the mandated fork with the same interpreter being checked."""

    command = [
        str(executable),
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--upgrade",
        CLOUDQUANT_BACKTRADER_GIT_URL,
    ]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as error:
        return {"returncode": 127, "stderr": _sanitize_diagnostic(str(error))}
    return {
        "returncode": completed.returncode,
        "stderr": _sanitize_diagnostic(completed.stderr),
    }


def ensure_cloudquant_backtrader(
    *,
    executable: Path | None = None,
    probe: Probe | None = None,
    install: Installer | None = None,
) -> dict[str, Any]:
    """Install only a missing Backtrader module; warn rather than replace a foreign one."""

    selected_executable = executable or Path(sys.executable)
    probe = probe or inspect_cloudquant_backtrader
    install = install or install_cloudquant_backtrader
    before = probe()
    if before.get("state") != "missing":
        return before
    installation = install(selected_executable)
    returncode = installation.get("returncode")
    if returncode != 0:
        return {
            "state": "installation_failed",
            "code": "BACKTRADER_INSTALL_FAILED",
            "message": "failed to install cloudQuant/backtrader in the current Python environment",
            "stderr_summary": str(installation.get("stderr", "")),
        }
    after = probe()
    if after.get("state") == "verified":
        result = dict(after)
        result.update(
            {
                "state": "installed",
                "code": "CLOUDQUANT_BACKTRADER_INSTALLED",
                "message": "installed and verified cloudQuant/backtrader",
            }
        )
        return result
    if after.get("state") == "warning":
        result = dict(after)
        result["installation_attempted"] = True
        return result
    return {
        "state": "installation_failed",
        "code": "BACKTRADER_INSTALL_FAILED",
        "message": "cloudQuant/backtrader installation completed but the module remains unavailable",
    }
