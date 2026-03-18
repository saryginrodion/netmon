from datetime import datetime
from collections.abc import Iterable
from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.metrics_repository.interface import MetricsSaver


class MetricsCollectorWithSaver:
    def __init__(self, collector: MetricsCollector, saver: MetricsSaver) -> None:
        self._collector = collector
        self._saver = saver

    async def collect_and_save(self) -> None:
        time = datetime.now()
        metrics: Iterable[BaseMetricEntry] = await self._collector.collect(time)
        await self._saver.save_metrics(metrics)
