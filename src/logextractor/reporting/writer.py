from collections import defaultdict
from pathlib import Path
from typing import TextIO

from logextractor.domain.models import ExtractionConfig, ExtractionResult, MatchedLine


class ResultWriter:

    @staticmethod
    def write(
        result: ExtractionResult,
        config: ExtractionConfig,
        output_path: Path,
    ) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            ResultWriter._write_header(file, result, config)
            ResultWriter._write_matched_lines(file, result)

    @staticmethod
    def _write_header(
        file: TextIO,
        result: ExtractionResult,
        config: ExtractionConfig,
    ) -> None:
        file.write("LOG EXTRACTOR RESULTS\n")
        file.write("---\n")
        file.write(f"Files read: {result.total_files_read}\n")
        file.write(f"Lines read: {result.total_lines_read}\n")
        file.write(f"Matched lines: {result.total_lines_matched}\n")
        file.write("---\n")
        file.write("Configuration\n")
        file.write(f"Include keywords: {ResultWriter._format_list(config.include_keywords)}\n")
        file.write(f"Trigger keywords: {ResultWriter._format_list(config.trigger_keywords)}\n")
        file.write(f"Exclude keywords: {ResultWriter._format_list(config.exclude_keywords)}\n")
        file.write(f"Duration seconds: {config.duration_seconds}\n")
        file.write("\n")

    @staticmethod
    def _write_matched_lines(file: TextIO, result: ExtractionResult) -> None:
        lines_by_file: dict[Path, list[MatchedLine]] = defaultdict(list)

        for line in result.matched_lines:
            lines_by_file[line.file_path].append(line)

        if not lines_by_file:
            file.write("No matching lines found.\n")
            return

        for file_path, lines in lines_by_file.items():
            file.write(f"File: {file_path}\n")
            file.write("-" * 80)
            file.write("\n")

            for line in lines:
                file.write(
                    f"[{line.reason}] "
                    f"line {line.line_number}: "
                    f"{line.raw_line}\n"
                )

            file.write("\n")

    @staticmethod
    def _format_list(values: list[str]) -> str:
        if not values:
            return "-"

        return ", ".join(values)
