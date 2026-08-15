from __future__ import annotations

import re

from .conftest import PRODUCT_ROOT
from .test_ci_python_matrix import job_block

MKDOCS_CONFIG = PRODUCT_ROOT / "mkdocs.yml"
READTHEDOCS_CONFIG = PRODUCT_ROOT / ".readthedocs.yaml"
DOCS_WORKFLOW = PRODUCT_ROOT / ".github" / "workflows" / "docs.yml"
CI_WORKFLOW = PRODUCT_ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = PRODUCT_ROOT / "pyproject.toml"
DOCS_DIR = PRODUCT_ROOT / "docs"

# Nav pages of the published site. The i18n plugin resolves each base name to
# its per-language file (<page>.<locale>.md), so every page must ship in both
# languages for the bilingual site contract to hold.
NAV_PAGES = ("index.md", "skills.md", "evals.md", "changelog.md", "roadmap.md")
LANGUAGES = ("en", "zh")


def yaml_block(text: str, marker: str) -> str | None:
    """Return the indented body following ``marker``.

    ``marker`` must match a whole line. The block ends at the first following
    non-empty line with no leading indentation (a top-level YAML key).
    """
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line == marker:
            break
    else:
        return None
    body = []
    for line in lines[index + 1 :]:
        if not line.strip():
            continue
        if not line.startswith("  "):
            break
        body.append(line)
    return "\n".join(body)


def test_mkdocs_configures_a_strict_bilingual_material_site() -> None:
    config = MKDOCS_CONFIG.read_text(encoding="utf-8")

    assert "site_name: backtrader-skills" in config
    assert "strict: true" in config
    assert "name: material" in config

    plugin = yaml_block(config, "  - i18n:")
    assert plugin is not None, "mkdocs.yml has no i18n plugin block"
    assert "docs_structure: suffix" in plugin
    assert "fallback_to_default: false" in plugin
    assert "locale: en" in plugin
    assert "locale: zh" in plugin
    assert "default: true" in plugin

    nav = yaml_block(config, "nav:")
    assert nav is not None, "mkdocs.yml has no nav block"
    for page in NAV_PAGES:
        assert page in nav, f"mkdocs.yml nav is missing {page}"


def test_every_nav_page_ships_in_both_languages() -> None:
    missing = [
        f"{page.removesuffix('.md')}.{language}.md"
        for page in NAV_PAGES
        for language in LANGUAGES
        if not (DOCS_DIR / f"{page.removesuffix('.md')}.{language}.md").is_file()
    ]
    assert not missing, f"bilingual docs site pages missing: {sorted(missing)}"


def test_readthedocs_config_builds_the_mkdocs_site_with_the_docs_extra() -> None:
    config = READTHEDOCS_CONFIG.read_text(encoding="utf-8")

    assert "version: 2" in config
    assert "os: ubuntu-22.04" in config
    assert 'python: "3.11"' in config
    assert "configuration: mkdocs.yml" in config
    assert "path: ." in config
    assert "extra_requirements:" in config
    assert "- docs" in config


def test_docs_workflow_publishes_the_site_on_master_push_only() -> None:
    workflow = DOCS_WORKFLOW.read_text(encoding="utf-8")

    assert "on:" in workflow
    assert "push:" in workflow
    assert "branches: [master]" in workflow
    assert "pull_request" not in workflow
    assert 'python-version: "3.11"' in workflow
    assert 'python -m pip install -e ".[docs]"' in workflow
    assert "mkdocs build --strict" in workflow
    assert "peaceiris/actions-gh-pages@v4" in workflow
    assert "github_token: ${{ secrets.GITHUB_TOKEN }}" in workflow
    assert "publish_dir: ./site" in workflow


def test_ci_quality_job_gates_the_docs_build() -> None:
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    quality = job_block(workflow, "quality")

    assert 'python -m pip install -e ".[dev]"' in quality
    assert "mkdocs build --strict" in quality


def test_pyproject_docs_extra_declares_the_site_toolchain_and_feeds_dev() -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    docs_extra = re.search(r"^docs = \[(?P<dependencies>[^\]]+)\]$", pyproject, re.MULTILINE)
    dev_extra = re.search(r"^dev = \[(?P<dependencies>[^\]]+)\]$", pyproject, re.MULTILINE)

    assert docs_extra is not None, "pyproject.toml has no docs extra"
    assert dev_extra is not None, "pyproject.toml has no dev extra"
    for dependency in ('"mkdocs-material>=9"', '"mkdocs-static-i18n>=1.0"'):
        assert dependency in docs_extra.group("dependencies"), f"docs extra misses {dependency}"
        assert dependency in dev_extra.group("dependencies"), f"dev extra misses {dependency}"
