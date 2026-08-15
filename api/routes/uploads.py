"""Accept raw images or zip archives into datasets/raw."""

import shutil
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from api.deps import REPO_ROOT, get_config
from pipeline.core.config import DEFAULT_SUPPORTED_EXTENSIONS

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB per file, 50*1024*1024 = 50MB
ZIP_EXTENSIONS = {".zip"}


def _raw_dir() -> Path:
    path = get_config().raw_dir
    if not path.is_absolute():
        path = REPO_ROOT / path
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def _safe_filename(name: str) -> str:
    """Keep only the basename; reject empty / traversal names."""
    cleaned = Path(name).name.strip()
    if not cleaned or cleaned in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid filename")
    return cleaned


def _is_image_name(name: str) -> bool:
    return Path(name).suffix.lower() in DEFAULT_SUPPORTED_EXTENSIONS


def _is_zip_name(name: str) -> bool:
    return Path(name).suffix.lower() in ZIP_EXTENSIONS


def _extract_zip(zip_path: Path, dest_dir: Path) -> list[str]:
    """
    Extract image files from zip into dest_dir.

    Zip-slip: skip entries that would write outside dest_dir.
    """
    extracted: list[str] = []
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            if info.is_dir():  # skip directories
                continue
            inner_name = Path(info.filename).name # .name is the basename of the file
            if not _is_image_name(inner_name):
                continue
            target = (dest_dir / inner_name).resolve()
            try:
                target.relative_to(dest_dir)
            except ValueError:
                continue
            with archive.open(info) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            extracted.append(inner_name)
    return extracted # return the list of image files that were extracted from the zip


@router.get("")  # list the available files in the raw directory
def list_uploads() -> dict:
    """List files currently in datasets/raw."""
    raw_dir = _raw_dir()
    files: list[dict] = []
    for path in sorted(raw_dir.iterdir()):
        if not path.is_file() or path.name.startswith("."): # skip directories and hidden files
            continue
        files.append(
            {
                "filename": path.name,
                "size_bytes": path.stat().st_size,
                "is_image": _is_image_name(path.name),
            }
        )
    return {"raw_dir": str(raw_dir), "count": len(files), "files": files}


@router.post("")
async def upload_files(
    files: list[UploadFile] = File(..., description="Images and/or .zip"), # ... means required
) -> dict:
    """
    Save uploaded images into datasets/raw.

    .zip is unpacked; only image entries are kept. The zip itself is not kept.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    raw_dir = _raw_dir()
    saved_images: list[str] = []
    skipped: list[str] = []
    from_zips: list[str] = []

    for upload in files:
        original = _safe_filename(upload.filename or "unnamed")
        data = await upload.read()
        if len(data) > MAX_UPLOAD_BYTES:
            skipped.append(original)
            continue

        if _is_zip_name(original):
            tmp_zip = raw_dir / f".tmp_{original}" # create a temporary file in the raw directory
            tmp_zip.write_bytes(data) # write the data to the temporary file
            try:
                extracted = _extract_zip(tmp_zip, raw_dir) # extract the images from tmp_zip file to the raw directory
                from_zips.extend(extracted)
                saved_images.extend(extracted)
            finally:
                tmp_zip.unlink(missing_ok=True) # unlink means delete the file, missing_ok=True means don't raise an error if the file doesn't exist
            continue

        if not _is_image_name(original):
            skipped.append(original)
            continue

        dest = raw_dir / original # zip file is not saved, only the images are saved
        dest.write_bytes(data) # write the data to the destination file, save the image to the raw directory
        saved_images.append(original) # add the image to the saved images list

    return {  # Return a status summary
        "raw_dir": str(raw_dir),
        "saved": saved_images,
        "from_zips": from_zips,
        "skipped": skipped,
        "saved_count": len(saved_images),
    }