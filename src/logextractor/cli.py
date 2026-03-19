"""
Provide the command-line entry point for the logextractor application.

This module parses command-line arguments, resolves the selected configuration
profile, and runs the extraction workflow.
"""

import argparse
from datetime import datetime
from pathlib import Path

from logextractor.config.loader import ConfigLoader
from logextractor.constants import DEFAULT_CONFIG_DIRECTORY, DEFAULT_CURRENT_YEAR
from logextractor.extraction.extractor import LogExtractor
from logextractor.reporting.writer import ResultWriter


def build_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser used by the CLI."""
    parser = argparse.ArgumentParser(
        prog="logextractor",
        description="Extract matching log entries from a log file using JSON rules.",
    )
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Path to the input log file.",
    )
    parser.add_argument(
        "-c",
        "--config",
        required=True,
        help="Configuration file name or path.",
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=DEFAULT_CURRENT_YEAR,
        help="Year used when parsing syslog timestamps. Defaults to the current year.",
    )
    return parser


def resolve_config_path(config_argument: str) -> Path:
    """Resolve the configuration path from either a file name or an explicit path."""
    config_path = Path(config_argument)

    if config_path.is_absolute():
        return config_path

    if config_path.parent == Path("."):
        return DEFAULT_CONFIG_DIRECTORY / config_path

    return config_path


def build_output_path(input_path: Path, config_path: Path, configured_output_path: str) -> Path:
    """
    Build the output file path using input file name, current time, and config file name.

    The directory is taken from the configured output path. The file name is generated as:
    <input-file-stem>_<HHMM>_<config-file-stem>.txt
    """
    output_directory = Path(configured_output_path).parent
    timestamp = datetime.now().strftime("%H%M")

    file_name = f"{input_path.stem}_{timestamp}_{config_path.stem}.txt"
    return output_directory / file_name


def main() -> None:
    """Run the CLI extraction workflow."""
    args = build_parser().parse_args()

    input_path = Path(args.input)
    config_path = resolve_config_path(args.config)

    config = ConfigLoader.load(config_path)
    extractor = LogExtractor(year=args.year)
    result = extractor.extract(input_path=input_path, config_path=config_path)

    output_path = build_output_path(
        input_path=input_path,
        config_path=config_path,
        configured_output_path=config.output_settings.output_file_path,
    )

    ResultWriter.write(result=result, config=config, output_path=output_path)

    print(f"Matched entries: {result.total_lines_matched}")
    print(f"Output written to: {output_path}")
