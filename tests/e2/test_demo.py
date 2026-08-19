from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_interactive_demo_all_scenarios_are_reproducible():
    root = Path(__file__).parents[2]
    result = subprocess.run(
        [sys.executable, str(root / "scripts/e2_demo.py"), "--all"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "[ALLOW] Alice retrieves her tenant-a waveguide source" in result.stdout
    assert "[NO EVIDENCE] Alice asks for the same query; tenant-b source is absent" in result.stdout
    assert "[DENY] Client tenant/role claims rejected" in result.stdout
    assert "[DENY] Tampered evidence rejected" in result.stdout
    assert "[PASS] audit hash chain verified" in result.stdout
