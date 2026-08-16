"""Detect corrupt or unreadable images."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFile


def is_corrupt_image(image_path: Path) -> tuple[bool, str | None]:
    """
    Return (is_corrupt, error_message).

    A file is corrupt if OpenCV/Pillow cannot fully decode pixel data.
    """
    image_path = Path(image_path)

    if not image_path.exists():
        return True, "File not found"

    if image_path.stat().st_size == 0:
        return True, "Empty file"


    previous = ImageFile.LOAD_TRUNCATED_IMAGES
    ImageFile.LOAD_TRUNCATED_IMAGES = False

    try:
        with Image.open(image_path) as img:
            img.verify()

        with Image.open(image_path) as img:
            img.load()
            width, height = img.size
            if width <= 0 or height <= 0:
                return True, f"Invalid dimensions: {width}x{height}"
    except Exception as exc:
        return True, f"Pillow decode failed: {exc}"
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = previous


    try:
        data = np.fromfile(str(image_path), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if image is None:
            return True, "OpenCV failed to decode image"
    except Exception as exc:
        return True, f"OpenCV decode failed: {exc}"

    return False, None