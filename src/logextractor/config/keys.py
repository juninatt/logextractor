"""
JSON configuration keys used when loading configuration profiles.

Centralizing these keys avoids scattering literal strings across the
configuration loader and simplifies future schema changes.
"""

# Profile metadata

PROFILE = "profile"
PROFILE_NAME = "name"
PROFILE_DESCRIPTION = "description"

# Input configuration

INPUT_SETTINGS = "input_settings"
LOG_TIMESTAMP_FORMAT = "log_timestamp_format"
FILE_ENCODING = "file_encoding"

# Output configuration

OUTPUT_SETTINGS = "output_settings"
OUTPUT_FILE_PATH = "output_file_path"
STRIP_COMMON_LOG_PREFIX = "strip_common_log_prefix"

# Time range

TIME_RANGE = "time_range"
TIMEZONE = "timezone"
START_TIME = "start_time"
END_TIME = "end_time"

# Filtering configuration

FILTERING = "filtering"
RULES = "rules"

RULE_NAME = "rule_name"
MATCH_LOG_LEVELS = "match_log_levels"
MATCH_SOURCES = "match_sources"
MATCH_LOGGER_NAME_CONTAINS = "match_logger_name_contains"
MATCH_MESSAGE_CONTAINS = "match_message_contains"
INCLUDE_CONTEXT_BEFORE_SECONDS = "include_context_before_seconds"
INCLUDE_CONTEXT_AFTER_SECONDS = "include_context_after_seconds"