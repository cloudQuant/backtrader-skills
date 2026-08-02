"""Thin source-checkout forwarder to the canonical acceptance implementation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT / "src"))

from backtrader_skills.acceptance import main  # noqa: E402
from backtrader_skills.errors import BacktraderSourceMismatch, SourceCheckoutNotFound  # noqa: E402
from backtrader_skills.source_checkout import resolve_backtrader_repository  # noqa: E402


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--repository", type=Path)
    arguments, remaining = parser.parse_known_args(argv)
    if "-h" in remaining or "--help" in remaining:
        return main(["--help"])
    try:
        repository = resolve_backtrader_repository(PRODUCT_ROOT, arguments.repository)
    except (BacktraderSourceMismatch, SourceCheckoutNotFound) as error:
        print(
            json.dumps(
                {"status": "error", "code": error.code, "message": str(error)},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    return main(["--repository", str(repository), *remaining])


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
