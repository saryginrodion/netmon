from datetime import datetime, timezone
from typing import Any
from influxdb_client_3 import Point
from netmon.entities.base_metric_entry import BaseMetricEntry
from netmon.entities.metricvalue import MetricValue


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

    if ent.packet_loss:
        point = point.field("pck_loss", float(ent.packet_loss))

    if ent.rtt:
        point = add_metric_value_to_point("rtt__", ent.rtt, point)

    if ent.latency_from:
        point = add_metric_value_to_point("lat_from__", ent.latency_from, point)

    if ent.latency_to:
        point = add_metric_value_to_point("lat_to__", ent.latency_to, point)

    return point

def metric_value_from_record(prefix: str, record: dict[str, Any]) -> MetricValue | None:
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

    return BaseMetricEntry(
        origin=str(record["origin"]),
        timestamp=timestamp,
        destination=str(record["dst_ip"]),
        rtt=metric_value_from_record("rtt__", record),
        latency_from=metric_value_from_record("lat_from__", record),
        latency_to=metric_value_from_record("lat_to__", record),
        packet_loss=(
            float(record["pck_loss"])
            if record.get("pck_loss") is not None
            else None
        ),
    )

