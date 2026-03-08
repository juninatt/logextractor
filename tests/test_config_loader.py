from pathlib import Path

import pytest

from logextractor.config.loader import ConfigLoader


PROFILE_PATHS = [
    Path("config/error-focused.json"),
    Path("config/warning-focused.json"),
    Path("config/source-focused.json"),
    Path("config/message-patterns.json"),
    Path("config/noise-reduction.json"),
    Path("config/broad-analysis.json"),
]


@pytest.mark.parametrize("config_path", PROFILE_PATHS)
def test_load_configuration_profile(config_path: Path) -> None:
    config = ConfigLoader.load(config_path)

    assert config.profile.name
    assert config.profile.description
    assert config.input_settings.log_timestamp_format == "syslog"
    assert config.input_settings.file_encoding == "utf-8"
    assert config.output_settings.output_file_path
    assert isinstance(config.filtering.rules, list)
    assert config.statistics.enable_statistics is True


@pytest.mark.parametrize("config_path", PROFILE_PATHS)
def test_each_profile_contains_at_least_one_rule(config_path: Path) -> None:
    config = ConfigLoader.load(config_path)

    assert len(config.filtering.rules) > 0


@pytest.mark.parametrize("config_path", PROFILE_PATHS)
def test_each_rule_has_a_name_and_log_levels(config_path: Path) -> None:
    config = ConfigLoader.load(config_path)

    for rule in config.filtering.rules:
        assert rule.rule_name
        assert len(rule.match_log_levels) > 0


def test_error_focused_profile_has_expected_core_values() -> None:
    config = ConfigLoader.load(Path("config/error-focused.json"))

    assert config.profile.name == "error-focused"
    assert config.output_settings.output_file_path == "output/error-focused.txt"
    assert config.filtering.rules[0].rule_name == "error_events"
    assert config.filtering.rules[0].match_log_levels == ["ERROR"]
