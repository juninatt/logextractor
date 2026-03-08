from datetime import datetime

from logextractor.domain.models import FilterConfig, FilterRule, LogEntry
from logextractor.filtering.matcher import LogMatcher


def test_matches_rule_by_level_and_source() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        level="ERROR",
        source="app-service",
        logger="com.example.service.EventProcessor",
        message="Failed to process event",
        raw_line="raw log line",
    )

    rule = FilterRule(
        rule_name="error_events",
        match_log_levels=["ERROR"],
        match_sources=["app-service"],
        match_logger_name_contains=None,
        match_message_contains=None,
        include_context_before_seconds=10,
        include_context_after_seconds=20,
    )

    assert LogMatcher.matches_rule(entry, rule) is True


def test_does_not_match_when_level_differs() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        level="INFO",
        source="app-service",
        logger="com.example.service.EventProcessor",
        message="Processed event successfully",
        raw_line="raw log line",
    )

    rule = FilterRule(
        rule_name="error_events",
        match_log_levels=["ERROR"],
        match_sources=["app-service"],
        match_logger_name_contains=None,
        match_message_contains=None,
        include_context_before_seconds=10,
        include_context_after_seconds=20,
    )

    assert LogMatcher.matches_rule(entry, rule) is False


def test_matches_rule_by_message_fragment() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        level="WARN",
        source="worker-service",
        logger="com.example.worker.JobRunner",
        message="Connection timeout while calling upstream service",
        raw_line="raw log line",
    )

    rule = FilterRule(
        rule_name="timeouts",
        match_log_levels=["WARN", "ERROR"],
        match_sources=None,
        match_logger_name_contains=None,
        match_message_contains=["timeout", "connection lost"],
        include_context_before_seconds=5,
        include_context_after_seconds=5,
    )

    assert LogMatcher.matches_rule(entry, rule) is True


def test_excludes_entry_by_global_level() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        level="DEBUG",
        source="worker-service",
        logger="com.example.worker.JobRunner",
        message="Polling for updates",
        raw_line="raw log line",
    )

    filter_config = FilterConfig(
        rules=[],
        exclude_log_levels=["DEBUG"],
        exclude_sources=[],
        exclude_messages_containing=[],
    )

    assert LogMatcher.is_excluded(entry, filter_config) is True
