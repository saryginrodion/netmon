from datetime import datetime, timezone
from typing import Any
from influxdb_client_3 import Point
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metric_name_enum import MetricName
from netmon.entities.metricvalue import MetricValue

__NAME_SPLITTER = "__"

def add_metric_value_to_point(prefix: str, val: MetricValue, point: Point) -> Point:
    return point \
            .field(prefix + "acc", float(val.accumulated)) \
            .field(prefix + "max", float(val.maximum)) \
            .field(prefix + "min", float(val.minimum)) \
            .field(prefix + "agg", int(val.aggregated_count))


def from_metric_entry_to_point(ent: BaseMetricEntry) -> Point:
    point = Point("metrics") \
        .tag("origin", ent.origin) \
        .field("dst_ip", ent.destination) \
        .time(datetime.fromtimestamp(ent.timestamp, tz=timezone.utc))

    for k, v in ent.metrics.items():
        if isinstance(v, MetricValue):
            point = add_metric_value_to_point(k.name + __NAME_SPLITTER, v, point)
        else:
            point = point.field(k.name, float(v))

    return point

def metric_value_from_record(name: str, record: dict[str, Any]) -> MetricValue | float | None:
    if record.get(name) is not None:
        return record.get(name)

    prefix = name + __NAME_SPLITTER
    acc = record.get(f"{prefix}acc")
    agg = record.get(f"{prefix}agg")

    if acc is None or agg is None or int(agg) <= 0:
        return None

    return MetricValue(
        accumulated=float(acc),
        maximum=float(record.get(f"{prefix}max", 0)),
        minimum=float(record.get(f"{prefix}min", 0)),
        aggregated_count=int(agg),
    )


def from_influx_record_to_metric_entry(record: dict[str, Any]) -> BaseMetricEntry:
    timestamp_raw = record["time"]

    if isinstance(timestamp_raw, datetime):
        timestamp = timestamp_raw.timestamp()
    else:
        timestamp = datetime.fromisoformat(str(timestamp_raw)).timestamp()

    metrics: dict[MetricName, MetricValue | float] = dict()

    for metric_name in MetricName:
        val = metric_value_from_record(metric_name.name, record)
        if val is None:
            continue

        metrics[metric_name] = val

    return BaseMetricEntry(
        origin=str(record["origin"]),
        timestamp=timestamp,
        destination=str(record["dst_ip"]),
        metrics=metrics,
    )

