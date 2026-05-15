from datetime import timedelta
from pathlib import Path

from logextractor.domain.models import (
    ExtractionConfig,
    ExtractionResult,
    LogEntry,
    MatchedLine,
    TriggerWindow,
)
from logextractor.filtering.matcher import LogMatcher
from logextractor.parsing.log_parser import LogParser


class LogExtractor:

    def __init__(self, year: int) -> None:
        self._parser = LogParser(year=year)

    def extract(
        self,
        input_paths: list[Path],
        config: ExtractionConfig,
    ) -> ExtractionResult:
        total_lines_read = 0
        matched_lines: list[MatchedLine] = []

        for input_path in input_paths:
            entries, lines_read = self._read_entries(input_path)
            total_lines_read += lines_read

            trigger_windows = self._build_trigger_windows(entries, config)

            for entry in entries:
                if LogMatcher.is_excluded(entry, config):
                    continue

                reason = self._get_match_reason(entry, config, trigger_windows)

                if reason is None:
                    continue

                matched_lines.append(
                    MatchedLine(
                        file_path=entry.file_path,
                        line_number=entry.line_number,
                        timestamp=entry.timestamp,
                        raw_line=entry.raw_line,
                        reason=reason,
                    )
                )

        return ExtractionResult(
            total_files_read=len(input_paths),
            total_lines_read=total_lines_read,
            total_lines_matched=len(matched_lines),
            matched_lines=matched_lines,
        )

    def _read_entries(self, input_path: Path) -> tuple[list[LogEntry], int]:
        entries: list[LogEntry] = []
        total_lines_read = 0

        with input_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                total_lines_read += 1

                entry = self._parser.parse_line(
                    line=line,
                    file_path=input_path,
                    line_number=line_number,
                )

                if entry is not None:
                    entries.append(entry)

        return entries, total_lines_read

    @staticmethod
    def _build_trigger_windows(
        entries: list[LogEntry],
        config: ExtractionConfig,
    ) -> list[TriggerWindow]:
        trigger_windows: list[TriggerWindow] = []

        for entry in entries:
            if LogMatcher.is_excluded(entry, config):
                continue

            if not LogMatcher.is_trigger(entry, config):
                continue

            trigger_windows.append(
                TriggerWindow(
                    file_path=entry.file_path,
                    start_timestamp=entry.timestamp,
                    end_timestamp=entry.timestamp
                    + timedelta(seconds=config.duration_seconds),
                    trigger_line=entry.raw_line,
                )
            )

        return trigger_windows

    @staticmethod
    def _get_match_reason(
        entry: LogEntry,
        config: ExtractionConfig,
        trigger_windows: list[TriggerWindow],
    ) -> str | None:
        if LogMatcher.is_trigger(entry, config):
            return "trigger"

        if LogMatcher.is_included(entry, config):
            return "include"

        if LogExtractor._is_inside_trigger_window(entry, trigger_windows):
            return "window"

        return None

    @staticmethod
    def _is_inside_trigger_window(
        entry: LogEntry,
        trigger_windows: list[TriggerWindow],
    ) -> bool:
        for window in trigger_windows:
            if entry.file_path != window.file_path:
                continue

            if window.start_timestamp <= entry.timestamp <= window.end_timestamp:
                return True

        return False
