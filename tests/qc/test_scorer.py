"""Tests for QC status scoring."""

from pipeline.qc.scorer import decide_quality_status


def test_decide_quality_status_priority() -> None:
    assert decide_quality_status(
        is_corrupt=True, is_blurry=True, is_duplicate=True
    ) == "reject"
    assert decide_quality_status(
        is_corrupt=False, is_blurry=True, is_duplicate=False
    ) == "warn"
    assert decide_quality_status(
        is_corrupt=False, is_blurry=False, is_duplicate=True
    ) == "warn"
    assert decide_quality_status(
        is_corrupt=False, is_blurry=False, is_duplicate=False
    ) == "pass"