from datetime import timedelta
from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field, IPvAnyAddress


class ActiveTCPConfig(BaseModel):
    type: Literal["activetcp"]
    addr: IPvAnyAddress
    port: int = Field(gt=0, lt=65535)
    packet_send_delay: timedelta = Field(default=timedelta(seconds=0.1))
    reconnect_interval: timedelta = timedelta(seconds=15)
    read_timeout: timedelta = timedelta(seconds=10)
    write_timeout: timedelta = timedelta(seconds=10)


class ActiveUDPConfig(BaseModel):
    type: Literal["activeudp"]
    addr: IPvAnyAddress
    port: int = Field(gt=0, lt=65535)
    packet_send_delay: timedelta = Field(default=timedelta(seconds=0.1))
    read_timeout: timedelta = timedelta(seconds=10)


CollectorConfig = Annotated[
    Union[ActiveTCPConfig, ActiveUDPConfig],
    Field(discriminator="type"),
]
