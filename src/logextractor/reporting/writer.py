from pathlib import Path

from logextractor.domain.models import ExtractionResult


class ResultWriter:
    """Writes extracted log results to a human-readable text file."""

    @staticmethod
    def write(result: ExtractionResult, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            file.write("logextractor result\n")
            file.write("===================\n\n")
            file.write(f"Input file: {result.input_file}\n")
            file.write(f"Total lines read: {result.total_lines_read}\n")
            file.write(f"Total lines parsed: {result.total_lines_parsed}\n")
            file.write(f"Total matched entries: {result.total_lines_matched}\n\n")
            file.write("Matched entries\n")
            file.write("---------------\n")

            for matched_entry in result.matched_entries:
                file.write(f"[{matched_entry.rule_name}] {matched_entry.entry.raw_line}\n")