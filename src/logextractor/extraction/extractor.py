"""
Run the end-to-end log extraction workflow for a single input file.

This module coordinates configuration loading, log parsing, rule matching,
and result collection. It acts as the main extraction layer between the CLI
and the lower-level parsing, filtering, and reporting components.
"""

from pathlib import Path

from logextractor.config.loader import ConfigLoader
from logextractor.domain.models import ExtractionResult, MatchedLogEntry
from logextractor.filtering.matcher import LogMatcher
from logextractor.parsing.log_parser import LogParser


class LogExtractor:
    """
    Process a log file and collect entries that match configured rules.
    """

    def __init__(self, year: int) -> None:
        self._year = year

    def extract(self, input_path: Path, config_path: Path) -> ExtractionResult:
        """
        Extract matching log entries from the given input file using the selected profile.
        """
        config = ConfigLoader.load(config_path)
        parser = LogParser(year=self._year)

        total_lines_read = 0
        total_lines_parsed = 0
        matched_entries: list[MatchedLogEntry] = []

        with input_path.open("r", encoding=config.input_settings.file_encoding) as file:
            for line in file:
                total_lines_read += 1

                entry = parser.parse_line(line)
                if entry is None:
                    continue

                total_lines_parsed += 1

                if LogMatcher.is_excluded(entry, config.filtering):
                    continue

                for rule in config.filtering.rules:
                    if LogMatcher.matches_rule(entry, rule):
                        matched_entries.append(
                            MatchedLogEntry(
                                rule_name=rule.rule_name,
                                entry=entry,
                            )
                        )

        return ExtractionResult(
            input_file=str(input_path),
            total_lines_read=total_lines_read,
            total_lines_parsed=total_lines_parsed,
            total_lines_matched=len(matched_entries),
            matched_entries=matched_entries,
        )
