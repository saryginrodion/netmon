from dataclasses import dataclass


@dataclass
class MetricValue:
    """Значение какой-либо метрики в 1 момент времени."""

    accumulated: float
    maximum: float
    minimum: float
    aggregated_count: int


    def add(self, value: float) -> None:
        self.accumulated += value
        self.aggregated_count += 1

    @property
    def value(self) -> float | None:
        """Вернет None только в том случае, если aggregated_count == 0."""
        if self.aggregated_count > 0:
            return self.accumulated / self.aggregated_count

        return None
