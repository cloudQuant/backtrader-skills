from __future__ import annotations

import json

from backtrader_skills.canonical import canonical_hash
from backtrader_skills.compare import compare_events, compare_metrics
from backtrader_skills.resources import resource_path


def assert_hash_matches_payload(result: dict[str, object]) -> None:
    payload = dict(result)
    comparison_hash = payload.pop("comparison_hash")
    assert comparison_hash == canonical_hash(payload)


def test_metric_comparison_has_complete_public_contract_and_stable_hash() -> None:
    fixture = json.loads(
        resource_path("fixtures", "comparison-positive.json").read_text(encoding="utf-8")
    )

    result = compare_metrics(fixture["left"], fixture["right"])

    assert set(result) == {
        "profile_version",
        "profile_hash",
        "diagnostics",
        "differences",
        "passed",
        "comparison_hash",
    }
    assert result["passed"] is True
    assert_hash_matches_payload(result)


def test_event_comparison_has_complete_public_contract_and_stable_hash() -> None:
    left = [
        {
            "sequence": 1,
            "kind": "buy",
            "data": "primary",
            "size": 1.0,
            "price": 100.0,
            "status": "completed",
            "ignored": "left-only",
        }
    ]
    right = [
        {
            "sequence": 1,
            "kind": "buy",
            "data": "primary",
            "size": 1.0,
            "price": 100.0,
            "status": "completed",
            "ignored": "right-only",
        }
    ]

    result = compare_events(left, right)

    assert set(result) == {
        "fields",
        "left_count",
        "right_count",
        "differences",
        "truncated",
        "passed",
        "comparison_hash",
    }
    assert result["passed"] is True
    assert result["fields"] == ["sequence", "kind", "data", "size", "price", "status"]
    assert_hash_matches_payload(result)
