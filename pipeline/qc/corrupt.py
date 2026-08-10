"""Detect corrupt or unreadable images."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFile # imgefile is used to load truncated images


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

    # Disallow truncated JPEG loads as "success".
    previous = ImageFile.LOAD_TRUNCATED_IMAGES
    ImageFile.LOAD_TRUNCATED_IMAGES = False # shut down LOAD_TRUNCATED_IMAGES mode

    try:
        with Image.open(image_path) as img:
            img.verify()  # verify if the file header is valid

        with Image.open(image_path) as img:
            img.load()  # force full decode
            width, height = img.size
            if width <= 0 or height <= 0:
                return True, f"Invalid dimensions: {width}x{height}"
    except Exception as exc:
        return True, f"Pillow decode failed: {exc}"
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = previous # restore the previous state; excute finally before return

    # Cross-check with OpenCV (used later for blur).
    try:
        data = np.fromfile(str(image_path), dtype=np.uint8) # read the image file as a binary string
        image = cv2.imdecode(data, cv2.IMREAD_COLOR) # decode the image using OpenCV
        if image is None:
            return True, "OpenCV failed to decode image"
    except Exception as exc:
        return True, f"OpenCV decode failed: {exc}"

    return False, None