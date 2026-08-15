"""Deterministic mechanical scorer for the golden-prompt skill eval suite.

Invokes the installed ``backtrader-skills`` CLI through subprocess only; never imports
backtrader_skills internals. ``run execute`` needs human approval in the host session, so it
is scored manually (see evals/README.md).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SHEET_VERSION = "skill-eval-score-sheet-v1"
TIMEOUT = 300
MANUAL_NOTE = "run execute requires human approval in the host session and is scored manually"
MANUAL_ROWS: list[dict[str, Any]] = [
    {"id": "skill_discovery", "max_score": 2, "score": None, "notes": ""},
    {"id": "correct_cli_usage", "max_score": 3, "score": None, "notes": ""},
    {"id": "artifact_validity", "max_score": 3, "score": None, "notes": ""},
    {"id": "approval_handling", "max_score": 2, "score": None, "notes": ""},
    {"id": "dual_mode_parity", "max_score": 3, "score": None, "notes": ""},
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _invoke(cli: str, target: Path, command: list[str]) -> dict[str, Any]:
    argv = [cli, "--target", str(target.resolve()), *command]
    try:
        completed = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.SubprocessError as error:
        return {"parsed": None, "parse_error": f"CLI invocation failed: {error}"}
    parsed: dict[str, Any] | None = None
    parse_error = "CLI produced no JSON output"
    if completed.stdout.strip():
        try:
            value = json.loads(completed.stdout.strip())
            parsed = value if isinstance(value, dict) else None
            parse_error = None if parsed is not None else "CLI stdout is not a JSON object"
        except json.JSONDecodeError:
            parse_error = "CLI stdout is not valid JSON"
    return {
        "stdout_tail": completed.stdout.strip()[-2000:],
        "parsed": parsed,
        "parse_error": parse_error,
    }


def _error_verdict(call: dict[str, Any], code: str, label: str) -> dict[str, Any]:
    parsed = call["parsed"]
    if parsed is not None and parsed.get("status") == "error":
        return {
            "verdict": "failed",
            "code": str(parsed.get("code", "CLI_ERROR")),
            "detail": str(parsed.get("message", "")),
        }
    return {
        "verdict": "error",
        "code": code,
        "detail": call["parse_error"] or f"{label} output is not the expected schema",
        "stdout_tail": call.get("stdout_tail", ""),
    }


def _review_verdict(call: dict[str, Any]) -> dict[str, Any]:
    parsed = call["parsed"]
    if not isinstance(parsed, dict) or parsed.get("schema_version") != "validation-report-v1":
        return dict(_error_verdict(call, "REVIEW_UNPARSEABLE", "review"), diagnostic_codes=[])
    diagnostics = parsed.get("diagnostics") or []
    return {
        "verdict": "passed" if parsed.get("status") == "passed" else "failed",
        "status": parsed.get("status"),
        "diagnostic_codes": sorted(
            {str(item.get("code")) for item in diagnostics if item.get("code")}
        ),
    }


def _prepare_verdict(dataset_id: str, call: dict[str, Any]) -> dict[str, Any]:
    parsed = call["parsed"]
    manifest = parsed.get("run_manifest") if isinstance(parsed, dict) else None
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "run-manifest-v1":
        return dict(_error_verdict(call, "PREPARE_UNPARSEABLE", "prepare"), note=MANUAL_NOTE)
    token = parsed.get("approval_token") or {}
    candidate = manifest.get("candidate") or {}
    dataset = manifest.get("dataset") or {}
    integrity = {
        "run_id": manifest.get("run_id"),
        "manifest_hash": manifest.get("manifest_hash"),
        "modes": manifest.get("modes"),
        "candidate_relative_path": candidate.get("relative_path"),
        "candidate_sha256": candidate.get("sha256"),
        "dataset_id": dataset.get("dataset_id"),
        "environment_hash": manifest.get("environment_hash"),
        "approval_token_id": token.get("token_id"),
    }
    ok = (
        bool(integrity["run_id"]),
        integrity["modes"] == ["runonce", "runnext"],
        integrity["dataset_id"] == dataset_id,
        bool(integrity["candidate_sha256"]),
        bool(integrity["approval_token_id"]),
    )
    return {
        "verdict": "passed" if all(ok) else "failed",
        "integrity": integrity,
        "note": MANUAL_NOTE,
    }


def _eval_metadata(arguments: argparse.Namespace, artifact_sha256: str | None) -> dict[str, Any]:
    return {
        "generator": "scripts/record_eval.py",
        "generated_at": _utc_now(),
        "target": str(arguments.target.resolve()),
        "artifact": str(arguments.artifact.resolve()),
        "artifact_sha256": artifact_sha256,
        "dataset_id": arguments.dataset_id,
    }


def _score(arguments: argparse.Namespace) -> dict[str, Any]:
    target = arguments.target.resolve()
    artifact = arguments.artifact.resolve()
    if not artifact.is_file():
        raise ValueError(f"artifact is not a file: {artifact}")
    cli = shutil.which("backtrader-skills")
    if cli is None:
        raise ValueError("backtrader-skills executable not found on PATH")
    review = _review_verdict(_invoke(cli, target, ["review", "--file", str(artifact)]))
    command = ["run", "prepare", "--candidate", str(artifact), "--dataset-id", arguments.dataset_id]
    prepare = _prepare_verdict(arguments.dataset_id, _invoke(cli, target, command))
    verdicts = (review["verdict"], prepare["verdict"])
    if verdicts == ("passed", "passed"):
        overall = "passed"
    elif "failed" in verdicts:
        overall = "failed"
    else:
        overall = "error"
    return {
        "score_sheet_version": SHEET_VERSION,
        "eval": _eval_metadata(arguments, _sha256(artifact)),
        "review": review,
        "run_prepare": prepare,
        "manual_rows": MANUAL_ROWS,
        "overall": {"status": overall, "mechanical_only": True, "note": MANUAL_NOTE},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="record_eval",
        description=(
            "Score one candidate artifact mechanically: run the installed CLI's review and "
            "run prepare steps, then write a JSON score sheet. run execute is scored manually."
        ),
    )
    parser.add_argument("--target", type=Path, required=True, help="backtrader checkout path")
    parser.add_argument("--artifact", type=Path, required=True, help="candidate strategy.py path")
    parser.add_argument("--dataset-id", required=True, help="full ds_<64hex> dataset ID")
    parser.add_argument("--out", type=Path, required=True, help="JSON score sheet output path")
    arguments = parser.parse_args(argv)
    try:
        sheet = _score(arguments)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        sheet = {
            "score_sheet_version": SHEET_VERSION,
            "eval": _eval_metadata(arguments, None),
            "status": "error",
            "code": "SCORER_INPUT_ERROR",
            "message": str(error),
        }
        exit_code = 2
    else:
        exit_code = 0 if sheet["overall"]["status"] == "passed" else 1
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    arguments.out.write_text(json.dumps(sheet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"score sheet written: {arguments.out}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
