"""The ``python -m backtrader_skills`` entrypoint forwards to the CLI."""

from __future__ import annotations

import os
import subprocess
import sys

from .conftest import SOURCE_ROOT


def test_python_dash_m_entrypoint_runs_the_cli() -> None:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(SOURCE_ROOT)
    completed = subprocess.run(
        [sys.executable, "-m", "backtrader_skills", "--version"],
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "0.1.0"
