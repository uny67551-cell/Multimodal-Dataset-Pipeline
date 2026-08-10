"""Tests for checksum duplicate detection."""

from pathlib import Path

from PIL import Image

from pipeline.qc.collector import QCTarget
from pipeline.qc.duplicate import find_duplicates


def test_find_duplicates_marks_second_copy(tmp_path: Path) -> None:
    a = tmp_path / "a.jpg"
    b = tmp_path / "b.jpg"
    Image.new("RGB", (16, 16), color=(9, 9, 9)).save(a, format="JPEG")
    b.write_bytes(a.read_bytes())  # exact duplicate bytes

    c = tmp_path / "c.jpg"
    Image.new("RGB", (16, 16), color=(200, 0, 0)).save(c, format="JPEG")

    targets = [
        QCTarget(image_id="id_a", image_path=a),
        QCTarget(image_id="id_b", image_path=b),
        QCTarget(image_id="id_c", image_path=c),
    ]
    dup_map = find_duplicates(targets)

    assert dup_map == {"id_b": "id_a"}