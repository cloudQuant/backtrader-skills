"""Thin source-checkout forwarder that rebuilds the distribution manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT / "src"))

from backtrader_skills.distribution import (  # noqa: E402
    build_distribution_manifest,
    verify_distribution_manifest,
)
from backtrader_skills.errors import IntegrityError  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify the tracked backtrader-skills distribution manifest."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify manifest.json against tracked distribution files without writing it",
    )
    arguments = parser.parse_args(argv)
    try:
        if arguments.check:
            manifest = verify_distribution_manifest(PRODUCT_ROOT)
            print(
                f"verified manifest: {manifest['manifest_hash']} ({manifest['file_count']} files)"
            )
        else:
            manifest = build_distribution_manifest(PRODUCT_ROOT)
            print(f"rebuilt manifest: {manifest['manifest_hash']} ({len(manifest['files'])} files)")
    except (IntegrityError, OSError) as error:
        print(f"manifest operation failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
