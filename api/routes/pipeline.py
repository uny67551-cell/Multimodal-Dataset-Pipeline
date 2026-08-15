"""Trigger existing pipeline stages over HTTP."""

from dataclasses import replace
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from api.deps import get_config
from pipeline.core.exceptions import PipelineError
from pipeline.export.filter import iter_included
from pipeline.export.stage import ExportStage
from pipeline.inference.factory import create_backend
from pipeline.inference.stage import InferenceStage
from pipeline.ingestion.stage import IngestionStage
from pipeline.metadata.stage import MetadataStage
from pipeline.qc.stage import QCStage

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

StageName = Literal["ingest", "infer", "metadata", "qc", "export"]


class InferOptions(BaseModel):
    backend: Literal["mock", "local", "api"] = Field(
        default="mock",  # default value is mock, it will be shown in the UI as the default value
        description="VLM backend. Use mock for tests; api calls DashScope.",
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"backend": "mock"},
        }
    )


class ExportOptions(BaseModel):
    include_blurry: bool | None = Field(
        default=None,  
        description="Allow blurry images. null = use YAML default.",
    )
    exclude_duplicates: bool | None = Field(
        default=None,
        description="Drop duplicate copies. null = use YAML default.",
    )
    require_caption: bool | None = Field(
        default=None,
        description="Require a non-empty caption. null = use YAML default.",
    )
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "include_blurry": False,
                "exclude_duplicates": True,
                "require_caption": True,
            }
        }
    )

def _copy_config():  # copy the config to avoid mutating the original config
    """Do not mutate the cached config singleton."""
    return replace(get_config())  # return a copy of the config


@router.get("/stages")
def list_stages() -> dict[str, Any]:
    return {
        "stages": [
            {"name": "ingest", "method": "POST", "path": "/api/pipeline/ingest"}, # name of the stage, method of the request, path of the request， they are titles
            {"name": "infer", "method": "POST", "path": "/api/pipeline/infer"},
            {"name": "metadata", "method": "POST", "path": "/api/pipeline/metadata"},
            {"name": "qc", "method": "POST", "path": "/api/pipeline/qc"},
            {"name": "export", "method": "POST", "path": "/api/pipeline/export"},
        ]
    }


@router.post("/ingest")
def run_ingest() -> dict[str, Any]:
    config = _copy_config()
    try:
        records = IngestionStage(config).run(input_dir=config.raw_dir)
    except (PipelineError, FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "stage": "ingest",
        "count": len(records),
        "report": str(config.ingestion_report_path),
    }


@router.post("/infer")
def run_infer(options: InferOptions = InferOptions()) -> dict[str, Any]:
    config = _copy_config()
    config = replace(
        config,
        inference=replace(config.inference, backend=options.backend),
    )
    try:
        backend = create_backend(config.inference)
        records = InferenceStage(config=config, backend=backend).run()
    except (PipelineError, FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "stage": "infer",
        "backend": backend.name,
        "count": len(records),
        "report": str(config.inference_report_path),
    }


@router.post("/metadata")
def run_metadata() -> dict[str, Any]:
    config = _copy_config()
    try:
        records = MetadataStage(config).run()
    except (PipelineError, FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "stage": "metadata",
        "count": len(records),
        "report": str(config.metadata_report_path),
    }


@router.post("/qc")
def run_qc() -> dict[str, Any]:
    config = _copy_config()
    try:
        records = QCStage(config).run()
    except (PipelineError, FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "stage": "qc",
        "count": len(records),
        "report": str(config.qc_report_path),
    }


@router.post("/export")
def run_export(options: ExportOptions = ExportOptions()) -> dict[str, Any]:
    config = _copy_config()
    export_cfg = config.export
    if options.include_blurry is not None:
        export_cfg = replace(export_cfg, include_blurry=options.include_blurry)
    if options.exclude_duplicates is not None:
        export_cfg = replace(export_cfg, exclude_duplicates=options.exclude_duplicates)
    if options.require_caption is not None:
        export_cfg = replace(export_cfg, require_caption=options.require_caption)
    config = replace(config, export=export_cfg)

    try:
        stage = ExportStage(config)
        records = stage.run()
    except (PipelineError, FileNotFoundError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    included = iter_included(records)
    return {
        "stage": "export",
        "count": len(records),
        "included": len(included),
        "export_dir": str(stage.export_dir),
        "report": str(stage.report_path),
    }