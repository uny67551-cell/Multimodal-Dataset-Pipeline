"""Unit tests for scanner module."""

from pathlib import Path
import pytest
from pipeline.core.exceptions import IngestionError
from pipeline.ingestion.scanner import scan_directory

EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

def test_scan_finds_images(sample_dir: Path) -> None:
    paths = scan_directory(sample_dir, EXTENSIONS, recursive=True)
    names = {path.name for path in paths} 

    assert "valid.jpg" in names # assert is a keyword in Python that is used to test a condition.
    assert "photo.png" in names # true or false
    assert "notes.txt" not in names

def test_scan_ignores_empty_extension_mismatch(sample_dir: Path) -> None:
    paths = scan_directory(sample_dir, (".png",), recursive=True)
    names = {path.name for path in paths}

    assert names == {"photo.png"}

def test_scan_non_recursive(sample_dir: Path) -> None:
    paths = scan_directory(sample_dir, EXTENSIONS, recursive=False)
    names = {path.name for path in paths}

    assert "valid.jpg" in names
    assert "photo.png" not in names

def test_scan_missing_directory(tmp_path: Path) -> None: # temporary path form pytest
    missing = tmp_path / "does_not_exist"
    with pytest.raises(IngestionError):  # test tool of raised error
        scan_directory(missing, EXTENSIONS) # end with if IngestionError received 