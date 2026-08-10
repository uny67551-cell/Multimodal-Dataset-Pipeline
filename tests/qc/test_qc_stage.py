"""Integration-style tests for QCStage."""

import json
from pathlib import Path

from PIL import Image

from pipeline.core.config import LoggingConfig, PipelineConfig, QCConfig
from pipeline.qc.stage import QCStage


def test_qc_stage_end_to_end(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()

    good = processed / "good.jpg"
    Image.new("RGB", (48, 48), color=(0, 128, 255)).save(good, format="JPEG")

    dup = processed / "dup.jpg"
    dup.write_bytes(good.read_bytes())

    empty = processed / "empty.jpg"
    empty.write_bytes(b"")

    # Prefer scanning processed/ (no metadata report needed).
    config = PipelineConfig(
        processed_dir=processed,
        output_dir=output_dir,
        qc=QCConfig(blur_threshold=100.0),
        logging=LoggingConfig(level="WARNING", log_file=None),
    )
    stage = QCStage(config)
    records = stage.run() 

    by_id = {r.image_id: r for r in records}

    # image_id 来自文件 stem
    assert by_id["empty"].quality_status == "reject"
    assert by_id["empty"].is_corrupt is True

    # 两者有且仅有一个 is_duplicate
    assert by_id["good"].is_duplicate != by_id["dup"].is_duplicate
    if by_id["dup"].is_duplicate:
        assert by_id["dup"].duplicate_of == "good"
    else:
        assert by_id["good"].duplicate_of == "dup"

    report_path = config.qc_report_path
    assert report_path.exists()
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["pipeline"] == "qc"
    assert data["blur_threshold"] == 100.0
    assert data["summary"]["total"] == 3
    assert data["summary"]["reject"] >= 1
    assert data["summary"]["duplicate"] >= 1


def test_qc_stage_uses_config_blur_threshold(tmp_path: Path) -> None:
    processed = tmp_path / "processed"
    processed.mkdir()
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()

    img = processed / "x.jpg"
    Image.new("RGB", (32, 32), color=(50, 50, 50)).save(img, format="JPEG")

    config = PipelineConfig(
        processed_dir=processed,
        output_dir=output_dir,
        qc=QCConfig(blur_threshold=999999.0),  # force almost everything blurry
        logging=LoggingConfig(level="WARNING", log_file=None),
    )
    stage = QCStage(config)  # do NOT pass blur_threshold=100
    records = stage.run(metadata_report_path=tmp_path / "nope.json")

    assert stage.blur_threshold == 999999.0
    assert records[0].is_blurry is True

    data = json.loads(config.qc_report_path.read_text(encoding="utf-8"))
    assert data["blur_threshold"] == 999999.0