from __future__ import annotations

import json
from pathlib import Path

from .conftest import PRODUCT_ROOT


def test_published_acceptance_evidence_records_clean_dependency_origin() -> None:
    evidence = json.loads(
        (PRODUCT_ROOT / "evidence" / "acceptance-7x2.json").read_text(encoding="utf-8")
    )

    assert evidence["schema_version"] == "acceptance-result-v1"
    assert evidence["passed"] is True
    assert len(evidence["cells"]) == 14

    distribution = evidence["distribution"]
    assert distribution["mode"] == "built-wheel-clean-install"
    assert distribution["source_checkout_on_sys_path"] is False
    assert distribution["installed_origin_verified"] is True

    filelock = distribution["runtime_dependencies"]["filelock"]
    assert filelock["origin_verified"] is True
    assert isinstance(filelock["version"], str) and filelock["version"]
    assert isinstance(filelock["module_path"], str) and filelock["module_path"]
    module_path = Path(filelock["module_path"])
    assert not module_path.is_absolute()
    assert ".." not in module_path.parts

    installer_smoke = distribution["installer_smoke"]
    assert installer_smoke["passed"] is True
    assert installer_smoke["host"] == "codex"
    assert set(installer_smoke["installed_skills"]) == {
        "backtrader-strategy-author",
        "backtrader-strategy-review",
        "backtrader-strategy-test",
    }
    assert installer_smoke["installed_file_count"] > 0
