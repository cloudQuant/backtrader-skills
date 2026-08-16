from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

from .conftest import PRODUCT_ROOT

SCRIPTS_DIR = PRODUCT_ROOT / "scripts"
PAGES_SITE_URL = "https://cloudquant.github.io/backtrader-skills/"
RTD_SITE_URL = "https://backtrader-skills.readthedocs.io/en/latest/"

SAMPLE_CONFIG = """\
site_name: example
strict: true

theme:
  name: material
"""


def load_build_docs():
    """Load scripts/build_docs.py as a standalone module for inspection."""
    spec = importlib.util.spec_from_file_location("build_docs", SCRIPTS_DIR / "build_docs.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_site_url_is_the_github_pages_base() -> None:
    module = load_build_docs()

    assert module.DEFAULT_SITE_URL == PAGES_SITE_URL


def test_inject_site_url_inserts_a_top_level_site_url_when_absent() -> None:
    module = load_build_docs()

    config = module.inject_site_url(SAMPLE_CONFIG, RTD_SITE_URL)

    lines = config.splitlines()
    assert lines[0] == "site_name: example"
    assert lines[1] == f"site_url: {RTD_SITE_URL}"
    assert "strict: true" in config
    assert "theme:" in config and "name: material" in config
    assert config.endswith("\n")


def test_inject_site_url_replaces_an_existing_top_level_site_url() -> None:
    module = load_build_docs()

    original = "site_name: example\nsite_url: https://old.example/\n\nnav:\n  - Home: index.md\n"
    config = module.inject_site_url(original, RTD_SITE_URL)

    assert config == original.replace("https://old.example/", RTD_SITE_URL)


def test_inject_site_url_leaves_indented_nested_site_urls_alone() -> None:
    module = load_build_docs()

    original = "site_name: example\nplugin:\n  site_url: nested\n"
    config = module.inject_site_url(original, PAGES_SITE_URL)

    assert config == (
        "site_name: example\n" f"site_url: {PAGES_SITE_URL}\n" "plugin:\n" "  site_url: nested\n"
    )


def test_main_injects_the_pages_default_when_no_env_url_is_set(monkeypatch, tmp_path) -> None:
    module = load_build_docs()
    module.PRODUCT_ROOT = tmp_path
    module.CONFIG_PATH = tmp_path / "mkdocs.yml"
    module.CONFIG_PATH.write_text(SAMPLE_CONFIG, encoding="utf-8")
    monkeypatch.delenv("DOCS_SITE_URL", raising=False)
    written: dict[str, str] = {}

    def fake_run(command, check):  # noqa: ARG001
        written["config"] = Path(command[5]).read_text(encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.main(["--strict"]) == 0
    assert written["config"].splitlines()[1] == f"site_url: {PAGES_SITE_URL}"


def test_main_injects_the_env_url_and_passes_arguments_through(monkeypatch, tmp_path) -> None:
    module = load_build_docs()
    module.PRODUCT_ROOT = tmp_path
    module.CONFIG_PATH = tmp_path / "mkdocs.yml"
    module.CONFIG_PATH.write_text(SAMPLE_CONFIG, encoding="utf-8")
    monkeypatch.setenv("DOCS_SITE_URL", RTD_SITE_URL)
    calls: list[list[str]] = []
    written: dict[str, str] = {}

    def fake_run(command, check):  # noqa: ARG001
        calls.append(command)
        written["config"] = Path(command[5]).read_text(encoding="utf-8")
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    assert module.main(["--strict", "--site-dir", "/out/html"]) == 0
    assert len(calls) == 1
    command = calls[0]
    assert command[:5] == [module.sys.executable, "-m", "mkdocs", "build", "-f"]
    assert command[6:] == ["--strict", "--site-dir", "/out/html"]
    assert written["config"].splitlines()[1] == f"site_url: {RTD_SITE_URL}"


def test_main_returns_the_mkdocs_exit_code(monkeypatch, tmp_path) -> None:
    module = load_build_docs()
    module.PRODUCT_ROOT = tmp_path
    module.CONFIG_PATH = tmp_path / "mkdocs.yml"
    module.CONFIG_PATH.write_text(SAMPLE_CONFIG, encoding="utf-8")
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda command, check: subprocess.CompletedProcess(command, 3),
    )

    assert module.main(["--strict"]) == 3


def test_main_reports_a_structured_failure_for_a_missing_config(capsys) -> None:
    module = load_build_docs()
    module.CONFIG_PATH = PRODUCT_ROOT / "no-such-mkdocs.yml"

    code = module.main([])

    assert code == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert payload["code"] == "MKDOCS_CONFIG_NOT_FOUND"
    assert "no-such-mkdocs.yml" in payload["message"]
