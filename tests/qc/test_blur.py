"""Tests for blur scoring."""

from pathlib import Path

import numpy as np
from PIL import Image

from pipeline.qc.blur import compute_blur_score, is_blurry_image


def test_solid_color_is_blurrier_than_checkerboard(tmp_path: Path) -> None:
    solid = tmp_path / "solid.jpg"
    Image.new("RGB", (64, 64), color=(128, 128, 128)).save(solid, format="JPEG")

    # High-contrast checkerboard -> higher Laplacian variance
    arr = np.zeros((64, 64, 3), dtype=np.uint8)
    arr[0:32, 0:32] = 255
    arr[32:64, 32:64] = 255
    sharp = tmp_path / "sharp.jpg"
    Image.fromarray(arr).save(sharp, format="JPEG")

    solid_score = compute_blur_score(solid)
    sharp_score = compute_blur_score(sharp)
    assert sharp_score > solid_score

    is_blurry, _ = is_blurry_image(solid, threshold=solid_score + 1.0)
    assert is_blurry is True

    is_blurry_sharp, _ = is_blurry_image(sharp, threshold=1.0)
    assert is_blurry_sharp is False