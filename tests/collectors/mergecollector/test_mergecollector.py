
from datetime import datetime
import pytest
import structlog

from netmon.collectors.dummy.collector import DummyCollector
from netmon.collectors.mergecollector.collector import MergeCollector
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metricvalue import MetricValue


@pytest.mark.asyncio
@pytest.mark.parametrize("metric_entries", [
    [
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
    ], []
])
async def test_merge_collector_correct(
    metric_entries: list[BaseMetricEntry],
) -> None:
    resulting_metric_entries = []
    resulting_metric_entries.extend(metric_entries)
    resulting_metric_entries.extend(metric_entries)

    merge_collector = MergeCollector(structlog.get_logger(), [
        DummyCollector(metric_entries),
        DummyCollector(metric_entries),
    ])

    collected = list(await merge_collector.collect(datetime.now()))

    assert len(resulting_metric_entries) == len(collected)
    assert all(resulting_metric_entries[i] == collected[i] for i in range(len(resulting_metric_entries)))


@pytest.mark.asyncio
@pytest.mark.parametrize("metric_entries", [
    [
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
    ], []
])
async def test_merge_collector_handled_error(
    metric_entries: list[BaseMetricEntry],
    handled_error_collector,
) -> None:
    resulting_metric_entries = []
    resulting_metric_entries.extend(metric_entries)
    resulting_metric_entries.extend(metric_entries)

    merge_collector = MergeCollector(structlog.get_logger(), [
        handled_error_collector,
        DummyCollector(metric_entries),
        handled_error_collector,
        DummyCollector(metric_entries),
        handled_error_collector,
    ])

    collected = list(await merge_collector.collect(datetime.now()))

    assert len(resulting_metric_entries) == len(collected)
    assert all(resulting_metric_entries[i] == collected[i] for i in range(len(resulting_metric_entries)))


@pytest.mark.asyncio
@pytest.mark.parametrize("metric_entries", [
    [
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
    ], []
])
async def test_merge_collector_unhandled_error(
    metric_entries: list[BaseMetricEntry],
    handled_error_collector,
    unhandled_error_collector,
) -> None:
    resulting_metric_entries = []
    resulting_metric_entries.extend(metric_entries)
    resulting_metric_entries.extend(metric_entries)

    merge_collector = MergeCollector(structlog.get_logger(), [
        DummyCollector(metric_entries),
        unhandled_error_collector,
        DummyCollector(metric_entries),
        handled_error_collector,
    ])

    try:
        await merge_collector.collect(datetime.now())
        raise Exception("should be unreachable")
    except:
        ...
