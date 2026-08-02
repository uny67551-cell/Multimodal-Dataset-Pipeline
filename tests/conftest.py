"""Shared fixtures for pipeline tests."""

from pathlib import Path
import pytest
from PIL import Image

@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    """
    Create a temporary directory with test files:
    - valid.jpg      : normal image
    - empty.jpg      : 0-byte file
    - notes.txt      : non-image file
    - sub/photo.png  : nested image
    """
    root = tmp_path / "sample"
    root.mkdir()

    # ↓↓↓ Create test files ↓↓↓

    # valid jpg
    valid = root / "valid.jpg"
    Image.new("RGB", (64, 48), color=(255, 0, 0)).save(valid, format="JPEG")

    # empty file
    empty = root / "empty.jpg"
    empty.write_bytes(b"") # 0-byte file

    # non-image
    (root / "notes.txt").write_text("not an image", encoding="utf-8") # non-image file

    # nested image
    nested = root / "sub" # nested image
    nested.mkdir()
    Image.new("RGB", (32, 32), color=(0, 255, 0)).save(
        nested / "photo.png",
        format="PNG",
    )


    return root