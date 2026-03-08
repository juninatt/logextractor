from datetime import datetime

from logextractor.domain.models import FilterConfig, FilterRule, LogEntry
from logextractor.filtering.matcher import LogMatcher


def test_matches_rule_by_level_and_process() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        level="ERROR",
        process="app-service",
        logger="com.example.service.EventProcessor",
        message="Failed to process event",
        raw_line="raw log line",
    )

    rule = FilterRule(
        name="error_events",
        levels=["ERROR"],
        processes=["app-service"],
        logger_contains_any=None,
        message_contains_any=None,
        context_before_seconds=10,
        context_after_seconds=20,
    )

    assert LogMatcher.matches_rule(entry, rule) is True


def test_does_not_match_when_level_differs() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        level="INFO",
        process="app-service",
        logger="com.example.service.EventProcessor",
        message="Processed event successfully",
        raw_line="raw log line",
    )

    rule = FilterRule(
        name="error_events",
        levels=["ERROR"],
        processes=["app-service"],
        logger_contains_any=None,
        message_contains_any=None,
        context_before_seconds=10,
        context_after_seconds=20,
    )

    assert LogMatcher.matches_rule(entry, rule) is False


def test_matches_rule_by_message_fragment() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        level="WARN",
        process="worker-service",
        logger="com.example.worker.JobRunner",
        message="Connection timeout while calling upstream service",
        raw_line="raw log line",
    )

    rule = FilterRule(
        name="timeouts",
        levels=["WARN", "ERROR"],
        processes=None,
        logger_contains_any=None,
        message_contains_any=["timeout", "connection lost"],
        context_before_seconds=5,
        context_after_seconds=5,
    )

    assert LogMatcher.matches_rule(entry, rule) is True


def test_excludes_entry_by_global_level() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        level="DEBUG",
        process="worker-service",
        logger="com.example.worker.JobRunner",
        message="Polling for updates",
        raw_line="raw log line",
    )

    filter_config = FilterConfig(
        rules=[],
        global_exclude_levels=["DEBUG"],
        global_exclude_processes=[],
        global_exclude_message_contains=[],
    )

    assert LogMatcher.is_excluded(entry, filter_config) is True