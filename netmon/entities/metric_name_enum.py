import enum


class MetricName(str, enum.Enum):
    rtt = "rtt"
    jitter = "jitter"
    latency_from = "latency_from"
    latency_to = "latency_to"
    packet_loss = "packet_loss"
    packets_sent = "packets_sent"
