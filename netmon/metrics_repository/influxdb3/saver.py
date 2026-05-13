from typing import Iterable, override

from influxdb_client_3 import InfluxDBClient3
from structlog.stdlib import BoundLogger
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.metrics_repository.influxdb3.helpers import from_metric_entry_to_point
from netmon.metrics_repository.interface import MetricsSaver
from netmon.util.chunked import chunked


class Influxdb3MetricsSaver(MetricsSaver):
    def __init__(
            self,
            logger: BoundLogger,
            client: InfluxDBClient3,
            ) -> None:
        self.__log = logger
        self.__client = client

        self.__log.info("initialized")

    @override
    async def save_metrics(self, metrics: Iterable[BaseMetricEntry]) -> None:
        self.__log.debug("saving metrics")

        points = [from_metric_entry_to_point(m) for m in metrics]

        for batch in chunked(points, 100):
            self.__client.write(batch)

        self.__log.info("metrics saved")
