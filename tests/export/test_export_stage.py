"""Integration-style tests for ExportStage."""

import json
from pathlib import Path

from PIL import Image

from pipeline.core.config import ExportConfig, LoggingConfig, PipelineConfig
from pipeline.export.stage import ExportStage


def _write_reports(tmp_path: Path, processed: Path) -> tuple[Path, Path]:
    good = processed / "good.jpg"
    Image.new("RGB", (24, 24), color=(0, 100, 200)).save(good, format="JPEG")
    dup = processed / "dup.jpg"
    dup.write_bytes(good.read_bytes())
    empty = processed / "empty.jpg"
    empty.write_bytes(b"")

    output_dir = tmp_path / "outputs"
    output_dir.mkdir()

    meta = {
        "pipeline": "metadata",
        "records": [
            {
                "id": "good",
                "status": "complete",
                "processed_path": str(good),
                "extension": ".jpg",
                "caption": "A blue square.",
                "tags": ["blue"],
                "objects": ["square"],
                "scene": "blue",
            },
            {
                "id": "dup",
                "status": "complete",
                "processed_path": str(dup),
                "extension": ".jpg",
                "caption": "A blue square.",
                "tags": ["blue"],
                "objects": ["square"],
                "scene": "blue",
            },
            {
                "id": "empty",
                "status": "complete",
                "processed_path": str(empty),
                "extension": ".jpg",
                "caption": "broken",
                "tags": [],
                "objects": [],
                "scene": None,
            },
            {
                "id": "nocap",
                "status": "ingestion_only",
                "processed_path": str(good),
                "extension": ".jpg",
                "caption": None,
                "tags": [],
                "objects": [],
                "scene": None,
            },
        ],
    }
    qc = {
        "pipeline": "qc",
        "records": [
            {
                "image_id": "good",
                "quality_status": "pass",
                "is_corrupt": False,
                "is_blurry": False,
                "is_duplicate": False,
                "duplicate_of": None,
                "blur_score": 200.0,
            },
            {
                "image_id": "dup",
                "quality_status": "warn",
                "is_corrupt": False,
                "is_blurry": False,
                "is_duplicate": True,
                "duplicate_of": "good",
                "blur_score": 200.0,
            },
            {
                "image_id": "empty",
                "quality_status": "reject",
                "is_corrupt": True,
                "is_blurry": False,
                "is_duplicate": False,
                "duplicate_of": None,
                "blur_score": None,
            },
            {
                "image_id": "nocap",
                "quality_status": "pass",
                "is_corrupt": False,
                "is_blurry": False,
                "is_duplicate": False,
                "duplicate_of": None,
                "blur_score": 200.0,
            },
        ],
    }

    meta_path = output_dir / "metadata_report.json"
    qc_path = output_dir / "qc_report.json"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    qc_path.write_text(json.dumps(qc), encoding="utf-8")
    return meta_path, qc_path


def test_export_stage_self_contained_package(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    meta_path, qc_path = _write_reports(tmp_path, processed)
    export_dir = tmp_path / "export_pkg"

    config = PipelineConfig(
        output_dir=tmp_path / "outputs",
        export=ExportConfig(
            export_dir=export_dir,
            exclude_duplicates=True,
            include_blurry=False,
            require_caption=True,
        ),
        logging=LoggingConfig(level="WARNING", log_file=None),
    )
    stage = ExportStage(config)
    records = stage.run(metadata_report_path=meta_path, qc_report_path=qc_path)

    included = [r for r in records if r.status == "included"]
    assert len(included) == 1
    assert included[0].id == "good"

    assert (export_dir / "images" / "good.jpg").exists()
    assert not (export_dir / "images" / "dup.jpg").exists()

    ann_lines = (export_dir / "annotations.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(ann_lines) == 1
    assert json.loads(ann_lines[0])["id"] == "good"

    llava_lines = (export_dir / "llava.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(llava_lines) == 1

    report = json.loads((export_dir / "export_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["included"] == 1
    assert report["summary"]["exclude_reasons"]["duplicate"] == 1
    assert report["summary"]["exclude_reasons"]["missing_caption"] == 1
    assert report["artifacts"]["images_copied"] == 1