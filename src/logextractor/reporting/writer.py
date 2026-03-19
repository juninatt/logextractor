"""
Write extraction results to a human-readable text file.

This module formats the extraction output together with the active
configuration profile so that each result file is self-describing.
"""

import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import TextIO

from logextractor.domain.models import (
    AppConfig,
    ExtractionResult,
    FilterRule,
    LogEntry,
    MatchedSequence,
)


class ResultWriter:
    """Write extraction results and active configuration details to an output file."""

    _COMMON_LOG_PREFIX_PATTERN = re.compile(
        r"^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+\S+\s+"
    )

    @staticmethod
    def write(result: ExtractionResult, config: AppConfig, output_path: Path) -> None:
        """
        Write the extraction result and the relevant profile configuration to disk.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            ResultWriter._write_header(file, result, config)
            ResultWriter._write_filtering_section(file, config)
            ResultWriter._write_time_range_section(file, config)
            ResultWriter._write_trigger_summary_section(file, result)
            ResultWriter._write_sequences_section(file, result, config)

    @staticmethod
    def _write_header(
        file: TextIO,
        result: ExtractionResult,
        config: AppConfig,
    ) -> None:
        """
        Write the top header and run overview.
        """
        file.write("LOG EXTRACTOR RESULTS\n")
        file.write("---\n")
        file.write(f"Profile: {config.profile.name}\n")
        file.write(f"Description: {config.profile.description}\n")
        file.write("---\n")
        file.write(
            f"Input file: {result.input_file} || "
            f"Source identifier: {result.source_identifier or '-'}\n"
        )
        file.write(
            f"Lines read: {result.total_lines_read} || "
            f"Lines parsed: {result.total_lines_parsed} || "
            f"Matched entries: {result.total_lines_matched}\n\n"
        )

    @staticmethod
    def _write_filtering_section(file: TextIO, config: AppConfig) -> None:
        """
        Write the active filtering rules section.
        """
        file.write("Active filtering configuration:\n")
        file.write("---\n")

        for rule in config.filtering.rules:
            ResultWriter._write_rule(file, rule)
            file.write("\n")

    @staticmethod
    def _write_time_range_section(file: TextIO, config: AppConfig) -> None:
        """
        Write the configured time range section when enabled.
        """
        if not config.time_range.enabled:
            return

        file.write("Time range\n")
        file.write("----------\n")
        file.write(
            f"Enabled: {ResultWriter._format_bool(config.time_range.enabled)} || "
            f"Timezone: {config.time_range.timezone} || "
            f"Start time: {config.time_range.start_time or '-'} || "
            f"End time: {config.time_range.end_time or '-'}\n\n"
        )

    @staticmethod
    def _write_trigger_summary_section(file: TextIO, result: ExtractionResult) -> None:
        """
        Write the trigger summary section.
        """
        file.write("Trigger summary\n")
        file.write("---------------\n")
        ResultWriter._write_trigger_summary(file, result)
        file.write("\n")

    @staticmethod
    def _write_sequences_section(
        file: TextIO,
        result: ExtractionResult,
        config: AppConfig,
    ) -> None:
        """
        Write all matched sequences.
        """
        total_sequences = len(result.sequences)

        file.write(f"Total matched sequences: {total_sequences}\n")
        file.write("-----------------\n\n")

        for index, sequence in enumerate(result.sequences, start=1):
            ResultWriter._write_sequence(
                file=file,
                index=index,
                total_sequences=total_sequences,
                sequence=sequence,
                strip_common_log_prefix=config.output_settings.strip_common_log_prefix,
            )

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
    def _write_sequence(
        file: TextIO,
        index: int,
        total_sequences: int,
        sequence: MatchedSequence,
        strip_common_log_prefix: bool,
    ) -> None:
        """
        Write one matched sequence with aggregated trigger counts and included log entries.
        """
        file.write(f"Sequence {index}/{total_sequences}\n")
        file.write("----------\n")
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

        file.write("Entries\n")
        file.write("-------\n")

        for entry in sequence.entries:
            formatted_line = ResultWriter._format_output_line(
                entry,
                strip_common_log_prefix,
            )

            if ResultWriter._is_trigger_entry(entry, sequence):
                file.write(f">>> {formatted_line}\n")
            else:
                file.write(f"    {formatted_line}\n")

        file.write("\n")

    @staticmethod
    def _write_sequence_trigger_summary(file: TextIO, sequence: MatchedSequence) -> None:
        """
        Write aggregated trigger counts for one sequence grouped by rule name.
        """
        trigger_counts: Counter[str] = Counter(
            trigger.rule_name for trigger in sequence.triggers
        )

        if not trigger_counts:
            file.write("-\n")
            return

        for rule_name, count in sorted(trigger_counts.items()):
            match_label = "match" if count == 1 else "matches"
            file.write(f"{rule_name}: {count} {match_label}\n")

    @staticmethod
    def _is_trigger_entry(entry: LogEntry, sequence: MatchedSequence) -> bool:
        """
        Return True if the entry corresponds to one of the sequence triggers.
        """
        for trigger in sequence.triggers:
            if (
                entry.timestamp == trigger.timestamp
                and entry.source == trigger.source
                and entry.logger == trigger.logger
                and entry.message == trigger.message
            ):
                return True

        return False

    @staticmethod
    def _format_output_line(entry: LogEntry, strip_common_log_prefix: bool) -> str:
        """
        Format one output line and remove the common syslog prefix if enabled.
        """
        line = entry.raw_line.rstrip("\n")

        if not strip_common_log_prefix:
            return line

        return ResultWriter._COMMON_LOG_PREFIX_PATTERN.sub(r"\1 ", line, count=1)

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