from pathlib import Path

from logextractor.config.loader import ConfigLoader


def test_load_example_config() -> None:
    config = ConfigLoader.load(Path("config/example-config.json"))

    assert config.input.timestamp_format == "syslog"
    assert config.input.encoding == "utf-8"
    assert config.output.file_path == "output/filtered_log.txt"
    assert config.statistics.enabled is True


def test_load_rules() -> None:
    config = ConfigLoader.load(Path("config/example-config.json"))

    assert isinstance(config.filters.rules, list)
