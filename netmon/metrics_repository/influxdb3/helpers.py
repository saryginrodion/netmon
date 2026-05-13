from datetime import datetime, timezone
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
        .field("dst_ip", ent.destinatation) \
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
