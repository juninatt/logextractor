import re
from datetime import datetime
from pathlib import Path

from logextractor.domain.models import LogEntry


ISO_TIMESTAMP_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2}))"
)

SYSLOG_TIMESTAMP_PATTERN = re.compile(
    r"^(?P<month>[A-Z][a-z]{2})\s+"
    r"(?P<day>\d{1,2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})"
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

    def __init__(self, year: int) -> None:
        self._year = year

    def parse_line(
        self,
        line: str,
        file_path: Path,
        line_number: int,
    ) -> LogEntry | None:
        raw_line = line.rstrip("\n")

        timestamp = self._parse_iso_timestamp(raw_line)

        if timestamp is None:
            timestamp = self._parse_syslog_timestamp(raw_line)

        if timestamp is None:
            return None

        return LogEntry(
            timestamp=timestamp,
            file_path=file_path,
            line_number=line_number,
            raw_line=raw_line,
        )

    def _parse_iso_timestamp(self, raw_line: str) -> datetime | None:
        match = ISO_TIMESTAMP_PATTERN.match(raw_line)

        if match is None:
            return None

        timestamp_value = match.group("timestamp")

        if timestamp_value.endswith("Z"):
            timestamp_value = timestamp_value.replace("Z", "+00:00")

        if re.search(r"[+-]\d{4}$", timestamp_value):
            timestamp_value = f"{timestamp_value[:-2]}:{timestamp_value[-2:]}"

        return datetime.fromisoformat(timestamp_value)

    def _parse_syslog_timestamp(self, raw_line: str) -> datetime | None:
        match = SYSLOG_TIMESTAMP_PATTERN.match(raw_line)

        if match is None:
            return None

        month_number = MONTHS[match.group("month")]
        hour, minute, second = map(int, match.group("time").split(":"))

        return datetime(
            year=self._year,
            month=month_number,
            day=int(match.group("day")),
            hour=hour,
            minute=minute,
            second=second,
        )
