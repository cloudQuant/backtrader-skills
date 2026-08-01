"""Thin source-checkout forwarder that rebuilds the distribution manifest."""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT / "src"))

from backtrader_skills.distribution import build_distribution_manifest  # noqa: E402

if __name__ == "__main__":
    manifest = build_distribution_manifest(PRODUCT_ROOT)
    print(f"rebuilt manifest: {manifest['manifest_hash']} ({len(manifest['files'])} files)")
