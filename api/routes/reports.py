"""Read-only report endpoints."""

import json
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, HTTPException

from api.deps import REPO_ROOT, get_config

router = APIRouter(prefix="/api/reports", tags=["reports"]) # APIRouter -> creates a router for the reports API
                                                            # Interface address for the reports API

StageName = Literal["ingestion", "inference", "metadata", "qc", "export"]


def _report_path_for(stage: StageName) -> Path: # pull the report path for a given stage
    config = get_config()
    mapping: dict[str, Path] = { # mapping = {}
        "ingestion": config.ingestion_report_path,
        "inference": config.inference_report_path,
        "metadata": config.metadata_report_path,
        "qc": config.qc_report_path,
        "export": Path(config.export.export_dir) / "export_report.json",
    }
    path = mapping[stage]
    # Resolve relative paths against repo root (API may start from any cwd)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _load_report(stage: StageName) -> dict[str, Any]: # load the report for a given stage
    path = _report_path_for(stage)
    if not path.exists():
        raise HTTPException( # raise an HTTP exception if the report is not found, similar to manual exceptions.py file
            status_code=404,
            detail=f"Report not found for stage '{stage}': {path}",
        )
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@router.get("")
def list_report_summaries() -> dict[str, Any]: # list the report summaries for each stage, in order to check if the report is available or not
    """
    Return availability + summary for each known stage.

    Missing reports appear as available=false (not an error).
    """
    stages: list[StageName] = [
        "ingestion",
        "inference",
        "metadata",
        "qc",
        "export",
    ]
    items: list[dict[str, Any]] = []
    for stage in stages:
        path = _report_path_for(stage)
        if not path.exists():
            items.append(
                {
                    "stage": stage,
                    "available": False,
                    "path": str(path),
                    "summary": None,
                }
            )
            continue
        data = _load_report(stage)
        items.append(
            {
                "stage": stage,
                "available": True,
                "path": str(path),
                "pipeline": data.get("pipeline"),
                "timestamp": data.get("timestamp"),
                "summary": data.get("summary"),
            }
        )
    return {"reports": items}


@router.get("/{stage}")
def get_report( # get the report for a specific given stage, can include the records or not
    stage: StageName,
    include_records: bool = True,
) -> dict[str, Any]:
    """
    Return one stage report.

    Query:
      include_records=false  → omit heavy records list (summary only)
    """
    data = _load_report(stage)
    if not include_records:
        data = {k: v for k, v in data.items() if k != "records"} # return the data in .json file except for the records
    return {
        "stage": stage,
        "path": str(_report_path_for(stage)),
        "report": data,
    }
