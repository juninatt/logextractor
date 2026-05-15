import argparse
from datetime import datetime
from pathlib import Path

from logextractor.config.loader import ConfigLoader
from logextractor.constants import DEFAULT_CONFIG_DIRECTORY, DEFAULT_CURRENT_YEAR
from logextractor.domain.models import ExtractionConfig
from logextractor.extraction.extractor import LogExtractor
from logextractor.reporting.writer import ResultWriter


LOGS_DIRECTORY = Path("logs")
OUTPUT_DIRECTORY = Path("output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logextractor",
        description="Extract matching log lines from all .log files in the logs directory.",
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Configuration file name or path.",
    )

    parser.add_argument(
        "-m",
        "--manual",
        action="store_true",
        help="Use manual keyword arguments instead of a configuration file.",
    )

    parser.add_argument(
        "--include",
        nargs="*",
        default=[],
        help="Keywords for lines that should be included.",
    )

    parser.add_argument(
        "--trigger",
        nargs="*",
        default=[],
        help="Keywords for lines that should start a time window.",
    )

    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Keywords for lines that should always be excluded.",
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=0,
        help="Number of seconds to include after each trigger match.",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output file.",
    )

    parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=DEFAULT_CURRENT_YEAR,
        help="Year used when parsing syslog timestamps.",
    )

    parser.add_argument(
        "--print",
        action="store_true",
        help="Print matching lines to console instead of writing to file.",
    )

    return parser


def resolve_config_path(config_argument: str) -> Path:
    config_path = Path(config_argument)

    if config_path.is_absolute():
        return config_path

    if config_path.parent == Path("."):
        return DEFAULT_CONFIG_DIRECTORY / config_path

    return config_path


def resolve_input_paths() -> list[Path]:
    if not LOGS_DIRECTORY.exists():
        raise FileNotFoundError(f"Logs directory does not exist: {LOGS_DIRECTORY}")

    if not LOGS_DIRECTORY.is_dir():
        raise NotADirectoryError(f"Logs path is not a directory: {LOGS_DIRECTORY}")

    paths = sorted(path for path in LOGS_DIRECTORY.iterdir() if path.is_file())

    if not paths:
        raise FileNotFoundError(f"No log files found in directory: {LOGS_DIRECTORY}")

    invalid_paths = [path for path in paths if path.suffix != ".log"]

    if invalid_paths:
        invalid_files = ", ".join(str(path) for path in invalid_paths)
        raise ValueError(f"Logs directory contains non-log files: {invalid_files}")

    return paths


def build_config(args: argparse.Namespace) -> ExtractionConfig:
    if args.manual:
        return ExtractionConfig(
            include_keywords=args.include,
            trigger_keywords=args.trigger,
            exclude_keywords=args.exclude,
            duration_seconds=args.duration,
        )

    if args.config is None:
        raise ValueError("Either --manual or --config must be provided.")

    return ConfigLoader.load(resolve_config_path(args.config))


def build_output_path(input_paths: list[Path], output_argument: str | None) -> Path:
    if output_argument:
        return Path(output_argument)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if len(input_paths) == 1:
        file_name = f"{input_paths[0].stem}_{timestamp}_filtered.txt"
    else:
        file_name = f"combined_{timestamp}_filtered.txt"

    return OUTPUT_DIRECTORY / file_name


def print_to_console(result) -> None:
    current_file: Path | None = None

    for line in result.matched_lines:
        if line.file_path != current_file:
            current_file = line.file_path
            print()
            print(f"File: {current_file}")
            print("-" * 80)

        print(f"[{line.reason}] line {line.line_number}: {line.raw_line}")

    print()
    print(f"Files read: {result.total_files_read}")
    print(f"Lines read: {result.total_lines_read}")
    print(f"Matched lines: {result.total_lines_matched}")


def main() -> None:
    args = build_parser().parse_args()

    input_paths = resolve_input_paths()
    config = build_config(args)

    extractor = LogExtractor(year=args.year)
    result = extractor.extract(
        input_paths=input_paths,
        config=config,
    )

    if args.print:
        print_to_console(result)
        return

    output_path = build_output_path(
        input_paths=input_paths,
        output_argument=args.output,
    )

    ResultWriter.write(
        result=result,
        config=config,
        output_path=output_path,
    )

    print(f"Matched lines: {result.total_lines_matched}")
    print(f"Output written to: {output_path}")


if __name__ == "__main__":
    main()