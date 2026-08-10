# Sprint 4 Architecture — Quality Control

## Goal

Mark images as `pass` / `warn` / `reject` using corrupt, blur, and
duplicate checks. Export `outputs/qc_report.json`. Do not delete files
by default (mark-only).

## Module Dependency Graph

```mermaid
graph TD
    main[main.py]

    config[core/config.py]
    logger[core/logger.py]
    exceptions[core/exceptions.py]

    qc_stage[qc/stage.py]
    collector[qc/collector.py]
    corrupt[qc/corrupt.py]
    blur[qc/blur.py]
    duplicate[qc/duplicate.py]
    scorer[qc/scorer.py]
    reporter[qc/reporter.py]
    qc_record[models/qc_record.py]

    metadata_report[outputs/metadata_report.json]
    processed[datasets/processed]
    qc_report[outputs/qc_report.json]

    main --> config
    main --> logger
    main --> qc_stage

    qc_stage --> collector
    qc_stage --> duplicate
    qc_stage --> scorer
    qc_stage --> reporter
    scorer --> corrupt
    scorer --> blur
    scorer --> qc_record
    reporter --> qc_record
    collector --> metadata_report
    collector --> processed
    reporter --> qc_report
    collector --> exceptions
    blur --> exceptions
```

## Data Flow

```mermaid
flowchart LR
    A[metadata_report or processed/] --> B[Collector]
    B --> C[find_duplicates]
    B --> D[per-image corrupt + blur]
    C --> E[Scorer / QCRecord]
    D --> E
    E --> F[QC Reporter]
    F --> G[qc_report.json]
```

## Collection Strategy

1. If `metadata_report.json` exists, collect targets from it
   (`id` + `processed_path` + optional `checksum`).
2. Otherwise fall back to scanning `datasets/processed`
   (`image_id` = filename stem).

## Status Rules

| quality_status | When |
|----------------|------|
| reject | `is_corrupt` |
| warn | blurry and/or duplicate (not corrupt) |
| pass | none of the above |

Corrupt wins over blur/duplicate.

## Duplicate Strategy

- Group by SHA256 checksum (from metadata or computed on disk).
- Keep the first image id in each group; mark later ids as duplicates
  of the kept id (`duplicate_of`).
- Exact byte match only in this sprint (no perceptual hash yet).

## Blur Metric

- OpenCV Laplacian variance on grayscale decode.
- Higher score usually means sharper.
- `is_blurry` when `score < blur_threshold`.

## Config

```yaml
qc:
  blur_threshold: 100.0
```

CLI override:

```bash
python main.py qc --blur-threshold 50
```

Priority: CLI > YAML > dataclass default.

## CLI

```bash
python main.py qc
python main.py qc --processed datasets/processed --blur-threshold 100
python main.py qc --metadata-report outputs/metadata_report.json
```
