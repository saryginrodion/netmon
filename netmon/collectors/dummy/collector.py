from datetime import datetime
from typing import Iterable, override
from netmon.collectors.collector_status import CollectorStatus
from netmon.collectors.info import CollectorInfo
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
    async def info(self) -> CollectorInfo:
        status = CollectorStatus.active if self._is_active else CollectorStatus.stopped

        return CollectorInfo(
            name="dummycollector",
            status=status,
        )

    @override
    async def set_active(self, is_active: bool):
        self._is_active = is_active
