import re

from logextractor.domain.models import ExtractionConfig, LogEntry


class LogMatcher:

    @staticmethod
    def is_excluded(entry: LogEntry, config: ExtractionConfig) -> bool:
        return LogMatcher._contains_any_keyword(entry.raw_line, config.exclude_keywords)

    @staticmethod
    def is_included(entry: LogEntry, config: ExtractionConfig) -> bool:
        return LogMatcher._contains_any_keyword(entry.raw_line, config.include_keywords)

    @staticmethod
    def is_trigger(entry: LogEntry, config: ExtractionConfig) -> bool:
        return LogMatcher._contains_any_keyword(entry.raw_line, config.trigger_keywords)

    @staticmethod
    def _contains_any_keyword(value: str, keywords: list[str]) -> bool:
        return any(
            LogMatcher._contains_keyword(value, keyword)
            for keyword in keywords
            if keyword
        )

    @staticmethod
    def _contains_keyword(value: str, keyword: str) -> bool:
        pattern = rf"(?<![A-Za-z0-9_]){re.escape(keyword)}(?![A-Za-z0-9_])"
        return re.search(pattern, value) is not None