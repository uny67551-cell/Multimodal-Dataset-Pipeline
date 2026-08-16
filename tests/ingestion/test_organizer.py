"""Unit tests for organizer module."""

from pathlib import Path
from pipeline.ingestion.organizer import organize_image
from pipeline.ingestion.validator import validate_image

def test_organize_copies_valid_image(sample_dir: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "processed"
    record = validate_image(sample_dir / "valid.jpg")
    result = organize_image(record, output_dir=output_dir, mode="copy")

    assert result.status == "valid"
    assert result.processed_path is not None
    assert result.processed_path.exists()
    assert result.processed_path.name == f"{result.id}{result.extension}"

    assert (sample_dir / "valid.jpg").exists()

def test_organize_skips_existing(sample_dir: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "processed"


    first_record = validate_image(sample_dir / "valid.jpg")
    first = organize_image(first_record, output_dir=output_dir, mode="copy")
    assert first.status == "valid"


    second_record = validate_image(sample_dir / "valid.jpg")
    second = organize_image(second_record, output_dir=output_dir, mode="copy")

    assert second.status == "skipped"
    assert second.error_message == "Destination already exists"

def test_organize_skips_invalid(sample_dir: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "processed"
    record = validate_image(sample_dir / "empty.jpg")
    result = organize_image(record, output_dir=output_dir, mode="copy")

    assert result.status == "invalid"
    assert result.processed_path is None
    assert not any(output_dir.glob("*")) if output_dir.exists() else True