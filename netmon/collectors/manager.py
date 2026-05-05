import asyncio
from datetime import datetime, timedelta
from typing import Iterable
from structlog.stdlib import BoundLogger
from netmon.collectors.errors import CollectionError
from netmon.collectors.interface import MetricsCollector
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.metrics_repository.interface import MetricsSaver
from netmon.util.async_error_suppressor import async_suppress_exceptions


class CollectorsManager:
    """Manages and runs collectors."""
    def __init__(
            self,
            logger: BoundLogger,
            collectors: list[MetricsCollector],
            metric_saver: MetricsSaver,
            collection_interval: timedelta,
        ) -> None:
        self.__logger = logger
        self.__collectors = collectors
        self.__metric_saver = metric_saver
        self.__collection_inteval = collection_interval


    async def collect(self) -> Iterable[BaseMetricEntry]:
        """Собирает с нескольких коллекторов все метрики.

        Все CollectionError ошибки игнорируются и логируются.
        """

        time = datetime.now()
        suppressed_collect_methods = [
            async_suppress_exceptions(
                {CollectionError}, self.__logger.bind(action="collect", scope=self.__class__.__name__, collector=collector.__class__.__name__)
            )(collector.collect)
            for collector in self.__collectors
        ]

        results_not_flatten = await asyncio.gather(*[collect(time) for collect in suppressed_collect_methods])
        results = []

        for result in results_not_flatten:
            if result is None:
                continue

            results.extend(result)

        return results

    async def __collection_proccess(self) -> None:
        while True:
            try:
                metrics = list(await self.collect())
                await self.__metric_saver.save_metrics(metrics)
                self.__logger.info("collected metrics", entries_count=len(metrics))
                await asyncio.sleep(self.__collection_inteval.total_seconds())
            except Exception as e:
                self.__logger.exception("exception in collect and save loop", error=str(e))

    def start_collection(self) -> None:
        self.__logger.info("starting collection process")
        asyncio.create_task(self.__collection_proccess())
