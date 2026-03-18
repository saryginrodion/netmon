import asyncio
from collections.abc import Iterable
from datetime import datetime
from typing import override

import structlog

from netmon.collectors.errors import CollectionError
from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.util.async_error_suppressor import async_suppress_exceptions


class MergeCollector(MetricsCollector):
    """Собирает с нескольких коллекторов все метрики при collect()."""

    def __init__(self, log: structlog.stdlib.BoundLogger, collectors: list[MetricsCollector]) -> None:
        self._collectors = collectors
        self._log = log

    @override
    async def collect(self, time: datetime) -> Iterable[BaseMetricEntry]:
        """Собирает с нескольких коллекторов все метрики.

        Все CollectionError ошибки игнорируются и логируются.
        """
        suppressed_collect_methods = [
            async_suppress_exceptions(
                {CollectionError}, self._log.bind(action="collect", scope=self.__class__.__name__, collector=collector.__class__.__name__)
            )(collector.collect)
            for collector in self._collectors
        ]

        results_not_flatten = await asyncio.gather(*[collect(time) for collect in suppressed_collect_methods])
        results = []

        for result in results_not_flatten:
            if result is None:
                continue

            results.extend(result)

        return results
