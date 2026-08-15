"""Load pipeline JSON reports from disk."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pipeline.core.config import PipelineConfig

ReportStage = Literal[
    "ingestion",
    "inference",
    "metadata",
    "qc",
    "export",
]

STAGE_FILENAMES: dict[ReportStage, str] = {
    "ingestion": "ingestion_report.json",
    "inference": "inference_report.json",
    "metadata": "metadata_report.json",
    "qc": "qc_report.json",
    "export": "export_report.json",
}


def resolve_report_path(config: PipelineConfig, stage: ReportStage) -> Path:
    """Return the expected report path for a pipeline stage."""
    if stage == "export":
        return Path(config.export.export_dir) / "export_report.json"
    return config.output_dir / STAGE_FILENAMES[stage]


def load_report(path: Path) -> dict[str, Any] | None:
    """Load one JSON report, or None if missing."""
    path = Path(path)
    if not path.exists() or not path.is_file():
        return None
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Report is not a JSON object: {path}")
    return data


def get_report_payload(
    config: PipelineConfig,
    stage: ReportStage,
    *,
    include_records: bool = True,
) -> dict[str, Any]:
    """
    Build API payload for one stage report.

    Always includes existence metadata; records can be omitted for lighter calls.
    """
    path = resolve_report_path(config, stage)
    report = load_report(path)

    if report is None:
        return {
            "stage": stage,
            "exists": False,
            "path": str(path),
            "summary": None,
            "records": [] if include_records else None,
            "report": None,
        }

    summary = report.get("summary")
    records = report.get("records", []) if include_records else None

    return {
        "stage": stage,
        "exists": True,
        "path": str(path),
        "summary": summary,
        "records": records,
        "pipeline": report.get("pipeline"),
        "timestamp": report.get("timestamp"),
        "version": report.get("version"),
    }


def list_report_summaries(config: PipelineConfig) -> list[dict[str, Any]]:
    """Return lightweight summary cards for all stages."""
    cards: list[dict[str, Any]] = []
    for stage in STAGE_FILENAMES:
        payload = get_report_payload(config, stage, include_records=False)
        cards.append(
            {
                "stage": payload["stage"],
                "exists": payload["exists"],
                "path": payload["path"],
                "summary": payload["summary"],
                "timestamp": payload["timestamp"],
            }
        )
    return cards
