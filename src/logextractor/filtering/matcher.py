"""
Evaluate parsed log entries against filtering rules.

This module contains the rule matching logic used during log extraction.
It determines whether a log entry matches a rule.
"""

from logextractor.domain.models import FilterRule, LogEntry


class LogMatcher:
    """
    Apply filtering rules to parsed log entries.
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
            entry.logger,
            rule.match_logger_name_contains,
        ):
            return False

        if rule.match_message_contains and not LogMatcher._contains_any(
            entry.message,
            rule.match_message_contains,
        ):
            return False

        return True

    @staticmethod
    def _contains_any(value: str | None, expected_fragments: list[str]) -> bool:
        """
        Return True if the value contains any of the specified fragments.
        """
        if value is None:
            return False

        return any(fragment in value for fragment in expected_fragments)
