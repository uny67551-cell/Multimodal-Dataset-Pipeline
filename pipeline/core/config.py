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
class LoggingConfig:
    """Logging settings."""
    level: str = "INFO"
    log_file: Path | None = None

@dataclass
class PipelineConfig:
    """Top-level pipeline configuration."""
    raw_dir: Path = Path("datasets/raw")  # default path 
    processed_dir: Path = Path("datasets/processed")
    output_dir: Path = Path("outputs")
    ingestion: IngestionConfig = field(default_factory=IngestionConfig) # (field(default_factory=class_name))
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    @property
    def ingestion_report_path(self) -> Path:
        """Default path for the ingestion JSON report."""
        return self.output_dir / "ingestion_report.json"

        # ↑↑↑ default values are used if no config file is provided

def load_config(config_path: Path | None = None) -> PipelineConfig:
    """
    Load pipeline configuration from YAML.
    Falls back to defaults when no config file is provided.
    """
    if config_path is None:
        return PipelineConfig()  # no config file provided, use default values
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # load config file(yaml), parse it into a dictionary

    with config_path.open("r", encoding="utf-8") as file:
        data: dict[str, Any] = yaml.safe_load(file) or {} # safe_load is a function that loads the yaml file into a dictionary
                                                          # or {} is a default value if value is not None or False
    paths = data.get("paths", {}) # get the paths from the dictionary,if not found, use default values {}
    ingestion_data = data.get("ingestion", {})
    logging_data = data.get("logging", {})
    extensions = ingestion_data.get(
        "supported_extensions",
        list(DEFAULT_SUPPORTED_EXTENSIONS),
    )

    # ↓↓↓ create IngestionConfig object with the data from the dictionary

    ingestion = IngestionConfig(
        supported_extensions=tuple(extensions),
        recursive=ingestion_data.get("recursive", True), # if not found, use default value True
        mode=ingestion_data.get("mode", "copy"),
    )

    # ↓↓↓ create LoggingConfig object with the data from the dictionary

    log_file = logging_data.get("log_file")
    logging_config = LoggingConfig(
        level=logging_data.get("level", "INFO"),
        log_file=Path(log_file) if log_file else None, # None means not saved to file
    )

    # ↓↓↓ create final PipelineConfig object with the data from the dictionary

    return PipelineConfig(
        raw_dir=Path(paths.get("raw_dir", "datasets/raw")),
        processed_dir=Path(paths.get("processed_dir", "datasets/processed")),
        output_dir=Path(paths.get("output_dir", "outputs")),
        ingestion=ingestion,
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