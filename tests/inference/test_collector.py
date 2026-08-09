"""Unit tests for inference collector."""

import json
from pathlib import Path

from PIL import Image

from pipeline.inference.collector import (
    collect_from_directory,
    collect_from_report,
)


def test_collect_from_directory(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    Image.new("RGB", (16, 16), color=(0, 0, 255)).save(
        processed / "abc123.jpg",
        format="JPEG",
    )
    (processed / "notes.txt").write_text("ignore", encoding="utf-8")

    targets = collect_from_directory(processed)

    assert len(targets) == 1
    assert targets[0].image_id == "abc123"
    assert targets[0].image_path.name == "abc123.jpg"


def test_collect_from_report(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    image_path = processed / "abc123.jpg"
    Image.new("RGB", (16, 16), color=(0, 128, 0)).save(image_path, format="JPEG")

    report_path = tmp_path / "ingestion_report.json"
    report_path.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "id": "abc123",
                        "processed_path": str(image_path),
                        "status": "valid",
                    },
                    {
                        "id": "unknown",
                        "processed_path": None,
                        "status": "invalid",
                    },
                    {
                        "id": "missing",
                        "processed_path": str(processed / "nope.jpg"),
                        "status": "valid",
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    targets = collect_from_report(report_path)

    assert len(targets) == 1
    assert targets[0].image_id == "abc123"

