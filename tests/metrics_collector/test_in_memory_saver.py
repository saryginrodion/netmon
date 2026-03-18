from datetime import datetime
import pytest
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metricvalue import MetricValue
from netmon.metrics_collector.in_memory_saver import InMemorySaver


@pytest.fixture
def sample_metrics() -> list[BaseMetricEntry]:
    return [
        BaseMetricEntry(
            origin="TestCollector",
            timestamp=datetime.now().timestamp(),
            destinatation="1.1.1.1",
            rtt=MetricValue(130, 1, 99, 5),
            latency_from=MetricValue(100, 1, 94, 2),
            latency_to=MetricValue(101, 1, 99, 4),
            packet_loss=0,
        ),
        BaseMetricEntry(
            origin="TestCollector",
            timestamp=datetime.now().timestamp(),
            destinatation="8.8.8.8",
            rtt=MetricValue(50, 1, 49, 2),
            latency_from=MetricValue(45, 1, 44, 1),
            latency_to=MetricValue(48, 1, 47, 1),
            packet_loss=0.1,
        ),
    ]


@pytest.mark.asyncio
async def test_save_metrics(sample_metrics: list[BaseMetricEntry]) -> None:
    saver = InMemorySaver()
    await saver.save_metrics(sample_metrics)
    assert len(saver.metrics) == 2
    assert saver.metrics == sample_metrics


@pytest.mark.asyncio
async def test_save_metrics_multiple_times(sample_metrics: list[BaseMetricEntry]) -> None:
    saver = InMemorySaver()
    await saver.save_metrics(sample_metrics)
    await saver.save_metrics(sample_metrics)
    assert len(saver.metrics) == 4


@pytest.mark.asyncio
async def test_save_empty_metrics() -> None:
    saver = InMemorySaver()
    await saver.save_metrics([])
    assert len(saver.metrics) == 0


@pytest.mark.asyncio
async def test_clear(sample_metrics: list[BaseMetricEntry]) -> None:
    saver = InMemorySaver()
    await saver.save_metrics(sample_metrics)
    assert len(saver.metrics) == 2
    saver.clear()
    assert len(saver.metrics) == 0


@pytest.mark.asyncio
async def test_metrics_returns_copy(sample_metrics: list[BaseMetricEntry]) -> None:
    saver = InMemorySaver()
    await saver.save_metrics(sample_metrics)
    metrics = saver.metrics
    metrics.clear()
    assert len(saver.metrics) == 2
