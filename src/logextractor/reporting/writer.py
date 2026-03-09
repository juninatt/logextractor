"""
Write extraction results to a human-readable text file.

This module formats the extraction output together with the active
configuration profile so that each result file is self-describing.
"""

from pathlib import Path

from logextractor.domain.models import AppConfig, ExtractionResult, FilterRule


class ResultWriter:
    """Write extraction results and active configuration details to an output file."""

    @staticmethod
    def write(result: ExtractionResult, config: AppConfig, output_path: Path) -> None:
        """
        Write the extraction result and the relevant profile configuration to disk.

        The output file includes both the extracted entries and the active
        filtering settings so the result remains understandable without
        reopening the original configuration file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            file.write("logextractor result\n")
            file.write("===================\n\n")

            file.write(f"Profile: {config.profile.name}\n")
            file.write(f"Description: {config.profile.description}\n\n")

            file.write(f"Input file: {result.input_file}\n")
            file.write(f"Total lines read: {result.total_lines_read}\n")
            file.write(f"Total lines parsed: {result.total_lines_parsed}\n")
            file.write(f"Total matched entries: {result.total_lines_matched}\n\n")

            file.write("Active filtering configuration\n")
            file.write("------------------------------\n")

            for rule in config.filtering.rules:
                ResultWriter._write_rule(file, rule)
                file.write("\n")

            file.write("Global exclusions\n")
            file.write("-----------------\n")
            file.write(
                f"Exclude log levels: "
                f"{ResultWriter._format_list(config.filtering.exclude_log_levels)}\n"
            )
            file.write(
                f"Exclude sources: "
                f"{ResultWriter._format_list(config.filtering.exclude_sources)}\n"
            )
            file.write(
                f"Exclude messages containing: "
                f"{ResultWriter._format_list(config.filtering.exclude_messages_containing)}\n\n"
            )

            file.write("Output settings\n")
            file.write("---------------\n")
            file.write(
                f"Output verbosity level: "
                f"{config.output_settings.output_verbosity_level}\n"
            )
            file.write(
                f"Write run summary: "
                f"{ResultWriter._format_bool(config.output_settings.write_run_summary)}\n"
            )
            file.write(
                f"Write statistics: "
                f"{ResultWriter._format_bool(config.output_settings.write_statistics)}\n\n"
            )

            file.write("Matched entries\n")
            file.write("---------------\n")

            for matched_entry in result.matched_entries:
                file.write(f"[{matched_entry.rule_name}] {matched_entry.entry.raw_line}\n")

    @staticmethod
    def _write_rule(file, rule: FilterRule) -> None:
        """Write one filtering rule in a readable format."""
        file.write(f"Rule: {rule.rule_name}\n")
        file.write(
            f"  Match log levels: "
            f"{ResultWriter._format_list(rule.match_log_levels)}\n"
        )
        file.write(
            f"  Match sources: "
            f"{ResultWriter._format_list(rule.match_sources)}\n"
        )
        file.write(
            f"  Match logger name contains: "
            f"{ResultWriter._format_list(rule.match_logger_name_contains)}\n"
        )
        file.write(
            f"  Match message contains: "
            f"{ResultWriter._format_list(rule.match_message_contains)}\n"
        )
        file.write(
            f"  Context before seconds: "
            f"{rule.include_context_before_seconds}\n"
        )
        file.write(
            f"  Context after seconds: "
            f"{rule.include_context_after_seconds}\n"
        )

    @staticmethod
    def _format_list(values: list[str] | None) -> str:
        """Format optional string lists for human-readable output."""
        if not values:
            return "-"

        return ", ".join(values)

    @staticmethod
    def _format_bool(value: bool) -> str:
        """Format boolean values consistently in output files."""
        return "true" if value else "false"
