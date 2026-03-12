from dataclasses import dataclass


@dataclass
class MetricValue:
    """Значение какой-либо метрики в 1 момент времени."""

    accumulated: float = 0
    maximum: float = 0
    minimum: float = 0
    aggregated_count: int = 0

    def add(self, value: float) -> None:
        self.accumulated += value
        self.aggregated_count += 1

        if self.aggregated_count == 1:
            self.maximum = value
            self.minimum = value
            return

        if self.maximum < value:
            self.maximum = value

        if self.minimum > value:
            self.minimum = value

    def add_all(self, values: list[float]) -> None:
        for v in values:
            self.add(v)

    @property
    def value(self) -> float | None:
        """Вернет None только в том случае, если aggregated_count == 0."""
        if self.aggregated_count > 0:
            return self.accumulated / self.aggregated_count

        return None
