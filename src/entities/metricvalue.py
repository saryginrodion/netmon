from dataclasses import dataclass


@dataclass
class MetricValue:
    """Значение какой-либо метрики в 1 момент времени."""

    accumulated: float
    maximum: float
    minimum: float
    aggregated_count: int
