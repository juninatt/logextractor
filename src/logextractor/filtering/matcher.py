"""
Evaluate parsed log entries against filtering rules and exclusion settings.

This module contains the rule matching logic used during log extraction.
It determines whether a log entry matches a rule or should be excluded
based on global filter settings.
"""

from logextractor.domain.models import FilterConfig, FilterRule, LogEntry


class LogMatcher:
    """
    Apply filtering rules and exclusion checks to parsed log entries.
    """

    @staticmethod
    def matches_rule(entry: LogEntry, rule: FilterRule) -> bool:
        """
        Return True if the log entry satisfies the given rule.

        Each rule field is optional. If a rule field is not defined, it does
        not restrict the match condition.
        """
        if rule.match_log_levels and entry.level not in rule.match_log_levels:
            return False

        if rule.match_sources and (
            entry.source is None or entry.source not in rule.match_sources
        ):
            return False

        if rule.match_logger_name_contains and not LogMatcher._contains_any(
            entry.logger, rule.match_logger_name_contains
        ):
            return False

        if rule.match_message_contains and not LogMatcher._contains_any(
            entry.message, rule.match_message_contains
        ):
            return False

        return True

    @staticmethod
    def is_excluded(entry: LogEntry, filter_config: FilterConfig) -> bool:
        """
        Return True if the log entry should be excluded by global filter settings.
        """
        if entry.level in filter_config.exclude_log_levels:
            return True

        if entry.source and entry.source in filter_config.exclude_sources:
            return True

        if LogMatcher._contains_any(
            entry.message, filter_config.exclude_messages_containing
        ):
            return True

        return False

    @staticmethod
    def _contains_any(value: str | None, expected_fragments: list[str]) -> bool:
        """
        Return True if the value contains any of the specified fragments.
        """
        if value is None:
            return False

        return any(fragment in value for fragment in expected_fragments)
