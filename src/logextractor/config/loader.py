import json
from pathlib import Path

from logextractor.domain.models import ExtractionConfig


class ConfigLoader:

    @staticmethod
    def load(config_path: Path) -> ExtractionConfig:
        with config_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return ExtractionConfig(
            include_keywords=data.get("include_keywords", []),
            trigger_keywords=data.get("trigger_keywords", []),
            exclude_keywords=data.get("exclude_keywords", []),
            duration_seconds=data.get("duration_seconds", 0),
        )
