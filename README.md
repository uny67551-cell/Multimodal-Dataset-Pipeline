# Multimodal Dataset Pipeline

An enterprise-style pipeline for multimodal dataset construction and quality control.

## Vision

Modern Vision-Language Models rely on high-quality datasets. Real-world image folders often have inconsistent naming, corrupted files, missing metadata, and messy structure.

This project builds a reusable pipeline that turns raw media folders into training-ready datasets with metadata, captions, and quality reports.

## Current Status

Sprint 1 completed: **Image Ingestion**

- Scan image directories
- Validate readable images
- Organize files with stable IDs
- Export JSON ingestion report
- CLI entry point with logging



## Installation

```bash
pip install -r requirements.txt
```



## Usage



### Run image ingestion

```bash
python main.py ingest -i datasets/sample -o datasets/processed
```

Optional flags:

```bash
python main.py ingest -i datasets/sample -o datasets/processed --log-level DEBUG
python main.py ingest -c configs/default.yaml -i datasets/sample
python main.py ingest -i datasets/sample --move
```



### Outputs

- Processed images: `datasets/processed/{id}.{ext}`
- Report: `outputs/ingestion_report.json`
- Log file: `outputs/logs/ingestion.log`



## Project Structure

```text
Multimodal-Dataset-Pipeline/
├── configs/                  # YAML configuration
├── datasets/
│   ├── raw/                  # Original input images
│   ├── processed/            # Normalized images
│   └── sample/               # Small local test images
├── docs/                     # Architecture notes
├── outputs/                  # Reports and logs
├── pipeline/
│   ├── core/                 # Config, logger, base stage, exceptions
│   ├── ingestion/            # Scanner / Validator / Organizer / Reporter
│   └── models/               # Shared data models
├── tests/                    # Unit and integration tests
├── tools/                    # Helper scripts
├── main.py                   # CLI entry point
└── requirements.txt
```



## Testing

```bash
python -m pytest tests/ingestion/ -v
```


## Roadmap

- [x] Image Ingestion
- [ ] VLM Inference
- [ ] Metadata Generation
- [ ] Quality Control
- [ ] Dataset Export
- [ ] Web UI



## Architecture

See [docs/architecture.md](docs/architecture.md) for module dependency and data-flow diagrams.