# Architecture

## Module Dependency Graph

Who imports whom in Sprint 1:

```mermaid
graph TD
    main[main.py]

    config[core/config.py]
    logger[core/logger.py]
    stage_base[core/stage.py]
    exceptions[core/exceptions.py]

    ingestion_stage[ingestion/stage.py]
    scanner[ingestion/scanner.py]
    validator[ingestion/validator.py]
    organizer[ingestion/organizer.py]
    reporter[ingestion/reporter.py]

    image_record[models/image_record.py]
    yaml[configs/default.yaml]

    main --> config
    main --> logger
    main --> ingestion_stage
    main --> yaml

    ingestion_stage --> stage_base
    ingestion_stage --> config
    ingestion_stage --> scanner
    ingestion_stage --> validator
    ingestion_stage --> organizer
    ingestion_stage --> reporter

    scanner --> exceptions
    validator --> image_record
    organizer --> image_record
    reporter --> image_record
    stage_base --> image_record
```

## Data Flow

How one ingestion run moves data:

```mermaid
flowchart LR
    A[datasets/raw or sample] --> B[Scanner]
    B --> C[list of Path]
    C --> D[Validator]
    D --> E[list of ImageRecord]
    E --> F[Organizer]
    F --> G[datasets/processed]
    E --> H[Reporter]
    F --> H
    H --> I[outputs/ingestion_report.json]
    main[main.py] --> J[setup_logger]
    J --> K[outputs/logs/ingestion.log]
```

## File Responsibilities

| File | Responsibility |
|------|----------------|
| `main.py` | CLI parsing, load config, setup logger, start stage |
| `core/config.py` | Load YAML into typed dataclasses |
| `core/logger.py` | Configure terminal + file logging |
| `core/stage.py` | Abstract stage interface |
| `core/exceptions.py` | Pipeline-specific errors |
| `models/image_record.py` | Shared image record model |
| `ingestion/scanner.py` | Find candidate image paths |
| `ingestion/validator.py` | Validate images and build records |
| `ingestion/organizer.py` | Copy/move to processed with stable IDs |
| `ingestion/reporter.py` | Build and export JSON report |
| `ingestion/stage.py` | Orchestrate the full ingestion pipeline |

## Design Notes

- Stages receive a `PipelineConfig` object; they do not load YAML themselves.
- Single-image failures become `status="invalid"` and do not crash the batch.
- Repeated ingestion of the same destination file becomes `status="skipped"`.
- Downstream modules should treat records with a non-null `processed_path` as usable.
