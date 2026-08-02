"""Scan directiories for  candidate image files."""

from pathlib import Path 
from pipeline.core.exceptions import IngestionError

def scan_directory(
    input_dir: Path, # Prompt signature
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

    input_dir = Path(input_dir) # Path is tool from pathlib, convet input to Path

    if not input_dir.exists():
        raise IngestionError(f"Input directory does not exist: {input_dir}")

    if not input_dir.is_dir():
        raise IngestionError(f"Input path is not a directory: {input_dir}")

    
    normalized_exts = {ext.lower() for ext in supported_extensions} # extention signature
    matched_paths: list[Path] = [] # Path is signature here; or list = []

    if recursive: # recursive is a boolean value, if True, scan subdirectories
        candidates = input_dir.rglob("*") # rglob is a method that returns a generator of all files in the directory and its subdirectories
    else:
        candidates = input_dir.glob("*") # glob is a method that returns a generator of all files in the directory
                                         # * is a wildcard that matches any character

    for path in candidates:
        if not path.is_file(): # is_file is a method that returns True if the path is a file
            continue # skips the rest of the loop and goes back to ‘for’ iteration

        if path.name.startswith("."): # startswith is a method that returns True if the path name starts with the given string
            continue

        if path.suffix.lower() not in normalized_exts: # suffix is a method that returns the suffix of the path
            continue
        matched_paths.append(path) # else

    return sorted(matched_paths) # sort based on the path name string


