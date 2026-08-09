"""Integration-style tests for MetadataStage."""

import json
from pathlib import Path

from pipeline.core.config import PipelineConfig, LoggingConfig
from pipeline.metadata.stage import MetadataStage


def test_metadata_stage_end_to_end(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()

    ingestion_report = output_dir / "ingestion_report.json"
    inference_report = output_dir / "inference_report.json"

    ingestion_report.write_text(
        json.dumps(
            {
                "pipeline": "ingestion",
                "records": [
                    {
                        "id": "id001",
                        "original_filename": "x.jpg",
                        "source_path": "sample/x.jpg",
                        "processed_path": "processed/id001.jpg",
                        "extension": ".jpg",
                        "width": 32,
                        "height": 32,
                        "format": "JPEG",
                        "file_size_bytes": 80,
                        "checksum": "cafebabe",
                        "status": "valid",
                        "error_message": None,
                        "ingested_at": "2026-08-09T00:00:00+00:00",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    inference_report.write_text(
        json.dumps(
            {
                "pipeline": "inference",
                "records": [
                    {
                        "image_id": "id001",
                        "image_path": "processed/id001.jpg",
                        "status": "success",
                        "caption": "A tiny image.",
                        "tags": ["tiny", "test"],
                        "objects": ["patch"],
                        "backend": "mock",
                        "error_message": None,
                        "inferred_at": "2026-08-09T00:01:00+00:00",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config = PipelineConfig(
        output_dir=output_dir,
        logging=LoggingConfig(level="WARNING", log_file=None),
    )
    stage = MetadataStage(config)
    records = stage.run(
        ingestion_report_path=ingestion_report,
        inference_report_path=inference_report,
    )

    assert len(records) == 1
    assert records[0].status == "complete"

    report_path = config.metadata_report_path
    assert report_path.exists()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["pipeline"] == "metadata"
    assert data["summary"]["complete"] == 1
    assert data["records"][0]["caption"] == "A tiny image."