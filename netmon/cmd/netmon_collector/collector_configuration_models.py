from datetime import timedelta
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, IPvAnyAddress
from ipaddress import IPvAnyAddress


class ActiveTCPConfig(BaseModel):
    type: Literal["activetcp"]
    addr: IPvAnyAddress
    port: int = Field(gt=0, lt=65535)
    packet_send_delay: timedelta = Field(default=timedelta(seconds=0.1))
    reconnect_interval: timedelta = timedelta(seconds=15)
    read_timeout: timedelta = timedelta(seconds=10)
    write_timeout: timedelta = timedelta(seconds=10)

    origin_name: str = "activetcp"


class ActiveUDPConfig(BaseModel):
    type: Literal["activeudp"]
    addr: IPvAnyAddress
    port: int = Field(gt=0, lt=65535)
    packet_send_delay: timedelta = Field(default=timedelta(seconds=0.1))
    read_timeout: timedelta = timedelta(seconds=10)

    origin_name: str = "activeudp"


CollectorConfig = Annotated[
    Union[ActiveTCPConfig, ActiveUDPConfig, ActiveQUICConfig],
    Field(discriminator="type"),
]

class ActiveQUICConfig(BaseModel):
    type: Literal["activequic"]

    addr: IPvAnyAddress
    port: int = Field(gt=0, lt=65535)

    packet_send_delay: timedelta = timedelta(seconds=1)
    origin_name: str = "activequic"
