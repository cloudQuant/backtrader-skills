"""Canonical resource path guards against traversal and missing entries."""

from __future__ import annotations

import pytest

from backtrader_skills.errors import ContractError
from backtrader_skills.resources import resource_path


@pytest.mark.parametrize(
    ("group", "name"),
    [
        ("contracts/../policies", "comparison-profile-v1.json"),
        ("contracts", "../policies/comparison-profile-v1.json"),
        ("..", "comparison-profile-v1.json"),
    ],
)
def test_resource_path_rejects_traversal(group: str, name: str) -> None:
    with pytest.raises(ContractError, match="traversal"):
        resource_path(group, name)


def test_resource_path_rejects_missing_resource() -> None:
    with pytest.raises(ContractError, match="does not exist"):
        resource_path("contracts", "no-such-schema.json")
