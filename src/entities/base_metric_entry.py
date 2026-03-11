from dataclasses import dataclass

from src.entities.metricvalue import MetricValue


@dataclass
class BaseMetricEntry:
    """Базовый датакласс для собранных метрик с коллектора."""

    origin: str
    """Источник (название коллектора), с которого пришла метрика."""
    timestamp: float
    """POSIX timestamp в секундах"""
    destinatation: str
    """IP сервера, запросы к которому измерялись"""

    rtt: MetricValue | None
    latency_from: MetricValue | None
    latency_to: MetricValue | None
    packet_loss: MetricValue | None
