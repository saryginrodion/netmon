from datetime import datetime
import json
from pathlib import Path
import pytest
import dacite

from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metricvalue import MetricValue
from netmon.metrics_repository.interface import MetricsSaver

@pytest.mark.asyncio
@pytest.mark.parametrize("metric_entries", [
    [
        BaseMetricEntry(
            origin="TestCollector1",
            timestamp=datetime.now().timestamp(),
            destination="1.1.1.1",
            rtt=MetricValue(130, 1, 99, 5),
            latency_from=MetricValue(100, 1, 94, 2),
            latency_to=MetricValue(101, 1, 99, 4),
            packet_loss=0,
        ),
        BaseMetricEntry(
            origin="TestCollector1",
            timestamp=datetime.now().timestamp(),
            destination="1.1.1.1",
            rtt=MetricValue(138, 2, 39, 5),
            latency_from=MetricValue(140, 1, 94, 1),
            latency_to=MetricValue(111, 1, 39, 3),
            packet_loss=0.42,
        ),
        BaseMetricEntry(
            origin="TestCollector2",
            timestamp=datetime.now().timestamp(),
            destination="1.224.1.222",
            rtt=MetricValue(120, 4, 99, 5),
            latency_from=MetricValue(130, 1, 94, 2),
            latency_to=MetricValue(121, 1, 99, 4),
            packet_loss=0.99,
        ),
    ], []
])
async def test_json_metrics(
    metric_entries: list[BaseMetricEntry],
    json_file_path: Path,
    json_saver: MetricsSaver,
) -> None:
    await json_saver.save_metrics(metric_entries)

    with open(json_file_path, "r") as f:
        metrics_dict = json.loads(f.read())
    
    assert isinstance(metrics_dict, list)
    assert len(metrics_dict) == len(metric_entries)

    for i, d in enumerate(metrics_dict):
        metric = dacite.from_dict(BaseMetricEntry, d)
        assert metric_entries[i] == metric
