from abc import abstractmethod
from collections.abc import Iterable
from typing import Protocol

from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.metrics_repository.filters import HistoryInterval, LastInterval, MetricFilters


class MetricsSaver(Protocol):
    @abstractmethod
    async def save_metrics(self, metrics: Iterable[BaseMetricEntry]) -> None:
        """Сохранить список метрик."""


class MetricQuerier(Protocol):
    @abstractmethod
    async def last_metrics(self, filters: MetricFilters, interval: LastInterval) -> Iterable[BaseMetricEntry]:
        """Получить список метрик за последнее время."""

    @abstractmethod
    async def history_metrics(self, filters: MetricFilters, interval: HistoryInterval) -> Iterable[BaseMetricEntry]:
        """Получить список метрик за определенное время."""
