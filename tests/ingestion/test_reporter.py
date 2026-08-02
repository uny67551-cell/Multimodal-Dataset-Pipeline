"""Unit tests for reporter module."""

import json
from pathlib import Path
from pipeline.ingestion.organizer import organize_batch
from pipeline.ingestion.reporter import build_report, export_report
from pipeline.ingestion.validator import validate_batch

def test_build_report_summary(sample_dir: Path, tmp_path: Path) -> None:
    paths = [
        sample_dir / "valid.jpg",
        sample_dir / "empty.jpg",
    ]
    records = validate_batch(paths, show_progress=False)
    records = organize_batch(records, output_dir=tmp_path / "processed")
    report = build_report(
        records=records,
        input_dir=sample_dir,
        output_dir=tmp_path / "processed",
    )
    summary = report["summary"]

    assert summary["total_scanned"] == 2
    assert summary["valid"] == 1
    assert summary["invalid"] == 1
    assert summary["skipped"] == 0
    assert len(report["records"]) == 2

def test_export_report_writes_json(sample_dir: Path, tmp_path: Path) -> None:
    paths = [sample_dir / "valid.jpg"]
    records = validate_batch(paths, show_progress=False)
    report = build_report(
        records=records,
        input_dir=sample_dir,
        output_dir=tmp_path / "processed",
    )
    output_path = tmp_path / "outputs" / "ingestion_report.json"
    export_report(report, output_path)
    
    assert output_path.exists()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["pipeline"] == "ingestion"
    assert data["summary"]["total_scanned"] == 1