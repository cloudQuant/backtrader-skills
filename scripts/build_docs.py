"""Build the docs site with a host-specific site_url injected into mkdocs.yml.
mkdocs-static-i18n derives the language-switcher links from config.site_url, so
each host needs its base URL baked in at build time; the checked-in mkdocs.yml
is never modified (a temp copy next to it gets the remaining argv passthrough).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PRODUCT_ROOT / "mkdocs.yml"
DEFAULT_SITE_URL = "https://cloudquant.github.io/backtrader-skills/"


def inject_site_url(text: str, url: str) -> str:
    """Set the top-level ``site_url`` in ``text`` to ``url`` (replace or insert)."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("site_url:"):
            lines[index] = f"site_url: {url}"
            break
    else:
        lines.insert(1, f"site_url: {url}")
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def fail(code: str, message: str) -> int:
    print(json.dumps({"status": "error", "code": code, "message": message}))
    return 2


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        if not CONFIG_PATH.is_file():
            return fail("MKDOCS_CONFIG_NOT_FOUND", f"missing mkdocs config: {CONFIG_PATH}")
        text = CONFIG_PATH.read_text(encoding="utf-8")
        config = inject_site_url(text, os.environ.get("DOCS_SITE_URL", DEFAULT_SITE_URL))
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=PRODUCT_ROOT, prefix=".mkdocs-", suffix=".yml"
        ) as temporary:
            temporary.write(config)
            temporary.flush()
            command = [sys.executable, "-m", "mkdocs", "build", "-f", temporary.name, *arguments]
            return subprocess.run(command, check=False).returncode
    except OSError as error:
        return fail("MKDOCS_BUILD_FAILED", f"mkdocs build failed: {error}")


if __name__ == "__main__":
    raise SystemExit(main())
