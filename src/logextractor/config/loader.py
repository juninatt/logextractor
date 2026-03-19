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
    TimeRangeConfig,
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
        time_range_data = data[keys.TIME_RANGE]

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
            strip_common_log_prefix=output_settings_data.get(
                keys.STRIP_COMMON_LOG_PREFIX,
                False,
            ),
        )

        time_range = TimeRangeConfig(
            enabled=time_range_data["enabled"],
            timezone=time_range_data["timezone"],
            start_time=time_range_data.get("start_time"),
            end_time=time_range_data.get("end_time"),
        )

        filter_config = FilterConfig(
            rules=ConfigLoader._parse_rules(filtering_data[keys.RULES]),
        )

        return AppConfig(
            profile=profile,
            input_settings=input_config,
            output_settings=output_config,
            filtering=filter_config,
            time_range=time_range,
        )

    @staticmethod
    def _parse_rules(rules_data: list[dict]) -> list[FilterRule]:
        """
        Convert raw rule dictionaries from JSON into FilterRule objects.
        """
        return [
            FilterRule(
                rule_name=rule_data[keys.RULE_NAME],
                match_log_levels=rule_data.get(keys.MATCH_LOG_LEVELS, []),
                match_sources=rule_data.get(keys.MATCH_SOURCES),
                match_logger_name_contains=rule_data.get(
                    keys.MATCH_LOGGER_NAME_CONTAINS
                ),
                match_message_contains=rule_data.get(keys.MATCH_MESSAGE_CONTAINS),
                include_context_before_seconds=rule_data.get(
                    keys.INCLUDE_CONTEXT_BEFORE_SECONDS,
                    0,
                ),
                include_context_after_seconds=rule_data.get(
                    keys.INCLUDE_CONTEXT_AFTER_SECONDS,
                    0,
                ),
            )
            for rule_data in rules_data
        ]
