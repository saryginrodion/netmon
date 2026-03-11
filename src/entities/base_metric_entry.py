from dataclasses import dataclass

from src.entities.metricvalue import MetricValue


@dataclass
class BaseMetricEntry:
    """Базовый датакласс для собранных метрик с коллектора."""

    origin: str
    timestamp: float
    destinatation: str
    port: int

    rtt: MetricValue | None
    latency_from: MetricValue | None
    latency_to: MetricValue | None
    packet_loss: MetricValue | None
