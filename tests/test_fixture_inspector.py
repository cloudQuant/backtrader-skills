"""Ephemeral fixture inspection used by the root compatibility script."""

from __future__ import annotations

import json

import pytest

from backtrader_skills.errors import ContractError
from backtrader_skills.fixture_inspector import main

from .helpers import write_market_csv


def test_fixture_inspector_prints_dataset_inspection(tmp_path, capsys) -> None:
    fixture = write_market_csv(tmp_path / "asset0.csv")
    assert main(["--fixture", str(fixture)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "dataset-inspection-v1"
    assert payload["feed"] == "fixture"
    assert payload["source"]["relative_path"] == fixture.name
    assert payload["summary"]["rows"] > 0


def test_fixture_inspector_rejects_missing_fixture(tmp_path) -> None:
    with pytest.raises(FileNotFoundError):
        main(["--fixture", str(tmp_path / "missing.csv")])


def test_fixture_inspector_rejects_unknown_format(tmp_path) -> None:
    fixture = write_market_csv(tmp_path / "asset0.csv")
    with pytest.raises(ContractError, match="adapter"):
        main(["--fixture", str(fixture), "--format", "not_an_adapter"])
