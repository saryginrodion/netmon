from datetime import datetime
from typing import Iterable, override

from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metricvalue import MetricValue
from netmon.metrics_repository.filters import HistoryInterval, LastInterval, MetricFilters
from netmon.metrics_repository.interface import MetricQuerier


class DummyMetricQuerier(MetricQuerier):
    @override
    async def last_metrics(self, filters: MetricFilters, interval: LastInterval) -> Iterable[BaseMetricEntry]:
        """Получить список метрик за последнее время."""
        return [
            BaseMetricEntry(
                origin="TestCollector1",
                timestamp=datetime.now().timestamp(),
                destinatation="1.1.1.1",
                rtt=MetricValue(130, 1, 99, 5),
                latency_from=MetricValue(100, 1, 94, 2),
                latency_to=MetricValue(101, 1, 99, 4),
                packet_loss=0,
            ),
            BaseMetricEntry(
                origin="TestCollector1",
                timestamp=datetime.now().timestamp(),
                destinatation="1.1.1.1",
                rtt=MetricValue(138, 2, 39, 5),
                latency_from=MetricValue(140, 1, 94, 1),
                latency_to=MetricValue(111, 1, 39, 3),
                packet_loss=0.42,
            ),
            BaseMetricEntry(
                origin="TestCollector2",
                timestamp=datetime.now().timestamp(),
                destinatation="1.224.1.222",
                rtt=MetricValue(120, 4, 99, 5),
                latency_from=MetricValue(130, 1, 94, 2),
                latency_to=MetricValue(121, 1, 99, 4),
                packet_loss=0.99,
            ),
        ]

    @override
    async def history_metrics(self, filters: MetricFilters, interval: HistoryInterval) -> Iterable[BaseMetricEntry]:
        """Получить список метрик за определенное время."""
        return [
            BaseMetricEntry(
                origin="TestCollector1",
                timestamp=datetime.now().timestamp(),
                destinatation="1.1.1.1",
                rtt=MetricValue(130, 1, 99, 5),
                latency_from=MetricValue(100, 1, 94, 2),
                latency_to=MetricValue(101, 1, 99, 4),
                packet_loss=0,
            ),
            BaseMetricEntry(
                origin="TestCollector1",
                timestamp=datetime.now().timestamp(),
                destinatation="1.1.1.1",
                rtt=MetricValue(138, 2, 39, 5),
                latency_from=MetricValue(140, 1, 94, 1),
                latency_to=MetricValue(111, 1, 39, 3),
                packet_loss=0.42,
            ),
            BaseMetricEntry(
                origin="TestCollector2",
                timestamp=datetime.now().timestamp(),
                destinatation="1.224.1.222",
                rtt=MetricValue(120, 4, 99, 5),
                latency_from=MetricValue(130, 1, 94, 2),
                latency_to=MetricValue(121, 1, 99, 4),
                packet_loss=0.99,
            ),
        ]
