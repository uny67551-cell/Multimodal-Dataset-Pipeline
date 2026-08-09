# Architecture

## Module Dependency Graph

```mermaid
graph TD
    main[main.py]

    config[core/config.py]
    logger[core/logger.py]
    exceptions[core/exceptions.py]

    ingestion_stage[ingestion/stage.py]
    scanner[ingestion/scanner.py]
    validator[ingestion/validator.py]
    organizer[ingestion/organizer.py]
    ingestion_reporter[ingestion/reporter.py]

    inference_stage[inference/stage.py]
    collector[inference/collector.py]
    factory[inference/factory.py]
    mock[inference/mock_vlm.py]
    local[inference/qwen_local.py]
    api[inference/qwen_api.py]
    prompts[inference/prompts.py]
    parser[inference/parser.py]
    inference_reporter[inference/reporter.py]

    image_record[models/image_record.py]
    inference_record[models/inference_record.py]

    main --> config
    main --> logger
    main --> ingestion_stage
    main --> inference_stage
    main --> factory

    ingestion_stage --> scanner
    ingestion_stage --> validator
    ingestion_stage --> organizer
    ingestion_stage --> ingestion_reporter
    scanner --> exceptions
    validator --> image_record
    organizer --> image_record
    ingestion_reporter --> image_record

    inference_stage --> collector
    inference_stage --> factory
    inference_stage --> inference_reporter
    factory --> mock
    factory --> local
    factory --> api
    local --> prompts
    local --> parser
    api --> prompts
    api --> parser
    inference_reporter --> inference_record
    mock --> inference_record
```

## Data Flow

### Ingestion

```mermaid
flowchart LR
    A[datasets/raw or sample] --> B[Scanner]
    B --> C[Validator]
    C --> D[Organizer]
    D --> E[datasets/processed]
    C --> F[Ingestion Reporter]
    D --> F
    F --> G[outputs/ingestion_report.json]
```

### Inference

```mermaid
flowchart LR
    G[ingestion_report.json] --> H[Collector]
    E[datasets/processed] --> H
    H --> I[VLM Backend]
    I --> J[mock / local / api]
    J --> K[InferenceRecord]
    K --> L[Inference Reporter]
    L --> M[outputs/inference_report.json]
```

## Backend Notes

| Backend | model_name example | Needs |
|---------|--------------------|--------|
| mock | n/a | nothing |
| local | `Qwen/Qwen2.5-VL-3B-Instruct` | GPU + HF weights |
| api | `qwen-vl-plus` | `QWEN_API_KEY` + `api_base` |

CLI overrides YAML for one-off runs, for example:

```bash
python main.py infer --backend mock
python main.py infer --backend api
python main.py infer --backend local
```

Truncated or corrupt JPEGs may pass lightweight ingestion checks but fail during full pixel decode in local/API vision preprocessing.
