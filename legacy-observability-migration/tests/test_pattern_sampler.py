"""Tests for log pattern sampling and normalization."""

from legacy_observability_migration.logs.pattern_sampler import sample_log_patterns


def test_sample_log_patterns_dedupes_near_identical_lines(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text(
        "\n".join(
            [
                "2024-01-01 12:00:00 order 123 processed",
                "2024-01-01 12:00:05 order 456 processed",
                "2024-01-01 12:00:10 payment failed for user 789",
            ]
        )
    )

    samples = sample_log_patterns(str(log_file), sample_size=10)

    # The two "order N processed" lines should collapse to one pattern
    assert len(samples) == 2
