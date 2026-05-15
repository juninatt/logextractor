from datetime import datetime
from pathlib import Path

from logextractor.domain.models import ExtractionConfig, LogEntry
from logextractor.filtering.matcher import LogMatcher


def test_is_included_when_line_contains_keyword_as_standalone_term() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        file_path=Path("logs/app.log"),
        line_number=10,
        raw_line="2026-02-26T13:09:01+00:00 app: error occurred while processing request",
    )

    config = ExtractionConfig(
        include_keywords=["error"],
        trigger_keywords=[],
        exclude_keywords=[],
        duration_seconds=30,
    )

    assert LogMatcher.is_included(entry, config) is True


def test_is_not_included_when_keyword_only_exists_as_part_of_longer_word() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        file_path=Path("logs/app.log"),
        line_number=11,
        raw_line='2026-02-26T13:09:01+00:00 app: Received validator errors:212',
    )

    config = ExtractionConfig(
        include_keywords=["error"],
        trigger_keywords=[],
        exclude_keywords=[],
        duration_seconds=30,
    )

    assert LogMatcher.is_included(entry, config) is False


def test_is_trigger_when_line_contains_trigger_keyword() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        file_path=Path("logs/app.log"),
        line_number=20,
        raw_line="2026-02-26T13:09:01+00:00 app: service restart initiated",
    )

    config = ExtractionConfig(
        include_keywords=[],
        trigger_keywords=["restart"],
        exclude_keywords=[],
        duration_seconds=60,
    )

    assert LogMatcher.is_trigger(entry, config) is True


def test_is_excluded_when_line_contains_exclude_keyword() -> None:
    entry = LogEntry(
        timestamp=datetime(2026, 2, 26, 13, 9, 1),
        file_path=Path("logs/app.log"),
        line_number=30,
        raw_line="2026-02-26T13:09:01+00:00 app: healthcheck passed",
    )

    config = ExtractionConfig(
        include_keywords=[],
        trigger_keywords=[],
        exclude_keywords=["healthcheck"],
        duration_seconds=0,
    )

    assert LogMatcher.is_excluded(entry, config) is True