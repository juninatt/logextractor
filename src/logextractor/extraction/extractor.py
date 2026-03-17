"""
Run the end-to-end log extraction workflow for a single input file.

This module coordinates configuration loading, log parsing, rule matching,
and result collection. It acts as the main extraction layer between the CLI
and the lower-level parsing, filtering, and reporting components.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from logextractor.domain.models import FilterRule

from logextractor.config.loader import ConfigLoader
from logextractor.domain.models import (
    ExtractionResult,
    LogEntry,
    MatchTrigger,
    MatchedSequence,
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
        parsed_entries: list[LogEntry] = []
        candidate_sequences: list[_CandidateSequence] = []

        with input_path.open("r", encoding=config.input_settings.file_encoding) as file:
            for line in file:
                total_lines_read += 1

                entry = parser.parse_line(line)
                if entry is None:
                    continue

                total_lines_parsed += 1
                parsed_entries.append(entry)

                if LogMatcher.is_excluded(entry, config.filtering):
                    continue

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
            total_lines_read=total_lines_read,
            total_lines_parsed=total_lines_parsed,
            total_lines_matched=total_lines_matched,
            sequences=final_sequences,
        )

    def _create_candidate_sequence(self, entry: LogEntry, rule: FilterRule) -> _CandidateSequence:
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

    def _merge_overlapping_sequences(
        self, sequences: list[_CandidateSequence]
    ) -> list[_CandidateSequence]:
        """
        Merge overlapping candidate sequences into larger chronological windows.
        """
        if not sequences:
            return []

        sorted_sequences = sorted(sequences, key=lambda sequence: sequence.start_timestamp)
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

    def _build_final_sequences(
        self,
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