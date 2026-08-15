"""Repair-path coverage: source rerender guardrails and typed-IR revision branches."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import backtrader_skills.repair as repair_module
from backtrader_skills.drafts import DraftManager
from backtrader_skills.errors import ContractError
from backtrader_skills.ir import default_strategy_spec
from backtrader_skills.repair import preview_repair, preview_spec_repair
from backtrader_skills.runtime import RuntimePaths


def _previewed_draft(tmp_path: Path, paths: RuntimePaths):
    spec = default_strategy_spec("single_data_indicator", "single_test", "ds_" + "a" * 64)
    manager = DraftManager(paths)
    return manager, manager.preview(spec)


def _write_validation_report(paths: RuntimePaths, draft_id: str, codes: list[str]) -> Path:
    report_path = paths.drafts / draft_id / "validation-report.json"
    report_path.write_text(
        json.dumps(
            {
                "schema_version": "validation-report-v1",
                "validation_hash": "f" * 64,
                "diagnostics": [{"code": code, "severity": "error"} for code in codes],
            }
        ),
        encoding="utf-8",
    )
    return report_path


def test_preview_repair_requires_a_validated_draft(tmp_path: Path) -> None:
    paths = RuntimePaths(tmp_path)
    _, draft = _previewed_draft(tmp_path, paths)
    with pytest.raises(ContractError, match="validated product-generated draft"):
        preview_repair(paths, draft["draft_id"])


def test_preview_repair_rejects_non_renderable_diagnostic_codes(tmp_path: Path) -> None:
    paths = RuntimePaths(tmp_path)
    _, draft = _previewed_draft(tmp_path, paths)
    _write_validation_report(paths, draft["draft_id"], ["BT_UNKNOWN_DIAGNOSTIC"])
    with pytest.raises(ContractError, match="cannot be source-patched"):
        preview_repair(paths, draft["draft_id"])


def test_preview_repair_rerenders_from_the_stored_spec(tmp_path: Path) -> None:
    paths = RuntimePaths(tmp_path)
    _, draft = _previewed_draft(tmp_path, paths)
    _write_validation_report(paths, draft["draft_id"], ["PY_SYNTAX_ERROR"])
    result = preview_repair(paths, draft["draft_id"])
    assert result["schema_version"] == "repair-preview-v1"
    assert result["method"] == "validated-ir-rerender"
    assert result["handled_codes"] == ["PY_SYNTAX_ERROR"]
    assert result["source_draft_id"] == draft["draft_id"]
    assert result["new_draft"]["draft_id"] != draft["draft_id"]


def test_preview_spec_repair_rejects_wrong_evidence_version(tmp_path: Path) -> None:
    paths = RuntimePaths(tmp_path)
    revised = default_strategy_spec("single_data_indicator", "single_test", "ds_" + "a" * 64)
    with pytest.raises(ContractError, match="ValidationReport v1"):
        preview_spec_repair(paths, revised, {"schema_version": "other", "diagnostics": []})


def test_preview_spec_repair_rejects_empty_diagnostics(tmp_path: Path) -> None:
    paths = RuntimePaths(tmp_path)
    revised = default_strategy_spec("single_data_indicator", "single_test", "ds_" + "a" * 64)
    evidence = {"schema_version": "validation-report-v1", "diagnostics": []}
    with pytest.raises(ContractError, match="at least one diagnostic"):
        preview_spec_repair(paths, revised, evidence)


def test_preview_spec_repair_rejects_unresolved_codes(tmp_path: Path, monkeypatch) -> None:
    paths = RuntimePaths(tmp_path)
    revised = default_strategy_spec("single_data_indicator", "single_test", "ds_" + "a" * 64)
    evidence = {
        "schema_version": "validation-report-v1",
        "validation_hash": "f" * 64,
        "diagnostics": [{"code": "BT_STILL_PRESENT", "severity": "error"}],
    }
    monkeypatch.setattr(
        repair_module,
        "_draft_diagnostic_codes",
        lambda paths, draft_id: {"BT_STILL_PRESENT"},
    )
    with pytest.raises(ContractError, match="does not resolve"):
        preview_spec_repair(paths, revised, evidence)
