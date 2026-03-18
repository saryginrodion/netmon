from datetime import datetime
from typing import Iterable, override
import pytest

from netmon.collectors.errors import CollectionError
from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry

class ErrorCollector(MetricsCollector):
    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    @override
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        raise self._exc


@pytest.fixture
def handled_error_collector():
    return ErrorCollector(CollectionError("handled error collector!"))

@pytest.fixture
def unhandled_error_collector():
    return ErrorCollector(Exception("unhandled error collector!"))
