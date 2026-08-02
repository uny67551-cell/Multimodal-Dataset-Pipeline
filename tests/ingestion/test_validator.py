"""Unit tests for validator module."""

from pathlib import Path
from pipeline.ingestion.validator import validate_image

def test_validate_valid_image(sample_dir: Path) -> None:
    record = validate_image(sample_dir / "valid.jpg")

    assert record.status == "valid"
    assert record.width == 64
    assert record.height == 48
    assert record.format == "JPEG"
    assert record.error_message is None
    assert len(record.id) == 12
    assert record.checksum != ""

def test_validate_empty_image(sample_dir: Path) -> None:
    record = validate_image(sample_dir / "empty.jpg")

    assert record.status == "invalid"
    assert record.error_message == "Empty file"

def test_validate_missing_file(tmp_path: Path) -> None:
    record = validate_image(tmp_path / "missing.jpg") # only path name was created

    assert record.status == "invalid"
    assert record.error_message == "File not found"