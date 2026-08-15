"""CLI dispatch coverage for the thin argument-handling surface."""

from __future__ import annotations

import json
from contextlib import nullcontext

import pytest

import backtrader_skills.cli as cli_module
from backtrader_skills.cli import main
from backtrader_skills.ir import default_strategy_spec
from backtrader_skills.resources import resource_path

from .helpers import write_market_csv


def _write_spec(tmp_path, *, dataset_id: str | None = None) -> str:
    spec_path = tmp_path / "spec.json"
    spec = default_strategy_spec(
        "single_data_indicator", "single_test", dataset_id or ("ds_" + "a" * 64)
    )
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    return str(spec_path)


def test_cli_scaffolds_and_validates_a_spec(tmp_path, capsys) -> None:
    assert (
        main(
            [
                "spec",
                "scaffold",
                "--archetype",
                "single_data_indicator",
                "--output-profile",
                "single_test",
                "--dataset-id",
                "ds_" + "a" * 64,
            ]
        )
        == 0
    )
    scaffolded = json.loads(capsys.readouterr().out)
    assert scaffolded["spec_version"] == "strategy-spec-v1"
    spec_path = tmp_path / "scaffolded.json"
    spec_path.write_text(json.dumps(scaffolded), encoding="utf-8")
    assert main(["spec", "validate", "--spec", str(spec_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["spec_version"] == "strategy-spec-v1"
    assert payload["spec_hash"]


def test_cli_compares_metrics_and_reports_input_errors(tmp_path, capsys) -> None:
    fixture = json.loads(
        resource_path("fixtures", "comparison-positive.json").read_text(encoding="utf-8")
    )
    left = tmp_path / "left.json"
    right = tmp_path / "right.json"
    left.write_text(json.dumps(fixture["left"]), encoding="utf-8")
    right.write_text(json.dumps(fixture["right"]), encoding="utf-8")
    assert main(["compare", "--left", str(left), "--right", str(right)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
    assert main(["compare", "--left", str(tmp_path / "missing.json"), "--right", str(right)]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert payload["code"] == "INPUT_OR_IO_ERROR"


def test_cli_data_root_add_and_inspect(tmp_path, capsys) -> None:
    fixture = write_market_csv(tmp_path / "prices")
    assert (
        main(
            [
                "--target",
                str(tmp_path),
                "data",
                "root-add",
                "--directory",
                str(fixture.parent),
                "--root-id",
                "prices",
            ]
        )
        == 0
    )
    capsys.readouterr()
    feed_spec = {
        "name": "asset0",
        "symbol": "ASSET0",
        "role": "execution",
        "source": {"root_id": "prices", "relative_path": fixture.name, "source_type": "local_file"},
        "format": "generic_csv",
        "timezone": "UTC",
    }
    spec_path = tmp_path / "feed-spec.json"
    spec_path.write_text(json.dumps(feed_spec), encoding="utf-8")
    assert main(["--target", str(tmp_path), "data", "inspect", "--feed-spec", str(spec_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "dataset-inspection-v1"


def test_cli_reports_skills_errors_as_json(tmp_path, capsys) -> None:
    assert main(["approval", "show", "--token-id", "tok_missing"]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert payload["code"] != "INPUT_OR_IO_ERROR"


def test_cli_repair_spec_requires_validation_report(tmp_path, capsys) -> None:
    assert main(["repair", "--spec", _write_spec(tmp_path)]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"


def test_cli_render_preview_accepts_expected_hashes(tmp_path, capsys) -> None:
    assert (
        main(
            [
                "--target",
                str(tmp_path),
                "render",
                "preview",
                "--spec",
                _write_spec(tmp_path),
                "--expected-hash",
                "strategies/generated/whatever.py=" + "a" * 64,
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == "artifact-manifest-v1"


def test_cli_render_preview_rejects_malformed_expected_hashes(tmp_path, capsys) -> None:
    assert (
        main(
            [
                "render",
                "preview",
                "--spec",
                _write_spec(tmp_path),
                "--expected-hash",
                "no-equals",
            ]
        )
        == 2
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    assert payload["code"] == "CONTRACT_INVALID"


@pytest.mark.parametrize(
    ("state", "message"),
    [
        ("warning", "backtrader version mismatch"),
        ("verified", "verified"),
        ("missing", "no usable backtrader"),
    ],
)
def test_cli_run_backtrader_runtime_states(tmp_path, capsys, monkeypatch, state, message) -> None:
    monkeypatch.setattr(
        cli_module,
        "ensure_cloudquant_backtrader",
        lambda: {"state": state, "message": message},
    )
    warnings_check = pytest.warns(RuntimeWarning) if state == "warning" else nullcontext()
    with warnings_check:
        result = main(
            [
                "run",
                "prepare",
                "--candidate",
                str(tmp_path / "candidate.py"),
                "--dataset-id",
                "ds_1",
            ]
        )
    assert result == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "error"
    if state == "missing":
        assert payload["code"] == "BACKTRADER_INSTALL_FAILED"
