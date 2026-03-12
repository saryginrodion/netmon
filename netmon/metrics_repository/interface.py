from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime

from netmon.entities.base_metric_entry import BaseMetricEntry


class MetricsRepository(ABC):
    """Репозиторий для сохранения метрик."""

    @abstractmethod
    async def save_metrics(self, metrics: Iterable[BaseMetricEntry]) -> None:
        """Сохранить список метрик."""

    @abstractmethod
    async def metrics_in_interval(self, interval_start: datetime, interval_stop: datetime) -> Iterable[BaseMetricEntry]:
        """Получить список метрик за выбранный период."""
