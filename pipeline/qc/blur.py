"""Blur detection using Laplacian variance."""

from pathlib import Path

import cv2
import numpy as np

from pipeline.core.exceptions import QCError


def compute_blur_score(image_path: Path) -> float:
    """
    Compute blur score for an image.

    Higher score usually means sharper image.
    """
    image_path = Path(image_path)
    data = np.fromfile(str(image_path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise QCError(f"Cannot decode image for blur score: {image_path}")

    # Variance of Laplacian is a common sharpness metric.
    return float(cv2.Laplacian(image, cv2.CV_64F).var())


def is_blurry_image(image_path: Path, threshold: float = 100.0) -> tuple[bool, float]:
    """
    Return (is_blurry, blur_score).

    Default threshold is a starting point; tune with your dataset.
    """
    score = compute_blur_score(image_path)
    return score < threshold, score # boolean expression returns True if score is less than threshold, otherwise False