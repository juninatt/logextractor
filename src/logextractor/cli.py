import argparse
from pathlib import Path

from logextractor.config.loader import ConfigLoader
from logextractor.extraction.extractor import LogExtractor
from logextractor.reporting.writer import ResultWriter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="logextractor",
        description="Extract matching log entries from a log file using JSON rules.",
    )
    parser.add_argument("--input", required=True, help="Path to the input log file.")
    parser.add_argument("--config", required=True, help="Path to the JSON config file.")
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year used when parsing syslog timestamps.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    input_path = Path(args.input)
    config_path = Path(args.config)

    config = ConfigLoader.load(config_path)
    extractor = LogExtractor(year=args.year)
    result = extractor.extract(input_path=input_path, config_path=config_path)

    output_path = Path(config.output.file_path)
    ResultWriter.write(result=result, output_path=output_path)

    print(f"Matched entries: {result.total_lines_matched}")
    print(f"Output written to: {output_path}")