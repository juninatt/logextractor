import json
from pathlib import Path

from logextractor.domain.models import (
    AppConfig,
    FilterConfig,
    FilterRule,
    InputConfig,
    OutputConfig,
    StatisticsConfig,
)


class ConfigLoader:
    """
    Loads application configuration from a JSON file
    and converts it into strongly typed domain objects.
    """

    @staticmethod
    def load(config_path: Path) -> AppConfig:
        with config_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        input_config = InputConfig(**data["input"])
        output_config = OutputConfig(**data["output"])

        rules = ConfigLoader._parse_rules(data["filters"]["rules"])

        filter_config = FilterConfig(
            rules=rules,
            global_exclude_levels=data["filters"].get("global_exclude_levels", []),
            global_exclude_processes=data["filters"].get("global_exclude_processes", []),
            global_exclude_message_contains=data["filters"].get(
                "global_exclude_message_contains", []
            ),
        )

        statistics_config = StatisticsConfig(**data["statistics"])

        return AppConfig(
            input=input_config,
            output=output_config,
            filters=filter_config,
            statistics=statistics_config,
        )

    @staticmethod
    def _parse_rules(rules_data: list[dict]) -> list[FilterRule]:
        rules: list[FilterRule] = []

        for rule in rules_data:
            rules.append(
                FilterRule(
                    name=rule["name"],
                    levels=rule.get("levels", []),
                    processes=rule.get("processes"),
                    logger_contains_any=rule.get("logger_contains_any"),
                    message_contains_any=rule.get("message_contains_any"),
                    context_before_seconds=rule.get("context_before_seconds", 0),
                    context_after_seconds=rule.get("context_after_seconds", 0),
                )
            )

        return rules