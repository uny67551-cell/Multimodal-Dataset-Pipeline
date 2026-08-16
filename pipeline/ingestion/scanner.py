"""Scan directiories for  candidate image files."""

from pathlib import Path
from pipeline.core.exceptions import IngestionError

def scan_directory(
    input_dir: Path,
    supported_extensions: tuple[str, ...],
    recursive: bool = True,
) -> list[Path]:
    """
    Scan a directory and return sorted image file paths.
    Args:
        input_dir: Directory containing raw images.
        supported_extensions: Allowed extensions, e.g. (".jpg", ".png").
        recursive: Whether to scan subdirectories.
    Returns:
        Sorted list of matching file paths.
    Raises:
        IngestionError: If input_dir does not exist or is not a directory.
    """

    input_dir = Path(input_dir)

    if not input_dir.exists():
        raise IngestionError(f"Input directory does not exist: {input_dir}")

    if not input_dir.is_dir():
        raise IngestionError(f"Input path is not a directory: {input_dir}")


    normalized_exts = {ext.lower() for ext in supported_extensions}
    matched_paths: list[Path] = []

    if recursive:
        candidates = input_dir.rglob("*")
    else:
        candidates = input_dir.glob("*")


    for path in candidates:
        if not path.is_file():
            continue

        if path.name.startswith("."):
            continue

        if path.suffix.lower() not in normalized_exts:
            continue
        matched_paths.append(path)

    return sorted(matched_paths)


