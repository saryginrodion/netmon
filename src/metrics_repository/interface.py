import abc
from collections.abc import Iterable

from entities.base_metric_entry import BaseMetricEntry


class MetricsRepository(abc.ABC):
    """Репозиторий для сохранения метрик."""

    @abc.abstractmethod
    def save_metrics(self, metrics: Iterable[BaseMetricEntry]) -> None:
        pass
