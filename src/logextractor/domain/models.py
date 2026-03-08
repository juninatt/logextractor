from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class LogEntry:
    """Represents a single parsed log entry."""

    timestamp: datetime
    level: str
    process: Optional[str]
    logger: Optional[str]
    message: str
    raw_line: str


@dataclass(frozen=True)
class FilterRule:
    """Defines a rule used to match log entries."""

    name: str
    levels: list[str]
    processes: list[str] | None
    logger_contains_any: list[str] | None
    message_contains_any: list[str] | None
    context_before_seconds: int
    context_after_seconds: int


@dataclass(frozen=True)
class InputConfig:
    """Defines how the input log file should be read."""

    timestamp_format: str
    encoding: str


@dataclass(frozen=True)
class OutputConfig:
    """Defines how extracted results should be written."""

    file_path: str
    include_summary: bool
    include_statistics: bool
    verbosity: str


@dataclass(frozen=True)
class StatisticsConfig:
    """Defines which statistics should be collected and written."""

    enabled: bool
    count_by_level: bool
    count_by_rule: bool
    count_by_process: bool
    detect_repetitive_messages: bool
    top_repetitive_message_limit: int


@dataclass(frozen=True)
class FilterConfig:
    """Groups all filtering rules and global exclusions."""

    rules: list[FilterRule]
    global_exclude_levels: list[str]
    global_exclude_processes: list[str]
    global_exclude_message_contains: list[str]


@dataclass(frozen=True)
class AppConfig:
    """Root configuration object for the application."""

    input: InputConfig
    output: OutputConfig
    filters: FilterConfig
    statistics: StatisticsConfig