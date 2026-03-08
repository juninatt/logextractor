from logextractor.domain.models import FilterConfig, FilterRule, LogEntry


class LogMatcher:
    """Matches parsed log entries against filter rules and exclusions."""

    @staticmethod
    def matches_rule(entry: LogEntry, rule: FilterRule) -> bool:
        if rule.levels and entry.level not in rule.levels:
            return False

        if rule.processes and (entry.process is None or entry.process not in rule.processes):
            return False

        if rule.logger_contains_any and not LogMatcher._contains_any(
            entry.logger, rule.logger_contains_any
        ):
            return False

        if rule.message_contains_any and not LogMatcher._contains_any(
            entry.message, rule.message_contains_any
        ):
            return False

        return True

    @staticmethod
    def is_excluded(entry: LogEntry, filter_config: FilterConfig) -> bool:
        if entry.level in filter_config.global_exclude_levels:
            return True

        if entry.process and entry.process in filter_config.global_exclude_processes:
            return True

        if LogMatcher._contains_any(
            entry.message, filter_config.global_exclude_message_contains
        ):
            return True

        return False

    @staticmethod
    def _contains_any(value: str | None, expected_fragments: list[str]) -> bool:
        if value is None:
            return False

        return any(fragment in value for fragment in expected_fragments)