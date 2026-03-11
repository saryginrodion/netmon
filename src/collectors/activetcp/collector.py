from collections.abc import Iterable
from datetime import datetime
from typing import override

from collectors.interface import MetricsCollector
from entities.base_metric_entry import BaseMetricEntry


class ActiveTCPCollector(MetricsCollector):
    def __init__(self) -> None:
        pass

    @override
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        return await super().collect(time)
