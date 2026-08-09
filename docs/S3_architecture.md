# Sprint 3 Architecture — Metadata Generation

## Goal

Merge Sprint 1 ingestion fields and Sprint 2 inference fields into one
metadata record per image, then export `outputs/metadata_report.json`.

## Module Dependency Graph

```mermaid
graph TD
    main[main.py]

    config[core/config.py]
    logger[core/logger.py]
    exceptions[core/exceptions.py]

    metadata_stage[metadata/stage.py]
    merger[metadata/merger.py]
    reporter[metadata/reporter.py]
    metadata_record[models/metadata_record.py]

    ingestion_report[outputs/ingestion_report.json]
    inference_report[outputs/inference_report.json]
    metadata_report[outputs/metadata_report.json]

    main --> config
    main --> logger
    main --> metadata_stage

    metadata_stage --> merger
    metadata_stage --> reporter
    merger --> metadata_record
    merger --> exceptions
    reporter --> metadata_record

    merger --> ingestion_report
    merger --> inference_report
    reporter --> metadata_report
```

## Data Flow

```mermaid
flowchart LR
    A[ingestion_report.json] --> C[Merger]
    B[inference_report.json] --> C
    C --> D[list of MetadataRecord]
    D --> E[Metadata Reporter]
    E --> F[metadata_report.json]
```

## Status Rules

| status | Meaning |
|--------|---------|
| complete | Has processed image + inference success |
| partial | Has processed image + inference failed/skipped |
| ingestion_only | Has processed image + no inference row |
| failed | No usable processed_path |

## Scene Field

Sprint 3 uses a lightweight placeholder:

- `scene = first tag` when tags exist
- otherwise `null`

No extra VLM call is made in this sprint.

## CLI

```bash
python main.py metadata
python main.py metadata --ingestion-report outputs/ingestion_report.json --inference-report outputs/inference_report.json
```
