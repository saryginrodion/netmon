from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime

from netmon.collectors.info import CollectorInfo
from netmon.entities.base_metric_entry import BaseMetricEntry


class MetricsCollector(ABC):
    """Один коллектор данных."""

    @abstractmethod
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        """Собрать метрики за момент времени `time`."""

    @abstractmethod
    async def info(self) -> CollectorInfo:
        """Вернуть текущую информацию о коллекторе."""


    @abstractmethod
    async def set_active(self, is_active: bool):
        """Запустить / остановить коллектор."""
