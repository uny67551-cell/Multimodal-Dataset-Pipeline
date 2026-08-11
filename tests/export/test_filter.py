"""Unit tests for export filters."""

from pathlib import Path

from PIL import Image

from pipeline.export.filter import apply_export_filters
from pipeline.models.export_record import ExportRecord


def _record(
    tmp_path: Path,
    *,
    image_id: str = "a",
    caption: str | None = "hello",
    is_duplicate: bool = False,
    is_blurry: bool = False,
    is_corrupt: bool = False,
    metadata_status: str = "complete",
) -> ExportRecord:
    path = tmp_path / f"{image_id}.jpg"
    if not is_corrupt:
        Image.new("RGB", (16, 16), color=(1, 2, 3)).save(path, format="JPEG") # create a 16x16 RGB image with color (1, 2, 3) and save it as JPEG
    else:
        path.write_bytes(b"")
    return ExportRecord(
        id=image_id,
        status="included",
        generated_at=ExportRecord.utc_now(),
        source_image_path=path,
        export_image_relpath=f"images/{image_id}.jpg",
        caption=caption,
        metadata_status=metadata_status,
        is_corrupt=is_corrupt,
        is_blurry=is_blurry,
        is_duplicate=is_duplicate,
        quality_status="reject" if is_corrupt else ("warn" if is_blurry or is_duplicate else "pass"),
    )


def test_filter_excludes_duplicate_and_blurry_by_default(tmp_path: Path) -> None:
    records = [
        _record(tmp_path, image_id="ok"),
        _record(tmp_path, image_id="dup", is_duplicate=True),
        _record(tmp_path, image_id="blur", is_blurry=True),
    ]
    apply_export_filters(
        records,
        exclude_duplicates=True,
        include_blurry=False,
        require_caption=True,
    )
    by_id = {r.id: r for r in records}
    assert by_id["ok"].status == "included"
    assert by_id["dup"].exclude_reason == "duplicate"
    assert by_id["blur"].exclude_reason == "blurry"


def test_filter_can_include_blurry_and_require_caption(tmp_path: Path) -> None:
    records = [
        _record(tmp_path, image_id="blur", is_blurry=True, caption="x"),
        _record(tmp_path, image_id="nocap", caption=None),
    ]
    apply_export_filters(
        records,
        exclude_duplicates=True,
        include_blurry=True,
        require_caption=True,
    )
    by_id = {r.id: r for r in records}
    assert by_id["blur"].status == "included"
    assert by_id["nocap"].exclude_reason == "missing_caption"