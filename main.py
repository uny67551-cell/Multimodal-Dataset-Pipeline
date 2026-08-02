"""CLI entry point for Multimodal Dataset Pipeline."""

import argparse
from pathlib import Path
from pipeline.core.config import load_config
from pipeline.core.logger import setup_logger
from pipeline.ingestion.stage import IngestionStage

def build_parser() -> argparse.ArgumentParser:  
    """Build command-line argument parser."""
    parser = argparse.ArgumentParser(               # create a new parser object;interpreter
        description="Multimodal Dataset Pipeline",  # display this when --help is called
    )
    # subparsers is a dictionary of subparsers; command is the key; ingest is the value. Only subparsers can be used as different command-modes.
    subparsers = parser.add_subparsers(dest="command", required=True) # command is a mode-tag; required=True means user must specify a subparser
    ingest = subparsers.add_parser(
        "ingest",                                   # name of container in command
        help="Run image ingestion pipeline",
    )
    ingest.add_argument(
        "--input", # user can input by --input or -i
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
        action="store_true", # default is False
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
    return parser # return the root parser object

def run_ingest(args: argparse.Namespace) -> None:
    """Load config, setup logging, and run ingestion."""
    config = load_config(args.config)

    # ↓↓↓ try to override config if value received

    if args.output is not None:
        config.processed_dir = args.output # override the processed directory
    if args.move:
        config.ingestion.mode = "move"
    if args.no_recursive:
        config.ingestion.recursive = False
    log_level = args.log_level or config.logging.level
    setup_logger(level=log_level, log_file=config.logging.log_file) # level to logger
    stage = IngestionStage(config) # logger to stage
    records = stage.run(input_dir=args.input)
    print(f"Done. Processed {len(records)} records.") # print the number of records
    print(f"Report: {config.ingestion_report_path}") # ingestion_report_path is a def created by @property
    if config.logging.log_file is not None:
        print(f"Log file: {config.logging.log_file}") # print the log file path

def main() -> None:
    """CLI main entry."""
    parser = build_parser() # build the parser object
    args = parser.parse_args() # parse the arguments and return a Namespace object
    if args.command == "ingest":
        run_ingest(args)
    else:
        parser.error(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()