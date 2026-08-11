"""Tests for JSONL / LLaVA writers."""

import json
from pathlib import Path

from PIL import Image

from pipeline.export.writers.jsonl import write_annotations_jsonl
from pipeline.export.writers.llava import write_llava_jsonl
from pipeline.models.export_record import ExportRecord


def test_writers_only_write_included(tmp_path: Path) -> None:
    img = tmp_path / "a.jpg"
    Image.new("RGB", (8, 8), color=(9, 9, 9)).save(img, format="JPEG")

    included = ExportRecord(
        id="a",
        status="included",
        generated_at=ExportRecord.utc_now(),
        source_image_path=img,
        export_image_relpath="images/a.jpg",
        caption="A tiny patch.",
    )
    excluded = ExportRecord(
        id="b",
        status="excluded",
        generated_at=ExportRecord.utc_now(),
        source_image_path=img,
        export_image_relpath="images/b.jpg",
        caption="nope",
        exclude_reason="duplicate",
    )

    ann = write_annotations_jsonl([included, excluded], tmp_path / "annotations.jsonl")
    llava = write_llava_jsonl([included, excluded], tmp_path / "llava.jsonl")

    ann_rows = [json.loads(line) for line in ann.read_text(encoding="utf-8").splitlines()]
    llava_rows = [json.loads(line) for line in llava.read_text(encoding="utf-8").splitlines()]

    assert len(ann_rows) == 1
    assert ann_rows[0]["id"] == "a"
    assert ann_rows[0]["image"] == "images/a.jpg"

    assert len(llava_rows) == 1
    assert llava_rows[0]["conversations"][1]["value"] == "A tiny patch."