from datetime import datetime
import pytest
from netmon.collectors.dummy.collector import DummyCollector
from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metricvalue import MetricValue
from netmon.metrics_collector.collector import MetricsCollectorWithSaver
from netmon.metrics_collector.in_memory_saver import InMemorySaver


@pytest.fixture
def dummy_metrics() -> list[BaseMetricEntry]:
    """Создать тестовые метрики."""
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


@pytest.fixture
def dummy_collector(dummy_metrics: list[BaseMetricEntry]) -> MetricsCollector:
    """Создать DummyCollector с тестовыми метриками."""
    return DummyCollector(dummy_metrics)


@pytest.fixture
def in_memory_saver() -> InMemorySaver:
    """Создать InMemorySaver."""
    return InMemorySaver()


@pytest.fixture
def collector_with_saver(
    dummy_collector: DummyCollector,
    in_memory_saver: InMemorySaver,
) -> MetricsCollectorWithSaver:
    """Создать MetricsCollectorWithSaver."""
    return MetricsCollectorWithSaver(dummy_collector, in_memory_saver)


@pytest.mark.asyncio
async def test_collect_and_save(
    collector_with_saver: MetricsCollectorWithSaver,
    in_memory_saver: InMemorySaver,
    dummy_metrics: list[BaseMetricEntry],
) -> None:
    """Проверить, что collect_and_save собирает и сохраняет метрики."""
    await collector_with_saver.collect_and_save()

    saved_metrics = in_memory_saver.metrics
    assert len(saved_metrics) == len(dummy_metrics)

    for expected, actual in zip(dummy_metrics, saved_metrics):
        assert expected == actual


@pytest.mark.asyncio
async def test_collect_and_save_multiple_times(
    collector_with_saver: MetricsCollectorWithSaver,
    in_memory_saver: InMemorySaver,
    dummy_metrics: list[BaseMetricEntry],
) -> None:
    """Проверить, что многократный вызов collect_and_save накапливает метрики."""
    await collector_with_saver.collect_and_save()
    await collector_with_saver.collect_and_save()
    await collector_with_saver.collect_and_save()

    saved_metrics = in_memory_saver.metrics
    assert len(saved_metrics) == len(dummy_metrics) * 3


@pytest.mark.asyncio
async def test_collect_and_save_empty_metrics(
    in_memory_saver: InMemorySaver,
) -> None:
    """Проверить, что collect_and_save работает с пустыми метриками."""
    empty_collector = DummyCollector([])
    collector_with_saver = MetricsCollectorWithSaver(empty_collector, in_memory_saver)

    await collector_with_saver.collect_and_save()

    assert len(in_memory_saver.metrics) == 0
