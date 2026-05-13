from datetime import timedelta
from pathlib import Path
from pydantic import BaseModel, ConfigDict

from netmon.cmd.netmon_collector.collector_configuration_models import CollectorConfig


class StorageConfig(BaseModel):
    file_path: Path


class APIConfig(BaseModel):
    port: int


class NetmonConfig(BaseModel):
    api: APIConfig

    collect_interval: timedelta

    storage: StorageConfig

    collectors: list[CollectorConfig]

    model_config = ConfigDict(extra="ignore")
