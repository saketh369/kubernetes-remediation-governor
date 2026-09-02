"""Tests for the legacy code scanner, no AWS/Bedrock calls required."""

import textwrap
from pathlib import Path

from legacy_observability_migration.analysis.code_scanner import scan_file


def test_scan_file_finds_branching_functions(tmp_path):
    sample = tmp_path / "legacy_module.py"
    sample.write_text(
        textwrap.dedent(
            """
            def trivial():
                return 1

            def process_order(order_id):
                if order_id is None:
                    raise ValueError("missing order id")
                for item in range(3):
                    pass
                return order_id
            """
        )
    )

    candidates = scan_file(sample, min_branches=1)
    names = {c.name for c in candidates}

    assert "process_order" in names
    assert "trivial" not in names  # no branches, filtered out
