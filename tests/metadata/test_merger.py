"""Unit tests for metadata merger."""

from pipeline.metadata.merger import merge_records


def test_merge_complete_record() -> None:
    ingestion = [
        {
            "id": "abc123",
            "original_filename": "a.jpg",
            "source_path": "datasets/sample/a.jpg",
            "processed_path": "datasets/processed/abc123.jpg",
            "extension": ".jpg",
            "width": 64,
            "height": 48,
            "format": "JPEG",
            "file_size_bytes": 100,
            "checksum": "deadbeef",
            "status": "valid",
            "error_message": None,
            "ingested_at": "2026-08-09T00:00:00+00:00",
        }
    ]
    inference = [
        {
            "image_id": "abc123",
            "image_path": "datasets/processed/abc123.jpg",
            "status": "success",
            "caption": "A red square.",
            "tags": ["red", "square"],
            "objects": ["square"],
            "backend": "mock",
            "error_message": None,
            "inferred_at": "2026-08-09T00:01:00+00:00",
        }
    ]

    records = merge_records(ingestion, inference)

    assert len(records) == 1
    record = records[0]
    assert record.status == "complete"
    assert record.caption == "A red square."
    assert record.scene == "red"
    assert record.tags == ["red", "square"]
    assert record.inference_backend == "mock"


def test_merge_failed_without_processed() -> None:
    ingestion = [
        {
            "id": "unknown",
            "original_filename": "empty.jpg",
            "source_path": "datasets/sample/empty.jpg",
            "processed_path": None,
            "extension": ".jpg",
            "width": None,
            "height": None,
            "format": None,
            "file_size_bytes": 0,
            "checksum": "",
            "status": "invalid",
            "error_message": "Empty file",
            "ingested_at": "2026-08-09T00:00:00+00:00",
        }
    ]

    records = merge_records(ingestion, [])

    assert len(records) == 1
    assert records[0].status == "failed"
    assert records[0].caption is None


def test_merge_ingestion_only() -> None:
    ingestion = [
        {
            "id": "only1",
            "original_filename": "b.jpg",
            "source_path": "datasets/sample/b.jpg",
            "processed_path": "datasets/processed/only1.jpg",
            "extension": ".jpg",
            "width": 10,
            "height": 10,
            "format": "JPEG",
            "file_size_bytes": 50,
            "checksum": "abc",
            "status": "valid",
            "error_message": None,
            "ingested_at": "2026-08-09T00:00:00+00:00",
        }
    ]

    records = merge_records(ingestion, [])

    assert records[0].status == "ingestion_only"
    assert records[0].inference_status is None