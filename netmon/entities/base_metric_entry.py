from dataclasses import dataclass

from netmon.entities.metric_name_enum import MetricName
from netmon.entities.metricvalue import MetricValue


@dataclass
class BaseMetricEntry:
    """Базовый датакласс для собранных метрик с коллектора."""

    origin: str
    """Источник (название коллектора), с которого пришла метрика."""
    timestamp: float
    """POSIX timestamp в секундах"""
    destination: str
    """IP сервера, запросы к которому измерялись"""

    metrics: dict[MetricName, MetricValue | float]
