"""Write LLaVA-style conversation JSONL for VLM fine-tuning."""

import json
from pathlib import Path
from typing import Any

from loguru import logger

from pipeline.export.filter import iter_included
from pipeline.models.export_record import ExportRecord

DEFAULT_HUMAN_PROMPT = "<image>\nDescribe this image in detail."


def _serialize_llava(record: ExportRecord) -> dict[str, Any]:
    """One LLaVA conversation row."""
    caption = (record.caption or "").strip() or "No caption available."
    return {
        "id": record.id,
        "image": record.export_image_relpath,
        "conversations": [
            {"from": "human", "value": DEFAULT_HUMAN_PROMPT},
            {"from": "gpt", "value": caption},
        ],
    }


def write_llava_jsonl(
    records: list[ExportRecord],
    output_path: Path,
    *,
    included_only: bool = True,
) -> Path:
    """Write llava.jsonl for included (or all) records."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = iter_included(records) if included_only else records
    with output_path.open("w", encoding="utf-8") as file:
        for record in rows:
            line = json.dumps(_serialize_llava(record), ensure_ascii=False)
            file.write(line + "\n")

    logger.info("Wrote {} LLaVA rows to {}", len(rows), output_path)
    return output_path