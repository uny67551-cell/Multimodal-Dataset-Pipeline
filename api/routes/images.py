"""Image file and gallery endpoints."""

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse  # FileResponse is a response class that returns a file based on HTTP response

from api.deps import REPO_ROOT, get_config
from api.routes.reports import _load_report
from pipeline.core.config import DEFAULT_SUPPORTED_EXTENSIONS

router = APIRouter(prefix="/api", tags=["images"])


def _resolve_repo_path(path: Path) -> Path:
    """Turn a config-relative path into an absolute path under the repo."""
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def _processed_dir() -> Path:
    return _resolve_repo_path(get_config().processed_dir)


def _find_processed_image(image_id: str) -> Path:
    """
    Locate one processed image by id (filename stem).

    Reject path-traversal ids such as '../secret'.
    """
    if not image_id or image_id in {".", ".."} or "/" in image_id or "\\" in image_id: # if the image_id is not valid (contains "." or "..", or contains "/" or "\"), raise an HTTP exception
        raise HTTPException(status_code=400, detail="Invalid image_id")

    processed_dir = _processed_dir()
    if not processed_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Processed dir not found: {processed_dir}")

    for ext in DEFAULT_SUPPORTED_EXTENSIONS:  # scan for the image in the processed directory with the default supported extensions
        candidate = (processed_dir / f"{image_id}{ext}").resolve()
        try:
            candidate.relative_to(processed_dir) # relative_to comes form Pathlib.Path class, it is used to compute the relative path between two paths
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid image path")
        if candidate.is_file(): 
            return candidate

    raise HTTPException(status_code=404, detail=f"Image not found: {image_id}")


def _safe_load_report(stage: str) -> dict[str, Any] | None:
    try:
        return _load_report(stage)  # type: ignore[arg-type]
    except HTTPException:
        return None


def _index_qc(qc_report: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not qc_report:
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for row in qc_report.get("records", []): # if not exists, return an empty list []
        image_id = row.get("image_id") # {{}}
        if image_id:
            indexed[str(image_id)] = row   # {image_id: record{key: value}}
    return indexed


@router.get("/gallery")
def list_gallery() -> dict[str, Any]:
    """
    Join metadata + QC into gallery cards.

    Falls back to scanning processed/ when metadata report is missing.
    """
    metadata = _safe_load_report("metadata")
    qc_index = _index_qc(_safe_load_report("qc"))
    items: list[dict[str, Any]] = []

    if metadata:
        for row in metadata.get("records", []):
            image_id = row.get("id")
            if not image_id or image_id == "unknown":
                continue
            qc = qc_index.get(str(image_id), {})
            processed = row.get("processed_path")
            exists = bool(processed and _resolve_repo_path(Path(processed)).is_file())
            items.append(
                {
                    "id": str(image_id),
                    "image_url": f"/api/images/{image_id}",
                    "exists": exists,
                    "caption": row.get("caption"),
                    "tags": row.get("tags") or [],
                    "objects": row.get("objects") or [],
                    "scene": row.get("scene"),
                    "metadata_status": row.get("status"),
                    "quality_status": qc.get("quality_status"),
                    "is_blurry": qc.get("is_blurry"),
                    "is_duplicate": qc.get("is_duplicate"),
                    "is_corrupt": qc.get("is_corrupt"),
                    "duplicate_of": qc.get("duplicate_of"),
                    "blur_score": qc.get("blur_score"),
                }
            )
    else:
        processed_dir = _processed_dir() # path
        if processed_dir.is_dir():
            for path in sorted(processed_dir.iterdir()):
                if not path.is_file() or path.suffix.lower() not in DEFAULT_SUPPORTED_EXTENSIONS:
                    continue
                image_id = path.stem # stem is a property that comes form Pathlib.Path class, it is used to get the filename without the extension
                qc = qc_index.get(image_id, {})
                items.append(
                    {
                        "id": image_id,
                        "image_url": f"/api/images/{image_id}",
                        "exists": True,
                        "caption": None,
                        "tags": [],
                        "objects": [],
                        "scene": None,
                        "metadata_status": None,
                        "quality_status": qc.get("quality_status"),
                        "is_blurry": qc.get("is_blurry"),
                        "is_duplicate": qc.get("is_duplicate"),
                        "is_corrupt": qc.get("is_corrupt"),
                        "duplicate_of": qc.get("duplicate_of"),
                        "blur_score": qc.get("blur_score"),
                    }
                )

    return {"total": len(items), "items": items}


@router.get("/images/{image_id}")
def get_image(image_id: str) -> FileResponse:
    """Return the processed image bytes for <img src=... />."""
    path = _find_processed_image(image_id)
    return FileResponse(path)