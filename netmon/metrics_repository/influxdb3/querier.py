from datetime import datetime, timezone
from typing import Iterable, override
from influxdb_client_3 import InfluxDBClient3
from structlog.stdlib import BoundLogger
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.metrics_repository.filters import HistoryInterval, LastInterval, MetricFilters
from netmon.metrics_repository.influxdb3.helpers import from_influx_record_to_metric_entry
from netmon.metrics_repository.interface import MetricQuerier


class Influxdb3MetricQuerier(MetricQuerier):
    def __init__(
        self,
        logger: BoundLogger,
        client: InfluxDBClient3,
    ) -> None:
        self.__log = logger
        self.__client = client

        self.__log.info("initialized")

    @override
    async def last_metrics(
        self,
        filters: MetricFilters,
        interval: LastInterval,
    ) -> Iterable[BaseMetricEntry]:
        sql = self.__build_last_metrics_query(filters, interval)

        self.__log.debug(
            "querying last metrics",
            sql=sql,
        )

        table = self.__client.query(
            query=sql,
            language="sql",
        )

        return [
            from_influx_record_to_metric_entry(record)
            for record in table.to_pylist()
        ]

    @override
    async def history_metrics(
        self,
        filters: MetricFilters,
        interval: HistoryInterval,
    ) -> Iterable[BaseMetricEntry]:
        sql = self.__build_history_metrics_query(filters, interval)

        self.__log.debug(
            "querying history metrics",
            sql=sql,
        )

        table = self.__client.query(
            query=sql,
            language="sql",
        )

        return [
            from_influx_record_to_metric_entry(record)
            for record in table.to_pylist()
        ]

    def __build_last_metrics_query(
        self,
        filters: MetricFilters,
        interval: LastInterval,
    ) -> str:
        now = datetime.now(tz=timezone.utc).timestamp()
        from_ts = now - interval.seconds

        history = HistoryInterval(
            from_timestamp=from_ts,
            to_timestamp=now,
        )

        return self.__build_history_metrics_query(filters, history)

    def __build_history_metrics_query(
        self,
        filters: MetricFilters,
        interval: HistoryInterval,
    ) -> str:
        where_parts: list[str] = [
            (
                f"time >= '{datetime.fromtimestamp(interval.from_timestamp, tz=timezone.utc).isoformat()}'"
            ),
            (
                f"time <= '{datetime.fromtimestamp(interval.to_timestamp, tz=timezone.utc).isoformat()}'"
            ),
        ]

        if filters.collectors:
            collectors = ", ".join(
                f"'{collector}'"
                for collector in filters.collectors
            )

            where_parts.append(f"origin IN ({collectors})")

        if filters.destination_ips:
            ips = ", ".join(
                f"'{ip}'"
                for ip in filters.destination_ips
            )

            where_parts.append(f"dst_ip IN ({ips})")

        metric_fields = self.__metric_fields(filters)

        where_clause = " AND ".join(where_parts)

        return f"""
SELECT
    time,
    origin,
    dst_ip,
    {metric_fields}
FROM metrics
WHERE {where_clause}
ORDER BY time DESC
"""

    def __metric_fields(self, filters: MetricFilters) -> str:
        fields: set[str] = set()

        for metric_type in filters.metric_types:
            match metric_type:
                case "rtt":
                    fields.update([
                        "rtt__acc",
                        "rtt__max",
                        "rtt__min",
                        "rtt__agg",
                    ])

                case "latency_from":
                    fields.update([
                        "lat_from__acc",
                        "lat_from__max",
                        "lat_from__min",
                        "lat_from__agg",
                    ])

                case "latency_to":
                    fields.update([
                        "lat_to__acc",
                        "lat_to__max",
                        "lat_to__min",
                        "lat_to__agg",
                    ])

                case "packet_loss":
                    fields.add("pck_loss")

        return ",\n    ".join(sorted(fields))
