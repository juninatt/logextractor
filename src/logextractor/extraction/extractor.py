"""
Run the end-to-end log extraction workflow for a single input file.

This module coordinates configuration loading, log parsing, rule matching,
and result collection. It acts as the main extraction layer between the CLI
and the lower-level parsing, filtering, and reporting components.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from logextractor.config.loader import ConfigLoader
from logextractor.domain.models import (
    ExtractionResult,
    FilterRule,
    LogEntry,
    MatchTrigger,
    MatchedSequence,
    TimeRangeConfig,
)
from logextractor.filtering.matcher import LogMatcher
from logextractor.parsing.log_parser import LogParser


@dataclass
class _CandidateSequence:
    """Represents a mutable time window before it is converted to a final sequence."""

    start_timestamp: datetime
    end_timestamp: datetime
    triggers: list[MatchTrigger]


class LogExtractor:
    """Process a log file and collect entries that match configured rules."""

    _SOURCE_IDENTIFIER_PATTERN = re.compile(
        r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+(\S+)\s+"
    )

    def __init__(self, year: int) -> None:
        self._year = year

    def extract(self, input_path: Path, config_path: Path) -> ExtractionResult:
        """
        Extract matching log sequences from the given input file using the selected profile.
        """
        config = ConfigLoader.load(config_path)
        parser = LogParser(year=self._year)

        total_lines_read = 0
        total_lines_parsed = 0
        total_lines_matched = 0
        source_identifier: str | None = None
        parsed_entries: list[LogEntry] = []
        candidate_sequences: list[_CandidateSequence] = []

        with input_path.open("r", encoding=config.input_settings.file_encoding) as file:
            for line in file:
                total_lines_read += 1

                if source_identifier is None:
                    source_identifier = self._extract_source_identifier(line)

                entry = parser.parse_line(line)
                if entry is None:
                    continue

                if not self._is_within_time_range(entry, config.time_range):
                    continue

                total_lines_parsed += 1
                parsed_entries.append(entry)

                for rule in config.filtering.rules:
                    if LogMatcher.matches_rule(entry, rule):
                        total_lines_matched += 1
                        candidate_sequences.append(
                            self._create_candidate_sequence(entry=entry, rule=rule)
                        )

        merged_sequences = self._merge_overlapping_sequences(candidate_sequences)
        final_sequences = self._build_final_sequences(
            parsed_entries=parsed_entries,
            merged_sequences=merged_sequences,
        )

        return ExtractionResult(
            input_file=str(input_path),
            source_identifier=source_identifier,
            total_lines_read=total_lines_read,
            total_lines_parsed=total_lines_parsed,
            total_lines_matched=total_lines_matched,
            sequences=final_sequences,
        )

    @classmethod
    def _extract_source_identifier(cls, line: str) -> str | None:
        """
        Extract the source identifier from the common syslog prefix.
        """
        match = cls._SOURCE_IDENTIFIER_PATTERN.match(line)
        if match is None:
            return None

        return match.group(1)

    @staticmethod
    def _is_within_time_range(entry: LogEntry, time_range: TimeRangeConfig) -> bool:
        """
        Return True if the entry falls within the configured UTC time range.

        The configured start and end times are interpreted as inclusive UTC
        times in HH:MM:SS format.
        """
        if not time_range.enabled:
            return True

        entry_time = entry.timestamp.time()

        start_time = (
            datetime.strptime(time_range.start_time, "%H:%M:%S").time()
            if time_range.start_time
            else None
        )
        end_time = (
            datetime.strptime(time_range.end_time, "%H:%M:%S").time()
            if time_range.end_time
            else None
        )

        if start_time and entry_time < start_time:
            return False

        if end_time and entry_time > end_time:
            return False

        return True

    @staticmethod
    def _create_candidate_sequence(
        entry: LogEntry,
        rule: FilterRule,
    ) -> _CandidateSequence:
        """
        Create an initial sequence window around a matched entry using rule context settings.
        """
        return _CandidateSequence(
            start_timestamp=entry.timestamp
            - timedelta(seconds=rule.include_context_before_seconds),
            end_timestamp=entry.timestamp
            + timedelta(seconds=rule.include_context_after_seconds),
            triggers=[
                MatchTrigger(
                    rule_name=rule.rule_name,
                    timestamp=entry.timestamp,
                    source=entry.source,
                    logger=entry.logger,
                    message=entry.message,
                )
            ],
        )

    @staticmethod
    def _merge_overlapping_sequences(
        sequences: list[_CandidateSequence],
    ) -> list[_CandidateSequence]:
        """
        Merge overlapping candidate sequences into larger chronological windows.
        """
        if not sequences:
            return []

        sorted_sequences = sorted(
            sequences,
            key=lambda sequence: sequence.start_timestamp,
        )
        merged: list[_CandidateSequence] = [sorted_sequences[0]]

        for current in sorted_sequences[1:]:
            previous = merged[-1]

            if current.start_timestamp <= previous.end_timestamp:
                previous.end_timestamp = max(previous.end_timestamp, current.end_timestamp)
                previous.triggers.extend(current.triggers)
                previous.triggers.sort(key=lambda trigger: trigger.timestamp)
            else:
                merged.append(current)

        return merged

    @staticmethod
    def _build_final_sequences(
        parsed_entries: list[LogEntry],
        merged_sequences: list[_CandidateSequence],
    ) -> list[MatchedSequence]:
        """
        Convert merged candidate windows into final matched sequences with entries.
        """
        final_sequences: list[MatchedSequence] = []

        for sequence in merged_sequences:
            entries = [
                entry
                for entry in parsed_entries
                if sequence.start_timestamp <= entry.timestamp <= sequence.end_timestamp
            ]

            final_sequences.append(
                MatchedSequence(
                    start_timestamp=sequence.start_timestamp,
                    end_timestamp=sequence.end_timestamp,
                    triggers=sequence.triggers,
                    entries=entries,
                )
            )

        return final_sequences
