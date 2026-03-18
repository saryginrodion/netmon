from datetime import datetime
from pathlib import Path
import pytest
from netmon.collectors.dummy.collector import DummyCollector
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metricvalue import MetricValue
from netmon.metrics_collector.collector import MetricsCollectorWithSaver
from netmon.metrics_collector.in_memory_saver import InMemorySaver
from netmon.metrics_repository.json_saver import JSONMetricsSaver


@pytest.fixture
def dummy_metrics() -> list[BaseMetricEntry]:
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
    ]


@pytest.mark.asyncio
async def test_collect_and_save_with_in_memory_saver(
    dummy_metrics: list[BaseMetricEntry],
) -> None:
    collector = DummyCollector(dummy_metrics)
    saver = InMemorySaver()
    wrapper = MetricsCollectorWithSaver(collector, saver)
    await wrapper.collect_and_save()
    assert len(saver.metrics) == 1
    assert saver.metrics[0] == dummy_metrics[0]


@pytest.mark.asyncio
async def test_collect_and_save_with_json_saver(
    dummy_metrics: list[BaseMetricEntry],
    tmp_path: Path,
) -> None:
    json_file = tmp_path / "metrics.json"
    
    collector = DummyCollector(dummy_metrics)
    saver = JSONMetricsSaver(json_file)
    wrapper = MetricsCollectorWithSaver(collector, saver)

    await wrapper.collect_and_save()
    assert json_file.exists()
    
    import json
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert len(data) == 1
    assert data[0]["origin"] == "TestCollector"
    assert data[0]["destinatation"] == "1.1.1.1"


@pytest.mark.asyncio
async def test_collect_and_save_multiple_with_json_saver(
    dummy_metrics: list[BaseMetricEntry],
    tmp_path: Path,
) -> None:
    json_file = tmp_path / "metrics.json"
    
    collector = DummyCollector(dummy_metrics)
    saver = JSONMetricsSaver(json_file)
    wrapper = MetricsCollectorWithSaver(collector, saver)

    await wrapper.collect_and_save()
    await wrapper.collect_and_save()

    import json
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert len(data) == 2
