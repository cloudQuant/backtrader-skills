"""Typed shapes for the public comparison and validation contracts.

These TypedDicts document the stable JSON shapes returned by the public API. They are additive
type hints only; runtime values are still plain dicts serialized through canonical JSON.
"""

from __future__ import annotations

from typing import Any, TypedDict


class Diagnostic(TypedDict):
    code: str
    severity: str
    file: str
    line: int
    column: int
    rule: str
    message: str
    suggestion: str


class Summary(TypedDict):
    errors: int
    warnings: int
    passed: bool


class MetricDifference(TypedDict, total=False):
    metric: str
    left: Any
    right: Any
    rule: Any


class MetricComparison(TypedDict):
    profile_version: str
    profile_hash: str
    diagnostics: list[dict[str, Any]]
    differences: list[MetricDifference]
    passed: bool
    comparison_hash: str


class EventComparison(TypedDict):
    fields: list[str]
    left_count: int
    right_count: int
    differences: list[dict[str, Any]]
    truncated: bool
    passed: bool
    comparison_hash: str
