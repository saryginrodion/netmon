from collections.abc import Iterable
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.metrics_repository.interface import MetricsSaver


class InMemorySaver(MetricsSaver):
    def __init__(self) -> None:
        self._metrics: list[BaseMetricEntry] = []

    async def save_metrics(self, metrics: Iterable[BaseMetricEntry]) -> None:
        self._metrics.extend(metrics)

    @property
    def metrics(self) -> list[BaseMetricEntry]:
        return self._metrics.copy()

    def clear(self) -> None:
        self._metrics.clear()
