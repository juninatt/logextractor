"""
Parse supported log formats into structured LogEntry objects.

This module converts raw log lines into typed log entries that can be used by
the filtering and extraction pipeline. It currently supports syslog-style lines
with optional embedded application log formats.
"""

import re
from datetime import datetime
from typing import Optional

from logextractor.domain.models import LogEntry


SYSLOG_PATTERN = re.compile(
    r"^(?P<month>[A-Z][a-z]{2})\s+"
    r"(?P<day>\d{1,2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"(?P<host>\S+)\s+"
    r"(?P<source>[^\[:]+)(?:\[(?P<pid>\d+)])?:\s*"
    r"(?P<content>.*)$"
)

APP_LOG_PATTERN = re.compile(
    r"^(?P<app_time>\d{2}:\d{2}:\d{2}[.,]\d{3})\s+"
    r"\[(?P<thread>[^\]]+)]\s+"
    r"(?P<level>TRACE|DEBUG|INFO|WARN|ERROR|FATAL)\s+"
    r"(?P<logger>.+?)\s+-\s+"
    r"(?P<message>.*)$"
)

LOGBACK_PATTERN = re.compile(
    r"^(?P<app_time>\d{2}:\d{2}:\d{2}[.,]\d{3})\s+\|-(?P<level>TRACE|DEBUG|INFO|WARN|ERROR|FATAL)\s+in\s+"
    r"(?P<message>.*)$"
)

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


class LogParser:
    """
    Parse raw log lines into structured LogEntry objects.
    """

    def __init__(self, year: int) -> None:
        self._year = year

    def parse_line(self, line: str) -> Optional[LogEntry]:
        """
        Parse a raw log line into a LogEntry instance.

        Returns None if the line does not match the supported syslog-based
        format. If only the outer syslog structure is recognized, the entry
        is still returned with level set to UNKNOWN.
        """
        raw_line = line.rstrip("\n")

        syslog_match = SYSLOG_PATTERN.match(raw_line)
        if not syslog_match:
            return None

        timestamp = self._parse_syslog_timestamp(
            month=syslog_match.group("month"),
            day=syslog_match.group("day"),
            time_value=syslog_match.group("time"),
        )

        source = syslog_match.group("source")
        content = syslog_match.group("content")

        app_match = APP_LOG_PATTERN.match(content)
        if app_match:
            return LogEntry(
                timestamp=timestamp,
                level=app_match.group("level"),
                source=source,
                logger=app_match.group("logger"),
                message=app_match.group("message"),
                raw_line=raw_line,
            )

        logback_match = LOGBACK_PATTERN.match(content)
        if logback_match:
            return LogEntry(
                timestamp=timestamp,
                level=logback_match.group("level"),
                source=source,
                logger=None,
                message=logback_match.group("message"),
                raw_line=raw_line,
            )

        return LogEntry(
            timestamp=timestamp,
            level="UNKNOWN",
            source=source,
            logger=None,
            message=content,
            raw_line=raw_line,
        )

    def _parse_syslog_timestamp(self, month: str, day: str, time_value: str) -> datetime:
        """
        Convert syslog date components into a datetime instance.

        Syslog timestamps do not include the year, so the parser uses the year
        provided when the LogParser instance is created.
        """
        month_number = MONTHS[month]
        hour, minute, second = map(int, time_value.split(":"))

        return datetime(
            year=self._year,
            month=month_number,
            day=int(day),
            hour=hour,
            minute=minute,
            second=second,
        )
