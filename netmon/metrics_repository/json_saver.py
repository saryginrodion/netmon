from datetime import datetime
from collections.abc import Iterable
from typing import Any
import json
from pathlib import Path
from netmon.entities.base_metric_entry import BaseMetricEntry
from .interface import MetricsSaver
from .errors import MetricSaveError

class JSONMetricsSaver(MetricsSaver):
    """Сохранение BaseMetricEntry только в JSON файл."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self._init_file()

    def _init_file(self) -> None:
        try:
            if not self.file_path.exists():
                self.file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
        except Exception as e:
            msg = f"Cannot initialize JSON file: {e}"
            raise MetricSaveError(msg) from e

    def _metric_to_dict(self, metric: BaseMetricEntry) -> dict[str, Any]:
        data = {}

        for key, value in metric.__dict__.items():

            if isinstance(value, datetime):
                data[key] = value.isoformat()

            elif hasattr(value, "__dict__"):
                data[key] = value.__dict__

            else:
                data[key] = value

        return data

    async def save_metrics(self, metrics: Iterable[BaseMetricEntry]) -> None:
        try:

            with open(self.file_path, "r", encoding="utf-8") as f:
                try:
                    stored_metrics = json.load(f)
                except json.JSONDecodeError:
                    stored_metrics = []

            new_metrics = [self._metric_to_dict(m) for m in metrics]

            stored_metrics.extend(new_metrics)

            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(stored_metrics, f, indent=4, ensure_ascii=False)

        except Exception as e:
            msg = f"Failed to save metrics: {e}"
            raise MetricSaveError(msg) from e