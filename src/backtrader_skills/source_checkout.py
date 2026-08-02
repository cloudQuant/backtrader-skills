"""Deterministic Backtrader repository discovery for source-checkout helpers."""

from __future__ import annotations

from pathlib import Path

from .backtrader_provenance import require_cloudquant_backtrader_repository
from .errors import SourceCheckoutNotFound


def is_backtrader_repository(path: Path) -> bool:
    """Return whether path has the minimal Backtrader source layout."""

    return (path / "backtrader" / "version.py").is_file()


def resolve_backtrader_repository(product_root: Path, explicit: Path | None = None) -> Path:
    """Resolve an explicit, nested, or sibling Backtrader repository root.

    An invalid explicit path is an operator error and never falls through to
    automatic discovery. Automatic discovery intentionally checks only the two
    layouts documented by the source-checkout helpers.
    """

    resolved_product_root = product_root.resolve()
    candidates = (
        (explicit,)
        if explicit is not None
        else (resolved_product_root.parent, resolved_product_root.parent / "backtrader")
    )
    for candidate in candidates:
        resolved = candidate.resolve()
        if is_backtrader_repository(resolved):
            return require_cloudquant_backtrader_repository(resolved)
    if explicit is not None:
        raise SourceCheckoutNotFound(
            f"explicit Backtrader repository is invalid: {explicit}",
            details={"path": str(explicit)},
        )
    raise SourceCheckoutNotFound(
        "unable to locate a Backtrader repository beside or around this source checkout",
        details={"candidates": [str(candidate) for candidate in candidates]},
    )
