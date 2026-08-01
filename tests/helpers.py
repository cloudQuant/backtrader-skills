from __future__ import annotations

import math
import os
from datetime import date, timedelta
from pathlib import Path

import pytest

from backtrader_skills.data import DataRegistry
from backtrader_skills.runtime import RuntimePaths


def backtrader_package_dir() -> Path | None:
    """Locate the backtrader source package for test isolation.

    Honors ``BT_BACKTRADER_DIR``. Otherwise searches upward from this product
    checkout for either ``<ancestor>/backtrader`` (the package directory) or
    ``<ancestor>/backtrader/backtrader`` (a fork repository root whose package
    is nested one level deeper). Returns ``None`` when no candidate contains
    both ``version.py`` and ``__init__.py``.
    """

    candidates: list[Path] = []
    env_dir = os.environ.get("BT_BACKTRADER_DIR")
    if env_dir:
        candidates.append(Path(env_dir))
    product_root = Path(__file__).resolve().parents[1]
    for ancestor in (product_root, *product_root.parents):
        candidates.append(ancestor / "backtrader")
        candidates.append(ancestor / "backtrader" / "backtrader")
    for candidate in candidates:
        if (candidate / "version.py").is_file() and (candidate / "__init__.py").is_file():
            return candidate.resolve()
    return None


def isolated_target(tmp_path: Path) -> Path:
    package = backtrader_package_dir()
    if package is None:
        pytest.skip("backtrader source package not found; set BT_BACKTRADER_DIR")
    target = tmp_path / "target"
    target.mkdir()
    (target / "backtrader").symlink_to(package, target_is_directory=True)
    return target


def write_market_csv(path: Path, *, phase: float = 0.0, rows: int = 96) -> Path:
    lines = ["datetime,open,high,low,close,volume,openinterest"]
    start = date(2024, 1, 1)
    for index in range(rows):
        close = 100.0 + math.sin(index / 4.0 + phase) * 8.0 + index * 0.04
        opening = close - math.sin(index / 3.0) * 0.5
        high = max(opening, close) + 1.0
        low = min(opening, close) - 1.0
        lines.append(
            f"{start + timedelta(days=index)},{opening:.8f},{high:.8f},"
            f"{low:.8f},{close:.8f},{1000 + index},0"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def register_dataset(
    target: Path,
    data_root: Path,
    *,
    feed_count: int = 1,
) -> dict:
    registry = DataRegistry(RuntimePaths(target))
    registry.add_root(data_root, root_id="prices")
    feeds = []
    for index in range(feed_count):
        name = f"asset{index}"
        file_name = f"{name}.csv"
        write_market_csv(data_root / file_name, phase=index * 0.7)
        feeds.append(
            {
                "name": name,
                "symbol": name.upper(),
                "role": "execution" if index == 0 else "signal",
                "tradable": index == 0,
                "source": {
                    "root_id": "prices",
                    "relative_path": file_name,
                    "source_type": "local_file",
                },
                "format": "generic_csv",
                "columns": {},
                "timeframe": "days",
                "compression": 1,
                "timezone": "UTC",
                "transforms": [],
            }
        )
    return registry.register(
        {
            "schema_version": "data-spec-v1",
            "feeds": feeds,
            "master_feed": "asset0",
            "alignment": "intersection",
            "minimum_overlap": 0.9,
            "license": "test-only",
            "sensitivity": "public",
        }
    )
