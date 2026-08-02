"""Integration tests for IngestionStage."""

import json
from pathlib import Path
from pipeline.core.config import PipelineConfig, IngestionConfig, LoggingConfig
from pipeline.ingestion.stage import IngestionStage

def test_ingestion_stage_end_to_end(sample_dir: Path, tmp_path: Path) -> None:
    processed_dir = tmp_path / "processed"
    output_dir = tmp_path / "outputs"
    config = PipelineConfig(
        raw_dir=sample_dir,
        processed_dir=processed_dir,
        output_dir=output_dir,
        ingestion=IngestionConfig(
            supported_extensions=(".jpg", ".jpeg", ".png", ".webp", ".bmp"),
            recursive=True,
            mode="copy",
        ),
        logging=LoggingConfig(level="WARNING", log_file=None),
    )
    stage = IngestionStage(config)
    records = stage.run()
    # Should scan valid.jpg, empty.jpg, sub/photo.png (notes.txt ignored)
    assert len(records) == 3
    statuses = {record.status for record in records}
    assert "valid" in statuses
    assert "invalid" in statuses
    # Processed directory should contain at least the valid images
    processed_files = list(processed_dir.glob("*"))
    assert len(processed_files) >= 1
    # Report should exist and have correct structure
    report_path = config.ingestion_report_path
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["pipeline"] == "ingestion"
    assert report["summary"]["total_scanned"] == 3
    assert report["summary"]["valid"] >= 1
    assert report["summary"]["invalid"] >= 1
    assert len(report["records"]) == 3