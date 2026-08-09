"""Integration-style tests for mock inference stage."""

import json
from pathlib import Path

from PIL import Image

from pipeline.core.config import PipelineConfig, InferenceConfig, LoggingConfig
from pipeline.inference.factory import create_backend
from pipeline.inference.mock_vlm import MockVLM
from pipeline.inference.stage import InferenceStage


def test_mock_vlm_infer(tmp_path: Path) -> None:
    image_path = tmp_path / "demo.jpg"
    Image.new("RGB", (20, 20), color=(255, 255, 0)).save(image_path, format="JPEG")

    record = MockVLM().infer(image_path=image_path, image_id="demo")

    assert record.status == "success"
    assert record.backend == "mock"
    assert record.caption is not None
    assert "demo" in record.tags


def test_inference_stage_with_mock(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    Image.new("RGB", (24, 24), color=(10, 20, 30)).save(
        processed / "id001.jpg",
        format="JPEG",
    )

    output_dir = tmp_path / "outputs"
    config = PipelineConfig(
        processed_dir=processed,
        output_dir=output_dir,
        inference=InferenceConfig(backend="mock"),
        logging=LoggingConfig(level="WARNING", log_file=None),
    )

    stage = InferenceStage(config=config, backend=create_backend(config.inference))
    records = stage.run(processed_dir=processed, report_path=tmp_path / "missing.json")

    assert len(records) == 1
    assert records[0].status == "success"

    report_path = config.inference_report_path
    assert report_path.exists()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["pipeline"] == "inference"
    assert data["backend"] == "mock"
    assert data["summary"]["success"] == 1