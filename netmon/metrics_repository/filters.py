from typing import Literal
from pydantic import BaseModel, Field, IPvAnyAddress


class MetricFilters(BaseModel):
    collectors: list[str] = Field(default=[])
    destination_ips: list[IPvAnyAddress] = Field(default=[])
    metric_types: list[Literal["rtt", "latency_from", "latency_to", "packet_loss"]]


class LastInterval(BaseModel):
    seconds: float = Field(ge=1.0, le=60.0 * 30.0)


class HistoryInterval(BaseModel):
    from_timestamp: float = Field(description="POSIX float seconds")
    to_timestamp: float = Field(description="POSIX float seconds")
