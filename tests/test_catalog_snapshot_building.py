"""Synthetic-corpus catalog construction and snapshot error-path coverage."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backtrader_skills.catalog import (
    ARCHETYPES,
    build_snapshot,
    iter_catalog_ids,
    load_snapshot,
    search_snapshot,
)
from backtrader_skills.errors import ContractError, IntegrityError


def _write_corpus(functional_root: Path, package_root: Path) -> None:
    for relative in ("advanced/test_alpha.py", "beta/test_beta.py", "delta/test_delta.py"):
        path = functional_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# corpus fixture\n", encoding="utf-8")
    for relative in ("advanced/alpha", "advanced/ignored", "beta/beta", "gamma/gamma"):
        directory = package_root / relative
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "strategy_main.py").write_text("# corpus fixture\n", encoding="utf-8")
        (directory / "run.py").write_text("# corpus fixture\n", encoding="utf-8")
    advanced_alpha = package_root / "advanced" / "alpha"
    (advanced_alpha / "config.yaml").write_text("key: value\n", encoding="utf-8")
    # Prefixed strategy files alone must not make a directory a package.
    excluded = package_root / "excluded" / "skipped"
    excluded.mkdir(parents=True, exist_ok=True)
    (excluded / "pybind11_strategy.py").write_text("# excluded\n", encoding="utf-8")
    (excluded / "python_swig_strategy.py").write_text("# excluded\n", encoding="utf-8")
    (excluded / "run.py").write_text("# excluded\n", encoding="utf-8")


def _build_snapshot(tmp_path: Path) -> Path:
    functional_root = tmp_path / "functional"
    package_root = tmp_path / "packages"
    functional_root.mkdir()
    package_root.mkdir()
    _write_corpus(functional_root, package_root)
    output = tmp_path / "catalog.jsonl"
    header = build_snapshot(functional_root, package_root, output, require_expected_counts=False)
    assert header["counts"] == {"functional_tests": 3, "strategy_packages": 4, "mapped": 2}
    assert output.is_file()
    return output


def test_build_snapshot_constructs_canonical_corpus_metadata(tmp_path: Path) -> None:
    output = _build_snapshot(tmp_path)
    header, entries = load_snapshot(output)

    assert header["schema_version"] == "corpus-manifest-v1"
    assert header["entry_count"] == 5
    assert len(entries) == 5
    by_id = {entry["canonical_id"]: entry for entry in entries}

    multi_label = by_id["advanced/alpha"]
    assert multi_label["mapping_status"] == "mapped"
    assert multi_label["archetypes"] == list(ARCHETYPES)
    assert multi_label["risk_tags"] == ["multi_label_review"]
    assert any(file_["path"] == "config.yaml" for file_ in multi_label["strategy_package"]["files"])

    fallback = by_id["gamma/gamma"]
    assert fallback["archetypes"] == ["single_data_indicator"]
    assert fallback["mapping_status"] == "package_only"
    assert fallback["functional_test"] is None

    functional_only = by_id["delta/delta"]
    assert functional_only["mapping_status"] == "functional_only"
    assert functional_only["strategy_package"] is None
    assert set(iter_catalog_ids(output)) == {
        "advanced/alpha",
        "advanced/ignored",
        "beta/beta",
        "delta/delta",
        "gamma/gamma",
    }


def test_build_snapshot_enforces_expected_counts_by_default(tmp_path: Path) -> None:
    functional_root = tmp_path / "functional"
    package_root = tmp_path / "packages"
    functional_root.mkdir()
    package_root.mkdir()
    _write_corpus(functional_root, package_root)
    with pytest.raises(IntegrityError, match="catalog counts changed"):
        build_snapshot(functional_root, package_root, tmp_path / "catalog.jsonl")


def test_load_snapshot_rejects_missing_header(tmp_path: Path) -> None:
    empty = tmp_path / "empty.jsonl"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ContractError, match="header is missing"):
        load_snapshot(empty)
    wrong = tmp_path / "wrong.jsonl"
    wrong.write_text('{"schema_version": "other"}\n', encoding="utf-8")
    with pytest.raises(ContractError, match="header is missing"):
        load_snapshot(wrong)


def _records(path: Path) -> tuple[list[dict], dict, list[dict]]:
    lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return lines, lines[0], lines[1:]


def test_load_snapshot_rejects_entry_count_drift(tmp_path: Path) -> None:
    output = _build_snapshot(tmp_path)
    lines, header, entries = _records(output)
    header["entry_count"] = len(entries) + 1
    output.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in lines) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(IntegrityError, match="entry count"):
        load_snapshot(output)


def test_load_snapshot_rejects_tampered_entry_hash(tmp_path: Path) -> None:
    output = _build_snapshot(tmp_path)
    lines, _, entries = _records(output)
    entries[0]["canonical_id"] = "tampered/id"
    output.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in lines) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(IntegrityError, match="entry hash"):
        load_snapshot(output)


def test_load_snapshot_rejects_manifest_entry_drift(tmp_path: Path) -> None:
    output = _build_snapshot(tmp_path)
    lines, header, _ = _records(output)
    header["entries"][0]["id"] = "tampered"
    output.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in lines) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(IntegrityError, match="manifest entries"):
        load_snapshot(output)


def test_load_snapshot_rejects_tampered_snapshot_hash(tmp_path: Path) -> None:
    output = _build_snapshot(tmp_path)
    lines, header, _ = _records(output)
    header["counts"]["mapped"] += 1
    output.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in lines) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(IntegrityError, match="snapshot hash"):
        load_snapshot(output)


def test_search_snapshot_validates_arguments(tmp_path: Path) -> None:
    output = _build_snapshot(tmp_path)
    with pytest.raises(ContractError, match="between 1 and 10"):
        search_snapshot(output, "trend", limit=0)
    with pytest.raises(ContractError, match="between 1 and 10"):
        search_snapshot(output, "trend", limit=11)
    with pytest.raises(ContractError, match="unknown archetype"):
        search_snapshot(output, "trend", archetype="not_an_archetype")


def test_search_snapshot_empty_query_and_fuzzy_token_match(tmp_path: Path) -> None:
    output = _build_snapshot(tmp_path)
    everything = search_snapshot(output, "", limit=10)
    assert len(everything["results"]) == 5
    assert everything["template"]["archetype"] == "single_data_indicator"
    fuzzy = search_snapshot(output, "ignorex", limit=3)
    assert "advanced/ignored" in {item["canonical_id"] for item in fuzzy["results"]}
