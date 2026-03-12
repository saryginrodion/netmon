from abc import abstractmethod
from collections.abc import Iterable
from datetime import datetime
from typing import Protocol

from netmon.entities.base_metric_entry import BaseMetricEntry


class MetricsSaver(Protocol):
    @abstractmethod
    async def save_metrics(self, metrics: Iterable[BaseMetricEntry]) -> None:
        """Сохранить список метрик."""


class MetricQuerier(Protocol):
    @abstractmethod
    async def metrics_in_interval(self, interval_start: datetime, interval_stop: datetime) -> Iterable[BaseMetricEntry]:
        """Получить список метрик за выбранный период."""
