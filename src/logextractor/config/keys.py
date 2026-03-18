"""
JSON configuration keys used when loading configuration profiles.

Centralizing these keys avoids scattering literal strings across the
configuration loader and simplifies future schema changes.
"""

# Profile metadata

PROFILE = "profile"  # Root section describing the configuration profile
PROFILE_NAME = "name"  # Human-readable name of the profile
PROFILE_DESCRIPTION = "description"  # Description explaining the profile purpose

# Input configuration

INPUT_SETTINGS = "input_settings"  # Root section describing how log files are read
LOG_TIMESTAMP_FORMAT = "log_timestamp_format"  # Timestamp format used in the log file
FILE_ENCODING = "file_encoding"  # Character encoding of the log file

# Output configuration

OUTPUT_SETTINGS = "output_settings"  # Root section describing how results are written
OUTPUT_FILE_PATH = "output_file_path"  # Path to the output file
WRITE_RUN_SUMMARY = "write_run_summary"  # Whether a summary of the run should be written
WRITE_STATISTICS = "write_statistics"  # Whether statistics should be included
OUTPUT_VERBOSITY_LEVEL = "output_verbosity_level"  # Controls how much output detail is written
STRIP_COMMON_LOG_PREFIX = "strip_common_log_prefix"

# Time restraints

TIME_RANGE = "time_range"  # Root section describing optional time filtering
TIMEZONE = "timezone"  # Time zone used for configured time values
START_TIME = "start_time"  # Lower inclusive time boundary in HH:MM:SS
END_TIME = "end_time"  # Upper inclusive time boundary in HH:MM:SS

# Filtering configuration

FILTERING = "filtering"  # Root section describing filtering rules
RULES = "rules"  # List of filtering rules

RULE_NAME = "rule_name"  # Name of the rule
MATCH_LOG_LEVELS = "match_log_levels"  # Log levels that should match the rule
MATCH_SOURCES = "match_sources"  # Syslog sources that should match
MATCH_LOGGER_NAME_CONTAINS = "match_logger_name_contains"  # Logger name fragments that should match
MATCH_MESSAGE_CONTAINS = "match_message_contains"  # Message fragments that should match
INCLUDE_CONTEXT_BEFORE_SECONDS = "include_context_before_seconds"  # Context seconds before a match
INCLUDE_CONTEXT_AFTER_SECONDS = "include_context_after_seconds"  # Context seconds after a match

# Global exclusions

EXCLUDE_LOG_LEVELS = "exclude_log_levels"  # Log levels to exclude globally
EXCLUDE_SOURCES = "exclude_sources"  # Sources to exclude globally
EXCLUDE_MESSAGES_CONTAINING = "exclude_messages_containing"  # Message fragments to exclude

# Statistics configuration

STATISTICS = "statistics"  # Root section describing statistics settings
ENABLE_STATISTICS = "enable_statistics"  # Whether statistics collection is enabled
COUNT_ENTRIES_BY_LEVEL = "count_entries_by_level"  # Count entries grouped by log level
COUNT_ENTRIES_BY_RULE = "count_entries_by_rule"  # Count matches grouped by rule
COUNT_ENTRIES_BY_SOURCE = "count_entries_by_source"  # Count entries grouped by source
DETECT_REPEATED_MESSAGES = "detect_repeated_messages"  # Detect repeated log messages
TOP_REPEATED_MESSAGE_LIMIT = "top_repeated_message_limit"  # Maximum repeated messages to report