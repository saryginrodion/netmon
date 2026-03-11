from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime

from entities.base_metric_entry import BaseMetricEntry


class MetricsCollector(ABC):
    """Один коллектор данных."""

    @abstractmethod
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        """Собрать метрики за момент времени `time`."""
