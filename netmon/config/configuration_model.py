from datetime import timedelta
from pydantic import BaseModel, ConfigDict

from netmon.config.collector_configuration_models import CollectorConfig


class StorageConfig(BaseModel):
    host: str
    token: str
    database: str


class APIConfig(BaseModel):
    port: int


class NetmonConfig(BaseModel):
    api: APIConfig

    collect_interval: timedelta

    storage: StorageConfig

    collectors: list[CollectorConfig]

    model_config = ConfigDict(extra="ignore")
