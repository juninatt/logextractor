from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class ExtractionConfig:
    include_keywords: list[str]
    trigger_keywords: list[str]
    exclude_keywords: list[str]
    duration_seconds: int


@dataclass(frozen=True)
class LogEntry:
    timestamp: datetime
    file_path: Path
    line_number: int
    raw_line: str


@dataclass(frozen=True)
class TriggerWindow:
    file_path: Path
    start_timestamp: datetime
    end_timestamp: datetime
    trigger_line: str


@dataclass(frozen=True)
class MatchedLine:
    file_path: Path
    line_number: int
    timestamp: datetime
    raw_line: str
    reason: str


@dataclass(frozen=True)
class ExtractionResult:
    total_files_read: int
    total_lines_read: int
    total_lines_matched: int
    matched_lines: list[MatchedLine]
