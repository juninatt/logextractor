"""
Application-wide constants.

These values define shared defaults used across multiple parts of the
application, such as default directories and runtime values.
"""

from datetime import datetime
from pathlib import Path

DEFAULT_CONFIG_DIRECTORY = Path("config")
DEFAULT_OUTPUT_DIRECTORY = Path("output")
DEFAULT_CURRENT_YEAR = datetime.now().year
DEFAULT_FILE_ENCODING = "utf-8"
DEFAULT_LOG_FILE_EXTENSION = ".log"