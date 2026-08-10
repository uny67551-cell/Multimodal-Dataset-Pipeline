"""Score per-image QC findings into a final quality status."""

from pathlib import Path

from pipeline.models.qc_record import QCRecord, QualityStatus
from pipeline.qc.blur import is_blurry_image
from pipeline.qc.corrupt import is_corrupt_image


def decide_quality_status(
    *,
    is_corrupt: bool,
    is_blurry: bool,
    is_duplicate: bool,
) -> QualityStatus:
    """Decide pass / warn / reject from boolean flags."""
    if is_corrupt:
        return "reject"
    if is_blurry or is_duplicate:
        return "warn"
    return "pass"


def build_qc_record(
    *,
    image_id: str,
    image_path: Path,
    blur_threshold: float,
    duplicate_of: str | None = None,
) -> QCRecord:
    """Run corrupt/blur checks and build one QCRecord."""
    checked_at = QCRecord.utc_now()
    image_path = Path(image_path)

    is_corrupt, corrupt_error = is_corrupt_image(image_path) # False, None
    is_blurry = False
    blur_score: float | None = None
    error_message = corrupt_error

    if not is_corrupt:
        try:
            is_blurry, blur_score = is_blurry_image(
                image_path,
                threshold=blur_threshold,
            )
        except Exception as exc:
            # Treat unexpected blur failures as corrupt/reject-level issues.
            is_corrupt = True
            error_message = f"Blur check failed: {exc}"

    is_duplicate = duplicate_of is not None # True while it owns value, False while it is empty
    quality_status = decide_quality_status(
        is_corrupt=is_corrupt,
        is_blurry=is_blurry,
        is_duplicate=is_duplicate,
    )

    return QCRecord(
        image_id=image_id,
        image_path=image_path,
        checked_at=checked_at,
        is_corrupt=is_corrupt,
        blur_score=blur_score,
        is_blurry=is_blurry,
        is_duplicate=is_duplicate,
        duplicate_of=duplicate_of,
        quality_status=quality_status,
        error_message=error_message,
    )