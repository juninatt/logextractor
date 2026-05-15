from pathlib import Path

from logextractor.parsing.log_parser import LogParser


def test_parse_iso_log_line_with_offset() -> None:
    parser = LogParser(year=2026)

    line = (
        "2026-03-21T23:30:58.145356+00:00 "
        "RIDANGO-DV25-122510727 kernel: KASLR disabled due to lack of seed"
    )

    entry = parser.parse_line(
        line=line,
        file_path=Path("logs/device.log"),
        line_number=12,
    )

    assert entry is not None
    assert entry.timestamp.year == 2026
    assert entry.timestamp.month == 3
    assert entry.timestamp.day == 21
    assert entry.file_path == Path("logs/device.log")
    assert entry.line_number == 12
    assert entry.raw_line == line


def test_parse_iso_log_line_with_compact_offset() -> None:
    parser = LogParser(year=2026)

    line = (
        "2026-04-20T00:00:00.645535+0000 "
        "RIDANGO-DV25-122510727 kernel: Boot complete"
    )

    entry = parser.parse_line(
        line=line,
        file_path=Path("logs/device.log"),
        line_number=1,
    )

    assert entry is not None
    assert entry.timestamp.year == 2026
    assert entry.timestamp.month == 4
    assert entry.timestamp.day == 20
    assert entry.file_path == Path("logs/device.log")
    assert entry.line_number == 1
    assert entry.raw_line == line


def test_parse_syslog_line() -> None:
    parser = LogParser(year=2026)

    line = "Feb 26 12:29:42 demo-host systemd-journald[255]: Forwarding to syslog missed 8 messages."

    entry = parser.parse_line(
        line=line,
        file_path=Path("logs/system.log"),
        line_number=44,
    )

    assert entry is not None
    assert entry.timestamp.year == 2026
    assert entry.timestamp.month == 2
    assert entry.timestamp.day == 26
    assert entry.file_path == Path("logs/system.log")
    assert entry.line_number == 44
    assert entry.raw_line == line


def test_return_none_for_unparseable_line() -> None:
    parser = LogParser(year=2026)

    entry = parser.parse_line(
        line="not a valid log line",
        file_path=Path("logs/system.log"),
        line_number=99,
    )

    assert entry is None