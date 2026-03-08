from logextractor.parsing.log_parser import LogParser


def test_parse_application_log_line() -> None:
    parser = LogParser(year=2026)

    line = (
        "Feb 26 13:09:01 demo-host app-service[2296]: "
        "13:09:01.146 [MAIN] ERROR com.example.service.EventProcessor - "
        "Failed to process event"
    )

    entry = parser.parse_line(line)

    assert entry is not None
    assert entry.timestamp.year == 2026
    assert entry.timestamp.month == 2
    assert entry.timestamp.day == 26
    assert entry.source == "app-service"
    assert entry.level == "ERROR"
    assert entry.logger == "com.example.service.EventProcessor"
    assert entry.message == "Failed to process event"


def test_parse_syslog_only_line() -> None:
    parser = LogParser(year=2026)

    line = (
        "Feb 26 12:29:42 demo-host systemd-journald[255]: "
        "Forwarding to syslog missed 8 messages."
    )

    entry = parser.parse_line(line)

    assert entry is not None
    assert entry.source == "systemd-journald"
    assert entry.level == "UNKNOWN"
    assert entry.logger is None
    assert entry.message == "Forwarding to syslog missed 8 messages."


def test_return_none_for_unparseable_line() -> None:
    parser = LogParser(year=2026)

    entry = parser.parse_line("not a valid log line")

    assert entry is None
