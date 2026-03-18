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
    write_run_summary: bool
    write_statistics: bool
    output_verbosity_level: str
    strip_common_log_prefix: bool


@dataclass(frozen=True)
class StatisticsConfig:
    """Defines which statistics should be collected and written."""

    enable_statistics: bool
    count_entries_by_level: bool
    count_entries_by_rule: bool
    count_entries_by_source: bool
    detect_repeated_messages: bool
    top_repeated_message_limit: int


@dataclass(frozen=True)
class FilterConfig:
    """Groups filtering rules and global exclusion settings."""

    rules: list[FilterRule]
    exclude_log_levels: list[str]
    exclude_sources: list[str]
    exclude_messages_containing: list[str]


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
    statistics: StatisticsConfig
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
