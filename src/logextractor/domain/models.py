from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProfileConfig:
    """Describes a named configuration profile and its intended purpose."""

    name: str
    description: str


@dataclass(frozen=True)
class LogEntry:
    """Represents a single parsed log entry."""

    timestamp: datetime
    level: str
    source: str | None
    logger: str | None
    message: str
    raw_line: str


@dataclass(frozen=True)
class FilterRule:
    """Defines one rule used to match relevant log entries."""

    rule_name: str
    match_log_levels: list[str]
    match_sources: list[str] | None
    match_logger_name_contains: list[str] | None
    match_message_contains: list[str] | None
    include_context_before_seconds: int
    include_context_after_seconds: int


@dataclass(frozen=True)
class InputConfig:
    """Defines how the input log file should be read."""

    log_timestamp_format: str
    file_encoding: str


@dataclass(frozen=True)
class OutputConfig:
    """Defines how extracted results should be written."""

    output_file_path: str
    strip_common_log_prefix: bool


@dataclass(frozen=True)
class FilterConfig:
    """Groups filtering rules."""

    rules: list[FilterRule]


@dataclass(frozen=True)
class TimeRangeConfig:
    """Defines an optional UTC time range used to restrict log analysis."""

    enabled: bool
    timezone: str
    start_time: str | None
    end_time: str | None


@dataclass(frozen=True)
class AppConfig:
    """Represents the complete application configuration loaded from a profile."""

    profile: ProfileConfig
    input_settings: InputConfig
    output_settings: OutputConfig
    filtering: FilterConfig
    time_range: TimeRangeConfig


@dataclass(frozen=True)
class MatchTrigger:
    """Represents a rule match that triggered a sequence."""

    rule_name: str
    timestamp: datetime
    source: str | None
    logger: str | None
    message: str


@dataclass(frozen=True)
class MatchedSequence:
    """Represents a merged time window triggered by one or more rule matches."""

    start_timestamp: datetime
    end_timestamp: datetime
    triggers: list[MatchTrigger]
    entries: list[LogEntry]


@dataclass(frozen=True)
class ExtractionResult:
    """Represents the result produced by processing a log file."""

    input_file: str
    source_identifier: str | None
    total_lines_read: int
    total_lines_parsed: int
    total_lines_matched: int
    sequences: list[MatchedSequence]