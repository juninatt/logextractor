"""
Write extraction results to a human-readable text file.

This module formats the extraction output together with the active
configuration profile so that each result file is self-describing.
"""

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import TextIO

from logextractor.domain.models import AppConfig, ExtractionResult, FilterRule, MatchedSequence


class ResultWriter:
    """Write extraction results and active configuration details to an output file."""

    @staticmethod
    def write(result: ExtractionResult, config: AppConfig, output_path: Path) -> None:
        """
        Write the extraction result and the relevant profile configuration to disk.
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

            file.write("Trigger summary\n")
            file.write("---------------\n")
            ResultWriter._write_trigger_summary(file, result)
            file.write("\n")

            file.write("Matched sequences\n")
            file.write("-----------------\n\n")

            for index, sequence in enumerate(result.sequences, start=1):
                ResultWriter._write_sequence(file, index, sequence)

    @staticmethod
    def _write_rule(file: TextIO, rule: FilterRule) -> None:
        """
        Write one filtering rule in a readable format.
        """
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
    def _write_trigger_summary(file: TextIO, result: ExtractionResult) -> None:
        """
        Write the total number of trigger matches grouped by rule name.
        """
        trigger_counts: Counter[str] = Counter()

        for sequence in result.sequences:
            for trigger in sequence.triggers:
                trigger_counts[trigger.rule_name] += 1

        if not trigger_counts:
            file.write("-\n")
            return

        for rule_name, count in sorted(trigger_counts.items()):
            file.write(f"{rule_name}: {count}\n")

    @staticmethod
    def _write_sequence(file: TextIO, index: int, sequence: MatchedSequence) -> None:
        """
        Write one matched sequence with aggregated trigger counts and included log entries.
        """
        file.write(f"Sequence {index}\n")
        file.write(f"{'-' * len(f'Sequence {index}')}\n")
        file.write(
            f"Window: {ResultWriter._format_timestamp(sequence.start_timestamp)}"
            f" -> {ResultWriter._format_timestamp(sequence.end_timestamp)}\n"
        )
        file.write(
            f"Duration: "
            f"{int((sequence.end_timestamp - sequence.start_timestamp).total_seconds())} seconds\n\n"
        )

        file.write("Triggered by\n")
        file.write("------------\n")
        ResultWriter._write_sequence_trigger_summary(file, sequence)
        file.write("\n")

        file.write("Entries:\n")

        for entry in sequence.entries:
            file.write(f"{entry.raw_line}\n")

        file.write("\n")

    @staticmethod
    def _write_sequence_trigger_summary(file: TextIO, sequence: MatchedSequence) -> None:
        """
        Write aggregated trigger counts for one sequence grouped by rule name.
        """
        trigger_counts: Counter[str] = Counter(trigger.rule_name for trigger in sequence.triggers)

        if not trigger_counts:
            file.write("-\n")
            return

        for rule_name, count in sorted(trigger_counts.items()):
            match_label = "match" if count == 1 else "matches"
            file.write(f"{rule_name}: {count} {match_label}\n")

    @staticmethod
    def _format_list(values: list[str] | None) -> str:
        """
        Format optional string lists for human-readable output.
        """
        if not values:
            return "-"

        return ", ".join(values)

    @staticmethod
    def _format_bool(value: bool) -> str:
        """
        Format boolean values consistently in output files.
        """
        return "true" if value else "false"

    @staticmethod
    def _format_timestamp(value: datetime) -> str:
        """
        Format timestamps consistently in output files.
        """
        return value.strftime("%Y-%m-%d %H:%M:%S")
