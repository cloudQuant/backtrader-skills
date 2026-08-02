"""Cross-process regression tests for one-time approval tokens."""

from __future__ import annotations

import multiprocessing
from pathlib import Path
from typing import Any

import pytest
from filelock import Timeout

import backtrader_skills.state as state_module
from backtrader_skills.errors import ApprovalError, ApprovalLockTimeout
from backtrader_skills.runtime import RuntimePaths
from backtrader_skills.state import TokenStore

BINDINGS = {"draft_id": "draft_concurrency", "draft_hash": "a" * 64}


class BarrierTokenStore(TokenStore):
    """Expose an old verify-to-consume gap whenever a caller uses verify publicly."""

    def __init__(self, paths: RuntimePaths, barrier: Any) -> None:
        super().__init__(paths)
        self._barrier = barrier

    def verify(self, token_id: str, kind: str, bindings: dict[str, Any]) -> dict[str, Any]:
        public = super().verify(token_id, kind, bindings)
        self._barrier.wait(timeout=10)
        return public


class AlwaysTimeout:
    def __enter__(self) -> None:
        raise Timeout("forced lock timeout")

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> bool:
        return False


def _issue_approved_token(tmp_path: Path) -> tuple[TokenStore, Path, str]:
    target = tmp_path / "target"
    store = TokenStore(RuntimePaths(target))
    token = store.issue("render_write", BINDINGS)
    store.approve(token["token_id"])
    return store, target, token["token_id"]


def _same_token_worker(
    target: str,
    token_id: str,
    start: Any,
    barrier: Any,
    results: Any,
    worker_id: int,
    operation: str,
) -> None:
    store = BarrierTokenStore(RuntimePaths(Path(target)), barrier)
    try:
        start.wait(timeout=10)
        if operation == "claim":
            with store.claim(token_id, "render_write", BINDINGS):
                effect = Path(target) / "effects" / f"{worker_id}.txt"
                effect.parent.mkdir(parents=True, exist_ok=True)
                effect.write_text("claimed\n", encoding="utf-8")
        else:
            store.consume(token_id, "render_write", BINDINGS)
        results.put(("consumed", worker_id))
    except ApprovalError as error:
        results.put(("error", error.code))
    except Exception as error:  # pragma: no cover - assertion reports unexpected failures.
        results.put(("unexpected", type(error).__name__))


def _run_same_token_workers(
    tmp_path: Path,
    operation: str,
) -> tuple[list[tuple[str, object]], Path, TokenStore, str]:
    store, target, token_id = _issue_approved_token(tmp_path)
    context = multiprocessing.get_context("spawn")
    start = context.Event()
    barrier = context.Barrier(2)
    results = context.Queue()
    workers = [
        context.Process(
            target=_same_token_worker,
            args=(str(target), token_id, start, barrier, results, worker_id, operation),
        )
        for worker_id in range(2)
    ]
    for worker in workers:
        worker.start()
    start.set()
    for worker in workers:
        worker.join(timeout=20)
        if worker.is_alive():
            worker.terminate()
            worker.join(timeout=5)
            pytest.fail("same-token worker did not finish")
        assert worker.exitcode == 0
    return [results.get(timeout=5) for _ in workers], target, store, token_id


def test_consume_serializes_same_token_across_processes(tmp_path: Path) -> None:
    results, _target, store, token_id = _run_same_token_workers(tmp_path, "consume")
    assert sorted(result[0] for result in results) == ["consumed", "error"]
    assert store.get(token_id)["state"] == "CONSUMED"


def test_claim_serializes_same_token_and_side_effects_across_processes(tmp_path: Path) -> None:
    results, target, store, token_id = _run_same_token_workers(tmp_path, "claim")
    assert sorted(result[0] for result in results) == ["consumed", "error"]
    assert len(list((target / "effects").glob("*.txt"))) == 1
    assert store.get(token_id)["state"] == "CONSUMED"


def test_claim_exception_leaves_token_available(tmp_path: Path) -> None:
    store, _target, token_id = _issue_approved_token(tmp_path)
    with pytest.raises(RuntimeError):
        with store.claim(token_id, "render_write", BINDINGS):
            raise RuntimeError("simulated write failure")
    assert store.get(token_id)["state"] == "ISSUED"

    with store.claim(token_id, "render_write", BINDINGS):
        pass
    assert store.get(token_id)["state"] == "CONSUMED"


def test_token_lock_timeout_has_a_stable_error_code(tmp_path: Path, monkeypatch) -> None:
    store, _target, token_id = _issue_approved_token(tmp_path)
    monkeypatch.setattr(state_module, "FileLock", lambda *_args, **_kwargs: AlwaysTimeout())
    with pytest.raises(ApprovalLockTimeout) as error:
        store.consume(token_id, "render_write", BINDINGS)
    assert error.value.code == "APPROVAL_LOCK_TIMEOUT"
