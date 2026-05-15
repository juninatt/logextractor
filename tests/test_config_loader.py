import json
from pathlib import Path

from logextractor.config.loader import ConfigLoader


def test_load_extraction_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "include_keywords": ["error", "timeout"],
                "trigger_keywords": ["restart"],
                "exclude_keywords": ["healthcheck"],
                "duration_seconds": 30,
            }
        ),
        encoding="utf-8",
    )

    config = ConfigLoader.load(config_path)

    assert config.include_keywords == ["error", "timeout"]
    assert config.trigger_keywords == ["restart"]
    assert config.exclude_keywords == ["healthcheck"]
    assert config.duration_seconds == 30


def test_load_extraction_config_uses_defaults_for_missing_fields(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}", encoding="utf-8")

    config = ConfigLoader.load(config_path)

    assert config.include_keywords == []
    assert config.trigger_keywords == []
    assert config.exclude_keywords == []
    assert config.duration_seconds == 0