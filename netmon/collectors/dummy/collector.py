from datetime import datetime
from typing import Iterable, override
from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry


class DummyCollector(MetricsCollector):
    def __init__(self, dummy_metrics: list[BaseMetricEntry]) -> None:
        self._dummy_metrics = dummy_metrics

    @override
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        return self._dummy_metrics
