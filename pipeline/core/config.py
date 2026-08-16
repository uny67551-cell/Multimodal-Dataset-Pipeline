"""Configuration loading for the pipeline."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml

DEFAULT_SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

@dataclass
class IngestionConfig:
    """Settings for the image ingestion stage."""
    supported_extensions: tuple[str, ...] = DEFAULT_SUPPORTED_EXTENSIONS
    recursive: bool = True
    mode: str = "copy"

@dataclass
class InferenceConfig:
    """Settings for the VLM inference stage."""
    backend: str = "mock"
    model_name: str = "Qwen/Qwen2.5-VL-3B-Instruct"
    load_in_4bit: bool = True
    max_new_tokens: int = 128
    max_pixels: int = 352800
    api_base: str = ""
    api_key_env: str = "VLM_API_KEY"
    api_timeout: int = 120

@dataclass
class QCConfig:
    """Settings for the quality-control stage."""
    blur_threshold: float = 100.0

@dataclass
class ExportConfig:
    """Settings for the dataset export stage."""
    export_dir: Path = Path("outputs/export")
    exclude_duplicates: bool = True
    include_blurry: bool = False
    require_caption: bool = True

@dataclass
class LoggingConfig:
    """Logging settings."""
    level: str = "INFO"
    log_file: Path | None = None

@dataclass
class PipelineConfig:
    """Top-level pipeline configuration."""
    raw_dir: Path = Path("datasets/raw")
    processed_dir: Path = Path("datasets/processed")
    output_dir: Path = Path("outputs")
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    inference: InferenceConfig = field(default_factory=InferenceConfig)
    qc: QCConfig = field(default_factory=QCConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @property
    def ingestion_report_path(self) -> Path:
        """Default path for the ingestion JSON report."""
        return self.output_dir / "ingestion_report.json"


    @property
    def inference_report_path(self) -> Path:
        """Default path for the inference JSON report."""
        return self.output_dir / "inference_report.json"

    @property
    def metadata_report_path(self) -> Path:
        """Default path for the metadata JSON report."""
        return self.output_dir / "metadata_report.json"

    @property
    def qc_report_path(self) -> Path:
        """Default path for the quality-control JSON report."""
        return self.output_dir / "qc_report.json"

    @property
    def export_dir(self) -> Path:
        """Default export package directory."""
        return self.export.export_dir

def load_config(config_path: Path | None = None) -> PipelineConfig:
    """
    Load pipeline configuration from YAML.
    Falls back to defaults when no config file is provided.
    """
    if config_path is None:
        return PipelineConfig()
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")


    with config_path.open("r", encoding="utf-8") as file:
        data: dict[str, Any] = yaml.safe_load(file) or {}

    paths = data.get("paths", {})
    ingestion_data = data.get("ingestion", {})
    inference_data = data.get("inference", {})
    qc_data = data.get("qc", {})
    export_data = data.get("export", {})
    logging_data = data.get("logging", {})

    extensions = ingestion_data.get(
        "supported_extensions",
        list(DEFAULT_SUPPORTED_EXTENSIONS),
    )


    ingestion = IngestionConfig(
        supported_extensions=tuple(extensions),
        recursive=ingestion_data.get("recursive", True),
        mode=ingestion_data.get("mode", "copy"),
    )

    inference = InferenceConfig(
        backend=inference_data.get("backend", "mock"),
        model_name=inference_data.get(
            "model_name",
            "Qwen/Qwen2.5-VL-3B-Instruct",
        ),
        load_in_4bit=inference_data.get("load_in_4bit", True),
        max_new_tokens=inference_data.get("max_new_tokens", 128),
        max_pixels=inference_data.get("max_pixels", 352800),
        api_base=inference_data.get("api_base", ""),
        api_key_env=inference_data.get("api_key_env", "VLM_API_KEY"),
        api_timeout=inference_data.get("api_timeout", 120),
    )

    qc = QCConfig(
        blur_threshold=float(qc_data.get("blur_threshold", 100.0)),
    )

    export = ExportConfig(
        export_dir=Path(export_data.get("export_dir", "outputs/export")),
        exclude_duplicates=bool(export_data.get("exclude_duplicates", True)),
        include_blurry=bool(export_data.get("include_blurry", False)),
        require_caption=bool(export_data.get("require_caption", True)),
    )


    log_file = logging_data.get("log_file")
    logging_config = LoggingConfig(
        level=logging_data.get("level", "INFO"),
        log_file=Path(log_file) if log_file else None,
    )


    return PipelineConfig(
        raw_dir=Path(paths.get("raw_dir", "datasets/raw")),
        processed_dir=Path(paths.get("processed_dir", "datasets/processed")),
        output_dir=Path(paths.get("output_dir", "outputs")),
        ingestion=ingestion,
        inference=inference,
        qc=qc,
        export=export,
        logging=logging_config,
    )

"""
PipelineConfig(
    raw_dir=Path('/mnt/data/raw_images'),
    processed_dir=Path('datasets/processed'),
    output_dir=Path('/mnt/data/results'),
    ingestion=IngestionConfig(
        supported_extensions=('.jpg', '.jpeg', '.png', '.webp', '.bmp'),
        mode='move'
    ),
    logging=LoggingConfig(
        level='DEBUG',
        log_file=Path('logs/my_app.log')
    )
)
"""