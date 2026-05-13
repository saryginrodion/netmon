from pydantic import BaseModel

from netmon.metrics_repository.filters import HistoryInterval, LastInterval, MetricFilters


class HistoryBody(BaseModel):
    filters: MetricFilters
    interval: HistoryInterval


class LastBody(BaseModel):
    filters: MetricFilters
    interval: LastInterval
