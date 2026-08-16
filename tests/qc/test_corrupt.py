"""Tests for corrupt image detection."""

from pathlib import Path

from PIL import Image

from pipeline.qc.corrupt import is_corrupt_image


def test_valid_image_is_not_corrupt(tmp_path: Path) -> None:
    path = tmp_path / "ok.jpg"
    Image.new("RGB", (32, 32), color=(10, 20, 30)).save(path, format="JPEG")

    is_corrupt, error = is_corrupt_image(path)
    assert is_corrupt is False
    assert error is None


def test_empty_file_is_corrupt(tmp_path: Path) -> None:
    path = tmp_path / "empty.jpg"
    path.write_bytes(b"")

    is_corrupt, error = is_corrupt_image(path)
    assert is_corrupt is True
    assert error is not None


def test_truncated_jpeg_is_corrupt(tmp_path: Path) -> None:
    path = tmp_path / "broken.jpg"
    Image.new("RGB", (64, 64), color=(1, 2, 3)).save(path, format="JPEG")
    data = path.read_bytes()
    path.write_bytes(data[: max(20, len(data) // 4)])

    is_corrupt, error = is_corrupt_image(path)
    assert is_corrupt is True
    assert error is not None