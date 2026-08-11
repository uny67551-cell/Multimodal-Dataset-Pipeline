# Multimodal Dataset Pipeline

An enterprise-style pipeline for multimodal dataset construction and quality control.

## Vision

Modern Vision-Language Models rely on high-quality datasets. Real-world image folders often have inconsistent naming, corrupted files, missing metadata, and messy structure.

This project builds a reusable pipeline that turns raw media folders into training-ready datasets with metadata, captions, and quality reports.

## Current Status

### Sprint 1 completed: Image Ingestion

- Scan image directories
- Validate readable images
- Organize files with stable IDs
- Export JSON ingestion report



### Sprint 2 completed: VLM Inference

- Pluggable backends: `mock` / `local` / `api`
- Collect targets from ingestion report or `datasets/processed`
- Generate caption / tags / objects
- Export JSON inference report



### Sprint 3 completed: Metadata Generation

- Merge ingestion + inference reports by image id
- Build unified MetadataRecord (caption / tags / objects / scene / file info)
- Export JSON metadata report
- CLI: `python main.py metadata`



### Sprint 4 completed: Quality Control

- Collect QC targets from metadata report or `datasets/processed`
- Detect corrupt / blurry / duplicate images
- Score `pass` / `warn` / `reject` (mark only, no delete by default)
- Export JSON QC report
- CLI: `python main.py qc`

### Sprint 5 completed: Dataset Export

- Join metadata + QC into export candidates
- Filter duplicates / blur / missing caption (configurable)
- Copy included images into a self-contained package
- Write `annotations.jsonl` + `llava.jsonl` + `export_report.json`
- CLI: `python main.py export`

## Installation

```bash
pip install -r requirements.txt
```

For local Qwen inference you may also need a HuggingFace mirror on some networks:

```powershell
$env:HF_ENDPOINT="https://hf-mirror.com"
$env:HF_HUB_DISABLE_XET="1"
```



## Usage



### 1) Image ingestion

```bash
python main.py ingest -i datasets/sample -o datasets/processed
```

Optional flags:

```bash
python main.py ingest -i datasets/sample -o datasets/processed --log-level DEBUG
python main.py ingest -c configs/default.yaml -i datasets/sample
python main.py ingest -i datasets/sample --move
```



### 2) VLM inference

Default backend is `mock` (no GPU / no API key):

```bash
python main.py infer
```

Use DashScope API:

```powershell
$env:QWEN_API_KEY="your_key"
python main.py infer --backend api
```

Set API model name in `configs/default.yaml` (example: `qwen-vl-plus`) and keep:

```yaml
api_base: https://dashscope.aliyuncs.com/compatible-mode/v1
```

Use local Qwen2.5-VL (needs GPU / downloaded weights; may be slow on 4GB VRAM):

```powershell
$env:HF_ENDPOINT="https://hf-mirror.com"
$env:HF_HUB_DISABLE_XET="1"
python main.py infer --backend local
```

Notes:

- API `model_name` example: `qwen-vl-plus`
- Local `model_name` example: `Qwen/Qwen2.5-VL-3B-Instruct`
- Do not commit API keys. Use environment variable `QWEN_API_KEY`.
- Truncated JPEGs may pass ingestion checks but fail during full vision decode.



### 3) Metadata generation

After ingestion and inference reports exist:

```bash
python main.py metadata
```

Optional:

```bash
python main.py metadata --ingestion-report outputs/ingestion_report.json --inference-report outputs/inference_report.json
```



### 4) Quality control

After metadata exists (or processed images are available):

```bash
python main.py qc
```

Optional:

```bash
python main.py qc --blur-threshold 50
python main.py qc --processed datasets/processed --metadata-report outputs/metadata_report.json
```

Tune `qc.blur_threshold` in `configs/default.yaml` (CLI overrides YAML).

### 5) Dataset export

After metadata and QC reports exist:

```bash
python main.py export
```

Optional:

```bash
python main.py export --include-blurry
python main.py export --no-require-caption
python main.py export --export-dir outputs/export_demo
```

Default policy (overridable via YAML / CLI):

- exclude duplicates
- exclude blurry images
- require non-empty caption
- always copy included images into the export package

### Outputs

- Processed images: `datasets/processed/{id}.{ext}`
- Ingestion report: `outputs/ingestion_report.json`
- Inference report: `outputs/inference_report.json`
- Metadata report: `outputs/metadata_report.json`
- QC report: `outputs/qc_report.json`
- Export package: `outputs/export/` (`images/`, `annotations.jsonl`, `llava.jsonl`, `export_report.json`)
- Log file: path configured in YAML (default under `outputs/logs/`)

## Project Structure

```text
Multimodal-Dataset-Pipeline/
├── configs/                  # YAML configuration
├── datasets/
│   ├── raw/                  # Original input images
│   ├── processed/            # Normalized images
│   └── sample/               # Small local test images
├── docs/                     # Architecture notes
├── outputs/                  # Reports, logs, and export packages
├── pipeline/
│   ├── core/                 # Config, logger, exceptions
│   ├── ingestion/            # Scanner / Validator / Organizer / Reporter
│   ├── inference/            # VLM backends + InferenceStage
│   ├── metadata/             # Merge reports into unified metadata
│   ├── qc/                   # Corrupt / blur / duplicate / QCStage
│   ├── export/               # Filter / writers / ExportStage
│   └── models/               # Shared data models
├── tests/                    # Unit and integration tests
├── tools/                    # Local helper scripts (gitignored)
├── main.py                   # CLI entry point
└── requirements.txt
```

## Testing

```bash
python -m pytest tests/ -v
```

Tests use temporary directories and the mock backend. They do not call paid APIs or require a GPU.

## Roadmap

- [x] Image Ingestion
- [x] VLM Inference
- [x] Metadata Generation
- [x] Quality Control
- [x] Dataset Export
- [ ] Web UI

## Architecture

- Sprint 1 (Ingestion): [docs/S1_architecture.md](docs/S1_architecture.md)
- Sprint 2 (Inference): [docs/S2_architecture.md](docs/S2_architecture.md)
- Sprint 3 (Metadata): [docs/S3_architecture.md](docs/S3_architecture.md)
- Sprint 4 (QC): [docs/S4_architecture.md](docs/S4_architecture.md)
- Sprint 5 (Export): [docs/S5_architecture.md](docs/S5_architecture.md)

