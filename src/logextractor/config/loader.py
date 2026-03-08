"""
Load JSON configuration profiles and map them to domain models.

This module translates the external JSON configuration schema into the
internal typed configuration model used by the application. Changes to the
configuration schema should normally only require updates in this module.
"""

import json
from pathlib import Path

from logextractor.config import keys
from logextractor.domain.models import (
    AppConfig,
    FilterConfig,
    FilterRule,
    InputConfig,
    OutputConfig,
    ProfileConfig,
    StatisticsConfig,
)


class ConfigLoader:
    """
    Load application configuration from a JSON file into typed domain objects.
    """


    @staticmethod
    def load(config_path: Path) -> AppConfig:
        """
        Load a configuration profile from disk and convert it to an AppConfig instance.
        """
        with config_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        profile_data = data[keys.PROFILE]
        input_settings_data = data[keys.INPUT_SETTINGS]
        output_settings_data = data[keys.OUTPUT_SETTINGS]
        filtering_data = data[keys.FILTERING]
        statistics_data = data[keys.STATISTICS]

        profile = ProfileConfig(
            name=profile_data[keys.PROFILE_NAME],
            description=profile_data[keys.PROFILE_DESCRIPTION],
        )

        input_config = InputConfig(
            log_timestamp_format=input_settings_data[keys.LOG_TIMESTAMP_FORMAT],
            file_encoding=input_settings_data[keys.FILE_ENCODING],
        )

        output_config = OutputConfig(
            output_file_path=output_settings_data[keys.OUTPUT_FILE_PATH],
            write_run_summary=output_settings_data[keys.WRITE_RUN_SUMMARY],
            write_statistics=output_settings_data[keys.WRITE_STATISTICS],
            output_verbosity_level=output_settings_data[keys.OUTPUT_VERBOSITY_LEVEL],
        )

        rules = ConfigLoader._parse_rules(filtering_data[keys.RULES])

        filter_config = FilterConfig(
            rules=rules,
            exclude_log_levels=filtering_data.get(keys.EXCLUDE_LOG_LEVELS, []),
            exclude_sources=filtering_data.get(keys.EXCLUDE_SOURCES, []),
            exclude_messages_containing=filtering_data.get(
                keys.EXCLUDE_MESSAGES_CONTAINING, []
            ),
        )

        statistics_config = StatisticsConfig(
            enable_statistics=statistics_data[keys.ENABLE_STATISTICS],
            count_entries_by_level=statistics_data[keys.COUNT_ENTRIES_BY_LEVEL],
            count_entries_by_rule=statistics_data[keys.COUNT_ENTRIES_BY_RULE],
            count_entries_by_source=statistics_data[keys.COUNT_ENTRIES_BY_SOURCE],
            detect_repeated_messages=statistics_data[keys.DETECT_REPEATED_MESSAGES],
            top_repeated_message_limit=statistics_data[keys.TOP_REPEATED_MESSAGE_LIMIT],
        )

        return AppConfig(
            profile=profile,
            input_settings=input_config,
            output_settings=output_config,
            filtering=filter_config,
            statistics=statistics_config,
        )

    @staticmethod
    def _parse_rules(rules_data: list[dict]) -> list[FilterRule]:
        """
        Convert raw rule dictionaries from JSON into FilterRule objects.
        """
        rules: list[FilterRule] = []

        for rule_data in rules_data:
            rules.append(
                FilterRule(
                    rule_name=rule_data[keys.RULE_NAME],
                    match_log_levels=rule_data.get(keys.MATCH_LOG_LEVELS, []),
                    match_sources=rule_data.get(keys.MATCH_SOURCES),
                    match_logger_name_contains=rule_data.get(
                        keys.MATCH_LOGGER_NAME_CONTAINS
                    ),
                    match_message_contains=rule_data.get(keys.MATCH_MESSAGE_CONTAINS),
                    include_context_before_seconds=rule_data.get(
                        keys.INCLUDE_CONTEXT_BEFORE_SECONDS, 0
                    ),
                    include_context_after_seconds=rule_data.get(
                        keys.INCLUDE_CONTEXT_AFTER_SECONDS, 0
                    ),
                )
            )

        return rules
