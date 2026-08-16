"""Duplicate detection based on file checksums."""

from __future__ import annotations

import hashlib
from pathlib import Path

from pipeline.qc.collector import QCTarget


def compute_checksum(path: Path) -> str:
    """Compute SHA256 checksum for a file."""
    sha256 = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def find_duplicates(targets: list[QCTarget]) -> dict[str, str]:
    """
    Find duplicate images among QC targets.

    Returns:
        Mapping: duplicate_image_id -> kept_image_id

    Strategy:
    - Group by checksum (from target.checksum or computed on the fly).
    - Keep the first image_id in each group (stable because collector sorts paths
      when scanning directories; metadata order follows the report).
    - Mark the rest as duplicates of the kept id.
    """
    checksum_to_kept: dict[str, str] = {}
    duplicate_map: dict[str, str] = {}

    for target in targets:
        checksum = target.checksum or compute_checksum(target.image_path)
        if not checksum:
            continue

        kept_id = checksum_to_kept.get(checksum)
        if kept_id is None:
            checksum_to_kept[checksum] = target.image_id
            continue

        if target.image_id == kept_id:
            continue

        duplicate_map[target.image_id] = kept_id

    return duplicate_map