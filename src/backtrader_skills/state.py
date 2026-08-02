"""File-backed, hash-bound, expiring one-time approval capabilities."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

from filelock import FileLock, Timeout

from .canonical import atomic_write_json, canonical_hash, load_json
from .errors import ApprovalError, ApprovalLockTimeout, IntegrityError
from .runtime import RuntimePaths

TOKEN_STATES = {"ISSUED", "CONSUMED", "REVOKED", "EXPIRED"}
TOKEN_KINDS = {"render_write", "run_execution", "install_write", "uninstall_write"}
DEFAULT_TTL_SECONDS = 15 * 60
MAX_TTL_SECONDS = 60 * 60
DEFAULT_LOCK_TIMEOUT_SECONDS = 10.0


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _token_digest(token_id: str) -> str:
    return hashlib.sha256(token_id.encode("utf-8")).hexdigest()


class _ApprovalClaim:
    def __init__(self, store: "TokenStore", token_id: str, record: dict[str, Any]) -> None:
        self._store = store
        self._token_id = token_id
        self._record = record
        self._consumed = False

    @property
    def consumed(self) -> bool:
        return self._consumed

    def consume(self) -> dict[str, Any]:
        if self._consumed:
            raise ApprovalError("approval token claim is already consumed")
        public = self._store._consume_unlocked(self._token_id, self._record)
        self._consumed = True
        return public


class TokenStore:
    def __init__(
        self,
        paths: RuntimePaths,
        *,
        clock: Callable[[], datetime] | None = None,
        lock_timeout_seconds: float = DEFAULT_LOCK_TIMEOUT_SECONDS,
    ) -> None:
        if lock_timeout_seconds < 0:
            raise ApprovalError("approval lock timeout must be non-negative")
        self.paths = paths.ensure()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._lock_timeout_seconds = lock_timeout_seconds
        self._workspace_subject_hash = canonical_hash({"workspace": self.paths.target.as_posix()})

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None:
            raise ApprovalError("token clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc)

    def _path(self, token_id: str) -> Path:
        if not token_id.startswith("tok_") or len(token_id) != 68:
            raise ApprovalError("approval token handle is invalid")
        return self.paths.tokens / f"{_token_digest(token_id)}.json"

    def _lock_path(self, token_id: str) -> Path:
        return self._path(token_id).with_suffix(".lock")

    @contextmanager
    def _locked(self, token_id: str) -> Iterator[None]:
        if not self._path(token_id).is_file():
            raise ApprovalError("approval token does not exist")
        try:
            with FileLock(str(self._lock_path(token_id)), timeout=self._lock_timeout_seconds):
                yield
        except Timeout as error:
            raise ApprovalLockTimeout("approval token is busy; retry the operation") from error

    def _write(self, token_id: str, record: dict[str, Any]) -> None:
        atomic_write_json(self._path(token_id), record)

    @staticmethod
    def _public(token_id: str, record: dict[str, Any]) -> dict[str, Any]:
        return {"token_id": token_id, **record}

    def issue(
        self,
        kind: str,
        bindings: dict[str, Any],
        *,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
    ) -> dict[str, Any]:
        if kind not in TOKEN_KINDS:
            raise ApprovalError(f"unsupported token kind: {kind}")
        if not 1 <= ttl_seconds <= MAX_TTL_SECONDS:
            raise ApprovalError(f"token ttl_seconds must be between 1 and {MAX_TTL_SECONDS}")
        issued_at = self._now()
        token_id = f"tok_{secrets.token_hex(32)}"
        record = {
            "schema_version": "approval-token-v2",
            "token_digest": _token_digest(token_id),
            "kind": kind,
            "state": "ISSUED",
            "binding_hash": canonical_hash(bindings),
            "workspace_subject_hash": self._workspace_subject_hash,
            "nonce": secrets.token_hex(16),
            "issued_at": _format_time(issued_at),
            "expires_at": _format_time(issued_at + timedelta(seconds=ttl_seconds)),
            "approved_at": None,
            "consumed_at": None,
            "revoked_at": None,
            "expired_at": None,
            "revocation_reason": None,
        }
        self._write(token_id, record)
        return self._public(token_id, record)

    def _get_unlocked(self, token_id: str) -> dict[str, Any]:
        path = self._path(token_id)
        record = cast(dict[str, Any], load_json(path))
        expected_digest = _token_digest(token_id)
        if not hmac.compare_digest(str(record.get("token_digest", "")), expected_digest):
            raise IntegrityError("approval token digest is invalid")
        if record.get("state") not in TOKEN_STATES:
            raise IntegrityError("approval token has an invalid state")
        if not hmac.compare_digest(
            str(record.get("workspace_subject_hash", "")),
            self._workspace_subject_hash,
        ):
            raise IntegrityError("approval token belongs to a different workspace")
        if record["state"] == "ISSUED" and self._now() >= _parse_time(record["expires_at"]):
            record["state"] = "EXPIRED"
            record["expired_at"] = _format_time(self._now())
            self._write(token_id, record)
        return record

    def get(self, token_id: str) -> dict[str, Any]:
        with self._locked(token_id):
            return self._public(token_id, self._get_unlocked(token_id))

    def approve(self, token_id: str) -> dict[str, Any]:
        with self._locked(token_id):
            record = self._get_unlocked(token_id)
            if record["state"] != "ISSUED":
                raise ApprovalError(f"only issued tokens can be approved; got {record['state']}")
            if record["approved_at"] is not None:
                raise ApprovalError("approval token has already been approved")
            record["approved_at"] = _format_time(self._now())
            self._write(token_id, record)
            return self._public(token_id, record)

    def revoke(self, token_id: str) -> dict[str, Any]:
        with self._locked(token_id):
            record = self._get_unlocked(token_id)
            if record["state"] != "ISSUED":
                raise ApprovalError(f"only issued tokens can be revoked; got {record['state']}")
            record["state"] = "REVOKED"
            record["revoked_at"] = _format_time(self._now())
            record["revocation_reason"] = "explicit"
            self._write(token_id, record)
            return self._public(token_id, record)

    def _verify_unlocked(
        self,
        token_id: str,
        kind: str,
        bindings: dict[str, Any],
    ) -> dict[str, Any]:
        record = self._get_unlocked(token_id)
        if record["kind"] != kind:
            raise ApprovalError("approval token kind does not match the requested operation")
        if record["state"] != "ISSUED":
            raise ApprovalError(f"approval token must be issued; got {record['state']}")
        if record["approved_at"] is None:
            raise ApprovalError("approval token requires an explicit approval action")
        if not hmac.compare_digest(str(record["binding_hash"]), canonical_hash(bindings)):
            record["state"] = "REVOKED"
            record["revoked_at"] = _format_time(self._now())
            record["revocation_reason"] = "binding_drift"
            self._write(token_id, record)
            raise IntegrityError("approval token bindings changed after validation")
        return record

    def verify(self, token_id: str, kind: str, bindings: dict[str, Any]) -> dict[str, Any]:
        with self._locked(token_id):
            return self._public(token_id, self._verify_unlocked(token_id, kind, bindings))

    def _consume_unlocked(self, token_id: str, record: dict[str, Any]) -> dict[str, Any]:
        record["state"] = "CONSUMED"
        record["consumed_at"] = _format_time(self._now())
        self._write(token_id, record)
        return self._public(token_id, record)

    def consume(self, token_id: str, kind: str, bindings: dict[str, Any]) -> dict[str, Any]:
        with self._locked(token_id):
            record = self._verify_unlocked(token_id, kind, bindings)
            return self._consume_unlocked(token_id, record)

    @contextmanager
    def claim(
        self,
        token_id: str,
        kind: str,
        bindings: dict[str, Any],
    ) -> Iterator[_ApprovalClaim]:
        """Run an approval-protected operation and consume only on normal exit."""

        with self._locked(token_id):
            record = self._verify_unlocked(token_id, kind, bindings)
            claim = _ApprovalClaim(self, token_id, record)
            yield claim
            if not claim.consumed:
                claim.consume()
