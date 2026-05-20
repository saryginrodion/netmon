from datetime import datetime
from typing import Iterable, override
from netmon.collectors.collector_status import CollectorStatus
from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry


class DummyCollector(MetricsCollector):
    def __init__(self, dummy_metrics: list[BaseMetricEntry]) -> None:
        self._dummy_metrics = dummy_metrics
        self._is_active = True

    @override
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        if self._is_active:
            return self._dummy_metrics

        return []

    @override
    async def status(self) -> CollectorStatus:
        return CollectorStatus.active if self._is_active else CollectorStatus.stopped

    @override
    async def set_active(self, is_active: bool):
        self._is_active = is_active
