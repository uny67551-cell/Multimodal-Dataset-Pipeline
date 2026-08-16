"""CLI entry point for Multimodal Dataset Pipeline."""

import argparse
from pathlib import Path
from pipeline.core.config import load_config
from pipeline.core.logger import setup_logger
from pipeline.ingestion.stage import IngestionStage
from pipeline.inference.factory import create_backend
from pipeline.inference.stage import InferenceStage
from pipeline.metadata.stage import MetadataStage
from pipeline.qc.stage import QCStage
from pipeline.export.stage import ExportStage
from pipeline.export.filter import iter_included

def build_parser() -> argparse.ArgumentParser:
    """Build command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Multimodal Dataset Pipeline",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)


    ingest = subparsers.add_parser(
        "ingest",
        help="Run image ingestion pipeline",
    )
    ingest.add_argument(
        "--input",
        "-i",
        type=Path,
        default=None,
        help="Input directory with raw images",
    )
    ingest.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output directory for processed images",
    )
    ingest.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("configs/default.yaml"),
        help="Path to YAML config file",
    )
    ingest.add_argument(
        "--move",
        action="store_true",
        help="Move files instead of copying",
    )
    ingest.add_argument(
        "--no-recursive",
        action="store_true",
        help="Do not scan subdirectories",
    )
    ingest.add_argument(
        "--log-level",
        default=None,
        help="Override log level, e.g. DEBUG / INFO",
    )


    infer = subparsers.add_parser(
        "infer",
        help="Run VLM inference pipeline",
    )
    infer.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("configs/default.yaml"),
    )
    infer.add_argument(
        "--processed",
        "-p",
        type=Path,
        default=None,
        help="Processed images directory (default: config.processed_dir)",
    )
    infer.add_argument(
        "--report",
        "-r",
        type=Path,
        default=None,
        help="Ingestion report JSON (default: outputs/ingestion_report.json)",
    )
    infer.add_argument(
        "--backend",
        "-b",
        default=None,
        help="Override backend: mock | local | api",
    )
    infer.add_argument("--log-level", default=None)


    metadata = subparsers.add_parser(
        "metadata",
        help="Merge ingestion and inference reports into metadata",
    )
    metadata.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("configs/default.yaml"),
    )
    metadata.add_argument(
        "--ingestion-report",
        type=Path,
        default=None,
        help="Ingestion report JSON (default: outputs/ingestion_report.json)",
    )
    metadata.add_argument(
        "--inference-report",
        type=Path,
        default=None,
        help="Inference report JSON (default: outputs/inference_report.json)",
    )
    metadata.add_argument("--log-level", default=None)


    qc = subparsers.add_parser(
        "qc",
        help="Run image quality-control pipeline",
    )
    qc.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("configs/default.yaml"),
    )
    qc.add_argument(
        "--metadata-report",
        type=Path,
        default=None,
        help="Metadata report JSON (default: outputs/metadata_report.json)",
    )
    qc.add_argument(
        "--processed",
        "-p",
        type=Path,
        default=None,
        help="Processed images directory (default: config.processed_dir)",
    )
    qc.add_argument(
        "--blur-threshold",
        type=float,
        default=None,
        help="Override blur Laplacian threshold (default: config.qc.blur_threshold)",
    )
    qc.add_argument("--log-level", default=None)


    export = subparsers.add_parser(
        "export",
        help="Export a self-contained training dataset package",
    )
    export.add_argument(
        "--config",
        "-c",
        type=Path,
        default=Path("configs/default.yaml"),
    )
    export.add_argument(
        "--metadata-report",
        type=Path,
        default=None,
        help="Metadata report JSON (default: outputs/metadata_report.json)",
    )
    export.add_argument(
        "--qc-report",
        type=Path,
        default=None,
        help="QC report JSON (default: outputs/qc_report.json)",
    )
    export.add_argument(
        "--export-dir",
        type=Path,
        default=None,
        help="Export package directory (default: config.export.export_dir)",
    )
    export.add_argument(
        "--include-blurry",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Include blurry images (default: config.export.include_blurry)",
    )
    export.add_argument(
        "--exclude-duplicates",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Exclude duplicate images (default: config.export.exclude_duplicates)",
    )
    export.add_argument(
        "--require-caption",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Require non-empty caption (default: config.export.require_caption)",
    )
    export.add_argument("--log-level", default=None)

    return parser

def run_ingest(args: argparse.Namespace) -> None:
    """Load config, setup logging, and run ingestion."""
    config = load_config(args.config)


    if args.output is not None:
        config.processed_dir = args.output
    if args.move:
        config.ingestion.mode = "move"
    if args.no_recursive:
        config.ingestion.recursive = False
    log_level = args.log_level or config.logging.level
    setup_logger(level=log_level, log_file=config.logging.log_file)
    stage = IngestionStage(config)
    records = stage.run(input_dir=args.input)
    print(f"Done. Processed {len(records)} records.")
    print(f"Report: {config.ingestion_report_path}")
    if config.logging.log_file is not None:
        print(f"Log file: {config.logging.log_file}")

def run_infer(args: argparse.Namespace) -> None:
    """Load config, setup logging, and run inference."""
    config = load_config(args.config)
    if args.backend is not None:
        config.inference.backend = args.backend
    log_level = args.log_level or config.logging.level
    setup_logger(level=log_level, log_file=config.logging.log_file)
    backend = create_backend(config.inference)
    stage = InferenceStage(config=config, backend=backend)
    records = stage.run(
        report_path=args.report,
        processed_dir=args.processed,
    )
    print(f"Done. Inferred {len(records)} records.")
    print(f"Backend: {backend.name}")
    print(f"Report: {config.inference_report_path}")
    if config.logging.log_file is not None:
        print(f"Log file: {config.logging.log_file}")

def run_metadata(args: argparse.Namespace) -> None:
    """Load config, setup logging, and run metadata merge."""
    config = load_config(args.config)
    log_level = args.log_level or config.logging.level
    setup_logger(level=log_level, log_file=config.logging.log_file)
    stage = MetadataStage(config)
    records = stage.run(
        ingestion_report_path=args.ingestion_report,
        inference_report_path=args.inference_report,
    )
    print(f"Done. Generated {len(records)} metadata records.")
    print(f"Report: {config.metadata_report_path}")
    if config.logging.log_file is not None:
        print(f"Log file: {config.logging.log_file}")

def run_qc(args: argparse.Namespace) -> None:
    """Load config, setup logging, and run quality control."""
    config = load_config(args.config)

    if args.blur_threshold is not None:
        config.qc.blur_threshold = args.blur_threshold

    log_level = args.log_level or config.logging.level
    setup_logger(level=log_level, log_file=config.logging.log_file)

    stage = QCStage(config)
    records = stage.run(
        metadata_report_path=args.metadata_report,
        processed_dir=args.processed,
    )

    pass_n = sum(1 for r in records if r.quality_status == "pass")
    warn_n = sum(1 for r in records if r.quality_status == "warn")
    reject_n = sum(1 for r in records if r.quality_status == "reject")

    print(f"Done. Checked {len(records)} images.")
    print(f"pass={pass_n} warn={warn_n} reject={reject_n}")
    print(f"blur_threshold={config.qc.blur_threshold}")
    print(f"Report: {config.qc_report_path}")
    if config.logging.log_file is not None:
        print(f"Log file: {config.logging.log_file}")

def run_export(args: argparse.Namespace) -> None:
    """Load config, setup logging, and run dataset export."""
    config = load_config(args.config)

    if args.export_dir is not None:
        config.export.export_dir = args.export_dir
    if args.include_blurry is not None:
        config.export.include_blurry = args.include_blurry
    if args.exclude_duplicates is not None:
        config.export.exclude_duplicates = args.exclude_duplicates
    if args.require_caption is not None:
        config.export.require_caption = args.require_caption

    log_level = args.log_level or config.logging.level
    setup_logger(level=log_level, log_file=config.logging.log_file)

    stage = ExportStage(config)
    records = stage.run(
        metadata_report_path=args.metadata_report,
        qc_report_path=args.qc_report,
    )

    included = iter_included(records)
    print(f"Done. Candidates={len(records)} included={len(included)}")
    print(f"exclude_duplicates={config.export.exclude_duplicates}")
    print(f"include_blurry={config.export.include_blurry}")
    print(f"require_caption={config.export.require_caption}")
    print(f"Export dir: {stage.export_dir}")
    print(f"Annotations: {stage.annotations_path}")
    print(f"Report: {stage.report_path}")
    print(f"LLaVA: {stage.llava_path}")
    if config.logging.log_file is not None:
        print(f"Log file: {config.logging.log_file}")

def main() -> None:
    """CLI main entry."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "ingest":
        run_ingest(args)
    elif args.command == "infer":
        run_infer(args)
    elif args.command == "metadata":
        run_metadata(args)
    elif args.command == "qc":
        run_qc(args)
    elif args.command == "export":
        run_export(args)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()