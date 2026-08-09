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

### Outputs

- Processed images: `datasets/processed/{id}.{ext}`
- Ingestion report: `outputs/ingestion_report.json`
- Inference report: `outputs/inference_report.json`
- Metadata report: `outputs/metadata_report.json`
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
├── outputs/                  # Reports and logs
├── pipeline/
│   ├── core/                 # Config, logger, exceptions
│   ├── ingestion/            # Scanner / Validator / Organizer / Reporter
│   ├── inference/            # VLM backends + InferenceStage
│   ├── metadata/             # Merge reports into unified metadata
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
- [ ] Quality Control
- [ ] Dataset Export
- [ ] Web UI

## Architecture

- Sprint 1 (Ingestion): [docs/S1_architecture.md](docs/S1_architecture.md)
- Sprint 2 (Inference): [docs/S2_architecture.md](docs/S2_architecture.md)
- Sprint 3 (Metadata): [docs/S3_architecture.md](docs/S3_architecture.md)
